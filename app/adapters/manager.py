# Simple adapter registry
from typing import Dict
from fastapi import APIRouter

# Import routers from adapter modules
from .awx import router as awx_router
from .ev import router as ev_router
from .sn import router as sn_router
from .llm import router as llm_router
from .audit import router as audit_router
from .context import router as context_router

# Registry mapping names to routers
ADAPTER_REGISTRY: Dict[str, APIRouter] = {
    "awx": awx_router,
    "ev": ev_router,
    "sn": sn_router,
    "llm": llm_router,
    "audit": audit_router,
    "context": context_router,
}

# Helper to get router by name


def get_adapter(name: str) -> APIRouter:
    """Return the FastAPI router for the requested adapter.

    Args:
        name: Adapter name string.
    Raises:
        KeyError if adapter not found.
    """
    if name not in ADAPTER_REGISTRY:
        raise KeyError(f"Adapter '{name}' not registered")
    return ADAPTER_REGISTRY[name]
