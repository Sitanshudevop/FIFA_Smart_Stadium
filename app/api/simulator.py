import json
import os

from async_lru import alru_cache
from fastapi import APIRouter
from google import genai
from google.genai import types
from pydantic import BaseModel

from app.core.stadium_state import STADIUM_STATE
from app.models.schemas import SimulationResult

router = APIRouter(prefix="/simulate", tags=["simulation"])


class SimulationRequest(BaseModel):
    scenario: str


@alru_cache(maxsize=50)
async def _cached_simulate(scenario: str, state_json: str):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "mock_key"))

    prompt = f"""
    Analyze the following incident scenario against the current stadium state:
    Scenario: {scenario}
    State: {state_json}
    
    Generate a predictive mitigation plan strictly adhering to the output schema.
    """

    response = await client.aio.models.generate_content(
        model="gemini-3.5-flash",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SimulationResult,
        ),
    )

    return response.parsed


@router.post("/", response_model=SimulationResult)
async def run_simulation(req: SimulationRequest):
    return await _cached_simulate(req.scenario, json.dumps(STADIUM_STATE))
