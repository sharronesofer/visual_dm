"""
Service for managing NPC version control operations.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.models.npc import NPC
from app.core.models.npc_version import NPCVersion
from app.core.models.version_control import CodeVersion
from app.core.database import db

class NPCVersionService:
    """Service for managing NPC version control operations."""

    @staticmethod
    def create_version(npc: NPC, change_type: str, change_description: str, 
                      changed_fields: List[str], code_version_id: Optional[int] = None) -> NPCVersion:
        """
        Create a new version for an NPC.
        
        Args:
            npc: The NPC instance to version
            change_type: Type of change (e.g., 'update', 'creation', 'deletion')
            change_description: Description of what changed
            changed_fields: List of fields that were changed
            code_version_id: Optional ID of associated code version
            
        Returns:
            The created NPCVersion instance
        """
        return npc.create_version(
            change_type=change_type,
            change_description=change_description,
            changed_fields=changed_fields,
            code_version_id=code_version_id
        )

    @staticmethod
    def get_version_history(npc_id: int) -> List[Dict[str, Any]]:
        """
        Get the complete version history for an NPC.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            List of version dictionaries in chronological order
        """
        npc = NPC.query.get(npc_id)
        if not npc:
            raise ValueError(f"NPC with ID {npc_id} not found")
        
        return npc.get_version_history()

    @staticmethod
    def get_version(npc_id: int, version_number: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific version of an NPC.
        
        Args:
            npc_id: ID of the NPC
            version_number: The version number to retrieve
            
        Returns:
            Version data dictionary or None if not found
        """
        npc = NPC.query.get(npc_id)
        if not npc:
            raise ValueError(f"NPC with ID {npc_id} not found")
        
        return npc.get_version(version_number)

    @staticmethod
    def revert_to_version(npc_id: int, version_number: int) -> None:
        """
        Revert an NPC to a specific version.
        
        Args:
            npc_id: ID of the NPC
            version_number: Version number to revert to
        """
        npc = NPC.query.get(npc_id)
        if not npc:
            raise ValueError(f"NPC with ID {npc_id} not found")
        
        npc.revert_to_version(version_number)
        db.session.commit()

    @staticmethod
    def compare_versions(npc_id: int, version1: int, version2: int) -> Dict[str, Any]:
        """
        Compare two versions of an NPC.
        
        Args:
            npc_id: ID of the NPC
            version1: First version number
            version2: Second version number
            
        Returns:
            Dictionary containing the differences between versions
        """
        npc = NPC.query.get(npc_id)
        if not npc:
            raise ValueError(f"NPC with ID {npc_id} not found")
        
        v1_data = npc.get_version(version1)
        v2_data = npc.get_version(version2)
        
        if not v1_data or not v2_data:
            raise ValueError("One or both versions not found")
        
        differences = {}
        
        # Compare all fields
        for key in v1_data.keys():
            if key in ['id', 'npc_id', 'version_number', 'created_at', 'updated_at']:
                continue
            
            if v1_data[key] != v2_data[key]:
                differences[key] = {
                    'version1': v1_data[key],
                    'version2': v2_data[key]
                }
        
        return differences

    @staticmethod
    def get_versions_by_code_version(code_version_id: int) -> List[Dict[str, Any]]:
        """
        Get all NPC versions associated with a specific code version.
        
        Args:
            code_version_id: ID of the code version
            
        Returns:
            List of NPC versions associated with the code version
        """
        versions = NPCVersion.query.filter_by(code_version_id=code_version_id).all()
        return [version.to_dict() for version in versions]

    @staticmethod
    def get_changes_in_timeframe(npc_id: int, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """
        Get all changes to an NPC within a specific timeframe.
        
        Args:
            npc_id: ID of the NPC
            start_time: Start of the timeframe
            end_time: End of the timeframe
            
        Returns:
            List of versions within the timeframe
        """
        versions = NPCVersion.query.filter(
            NPCVersion.npc_id == npc_id,
            NPCVersion.created_at >= start_time,
            NPCVersion.created_at <= end_time
        ).order_by(NPCVersion.version_number).all()
        
        return [version.to_dict() for version in versions]

    @staticmethod
    def get_latest_version(npc_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the latest version of an NPC.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            Latest version data or None if no versions exist
        """
        latest = NPCVersion.query.filter_by(npc_id=npc_id).order_by(NPCVersion.version_number.desc()).first()
        return latest.to_dict() if latest else None

    @staticmethod
    def get_version_at_time(npc_id: int, timestamp: datetime) -> Optional[Dict[str, Any]]:
        """
        Get the version of an NPC that was current at a specific time.
        
        Args:
            npc_id: ID of the NPC
            timestamp: The point in time
            
        Returns:
            Version data or None if no version existed
        """
        version = NPCVersion.query.filter(
            NPCVersion.npc_id == npc_id,
            NPCVersion.created_at <= timestamp
        ).order_by(NPCVersion.version_number.desc()).first()
        
        return version.to_dict() if version else None

    @staticmethod
    def get_related_versions(npc_id: int, related_npc_id: int) -> List[Dict[str, Any]]:
        """
        Get versions of an NPC that involved changes to its relationship with another NPC.
        
        Args:
            npc_id: ID of the first NPC
            related_npc_id: ID of the related NPC
            
        Returns:
            List of versions involving relationship changes
        """
        versions = NPCVersion.query.filter(
            NPCVersion.npc_id == npc_id,
            NPCVersion.changed_fields.contains(['relationships'])
        ).order_by(NPCVersion.version_number).all()
        
        # Filter versions where the relationship with the specific NPC changed
        related_versions = []
        for version in versions:
            relationships = version.relationships
            if str(related_npc_id) in relationships:
                related_versions.append(version.to_dict())
        
        return related_versions 