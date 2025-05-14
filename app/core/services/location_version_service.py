"""
Service for managing location version control operations.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import db
from app.core.models.location import Location
from app.core.models.location_version import LocationVersion, LocationChangeLog

class LocationVersionService:
    """Service for managing location version control."""
    
    def __init__(self, session: Session = None):
        """Initialize with optional session override."""
        self.session = session or db.session
        
    def create_initial_version(self, location: Location, changed_by: str) -> LocationVersion:
        """Create the initial version for a new location."""
        version = location.create_version(
            change_type='creation',
            change_reason='Initial location creation',
            changed_by=changed_by
        )
        self.session.add(version)
        self.session.commit()
        return version
        
    def update_location(self, location: Location, updates: Dict[str, Any], 
                       change_reason: str, changed_by: str) -> Tuple[LocationVersion, List[LocationChangeLog]]:
        """Update a location and create a new version with change logs."""
        # Track changes
        changes = []
        for field, new_value in updates.items():
            if hasattr(location, field):
                old_value = getattr(location, field)
                if old_value != new_value:
                    setattr(location, field, new_value)
                    changes.append((field, old_value, new_value))
                    
        if not changes:
            return None, []
            
        # Create new version
        version = location.create_version(
            change_type='modification',
            change_reason=change_reason,
            changed_by=changed_by
        )
        
        # Log individual changes
        logs = []
        for field, old_value, new_value in changes:
            log = location.log_change(
                version_id=version.id,
                field_name=field,
                old_value=old_value,
                new_value=new_value
            )
            logs.append(log)
            
        self.session.add(version)
        self.session.add_all(logs)
        self.session.commit()
        
        return version, logs
        
    def get_version_history(self, location_id: int) -> List[LocationVersion]:
        """Get the complete version history for a location."""
        return (LocationVersion.query
                .filter_by(location_id=location_id)
                .order_by(LocationVersion.version_number)
                .all())
                
    def get_version(self, location_id: int, version_number: int) -> Optional[LocationVersion]:
        """Get a specific version of a location."""
        return (LocationVersion.query
                .filter_by(location_id=location_id, version_number=version_number)
                .first())
                
    def get_changes_between_versions(self, location_id: int, 
                                   from_version: int, to_version: int) -> List[LocationChangeLog]:
        """Get all changes between two versions of a location."""
        return (LocationChangeLog.query
                .join(LocationVersion)
                .filter(
                    LocationChangeLog.location_id == location_id,
                    LocationVersion.version_number > from_version,
                    LocationVersion.version_number <= to_version
                )
                .order_by(LocationVersion.version_number, LocationChangeLog.id)
                .all())
                
    def revert_location(self, location: Location, version_number: int, 
                       change_reason: str = None) -> Optional[LocationVersion]:
        """Revert a location to a specific version."""
        if location.revert_to_version(version_number):
            self.session.commit()
            return location.current_version
        return None
        
    def compare_versions(self, version1: LocationVersion, 
                        version2: LocationVersion) -> Dict[str, Dict[str, Any]]:
        """Compare two versions and return differences."""
        differences = {}
        
        # Fields to compare (excluding metadata fields)
        fields_to_compare = [
            'name', 'description', 'type', 'coordinates', 'size', 'level',
            'difficulty', 'resources', 'npcs', 'quests', 'points_of_interest',
            'features', 'objects', 'state'
        ]
        
        for field in fields_to_compare:
            val1 = getattr(version1, field)
            val2 = getattr(version2, field)
            
            if val1 != val2:
                differences[field] = {
                    'old': val1,
                    'new': val2
                }
                
        return differences
        
    def get_location_at_date(self, location_id: int, target_date: datetime) -> Optional[LocationVersion]:
        """Get the version of a location as it existed at a specific date."""
        return (LocationVersion.query
                .filter(
                    LocationVersion.location_id == location_id,
                    LocationVersion.created_at <= target_date
                )
                .order_by(LocationVersion.version_number.desc())
                .first()) 