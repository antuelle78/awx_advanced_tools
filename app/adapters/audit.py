import os
from fastapi import APIRouter, Depends, HTTPException
from app.adapters.token_auth import verify_token
from app.config import settings

router = APIRouter(prefix="/audit", tags=["Audit Log"])

@router.get("/logs")
async def get_logs(user: str = Depends(verify_token)):
    try:
        logs = []
        for f in os.listdir(settings.audit_log_dir):
            if f.endswith(".log"):
                with open(os.path.join(settings.audit_log_dir, f), "r") as fh:
                    logs.append(fh.read())
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
