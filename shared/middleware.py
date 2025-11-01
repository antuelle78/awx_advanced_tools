"""
Shared middleware for all MCP servers.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from typing import Callable


logger = logging.getLogger(__name__)


def setup_middleware(app: FastAPI):
    """Setup common middleware for all MCP servers."""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure per environment
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            logger.info(
                f"Response: {response.status_code} "
                f"(took {process_time:.3f}s)"
            )
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
            
        except Exception as exc:
            logger.error(f"Request failed: {exc}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
    
    return app
