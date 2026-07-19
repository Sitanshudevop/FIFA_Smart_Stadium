import threading
from collections import deque
from datetime import datetime, timezone

_TELEMETRY_LOG = deque(maxlen=1000)
_TELEMETRY_LOCK = threading.Lock()
_TOTAL_TOKENS = 0


def log_metric(endpoint: str, latency_ms: float, tokens: int, flagged: bool) -> None:
    """
    Log a telemetry metric for an endpoint.
    
    Args:
        endpoint (str): The endpoint path.
        latency_ms (float): Request latency in milliseconds.
        tokens (int): Number of AI tokens consumed.
        flagged (bool): Whether the request was flagged by security.
    """
    global _TOTAL_TOKENS
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "latency_ms": round(latency_ms, 2),
        "tokens": tokens,
        "guardrail_flagged": flagged,
    }
    with _TELEMETRY_LOCK:
        _TELEMETRY_LOG.append(entry)
        _TOTAL_TOKENS += tokens


def get_telemetry_logs() -> list:
    """
    Retrieve all telemetry logs.
    
    Returns:
        list: A list of recorded telemetry events.
    """
    with _TELEMETRY_LOCK:
        return list(_TELEMETRY_LOG)


def get_total_tokens() -> int:
    """
    Calculate total tokens used across all logged metrics.
    
    Returns:
        int: Total number of tokens.
    """
    with _TELEMETRY_LOCK:
        return _TOTAL_TOKENS
