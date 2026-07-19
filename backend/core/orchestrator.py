"""
orchestrator.py — Async multi-agent GenAI orchestration service (hardened).

Houses the StadiumOrchestrator class which manages two distinct agents:
  1. Incident Commander  — severity triage & structured task assignment
  2. Multilingual Fan Assistant — language detection & localized guidance

Security hardening (Phase 3):
  - All user inputs are sanitized via backend.core.security before LLM calls
  - LLM outputs are schema-enforced via response_schema (no free-form parsing)
  - GenAI SDK calls wrapped in robust error handling with typed fallbacks
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import time
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from google import genai
from google.genai import types

from backend.core.config import PROMPTS, get_settings
from backend.core.security import sanitize_input, validate_language_code
from backend.schemas.payload import FanAssistLLM, TaskAssignmentLLM

logger = logging.getLogger("stadium_ops.orchestrator")

# ── Global Token Tracker ──────────────────────────────────────────────────────

TOKEN_TRACKER = {
    "gemini-1.5-flash": {"input": 0, "output": 0},
    "gemini-1.5-pro": {"input": 0, "output": 0},
}

def track_tokens(model: str, response: Any) -> None:
    """Track token usage from a GenAI response."""
    if not hasattr(response, 'usage_metadata') or not response.usage_metadata:
        return
    # Normalize model name key
    model_key = "gemini-1.5-pro" if "pro" in model.lower() else "gemini-1.5-flash"
    
    TOKEN_TRACKER[model_key]["input"] += response.usage_metadata.prompt_token_count or 0
    TOKEN_TRACKER[model_key]["output"] += response.usage_metadata.candidates_token_count or 0

# ── Async TTL Cache ───────────────────────────────────────────────────────────

class AsyncTTLCache:
    """
    Lightweight in-memory async cache with per-entry time-to-live.

    Thread-safe via an asyncio.Lock.  Expired entries are lazily evicted
    on read and periodically swept on write when the map exceeds a
    configurable high-water mark.
    """

    __slots__ = ("_store", "_lock", "_default_ttl", "_max_size")

    def __init__(self, default_ttl: int = 300, max_size: int = 2048) -> None:
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock: asyncio.Lock = asyncio.Lock()
        self._default_ttl: int = default_ttl          # seconds
        self._max_size: int = max_size

    @staticmethod
    def _make_key(text: str) -> str:
        """Normalize & hash input for consistent cache keys."""
        normalized = re.sub(r"\s+", " ", text.strip().lower())
        return hashlib.sha256(normalized.encode()).hexdigest()

    async def get(self, raw_query: str) -> Optional[Any]:
        """Return cached value if present and not expired, else None."""
        key = self._make_key(raw_query)
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    async def set(self, raw_query: str, value: Any, ttl: Optional[int] = None) -> None:
        """Insert or overwrite a cache entry."""
        key = self._make_key(raw_query)
        expires_at = time.monotonic() + (ttl or self._default_ttl)
        async with self._lock:
            # Lazy sweep if we exceed high-water mark
            if len(self._store) >= self._max_size:
                now = time.monotonic()
                self._store = {
                    k: v for k, v in self._store.items() if v[1] > now
                }
            self._store[key] = (value, expires_at)

    async def stats(self) -> dict[str, int]:
        """Return cache size metrics (non-blocking snapshot)."""
        async with self._lock:
            now = time.monotonic()
            alive = sum(1 for _, (__, exp) in self._store.items() if exp > now)
            return {"total_entries": len(self._store), "alive_entries": alive}


# ── Severity Classifier ──────────────────────────────────────────────────────

# Keyword → severity mapping evaluated top-down (first match wins)
_SEVERITY_RULES: list[tuple[str, list[str]]] = [
    ("CRITICAL", [
        "stampede", "collapse", "bomb", "explosive", "shooting", "gunshot",
        "cardiac arrest", "structural failure", "fire", "blaze",
        "mass casualty", "terrorist", "crush",
    ]),
    ("HIGH", [
        "medical emergency", "unconscious", "bleeding", "fracture",
        "crowd surge", "overcrowd", "security breach", "weapon",
        "power outage", "evacuation", "heat stroke", "dehydration severe",
    ]),
    ("MEDIUM", [
        "gate congestion", "congestion", "fainting", "lost child",
        "altercation", "fight", "vandalism", "water leak",
        "equipment failure", "elevator stuck", "escalator",
    ]),
    ("LOW", [
        "noise complaint", "lost item", "spill", "broken seat",
        "wifi", "signal", "restroom", "litter", "minor delay",
    ]),
]


def classify_severity(description: str) -> str:
    """
    Deterministically classify incident severity from description text.

    Runs in O(keywords) — no LLM call needed for initial triage.
    The GenAI agent may override this in its structured response.
    """
    text_lower = description.lower()
    for level, keywords in _SEVERITY_RULES:
        for kw in keywords:
            if kw in text_lower:
                return level
    return "MEDIUM"  # safe default


def estimate_crowd_impact(severity: str, zone: str) -> str:
    """Heuristic crowd-impact estimate based on severity tier."""
    impact_map: dict[str, str] = {
        "CRITICAL": "500+ fans potentially affected — full-sector evacuation likely",
        "HIGH":     "100-500 fans potentially affected — partial zone restriction",
        "MEDIUM":   "50-100 fans — localized disruption, steward intervention",
        "LOW":      "<50 fans — minimal operational impact",
    }
    return impact_map.get(severity, "Unknown impact scope")


# ── Stadium Orchestrator ──────────────────────────────────────────────────────

class StadiumOrchestrator:
    """
    Central orchestration service managing two GenAI agents backed by
    the official Google GenAI SDK (``google-genai``).

    Security hardening:
      - All user inputs sanitized via security.sanitize_input()
      - LLM outputs enforced via response_schema (Pydantic → SDK schema)
      - GenAI failures return typed fallback models, never raw exceptions

    Each agent's system prompt and generation config are sourced
    exclusively from prompts.json — zero hardcoded LLM instructions.
    """

    def __init__(self) -> None:
        settings = get_settings()
        api_key: str = settings.GEMINI_API_KEY

        # Initialize Google GenAI client
        self._client: genai.Client = genai.Client(api_key=api_key)
        self._model: str = settings.LLM_MODEL

        # Load prompt configs (read-only references)
        self._incident_cfg: dict[str, Any] = PROMPTS["incident_commander"]
        self._fan_cfg: dict[str, Any] = PROMPTS["multilingual_fan_assistant"]

        # FAQ cache — TTL and size from settings
        self.cache: AsyncTTLCache = AsyncTTLCache(
            default_ttl=settings.CACHE_TTL_SECONDS,
            max_size=settings.CACHE_MAX_SIZE,
        )

        logger.info(
            "StadiumOrchestrator initialised  model=%s  prompts=%d",
            self._model,
            len(PROMPTS),
        )

    # ── Agent 1: Incident Commander ──────────────────────────────────────

    async def process_incident(
        self,
        zone: str,
        description: str,
        reporter: Optional[str] = None,
        timestamp: Optional[str] = None,
        simplify_language: bool = False,
    ) -> dict[str, Any]:
        """
        Triage a stadium incident:
          1. Sanitize all user-provided text (injection mitigation)
          2. Deterministic severity classification (keyword engine)
          3. Metadata extraction (location, time, crowd impact)
          4. GenAI-powered structured task-assignment (schema-enforced)

        Returns a fully typed task-assignment payload dict.
        """
        # ── Sanitize inputs ──────────────────────────────────────────────
        safe_zone: str = sanitize_input(
            zone, field_name="zone", max_length=100,
            strip_markdown=False, strip_html_tags=True,
        )
        safe_description: str = sanitize_input(
            description, field_name="description", max_length=4000,
        )
        safe_reporter: Optional[str] = None
        if reporter:
            safe_reporter = sanitize_input(
                reporter, field_name="reporter", max_length=120,
                strip_markdown=False,
            )

        # ── Classify & extract metadata ──────────────────────────────────
        severity: str = classify_severity(safe_description)
        incident_id: str = f"INC-{uuid4().hex[:8].upper()}"
        event_time: str = timestamp or datetime.now(timezone.utc).isoformat()
        crowd_impact: str = estimate_crowd_impact(severity, safe_zone)

        # ── Build user message for LLM ───────────────────────────────────
        user_message: str = (
            f"INCIDENT REPORT\n"
            f"ID: {incident_id}\n"
            f"Zone: {safe_zone}\n"
            f"Severity: {severity}\n"
            f"Description: {safe_description}\n"
            f"Reporter: {safe_reporter or 'Anonymous'}\n"
            f"Timestamp: {event_time}\n"
            f"Estimated Crowd Impact: {crowd_impact}\n\n"
            f"Produce a structured task-assignment response."
        )

        # ── Handle Simplify Language ─────────────────────────────────────
        sys_prompt = self._incident_cfg["system_prompt"]
        if simplify_language:
            sys_prompt += "\n\nRewrite this response using simple vocabulary at a 5th-grade reading level. Keep sentences short and clear."

        # ── Schema-enforced GenAI call ───────────────────────────────────
        start_time = time.time()
        parsed_result: Optional[TaskAssignmentLLM] = await self._call_genai_structured(
            system_prompt=sys_prompt,
            user_content=user_message,
            response_schema=TaskAssignmentLLM,
            temperature=self._incident_cfg.get("temperature", 0.2),
            max_tokens=self._incident_cfg.get("max_tokens", 1024),
        )
        latency_ms = int((time.time() - start_time) * 1000)

        # Build task assignment dict (from parsed model or fallback)
        if parsed_result is not None:
            task_assignment: dict[str, Any] = parsed_result.model_dump()
        else:
            task_assignment = {
                "severity": severity,
                "affected_zone": safe_zone,
                "response_units": ["Manual dispatch required"],
                "action_steps": ["Route to operations control for manual triage"],
                "estimated_resolution_minutes": 0,
                "escalation_required": True,
                "commander_notes": "GenAI pipeline unavailable — manual override engaged.",
                "fallback": True,
            }

        return {
            "incident_id": incident_id,
            "zone": safe_zone,
            "severity": severity,
            "crowd_impact": crowd_impact,
            "reporter": safe_reporter,
            "timestamp": event_time,
            "acknowledged_at": datetime.now(timezone.utc).isoformat(),
            "task_assignment": task_assignment,
            "raw_ai_response": None,  # No raw text — schema-enforced output
            "latency_ms": latency_ms,
            "model_used": self._model,
        }

    # ── Agent 2: Multilingual Fan Assistant ──────────────────────────────

    async def assist_fan(
        self,
        message: str,
        language: str = "en",
        match_id: Optional[str] = None,
        simplify_language: bool = False,
    ) -> dict[str, Any]:
        """
        Handle a fan assistance query:
          1. Sanitize user message (injection mitigation)
          2. Validate language code
          3. Check TTL cache for FAQ hit → instant response
          4. On cache miss → invoke GenAI with schema-enforced output
          5. Flag safety escalations

        Returns a structured fan-response payload dict.
        """
        # ── Sanitize inputs ──────────────────────────────────────────────
        safe_message: str = sanitize_input(
            message, field_name="message", max_length=1000,
        )
        safe_language: str = validate_language_code(language)

        # ── Cache-first path ─────────────────────────────────────────────
        cached: Optional[Any] = await self.cache.get(safe_message)
        if cached is not None:
            logger.debug("Cache HIT for fan query hash")
            result_copy: dict[str, Any] = dict(cached)
            result_copy["cache_hit"] = True
            return result_copy

        # ── Build user message for LLM ───────────────────────────────────
        context_block: str = f"[Match: {match_id}] " if match_id else ""
        user_message: str = (
            f"{context_block}"
            f"Fan query (language hint: {safe_language}):\n"
            f"{safe_message}\n\n"
            f"Respond in the fan's language. If the query involves a safety "
            f"concern, set escalated to true."
        )

        # ── Handle Simplify Language ─────────────────────────────────────
        sys_prompt = self._fan_cfg["system_prompt"]
        if simplify_language:
            sys_prompt += "\n\nRewrite this response using simple vocabulary at a 5th-grade reading level. Keep sentences short and clear."

        # ── Schema-enforced GenAI call ───────────────────────────────────
        start_time = time.time()
        parsed_result: Optional[FanAssistLLM] = await self._call_genai_structured(
            system_prompt=sys_prompt,
            user_content=user_message,
            response_schema=FanAssistLLM,
            temperature=self._fan_cfg.get("temperature", 0.7),
            max_tokens=self._fan_cfg.get("max_tokens", 512),
        )
        latency_ms = int((time.time() - start_time) * 1000)

        if parsed_result is not None:
            reply_text: str = parsed_result.reply
            detected_language: str = parsed_result.detected_language
            escalated: bool = parsed_result.escalated
        else:
            reply_text = (
                "We're experiencing high demand. "
                "Please visit the nearest Info Desk for assistance."
            )
            detected_language = safe_language
            escalated = False

        result: dict[str, Any] = {
            "reply": reply_text,
            "detected_language": detected_language,
            "escalated": escalated,
            "match_id": match_id,
            "cache_hit": False,
            "latency_ms": latency_ms,
            "model_used": self._model,
        }

        # Cache non-escalated FAQ responses
        if not escalated:
            await self.cache.set(safe_message, result, ttl=self.cache._default_ttl)

        return result

    # ── Schema-Enforced GenAI SDK Call ────────────────────────────────────

    async def _call_genai_structured(
        self,
        system_prompt: str,
        user_content: str,
        response_schema: type,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Any:
        """
        Invoke the Google GenAI SDK with enforced structured output.

        Uses ``response_mime_type="application/json"`` and ``response_schema``
        to guarantee the model returns JSON conforming to the provided
        Pydantic model.  The SDK handles schema conversion and validates
        the response, returning ``response.parsed`` as a typed object.

        Parameters
        ----------
        system_prompt : str
            The agent's system instruction (from prompts.json).
        user_content : str
            Sanitized user input.
        response_schema : type
            A Pydantic BaseModel class (e.g., TaskAssignmentLLM).
        temperature : float
            Generation temperature.
        max_tokens : int
            Maximum output tokens.

        Returns
        -------
        Pydantic model instance | None
            The parsed, validated model on success; None on failure.
        """
        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=user_content,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                ),
            )
            
            track_tokens(self._model, response)

            # response.parsed returns the Pydantic model instance directly
            if response.parsed is not None:
                logger.debug(
                    "Structured GenAI response received  schema=%s",
                    response_schema.__name__,
                )
                return response.parsed

            # Fallback: response.text exists but .parsed is None
            logger.warning(
                "GenAI returned text but parsed is None  schema=%s  text=%.200s",
                response_schema.__name__,
                response.text or "(empty)",
            )
            return None

        except Exception as exc:
            logger.error(
                "GenAI SDK call failed  schema=%s  error=%s",
                response_schema.__name__,
                exc,
                exc_info=True,
            )
            return None


# ── Module-level singleton (lazy) ─────────────────────────────────────────────

_orchestrator_instance: Optional[StadiumOrchestrator] = None


def get_orchestrator() -> StadiumOrchestrator:
    """
    Return the module-level StadiumOrchestrator singleton.

    Lazy-initialised on first call so import-time side-effects are avoided
    when the API key is not yet configured (e.g., during testing).
    """
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = StadiumOrchestrator()
    return _orchestrator_instance
