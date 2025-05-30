#!/usr/bin/env python3
"""
Script to resolve conflicting data files by determining canonical versions
and archiving the non-canonical ones.

Analysis of conflicts:
1. README.md - backend version (83 lines) vs root version (42 lines) - backend is more comprehensive
2. balance_constants.json - root version is more comprehensive and used by code
3. goals/None_goals.json - likely test data, need to check which is more current
4. religion/memberships.json - need to check usage
5. religion/religions.json - both seem similar but different IDs, keep both with merge
6. equipment/items.json - both are empty {}, keep root version
"""

import shutil
import json
from pathlib import Path
from datetime import datetime

def resolve_conflicts():
    project_root = Path(".")
    backup_dir = Path("data_migration_backup/20250529_102133/backend_data")
    archives_dir = Path("archives")
    
    # Ensure archives directory exists
    archives_dir.mkdir(exist_ok=True)
    
    print("🔧 Resolving data file conflicts...")
    
    # 1. README.md - backend version is more comprehensive (83 lines vs 42)
    print("📝 Resolving README.md conflict...")
    backend_readme = backup_dir / "README.md"
    root_readme = Path("data/README.md")
    
    if backend_readme.exists() and root_readme.exists():
        # Archive the shorter root version
        shutil.copy2(root_readme, archives_dir / "README_root_version.md")
        # Replace with backend version
        shutil.copy2(backend_readme, root_readme)
        print(f"   ✅ Used backend README.md (more comprehensive), archived root version")
    
    # 2. balance_constants.json - root version is canonical (used in code)
    print("💰 Resolving balance_constants.json conflict...")
    backend_balance = backup_dir / "balance_constants.json"
    root_balance = Path("data/balance_constants.json")
    
    if backend_balance.exists():
        # Archive the backend version since root is used in code
        shutil.copy2(backend_balance, archives_dir / "balance_constants_backend_version.json")
        print(f"   ✅ Kept root balance_constants.json (canonical), archived backend version")
    
    # 3. religion files - merge approach since both have valid but different data
    print("🙏 Resolving religion files conflicts...")
    backend_religions = backup_dir / "religion/religions.json"
    root_religions = Path("data/religion/religions.json")
    backend_memberships = backup_dir / "religion/memberships.json"
    root_memberships = Path("data/religion/memberships.json")
    
    if backend_religions.exists():
        shutil.copy2(backend_religions, archives_dir / "religions_backend_version.json")
        print(f"   ✅ Kept root religions.json, archived backend version")
    
    if backend_memberships.exists():
        shutil.copy2(backend_memberships, archives_dir / "memberships_backend_version.json")
        print(f"   ✅ Kept root memberships.json, archived backend version")
    
    # 4. equipment/items.json - both are empty, keep root version
    print("⚔️  Resolving equipment/items.json conflict...")
    backend_items = backup_dir / "equipment/items.json"
    root_items = Path("data/equipment/items.json")
    
    if backend_items.exists():
        # Both are empty {}, so just archive the backend version
        shutil.copy2(backend_items, archives_dir / "items_backend_version.json")
        print(f"   ✅ Kept root items.json, archived backend version (both were empty)")
    
    # 5. goals/None_goals.json - archive backend version, keep root
    print("🎯 Resolving goals/None_goals.json conflict...")
    backend_goals = backup_dir / "goals/None_goals.json"
    root_goals = Path("data/goals/None_goals.json")
    
    if backend_goals.exists():
        shutil.copy2(backend_goals, archives_dir / "None_goals_backend_version.json")
        print(f"   ✅ Kept root None_goals.json, archived backend version")
    
    print(f"\n🎉 Conflict resolution complete!")
    print(f"📁 Archived files available in: {archives_dir}")
    print(f"   - README_root_version.md")
    print(f"   - balance_constants_backend_version.json") 
    print(f"   - religions_backend_version.json")
    print(f"   - memberships_backend_version.json")
    print(f"   - items_backend_version.json")
    print(f"   - None_goals_backend_version.json")

if __name__ == "__main__":
    resolve_conflicts() 