"""
API Versioning

This module provides utilities for managing API versioning in the Visual DM API.
"""

from fastapi import FastAPI, APIRouter
from enum import Enum
from typing import Dict, List, Optional


class APIVersion(str, Enum):
    """Available API versions"""
    V1 = "v1"


class VersionedAPI:
    """
    Manager for versioned API endpoints.
    
    This class helps maintain multiple versions of the API in a structured way.
    """
    
    def __init__(self, app: FastAPI, prefix: str = "/api"):
        """
        Initialize the versioned API manager.
        
        Args:
            app: The FastAPI application instance
            prefix: The global prefix for all API versions (default: "/api")
        """
        self.app = app
        self.prefix = prefix
        self.versions: Dict[APIVersion, APIRouter] = {}
        
    def create_version(self, version: APIVersion, description: str) -> APIRouter:
        """
        Create a new API version router.
        
        Args:
            version: The API version enum value
            description: Description for this API version
            
        Returns:
            An APIRouter for this version
        """
        # Create a root router for this version
        router = APIRouter(
            prefix=f"{self.prefix}/{version}",
            responses={
                500: {"description": "Internal Server Error"}
            }
        )
        
        # Store the router for this version
        self.versions[version] = router
        
        return router
    
    def include_router(self, router: APIRouter, version: APIVersion):
        """
        Include a router in a specific API version.
        
        Args:
            router: The router to include
            version: The API version to include it in
        
        Raises:
            ValueError: If the specified version doesn't exist
        """
        if version not in self.versions:
            raise ValueError(f"API version {version} has not been created")
        
        self.versions[version].include_router(router)
    
    def finalize(self):
        """
        Register all version routers with the main application.
        
        Call this method after all routers have been added to their respective versions.
        """
        for version, router in self.versions.items():
            self.app.include_router(router)


def create_versioned_api(app: FastAPI) -> VersionedAPI:
    """
    Factory function to create and set up a versioned API.
    
    Args:
        app: The FastAPI application instance
        
    Returns:
        A configured VersionedAPI instance with v1 ready
    """
    api = VersionedAPI(app)
    
    # Create v1 API
    api.create_version(
        APIVersion.V1,
        "Version 1 of the Visual DM API"
    )
    
    return api 