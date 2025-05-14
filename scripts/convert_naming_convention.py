#!/usr/bin/env python3
"""
Name Convention Converter

This script helps convert camelCase names to snake_case in Python files.
It's part of the TypeScript to Python migration toolkit.

Usage:
  python convert_naming_convention.py --dir <directory> [options]
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Any

class NamingConventionConverter:
    """Converts camelCase names to snake_case in Python files."""
    
    def __init__(self, directory: str, dry_run: bool = False, 
                exclude_patterns: List[str] = None, verbose: bool = False):
        """
        Initialize the converter.
        
        Args:
            directory: Directory to process
            dry_run: If True, don't actually make changes
            exclude_patterns: List of glob patterns to exclude
            verbose: If True, print detailed information
        """
        self.directory = directory
        self.dry_run = dry_run
        self.exclude_patterns = exclude_patterns or ['**/node_modules/**', '**/.git/**', '**/venv/**']
        self.verbose = verbose
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'names_converted': 0,
            'skipped_files': 0
        }
        # Dictionary to track name conversions for consistency
        self.conversion_map = {}
        # Set of Python keywords to avoid
        self.python_keywords = {
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 
            'except', 'finally', 'for', 'from', 'global', 'if', 'import', 
            'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 
            'return', 'try', 'while', 'with', 'yield'
        }
    
    def camel_to_snake(self, name: str) -> str:
        """
        Convert camelCase to snake_case.
        
        Args:
            name: The camelCase name to convert
            
        Returns:
            The snake_case version of the name
        """
        # Check if we've already converted this name
        if name in self.conversion_map:
            return self.conversion_map[name]
            
        # Handle empty strings
        if not name:
            return name
            
        # Don't convert if it's already snake_case or ALL_CAPS
        if '_' in name and not (name.isupper() or any(c.isupper() for c in name.split('_')[0])):
            return name
        
        # Special case for names that start with capital letters (likely class names)
        # We don't want to convert those as they should remain CamelCase
        if name[0].isupper() and any(c.islower() for c in name):
            return name
            
        # Convert the name
        snake_name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        
        # Add underscore if the name is a Python keyword
        if snake_name in self.python_keywords:
            snake_name += '_'
            
        # Store the conversion for consistency
        self.conversion_map[name] = snake_name
        return snake_name
    
    def process_file(self, file_path: Path) -> Tuple[int, bool]:
        """
        Process a single file.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Tuple of (number of names converted, whether file was modified)
        """
        # Skip files that match exclude patterns
        for pattern in self.exclude_patterns:
            if Path(file_path).match(pattern):
                if self.verbose:
                    print(f"Skipping excluded file: {file_path}")
                return 0, False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            if self.verbose:
                print(f"Skipping binary file: {file_path}")
            self.stats['skipped_files'] += 1
            return 0, False
            
        # Skip if file doesn't look like Python
        if not file_path.suffix == '.py':
            if self.verbose:
                print(f"Skipping non-Python file: {file_path}")
            self.stats['skipped_files'] += 1
            return 0, False
            
        original_content = content
        names_converted = 0
        
        # Find variable and function names
        # Look for variable assignments: name = value
        var_pattern = r'\b([a-zA-Z][a-zA-Z0-9]*)(?=\s*=\s*)'
        # Look for function definitions: def name(
        func_pattern = r'def\s+([a-zA-Z][a-zA-Z0-9]*)(?=\s*\()'
        # Look for method parameters: def func(param1, param2)
        param_pattern = r'def\s+[a-zA-Z][a-zA-Z0-9]*\s*\(\s*(?:[a-zA-Z][a-zA-Z0-9]*\s*,\s*)*([a-zA-Z][a-zA-Z0-9]*)(?=\s*(?:,|\)))'
        # Look for function/method calls: func(
        call_pattern = r'\b([a-zA-Z][a-zA-Z0-9]*)(?=\s*\()'
        
        # Find and replace variable names
        for pattern in [var_pattern, func_pattern, param_pattern, call_pattern]:
            matches = re.finditer(pattern, content)
            for match in matches:
                name = match.group(1)
                snake_name = self.camel_to_snake(name)
                
                # Skip if name is already snake_case or doesn't need conversion
                if name == snake_name:
                    continue
                    
                # Replace the name
                content = content.replace(f"{name}(", f"{snake_name}(")
                content = re.sub(r'\b' + re.escape(name) + r'\b', snake_name, content)
                names_converted += 1
        
        # Only write the file if changes were made and not in dry-run mode
        if content != original_content:
            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            return names_converted, True
        
        return 0, False
    
    def process_directory(self) -> Dict[str, int]:
        """
        Process all Python files in the directory.
        
        Returns:
            Statistics dictionary
        """
        directory_path = Path(self.directory)
        
        if not directory_path.exists():
            print(f"Error: Directory {self.directory} does not exist.")
            return self.stats
            
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = Path(root) / file
                
                # Skip files that match exclude patterns
                skip = False
                for pattern in self.exclude_patterns:
                    if file_path.match(pattern):
                        skip = True
                        break
                        
                if skip:
                    continue
                    
                self.stats['files_processed'] += 1
                names_converted, file_modified = self.process_file(file_path)
                
                if names_converted > 0:
                    self.stats['names_converted'] += names_converted
                    if file_modified:
                        self.stats['files_modified'] += 1
                        if self.verbose:
                            print(f"Modified {file_path}: {names_converted} names converted")
        
        return self.stats
        
    def print_stats(self):
        """Print statistics about the conversion process."""
        print("\nName Convention Conversion Statistics:")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Files modified: {self.stats['files_modified']}")
        print(f"Names converted: {self.stats['names_converted']}")
        print(f"Files skipped: {self.stats['skipped_files']}")
        
        if self.dry_run:
            print("\nThis was a dry run. No files were actually modified.")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Convert camelCase names to snake_case in Python files'
    )
    parser.add_argument(
        '--dir', 
        required=True, 
        help='Directory to process'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true', 
        help="Don't actually make changes"
    )
    parser.add_argument(
        '--exclude', 
        nargs='+', 
        default=['**/node_modules/**', '**/.git/**', '**/venv/**'],
        help='Glob patterns to exclude'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true', 
        help='Print detailed information'
    )
    
    args = parser.parse_args()
    
    converter = NamingConventionConverter(
        directory=args.dir,
        dry_run=args.dry_run,
        exclude_patterns=args.exclude,
        verbose=args.verbose
    )
    
    converter.process_directory()
    converter.print_stats()

if __name__ == '__main__':
    main() 