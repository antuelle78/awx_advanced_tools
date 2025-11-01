"""
Pydantic schemas for Inventory Management server.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class CreateInventoryRequest(BaseModel):
    """Request model for creating an inventory."""
    name: str
    variables: Optional[Dict[str, Any]] = None
    organization: Optional[int] = None


class CreateHostRequest(BaseModel):
    """Request model for creating a host."""
    name: str
    inventory: int
    variables: Optional[Dict[str, Any]] = None


class InventoryResponse(BaseModel):
    """Response model for inventory details."""
    id: int
    name: str
    organization: Optional[int] = None
    variables: Optional[Dict[str, Any]] = None
