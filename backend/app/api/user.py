from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.user_service import UserService
from loguru import logger

router = APIRouter()

class SyncRequest(BaseModel):
    firebase_uid: str
    email: str = None

class PaymentRequest(BaseModel):
    firebase_uid: str

@router.post("/auth/sync", tags=["User"])
def sync_user(request: SyncRequest):
    """Sync Firebase user to DB and returning plan"""
    try:
        result = UserService.sync_user(request.firebase_uid, request.email)
        return result
    except Exception as e:
        logger.exception(f"Sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/payment/simulate", tags=["User"])
async def simulate_payment(request: PaymentRequest):
    """Simulate payment and upgrade user"""
    try:
        result = await UserService.simulate_payment(request.firebase_uid)
        return result
    except Exception as e:
        logger.exception(f"Payment simulation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
