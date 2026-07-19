from fastapi import APIRouter, Header, HTTPException, Depends
from app.core.telemetry import get_telemetry_logs
from app.core.config import settings

router = APIRouter(prefix="/telemetry", tags=["admin"])

def verify_admin_token(x_admin_token: str = Header(None)):
    if x_admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.get("/", dependencies=[Depends(verify_admin_token)])
async def get_telemetry():
    return {"logs": get_telemetry_logs()}
