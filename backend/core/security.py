"""
security.py — Input sanitization & prompt injection mitigation layer.

All raw user text (fan messages, incident descriptions) MUST pass through
``sanitize_input()`` before reaching any GenAI system prompt.  High-risk
injection payloads are blocked with an HTTP 400 and securely logged.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from fastapi import HTTPException

logger = logging.getLogger("stadium_ops.security")

# ── Injection Signatures ──────────────────────────────────────────────────────
# Compiled once at module-import time for O(1) amortised matching.
# Each tuple: (pattern, human-readable label for audit logs)

_INJECTION_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Direct instruction override attempts
    (re.compile(r"ignore\s+(all\s+)?(your\s+)?(previous|prior|above|earlier)?\s*(instructions?|prompts?|rules?|context)", re.IGNORECASE),
     "instruction_override"),
    (re.compile(r"disregard\s+(all\s+)?(your\s+)?(previous|prior|above|earlier)?\s*(instructions?|prompts?|rules?|context)", re.IGNORECASE),
     "instruction_override"),
    (re.compile(r"forget\s+(all\s+)?(your\s+)?(previous|prior|above|earlier)?\s*(instructions?|prompts?|rules?|context|training)", re.IGNORECASE),
     "instruction_override"),

    # System / role hijacking
    (re.compile(r"(you\s+are\s+now|act\s+as|pretend\s+(to\s+be|you\s+are)|role\s*play\s+as)\s+", re.IGNORECASE),
     "role_hijack"),
    (re.compile(r"system\s*(override|prompt|message|instruction|command)", re.IGNORECASE),
     "system_override"),
    (re.compile(r"(new\s+)?system\s*:\s*", re.IGNORECASE),
     "system_injection"),
    (re.compile(r"\[SYSTEM\]", re.IGNORECASE),
     "system_tag_injection"),

    # Prompt leaking / exfiltration
    (re.compile(r"(reveal|show|display|print|output|repeat|echo)\s+(your|the|system)\s+(prompt|instructions?|rules?|context)", re.IGNORECASE),
     "prompt_leak"),
    (re.compile(r"what\s+(are|is)\s+your\s+(system\s+)?(prompt|instructions?|rules?)", re.IGNORECASE),
     "prompt_leak"),

    # Jailbreak delimiters & encoding tricks
    (re.compile(r"<\|im_start\|>|<\|im_end\|>|<\|system\|>|<\|user\|>|<\|assistant\|>", re.IGNORECASE),
     "delimiter_injection"),
    (re.compile(r"\\x[0-9a-fA-F]{2}", re.IGNORECASE),
     "hex_encoding_bypass"),
    (re.compile(r"base64\s*[:=]", re.IGNORECASE),
     "base64_bypass"),

    # DAN / persona override
    (re.compile(r"\bDAN\b.*\b(mode|jailbreak|enabled)\b", re.IGNORECASE),
     "dan_jailbreak"),
    (re.compile(r"(developer|debug|admin|root|sudo)\s*(mode|access|override)", re.IGNORECASE),
     "privilege_escalation"),

    # Output schema manipulation
    (re.compile(r"(return|output|respond\s+with)\s+(only\s+)?(true|false|null|none|undefined)", re.IGNORECASE),
     "output_manipulation"),
    (re.compile(r"(do\s+not|don'?t|never)\s+(follow|obey|comply|listen)", re.IGNORECASE),
     "compliance_bypass"),
]

# ── Markdown / Formatting Exploits ────────────────────────────────────────────
_MARKDOWN_FENCES: re.Pattern[str] = re.compile(r"```[\s\S]*?```")
_ANGLE_TAGS: re.Pattern[str] = re.compile(r"<[^>]{1,200}>")
_CONTROL_CHARS: re.Pattern[str] = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_EXCESSIVE_WHITESPACE: re.Pattern[str] = re.compile(r"[ \t]{10,}")
_EXCESSIVE_NEWLINES: re.Pattern[str] = re.compile(r"\n{4,}")


# ── Public API ────────────────────────────────────────────────────────────────

def sanitize_input(
    text: str,
    *,
    field_name: str = "input",
    max_length: int = 4000,
    strip_markdown: bool = True,
    strip_html_tags: bool = True,
    source_ip: Optional[str] = None,
) -> str:
    """
    Sanitize and validate raw user text before it reaches a GenAI prompt.

    Processing order:
      1. Length enforcement
      2. Control character removal
      3. Markdown fence stripping (optional)
      4. HTML/angle-bracket tag stripping (optional)
      5. Whitespace normalisation
      6. Injection pattern scanning → HTTP 400 on match

    Parameters
    ----------
    text : str
        Raw user input.
    field_name : str
        Name of the field (for error messages and audit logs).
    max_length : int
        Hard ceiling on input length after sanitization.
    strip_markdown : bool
        Remove markdown code fences (```) to prevent prompt boundary escapes.
    strip_html_tags : bool
        Remove angle-bracket tags to prevent pseudo-XML injection.
    source_ip : str | None
        Optional client IP for structured audit logging.

    Returns
    -------
    str
        Sanitized text safe to interpolate into a GenAI prompt.

    Raises
    ------
    HTTPException (400)
        If the input contains a detected injection pattern.
    """
    # ── Step 0: Type guard ───────────────────────────────────────────────
    if not isinstance(text, str):
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_input", "field": field_name, "message": "Input must be a string."},
        )

    # ── Step 1: Strip control characters ─────────────────────────────────
    cleaned: str = _CONTROL_CHARS.sub("", text)

    # ── Step 2: Strip markdown fences ────────────────────────────────────
    if strip_markdown:
        cleaned = _MARKDOWN_FENCES.sub("[code-block-removed]", cleaned)

    # ── Step 3: Strip HTML/angle tags ────────────────────────────────────
    if strip_html_tags:
        cleaned = _ANGLE_TAGS.sub("", cleaned)

    # ── Step 4: Normalise whitespace ─────────────────────────────────────
    cleaned = _EXCESSIVE_WHITESPACE.sub(" ", cleaned)
    cleaned = _EXCESSIVE_NEWLINES.sub("\n\n", cleaned)
    cleaned = cleaned.strip()

    # ── Step 5: Length enforcement ────────────────────────────────────────
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
        logger.warning(
            "Input truncated  field=%s  original_len=%d  max=%d  ip=%s",
            field_name, len(text), max_length, source_ip or "unknown",
        )

    # ── Step 6: Empty-after-sanitization check ───────────────────────────
    if not cleaned:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "empty_input",
                "field": field_name,
                "message": "Input is empty after sanitization.",
            },
        )

    # ── Step 7: Injection pattern scan ───────────────────────────────────
    _scan_for_injections(cleaned, field_name=field_name, source_ip=source_ip)

    return cleaned


def _scan_for_injections(
    text: str,
    *,
    field_name: str,
    source_ip: Optional[str] = None,
) -> None:
    """
    Scan sanitized text against compiled injection patterns.

    On match: log an audit event and raise HTTP 400.
    Uses structured logging fields for SIEM ingestion.
    """
    for pattern, label in _INJECTION_PATTERNS:
        match: Optional[re.Match[str]] = pattern.search(text)
        if match:
            # Truncate matched snippet for log safety (no full user payload in logs)
            snippet: str = match.group()[:80]

            logger.warning(
                "PROMPT_INJECTION_BLOCKED  label=%s  field=%s  snippet=%.80s  ip=%s",
                label,
                field_name,
                snippet,
                source_ip or "unknown",
            )

            raise HTTPException(
                status_code=400,
                detail={
                    "error": "prompt_injection_detected",
                    "field": field_name,
                    "message": (
                        "Your input contains content that cannot be processed. "
                        "Please rephrase your request using natural language."
                    ),
                },
            )


def validate_language_code(code: str) -> str:
    """
    Validate an ISO 639-1 language code.
    Only allow known safe codes to prevent injection via the language field.
    """
    _ALLOWED_CODES: set[str] = {
        "en", "es", "fr", "ar", "pt", "de",  # Primary FIFA WC languages
        "zh", "ja", "ko", "ru", "hi", "it",  # Extended support
        "nl", "pl", "tr", "sv", "da", "no",
    }
    if not code:
        return "en"
    normalised: str = code.strip().lower()[:5]
    if normalised not in _ALLOWED_CODES:
        return "en"  # Safe fallback
    return normalised

def redact_pii(text: str) -> str:
    """
    Redact mock PII such as Names, Phone Numbers, and Seat Numbers from OCR text.
    """
    if not text:
        return text
    # Redact seat numbers (e.g. Seat A-12, Section 108)
    text = re.sub(r'(?i)\b(seat|section|row)\s+[A-Z0-9-]{1,5}\b', r'\1 [REDACTED]', text)
    # Redact names following "Name:" pattern
    text = re.sub(r'(?i)\bname:\s*[A-Z][a-z]+\s+[A-Z][a-z]+\b', 'Name: [REDACTED]', text)
    # Redact phone numbers (e.g. 555-123-4567)
    text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[REDACTED_PHONE]', text)
    return text
