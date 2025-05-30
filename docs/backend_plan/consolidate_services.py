#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path

# Configuration
BACKEND_DIR = os.path.abspath("../backend")
ARCHIVE_DIR = os.path.join(BACKEND_DIR, "archive")
TOP_LEVEL_SERVICES = os.path.join(BACKEND_DIR, "services")
SRC_SERVICES = os.path.join(BACKEND_DIR, "src", "services")

def run_command(cmd):
    """Run a command and return its output."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""

def check_imports(module_path):
    """Check how many times a module is imported in the codebase."""
    # Remove the backend/ prefix to match import statements
    relative_path = module_path.replace(BACKEND_DIR + "/", "")
    cmd = f'find {BACKEND_DIR} -name "*.py" -type f -exec grep -l "from {relative_path} import\\|import {relative_path}\\." {{}} \\; | wc -l'
    result = run_command(cmd)
    try:
        return int(result.strip())
    except ValueError:
        return 0

def copy_unique_files(src_dir, dest_dir):
    """Copy files from src_dir to dest_dir if they don't exist in dest_dir."""
    if not os.path.exists(src_dir):
        print(f"Source directory {src_dir} does not exist.")
        return
    
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    for root, dirs, files in os.walk(src_dir):
        # Get the relative path from src_dir
        rel_path = os.path.relpath(root, src_dir)
        if rel_path == ".":
            rel_path = ""
        
        # Create the corresponding directory in dest_dir
        dest_path = os.path.join(dest_dir, rel_path)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        
        # Copy files that don't exist in dest_dir
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_path, file)
            if not os.path.exists(dest_file):
                shutil.copy2(src_file, dest_file)
                print(f"Copied {src_file} to {dest_file}")

def consolidate_services():
    """Consolidate services folders."""
    # Check which services folder is more commonly imported
    top_level_imports = check_imports("services")
    src_imports = check_imports("src.services")
    
    print(f"Top-level services imports: {top_level_imports}")
    print(f"src.services imports: {src_imports}")
    
    # Determine which folder to keep as the primary one
    if top_level_imports >= src_imports:
        primary_dir = TOP_LEVEL_SERVICES
        secondary_dir = SRC_SERVICES
        print("Keeping top-level services as primary")
    else:
        primary_dir = SRC_SERVICES
        secondary_dir = TOP_LEVEL_SERVICES
        print("Keeping src.services as primary")
    
    # Copy unique files from secondary to primary
    copy_unique_files(secondary_dir, primary_dir)
    
    # Create a backup of the secondary directory
    secondary_basename = os.path.basename(os.path.dirname(secondary_dir)) + "_" + os.path.basename(secondary_dir)
    backup_dir = os.path.join(ARCHIVE_DIR, secondary_basename)
    if os.path.exists(secondary_dir):
        shutil.copytree(secondary_dir, backup_dir, dirs_exist_ok=True)
        print(f"Created backup of {secondary_dir} at {backup_dir}")
    
    # If primary dir is src.services, create symlink from top-level to src
    if primary_dir == SRC_SERVICES and os.path.exists(secondary_dir):
        shutil.rmtree(secondary_dir)
        # Copy src.services to top-level instead of creating symlink
        shutil.copytree(primary_dir, secondary_dir, dirs_exist_ok=True)
        print(f"Copied {primary_dir} to {secondary_dir}")

if __name__ == "__main__":
    consolidate_services() 