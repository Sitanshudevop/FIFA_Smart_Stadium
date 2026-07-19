"""
telemetry.py — Zero-dependency, ultra-lightweight telemetry engine.
"""

from collections import deque
import threading
from datetime import datetime, timezone
import re

# Memory-capped queue (maxlen=1000) prevents disk bloat and memory leaks
_TELEMETRY_LOG: deque = deque(maxlen=1000)
_TELEMETRY_LOCK = threading.Lock()

# Fast regex-based safety check for prompt injection guardrails
GUARDRAIL_PATTERN = re.compile(r"(?i)(ignore previous|override system|bypass)")

def log_ai_interaction(
    endpoint: str, 
    latency_ms: float, 
    tokens_in: int, 
    tokens_out: int, 
    guardrail_flagged: bool
) -> None:
    """Thread-safe logging of AI interactions."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "latency_ms": round(latency_ms, 2),
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "guardrail_flagged": guardrail_flagged,
    }
    with _TELEMETRY_LOCK:
        _TELEMETRY_LOG.append(entry)

def get_telemetry_logs() -> list:
    """Safely return a copy of the telemetry log."""
    with _TELEMETRY_LOCK:
        return list(_TELEMETRY_LOG)

def check_guardrails(prompt: str) -> bool:
    """Return True if malicious strings are detected."""
    return bool(GUARDRAIL_PATTERN.search(prompt))
