# main entrypoint
# Added comment to trigger CI/CD after adding Docker Hub secrets
from fastapi import FastAPI
from app.adapters.awx import router as awx_router
from app.adapters.auth import router as auth_router
from app.adapters.awx_service import awx_client
import logging, json

app = FastAPI(title="AWX Advanced Tools", description="Orchestration gateway", version="1.0.0")

app.include_router(awx_router)
app.include_router(auth_router)

@app.get("/")
async def root_health_check():
    return {"status": "running"}

# Configure root logger to emit JSON
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
        }
        # Include exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
root_logger.handlers = [handler]

# Health check helpers
from fastapi import Response

async def awx_ping() -> bool:
    try:
        # GET base URL to ensure AWX reachable
        await awx_client.list_schedules(0)  # dummy ID; will error but success status indicates reachability
        return True
    except Exception:
        return False

@app.get("/health")
async def health():
    # Simple liveness
    return {"status": "running"}

@app.get("/ready")
async def ready():
    available = await awx_ping()
    return {"ready": available, "awx": available}

# Removed duplicate liveness endpoint