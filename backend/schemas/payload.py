"""
payload.py — Pydantic models for request/response validation.

All API data contracts AND GenAI response_schema enforcement models
live here, keeping validation logic strictly separated from routing
and business logic.

Models suffixed with ``LLM`` are passed directly to the Google GenAI
SDK's ``response_schema`` parameter to enforce structured output at
the model level — eliminating free-form text parsing entirely.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ══════════════════════════════════════════════════════════════════════════════
#  ENUMS
# ══════════════════════════════════════════════════════════════════════════════

class Severity(str, Enum):
    P1 = "P1"  # Critical — immediate danger to life
    P2 = "P2"  # High — potential escalation risk
    P3 = "P3"  # Medium — operational disruption
    P4 = "P4"  # Low — informational


class IncidentSeverity(str, Enum):
    """Orchestrator-level severity (maps to keyword classifier output)."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AgentRole(str, Enum):
    INCIDENT_COMMANDER = "incident_commander"
    FAN_ASSISTANT = "multilingual_fan_assistant"


# ══════════════════════════════════════════════════════════════════════════════
#  LLM RESPONSE SCHEMAS  (passed to GenAI response_schema — no defaults)
# ══════════════════════════════════════════════════════════════════════════════


class AccessibilityFlags(BaseModel):
    high_contrast: bool = False
    enlarged_text: bool = False
    auto_tts_active: bool = False
    simplified_view: bool = False

class TaskAssignmentLLM(BaseModel):
    """
    Schema enforced at the Gemini model level via ``response_schema``.

    Every field is required (no defaults) to guarantee the model
    produces a complete, parseable object on every call.
    Avoid ``Optional`` and ``default`` here — the SDK may reject them.
    """

    severity: str = Field(
        description="Classified severity: CRITICAL, HIGH, MEDIUM, or LOW.",
    )
    affected_zone: str = Field(
        description="Stadium zone / sector affected by this incident.",
    )
    response_units: list[str] = Field(
        description="Ordered list of response units to deploy (e.g., 'Medical Team Alpha', 'Security Unit 3').",
    )
    action_steps: list[str] = Field(
        description="Ordered action steps the Incident Commander recommends.",
    )
    estimated_resolution_minutes: int = Field(
        description="Estimated minutes to resolve the incident.",
    )
    escalation_required: bool = Field(
        description="Whether this incident requires escalation to venue command.",
    )
    commander_notes: str = Field(
        description="Free-text operational notes from the Incident Commander.",
    )
    accessibility_flags: AccessibilityFlags = Field(description="Dynamic accessibility adjustments based on user context.")


class FanAssistLLM(BaseModel):
    """
    Schema enforced at the Gemini model level for fan assistant responses.

    The model MUST produce all fields — the SDK rejects partial objects.
    """

    reply: str = Field(
        description="The assistant's response to the fan, in the fan's language.",
    )
    detected_language: str = Field(
        description="ISO 639-1 language code detected in the fan's query.",
    )
    escalated: bool = Field(
        description="True if the query involves a safety concern requiring Incident Commander escalation.",
    )
    accessibility_flags: AccessibilityFlags = Field(description="Dynamic accessibility adjustments based on user context.")


# ══════════════════════════════════════════════════════════════════════════════
#  INCIDENT PAYLOADS — PHASE 1 (backward-compatible simple log)
# ══════════════════════════════════════════════════════════════════════════════

class IncidentCreate(BaseModel):
    """Inbound payload to report a stadium incident."""

    zone: str = Field(
        ...,
        min_length=1,
        max_length=50,
        examples=["North Stand Gate 4"],
        description="Stadium zone where the incident occurred.",
    )
    description: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        examples=["Medical emergency — fan collapsed near row 12."],
    )
    severity: Severity = Field(
        default=Severity.P3,
        description="Initial severity classification.",
    )
    reporter: Optional[str] = Field(
        default=None,
        max_length=120,
        examples=["Steward-B7"],
    )


class IncidentResponse(BaseModel):
    """Outbound payload after incident is logged."""

    incident_id: str
    zone: str
    severity: Severity
    acknowledged_at: datetime
    ai_action_plan: Optional[str] = None


# ══════════════════════════════════════════════════════════════════════════════
#  INCIDENT COMMANDER — PHASE 2 (GenAI orchestration)
# ══════════════════════════════════════════════════════════════════════════════

class IncidentProcessRequest(BaseModel):
    """Inbound payload for the AI-powered incident processing pipeline."""

    zone: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["North Stand Gate 4"],
        description="Stadium zone / sector identifier.",
    )
    description: str = Field(
        ...,
        min_length=5,
        max_length=4000,
        examples=[
            "Crowd surge detected at East Tunnel entrance. "
            "Multiple fans reporting difficulty breathing.",
        ],
        description="Free-text incident description from the field.",
    )
    reporter: Optional[str] = Field(
        default=None,
        max_length=120,
        examples=["Steward-B7", "CCTV-Operator-3"],
        description="Identifier of the person or system filing the report.",
    )
    timestamp: Optional[str] = Field(
        default=None,
        examples=["2026-07-14T20:30:00Z"],
        description="ISO-8601 event timestamp. Server UTC is used if omitted.",
    )
    simplify_language: bool = Field(
        default=False,
        description="Toggle cognitive accessibility (simplify output to 5th-grade reading level).",
    )


class TaskAssignment(BaseModel):
    """API-facing task assignment (allows Optional for fallback scenarios)."""

    severity: Optional[str] = None
    affected_zone: Optional[str] = None
    response_units: list[str] = Field(default_factory=list)
    action_steps: list[str] = Field(default_factory=list)
    estimated_resolution_minutes: Optional[int] = None
    escalation_required: Optional[bool] = None
    commander_notes: Optional[str] = None
    # Fallback fields when structured output fails
    raw_response: Optional[str] = None
    parse_error: Optional[str] = None
    error: Optional[str] = None
    fallback: Optional[bool] = None
    accessibility_flags: Optional[AccessibilityFlags] = None


class IncidentProcessResponse(BaseModel):
    """Full outbound payload from /incidents/process."""

    incident_id: str
    zone: str
    severity: str
    crowd_impact: str
    reporter: Optional[str] = None
    timestamp: str
    acknowledged_at: str
    task_assignment: TaskAssignment
    raw_ai_response: Optional[str] = None
    latency_ms: Optional[int] = None
    model_used: Optional[str] = None


# ══════════════════════════════════════════════════════════════════════════════
#  FAN ASSISTANT PAYLOADS
# ══════════════════════════════════════════════════════════════════════════════

class FanQuery(BaseModel):
    """Inbound payload from a fan seeking assistance."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        examples=["¿Dónde puedo encontrar comida halal?"],
    )
    language: str = Field(
        default="en",
        max_length=5,
        description="ISO 639-1 language code.",
    )
    match_id: Optional[str] = Field(
        default=None,
        description="Current match identifier for context.",
    )
    simplify_language: bool = Field(
        default=False,
        description="Toggle cognitive accessibility.",
    )


class FanResponse(BaseModel):
    """Outbound payload with assistant reply."""

    reply: str
    detected_language: str
    escalated: bool = False

class FanAssistResponse(BaseModel):
    """Extended outbound payload from /fan/assist (Phase 2)."""

    reply: str
    detected_language: str
    escalated: bool = False
    match_id: Optional[str] = None
    cache_hit: bool = False
    latency_ms: Optional[int] = None
    model_used: Optional[str] = None
    accessibility_flags: Optional[AccessibilityFlags] = None


# ══════════════════════════════════════════════════════════════════════════════
#  HEALTH & DIAGNOSTICS
# ══════════════════════════════════════════════════════════════════════════════

class HealthCheck(BaseModel):
    status: str = "operational"
    version: str
    prompts_loaded: int


class CacheStats(BaseModel):
    """Diagnostic payload for the FAQ cache."""

    total_entries: int
    alive_entries: int


# ══════════════════════════════════════════════════════════════════════════════
#  VISION ACCESSIBILITY PAYLOADS
# ══════════════════════════════════════════════════════════════════════════════

class VisionNavigateLLM(BaseModel):
    """
    Schema enforced at the Gemini model level for vision accessibility.
    """
    aria_label_text: str = Field(
        description="A highly descriptive text optimized for screen readers, summarizing the image and primary navigation."
    )
    navigation_steps: list[str] = Field(
        description="Step-by-step routing instructions extracted from the image. Empty list if irrelevant."
    )
    is_valid_stadium_image: bool = Field(
        description="True if the image contains valid stadium signage, tickets, or routing info. False if blurry or irrelevant."
    )
    fallback_message: str = Field(
        description="Translated message asking the user to retake the photo or provide manual input if the image is invalid. Empty if valid."
    )
    accessibility_flags: AccessibilityFlags = Field(description="Dynamic accessibility adjustments based on user context.")


class VisionNavigateResponse(BaseModel):
    """Outbound payload for the vision navigation endpoint."""
    aria_label_text: str
    navigation_steps: list[str]
    is_valid: bool
    fallback_message: Optional[str] = None
    accessibility_flags: Optional[AccessibilityFlags] = None


# ══════════════════════════════════════════════════════════════════════════════
#  SIMULATION CRISIS ENGINE PAYLOADS
# ══════════════════════════════════════════════════════════════════════════════

class PublicAnnouncements(BaseModel):
    """Localized public announcements for crisis simulations."""
    english: str
    spanish: str
    french: str


class SimulationWhatIfLLM(BaseModel):
    """
    Schema enforced at the Gemini model level for what-if crisis simulation.
    All fields are strictly required.
    """
    risk_level: IncidentSeverity = Field(
        description="String enum stringently bound to LOW, MEDIUM, HIGH, or CRITICAL."
    )
    crowd_rerouting_instructions: list[str] = Field(
        description="Array of strings containing step-by-step zone re-allocation maneuvers."
    )
    public_announcements: PublicAnnouncements = Field(
        description="Pre-drafted, localized PA texts mapped across English, Spanish, and French."
    )
    operational_bottlenecks: list[str] = Field(
        description="Detailed list of affected stadium resources matching the hardcoded state values."
    )


class SimulationRequest(BaseModel):
    """Inbound payload for the whatif simulation engine."""
    incident_scenario: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        examples=["Severe thunderstorm flooding Gate B, disrupting Metro Line 2"],
    )


class SimulationResponse(BaseModel):
    """Outbound payload matching the simulation response."""
    scenario_analyzed: str
    risk_level: str
    crowd_rerouting_instructions: list[str]
    public_announcements: dict[str, str]
    operational_bottlenecks: list[str]


# ══════════════════════════════════════════════════════════════════════════════
#  DISPATCH ORCHESTRATION PAYLOADS
# ══════════════════════════════════════════════════════════════════════════════

class AssignedVolunteer(BaseModel):
    id: str
    name: str
    current_zone: str


class DispatchResolutionLLM(BaseModel):
    """
    Schema enforced at the Gemini model level for volunteer dispatch resolution.
    """
    incident_id: str = Field(description="Standard tracking string generated for the incident.")
    assigned_volunteer: AssignedVolunteer = Field(description="The matched individual's details.")
    dispatch_reasoning: str = Field(description="Clear, professional explanation detailing why this volunteer was selected.")
    action_items: list[str] = Field(description="Localized checklist of steps transmitted directly to the volunteer's mobile device.")
    accessibility_flags: AccessibilityFlags = Field(description="Dynamic accessibility adjustments based on user context.")


class DispatchRequest(BaseModel):
    incident_description: str = Field(
        ...,
        examples=["A fan collapsed in the upper deck of Zone C and only speaks Spanish"],
    )


class DispatchResponse(BaseModel):
    incident_id: str
    assigned_volunteer: AssignedVolunteer
    dispatch_reasoning: str
    action_items: list[str]
    accessibility_flags: Optional[AccessibilityFlags] = None

