"""API routes for Notifications server."""

from fastapi import APIRouter, HTTPException
from shared.awx_client import awx_client
import httpx

router = APIRouter()


@router.get("/activity_stream")
async def get_activity_stream(page: int = 1):
    """Get activity stream (audit log)."""
    try:
        # Use generic request method
        url = f"{awx_client.base_url}/api/v2/activity_stream/"
        params = {"page": page, "page_size": 50}
        resp = await awx_client._request("GET", url, params=params)
        return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/test")
async def test_connection():
    """Test AWX connection."""
    try:
        url = f"{awx_client.base_url}/api/v2/activity_stream/"
        resp = await awx_client._request("GET", url, params={"page_size": 1})
        result = resp.json()
        return {"status": "connected", "activity_count": result.get("count", 0)}
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"AWX connection failed: {str(exc)}"
        )
