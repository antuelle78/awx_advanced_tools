from fastapi import APIRouter

router = APIRouter(prefix="/sn", tags=["ServiceNow"])


@router.post("/incident")
async def create_incident(incident: dict):
    # placeholder: just echo
    return {"status": "incident_created", "incident": incident}
