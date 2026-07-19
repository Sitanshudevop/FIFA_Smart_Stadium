from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Phase 9: Accessibility ──
class AccessibilityFlags(BaseModel):
    high_contrast: bool = False
    enlarged_text: bool = False
    auto_tts: bool = False


# ── Phase 2: Basic Contracts ──
class FanRequest(BaseModel):
    query: str
    language: Optional[str] = "en"
    location_coordinates: Optional[str] = None


class SeverityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class OperatorAction(BaseModel):
    incident_description: str
    severity: SeverityEnum


class APIResponse(BaseModel):
    status: str
    data: Optional[Any] = None
    message: Optional[str] = None
    accessibility_flags: Optional[AccessibilityFlags] = None


# ── Phase 3: Vision & Accessibility ──
class NavigationStep(BaseModel):
    step_number: int
    instruction: str


class NavigationResponse(BaseModel):
    screen_reader_text: str = Field(
        ...,
        description="Clean, punctuation-heavy text designed for immediate text-to-speech announcement.",
    )
    steps: List[NavigationStep]
    accessibility_flags: Optional[AccessibilityFlags] = None


# ── Phase 4: Simulator ──
class SimulationResult(BaseModel):
    risk_matrix_score: int = Field(..., ge=1, le=10)
    multilingual_pa_drafts: Dict[str, str] = Field(
        ..., description="Dictionary mapping language codes to broadcast text"
    )
    crowd_reroute_logic: List[str] = Field(
        ..., description="List of operational commands"
    )


# ── Phase 5: Dispatcher ──
class DispatchPayload(BaseModel):
    volunteer_id: str
    dispatch_reasoning: str
    action_checklist: List[str]


# ── Auth ──
class GoogleAuthRequest(BaseModel):
    credential: str


class GoogleAuthResponse(BaseModel):
    token: str
    user: Dict[str, str]
