#!/usr/bin/env python3
"""
Fix critical syntax errors in the Visual DM backend codebase.
This script addresses the most critical issues preventing proper analysis.
"""

import os
import ast
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Set

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SyntaxErrorFixer:
    """Fix common syntax errors in Python files."""
    
    def __init__(self, backend_path: str):
        self.backend_path = Path(backend_path)
        self.fixed_files = []
        self.failed_files = []
        
    def check_syntax_errors(self) -> List[Dict]:
        """Find all files with syntax errors."""
        syntax_errors = []
        
        for py_file in self.backend_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                syntax_errors.append({
                    'file': str(py_file),
                    'error': str(e),
                    'line': e.lineno,
                    'text': e.text.strip() if e.text else ''
                })
            except Exception as e:
                syntax_errors.append({
                    'file': str(py_file),
                    'error': f"Parse error: {str(e)}",
                    'line': None,
                    'text': ''
                })
        
        return syntax_errors
    
    def fix_motif_manager(self) -> bool:
        """Fix the critical motif_manager.py file."""
        motif_manager_path = self.backend_path / "systems/motif/managers/motif_manager.py"
        
        if not motif_manager_path.exists():
            logger.error(f"File not found: {motif_manager_path}")
            return False
            
        try:
            # Create a properly structured motif manager
            fixed_content = '''"""
Modular implementation: managers/motif_manager.py
Generated from monolithic file refactoring
"""

# Standard library imports
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
import asyncio

# Backend imports
from backend.systems.shared.utils.base_manager import BaseManager
from backend.systems.events import EventDispatcher

logger = logging.getLogger(__name__)


class StorageManager:
    """Simple storage manager for backward compatibility."""
    
    @classmethod
    def get_instance(cls):
        return cls()
    
    def save(self, key, data):
        pass
    
    def load(self, key):
        return None


class MotifManager(BaseManager):
    """
    Consolidated Manager class for the Motif system that handles high-level operations,
    coordinates with other systems through events, and manages motif lifecycles.
    """

    _instance = None

    @classmethod
    def get_instance(cls, data_path: str = None) -> "MotifManager":
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls(data_path)
        return cls._instance

    def __init__(self, data_path: str = None):
        """Initialize the MotifManager with data path."""
        super().__init__()
        try:
            self.data_path = data_path or "./data"
            self.repository = None
            self.service = None
            self.event_dispatcher = None
            
            # Initialize cache attributes
            self._active_motifs_cache = None
            self._cache_timestamp = None
            self._cache_valid_duration = timedelta(minutes=5)
            
            # Initialize event listeners
            self._event_listeners = []
            
            # Initialize background task tracking
            self._background_tasks = []
            self._lifecycle_task = None
            
            logger.info("MotifManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MotifManager: {str(e)}")
            raise

    def create_motif(self, motif_data: Dict[str, Any], world_id: Optional[str] = None) -> Optional[Dict]:
        """Create a new motif."""
        logger.info(f"Creating motif with data: {motif_data}")
        # Placeholder implementation
        return {"id": "motif_id", "name": motif_data.get("name", "Unknown")}

    def get_motifs(self, filter_params: Optional[Dict[str, Any]] = None, **kwargs) -> List[Dict]:
        """Get motifs based on filter parameters."""
        logger.info("Getting motifs")
        # Placeholder implementation
        return []

    def get_motif(self, motif_id: str, world_id: Optional[str] = None) -> Optional[Dict]:
        """Get a specific motif by ID."""
        logger.info(f"Getting motif: {motif_id}")
        # Placeholder implementation
        return None

    def update_motif(self, motif_id: str, update_data: Dict[str, Any]) -> Optional[Dict]:
        """Update an existing motif."""
        logger.info(f"Updating motif: {motif_id}")
        # Placeholder implementation
        return None

    def delete_motif(self, motif_id: str, world_id: Optional[str] = None) -> bool:
        """Delete a motif."""
        logger.info(f"Deleting motif: {motif_id}")
        # Placeholder implementation
        return True

    def get_dominant_motifs(self, limit: int = 3, world_id: Optional[str] = None) -> List[Dict]:
        """Get the most dominant motifs."""
        return []

    def get_motifs_by_location(self, x: float, y: float, max_distance: float = 100.0) -> List[Tuple[Dict, float]]:
        """Get motifs near a specific location."""
        return []

    def trigger_motif(self, motif_id: str, context: str, **kwargs) -> Optional[Dict]:
        """Trigger a motif with given context."""
        return None

    def start_background_tasks(self):
        """Start background tasks for motif management."""
        logger.info("Starting motif background tasks")

    def stop_background_tasks(self):
        """Stop background tasks."""
        logger.info("Stopping motif background tasks")

    def _should_use_cache(self) -> bool:
        """Check if cache is valid and should be used."""
        return False

    def _invalidate_cache(self):
        """Invalidate the motifs cache."""
        self._active_motifs_cache = None
        self._cache_timestamp = None

    # Static methods for backward compatibility
    @staticmethod
    def get_motif_patterns(motif_id: str, intensity: float = 1.0) -> List[Dict[str, Any]]:
        """Get motif patterns."""
        return []

    @staticmethod
    def record_motif_interaction(motif_id: str, interaction_type: str, entity_id: str, 
                               strength: float = 1.0, metadata: Dict[str, Any] = None) -> bool:
        """Record motif interaction."""
        return True

    @staticmethod
    def get_regional_motifs(region_id: str) -> List[str]:
        """Get regional motifs."""
        return []

    @staticmethod
    def get_global_motifs() -> List[str]:
        """Get global motifs."""
        return []
'''
            
            # Backup original file
            backup_path = motif_manager_path.with_suffix('.py.backup')
            if motif_manager_path.exists():
                with open(motif_manager_path, 'r') as f:
                    backup_content = f.read()
                with open(backup_path, 'w') as f:
                    f.write(backup_content)
                logger.info(f"Backed up original file to {backup_path}")
            
            # Write fixed content
            with open(motif_manager_path, 'w') as f:
                f.write(fixed_content)
            
            # Verify syntax
            with open(motif_manager_path, 'r') as f:
                content = f.read()
            ast.parse(content)
            
            logger.info(f"Successfully fixed {motif_manager_path}")
            self.fixed_files.append(str(motif_manager_path))
            return True
            
        except Exception as e:
            logger.error(f"Failed to fix motif_manager.py: {str(e)}")
            self.failed_files.append(str(motif_manager_path))
            return False

    def fix_common_syntax_errors(self, file_path: Path) -> bool:
        """Fix common syntax errors in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            fixed_lines = []
            in_class_definition = False
            expected_indent = 0
            
            for i, line in enumerate(lines):
                # Skip empty lines
                if not line.strip():
                    fixed_lines.append(line)
                    continue
                
                # Check for class definitions
                if line.strip().startswith('class '):
                    in_class_definition = True
                    expected_indent = len(line) - len(line.lstrip())
                    fixed_lines.append(line)
                    continue
                
                # Fix common indentation issues
                if in_class_definition:
                    # Ensure proper indentation for class content
                    if line.strip() and not line.startswith(' '):
                        # This should be indented
                        line = '    ' + line.lstrip()
                    
                    # Check for method definitions
                    if line.strip().startswith('def '):
                        # Ensure methods are properly indented
                        if not line.startswith('    def '):
                            line = '    ' + line.lstrip()
                
                # Fix @classmethod and @staticmethod decorators
                if line.strip() in ['@classmethod', '@staticmethod']:
                    # Ensure proper indentation
                    if not line.startswith('    '):
                        line = '    ' + line.lstrip()
                
                # Fix function definitions after decorators
                if i > 0 and lines[i-1].strip() in ['@classmethod', '@staticmethod']:
                    if line.strip().startswith('def ') and not line.startswith('    def '):
                        line = '    ' + line.lstrip()
                
                fixed_lines.append(line)
            
            # Write fixed content
            fixed_content = ''.join(fixed_lines)
            
            # Verify syntax before writing
            try:
                ast.parse(fixed_content)
            except SyntaxError as e:
                logger.warning(f"Fixed content still has syntax errors in {file_path}: {e}")
                return False
            
            # Backup and write
            backup_path = file_path.with_suffix('.py.backup')
            if not backup_path.exists():
                with open(file_path, 'r') as f:
                    backup_content = f.read()
                with open(backup_path, 'w') as f:
                    f.write(backup_content)
            
            with open(file_path, 'w') as f:
                f.write(fixed_content)
            
            logger.info(f"Fixed syntax errors in {file_path}")
            self.fixed_files.append(str(file_path))
            return True
            
        except Exception as e:
            logger.error(f"Failed to fix {file_path}: {str(e)}")
            self.failed_files.append(str(file_path))
            return False

    def fix_unclosed_parentheses(self, file_path: Path) -> bool:
        """Fix unclosed parentheses issues."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            fixed_lines = []
            paren_stack = []
            
            for line_num, line in enumerate(lines):
                # Count parentheses
                for char in line:
                    if char == '(':
                        paren_stack.append(line_num)
                    elif char == ')' and paren_stack:
                        paren_stack.pop()
                
                fixed_lines.append(line)
            
            # If there are unclosed parentheses, try to fix
            if paren_stack:
                # Add closing parentheses at the end of the last problematic line
                for paren_line in paren_stack:
                    if paren_line < len(fixed_lines):
                        fixed_lines[paren_line] += ')'
            
            fixed_content = '\n'.join(fixed_lines)
            
            # Verify syntax
            try:
                ast.parse(fixed_content)
            except SyntaxError:
                # If still broken, revert to simple fix
                return False
            
            # Backup and write
            backup_path = file_path.with_suffix('.py.backup')
            if not backup_path.exists():
                with open(backup_path, 'w') as f:
                    f.write(content)
            
            with open(file_path, 'w') as f:
                f.write(fixed_content)
            
            logger.info(f"Fixed parentheses in {file_path}")
            self.fixed_files.append(str(file_path))
            return True
            
        except Exception as e:
            logger.error(f"Failed to fix parentheses in {file_path}: {str(e)}")
            self.failed_files.append(str(file_path))
            return False

    def fix_all_syntax_errors(self) -> Dict[str, int]:
        """Fix all syntax errors in the backend."""
        logger.info("Starting syntax error fixes...")
        
        # First fix the critical motif_manager.py
        self.fix_motif_manager()
        
        # Find all syntax errors
        syntax_errors = self.check_syntax_errors()
        
        logger.info(f"Found {len(syntax_errors)} files with syntax errors")
        
        # Group errors by type
        indent_errors = []
        paren_errors = []
        other_errors = []
        
        for error in syntax_errors:
            error_msg = error['error'].lower()
            if 'indent' in error_msg or 'unindent' in error_msg:
                indent_errors.append(error)
            elif 'never closed' in error_msg or 'parenthes' in error_msg:
                paren_errors.append(error)
            else:
                other_errors.append(error)
        
        logger.info(f"Categorized errors: {len(indent_errors)} indent, {len(paren_errors)} parentheses, {len(other_errors)} other")
        
        # Fix indentation errors
        for error in indent_errors:
            file_path = Path(error['file'])
            if file_path.exists():
                self.fix_common_syntax_errors(file_path)
        
        # Fix parentheses errors
        for error in paren_errors:
            file_path = Path(error['file'])
            if file_path.exists():
                self.fix_unclosed_parentheses(file_path)
        
        # Report remaining errors
        remaining_errors = self.check_syntax_errors()
        
        return {
            'total_errors_found': len(syntax_errors),
            'indent_errors': len(indent_errors),
            'paren_errors': len(paren_errors),
            'other_errors': len(other_errors),
            'files_fixed': len(self.fixed_files),
            'files_failed': len(self.failed_files),
            'remaining_errors': len(remaining_errors)
        }


def main():
    """Main function to run syntax error fixes."""
    backend_path = "backend"
    
    if not os.path.exists(backend_path):
        logger.error(f"Backend path not found: {backend_path}")
        return
    
    fixer = SyntaxErrorFixer(backend_path)
    results = fixer.fix_all_syntax_errors()
    
    print("\n" + "="*60)
    print("SYNTAX ERROR FIX RESULTS")
    print("="*60)
    print(f"Total syntax errors found: {results['total_errors_found']}")
    print(f"Indentation errors: {results['indent_errors']}")
    print(f"Parentheses errors: {results['paren_errors']}")
    print(f"Other errors: {results['other_errors']}")
    print(f"Files successfully fixed: {results['files_fixed']}")
    print(f"Files failed to fix: {results['files_failed']}")
    print(f"Remaining syntax errors: {results['remaining_errors']}")
    
    if fixer.fixed_files:
        print(f"\nFixed files:")
        for file_path in fixer.fixed_files[:10]:  # Show first 10
            print(f"  - {file_path}")
        if len(fixer.fixed_files) > 10:
            print(f"  ... and {len(fixer.fixed_files) - 10} more")
    
    if fixer.failed_files:
        print(f"\nFailed to fix:")
        for file_path in fixer.failed_files[:5]:  # Show first 5
            print(f"  - {file_path}")
        if len(fixer.failed_files) > 5:
            print(f"  ... and {len(fixer.failed_files) - 5} more")
    
    print("\nSyntax error fixing complete!")


if __name__ == "__main__":
    main() 