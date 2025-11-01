"""
API routes for Organization Management server.

Handles:
- Organization listing, creation, updates
- Organization deletion
"""

from fastapi import APIRouter, HTTPException
from shared.awx_client import awx_client
from .schemas import CreateOrganizationRequest, UpdateOrganizationRequest
import httpx

router = APIRouter()


@router.get("/organizations")
async def list_organizations(name: str = None):
    """List all organizations, optionally filtered by name."""
    try:
        return await awx_client.list_organizations(name)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/organizations/{organization_id}")
async def get_organization(organization_id: int):
    """Get organization details by ID."""
    try:
        return await awx_client.get_organization(organization_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/organizations")
async def create_organization(request: CreateOrganizationRequest):
    """Create a new organization."""
    try:
        return await awx_client.create_organization(
            name=request.name,
            description=request.description
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.patch("/organizations/{organization_id}")
async def update_organization(organization_id: int, request: UpdateOrganizationRequest):
    """Update organization details."""
    try:
        return await awx_client.update_organization(
            organization_id=organization_id,
            name=request.name,
            description=request.description
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/organizations/{organization_id}")
async def delete_organization(organization_id: int):
    """Delete an organization."""
    try:
        return await awx_client.delete_organization(organization_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/test")
async def test_connection():
    """Test AWX connection."""
    try:
        result = await awx_client.list_organizations()
        return {
            "status": "connected",
            "organization_count": result.get("count", 0)
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AWX connection failed: {str(exc)}")
