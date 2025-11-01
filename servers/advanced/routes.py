"""API routes for Advanced Operations server."""

from fastapi import APIRouter, HTTPException
from shared.awx_client import awx_client
from .schemas import CreateCredentialRequest
import httpx

router = APIRouter()


@router.get("/credentials")
async def list_credentials():
    try:
        return await awx_client.list_credentials()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/credentials/{credential_id}")
async def get_credential(credential_id: int):
    try:
        return await awx_client.get_credential(credential_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.post("/credentials")
async def create_credential(request: CreateCredentialRequest):
    try:
        return await awx_client.create_credential(
            request.name, request.credential_type, request.inputs
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.delete("/credentials/{credential_id}")
async def delete_credential(credential_id: int):
    try:
        return await awx_client.delete_credential(credential_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))


@router.get("/test")
async def test_connection():
    try:
        result = await awx_client.list_credentials()
        return {"status": "connected", "credential_count": result.get("count", 0)}
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"AWX connection failed: {str(exc)}"
        )
