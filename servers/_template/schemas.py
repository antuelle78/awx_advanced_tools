"""
Pydantic schemas for {SERVER_NAME} server.

Define request/response models here.
"""

from pydantic import BaseModel
from typing import Optional


# Example schema - customize for your server
class ExampleRequest(BaseModel):
    """Example request model."""

    name: str
    description: Optional[str] = None


class ExampleResponse(BaseModel):
    """Example response model."""

    id: int
    name: str
    status: str
