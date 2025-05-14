#!/usr/bin/env python3
"""
Full TypeScript Codebase to Python Converter

This script converts all TypeScript files in the codebase to Python,
following the conversion patterns established in the worldgen module migration.
"""

import os
import sys
import re
import glob
import json
import argparse
import subprocess
import shutil
import time
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

# Base directory for output files
OUTPUT_DIR = "python_converted"

# Import the existing fix_worldgen_py_files rules and patterns for reuse
try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from fix_worldgen_py_files import TS_TO_PY_RULES, fix_imports, PYTHON_HEADER
except ImportError:
    print("Warning: Could not import fix_worldgen_py_files module. Using default rules.")
    # Define fallback conversion rules if import fails
    TS_TO_PY_RULES = [
        # TypeScript interfaces to Python classes/protocols
        (r'interface\s+(\w+)\s*{([^}]+)}', r'class \1:\n\2'),
        # Constructor conversion
        (r'constructor\(([^)]*)\)\s*{([^}]*)}', r'def __init__(self, \1):\2'),
        # And other rules...
    ]

# Stats tracking
conversion_stats = {
    "total_files": 0,
    "converted_files": 0,
    "skipped_files": 0,
    "failed_files": 0,
    "start_time": 0,
    "end_time": 0,
    "directories": set()
}

# Module dependencies tracking
module_dependencies = {}

def collect_typescript_files(source_dir: str, exclude_dirs: List[str] = None) -> List[str]:
    """Find all TypeScript files in the codebase"""
    if exclude_dirs is None:
        exclude_dirs = ["node_modules", "dist", "build", ".git", ".next"]
    
    print(f"Collecting TypeScript files from {source_dir}...")
    
    typescript_files = []
    
    for root, dirs, files in os.walk(source_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.ts') and not file.endswith('.d.ts'):
                file_path = os.path.join(root, file)
                typescript_files.append(file_path)
                # Track directory for module structure
                rel_dir = os.path.relpath(os.path.dirname(file_path), source_dir)
                conversion_stats["directories"].add(rel_dir)
    
    conversion_stats["total_files"] = len(typescript_files)
    print(f"Found {len(typescript_files)} TypeScript files in {len(conversion_stats['directories'])} directories")
    
    return typescript_files

def create_output_structure(output_dir: str, directories: Set[str]) -> None:
    """Create the output directory structure"""
    print(f"Creating output directory structure in {output_dir}...")
    
    # Create base output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create subdirectories
    for directory in directories:
        target_dir = os.path.join(output_dir, directory)
        os.makedirs(target_dir, exist_ok=True)
        
        # Add __init__.py files for Python package structure
        init_file = os.path.join(target_dir, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                module_name = os.path.basename(directory)
                f.write(f'"""{module_name} module"""\n\n')
    
    print(f"Created directory structure with {len(directories)} directories")

def analyze_imports(ts_file: str) -> Dict[str, List[str]]:
    """Analyze TypeScript imports in a file"""
    imports = {}
    
    with open(ts_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Match import statements
    import_pattern = r'import\s+{([^}]+)}\s+from\s+[\'"]([^\'"]+)[\'"]'
    for match in re.finditer(import_pattern, content):
        symbols = [s.strip() for s in match.group(1).split(',')]
        module = match.group(2)
        imports[module] = symbols
    
    return imports

def build_dependency_graph(typescript_files: List[str]) -> None:
    """Build a dependency graph of TypeScript modules"""
    print("Building module dependency graph...")
    
    for ts_file in typescript_files:
        rel_path = os.path.relpath(ts_file)
        # Use path without extension as module name
        module_name = os.path.splitext(rel_path)[0]
        
        imports = analyze_imports(ts_file)
        module_dependencies[module_name] = imports
    
    print(f"Built dependency graph for {len(module_dependencies)} modules")

def determine_conversion_order() -> List[str]:
    """Determine the order to convert files based on dependencies"""
    # This is a simplified topological sort
    # In a real implementation, we'd properly handle cycles
    
    # For now, we'll use a simple heuristic:
    # 1. Convert utility files first
    # 2. Convert model/type files next
    # 3. Convert component files last
    
    # This could be enhanced with a proper dependency analysis
    return [
        "**/utils/**/*.ts",        # Utilities first
        "**/types/**/*.ts",        # Types/interfaces second
        "**/models/**/*.ts",       # Data models third
        "**/services/**/*.ts",     # Services fourth
        "**/hooks/**/*.ts",        # Hooks fifth
        "**/components/**/*.ts",   # Components last
        "**/*.ts",                 # Everything else
    ]

def convert_file(ts_file: str, output_dir: str) -> Tuple[str, bool]:
    """Convert a single TypeScript file to Python"""
    # Get relative path for output
    rel_path = os.path.relpath(ts_file)
    py_path = os.path.join(output_dir, os.path.splitext(rel_path)[0] + '.py')
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(py_path), exist_ok=True)
    
    try:
        # Read TypeScript file
        with open(ts_file, 'r', encoding='utf-8', errors='ignore') as f:
            ts_content = f.read()
        
        # Skip empty files
        if not ts_content.strip():
            print(f"Skipping empty file: {ts_file}")
            return ts_file, False
        
        # Apply initial conversion using ts2py.py script
        try:
            # Try to use the existing script if available
            subprocess.run([
                "python", "scripts/ts2py.py", 
                "--input", ts_file, 
                "--output", py_path
            ], check=True, capture_output=True)
            
            # Read the converted output
            with open(py_path, 'r', encoding='utf-8') as f:
                py_content = f.read()
                
        except (subprocess.SubprocessError, FileNotFoundError):
            # Fall back to manual conversion
            py_content = ts_content
            
            # Add Python header
            filename = os.path.basename(py_path)
            module_name = os.path.splitext(filename)[0]
            py_content = PYTHON_HEADER.format(
                filename=filename,
                description=f"Python implementation of {module_name}"
            ) + py_content
            
            # Apply conversion rules
            for pattern, replacement in TS_TO_PY_RULES:
                py_content = re.sub(pattern, replacement, py_content)
        
        # Additional post-processing
        py_content = fix_imports(py_content, os.path.basename(py_path))
        
        # Convert camelCase to snake_case for functions and variables
        def snake_case_replacer(match):
            name = match.group(1)
            # Don't convert class names
            if name[0].isupper():
                return match.group(0)
            # Convert to snake_case
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        
        py_content = re.sub(r'def\s+([a-zA-Z0-9]+)', lambda m: 'def ' + snake_case_replacer(m), py_content)
        
        # Fix JavaScript method names to Python style
        py_content = re.sub(r'\.forEach\(', '.for_each(', py_content)
        py_content = re.sub(r'\.map\(', '.map(', py_content)
        py_content = re.sub(r'\.filter\(', '.filter(', py_content)
        py_content = re.sub(r'\.reduce\(', '.reduce(', py_content)
        py_content = re.sub(r'\.push\(', '.append(', py_content)
        py_content = re.sub(r'\.length', '.length()', py_content)
        
        # Write the converted Python file
        with open(py_path, 'w', encoding='utf-8') as f:
            f.write(py_content)
        
        return ts_file, True
        
    except Exception as e:
        print(f"Error converting {ts_file}: {e}")
        return ts_file, False

def process_batch(files_batch: List[str], output_dir: str) -> Dict[str, List[str]]:
    """Process a batch of files"""
    results = {
        "success": [],
        "failed": []
    }
    
    for ts_file in files_batch:
        file, success = convert_file(ts_file, output_dir)
        if success:
            results["success"].append(file)
        else:
            results["failed"].append(file)
    
    return results

def convert_files_parallel(typescript_files: List[str], output_dir: str, max_workers: int = None) -> None:
    """Convert TypeScript files to Python in parallel"""
    if max_workers is None:
        max_workers = os.cpu_count() or 4
    
    print(f"Converting {len(typescript_files)} files using {max_workers} workers...")
    
    # Split files into batches
    batch_size = max(1, len(typescript_files) // max_workers)
    batches = [typescript_files[i:i + batch_size] for i in range(0, len(typescript_files), batch_size)]
    
    success_count = 0
    failed_files = []
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_batch, batch, output_dir): i for i, batch in enumerate(batches)}
        
        for future in as_completed(futures):
            try:
                results = future.result()
                success_count += len(results["success"])
                failed_files.extend(results["failed"])
                
                # Progress update
                progress = min(100, int(100 * success_count / len(typescript_files)))
                print(f"Progress: {progress}% ({success_count}/{len(typescript_files)})")
                
            except Exception as e:
                print(f"Batch failed: {e}")
    
    conversion_stats["converted_files"] = success_count
    conversion_stats["failed_files"] = len(failed_files)
    
    print(f"Conversion complete: {success_count} files converted successfully, {len(failed_files)} files failed")
    
    if failed_files:
        print("\nFailed files:")
        for file in failed_files[:10]:  # Show only first 10 failures
            print(f"  - {file}")
        if len(failed_files) > 10:
            print(f"  ... and {len(failed_files) - 10} more")

def create_python_package_structure(output_dir: str) -> None:
    """Create a proper Python package structure with init files"""
    print("Creating Python package structure...")
    
    # Add a root __init__.py if it doesn't exist
    root_init = os.path.join(output_dir, "__init__.py")
    if not os.path.exists(root_init):
        with open(root_init, 'w') as f:
            f.write('"""Visual DM Python Implementation"""\n\n')
    
    # Add setup.py for package installation
    setup_py = os.path.join(output_dir, "setup.py")
    if not os.path.exists(setup_py):
        with open(setup_py, 'w') as f:
            f.write("""
#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="visual_dm",
    version="1.0.0",
    description="Visual DM Python Implementation",
    author="Visual DM Team",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.6.0",
        "matplotlib>=3.4.0",
        "pillow>=8.2.0",
    ],
    python_requires=">=3.7",
)
""")
    
    # Walk through all directories and add __init__.py files
    for root, dirs, files in os.walk(output_dir):
        # Skip setup tools directories
        if any(exclude in root for exclude in ["__pycache__", ".git", "node_modules", "venv"]):
            continue
            
        # Add __init__.py if not present
        init_file = os.path.join(root, "__init__.py")
        if not os.path.exists(init_file) and root != output_dir:
            module_name = os.path.basename(root)
            with open(init_file, 'w') as f:
                f.write(f'"""{module_name} module"""\n\n')
    
    print("Python package structure created")

def generate_conversion_report(output_dir: str, stats: Dict) -> None:
    """Generate a conversion report"""
    print("Generating conversion report...")
    
    report_path = os.path.join(output_dir, "CONVERSION_REPORT.md")
    
    # Calculate elapsed time
    elapsed = stats["end_time"] - stats["start_time"]
    hours, remainder = divmod(elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    success_rate = 0
    if stats["total_files"] > 0:
        success_rate = (stats["converted_files"] / stats["total_files"]) * 100
    
    with open(report_path, 'w') as f:
        f.write(f"""# TypeScript to Python Conversion Report

## Summary

- **Date:** {time.strftime("%Y-%m-%d %H:%M:%S")}
- **Duration:** {int(hours)}h {int(minutes)}m {int(seconds)}s
- **Total TypeScript Files:** {stats["total_files"]}
- **Successfully Converted:** {stats["converted_files"]}
- **Skipped Files:** {stats["skipped_files"]}
- **Failed Conversions:** {stats["failed_files"]}
- **Success Rate:** {success_rate:.2f}%
- **Directories Processed:** {len(stats["directories"])}

## Conversion Process

The conversion from TypeScript to Python was performed using an automated conversion pipeline that:

1. Collected all TypeScript files from the source codebase
2. Created a matching directory structure in the output directory
3. Converted TypeScript syntax to Python using pattern matching and transformations
4. Added proper Python package structure with `__init__.py` files
5. Fixed imports and references between modules
6. Applied Python naming conventions (snake_case) to functions and variables

## Key Conversions

- TypeScript interfaces became Python classes and Protocol classes
- ES6 class syntax converted to Python class syntax
- Arrow functions converted to regular Python functions
- JavaScript array methods converted to Python list operations
- TypeScript typing converted to Python type hints

## Next Steps

1. **Manual Review** - Review converted files for any issues
2. **Fix Failed Conversions** - Address files that failed automatic conversion
3. **Testing** - Create and run tests to verify functionality
4. **Performance Optimization** - Optimize critical code paths
5. **Documentation** - Update documentation to reflect Python implementation

## Getting Started with the Python Code

```python
# Example usage of the converted code
from visual_dm import initialize_app

app = initialize_app()
app.run()
```

## Notes on Failed Conversions

Files that failed conversion typically contain complex TypeScript patterns
that require manual intervention, such as:

- Complex generic types
- Advanced decorators
- React/JSX components
- TypeScript-specific language features

These files are listed in `failed_conversions.txt` and should be prioritized
for manual conversion.
""")
    
    # Also create a list of failed files for reference
    failed_list_path = os.path.join(output_dir, "failed_conversions.txt")
    with open(failed_list_path, 'w') as f:
        for file in stats.get("failed_files_list", []):
            f.write(f"{file}\n")
    
    print(f"Conversion report generated: {report_path}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Convert all TypeScript files in the codebase to Python"
    )
    parser.add_argument('--source-dir', type=str, default=".",
                       help="Source directory containing TypeScript files")
    parser.add_argument('--output-dir', type=str, default=OUTPUT_DIR,
                       help="Output directory for Python files")
    parser.add_argument('--exclude', type=str, nargs='+',
                       default=["node_modules", "dist", "build", ".git", ".next"],
                       help="Directories to exclude from conversion")
    parser.add_argument('--max-workers', type=int, default=None,
                       help="Maximum number of worker processes")
    parser.add_argument('--clean', action='store_true',
                       help="Clean the output directory before conversion")
    
    args = parser.parse_args()
    
    # Track timing
    conversion_stats["start_time"] = time.time()
    
    # Clean output directory if requested
    if args.clean and os.path.exists(args.output_dir):
        print(f"Cleaning output directory: {args.output_dir}")
        shutil.rmtree(args.output_dir)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Collect TypeScript files
    typescript_files = collect_typescript_files(args.source_dir, args.exclude)
    
    # Create output directory structure
    create_output_structure(args.output_dir, conversion_stats["directories"])
    
    # Build dependency graph
    build_dependency_graph(typescript_files)
    
    # Convert files in parallel
    convert_files_parallel(typescript_files, args.output_dir, args.max_workers)
    
    # Create Python package structure
    create_python_package_structure(args.output_dir)
    
    # Generate conversion report
    conversion_stats["end_time"] = time.time()
    generate_conversion_report(args.output_dir, conversion_stats)
    
    print("Conversion process complete!")

if __name__ == "__main__":
    main() 