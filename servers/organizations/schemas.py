"""
Pydantic schemas for Organization Management server.
"""

from pydantic import BaseModel
from typing import Optional


class CreateOrganizationRequest(BaseModel):
    """Request model for creating an organization."""

    name: str
    description: Optional[str] = None


class UpdateOrganizationRequest(BaseModel):
    """Request model for updating an organization."""

    name: Optional[str] = None
    description: Optional[str] = None


class OrganizationResponse(BaseModel):
    """Response model for organization details."""

    id: int
    name: str
    description: Optional[str] = None
