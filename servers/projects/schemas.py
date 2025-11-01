"""
Pydantic schemas for Project Management server.

Define request/response models for project operations.
"""

from pydantic import BaseModel
from typing import Optional


class CreateProjectRequest(BaseModel):
    """Request model for creating a project."""

    name: str
    scm_type: str  # e.g., 'git', 'svn', 'hg', 'insights'
    scm_url: str
    description: Optional[str] = None


class UpdateProjectRequest(BaseModel):
    """Request model for updating a project."""

    name: Optional[str] = None
    scm_type: Optional[str] = None
    scm_url: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    """Response model for project details."""

    id: int
    name: str
    scm_type: str
    scm_url: str
    description: Optional[str] = None
