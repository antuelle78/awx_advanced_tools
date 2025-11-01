"""Schedules Management MCP Server - Port: 8007"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI
from shared.awx_client import awx_client
from shared.middleware import setup_middleware
from .routes import router

app = FastAPI(title="AWX MCP - Schedules", description="Schedule management", version="2.0.0", docs_url="/docs", redoc_url="/redoc")
setup_middleware(app)
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "healthy", "server": "Schedules", "version": "2.0.0"}

@app.get("/")
async def root():
    return {
        "server": "Schedules",
        "version": "2.0.0",
        "description": "Schedule management",
        "tools": ["list_schedules", "get_schedule", "create_schedule", "update_schedule", "toggle_schedule", "delete_schedule", "test_connection"],
        "docs": "/docs", "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
