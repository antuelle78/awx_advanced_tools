from fastapi import APIRouter

router = APIRouter(prefix="/ev", tags=["Event Vault"])


@router.post("/publish")
async def publish_event(event: dict):
    # placeholder: just return event
    return {"status": "published", "event": event}


@router.get("/subscribe")
async def subscribe_event(topic: str):
    # placeholder: return dummy subscription
    return {"topic": topic, "status": "subscribed"}
