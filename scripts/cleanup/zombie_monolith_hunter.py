#!/usr/bin/env python3
"""
🧟 ZOMBIE MONOLITH HUNTER
Identifies large files that are likely leftovers from refactoring
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_zombie_monoliths():
    """Find large files that might be zombie monoliths"""
    
    systems_dir = Path("backend/systems")
    if not systems_dir.exists():
        print("❌ backend/systems directory not found")
        return
    
    print("🧟 ZOMBIE MONOLITH HUNTER")
    print("=" * 60)
    
    # Find all Python files and their sizes
    large_files = []
    
    for py_file in systems_dir.rglob("*.py"):
        if py_file.is_file():
            try:
                lines = len(py_file.read_text(encoding='utf-8').splitlines())
                size_kb = py_file.stat().st_size / 1024
                
                # Consider files over 500 lines or 20KB as potentially large
                if lines > 500 or size_kb > 20:
                    large_files.append({
                        'path': py_file,
                        'lines': lines,
                        'size_kb': size_kb,
                        'system': py_file.parts[2] if len(py_file.parts) > 2 else 'unknown'
                    })
            except Exception as e:
                continue
    
    # Sort by size (largest first)
    large_files.sort(key=lambda x: x['lines'], reverse=True)
    
    print(f"\n📊 LARGE FILES ANALYSIS ({len(large_files)} files > 500 lines)")
    print("=" * 60)
    
    zombie_candidates = []
    
    for file_info in large_files:
        path = file_info['path']
        lines = file_info['lines']
        size_kb = file_info['size_kb']
        system = file_info['system']
        
        # Check if this might be a zombie monolith
        is_zombie_candidate = False
        zombie_reasons = []
        
        # Pattern 1: Generic names that suggest monolithic design
        generic_names = ['class', 'manager', 'service', 'utils', 'main', 'core']
        filename = path.stem.lower()
        
        for generic in generic_names:
            if generic in filename and lines > 1000:
                is_zombie_candidate = True
                zombie_reasons.append(f"Large file with generic name '{generic}'")
        
        # Pattern 2: Check if there are smaller files in same directory that might be refactored pieces
        parent_dir = path.parent
        sibling_files = [f for f in parent_dir.glob("*.py") if f != path]
        
        if len(sibling_files) > 3 and lines > 1500:
            is_zombie_candidate = True
            zombie_reasons.append(f"Large file ({lines} lines) with {len(sibling_files)} siblings")
        
        # Pattern 3: Files that are much larger than average in their system
        if lines > 1500:
            is_zombie_candidate = True
            zombie_reasons.append(f"Exceptionally large file ({lines} lines)")
        
        status = "🧟 ZOMBIE CANDIDATE" if is_zombie_candidate else "📄 Large file"
        
        print(f"\n{status}")
        print(f"   📁 {path.relative_to(systems_dir)}")
        print(f"   📏 {lines:,} lines, {size_kb:.1f} KB")
        print(f"   🏷️  System: {system}")
        
        if is_zombie_candidate:
            zombie_candidates.append(file_info)
            for reason in zombie_reasons:
                print(f"   ⚠️  {reason}")
            
            # Show sibling files
            if sibling_files:
                print(f"   👥 Siblings: {', '.join([f.name for f in sibling_files[:5]])}")
                if len(sibling_files) > 5:
                    print(f"        ... and {len(sibling_files) - 5} more")
    
    print(f"\n🎯 ZOMBIE SUMMARY")
    print("=" * 60)
    print(f"Total large files: {len(large_files)}")
    print(f"Zombie candidates: {len(zombie_candidates)}")
    
    if zombie_candidates:
        total_zombie_lines = sum(f['lines'] for f in zombie_candidates)
        print(f"Potential lines to review: {total_zombie_lines:,}")
        print(f"Potential size reduction: {sum(f['size_kb'] for f in zombie_candidates):.1f} KB")
        
        print(f"\n🔍 TOP ZOMBIE CANDIDATES:")
        for i, zombie in enumerate(zombie_candidates[:10], 1):
            print(f"{i:2d}. {zombie['path'].name} ({zombie['lines']:,} lines)")
    
    return zombie_candidates

if __name__ == "__main__":
    analyze_zombie_monoliths() 