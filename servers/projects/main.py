"""
Project Management MCP Server

Project SCM management operations.
Port: 8005
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
    title="AWX MCP - Project Management",
    description="Project SCM management operations",
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
    return {"status": "healthy", "server": "Project Management", "version": "2.0.0"}


@app.get("/ready")
async def ready():
    """Readiness check - verifies AWX connection."""
    try:
        # Test AWX connection by listing projects
        await awx_client.list_projects()
        return {"ready": True, "server": "Project Management", "awx_connected": True}
    except Exception as e:
        return {
            "ready": False,
            "server": "Project Management",
            "awx_connected": False,
            "error": str(e),
        }


@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "server": "Project Management",
        "version": "2.0.0",
        "description": "Project SCM management",
        "tools": [
            "list_projects",
            "get_project",
            "create_project",
            "update_project",
            "delete_project",
            "sync_project",
            "test_connection",
        ],
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)
