"""
Repository for the religion system.

This module provides data access layer for religions and memberships,
handling JSON storage and retrieval.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import Religion, ReligionMembership

# Setup logging
logger = logging.getLogger(__name__)


class ReligionRepository:
    """
    Repository for storing and retrieving religion and membership data.
    
    Handles the data persistence layer, abstracting storage details from
    the service layer.
    """
    
    def __init__(self, storage_dir: str = "data/religion"):
        """Initialize the repository with storage location."""
        self.storage_dir = storage_dir
        self.religions_file = os.path.join(storage_dir, "religions.json")
        self.memberships_file = os.path.join(storage_dir, "memberships.json")
        
        # Ensure storage directory exists
        os.makedirs(storage_dir, exist_ok=True)
        
        # Load data from storage
        self.religions: Dict[str, Religion] = {}
        self.memberships: Dict[str, ReligionMembership] = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """Load religion and membership data from storage."""
        try:
            if os.path.exists(self.religions_file):
                with open(self.religions_file, "r", encoding="utf-8") as f:
                    religions_data = json.load(f)
                    self.religions = {
                        r_id: Religion(**r_data)
                        for r_id, r_data in religions_data.items()
                    }
            
            if os.path.exists(self.memberships_file):
                with open(self.memberships_file, "r", encoding="utf-8") as f:
                    memberships_data = json.load(f)
                    self.memberships = {
                        m_id: ReligionMembership(**m_data)
                        for m_id, m_data in memberships_data.items()
                    }
        except Exception as e:
            logger.error(f"Error loading religion data: {str(e)}")
            # Initialize with empty data on error
            self.religions = {}
            self.memberships = {}
    
    def _save_data(self) -> None:
        """Save religion and membership data to storage."""
        try:
            with open(self.religions_file, "w", encoding="utf-8") as f:
                religions_data = {
                    r_id: r.dict() for r_id, r in self.religions.items()
                }
                json.dump(religions_data, f, indent=2, default=str)
            
            with open(self.memberships_file, "w", encoding="utf-8") as f:
                memberships_data = {
                    m_id: m.dict() for m_id, m in self.memberships.items()
                }
                json.dump(memberships_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving religion data: {str(e)}")
    
    # Religion repository methods
    
    def create_religion(self, religion: Religion) -> Religion:
        """Create a new religion in the repository."""
        self.religions[religion.id] = religion
        self._save_data()
        return religion
    
    def get_religion(self, religion_id: str) -> Optional[Religion]:
        """Get a religion by ID."""
        return self.religions.get(religion_id)
    
    def get_all_religions(self) -> List[Religion]:
        """Get all religions."""
        return list(self.religions.values())
    
    def update_religion(self, religion: Religion) -> Religion:
        """Update an existing religion."""
        self.religions[religion.id] = religion
        self._save_data()
        return religion
    
    def delete_religion(self, religion_id: str) -> bool:
        """Delete a religion by ID."""
        if religion_id not in self.religions:
            return False
        
        del self.religions[religion_id]
        self._save_data()
        return True
    
    # Membership repository methods
    
    def create_membership(self, membership: ReligionMembership) -> ReligionMembership:
        """Create a new membership in the repository."""
        self.memberships[membership.id] = membership
        self._save_data()
        return membership
    
    def get_membership(self, membership_id: str) -> Optional[ReligionMembership]:
        """Get a membership by ID."""
        return self.memberships.get(membership_id)
    
    def get_memberships_by_entity(self, entity_id: str) -> List[ReligionMembership]:
        """Get all memberships for an entity."""
        return [
            m for m in self.memberships.values() 
            if m.entity_id == entity_id
        ]
    
    def get_memberships_by_religion(self, religion_id: str) -> List[ReligionMembership]:
        """Get all memberships for a religion."""
        return [
            m for m in self.memberships.values() 
            if m.religion_id == religion_id
        ]
    
    def update_membership(self, membership: ReligionMembership) -> ReligionMembership:
        """Update an existing membership."""
        self.memberships[membership.id] = membership
        self._save_data()
        return membership
    
    def delete_membership(self, membership_id: str) -> bool:
        """Delete a membership by ID."""
        if membership_id not in self.memberships:
            return False
        
        del self.memberships[membership_id]
        self._save_data()
        return True
    
    def delete_memberships_by_religion(self, religion_id: str) -> int:
        """Delete all memberships for a religion."""
        to_delete = [
            m_id for m_id, m in self.memberships.items()
            if m.religion_id == religion_id
        ]
        
        for m_id in to_delete:
            del self.memberships[m_id]
        
        if to_delete:
            self._save_data()
        
        return len(to_delete) 