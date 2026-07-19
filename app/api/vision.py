from fastapi import APIRouter, UploadFile, File, Form
import asyncio
import time
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
from google.oauth2 import service_account
from app.models.schemas import NavigationResponse
from app.core.config import settings
from app.core.telemetry import log_metric

router = APIRouter(prefix="/vision", tags=["vision"])

@router.post("/navigate", response_model=NavigationResponse)
async def navigate_vision(file: UploadFile = File(...), language: str = Form("English")):
    # CRITICAL CONSTRAINT: Read directly into memory byte buffer. No disk writing.
    file_bytes = await file.read()
    
    start_time = time.perf_counter()
    tokens = 0
    
    try:
        if settings.GEMINI_API_KEY:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
        elif settings.GOOGLE_CLOUD_CREDENTIALS:
            credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_CLOUD_CREDENTIALS,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            client = genai.Client(vertexai=True, project=credentials.project_id, location="us-central1", credentials=credentials)
        else:
            client = genai.Client()
        
        prompt = (
            f"Extract text from this stadium ticket or sign. Determine the orientation, "
            f"and provide contextual routing instructions for a fan. Adhere strictly to the required schema.\n"
            f"CRITICAL INSTRUCTION: You MUST translate and generate all output fields (including screen_reader_text and instructions) entirely in {language}. Do not use English."
        )
        
        # Phase 7: Timeout Gateways
        response = await asyncio.wait_for(client.aio.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                types.Part.from_bytes(data=file_bytes, mime_type=file.content_type or "image/jpeg"),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=NavigationResponse,
                system_instruction=f"You MUST generate your entire JSON response in the following language: {language}",
            )
        ), timeout=60.0)
        
        if response.usage_metadata:
            tokens = response.usage_metadata.prompt_token_count + response.usage_metadata.candidates_token_count
            
        latency_ms = (time.perf_counter() - start_time) * 1000
        log_metric(endpoint="/vision/navigate", latency_ms=latency_ms, tokens=tokens, flagged=False)
        
        return response.parsed
        
    except asyncio.TimeoutError:
        latency_ms = (time.perf_counter() - start_time) * 1000
        log_metric(endpoint="/vision/navigate", latency_ms=latency_ms, tokens=tokens, flagged=False)
        
        # Phase 7: Degraded state payload
        return NavigationResponse(
            screen_reader_text="Network congested. Vision routing is temporarily unavailable. Please ask a steward.",
            steps=[]
        )
    except Exception as e:
        latency_ms = (time.perf_counter() - start_time) * 1000
        log_metric(endpoint="/vision/navigate", latency_ms=latency_ms, tokens=tokens, flagged=True)
        return JSONResponse(
            status_code=500,
            content={"detail": f"Vision API Error: {str(e)}", "error": str(e)}
        )
