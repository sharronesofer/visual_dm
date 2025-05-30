#!/usr/bin/env python3
import os
import subprocess
import sys

def run_command(cmd):
    """Run a command and return its output."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""

# Folders to skip (important documentation, configuration, etc.)
SKIP_FOLDERS = {
    "docs", "reports", "scripts", "logs", "config", "archive", "data", 
    "migrations", "alembic", "alembic_broken", "performance", "tests", 
    "templates", "helm", "k8s", "__pycache__", ".pytest_cache", "htmlcov"
}

# Get all top-level directories in backend
backend_dir = "backend"
top_level_dirs = [d for d in os.listdir(backend_dir) 
                 if os.path.isdir(os.path.join(backend_dir, d)) 
                 and d not in SKIP_FOLDERS
                 and not d.startswith('.')]

print(f"Found {len(top_level_dirs)} top-level directories in {backend_dir}/")

unused_dirs = []
for directory in sorted(top_level_dirs):
    # Check if any Python files import from this directory
    cmd = f"find {backend_dir} -name '*.py' -type f -exec grep -l 'from {directory} import\\|import {directory}\\.' {{}} \\; | head -1"
    result = run_command(cmd)
    
    # If no imports are found, mark this directory as unused
    if not result:
        unused_dirs.append(directory)

print(f"\nFound {len(unused_dirs)} potentially unused directories:")
for d in unused_dirs:
    print(f"- {backend_dir}/{d}")

print("\nDirectories to skip:")
for d in sorted(SKIP_FOLDERS):
    print(f"- {backend_dir}/{d}")

# Save to file
with open("unused_folders.txt", "w") as f:
    for d in unused_dirs:
        f.write(f"{d}\n")

print("\nList of potentially unused folders saved to unused_folders.txt")
print("IMPORTANT: Review this list carefully before archiving any folders!") 