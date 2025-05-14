"""API version management system."""

from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class VersionStatus(str, Enum):
    """API version status."""
    STABLE = "stable"
    BETA = "beta"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"

@dataclass
class APIVersion:
    """API version information."""
    version: str  # e.g., 'v1', 'v2'
    status: VersionStatus
    release_date: datetime
    sunset_date: Optional[datetime] = None
    description: str = ""
    breaking_changes: List[str] = None
    migration_guide: Optional[str] = None

class VersionManager:
    """Manages API versioning, deprecation, and documentation."""
    
    def __init__(self, base_path: str = "/api"):
        """Initialize version manager.
        
        Args:
            base_path: Base API path
        """
        self.base_path = base_path.rstrip('/')
        self.versions: Dict[str, APIVersion] = {}
        self.current_version = "v1"
        self.docs_path = Path("docs/api")
        self.docs_path.mkdir(parents=True, exist_ok=True)
        
    def register_version(
        self,
        version: str,
        status: VersionStatus = VersionStatus.STABLE,
        description: str = "",
        breaking_changes: List[str] = None,
        migration_guide: Optional[str] = None,
        sunset_date: Optional[datetime] = None
    ) -> None:
        """Register a new API version.
        
        Args:
            version: Version identifier (e.g., 'v1', 'v2')
            status: Version status
            description: Version description
            breaking_changes: List of breaking changes from previous version
            migration_guide: Path to migration guide markdown file
            sunset_date: Optional date when version will be sunset
        """
        if version in self.versions:
            logger.warning(f"Version {version} already registered")
            return
            
        api_version = APIVersion(
            version=version,
            status=status,
            release_date=datetime.now(),
            sunset_date=sunset_date,
            description=description,
            breaking_changes=breaking_changes or [],
            migration_guide=migration_guide
        )
        
        self.versions[version] = api_version
        logger.info(f"Registered API version {version}")
        
        # Generate version documentation
        self._generate_version_docs(api_version)
        
    def deprecate_version(
        self,
        version: str,
        sunset_date: datetime,
        migration_guide: Optional[str] = None
    ) -> None:
        """Mark a version as deprecated.
        
        Args:
            version: Version to deprecate
            sunset_date: Date when version will be removed
            migration_guide: Optional path to migration guide
        """
        if version not in self.versions:
            logger.error(f"Version {version} not found")
            return
            
        api_version = self.versions[version]
        api_version.status = VersionStatus.DEPRECATED
        api_version.sunset_date = sunset_date
        
        if migration_guide:
            api_version.migration_guide = migration_guide
            
        logger.info(f"Deprecated version {version}, sunset date: {sunset_date}")
        
        # Update version documentation
        self._generate_version_docs(api_version)
        
    def sunset_version(self, version: str) -> None:
        """Mark a version as sunset (end-of-life).
        
        Args:
            version: Version to sunset
        """
        if version not in self.versions:
            logger.error(f"Version {version} not found")
            return
            
        api_version = self.versions[version]
        api_version.status = VersionStatus.SUNSET
        logger.info(f"Sunset version {version}")
        
        # Update version documentation
        self._generate_version_docs(api_version)
        
    def get_version_url(self, version: str) -> str:
        """Get the base URL for a version.
        
        Args:
            version: API version
            
        Returns:
            Full URL path including version
        """
        return f"{self.base_path}/{version}"
        
    def get_active_versions(self) -> Set[str]:
        """Get all non-sunset versions.
        
        Returns:
            Set of active version strings
        """
        return {
            v.version for v in self.versions.values()
            if v.status != VersionStatus.SUNSET
        }
        
    def _generate_version_docs(self, version: APIVersion) -> None:
        """Generate documentation for an API version.
        
        Args:
            version: APIVersion instance
        """
        doc_file = self.docs_path / f"{version.version}.md"
        
        content = [
            f"# API {version.version}",
            "",
            f"**Status:** {version.status.value}",
            f"**Release Date:** {version.release_date.strftime('%Y-%m-%d')}",
            ""
        ]
        
        if version.sunset_date:
            content.extend([
                "## ⚠️ Deprecation Notice",
                f"This version will be sunset on {version.sunset_date.strftime('%Y-%m-%d')}.",
                "Please migrate to a newer version.",
                ""
            ])
            
        if version.description:
            content.extend([
                "## Description",
                version.description,
                ""
            ])
            
        if version.breaking_changes:
            content.extend([
                "## Breaking Changes",
                *[f"- {change}" for change in version.breaking_changes],
                ""
            ])
            
        if version.migration_guide:
            content.extend([
                "## Migration Guide",
                f"See the [migration guide]({version.migration_guide}) for detailed upgrade instructions.",
                ""
            ])
            
        doc_file.write_text("\n".join(content))
        logger.info(f"Generated documentation for {version.version}") 