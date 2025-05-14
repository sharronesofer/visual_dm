"""
Firebase-based event logging functionality.
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional
from firebase_admin import db
import os

class FirebaseLogger:
    """A class for logging events to Firebase."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, base_path: str = "logs"):
        """Initialize the logger with a base path in Firebase."""
        if not self._initialized:
            self.base_path = base_path
            self._ref = None
            FirebaseLogger._initialized = True
    
    @property
    def ref(self):
        """Lazy initialization of Firebase reference."""
        if self._ref is None:
            if os.getenv("TESTING") == "true":
                # Use mock reference in tests
                from unittest.mock import MagicMock
                self._ref = MagicMock()
                self._ref.push.return_value = MagicMock(key='test-key')
            else:
                try:
                    self._ref = db.reference(self.base_path)
                except ValueError:
                    # Firebase not initialized yet
                    from app.core.utils.firebase_utils import initialize_firebase
                    initialize_firebase()
                    self._ref = db.reference(self.base_path)
        return self._ref
    
    def log_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Log an event to Firebase."""
        try:
            event = {
                'type': event_type,
                'data': event_data,
                'timestamp': datetime.now().isoformat()
            }
            self.ref.push(event)
            return True
        except Exception as e:
            print(f"Error logging event to Firebase: {e}")
            return False
    
    def log_error(self, error_message: str, context: Dict[str, Any]) -> bool:
        """Log an error to Firebase."""
        return self.log_event('error', {
            'message': error_message,
            'context': context
        })
    
    def log_user_action(self, user_id: str, action: str, details: Dict[str, Any]) -> bool:
        """Log a user action to Firebase."""
        return self.log_event('user_action', {
            'user_id': user_id,
            'action': action,
            'details': details
        })
    
    def log_system_metric(self, metric_name: str, value: Any, metadata: Dict[str, Any] = None) -> bool:
        """Log a system metric to Firebase."""
        return self.log_event('system_metric', {
            'metric': metric_name,
            'value': value,
            'metadata': metadata or {}
        })

# Global logger instance
_logger = FirebaseLogger()

def log_event(event_type: str, event_data: Dict[str, Any]) -> bool:
    """Global function to log an event to Firebase."""
    return _logger.log_event(event_type, event_data)

def log_error(error_message: str, context: Dict[str, Any]) -> bool:
    """Global function to log an error to Firebase."""
    return _logger.log_error(error_message, context)

def log_user_action(user_id: str, action: str, details: Dict[str, Any]) -> bool:
    """Global function to log a user action to Firebase."""
    return _logger.log_user_action(user_id, action, details)

def log_system_metric(metric_name: str, value: Any, metadata: Dict[str, Any] = None) -> bool:
    """Global function to log a system metric to Firebase."""
    return _logger.log_system_metric(metric_name, value, metadata)