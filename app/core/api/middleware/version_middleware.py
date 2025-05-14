"""API version middleware."""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from datetime import datetime
import re

from ..version_manager import VersionManager, VersionStatus

class VersionMiddleware(BaseHTTPMiddleware):
    """Middleware for API version handling and deprecation warnings."""
    
    def __init__(
        self,
        app,
        version_manager: VersionManager,
        *args,
        **kwargs
    ):
        """Initialize version middleware.
        
        Args:
            app: FastAPI application
            version_manager: VersionManager instance
        """
        super().__init__(app, *args, **kwargs)
        self.version_manager = version_manager
        
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process the request and handle versioning.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint
            
        Returns:
            Response with appropriate version headers
        """
        # Extract version from path
        version = self._extract_version(request.url.path)
        
        if not version:
            # No version in path, use current version
            version = self.version_manager.current_version
            
        # Check if version exists
        if version not in self.version_manager.versions:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "version_not_found",
                    "message": f"API version {version} not found",
                    "available_versions": list(self.version_manager.get_active_versions())
                }
            )
            
        api_version = self.version_manager.versions[version]
        
        # Check if version is sunset
        if api_version.status == VersionStatus.SUNSET:
            return JSONResponse(
                status_code=410,
                content={
                    "error": "version_sunset",
                    "message": f"API version {version} has been sunset",
                    "available_versions": list(self.version_manager.get_active_versions())
                }
            )
            
        # Process request
        response = await call_next(request)
        
        # Add version headers
        response.headers["X-API-Version"] = version
        response.headers["X-API-Version-Status"] = api_version.status.value
        
        # Add deprecation warning if needed
        if api_version.status == VersionStatus.DEPRECATED:
            response.headers["Warning"] = (
                f'299 - "API version {version} is deprecated and will be sunset on '
                f'{api_version.sunset_date.strftime("%Y-%m-%d")}. '
                f'Please migrate to a newer version."'
            )
            
            if api_version.migration_guide:
                response.headers["Link"] = (
                    f'<{api_version.migration_guide}>; '
                    'rel="deprecation"; type="text/html"'
                )
                
        return response
        
    def _extract_version(self, path: str) -> str:
        """Extract version from URL path.
        
        Args:
            path: URL path
            
        Returns:
            Version string or None
        """
        match = re.search(r"/api/v(\d+)", path)
        if match:
            return f"v{match.group(1)}"
        return None 