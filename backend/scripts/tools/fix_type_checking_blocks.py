#!/usr/bin/env python3
"""
Fix malformed TYPE_CHECKING blocks in Python files.
These blocks have incorrect indentation causing widespread syntax errors.
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TypeCheckingFixer:
    """Fix malformed TYPE_CHECKING blocks."""
    
    def __init__(self, backend_path: str):
        self.backend_path = Path(backend_path)
        self.fixed_files = []
        self.failed_files = []
        
    def fix_type_checking_block(self, content: str) -> str:
        """Fix TYPE_CHECKING import blocks with proper indentation."""
        lines = content.split('\n')
        fixed_lines = []
        in_type_checking = False
        type_checking_indent = 0
        
        for i, line in enumerate(lines):
            # Detect TYPE_CHECKING block start
            if 'if TYPE_CHECKING:' in line:
                in_type_checking = True
                type_checking_indent = len(line) - len(line.lstrip())
                fixed_lines.append(line)
                continue
                
            # Handle lines inside TYPE_CHECKING block
            if in_type_checking:
                # Empty lines are preserved
                if line.strip() == '':
                    fixed_lines.append(line)
                    continue
                    
                current_indent = len(line) - len(line.lstrip())
                
                # Check if this line should be part of the TYPE_CHECKING block
                if (line.strip().startswith('from ') or 
                    line.strip().startswith('import ') or
                    line.strip().startswith('#') or
                    line.strip().startswith(')')):
                    
                    # This line should be indented under TYPE_CHECKING
                    if current_indent <= type_checking_indent:
                        proper_indent = ' ' * (type_checking_indent + 4)
                        fixed_line = proper_indent + line.lstrip()
                        fixed_lines.append(fixed_line)
                    else:
                        fixed_lines.append(line)
                else:
                    # We've reached a line that's not part of TYPE_CHECKING
                    in_type_checking = False
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
                
        return '\n'.join(fixed_lines)
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix a single file's TYPE_CHECKING blocks."""
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Skip if no TYPE_CHECKING
            if 'TYPE_CHECKING' not in content:
                return True
                
            # Fix the content
            fixed_content = self.fix_type_checking_block(content)
            
            # Only write if content changed
            if fixed_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                    
                logger.info(f"Fixed TYPE_CHECKING in {file_path}")
                self.fixed_files.append(str(file_path))
                
            return True
            
        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")
            self.failed_files.append(str(file_path))
            return False
    
    def fix_all_files(self) -> Dict:
        """Fix TYPE_CHECKING blocks in all Python files."""
        logger.info("Starting TYPE_CHECKING block fixes...")
        
        # Find all Python files
        python_files = list(self.backend_path.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files to check")
        
        for file_path in python_files:
            self.fix_file(file_path)
            
        result = {
            'total_files': len(python_files),
            'fixed_files': len(self.fixed_files),
            'failed_files': len(self.failed_files),
            'fixed_file_list': self.fixed_files,
            'failed_file_list': self.failed_files
        }
        
        logger.info(f"TYPE_CHECKING fixes complete:")
        logger.info(f"  - Total files checked: {result['total_files']}")
        logger.info(f"  - Files fixed: {result['fixed_files']}")
        logger.info(f"  - Files failed: {result['failed_files']}")
        
        return result

def main():
    """Main execution function."""
    backend_path = "backend/systems"
    
    if not os.path.exists(backend_path):
        logger.error(f"Backend path not found: {backend_path}")
        return 1
        
    fixer = TypeCheckingFixer(backend_path)
    result = fixer.fix_all_files()
    
    return 0 if result['failed_files'] == 0 else 1

if __name__ == "__main__":
    exit(main()) 