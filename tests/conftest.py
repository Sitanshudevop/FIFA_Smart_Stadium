"""
conftest.py — Shared fixtures for the Smart Stadium Ops test suite.

Strategy: Mock the google.genai SDK at the sys.modules level BEFORE any
backend module imports it.  This guarantees deterministic execution
without the google-genai package installed or an API key present.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ══════════════════════════════════════════════════════════════════════════════
#  MODULE-LEVEL SDK MOCK  (must run before any backend import)
# ══════════════════════════════════════════════════════════════════════════════

# Create mock module hierarchy for google.genai
try:
    import google
except ImportError:
    _mock_google = MagicMock()
    sys.modules.setdefault("google", _mock_google)
    google = _mock_google

_mock_genai = MagicMock()
_mock_types = MagicMock()

class DefaultMockUsage:
    prompt_token_count = 10
    candidates_token_count = 20

class DefaultMockResponse:
    text = "Nearest exit is Gate 3."
    usage_metadata = DefaultMockUsage()
    parsed = type("ParsedMock", (), {
        "screen_reader_text": "Proceed to Gate 3.",
        "steps": [{"step_number": 1, "instruction": "Go straight"}],
        "risk_level": type("RiskLevel", (), {"value": "low"})(),
        "crowd_rerouting_instructions": ["Go left"],
        "assigned_volunteer": "John Doe",
        "dispatch_reasoning": "Close by",
        "action_items": ["Investigate"]
    })()

_mock_client = MagicMock()
_mock_client.aio.models.generate_content = AsyncMock(return_value=DefaultMockResponse())
_mock_client.models.generate_content = MagicMock(return_value=DefaultMockResponse())
_mock_genai.Client.return_value = _mock_client

# Wire up the GenAI types mock
_mock_genai.types = _mock_types

# Make types.GenerateContentConfig a passthrough class
_mock_types.GenerateContentConfig = type("GenerateContentConfig", (), {"__init__": lambda self, **kw: None})

# Install mocks into sys.modules before any import
sys.modules.setdefault("google.genai", _mock_genai)
sys.modules.setdefault("google.genai.types", _mock_types)

# Ensure `from google import genai` works
google.genai = _mock_genai

# Now set GEMINI_API_KEY in environment
os.environ["GEMINI_API_KEY"] = "AIzaFAKE_test_key_1234567890"
