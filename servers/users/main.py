"""
User Management MCP Server

User account management operations.
Port: 8004
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
    title="AWX MCP - User Management",
    description="User account management operations",
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
        "server": "User Management",
        "version": "2.0.0"
    }


@app.get("/ready")
async def ready():
    """Readiness check - verifies AWX connection."""
    try:
        # Test AWX connection by listing users
        await awx_client.list_users()
        return {
            "ready": True,
            "server": "User Management",
            "awx_connected": True
        }
    except Exception as e:
        return {
            "ready": False,
            "server": "User Management",
            "awx_connected": False,
            "error": str(e)
        }


@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "server": "User Management",
        "version": "2.0.0",
        "description": "User account management",
        "tools": [
            "list_users",
            "get_user",
            "get_user_by_name",
            "create_user",
            "update_user",
            "delete_user",
            "test_connection"
        ],
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
