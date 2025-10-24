from fastapi import APIRouter, Depends
from app.adapters.token_auth import verify_token

router = APIRouter(prefix="/sn", tags=["ServiceNow"])

@router.post("/incident")
async def create_incident(incident: dict, user: str = Depends(verify_token)):
    # placeholder: just echo
    return {"status": "incident_created", "incident": incident}
