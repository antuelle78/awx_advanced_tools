import json
import os
from datetime import datetime
from app.config import settings

# Ensure audit log directory exists
os.makedirs(settings.audit_log_dir, exist_ok=True)

# Simple logger writing to JSON file per context

def audit(user: str, action: str, platform: str, request: dict, response: dict | None = None, error: str | None = None):
    entry = {
        "user": user,
        "action": action,
        "platform": platform,
        "request": request,
        "response": response,
        "error": error,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    log_path = os.path.join(settings.audit_log_dir, f"audit_{datetime.utcnow().strftime('%Y%m%d')}.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
