"""
Pydantic schemas for Templates server.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class CreateJobTemplateRequest(BaseModel):
    """Request model for creating a job template."""

    name: str
    inventory: int
    project: int
    playbook: str
    description: Optional[str] = None
    extra_vars: Optional[Dict[str, Any]] = None


class CreateWorkflowTemplateRequest(BaseModel):
    """Request model for creating a workflow template."""

    name: str
    description: Optional[str] = None


class UpdateWorkflowTemplateRequest(BaseModel):
    """Request model for updating a workflow template."""

    name: Optional[str] = None
    description: Optional[str] = None


class LaunchWorkflowRequest(BaseModel):
    """Request model for launching a workflow template."""

    extra_vars: Optional[Dict[str, Any]] = None
