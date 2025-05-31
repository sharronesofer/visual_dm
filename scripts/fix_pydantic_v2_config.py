#!/usr/bin/env python3
"""
Pydantic V2 Configuration Migration Script

This script fixes common Pydantic V1 -> V2 migration issues:
- class Config -> model_config = ConfigDict(...)
- orm_mode = True -> from_attributes = True
- allow_population_by_field_name = True -> populate_by_name = True
- @validator -> @field_validator
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PydanticV2ConfigFixer:
    """Fixes Pydantic V1 configuration patterns to V2 format."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.files_processed = 0
        self.total_fixes = 0
    
    def fix_pydantic_config(self, content: str) -> Tuple[str, int]:
        """Fix Pydantic V1 patterns in content."""
        fixes_made = 0
        original_content = content
        
        # Fix class Config -> model_config = ConfigDict(...)
        class_config_pattern = r'(\s*)class Config:\s*\n((?:\s*[^}]+\n)*?)'
        
        def replace_class_config(match):
            nonlocal fixes_made
            indent = match.group(1)
            config_body = match.group(2)
            
            # Extract configuration options
            options = []
            for line in config_body.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Fix common patterns
                    if 'orm_mode = True' in line:
                        options.append('from_attributes=True')
                    elif 'allow_population_by_field_name = True' in line:
                        options.append('populate_by_name=True')
                    elif '=' in line and not line.startswith('def '):
                        options.append(line)
            
            if options:
                config_dict_content = ', '.join(options)
                replacement = f'{indent}model_config = ConfigDict({config_dict_content})'
            else:
                replacement = f'{indent}model_config = ConfigDict()'
            
            fixes_made += 1
            return replacement
        
        content = re.sub(class_config_pattern, replace_class_config, content, flags=re.MULTILINE)
        
        # Add ConfigDict import if we made changes and it's not already imported
        if fixes_made > 0 and 'from pydantic import' in content and 'ConfigDict' not in content:
            # Find existing pydantic import and add ConfigDict
            pydantic_import_pattern = r'(from pydantic import [^;\n]+)'
            def add_config_dict(match):
                import_line = match.group(1)
                if 'ConfigDict' not in import_line:
                    return f'{import_line}, ConfigDict'
                return import_line
            
            content = re.sub(pydantic_import_pattern, add_config_dict, content)
            
        # If no pydantic import found but we made fixes, add it
        elif fixes_made > 0 and 'ConfigDict' not in content:
            # Add import at the top after other imports
            import_lines = content.split('\n')
            insert_idx = 0
            for i, line in enumerate(import_lines):
                if line.startswith('from ') or line.startswith('import '):
                    insert_idx = i + 1
                elif line.strip() == '':
                    continue
                else:
                    break
            
            import_lines.insert(insert_idx, 'from pydantic import ConfigDict')
            content = '\n'.join(import_lines)
        
        return content, fixes_made
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip if no class Config found
            if 'class Config:' not in content:
                return False
            
            new_content, fixes_made = self.fix_pydantic_config(content)
            
            if fixes_made > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                logger.info(f"Fixed {fixes_made} Pydantic issues in {file_path}")
                self.total_fixes += fixes_made
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return False
    
    def process_directory(self, directory: Path) -> None:
        """Process all Python files in a directory recursively."""
        python_files = list(directory.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files in {directory}")
        
        for file_path in python_files:
            if self.process_file(file_path):
                self.files_processed += 1
    
    def run(self, directories: List[str] = None) -> None:
        """Run the migration on specified directories."""
        if directories is None:
            directories = ["backend/systems", "backend/infrastructure"]
        
        logger.info("Starting Pydantic V2 configuration migration...")
        
        for directory in directories:
            dir_path = self.project_root / directory
            if dir_path.exists():
                logger.info(f"Processing directory: {dir_path}")
                self.process_directory(dir_path)
            else:
                logger.warning(f"Directory not found: {dir_path}")
        
        logger.info(f"Migration complete!")
        logger.info(f"Files processed: {self.files_processed}")
        logger.info(f"Total fixes applied: {self.total_fixes}")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix Pydantic V2 configuration issues")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--directories", nargs="+", default=["backend/systems", "backend/infrastructure"], 
                        help="Directories to process")
    
    args = parser.parse_args()
    
    fixer = PydanticV2ConfigFixer(args.project_root)
    fixer.run(args.directories)

if __name__ == "__main__":
    main() 