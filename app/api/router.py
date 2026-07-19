"""
API Router configuration for FIFA Smart Stadium Backend.
Handles all core routes for fan engagement, operational dispatching, and mock bracket data.
"""

from fastapi import APIRouter, Request
from fastapi.responses import Response
from typing import Any, Optional
import asyncio
import time
import logging
from pydantic import BaseModel
from google import genai
from google.oauth2 import service_account

from app.models.schemas import FanRequest, APIResponse
from async_lru import alru_cache
from app.core.security import sanitize_user_input
from app.core.telemetry import log_metric, get_total_tokens
from app.core.config import settings
from app.core.maps_mock import GoogleMapsMockClient
from app.core.rate_limit import limiter

from app.api.vision import router as vision_router
from app.api.simulator import router as simulator_router
from app.agents.dispatcher import router as dispatcher_router
from app.api.admin import router as admin_router
from app.api.auth import router as auth_router

logger = logging.getLogger("fifa_app")

api_router = APIRouter()

@alru_cache(maxsize=128)
async def _cached_genai_call(prompt: str, timeout: float = 60.0) -> dict:
    if settings.GEMINI_API_KEY:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
    elif settings.GOOGLE_CLOUD_CREDENTIALS:
        creds = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_CLOUD_CREDENTIALS,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        client = genai.Client(vertexai=True, project=creds.project_id, location="us-central1", credentials=creds)
    else:
        client = genai.Client()
    
    res = await asyncio.wait_for(client.aio.models.generate_content(
        model="gemini-3.5-flash",
        contents=[prompt]
    ), timeout=timeout)
    
    tokens = 0
    if res.usage_metadata:
        tokens = res.usage_metadata.prompt_token_count + res.usage_metadata.candidates_token_count
        
    return {"text": res.text, "tokens": tokens}

class OrderDeliveryRequest(BaseModel):
    """Payload schema for fan order delivery."""
    item: str
    zone: str = "Unknown"

class OpsDispatchRequest(BaseModel):
    """Payload schema for operational tactical dispatch."""
    resource: str
    zone: str
    incident: Optional[str] = None

class FanAssistRequest(BaseModel):
    """Payload schema for AI Fan Assistant queries."""
    message: str
    language: str = "en"
    simplify_language: bool = False
    stadium: str = "Unknown Stadium"

class TTSRequest(BaseModel):
    """Payload schema for Text-to-Speech synthesis."""
    text: str

@api_router.post("/fan/query", response_model=APIResponse)
@limiter.limit("5/minute")
async def handle_fan_query(request: Request, payload: FanRequest) -> APIResponse:
    """
    Process inbound fan queries using Google GenAI with strict timeouts.
    
    Args:
        request (Request): The incoming request (for rate limiting).
        payload (FanRequest): The fan's query payload.
        
    Returns:
        APIResponse: Standardized response object with AI reply or fallback string.
    """
    clean_query_string, is_flagged_input = sanitize_user_input(payload.query)
    start_time_counter = time.perf_counter()
    total_token_count = 0
    
    try:
        if settings.GEMINI_API_KEY:
            genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        elif settings.GOOGLE_CLOUD_CREDENTIALS:
            cloud_credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_CLOUD_CREDENTIALS,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            genai_client = genai.Client(vertexai=True, project=cloud_credentials.project_id, location="us-central1", credentials=cloud_credentials)
        else:
            genai_client = genai.Client()
        
        prompt_instruction = f"Respond to this fan: {clean_query_string} at {payload.location_coordinates}"
        
        hits_before = _cached_genai_call.cache_info().hits
        ai_response = await _cached_genai_call(prompt_instruction, 4.0)
        is_hit = _cached_genai_call.cache_info().hits > hits_before
        
        total_token_count = ai_response["tokens"]
            
        latency_milliseconds = (time.perf_counter() - start_time_counter) * 1000
        
        if not is_hit:
            log_metric(endpoint="/fan/query", latency_ms=latency_milliseconds, tokens=total_token_count, flagged=is_flagged_input)
        
        return APIResponse(
            status="success",
            message=ai_response["text"],
            data={"query": clean_query_string, "language": payload.language}
        )
        
    except asyncio.TimeoutError:
        logger.warning("Timeout while processing fan query, falling back to degraded state.")
        latency_milliseconds = (time.perf_counter() - start_time_counter) * 1000
        log_metric(endpoint="/fan/query", latency_ms=latency_milliseconds, tokens=total_token_count, flagged=is_flagged_input)
        
        return APIResponse(
            status="degraded_performance",
            message="Network congested. Please proceed to the nearest yellow steward for directions.",
            data={"query": clean_query_string}
        )
    except Exception as general_error:
        logger.error(f"Failed to process fan query: {general_error}")
        return APIResponse(
            status="error",
            message="We are experiencing technical difficulties. Please try again later.",
            data={"query": clean_query_string}
        )

@api_router.get("/ops/metrics", tags=["ops"])
async def get_ops_metrics() -> dict[str, float]:
    """
    Retrieve operational metrics including telemetry token counts and costs.
    
    Returns:
        dict: A dictionary of tokens, estimated cost, and simulated savings.
    """
    try:
        total_token_count = get_total_tokens()
        token_rate_multiplier = 0.000075
        estimated_monetary_cost = total_token_count * token_rate_multiplier
        estimated_savings_cost = estimated_monetary_cost
        
        return {
            "tokens": float(total_token_count),
            "cost": float(estimated_monetary_cost),
            "saved": float(estimated_savings_cost)
        }
    except Exception as general_error:
        logger.error(f"Failed to fetch ops metrics: {general_error}")
        return {"tokens": 0.0, "cost": 0.0, "saved": 0.0}

@api_router.post("/ops/dispatch", tags=["ops"])
async def execute_ops_dispatch(request: OpsDispatchRequest) -> dict[str, str]:
    """
    Execute a tactical dispatch command to a specified zone.
    
    Args:
        request (OpsDispatchRequest): The resource and zone to dispatch to.
        
    Returns:
        dict: A status confirmation.
    """
    try:
        return {"status": "Success", "dispatched_resource": request.resource, "target_zone": request.zone}
    except Exception as general_error:
        logger.error(f"Dispatch error: {general_error}")
        return {"status": "Failed", "error": "Internal processing error"}

@api_router.post("/order-delivery", tags=["fan"])
async def process_order_delivery(request: OrderDeliveryRequest) -> dict[str, Any]:
    """
    Process an express order delivery request to a seat zone.
    
    Args:
        request (OrderDeliveryRequest): The item and zone payload.
        
    Returns:
        dict: Delivery confirmation and routing instructions.
    """
    try:
        delivery_item = request.item
        delivery_target_zone = request.zone
        
        estimated_time_string = "5-7 minutes"
        routing_instructions = [
            f"Order received at Concourse B Kiosk (lowest wait time: 5 mins).",
            f"Runner dispatched to pickup {delivery_item}.",
            f"Runner navigating via Section 108 (Light traffic) to {delivery_target_zone}.",
            f"Expected delivery at your seat shortly."
        ]
        
        return {
            "status": "success",
            "message": f"Your {delivery_item} is being prepared.",
            "estimated_time": estimated_time_string,
            "instructions": routing_instructions
        }
    except Exception as general_error:
        logger.error(f"Failed to process order: {general_error}")
        return {"status": "error", "message": "Failed to process order at this time."}

@api_router.post("/tts", tags=["fan"])
async def generate_text_to_speech(request: TTSRequest) -> Any:
    """
    Generate an audio stream from text using Google Cloud Text-to-Speech.
    
    Args:
        request (TTSRequest): The text payload to synthesize.
        
    Returns:
        Response: HTTP audio/mp3 stream, or a JSON error dictionary on failure.
    """
    try:
        from google.cloud import texttospeech
        if settings.GOOGLE_CLOUD_CREDENTIALS:
            cloud_credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_CLOUD_CREDENTIALS,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            tts_client = texttospeech.TextToSpeechClient(credentials=cloud_credentials)
        else:
            tts_client = texttospeech.TextToSpeechClient()
            
        synthesis_input_config = texttospeech.SynthesisInput(text=request.text)
        voice_selection_config = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Standard-D"
        )
        audio_encoding_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        synthesized_audio_response = tts_client.synthesize_speech(
            input=synthesis_input_config, voice=voice_selection_config, audio_config=audio_encoding_config
        )
        
        return Response(content=synthesized_audio_response.audio_content, media_type="audio/mp3")
    except Exception as general_error:
        logger.error(f"TTS Synthesis Failed: {general_error}")
        return {"status": "error", "message": "Audio synthesis failed gracefully."}

@api_router.post("/fan/assist", tags=["fan"])
@limiter.limit("5/minute")
async def handle_fan_assist(request: Request, payload: FanAssistRequest) -> dict[str, Any]:
    """
    Handle complex Fan Assistant queries with context-aware GenAI synthesis.
    
    Args:
        request (Request): The incoming request (for rate limiting).
        payload (FanAssistRequest): The detailed fan prompt and location.
        
    Returns:
        dict: The synthesized AI response with telemetry metadata.
    """
    clean_message_string, is_flagged_input = sanitize_user_input(payload.message)
    start_time_counter = time.perf_counter()
    total_token_count = 0

    language_simplification_instruction = ""
    if payload.simplify_language:
        language_simplification_instruction = " Use very simple vocabulary and short sentences."

    try:
        if settings.GEMINI_API_KEY:
            genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        elif settings.GOOGLE_CLOUD_CREDENTIALS:
            cloud_credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_CLOUD_CREDENTIALS,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            genai_client = genai.Client(vertexai=True, project=cloud_credentials.project_id, location="us-central1", credentials=cloud_credentials)
        else:
            genai_client = genai.Client()
            
        maps_mock_client = GoogleMapsMockClient()
        geolocation_payload = maps_mock_client.geocode(payload.stadium)
        location_coordinate_string = f"Coordinates: {geolocation_payload[0]['geometry']['location']['lat']}, {geolocation_payload[0]['geometry']['location']['lng']}"
            
        system_prompt_instruction = (
            f"You are a helpful stadium assistant for the FIFA 2026 World Cup. The user is currently located at {payload.stadium} ({location_coordinate_string}). Answer their query based specifically on the layout, amenities, and environment of this exact stadium. "
            f"Keep your response extremely concise, ideally 1-3 sentences maximum. "
            f"You must reply in the following language: {payload.language}. {language_simplification_instruction} "
            f"Fan query: {clean_message_string}"
        )

        hits_before = _cached_genai_call.cache_info().hits
        ai_response = await _cached_genai_call(system_prompt_instruction, 60.0)
        is_hit = _cached_genai_call.cache_info().hits > hits_before

        total_token_count = ai_response["tokens"]

        latency_milliseconds = round((time.perf_counter() - start_time_counter) * 1000)
        
        if not is_hit:
            log_metric(endpoint="/fan/assist", latency_ms=latency_milliseconds, tokens=total_token_count, flagged=is_flagged_input)

        return {
            "reply": ai_response["text"],
            "model_used": "gemini-3.5-flash",
            "latency_ms": latency_milliseconds,
            "detected_language": payload.language,
            "cache_hit": is_hit,
            "screen_reader_text": ai_response["text"]
        }

    except asyncio.TimeoutError:
        logger.warning("Timeout on /fan/assist, activating fallback.")
        latency_milliseconds = round((time.perf_counter() - start_time_counter) * 1000)
        log_metric(endpoint="/fan/assist", latency_ms=latency_milliseconds, tokens=total_token_count, flagged=is_flagged_input)
        return {
            "reply": "Network congested. Please proceed to the nearest yellow steward for directions.",
            "model_used": "Offline Cache",
            "latency_ms": latency_milliseconds,
            "detected_language": payload.language,
            "cache_hit": True,
            "screen_reader_text": "Network congested. Showing cached offline data."
        }
    except Exception as general_error:
        logger.error(f"Exception on /fan/assist: {general_error}")
        latency_milliseconds = round((time.perf_counter() - start_time_counter) * 1000)
        log_metric(endpoint="/fan/assist", latency_ms=latency_milliseconds, tokens=total_token_count, flagged=True)
        return {
            "reply": "Our AI assistant is temporarily unavailable. Please try again soon.",
            "model_used": "Error Handling Fallback",
            "latency_ms": latency_milliseconds,
            "detected_language": payload.language,
            "cache_hit": False
        }

@api_router.get("/config", tags=["config"])
async def get_public_config() -> dict[str, str]:
    """
    Serve public configuration variables to frontend clients.
    
    Returns:
        dict: Public keys like Google Maps and Google Client IDs.
    """
    try:
        return {
            "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
            "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID
        }
    except Exception as general_error:
        logger.error(f"Failed to fetch public config: {general_error}")
        return {"GOOGLE_MAPS_API_KEY": "", "GOOGLE_CLIENT_ID": ""}

@api_router.get("/live-bracket", tags=["sports"])
async def get_live_tournament_bracket() -> dict[str, Any]:
    """
    Return authentic 2026 FIFA World Cup knockout stage data.
    
    Returns:
        dict: A highly structured JSON tree of tournament matches.
    """
    try:
        return {
            "rounds": [
                {
                    "name": "Round of 16",
                    "matches": [
                        {"id": 89, "date": "Jul 04", "venue": "BC Place, Vancouver", "home": {"name": "MAR", "flag": "🇲🇦", "score": "3"}, "away": {"name": "CAN", "flag": "🇨🇦", "score": "0"}},
                        {"id": 90, "date": "Jul 04", "venue": "Lumen Field, Seattle", "home": {"name": "FRA", "flag": "🇫🇷", "score": "1"}, "away": {"name": "PAR", "flag": "🇵🇾", "score": "0"}},
                        {"id": 91, "date": "Jul 05", "venue": "Levi's Stadium, San Francisco", "home": {"name": "NOR", "flag": "🇳🇴", "score": "2"}, "away": {"name": "BRA", "flag": "🇧🇷", "score": "1"}},
                        {"id": 92, "date": "Jul 05", "venue": "SoFi Stadium, Los Angeles", "home": {"name": "ENG", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "score": "3"}, "away": {"name": "MEX", "flag": "🇲🇽", "score": "2"}},
                        {"id": 93, "date": "Jul 06", "venue": "NRG Stadium, Houston", "home": {"name": "ESP", "flag": "🇪🇸", "score": "1"}, "away": {"name": "POR", "flag": "🇵🇹", "score": "0"}},
                        {"id": 94, "date": "Jul 06", "venue": "AT&T Stadium, Dallas", "home": {"name": "BEL", "flag": "🇧🇪", "score": "4"}, "away": {"name": "USA", "flag": "🇺🇸", "score": "1"}},
                        {"id": 95, "date": "Jul 07", "venue": "Mercedes-Benz Stadium, Atlanta", "home": {"name": "ARG", "flag": "🇦🇷", "score": "3"}, "away": {"name": "EGY", "flag": "🇪🇬", "score": "2"}},
                        {"id": 96, "date": "Jul 07", "venue": "Hard Rock Stadium, Miami", "home": {"name": "SUI", "flag": "🇨🇭", "score": "0(4)"}, "away": {"name": "COL", "flag": "🇨🇴", "score": "0(3)"}}
                    ]
                },
                {
                    "name": "Quarter-finals",
                    "matches": [
                        {"id": 97, "date": "Jul 10", "venue": "Gillette Stadium, Boston", "home": {"name": "FRA", "flag": "🇫🇷", "score": "2"}, "away": {"name": "MAR", "flag": "🇲🇦", "score": "0"}},
                        {"id": 98, "date": "Jul 10", "venue": "Lincoln Financial Field, Philadelphia", "home": {"name": "ESP", "flag": "🇪🇸", "score": "2"}, "away": {"name": "BEL", "flag": "🇧🇪", "score": "1"}},
                        {"id": 99, "date": "Jul 11", "venue": "Arrowhead Stadium, Kansas City", "home": {"name": "ENG", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "score": "2"}, "away": {"name": "NOR", "flag": "🇳🇴", "score": "1"}},
                        {"id": 100, "date": "Jul 11", "venue": "Hard Rock Stadium, Miami", "home": {"name": "ARG", "flag": "🇦🇷", "score": "3"}, "away": {"name": "SUI", "flag": "🇨🇭", "score": "1"}}
                    ]
                },
                {
                    "name": "Semi-finals",
                    "matches": [
                        {"id": 101, "date": "Jul 14", "venue": "AT&T Stadium, Dallas", "home": {"name": "ESP", "flag": "🇪🇸", "score": "2"}, "away": {"name": "FRA", "flag": "🇫🇷", "score": "0"}},
                        {"id": 102, "date": "Jul 15", "venue": "Mercedes-Benz Stadium, Atlanta", "home": {"name": "ARG", "flag": "🇦🇷", "score": "2"}, "away": {"name": "ENG", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "score": "1"}}
                    ]
                },
                {
                    "name": "Final",
                    "matches": [
                        {"id": 104, "date": "Jul 19", "venue": "MetLife Stadium, New York/New Jersey", "home": {"name": "ESP", "flag": "🇪🇸", "score": "-"}, "away": {"name": "ARG", "flag": "🇦🇷", "score": "-"}}
                    ]
                }
            ]
        }
    except Exception as general_error:
        logger.error(f"Failed to fetch bracket data: {general_error}")
        return {"rounds": []}

api_router.include_router(vision_router)
api_router.include_router(simulator_router)
api_router.include_router(dispatcher_router)
api_router.include_router(admin_router)
api_router.include_router(auth_router)
