"""
Templates MCP Server

Job and workflow template management operations.
Port: 8003
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
    title="AWX MCP - Templates",
    description="Job and workflow template management operations",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup middleware
setup_middleware(app)

# Include routes
app.include_router(router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": "Templates",
        "version": "2.0.0"
    }


@app.get("/ready")
async def ready():
    """Readiness check - verifies AWX connection."""
    try:
        # Test AWX connection by listing workflow templates
        await awx_client.list_workflow_job_templates()
        return {
            "ready": True,
            "server": "Templates",
            "awx_connected": True
        }
    except Exception as e:
        return {
            "ready": False,
            "server": "Templates",
            "awx_connected": False,
            "error": str(e)
        }


@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "server": "Templates",
        "version": "2.0.0",
        "description": "Job and workflow template management",
        "tools": [
            "create_job_template",
            "list_workflow_templates",
            "create_workflow_template",
            "update_workflow_template",
            "delete_workflow_template",
            "launch_workflow_template",
            "test_connection"
        ],
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
