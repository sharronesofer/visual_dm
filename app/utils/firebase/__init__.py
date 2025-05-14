"""
Firebase initialization and utilities.
"""

import os
from unittest.mock import MagicMock
from app.utils.firebase.client import firebase_get, firebase_set, firebase_update, firebase_delete
from app.utils.firebase.logging import log_event, log_error, log_user_action, log_system_metric
from app.utils.firebase.routes import firebase_bp

# Check if we're in a test environment
if os.getenv("TESTING") == "True":
    # Create mock objects
    mock_ref = MagicMock()
    mock_ref.get.return_value = {}
    mock_ref.set.return_value = None
    mock_ref.update.return_value = None
    mock_ref.delete.return_value = None
    mock_ref.push.return_value = MagicMock(key='test-key')
    mock_ref.child.return_value = mock_ref

    # Create mock functions
    def mock_log_event(*args, **kwargs):
        return True

    def mock_log_error(*args, **kwargs):
        return True

    def mock_log_user_action(*args, **kwargs):
        return True

    def mock_log_system_metric(*args, **kwargs):
        return True

    # Export mock functions
    log_event = mock_log_event
    log_error = mock_log_error
    log_user_action = mock_log_user_action
    log_system_metric = mock_log_system_metric

else:
    # Import real functions
    from app.utils.firebase.logging import log_event, log_error, log_user_action, log_system_metric

__all__ = [
    'firebase_get',
    'firebase_set',
    'firebase_update',
    'firebase_delete',
    'log_event',
    'log_error',
    'log_user_action',
    'log_system_metric',
    'firebase_bp'
] 