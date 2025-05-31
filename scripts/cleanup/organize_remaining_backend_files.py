#!/usr/bin/env python3
"""
Backend Remaining Files Organization Script

This script handles the remaining misplaced directories and files in /backend:
- backend/backend/ → merge content appropriately
- backend/htmlcov_region/ → scripts/coverage/htmlcov_region/
- backend/rules_json/ → data/rules_json/ (but user said ignore data)
- backend/core/ → systems/shared/core/ (or keep as core/ if it's infrastructure)
- backend/.env → move to root or docs if it's a template
- Other cache and build artifacts
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

def organize_remaining_files(backend_path: str = "backend", dry_run: bool = True):
    """Organize remaining misplaced files and directories"""
    backend_path = Path(backend_path)
    
    print(f"{'DRY RUN: ' if dry_run else ''}Organizing remaining backend files...")
    
    moves = []
    
    # 1. Handle backend/backend/ - this looks like a duplicate structure
    backend_backend = backend_path / "backend"
    if backend_backend.exists():
        print(f"\n📁 Processing {backend_backend}")
        
        # Move useful files from backend/backend/ to appropriate locations
        for item in backend_backend.iterdir():
            if item.name == "systems":
                # Skip systems as we already have the main one
                print(f"  ⏭️  Skipping duplicate systems directory")
                continue
            elif item.name == "tests":
                print(f"  ⏭️  Skipping duplicate tests directory")  
                continue
            elif item.name == "data":
                print(f"  ⏭️  Skipping duplicate data directory")
                continue
            elif item.name.endswith('.json') or item.name.endswith('.md'):
                # Move reports and JSON files to docs
                target = backend_path / "docs" / item.name
                moves.append((item, target, "Duplicate report/data"))
            elif item.name in ['.coverage', 'coverage.json']:
                # Move coverage files
                target = backend_path / "scripts" / "coverage" / item.name
                moves.append((item, target, "Coverage data"))
    
    # 2. Handle htmlcov_region/ - coverage report
    htmlcov_region = backend_path / "htmlcov_region"
    if htmlcov_region.exists():
        target = backend_path / "scripts" / "coverage" / "htmlcov_region"
        moves.append((htmlcov_region, target, "Regional coverage report"))
    
    # 3. Handle rules_json/ - game data (but user said ignore data)
    rules_json = backend_path / "rules_json"
    if rules_json.exists():
        # Since user said ignore /data, let's move this to a better location
        target = backend_path / "systems" / "shared" / "data" / "rules_json"
        moves.append((rules_json, target, "Game rules data"))
    
    # 4. Handle core/ - looks like infrastructure code
    core_dir = backend_path / "core"
    if core_dir.exists():
        # This looks like shared infrastructure, move to systems/shared/
        target = backend_path / "systems" / "shared" / "core"
        moves.append((core_dir, target, "Core infrastructure"))
    
    # 5. Handle .env file in docs (it was moved there by mistake)
    env_file = backend_path / "docs" / ".env"
    if env_file.exists():
        # .env should be in project root or stay in backend root for backend config
        target = backend_path / ".env"
        moves.append((env_file, target, "Environment configuration"))
    
    # 6. Clean up any remaining __pycache__ in docs
    pycache_docs = backend_path / "docs" / "__pycache__"
    if pycache_docs.exists():
        print(f"  🗑️  Will remove __pycache__ from docs")
        if not dry_run:
            shutil.rmtree(pycache_docs)
    
    # Display plan
    print(f"\n📋 Additional organization plan:")
    for source, target, description in moves:
        print(f"  📄 {source.name} → {target.relative_to(backend_path)} ({description})")
    
    # Execute moves
    if not dry_run:
        print(f"\n🚀 Executing additional file moves...")
        for source, target, description in moves:
            try:
                # Create parent directory if needed
                target.parent.mkdir(parents=True, exist_ok=True)
                
                if source.is_dir():
                    shutil.move(str(source), str(target))
                else:
                    shutil.move(str(source), str(target))
                    
                print(f"    ✅ Moved {source.name} → {target.relative_to(backend_path)}")
            except Exception as e:
                print(f"    ❌ Failed to move {source.name}: {e}")
        
        # Remove the now-empty backend/backend directory
        if backend_backend.exists() and not any(backend_backend.iterdir()):
            try:
                backend_backend.rmdir()
                print(f"    ✅ Removed empty backend/backend directory")
            except Exception as e:
                print(f"    ❌ Failed to remove backend/backend: {e}")
    
    print(f"\n📊 Summary: {len(moves)} additional moves planned")
    return moves

def verify_canonical_structure(backend_path: str = "backend"):
    """Verify the final canonical structure"""
    backend_path = Path(backend_path)
    
    print(f"\n🔍 Verifying canonical structure in {backend_path}")
    
    expected_structure = {
        'systems': 'Core game systems',
        'tests': 'All test files',
        'docs': 'Documentation and reports',
        'scripts': 'Development and maintenance scripts',
        'logs': 'Log files',
        'data': 'Game data (user specified to ignore)',
        'main.py': 'Application entry point',
        'requirements.txt': 'Dependencies'
    }
    
    print("\n✅ Expected canonical structure:")
    for item, description in expected_structure.items():
        path = backend_path / item
        status = "✅" if path.exists() else "❌"
        print(f"  {status} {item} - {description}")
    
    # Check for any remaining unexpected files/directories
    unexpected = []
    for item in backend_path.iterdir():
        if item.name not in expected_structure and not item.name.startswith('.') and item.name != '__pycache__':
            unexpected.append(item.name)
    
    if unexpected:
        print(f"\n⚠️  Unexpected items still in backend root:")
        for item in unexpected:
            print(f"    📄 {item}")
    else:
        print(f"\n🎉 Backend directory structure is now canonical!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Organize remaining backend files")
    parser.add_argument("--execute", action="store_true", help="Execute the moves (default is dry run)")
    parser.add_argument("--backend-path", default="backend", help="Path to backend directory")
    
    args = parser.parse_args()
    
    # Organize remaining files
    moves = organize_remaining_files(args.backend_path, dry_run=not args.execute)
    
    # Verify structure
    verify_canonical_structure(args.backend_path)
    
    if not args.execute:
        print("\n💡 This was a dry run. Use --execute to actually move files.")
        print("   python organize_remaining_backend_files.py --execute") 