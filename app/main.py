# main entrypoint
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.adapters.awx import router as awx_router
from app.adapters.llm import router as llm_router
from app.adapters.audit import router as audit_router
from app.adapters.ev import router as ev_router
from app.adapters.sn import router as sn_router
from app.auth import router as auth_router
from app.adapters.awx_service import awx_client
import logging
import json

app = FastAPI(
    title="AWX Advanced Tools", description="Orchestration gateway", version="1.0.0"
)

# Add CORS middleware to allow Open-WebUI to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Open-WebUI domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(awx_router)
app.include_router(llm_router)
app.include_router(audit_router)
app.include_router(ev_router)
app.include_router(sn_router)


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


async def awx_ping() -> bool:
    try:
        # GET job templates to ensure AWX reachable
        await awx_client.list_templates()
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
