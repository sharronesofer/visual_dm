"""
API management system with versioning and documentation.
"""

import logging
import json
from typing import Dict, Any, Optional, List, Callable, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from .error_handler import handle_component_error, ErrorSeverity
from .api_response import APIResponse, APIStatus, APIError

logger = logging.getLogger(__name__)

@dataclass
class APIVersion:
    """API version information."""
    version: str
    status: str  # 'stable', 'beta', 'deprecated'
    release_date: datetime
    description: str
    endpoints: Dict[str, Dict[str, Any]]

@dataclass
class APIEndpoint:
    """API endpoint information."""
    path: str
    method: str
    description: str
    parameters: List[Dict[str, Any]]
    responses: Dict[str, Dict[str, Any]]
    tags: List[str]
    deprecated: bool = False

class APIManager:
    """Manages API versions and documentation."""
    
    def __init__(self, base_path: str = "/api"):
        """Initialize the API manager.
        
        Args:
            base_path: Base path for API endpoints
        """
        try:
            self.base_path = base_path
            self.versions: Dict[str, APIVersion] = {}
            self.endpoints: Dict[str, APIEndpoint] = {}
            self.current_version = "1.0.0"
            self.documentation_path = Path("docs/api")
            
            # Create documentation directory
            self.documentation_path.mkdir(parents=True, exist_ok=True)
            
            logger.info("API manager initialized")
            
        except Exception as e:
            handle_component_error(
                "APIManager",
                "__init__",
                e,
                ErrorSeverity.CRITICAL
            )
            raise
            
    def register_version(
        self,
        version: str,
        status: str = "stable",
        description: str = ""
    ) -> APIResponse:
        """Register a new API version.
        
        Args:
            version: Version number (semantic versioning)
            status: Version status
            description: Version description
            
        Returns:
            APIResponse with registration result
        """
        try:
            if version in self.versions:
                return APIResponse.error(
                    APIStatus.CONFLICT,
                    "version_exists",
                    f"Version {version} already registered"
                )
                
            api_version = APIVersion(
                version=version,
                status=status,
                release_date=datetime.now(),
                description=description,
                endpoints={}
            )
            
            self.versions[version] = api_version
            logger.info(f"Registered API version {version}")
            
            return APIResponse.success(
                data={"version": version},
                metadata={"status": status}
            )
            
        except Exception as e:
            handle_component_error(
                "APIManager",
                "register_version",
                e,
                ErrorSeverity.ERROR
            )
            return APIResponse.error(
                APIStatus.INTERNAL_ERROR,
                "registration_failed",
                "Failed to register API version",
                {"error": str(e)}
            )
            
    def register_endpoint(
        self,
        path: str,
        method: str,
        description: str,
        parameters: List[Dict[str, Any]],
        responses: Dict[str, Dict[str, Any]],
        tags: List[str],
        version: Optional[str] = None,
        deprecated: bool = False
    ) -> APIResponse:
        """Register a new API endpoint.
        
        Args:
            path: Endpoint path
            method: HTTP method
            description: Endpoint description
            parameters: List of parameter definitions
            responses: Response definitions
            tags: Endpoint tags
            version: API version (defaults to current version)
            deprecated: Whether the endpoint is deprecated
            
        Returns:
            APIResponse with registration result
        """
        try:
            version = version or self.current_version
            
            if version not in self.versions:
                return APIResponse.error(
                    APIStatus.NOT_FOUND,
                    "version_not_found",
                    f"Version {version} not registered"
                )
                
            endpoint = APIEndpoint(
                path=path,
                method=method,
                description=description,
                parameters=parameters,
                responses=responses,
                tags=tags,
                deprecated=deprecated
            )
            
            # Add to version
            self.versions[version].endpoints[f"{method} {path}"] = endpoint.__dict__
            
            # Add to global endpoints
            self.endpoints[f"{method} {path}"] = endpoint
            
            logger.info(f"Registered endpoint {method} {path} for version {version}")
            
            return APIResponse.success(
                data={
                    "path": path,
                    "method": method,
                    "version": version
                },
                metadata={"deprecated": deprecated}
            )
            
        except Exception as e:
            handle_component_error(
                "APIManager",
                "register_endpoint",
                e,
                ErrorSeverity.ERROR
            )
            return APIResponse.error(
                APIStatus.INTERNAL_ERROR,
                "registration_failed",
                "Failed to register API endpoint",
                {"error": str(e)}
            )
            
    def generate_openapi_spec(self, version: Optional[str] = None) -> APIResponse:
        """Generate OpenAPI specification.
        
        Args:
            version: API version (defaults to current version)
            
        Returns:
            APIResponse with OpenAPI specification
        """
        try:
            version = version or self.current_version
            
            if version not in self.versions:
                return APIResponse.error(
                    APIStatus.NOT_FOUND,
                    "version_not_found",
                    f"Version {version} not registered"
                )
                
            api_version = self.versions[version]
            
            spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": "Game API",
                    "version": version,
                    "description": api_version.description,
                    "contact": {
                        "name": "API Support",
                        "url": "https://example.com/support",
                        "email": "support@example.com"
                    }
                },
                "servers": [
                    {
                        "url": f"{self.base_path}/v{version}",
                        "description": f"API version {version}"
                    }
                ],
                "paths": {},
                "components": {
                    "schemas": {},
                    "securitySchemes": {
                        "bearerAuth": {
                            "type": "http",
                            "scheme": "bearer",
                            "bearerFormat": "JWT"
                        }
                    }
                },
                "security": [
                    {"bearerAuth": []}
                ]
            }
            
            # Add endpoints
            for endpoint_key, endpoint_data in api_version.endpoints.items():
                method, path = endpoint_key.split(" ", 1)
                path = path.lower()
                
                if path not in spec["paths"]:
                    spec["paths"][path] = {}
                    
                spec["paths"][path][method.lower()] = {
                    "summary": endpoint_data["description"],
                    "deprecated": endpoint_data["deprecated"],
                    "tags": endpoint_data["tags"],
                    "parameters": endpoint_data["parameters"],
                    "responses": endpoint_data["responses"]
                }
                
            return APIResponse.success(data=spec)
            
        except Exception as e:
            handle_component_error(
                "APIManager",
                "generate_openapi_spec",
                e,
                ErrorSeverity.ERROR
            )
            return APIResponse.error(
                APIStatus.INTERNAL_ERROR,
                "generation_failed",
                "Failed to generate OpenAPI specification",
                {"error": str(e)}
            )
            
    def save_openapi_spec(self, version: Optional[str] = None) -> APIResponse:
        """Save OpenAPI specification to file.
        
        Args:
            version: API version (defaults to current version)
            
        Returns:
            APIResponse with save result
        """
        try:
            version = version or self.current_version
            spec_response = self.generate_openapi_spec(version)
            
            if spec_response.is_error():
                return spec_response
                
            # Save specification
            spec_path = self.documentation_path / f"openapi-v{version}.json"
            with open(spec_path, "w") as f:
                json.dump(spec_response.data, f, indent=2)
                
            logger.info(f"Saved OpenAPI specification for version {version}")
            
            return APIResponse.success(
                data={"path": str(spec_path)},
                metadata={"version": version}
            )
            
        except Exception as e:
            handle_component_error(
                "APIManager",
                "save_openapi_spec",
                e,
                ErrorSeverity.ERROR
            )
            return APIResponse.error(
                APIStatus.INTERNAL_ERROR,
                "save_failed",
                "Failed to save OpenAPI specification",
                {"error": str(e)}
            )
            
    def get_endpoint_info(self, path: str, method: str) -> APIResponse:
        """Get information about an endpoint.
        
        Args:
            path: Endpoint path
            method: HTTP method
            
        Returns:
            APIResponse with endpoint information
        """
        try:
            endpoint_key = f"{method} {path}"
            endpoint = self.endpoints.get(endpoint_key)
            
            if not endpoint:
                return APIResponse.error(
                    APIStatus.NOT_FOUND,
                    "endpoint_not_found",
                    f"Endpoint {endpoint_key} not found"
                )
                
            return APIResponse.success(data=endpoint.__dict__)
            
        except Exception as e:
            handle_component_error(
                "APIManager",
                "get_endpoint_info",
                e,
                ErrorSeverity.ERROR
            )
            return APIResponse.error(
                APIStatus.INTERNAL_ERROR,
                "retrieval_failed",
                "Failed to retrieve endpoint information",
                {"error": str(e)}
            )
            
    def cleanup(self) -> APIResponse:
        """Clean up API manager resources.
        
        Returns:
            APIResponse with cleanup result
        """
        try:
            # Clear versions and endpoints
            self.versions.clear()
            self.endpoints.clear()
            
            logger.info("API manager cleaned up")
            
            return APIResponse.success()
            
        except Exception as e:
            handle_component_error(
                "APIManager",
                "cleanup",
                e,
                ErrorSeverity.ERROR
            )
            return APIResponse.error(
                APIStatus.INTERNAL_ERROR,
                "cleanup_failed",
                "Failed to clean up API manager",
                {"error": str(e)}
            ) 