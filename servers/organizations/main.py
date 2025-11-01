"""
Organization Management MCP Server

Organization management operations.
Port: 8006
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI
from shared.awx_client import awx_client
from shared.middleware import setup_middleware
from .routes import router

app = FastAPI(
    title="AWX MCP - Organization Management",
    description="Organization management operations",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

setup_middleware(app)
app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "server": "Organization Management",
        "version": "2.0.0",
    }


@app.get("/ready")
async def ready():
    try:
        await awx_client.list_organizations()
        return {
            "ready": True,
            "server": "Organization Management",
            "awx_connected": True,
        }
    except Exception as e:
        return {
            "ready": False,
            "server": "Organization Management",
            "awx_connected": False,
            "error": str(e),
        }


@app.get("/")
async def root():
    return {
        "server": "Organization Management",
        "version": "2.0.0",
        "description": "Organization management",
        "tools": [
            "list_organizations",
            "get_organization",
            "create_organization",
            "update_organization",
            "delete_organization",
            "test_connection",
        ],
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8006)
