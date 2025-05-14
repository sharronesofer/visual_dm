"""
Core Firebase operations for database interaction.
"""

import firebase_admin
from firebase_admin import credentials, db
from typing import Any, Dict, Optional, Union
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FirebaseClient:
    """
    Authoritative class for all Firebase operations.
    Consolidates functionality from FirebaseClient, FirebaseRoutes, and standalone functions.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, base_path: str = ""):
        """Initialize with optional base path."""
        if not self._initialized:
            self.base_path = base_path
            self._ref = None
            FirebaseClient._initialized = True
    
    @property
    def ref(self):
        """Lazy initialization of Firebase reference."""
        if self._ref is None:
            try:
                self._ref = db.reference(self.base_path)
            except ValueError:
                # Firebase not initialized yet
                from app.core.utils.firebase_utils import initialize_firebase
                initialize_firebase()
                self._ref = db.reference(self.base_path)
        return self._ref
    
    def get(self, path: str = "") -> Optional[Dict[str, Any]]:
        """Get data from Firebase at the specified path."""
        try:
            return self.ref.child(path).get()
        except Exception as e:
            logger.error(f"Error getting data from Firebase: {e}")
            return None
            
    def set(self, path: str, data: Dict[str, Any]) -> bool:
        """Set data in Firebase at the specified path."""
        try:
            self.ref.child(path).set(data)
            logger.debug(f"Set data at path: {path}")
            return True
        except Exception as e:
            logger.error(f"Error setting data in Firebase: {e}")
            return False
            
    def update(self, path: str, data: Dict[str, Any]) -> bool:
        """Update data in Firebase at the specified path."""
        try:
            self.ref.child(path).update(data)
            logger.debug(f"Updated data at path: {path}")
            return True
        except Exception as e:
            logger.error(f"Error updating data in Firebase: {e}")
            return False
            
    def delete(self, path: str) -> bool:
        """Delete data from Firebase at the specified path."""
        try:
            self.ref.child(path).delete()
            logger.debug(f"Deleted data at path: {path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting data from Firebase: {e}")
            return False
            
    def push(self, path: str, data: Dict[str, Any]) -> Optional[str]:
        """Push data to Firebase at the specified path and return the key."""
        try:
            new_ref = self.ref.child(path).push(data)
            logger.debug(f"Pushed data at path: {path}")
            return new_ref.key
        except Exception as e:
            logger.error(f"Error pushing data to Firebase: {e}")
            return None
            
    def log_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Log an event to Firebase."""
        try:
            self.ref.child('events').push({
                'type': event_type,
                'data': event_data,
                'timestamp': {'.sv': 'timestamp'}
            })
            logger.debug(f"Logged event: {event_type}")
        except Exception as e:
            logger.error(f"Error logging event to Firebase: {e}")

# Create a default instance for convenience
firebase_client = FirebaseClient()

# Legacy function wrappers for backward compatibility
def firebase_get(path: str) -> Optional[Dict[str, Any]]:
    """Legacy wrapper for get operation."""
    return firebase_client.get(path)

def firebase_set(path: str, data: Dict[str, Any]) -> bool:
    """Legacy wrapper for set operation."""
    return firebase_client.set(path, data)

def firebase_update(path: str, data: Dict[str, Any]) -> bool:
    """Legacy wrapper for update operation."""
    return firebase_client.update(path, data)

def firebase_delete(path: str) -> bool:
    """Legacy wrapper for delete operation."""
    return firebase_client.delete(path) 