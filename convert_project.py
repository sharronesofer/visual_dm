#!/usr/bin/env python3

import os
import sys
import shutil
import argparse
import logging
import subprocess
import glob
from typing import List, Set, Dict, Tuple
from pathlib import Path
import concurrent.futures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('convert_project')

# File extensions to ignore when copying
IGNORE_EXTENSIONS = {
    '.ts', '.tsx', '.js', '.jsx', '.tsbuildinfo', '.map', '.log', '.lock'
}

# Directories to ignore when copying
IGNORE_DIRS = {
    'node_modules', 'dist', 'build', 'coverage', '.git', '.github', '.vscode', 
    '__tests__', '__mocks__'
}

def convert_typescript_file(ts_file: str, output_dir: str) -> str:
    """Convert a TypeScript file to Python and return the output path."""
    # Calculate the output path
    rel_path = os.path.relpath(ts_file, os.path.dirname(output_dir))
    output_path = os.path.join(output_dir, rel_path)
    output_path = output_path.replace('.ts', '.py').replace('.tsx', '.py')
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Convert the file using ts2py.py
    try:
        cmd = [sys.executable, 'ts2py.py', ts_file, '--output', output_path]
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"Converted: {ts_file} -> {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Error converting {ts_file}: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return ""

def copy_non_typescript_file(file_path: str, output_dir: str) -> None:
    """Copy a non-TypeScript file to the output directory, preserving directory structure."""
    # Calculate the output path
    rel_path = os.path.relpath(file_path, os.path.dirname(output_dir))
    output_path = os.path.join(output_dir, rel_path)
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Copy the file
    try:
        shutil.copy2(file_path, output_path)
        logger.info(f"Copied: {file_path} -> {output_path}")
    except Exception as e:
        logger.error(f"Error copying {file_path}: {str(e)}")

def should_ignore_file(file_path: str) -> bool:
    """Check if a file should be ignored."""
    # Check file extension
    _, ext = os.path.splitext(file_path)
    if ext.lower() in IGNORE_EXTENSIONS:
        return True
    
    # Check if file is in an ignored directory
    for ignore_dir in IGNORE_DIRS:
        if f"/{ignore_dir}/" in file_path or file_path.startswith(f"{ignore_dir}/"):
            return True
    
    return False

def find_typescript_files(directory: str) -> List[str]:
    """Find all TypeScript files in the directory recursively."""
    ts_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file.endswith('.ts') or file.endswith('.tsx'):
                file_path = os.path.join(root, file)
                ts_files.append(file_path)
    
    return ts_files

def find_non_typescript_files(directory: str) -> List[str]:
    """Find all non-TypeScript files that should be copied."""
    other_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip TypeScript files
            if file.endswith('.ts') or file.endswith('.tsx'):
                continue
            
            # Skip other ignored files
            if should_ignore_file(file_path):
                continue
            
            other_files.append(file_path)
    
    return other_files

def create_init_files(output_dir: str) -> None:
    """Create __init__.py files in Python packages."""
    for root, dirs, files in os.walk(output_dir):
        # Skip if this directory already has an __init__.py
        if '__init__.py' in files:
            continue
        
        # Only create __init__.py if there are Python files in this directory
        py_files = [f for f in files if f.endswith('.py')]
        if py_files:
            init_file = os.path.join(root, '__init__.py')
            with open(init_file, 'w', encoding='utf-8') as f:
                # Create a minimal package file
                package_name = os.path.basename(root)
                f.write(f'"""{package_name} package.\n\nAutomatically generated during TS to Python conversion.\n"""\n')
            logger.info(f"Created: {init_file}")

def fix_python_files(output_dir: str) -> None:
    """Fix common issues in converted Python files."""
    try:
        cmd = [sys.executable, 'fix_python_conversion.py', output_dir, '--recursive']
        subprocess.run(cmd, check=True)
        logger.info(f"Fixed Python files in {output_dir}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error fixing Python files: {e.stderr.decode() if e.stderr else 'Unknown error'}")

def update_imports(output_dir: str) -> None:
    """Update imports to relative imports in the Python converted files."""
    python_files = glob.glob(os.path.join(output_dir, '**', '*.py'), recursive=True)
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix import statements
            lines = content.split('\n')
            fixed_lines = []
            
            for line in lines:
                if line.startswith('from ') and ' import ' in line:
                    parts = line.split(' import ')
                    module = parts[0].replace('from ', '')
                    
                    # Skip already-relative imports and built-in imports
                    if module.startswith('.') or '.' not in module:
                        fixed_lines.append(line)
                        continue
                    
                    # Convert to relative import
                    rel_path = os.path.relpath(
                        os.path.join(output_dir, module.replace('.', '/')),
                        os.path.dirname(py_file)
                    )
                    
                    if rel_path == '.':
                        # Same directory
                        fixed_import = f"from . import {parts[1]}"
                    else:
                        # Create relative path
                        rel_module = '.' + rel_path.replace('/', '.')
                        fixed_import = f"from {rel_module} import {parts[1]}"
                    
                    fixed_lines.append(fixed_import)
                else:
                    fixed_lines.append(line)
            
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fixed_lines))
            
            logger.info(f"Updated imports in {py_file}")
        except Exception as e:
            logger.error(f"Error updating imports in {py_file}: {str(e)}")

def convert_npm_packages(output_dir: str) -> None:
    """Create/update requirements.txt file for Python dependencies."""
    # Map of common npm packages to Python equivalents
    npm_to_pip = {
        "react": "flask",  # Web framework replacement
        "next": "flask",
        "axios": "requests",
        "redux": "pydux",
        "react-redux": "pydux",
        "express": "flask",
        "lodash": "pydash",
        "moment": "python-dateutil",
        "uuid": "uuid",
        "jest": "pytest",
        "typescript": "mypy",
        "eslint": "pylint",
        "prettier": "black",
        "webpack": "",  # No direct equivalent
        "babel": "",  # No direct equivalent
        "firebase": "firebase-admin",
        "mongodb": "pymongo",
        "mongoose": "mongoengine",
        "pg": "psycopg2-binary",
        "sequelize": "sqlalchemy",
        "passport": "flask-login",
        "cors": "flask-cors",
        "socket.io": "flask-socketio",
        "dotenv": "python-dotenv",
        "winston": "logging",  # Python standard library
    }
    
    # Create a basic requirements file
    requirements_path = os.path.join(output_dir, 'requirements.txt')
    
    with open(requirements_path, 'w', encoding='utf-8') as f:
        f.write("# Python dependencies for converted TypeScript project\n")
        f.write("# Auto-generated equivalents of npm packages\n\n")
        
        # Add common Python packages
        f.write("# Web framework and utilities\n")
        f.write("flask>=2.3.3\n")
        f.write("flask-cors>=4.0.0\n")
        f.write("flask-socketio>=5.3.6\n")
        f.write("gunicorn>=21.2.0\n")
        f.write("\n# HTTP client\n")
        f.write("requests>=2.31.0\n")
        f.write("\n# Data processing\n")
        f.write("pydash>=7.0.6\n")
        f.write("python-dateutil>=2.8.2\n")
        f.write("\n# Database clients\n")
        f.write("sqlalchemy>=2.0.23\n")
        f.write("pymongo>=4.6.0\n")
        f.write("psycopg2-binary>=2.9.9\n")
        f.write("\n# Development tools\n")
        f.write("pytest>=7.4.3\n")
        f.write("mypy>=1.7.0\n")
        f.write("pylint>=3.0.2\n")
        f.write("black>=23.11.0\n")
        f.write("autopep8>=2.0.4\n")
        f.write("\n# Other utilities\n")
        f.write("python-dotenv>=1.0.0\n")
        f.write("uuid>=1.30\n")
        f.write("pyyaml>=6.0.1\n")
        
        # Check package.json if it exists
        package_json = os.path.join(os.path.dirname(output_dir), 'package.json')
        if os.path.exists(package_json):
            import json
            try:
                with open(package_json, 'r', encoding='utf-8') as pj:
                    package_data = json.load(pj)
                
                # Add dependencies from package.json
                all_deps = {}
                if 'dependencies' in package_data:
                    all_deps.update(package_data['dependencies'])
                if 'devDependencies' in package_data:
                    all_deps.update(package_data['devDependencies'])
                
                if all_deps:
                    f.write("\n# Additional dependencies from package.json\n")
                    for npm_pkg in all_deps:
                        # Remove version specifier (e.g., "^1.2.3")
                        pkg_name = npm_pkg.strip()
                        
                        # Get Python equivalent if available
                        pip_pkg = npm_to_pip.get(pkg_name, "")
                        if pip_pkg and pip_pkg not in ["flask", "pytest", "mypy", "pylint", "black"]:  # Skip already added
                            f.write(f"{pip_pkg}\n")
            except Exception as e:
                logger.error(f"Error parsing package.json: {str(e)}")
    
    logger.info(f"Created requirements.txt at {requirements_path}")

def create_readme(output_dir: str, src_dir: str) -> None:
    """Create a README file for the converted project."""
    readme_path = os.path.join(output_dir, 'README.md')
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("# Python Converted Project\n\n")
        f.write("This project has been automatically converted from TypeScript to Python.\n\n")
        f.write("## Project Structure\n\n")
        
        # List top-level directories
        f.write("### Directories\n\n")
        directories = []
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isdir(item_path) and not item.startswith('.') and item not in ['__pycache__']:
                directories.append(item)
        
        for directory in sorted(directories):
            f.write(f"- `{directory}/`: {directory.capitalize()} module\n")
        
        f.write("\n## Setup\n\n")
        f.write("1. Create a Python virtual environment:\n")
        f.write("   ```bash\n")
        f.write("   python -m venv venv\n")
        f.write("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate\n")
        f.write("   ```\n\n")
        f.write("2. Install dependencies:\n")
        f.write("   ```bash\n")
        f.write("   pip install -r requirements.txt\n")
        f.write("   ```\n\n")
        f.write("## Running the Project\n\n")
        f.write("To run the main application:\n\n")
        f.write("```bash\n")
        f.write("python app.py\n")
        f.write("```\n\n")
        f.write("## Testing\n\n")
        f.write("Run tests with pytest:\n\n")
        f.write("```bash\n")
        f.write("pytest\n")
        f.write("```\n")
    
    logger.info(f"Created README.md at {readme_path}")

def create_app_py(output_dir: str) -> None:
    """Create a main application entry point."""
    app_path = os.path.join(output_dir, 'app.py')
    
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write("""#!/usr/bin/env python3

import os
import sys
import logging
from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('app')

# Create Flask app
app = Flask(__name__, static_folder='static')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

@app.route('/')
def index():
    return jsonify({
        'message': 'Python converted application is running',
        'status': 'success'
    })

# Add your API routes here
# @app.route('/api/something', methods=['GET'])
# def get_something():
#     return jsonify({'data': 'value'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
""")
    
    logger.info(f"Created app.py at {app_path}")

def main():
    parser = argparse.ArgumentParser(description='Convert TypeScript project to Python')
    parser.add_argument('input_dir', help='Input directory containing TypeScript project')
    parser.add_argument('--output-dir', '-o', help='Output directory for Python project (default: python_converted)')
    parser.add_argument('--skip-non-ts', action='store_true', help='Skip copying non-TypeScript files')
    parser.add_argument('--jobs', '-j', type=int, default=os.cpu_count(), help='Number of parallel conversion jobs')
    
    args = parser.parse_args()
    
    input_dir = args.input_dir
    output_dir = args.output_dir or os.path.join(os.path.dirname(input_dir), 'python_converted')
    
    if not os.path.isdir(input_dir):
        logger.error(f"Input directory does not exist: {input_dir}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all TypeScript files
    logger.info(f"Finding TypeScript files in {input_dir}")
    ts_files = find_typescript_files(input_dir)
    logger.info(f"Found {len(ts_files)} TypeScript files to convert")
    
    # Convert TypeScript files in parallel
    logger.info(f"Converting TypeScript files using {args.jobs} parallel jobs")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
        future_to_file = {
            executor.submit(convert_typescript_file, ts_file, output_dir): ts_file
            for ts_file in ts_files
        }
        
        for future in concurrent.futures.as_completed(future_to_file):
            # Just wait for completion, logging is done in the function
            pass
    
    # Copy non-TypeScript files if needed
    if not args.skip_non_ts:
        logger.info(f"Finding non-TypeScript files in {input_dir}")
        other_files = find_non_typescript_files(input_dir)
        logger.info(f"Found {len(other_files)} non-TypeScript files to copy")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            future_to_file = {
                executor.submit(copy_non_typescript_file, file, output_dir): file
                for file in other_files
            }
            
            for future in concurrent.futures.as_completed(future_to_file):
                # Just wait for completion, logging is done in the function
                pass
    
    # Create __init__.py files
    logger.info("Creating __init__.py files")
    create_init_files(output_dir)
    
    # Fix common issues in converted Python files
    logger.info("Fixing common issues in converted Python files")
    fix_python_files(output_dir)
    
    # Update imports to use relative imports
    logger.info("Updating imports to use relative imports")
    update_imports(output_dir)
    
    # Create requirements.txt
    logger.info("Creating requirements.txt")
    convert_npm_packages(output_dir)
    
    # Create README.md
    logger.info("Creating README.md")
    create_readme(output_dir, input_dir)
    
    # Create app.py
    logger.info("Creating app.py")
    create_app_py(output_dir)
    
    logger.info(f"Conversion complete. Output directory: {output_dir}")
    logger.info("Run 'pip install -r requirements.txt' to install dependencies.")
    logger.info("Run 'python app.py' to start the application.")

if __name__ == '__main__':
    main() 