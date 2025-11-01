"""
API routes for Inventory Management server.

Handles:
- Inventory listing, creation, deletion
- Inventory synchronization
- Host management (list, create)
"""

from fastapi import APIRouter, HTTPException
from shared.awx_client import awx_client
from .schemas import CreateInventoryRequest, CreateHostRequest
import httpx

router = APIRouter()


@router.get("/inventories")
async def list_inventories(name: str = None):
    """List all inventories."""
    try:
        return await awx_client.list_inventories(name)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/inventories/{inventory_id}")
async def get_inventory(inventory_id: int):
    """Get inventory details."""
    try:
        return await awx_client.get_inventory(inventory_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/inventories")
async def create_inventory(request: CreateInventoryRequest):
    """Create a new inventory."""
    try:
        return await awx_client.create_inventory(
            name=request.name,
            variables=request.variables,
            organization=request.organization
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/inventories/{inventory_id}")
async def delete_inventory(inventory_id: int):
    """Delete an inventory."""
    try:
        return await awx_client.delete_inventory(inventory_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/inventories/{inventory_id}/sync")
async def sync_inventory(inventory_id: int):
    """Sync an inventory."""
    try:
        return await awx_client.sync_inventory(inventory_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/hosts")
async def list_hosts(inventory: int = None):
    """List all hosts, optionally filtered by inventory."""
    try:
        return await awx_client.list_hosts(inventory)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/hosts")
async def create_host(request: CreateHostRequest):
    """Create a new host."""
    try:
        host_data = {
            "name": request.name,
            "inventory": request.inventory
        }
        if request.variables:
            host_data["variables"] = request.variables
        return await awx_client.create_host(host_data)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/test")
async def test_connection():
    """Test AWX connection."""
    try:
        result = await awx_client.list_inventories()
        return {
            "status": "connected",
            "inventory_count": result.get("count", 0)
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AWX connection failed: {str(exc)}")
