from fastapi import APIRouter, HTTPException, Depends
from google.oauth2 import id_token
from google.auth.transport import requests
from app.models.schemas import GoogleAuthRequest, GoogleAuthResponse
from app.core.config import settings
import uuid
import asyncio

router = APIRouter()

@router.post("/auth/google", response_model=GoogleAuthResponse, tags=["auth"])
async def google_auth(request: GoogleAuthRequest):
    try:
        # Verify Identity Structural Integrity (Offloaded to a thread to prevent blocking event loop)
        idinfo = await asyncio.to_thread(
            id_token.verify_oauth2_token,
            request.credential, 
            requests.Request(), 
            settings.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10
        )

        # Extract User Profile Metadata
        user_id = idinfo['sub']
        email = idinfo.get('email', '')
        name = idinfo.get('name', '')
        picture = idinfo.get('picture', '')

        # Generate a custom session token
        session_token = f"session_{uuid.uuid4().hex}"

        return GoogleAuthResponse(
            token=session_token,
            user={
                "id": user_id,
                "email": email,
                "name": name,
                "picture": picture
            }
        )
    except ValueError as e:
        # Invalid token
        raise HTTPException(status_code=401, detail=f"Invalid credential: {str(e)}")
