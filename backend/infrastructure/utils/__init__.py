"""
Utility functions and helpers.
"""

import re
import unicodedata
import os
import json
from pathlib import Path

def ensure_directory(path):
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists
    """
    Path(path).mkdir(parents=True, exist_ok=True)

def safe_write_json(file_path, data):
    """
    Safely write JSON data to a file with error handling.
    
    Args:
        file_path: Path to the JSON file
        data: Data to write as JSON
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if directory:
            ensure_directory(directory)
        
        # Write JSON data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error writing JSON to {file_path}: {e}")
        return False

def secure_filename(filename):
    """
    Secure a filename to prevent directory traversal and other issues.
    This is a basic implementation similar to werkzeug.utils.secure_filename.
    """
    if not filename:
        return "unnamed"
    
    # Replace directory traversal patterns
    filename = filename.replace('..', '')
    filename = filename.replace('/', '_')
    filename = filename.replace('\\', '_')
    
    # Normalize unicode and remove non-ascii
    filename = unicodedata.normalize('NFKD', filename)
    filename = filename.encode('ascii', 'ignore').decode('ascii')
    
    # Remove non-alphanumeric characters except dots, dashes, and underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Remove leading dots and multiple consecutive dots
    filename = re.sub(r'^\.+', '', filename)
    filename = re.sub(r'\.{2,}', '.', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
    
    return filename or "unnamed"

def get_document(path):
    """
    Stub function for document retrieval.
    TODO: Implement actual document retrieval logic.
    """
    return None

def set_document(path, data):
    """
    Stub function for document setting.
    TODO: Implement actual document setting logic.
    """
    return True

def update_document(path, data):
    """
    Stub function for document updating.
    TODO: Implement actual document updating logic.
    """
    return True

def get_collection(name):
    """
    Stub function for collection retrieval.
    TODO: Implement actual collection retrieval logic.
    """
    # Return a mock collection object
    class MockCollection:
        def where(self, *args):
            return self
        def get(self):
            return []
        def add(self, data):
            return {"id": "mock_doc_id"}
        def document(self, doc_id):
            return self
        def set(self, data):
            pass
        def update(self, data):
            pass
        def delete(self):
            pass
    
    return MockCollection()

def get_firestore_client():
    """
    Stub function for Firestore client.
    TODO: Implement actual Firestore client initialization.
    """
    # Return a mock client for now to prevent import errors
    class MockFirestoreClient:
        def collection(self, name):
            return self
        def document(self, name):
            return self
        def get(self):
            return None
        def set(self, data):
            pass
        def update(self, data):
            pass
        def delete(self):
            pass
    
    return MockFirestoreClient()

try:
    from .json_utils import *
    from .error import *
    from .backup import *
    from .restore import *
    from .db_health import *
    from .jwt import *
    from .password import *
    from .audit_log import *
    from .npc_travel_utils import *
except ImportError:
    pass

# Import common exceptions for backwards compatibility
try:
    from backend.infrastructure.shared.exceptions import (
        ServiceError, NotFoundError, ValidationError, ConflictError
    )
except ImportError:
    # Define fallback exceptions if shared module doesn't exist
    class ServiceError(Exception):
        pass
    class NotFoundError(Exception):
        pass
    class ValidationError(Exception):
        pass
    class ConflictError(Exception):
        pass

# Additional domain-specific exceptions
class TensionError(Exception):
    """Exception raised for tension calculation errors."""
    pass

class GenerationError(Exception):
    """Exception raised for world generation errors."""
    pass

# HACK: PerlinNoise placeholder - implement or use external library
# TODO: Implement proper Perlin noise or use noise library
class PerlinNoise:
    """Placeholder Perlin noise implementation"""
    def __init__(self, octaves=4, seed=None):
        self.octaves = octaves
        self.seed = seed or 0
    
    def __call__(self, x, y=None, z=None):
        """Generate noise value at coordinates"""
        import math
        # Simple placeholder that generates pseudo-random values
        if y is None:
            y = 0
        if z is None:
            z = 0
        
        # Basic hash-based noise (not true Perlin)
        h = hash((int(x * 1000), int(y * 1000), int(z * 1000), self.seed)) % 2147483647
        return (h / 2147483647.0) * 2.0 - 1.0

__all__ = [
    "secure_filename",
    "ensure_directory",
    "safe_write_json",
    "get_document",
    "set_document",
    "update_document",
    "get_firestore_client",
    "get_collection",
    "ServiceError",
    "NotFoundError", 
    "ValidationError",
    "ConflictError",
    "TensionError",
    "GenerationError",
    "PerlinNoise",
    # Add specific exports here as needed
] 