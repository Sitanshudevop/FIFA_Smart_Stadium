"""
config.py — Zero-trust environment settings & prompt loader.

All credentials are sourced exclusively from environment variables via
pydantic-settings.  No placeholder strings, no hardcoded secrets.
A missing or empty GEMINI_API_KEY triggers an immediate RuntimeError
at startup to prevent silent misconfiguration.
"""

from __future__ import annotations

import json
import logging
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger("stadium_ops.config")

# ── Paths ──────────────────────────────────────────────────────────────────────
_BASE_DIR = Path(__file__).resolve().parent.parent          # backend/
_PROMPTS_PATH = _BASE_DIR / "prompts.json"

# ── Required Environment Variables ────────────────────────────────────────────
_REQUIRED_ENV_VARS: list[str] = [
    "GEMINI_API_KEY",
]


# ── Application Settings ──────────────────────────────────────────────────────
class Settings(BaseSettings):
    """
    Immutable application-wide configuration sourced from env vars.

    Security invariants:
      - No field has a default that contains a credential.
      - GEMINI_API_KEY has no default — it MUST come from the environment.
      - Validators reject empty strings and placeholder patterns.
    """

    APP_NAME: str = "Smart Stadium Ops — FIFA World Cup 2026"
    APP_VERSION: str = "0.2.0"
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["*"]

    # ── GenAI Credentials (MANDATORY — no defaults) ──────────────────────
    GEMINI_API_KEY: str
    LLM_MODEL: str = "gemini-2.5-flash"

    # ── Rate Limits & Security Tuning ────────────────────────────────────
    MAX_INPUT_LENGTH: int = 4000
    CACHE_TTL_SECONDS: int = 300
    CACHE_MAX_SIZE: int = 2048

    @field_validator("GEMINI_API_KEY")
    @classmethod
    def _validate_api_key(cls, v: str) -> str:
        """
        Reject empty, whitespace-only, or obvious placeholder values.
        """
        stripped = v.strip()
        _PLACEHOLDER_PATTERNS: list[str] = [
            "your-", "your_", "replace", "placeholder", "changeme",
            "xxx", "todo", "insert", "api_key_here", "PASTE",
        ]
        if not stripped:
            raise ValueError(
                "GEMINI_API_KEY is empty. Set a valid API key in your "
                "environment or .env file."
            )
        lower = stripped.lower()
        for pattern in _PLACEHOLDER_PATTERNS:
            if pattern in lower:
                raise ValueError(
                    f"GEMINI_API_KEY appears to be a placeholder "
                    f"(matched '{pattern}'). Set a real API key."
                )
        return stripped

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def _validate_origins(cls, v: list[str]) -> list[str]:
        """Warn if wildcard origins are used outside debug mode."""
        if "*" in v:
            logger.warning(
                "SECURITY: ALLOWED_ORIGINS contains wildcard '*'. "
                "Restrict this in production deployments."
            )
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Strip whitespace from all env var values
        str_strip_whitespace = True
        extra = "ignore"


def _enforce_required_env() -> None:
    """
    Validate that all critical environment variables resolve to non-empty
    values BEFORE the application can serve traffic.

    Raises RuntimeError with actionable guidance on failure.
    """
    try:
        settings = Settings()  # type: ignore[call-arg]
    except Exception as exc:
        msg = (
            "\n"
            "╔══════════════════════════════════════════════════════════════╗\n"
            "║  FATAL: Missing or invalid environment configuration       ║\n"
            "╠══════════════════════════════════════════════════════════════╣\n"
            f"║  {exc!s:.56s}  ║\n"
            "║                                                            ║\n"
            "║  Required variables:                                       ║\n"
            "║    • GEMINI_API_KEY  — Google GenAI API key                ║\n"
            "║                                                            ║\n"
            "║  Set via environment:                                      ║\n"
            '║    export GEMINI_API_KEY="AIza..."                         ║\n'
            "║  Or via .env file in the project root.                     ║\n"
            "╚══════════════════════════════════════════════════════════════╝\n"
        )
        logger.critical(msg)
        raise RuntimeError(msg) from exc
    return None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached singleton of validated application settings.

    First call performs full env-var validation.
    Subsequent calls return the cached instance with zero overhead.
    """
    _enforce_required_env()
    return Settings()  # type: ignore[call-arg]


# ── Prompt Loader ─────────────────────────────────────────────────────────────
def load_prompts(path: Path = _PROMPTS_PATH) -> dict[str, Any]:
    """
    Read prompts.json once and return the full dictionary.

    Raises FileNotFoundError with a clear message if the file is missing,
    so misconfigurations surface immediately at startup.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Prompt configuration not found at {path}. "
            "Ensure backend/prompts.json exists."
        )
    with path.open(encoding="utf-8") as fh:
        data: dict[str, Any] = json.load(fh)

    # Validate prompt structure
    required_keys: set[str] = {"role", "system_prompt", "temperature", "max_tokens"}
    for agent_name, agent_cfg in data.items():
        if not isinstance(agent_cfg, dict):
            raise ValueError(f"Prompt config for '{agent_name}' must be a dict.")
        missing = required_keys - set(agent_cfg.keys())
        if missing:
            raise ValueError(
                f"Prompt config for '{agent_name}' is missing keys: {missing}"
            )

    logger.info("Loaded %d prompt configurations from %s", len(data), path.name)
    return data


# Load once at module-import time so every downstream import can use it.
PROMPTS: dict[str, Any] = load_prompts()
