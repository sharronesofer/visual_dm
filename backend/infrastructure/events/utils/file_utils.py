"""
File management utilities.
Inherits from BaseManager for common functionality.
"""

import logging
import os
import shutil
from typing import Optional, List, Dict, Any
from pathlib import Path
from backend.infrastructure.utils import secure_filename
from backend.infrastructure.events.utils.base_manager import BaseManager
from backend.infrastructure.config import settings
import json
import yaml
from datetime import datetime

logger = logging.getLogger(__name__)

class FileManager(BaseManager):
    """Manager for file operations and asset management"""
    
    def __init__(self):
        super().__init__()
        self.base_path = Path(settings.BASE_DIR)
        self.data_path = self.base_path / "data"
        self.upload_folder = self.base_path / "uploads"
        self.asset_folder = self.base_path / "assets"
        self.max_file_size = 16 * 1024 * 1024  # 16MB default
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'md'}
        self.max_filename_length = 255
        
        # MIME type validation mapping
        self.allowed_mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'md': 'text/markdown'
        }
        
        # Create necessary directories
        self.ensure_directories()
        
    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.upload_folder.mkdir(parents=True, exist_ok=True)
        self.asset_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directories: {self.upload_folder}, {self.asset_folder}")
        
    def save_file(self, file: Any, filename: Optional[str] = None) -> Optional[str]:
        """Save an uploaded file."""
        try:
            if not file:
                return None
                
            if not filename:
                filename = secure_filename(file.filename)
                
            if not self._is_allowed_file(filename):
                return None
                
            file_path = self.upload_folder / filename
            file.save(str(file_path))
            
            logger.info(f"Saved file: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self._log_error('file save', e)
            return None
            
    def move_to_assets(self, source_path: str) -> Optional[str]:
        """Move a file to the assets directory."""
        try:
            source = Path(source_path)
            if not source.exists():
                return None
                
            target_folder = self.asset_folder / source.parent.name
            target_folder.mkdir(parents=True, exist_ok=True)
            
            target_path = target_folder / source.name
            shutil.move(str(source), str(target_path))
            
            logger.info(f"Moved file to assets: {target_path}")
            return str(target_path)
            
        except Exception as e:
            self._log_error('file move', e)
            return None
            
    def delete_file(self, file_path: str) -> bool:
        """Delete a file."""
        try:
            full_path = self.data_path / file_path
            if full_path.exists():
                full_path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            self._log_error('file deletion', e)
            return False
            
    def _is_allowed_file(self, filename: str) -> bool:
        """Check if the file type is allowed with enhanced security validation."""
        if not filename or not isinstance(filename, str):
            return False
            
        # Check filename length
        if len(filename) > self.max_filename_length:
            logger.warning(f"Filename too long: {len(filename)} characters")
            return False
            
        # Check for path traversal attempts
        if '..' in filename or filename.startswith('/') or '\\' in filename:
            logger.warning(f"Potential path traversal attempt: {filename}")
            return False
            
        # Check for null bytes or control characters
        if '\x00' in filename or any(ord(c) < 32 for c in filename if c not in '\t\n\r'):
            logger.warning(f"Invalid characters in filename: {filename}")
            return False
            
        # Standard extension check
        if '.' not in filename:
            return False
            
        extension = filename.rsplit('.', 1)[1].lower()
        if extension not in self.allowed_extensions:
            logger.warning(f"File extension not allowed: {extension}")
            return False
            
        return True
        
    def _validate_file_content(self, file_path: str, expected_extension: str) -> bool:
        """Validate file content matches expected type."""
        try:
            import magic
            
            # Get file MIME type
            mime_type = magic.from_file(file_path, mime=True)
            expected_mime = self.allowed_mime_types.get(expected_extension)
            
            if expected_mime and mime_type != expected_mime:
                logger.warning(f"MIME type mismatch: expected {expected_mime}, got {mime_type}")
                return False
                
            return True
        except ImportError:
            # python-magic not available, skip MIME validation
            logger.warning("python-magic not installed, skipping MIME type validation")
            return True
        except Exception as e:
            logger.error(f"Error validating file content: {e}")
            return False

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a file."""
        try:
            full_path = self.data_path / file_path
            if not full_path.exists():
                return None
                
            return {
                'name': full_path.name,
                'size': full_path.stat().st_size,
                'created': datetime.fromtimestamp(full_path.stat().st_ctime),
                'modified': datetime.fromtimestamp(full_path.stat().st_mtime),
                'type': full_path.suffix[1:] if full_path.suffix else None
            }
        except Exception as e:
            self._log_error('file info retrieval', e)
            return None

    def read_file(self, file_path: str, file_type: str = "json") -> Dict[str, Any]:
        """Read a file and return its contents."""
        full_path = self.data_path / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(full_path, 'r') as f:
            if file_type == "json":
                return json.load(f)
            elif file_type == "yaml":
                return yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

    def write_file(self, file_path: str, data: Dict[str, Any], file_type: str = "json") -> None:
        """Write data to a file."""
        full_path = self.data_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'w') as f:
            if file_type == "json":
                json.dump(data, f, indent=2)
            elif file_type == "yaml":
                yaml.dump(data, f, default_flow_style=False)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """List files in a directory matching a pattern."""
        full_path = self.data_path / directory
        if not full_path.exists():
            return []
        return [str(f.relative_to(self.data_path)) for f in full_path.glob(pattern)]

    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        return (self.data_path / file_path).exists() 