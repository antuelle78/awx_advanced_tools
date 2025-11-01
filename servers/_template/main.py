"""
Template MCP Server

Copy this template and customize for your specific server.

Replace:
- {SERVER_NAME} with the server name (e.g., "Core Operations")
- {DESCRIPTION} with server description
- {PORT} with server port (8001-8010)
"""

import sys
import os

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI
from shared.awx_client import awx_client
from shared.middleware import setup_middleware
from .routes import router

app = FastAPI(
    title="AWX MCP - {SERVER_NAME}",
    description="{DESCRIPTION}",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup middleware
setup_middleware(app)

# Include routes
app.include_router(router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "server": "{SERVER_NAME}", "version": "2.0.0"}


@app.get("/ready")
async def ready():
    """Readiness check - verifies AWX connection."""
    try:
        # Test AWX connection by listing templates
        await awx_client.list_templates()
        return {"ready": True, "server": "{SERVER_NAME}", "awx_connected": True}
    except Exception as e:
        return {
            "ready": False,
            "server": "{SERVER_NAME}",
            "awx_connected": False,
            "error": str(e),
        }


@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "server": "{SERVER_NAME}",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
    }


if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
