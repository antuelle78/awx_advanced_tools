"""
Pydantic schemas for Core Operations server.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class LaunchJobRequest(BaseModel):
    """Request model for launching a job template."""

    extra_vars: Optional[Dict[str, Any]] = None


class JobStatusResponse(BaseModel):
    """Response model for job status."""

    id: int
    status: str
    name: str
    finished: Optional[str] = None
