"""
API routes for User Management server.

Handles:
- User listing, creation, updates
- User deletion
- User lookup by name
"""

from fastapi import APIRouter, HTTPException
from shared.awx_client import awx_client
from .schemas import CreateUserRequest, UpdateUserRequest
import httpx

router = APIRouter()


@router.get("/users")
async def list_users(username: str = None):
    """List all users, optionally filtered by username."""
    try:
        return await awx_client.list_users(username)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get user details by ID."""
    try:
        return await awx_client.get_user(user_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/users/by_name/{username}")
async def get_user_by_name(username: str):
    """Get user details by username."""
    try:
        return await awx_client.get_user_by_name(username)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except HTTPException:
        raise


@router.post("/users")
async def create_user(request: CreateUserRequest):
    """Create a new user."""
    try:
        return await awx_client.create_user(
            username=request.username,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.patch("/users/{user_id}")
async def update_user(user_id: int, request: UpdateUserRequest):
    """Update user details."""
    try:
        return await awx_client.update_user(
            user_id=user_id,
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Delete a user."""
    try:
        return await awx_client.delete_user(user_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/test")
async def test_connection():
    """Test AWX connection."""
    try:
        result = await awx_client.list_users()
        return {"status": "connected", "user_count": result.get("count", 0)}
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"AWX connection failed: {str(exc)}"
        )
