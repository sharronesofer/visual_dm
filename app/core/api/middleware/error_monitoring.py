"""Error monitoring middleware."""

import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ..error_handling.monitoring import ErrorMonitor

class ErrorMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for error monitoring and request tracking."""
    
    def __init__(
        self,
        app,
        error_monitor: ErrorMonitor,
        *args,
        **kwargs
    ):
        """Initialize error monitoring middleware.
        
        Args:
            app: FastAPI application
            error_monitor: ErrorMonitor instance
        """
        super().__init__(app, *args, **kwargs)
        self.error_monitor = error_monitor
        
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process request and handle errors.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint
            
        Returns:
            Response
        """
        # Add request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        try:
            # Get request data for error logging
            request_data = {
                "method": request.method,
                "path": str(request.url.path),
                "headers": dict(request.headers),
                "query_params": dict(request.query_params),
                "client_ip": request.client.host if request.client else None
            }
            
            # Process request
            response = await call_next(request)
            return response
            
        except Exception as e:
            # Log error
            self.error_monitor.log_error(
                error=e,
                request_id=request_id,
                request_data=request_data,
                user_id=getattr(request.state, "user_id", None)
            )
            
            # Re-raise the error to be handled by FastAPI's error handlers
            raise 