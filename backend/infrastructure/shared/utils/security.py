"""
Shared utility module for security
Redirected from werkzeug.utils
"""

# Basic implementations - extend as needed
def secure_filename(filename: str) -> str:
    """Secure a filename by removing potentially dangerous characters."""
    import re
    filename = re.sub(r'[^\w\-_\.]', '', filename)
    return filename

class CoordinateSystem:
    """Basic coordinate system implementation."""
    def __init__(self, origin=(0, 0)):
        self.origin = origin
    
    def transform(self, point):
        return (point[0] - self.origin[0], point[1] - self.origin[1])

def load_data_file(file_path: str):
    """Basic data file loader."""
    import json
    from pathlib import Path
    
    path = Path(file_path)
    if path.suffix == '.json':
        with open(path, 'r') as f:
            return json.load(f)
    else:
        with open(path, 'r') as f:
            return f.read()
