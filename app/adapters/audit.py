import os
from fastapi import APIRouter, HTTPException
from app.config import settings

router = APIRouter(prefix="/audit", tags=["Audit Log"])


@router.get("/logs")
async def get_logs():
    try:
        logs = []
        for f in os.listdir(settings.audit_log_dir):
            if f.endswith(".log"):
                with open(os.path.join(settings.audit_log_dir, f), "r") as fh:
                    logs.append(fh.read())
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
