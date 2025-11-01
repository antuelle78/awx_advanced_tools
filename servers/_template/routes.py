"""
API routes for {SERVER_NAME} server.

Define all endpoints for this specialized server here.
"""

from fastapi import APIRouter

router = APIRouter()


# Example endpoint - customize for your server
@router.get("/example")
async def example_endpoint():
    """Example endpoint - replace with actual endpoints."""
    return {"message": "This is a template endpoint"}


# Add your specialized endpoints here
# Example:
# @router.get("/templates")
# async def list_templates():
#     try:
#         return await awx_client.list_templates()
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
