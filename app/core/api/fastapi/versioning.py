"""API versioning utilities."""

from typing import Optional, Sequence
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute

class VersionedAPIRouter(APIRouter):
    """Router with API versioning support."""
    
    def __init__(
        self,
        version: str,
        *args,
        prefix: Optional[str] = None,
        **kwargs
    ):
        """Initialize versioned router.
        
        Args:
            version: API version (e.g., 'v1', 'v2')
            prefix: Optional prefix before version (e.g., '/api')
            *args: Additional positional arguments for APIRouter
            **kwargs: Additional keyword arguments for APIRouter
        """
        # Construct versioned prefix
        if prefix:
            prefix = prefix.rstrip('/')
        else:
            prefix = '/api'
            
        versioned_prefix = f"{prefix}/{version}"
        
        # Initialize router with versioned prefix
        super().__init__(*args, prefix=versioned_prefix, **kwargs)
        
        self.version = version
        self.base_prefix = prefix

    def include_router(
        self,
        router: APIRouter,
        *args,
        prefix: Optional[str] = None,
        **kwargs
    ) -> None:
        """Include another router with version-aware prefix handling.
        
        Args:
            router: Router to include
            prefix: Optional additional prefix
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        if prefix:
            prefix = prefix.lstrip('/')
            full_prefix = f"/{prefix}"
        else:
            full_prefix = ""
            
        super().include_router(router, *args, prefix=full_prefix, **kwargs)

def version_routes(
    app: FastAPI,
    routers: Sequence[APIRouter],
    version: str = 'v1',
    prefix: str = '/api'
) -> None:
    """Version a group of routes under a common version prefix.
    
    Args:
        app: FastAPI application instance
        routers: Sequence of routers to version
        version: API version (e.g., 'v1', 'v2')
        prefix: Base API prefix
    """
    versioned_router = VersionedAPIRouter(version=version, prefix=prefix)
    
    for router in routers:
        versioned_router.include_router(router)
        
    app.include_router(versioned_router)

def get_api_versions(app: FastAPI) -> set[str]:
    """Get all API versions used in the application.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Set of version strings
    """
    versions = set()
    
    for route in app.routes:
        if isinstance(route, APIRoute):
            # Extract version from route path
            parts = route.path.split('/')
            for part in parts:
                if part.startswith('v') and part[1:].isdigit():
                    versions.add(part)
                    
    return versions 