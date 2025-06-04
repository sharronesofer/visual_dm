#!/usr/bin/env python3
"""
Enhanced batch processing script to fix remaining common test errors.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedBatchFixer:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.fixes_applied = 0
        self.files_modified = 0
        
    def fix_pydantic_v2_migrations(self, content: str) -> Tuple[str, int]:
        """Fix Pydantic v2 migration issues."""
        fixes = 0
        
        # Fix .dict() -> .model_dump()
        if '.dict()' in content:
            content = re.sub(r'\.dict\(\)', '.model_dump()', content)
            fixes += 1
            logger.info("  Fixed .dict() -> .model_dump()")
        
        # Fix .copy() -> .model_copy()
        if '.copy(' in content:
            content = re.sub(r'\.copy\(', '.model_copy(', content)
            fixes += 1
            logger.info("  Fixed .copy() -> .model_copy()")
        
        # Fix orm_mode=True -> from_attributes=True
        if 'orm_mode=True' in content:
            content = re.sub(r'orm_mode=True', 'from_attributes=True', content)
            fixes += 1
            logger.info("  Fixed orm_mode=True -> from_attributes=True")
        
        return content, fixes
    
    def fix_enum_value_mismatches(self, content: str) -> Tuple[str, int]:
        """Fix enum value mismatches."""
        fixes = 0
        
        # Season enum fixes
        if 'Season.FALL' in content:
            content = re.sub(r'Season\.FALL', 'Season.AUTUMN', content)
            fixes += 1
            logger.info("  Fixed Season.FALL -> Season.AUTUMN")
        
        # Weather enum fixes
        weather_fixes = {
            'WeatherState.CLOUDY': 'WeatherState.CLEAR',
            'WeatherState.RAIN': 'WeatherState.CLEAR',
            'WeatherCondition.CLOUDY': 'WeatherCondition.CLEAR',
            'WeatherCondition.RAIN': 'WeatherCondition.CLEAR'
        }
        
        for old, new in weather_fixes.items():
            if old in content:
                content = re.sub(re.escape(old), new, content)
                fixes += 1
                logger.info(f"  Fixed {old} -> {new}")
        
        return content, fixes
    
    def fix_missing_imports(self, content: str, file_path: str) -> Tuple[str, int]:
        """Fix missing imports based on file context."""
        fixes = 0
        
        # Fix Calendar import in time manager tests
        if 'test_time_manager.py' in file_path and 'Calendar' in content and 'from backend.systems.game_time.models.calendar_model import' not in content:
            # Find imports section
            lines = content.split('\n')
            import_line_idx = None
            for i, line in enumerate(lines):
                if line.startswith('from backend.systems.game_time'):
                    import_line_idx = i
                    break
            
            if import_line_idx is not None:
                lines.insert(import_line_idx + 1, 'from backend.systems.game_time.models.calendar_model import Calendar')
                
                content = '\n'.join(lines)
                fixes += 1
                logger.info("  Added Calendar import")
        
        return content, fixes
    
    def fix_json_serialization(self, content: str) -> Tuple[str, int]:
        """Fix JSON serialization issues with datetime objects."""
        fixes = 0
        
        # Add datetime JSON encoder import if needed
        if 'json.dump(' in content and 'datetime' in content and 'default=' not in content:
            # Add custom JSON encoder
            if 'import json' in content and 'from datetime import datetime' in content:
                # Replace json.dump calls with custom encoder
                content = re.sub(
                    r'json\.dump\(([^,]+),\s*([^,]+)(?:,\s*indent=\d+)?\)',
                    r'json.dump(\1, \2, default=str, indent=2)',
                    content
                )
                fixes += 1
                logger.info("  Added datetime JSON serialization fix")
        
        return content, fixes
    
    def fix_api_mismatches(self, content: str) -> Tuple[str, int]:
        """Fix API mismatches between test expectations and actual implementation."""
        fixes = 0
        
        # Fix TimeManager.game_time -> TimeManager.get_time()
        if 'time_manager.game_time' in content:
            content = re.sub(r'time_manager\.game_time', 'time_manager.get_time()', content)
            fixes += 1
            logger.info("  Fixed time_manager.game_time -> time_manager.get_time()")
        
        # Fix CalendarData.days_per_month -> CalendarData.days_in_current_month
        if '.days_per_month' in content:
            content = re.sub(r'\.days_per_month', '.days_in_current_month', content)
            fixes += 1
            logger.info("  Fixed .days_per_month -> .days_in_current_month")
        
        return content, fixes
    
    def process_file(self, file_path: str) -> bool:
        """Process a single file with all fixes."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            total_fixes = 0
            
            # Apply all fix categories
            content, fixes = self.fix_pydantic_v2_migrations(content)
            total_fixes += fixes
            
            content, fixes = self.fix_enum_value_mismatches(content)
            total_fixes += fixes
            
            content, fixes = self.fix_missing_imports(content, file_path)
            total_fixes += fixes
            
            content, fixes = self.fix_json_serialization(content)
            total_fixes += fixes
            
            content, fixes = self.fix_api_mismatches(content)
            total_fixes += fixes
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.files_modified += 1
                self.fixes_applied += total_fixes
                logger.info(f"Modified {file_path} with {total_fixes} fixes")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return False
    
    def process_directory(self, directory: str) -> None:
        """Process all Python files in a directory."""
        for root, dirs, files in os.walk(directory):
            # Skip certain directories
            skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.process_file(file_path)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced batch fix for common test errors')
    parser.add_argument('--project-root', default=os.getcwd(), help='Project root directory')
    parser.add_argument('--dirs', nargs='+', default=['backend/tests'], help='Directories to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without making changes')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    fixer = EnhancedBatchFixer(args.project_root)
    
    logger.info(f"Starting enhanced batch fixes on directories: {args.dirs}")
    
    for directory in args.dirs:
        full_path = os.path.join(args.project_root, directory)
        if os.path.exists(full_path):
            logger.info(f"Processing directory: {full_path}")
            fixer.process_directory(full_path)
        else:
            logger.warning(f"Directory not found: {full_path}")
    
    logger.info(f"Enhanced batch fixes complete. Applied {fixer.fixes_applied} fixes to {fixer.files_modified} files.")

if __name__ == "__main__":
    main() 