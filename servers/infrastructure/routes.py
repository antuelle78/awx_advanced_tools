"""API routes for Infrastructure server."""
from fastapi import APIRouter, HTTPException
from shared.awx_client import awx_client
import httpx

router = APIRouter()

@router.get("/ping")
async def ping_awx():
    """Ping AWX to check connectivity."""
    try:
        url = f"{awx_client.base_url}/api/v2/ping/"
        resp = await awx_client._request("GET", url)
        return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))

@router.get("/config")
async def get_config():
    """Get AWX configuration."""
    try:
        url = f"{awx_client.base_url}/api/v2/config/"
        resp = await awx_client._request("GET", url)
        return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))

@router.get("/test")
async def test_connection():
    """Test AWX connection."""
    try:
        url = f"{awx_client.base_url}/api/v2/ping/"
        resp = await awx_client._request("GET", url)
        result = resp.json()
        return {"status": "connected", "version": result.get("version", "unknown")}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AWX connection failed: {str(exc)}")
