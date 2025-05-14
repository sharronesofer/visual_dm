#!/usr/bin/env python3

import os
import re
import sys
import glob
import argparse
import logging
from typing import List, Optional, Set, Dict
import importlib.util
import ast
import autopep8

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('fix_python')

# Common issues to fix
class PythonFixer:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
    
    def fix_file(self, file_path: str) -> None:
        """Apply all fixes to a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply fixes
            fixed_content = self.fix_content(content)
            
            # Format with autopep8
            fixed_content = autopep8.fix_code(fixed_content, options={'max_line_length': 100})
            
            if self.dry_run:
                logger.info(f"Would fix: {file_path}")
                return
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            logger.info(f"Fixed: {file_path}")
        except Exception as e:
            logger.error(f"Error fixing {file_path}: {str(e)}")
    
    def fix_content(self, content: str) -> str:
        """Apply all fixes to the content."""
        # Fix imports
        content = self.fix_imports(content)
        
        # Fix variable names (camelCase to snake_case)
        content = self.fix_variable_names(content)
        
        # Fix function calls
        content = self.fix_function_calls(content)
        
        # Fix common syntax issues
        content = self.fix_syntax(content)
        
        # Fix boolean values
        content = self.fix_booleans(content)
        
        # Fix class definitions
        content = self.fix_classes(content)
        
        # Fix string formatting
        content = self.fix_string_formatting(content)
        
        return content
    
    def fix_imports(self, content: str) -> str:
        """Fix import statements."""
        # Remove duplicate imports
        import_lines = []
        seen_imports = set()
        
        for line in content.split('\n'):
            if line.startswith('import ') or line.startswith('from '):
                if line not in seen_imports:
                    import_lines.append(line)
                    seen_imports.add(line)
            else:
                import_lines.append(line)
        
        content = '\n'.join(import_lines)
        
        # Group and sort imports
        try:
            import_block_pattern = r'((?:(?:import|from)\s+.+\n)+)'
            import_blocks = re.findall(import_block_pattern, content)
            
            for block in import_blocks:
                sorted_imports = sorted(block.strip().split('\n'))
                content = content.replace(block, '\n'.join(sorted_imports) + '\n\n')
        except Exception as e:
            logger.warning(f"Error sorting imports: {str(e)}")
        
        return content
    
    def fix_variable_names(self, content: str) -> str:
        """Convert camelCase variable names to snake_case."""
        def camel_to_snake(match):
            name = match.group(1)
            if name.startswith('__'):
                # Special methods, don't convert
                return match.group(0)
            
            # Don't convert if it's imported or a class name
            if re.search(rf'(?:from|import)\s+\w+\s+\w+\s+{name}', content) or name[0].isupper():
                return match.group(0)
            
            # Convert camelCase to snake_case
            snake_name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
            return match.group(0).replace(name, snake_name)
        
        # Match variable definitions and method/function definitions
        var_pattern = r'((?:self\.)?[a-zA-Z_][a-zA-Z0-9_]*)\s*='
        func_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        
        content = re.sub(var_pattern, camel_to_snake, content)
        content = re.sub(func_pattern, camel_to_snake, content)
        
        return content
    
    def fix_function_calls(self, content: str) -> str:
        """Fix function calls with JS-style method chaining."""
        # Replace .then() with await
        then_pattern = r'\.then\(\s*([^)]+)\s*\)'
        content = re.sub(then_pattern, lambda m: f"\nawait {m.group(1)}", content)
        
        # Replace .catch() with try/except
        catch_pattern = r'\.catch\(\s*([^)]+)\s*\)'
        
        def catch_replacer(match):
            handler = match.group(1)
            return f"""
try:
    # Previous operation
except Exception as e:
    {handler}(e)
"""
        
        content = re.sub(catch_pattern, catch_replacer, content)
        
        return content
    
    def fix_syntax(self, content: str) -> str:
        """Fix common syntax issues."""
        # Fix triple-equal comparisons
        content = re.sub(r'===', '==', content)
        content = re.sub(r'!==', '!=', content)
        
        # Fix increment/decrement operators
        content = re.sub(r'(\w+)\+\+', r'\1 += 1', content)
        content = re.sub(r'(\w+)--', r'\1 -= 1', content)
        
        # Fix null/undefined comparisons
        content = re.sub(r'([^=!<>])(null|undefined)', r'\1None', content)
        
        # Fix return statements
        content = re.sub(r'return\s*;', 'return None', content)
        
        # Fix array destructuring
        destructure_pattern = r'const\s+\[\s*([^]]+)\s*\]\s*=\s*([^;]+)'
        
        def destructure_replacer(match):
            variables = [v.strip() for v in match.group(1).split(',')]
            array = match.group(2)
            
            if len(variables) <= 3:
                return f"{', '.join(variables)} = {array}"
            else:
                lines = []
                for i, var in enumerate(variables):
                    lines.append(f"{var} = {array}[{i}]")
                return '\n'.join(lines)
        
        content = re.sub(destructure_pattern, destructure_replacer, content)
        
        # Fix object destructuring
        obj_destructure_pattern = r'const\s+{\s*([^}]+)\s*}\s*=\s*([^;]+)'
        
        def obj_destructure_replacer(match):
            properties = [p.strip() for p in match.group(1).split(',')]
            obj = match.group(2)
            
            lines = []
            for prop in properties:
                # Handle renaming: { oldName: newName }
                if ':' in prop:
                    old_name, new_name = [p.strip() for p in prop.split(':')]
                    lines.append(f"{new_name} = {obj}['{old_name}']")
                else:
                    lines.append(f"{prop} = {obj}['{prop}']")
            
            return '\n'.join(lines)
        
        content = re.sub(obj_destructure_pattern, obj_destructure_replacer, content)
        
        return content
    
    def fix_booleans(self, content: str) -> str:
        """Fix boolean values."""
        content = re.sub(r'\btrue\b', 'True', content)
        content = re.sub(r'\bfalse\b', 'False', content)
        
        return content
    
    def fix_classes(self, content: str) -> str:
        """Fix class definitions."""
        # Add docstrings to classes
        class_pattern = r'class\s+(\w+)(?:\([^)]*\))?:\s*(?:"""[^"]*""")?'
        
        def class_replacer(match):
            class_name = match.group(1)
            if '"""' in match.group(0):
                # Already has a docstring
                return match.group(0)
            
            return f'class {class_name}:\n    """Class representing {class_name}."""'
        
        content = re.sub(class_pattern, class_replacer, content)
        
        return content
    
    def fix_string_formatting(self, content: str) -> str:
        """Fix string formatting."""
        # Convert template literals to f-strings
        template_pattern = r'"([^"]*)\{([^}]+)\}([^"]*)"'
        content = re.sub(template_pattern, r'f"\1{\2}\3"', content)
        
        return content

def find_python_files(directory: str, recursive: bool = True) -> List[str]:
    """Find all Python files in the directory."""
    if recursive:
        pattern = os.path.join(directory, '**', '*.py')
        files = glob.glob(pattern, recursive=True)
    else:
        pattern = os.path.join(directory, '*.py')
        files = glob.glob(pattern)
    
    return files

def main():
    parser = argparse.ArgumentParser(description='Fix common issues in converted Python files')
    parser.add_argument('directory', help='Directory containing converted Python files')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Show files that would be fixed without making changes')
    parser.add_argument('--recursive', '-r', action='store_true', help='Process directories recursively')
    
    args = parser.parse_args()
    
    directory = args.directory
    if not os.path.isdir(directory):
        logger.error(f"Directory does not exist: {directory}")
        sys.exit(1)
    
    fixer = PythonFixer(dry_run=args.dry_run)
    
    # Find Python files
    files = find_python_files(directory, recursive=args.recursive)
    
    # Fix each file
    for file_path in files:
        fixer.fix_file(file_path)
    
    logger.info(f"Processed {len(files)} Python files")

if __name__ == '__main__':
    main() 