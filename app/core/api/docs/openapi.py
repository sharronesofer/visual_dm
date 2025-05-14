"""OpenAPI documentation generator with versioning support."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json

from ..version_manager import VersionManager, VersionStatus

class OpenAPIGenerator:
    """Generates OpenAPI documentation for versioned APIs."""
    
    def __init__(
        self,
        version_manager: VersionManager,
        title: str = "Game Management API",
        description: str = "RESTful API for game world management"
    ):
        """Initialize OpenAPI generator.
        
        Args:
            version_manager: VersionManager instance
            title: API title
            description: API description
        """
        self.version_manager = version_manager
        self.title = title
        self.description = description
        self.docs_path = Path("docs/api/openapi")
        self.docs_path.mkdir(parents=True, exist_ok=True)
        
    def generate_all(self) -> None:
        """Generate OpenAPI specs for all active versions."""
        for version in self.version_manager.get_active_versions():
            self.generate_version(version)
            
    def generate_version(self, version: str) -> None:
        """Generate OpenAPI spec for a specific version.
        
        Args:
            version: API version to generate docs for
        """
        if version not in self.version_manager.versions:
            raise ValueError(f"Version {version} not found")
            
        api_version = self.version_manager.versions[version]
        
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": self.title,
                "version": version,
                "description": self._get_version_description(api_version)
            },
            "servers": [
                {
                    "url": self.version_manager.get_version_url(version),
                    "description": f"API {version}"
                }
            ],
            "paths": self._get_paths(version),
            "components": {
                "schemas": self._get_schemas(version),
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                },
                "responses": self._get_common_responses()
            },
            "security": [
                {"bearerAuth": []}
            ],
            "tags": self._get_tags()
        }
        
        # Save spec
        spec_file = self.docs_path / f"{version}.json"
        spec_file.write_text(json.dumps(spec, indent=2))
        
    def _get_version_description(self, version: Any) -> str:
        """Generate version description with status info.
        
        Args:
            version: APIVersion instance
            
        Returns:
            Formatted description
        """
        description = [version.description, ""]
        
        if version.status == VersionStatus.DEPRECATED:
            description.extend([
                "⚠️ **DEPRECATED**",
                f"This version will be sunset on {version.sunset_date.strftime('%Y-%m-%d')}.",
                "Please migrate to a newer version.",
                ""
            ])
            
        if version.breaking_changes:
            description.extend([
                "## Breaking Changes",
                *[f"- {change}" for change in version.breaking_changes],
                ""
            ])
            
        if version.migration_guide:
            description.extend([
                "## Migration Guide",
                f"See the [migration guide]({version.migration_guide}) for upgrade instructions.",
                ""
            ])
            
        return "\n".join(description)
        
    def _get_paths(self, version: str) -> Dict[str, Any]:
        """Get API paths for version.
        
        Args:
            version: API version
            
        Returns:
            OpenAPI paths object
        """
        # This would be populated based on your route definitions
        # For now, returning empty dict as placeholder
        return {}
        
    def _get_schemas(self, version: str) -> Dict[str, Any]:
        """Get API schemas for version.
        
        Args:
            version: API version
            
        Returns:
            OpenAPI schemas object
        """
        # This would be populated based on your model definitions
        # For now, returning empty dict as placeholder
        return {}
        
    def _get_common_responses(self) -> Dict[str, Any]:
        """Get common response definitions.
        
        Returns:
            OpenAPI responses object
        """
        return {
            "Error": {
                "description": "Error response",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {
                                    "type": "object",
                                    "properties": {
                                        "code": {"type": "string"},
                                        "message": {"type": "string"},
                                        "details": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "field": {"type": "string"},
                                                    "error": {"type": "string"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
    def _get_tags(self) -> List[Dict[str, str]]:
        """Get API tags.
        
        Returns:
            List of tag objects
        """
        return [
            {"name": "NPCs", "description": "NPC management endpoints"},
            {"name": "Items", "description": "Item management endpoints"},
            {"name": "Locations", "description": "Location management endpoints"},
            {"name": "Quests", "description": "Quest management endpoints"},
            {"name": "Factions", "description": "Faction management endpoints"},
            {"name": "Relationships", "description": "Entity relationship endpoints"}
        ] 