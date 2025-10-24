from fastapi import APIRouter, Depends
from app.adapters.token_auth import verify_token

router = APIRouter(prefix="/ev", tags=["Event Vault"])

@router.post("/publish")
async def publish_event(event: dict, user: str = Depends(verify_token)):
    # placeholder: just return event
    return {"status": "published", "event": event}

@router.get("/subscribe")
async def subscribe_event(topic: str, user: str = Depends(verify_token)):
    # placeholder: return dummy subscription
    return {"topic": topic, "status": "subscribed"}
