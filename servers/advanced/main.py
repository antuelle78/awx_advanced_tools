import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fastapi import FastAPI
from shared.middleware import setup_middleware
from .routes import router

app = FastAPI(
    title="AWX MCP - Advanced Operations",
    description="Advanced operations",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
setup_middleware(app)
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "healthy", "server": "Advanced Operations", "version": "2.0.0"}


@app.get("/")
async def root():
    return {
        "server": "Advanced Operations",
        "version": "2.0.0",
        "description": "Advanced operations",
        "tools": [
            "list_credentials",
            "get_credential",
            "create_credential",
            "delete_credential",
            "test_connection",
        ],
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8008)
