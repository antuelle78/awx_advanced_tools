"""
Shared authentication and authorization logic.
"""

import os
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials


security = HTTPBasic()


# Internal service-to-service authentication
INTERNAL_TOKEN = os.getenv("INTERNAL_AUTH_TOKEN", "change-me-in-production")


def verify_internal_request(request: Request) -> bool:
    """Verify that a request comes from another internal MCP server."""
    token = request.headers.get("X-Internal-Token")
    return token == INTERNAL_TOKEN


async def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Get current authenticated user."""
    # This is a simple implementation
    # In production, verify against actual user database or JWT
    return credentials.username


def require_internal_auth(request: Request):
    """Require internal authentication for inter-server communication."""
    if not verify_internal_request(request):
        raise HTTPException(
            status_code=403,
            detail="Invalid internal authentication token"
        )
    return True
