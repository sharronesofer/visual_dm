# Mock dependencies for quest system tests
from unittest.mock import MagicMock, patch
import sys

# Mock Firebase functions
mock_firebase_app = MagicMock()
mock_firestore = MagicMock()

# Apply patches to prevent actual Firebase imports
sys.modules["firebase_admin"] = MagicMock()
sys.modules["firebase_admin.firestore"] = MagicMock()
sys.modules["firebase_admin.credentials"] = MagicMock()

# Mock event system dependencies
sys.modules["backend.core"] = MagicMock()
sys.modules["backend.core.event_bus"] = MagicMock()

# Other common mocks that might be needed
mock_database = MagicMock()
mock_auth = MagicMock()
mock_storage = MagicMock()

# Mock quest manager dependencies
mock_quest_repository = MagicMock()
mock_quest_service = MagicMock()
