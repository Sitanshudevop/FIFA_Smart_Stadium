from fastapi import APIRouter
from pydantic import BaseModel
import os
import json
from google import genai
from google.genai import types
from app.models.schemas import SimulationResult
from app.core.stadium_state import STADIUM_STATE

router = APIRouter(prefix="/simulate", tags=["simulation"])

class SimulationRequest(BaseModel):
    scenario: str

@router.post("/", response_model=SimulationResult)
async def run_simulation(req: SimulationRequest):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "mock_key"))
    
    prompt = f"""
    Analyze the following incident scenario against the current stadium state:
    Scenario: {req.scenario}
    State: {json.dumps(STADIUM_STATE)}
    
    Generate a predictive mitigation plan strictly adhering to the output schema.
    """
    
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SimulationResult,
        )
    )
    
    return response.parsed
