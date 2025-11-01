"""
Pydantic schemas for User Management server.

Define request/response models for user operations.
"""

from pydantic import BaseModel
from typing import Optional


class CreateUserRequest(BaseModel):
    """Request model for creating a user."""
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None


class UpdateUserRequest(BaseModel):
    """Request model for updating a user."""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    """Response model for user details."""
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
