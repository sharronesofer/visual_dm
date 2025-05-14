#!/usr/bin/env python3
"""
World Generation TypeScript to Python Fixer

This script improves the automatically converted TypeScript files
for the World Generation System by applying Python best practices
and fixing common conversion issues.
"""

import os
import re
import sys
import glob
import shutil
from typing import List, Dict, Any, Optional

# Base directory for Python converted files
PYTHON_DIR = "python_converted/src/worldgen"

# Conversion rules and patterns
TS_TO_PY_RULES = [
    # TypeScript interfaces to Python classes/protocols
    (r'interface\s+(\w+)\s*{([^}]+)}', r'class \1:\n\2'),
    
    # Constructor conversion
    (r'constructor\(([^)]*)\)\s*{([^}]*)}', r'def __init__(self, \1):\2'),
    
    # Method conversion
    (r'(public|private)\s+(\w+)\((.*?)\):\s*([^{]+){([^}]*)}', r'def \2(self, \3) -> \4:\5'),
    
    # Arrow function conversion
    (r'const\s+(\w+)\s*=\s*\((.*?)\)\s*=>\s*{([^}]*)}', r'def \1(\2):\3'),
    
    # Variable declaration conversion
    (r'(const|let|var)\s+(\w+)(\:\s*[^=]+)?\s*=\s*([^;]+);', r'\2 = \4'),
    
    # Type conversion
    (r'(\w+):\s*string', r'\1: str'),
    (r'(\w+):\s*number', r'\1: float'),
    (r'(\w+):\s*boolean', r'\1: bool'),
    (r'(\w+):\s*any', r'\1: Any'),
    (r'Array<([^>]+)>', r'List[\1]'),
    (r'(\w+)\[\]', r'List[\1]'),
    (r'Record<([^,]+),\s*([^>]+)>', r'Dict[\1, \2]'),
    (r'Map<([^,]+),\s*([^>]+)>', r'Dict[\1, \2]'),
    
    # Export removal
    (r'export\s+', r''),
    
    # this. to self.
    (r'this\.', r'self.'),
    
    # forEach to for loop
    (r'(\w+)\.forEach\((.*?)\s*=>\s*{([^}]*)}', r'for \2 in \1:\3'),
    
    # map to list comprehension (simplified)
    (r'(\w+)\.map\((.*?)\s*=>\s*([^}]+)\)', r'[\3 for \2 in \1]'),
    
    # filter to list comprehension (simplified)
    (r'(\w+)\.filter\((.*?)\s*=>\s*([^}]+)\)', r'[\2 for \2 in \1 if \3]'),
    
    # Semicolon removal
    (r';', r''),
    
    # Boolean literals
    (r'\btrue\b', r'True'),
    (r'\bfalse\b', r'False'),
    
    # null/undefined to None
    (r'\bnull\b', r'None'),
    (r'\bundefined\b', r'None'),
    
    # import conversion (simplified)
    (r'import\s*{([^}]+)}\s*from\s*[\'"]([^\'"]+)[\'"]', r'from \2 import \1'),
]

# Python header for all files
PYTHON_HEADER = """#!/usr/bin/env python3
\"\"\"
{filename} - {description}

This file was auto-converted from TypeScript to Python.
\"\"\"

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
"""

# File descriptions for headers
FILE_DESCRIPTIONS = {
    "IWorldGenerator.py": "Interfaces and contracts for world generation",
    "DeterministicRNG.py": "Deterministic random number generator implementation", 
    "GeneratorRegistry.py": "Registry system for world generators",
    "GenerationPipeline.py": "Pipeline framework for generation steps",
    "BaseRegionGenerator.py": "Abstract base class for region generators",
    "ProceduralRegionGenerator.py": "Procedural terrain generation implementation",
    "HandcraftedRegionGenerator.py": "Template-based region generation",
    "RegionGeneratorFactory.py": "Factory for creating region generators",
    "RegionGeneratorInterfaces.py": "Additional region generator interfaces",
    "RegionValidationRules.py": "Validation rules for region data",
    "RegionValidator.py": "Validation system for regions",
}

def fix_imports(content: str, filename: str) -> str:
    """Add appropriate imports based on file content"""
    needs_import = []
    
    # Check for common patterns that need imports
    if "Enum" in content or "enum" in content:
        needs_import.append("from enum import Enum")
    
    if "json" in content:
        needs_import.append("import json")
    
    if "math" in content or "Math." in content:
        needs_import.append("import math")
    
    if "random" in content:
        needs_import.append("import random")
    
    if "@abstractmethod" in content or "ABC" in content:
        needs_import.append("from abc import ABC, abstractmethod")
    
    # Add TypeVar if needed
    if "List[" in content or "Dict[" in content:
        if "TypeVar" not in content:
            needs_import.append("T = TypeVar('T')")
            needs_import.append("U = TypeVar('U')")
    
    # Special imports for specific files
    if "DeterministicRNG" in filename:
        needs_import.append("import math")
        needs_import.append("from .IWorldGenerator import IRandomGenerator")
    
    if "BaseRegionGenerator" in filename:
        needs_import.append("from .IWorldGenerator import IRegionGenerator, GeneratorType, Region, RegionGeneratorOptions, GenerationResult")
    
    if "GeneratorRegistry" in filename:
        needs_import.append("from .IWorldGenerator import IGeneratorRegistry, IRegionGenerator")
    
    # Add imports to content
    import_block = "\n".join(needs_import)
    if import_block:
        # Find where imports should go (after existing imports or after header)
        import_pos = content.find("\n\n", content.find("from typing"))
        if import_pos == -1:
            import_pos = content.find("\n\n", content.find("\"\"\""))
        
        if import_pos != -1:
            return content[:import_pos] + "\n" + import_block + content[import_pos:]
    
    return content

def fix_ts_file(file_path: str, dry_run: bool = False) -> Optional[str]:
    """Fix a single file converted from TypeScript to Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get base filename
        filename = os.path.basename(file_path)
        
        # Skip if not a .py file
        if not filename.endswith('.py'):
            return None
        
        # Add Python header if not present
        if not content.startswith('#!/usr/bin/env python3'):
            description = FILE_DESCRIPTIONS.get(filename, "Part of the World Generation System")
            content = PYTHON_HEADER.format(
                filename=filename,
                description=description
            ) + content
        
        # Apply all conversion rules
        for pattern, replacement in TS_TO_PY_RULES:
            content = re.sub(pattern, replacement, content)
        
        # Fix JavaScript method names to Python style
        content = re.sub(r'\.forEach\(', '.for_each(', content)
        content = re.sub(r'\.map\(', '.map(', content)
        content = re.sub(r'\.filter\(', '.filter(', content)
        content = re.sub(r'\.reduce\(', '.reduce(', content)
        content = re.sub(r'\.push\(', '.append(', content)
        content = re.sub(r'\.length', '.length()', content)
        
        # Fix camelCase to snake_case for functions and variables
        def snake_case_replacer(match):
            name = match.group(1)
            # Don't convert class names
            if name[0].isupper():
                return match.group(0)
            # Convert to snake_case
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        
        content = re.sub(r'def\s+([a-zA-Z0-9]+)', lambda m: 'def ' + snake_case_replacer(m), content)
        
        # Fix imports
        content = fix_imports(content, filename)
        
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return content
    except Exception as e:
        print(f"Error fixing file {file_path}: {e}")
        return None

def fix_worldgen_files(python_dir: str = PYTHON_DIR, dry_run: bool = False) -> Dict[str, Any]:
    """Fix all Python files converted from TypeScript in the World Generation system"""
    results = {
        "success": [],
        "failed": [],
        "skipped": []
    }
    
    # Find all Python files in the directory
    for root, _, files in os.walk(python_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}...")
                
                result = fix_ts_file(file_path, dry_run)
                if result is not None:
                    results["success"].append(file_path)
                else:
                    results["failed"].append(file_path)
    
    return results

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix Python files converted from TypeScript for the World Generation System"
    )
    parser.add_argument('--dry-run', action='store_true', 
                        help="Don't modify files, just print what would be done")
    parser.add_argument('--dir', type=str, default=PYTHON_DIR,
                        help=f"Directory containing Python files (default: {PYTHON_DIR})")
    
    args = parser.parse_args()
    
    print(f"Fixing World Generation Python files in {args.dir}...")
    results = fix_worldgen_files(args.dir, args.dry_run)
    
    print(f"\nResults:")
    print(f"  Success: {len(results['success'])}")
    print(f"  Failed: {len(results['failed'])}")
    
    if results['failed']:
        print("\nFailed files:")
        for file in results['failed']:
            print(f"  - {file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 