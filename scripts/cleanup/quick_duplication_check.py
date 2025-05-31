#!/usr/bin/env python3

import os
import hashlib
from collections import defaultdict, Counter
from pathlib import Path
import re

def quick_duplication_check(backend_dir):
    """Quick check for remaining duplicates"""
    print("⚡ QUICK DUPLICATION CHECK")
    print("=" * 50)
    
    backend_path = Path(backend_dir)
    python_files = list(backend_path.rglob("*.py"))
    
    print(f"📁 Analyzing {len(python_files)} Python files...")
    
    # File-level checks
    file_hashes = defaultdict(list)
    file_names = defaultdict(list)
    
    # Function and class pattern checks
    function_bodies = defaultdict(list)
    class_bodies = defaultdict(list)
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # File duplicate check
            file_hash = hashlib.md5(content.encode()).hexdigest()
            file_hashes[file_hash].append(file_path)
            
            # File name duplicate check
            file_names[file_path.name].append(file_path)
            
            # Function duplicate check (simple pattern)
            functions = re.findall(r'def\s+(\w+)\s*\([^)]*\):\s*\n((?:\s{4,}.*\n)*)', content)
            for func_name, func_body in functions:
                func_body_hash = hashlib.md5(func_body.encode()).hexdigest()
                function_bodies[func_body_hash].append((file_path, func_name, func_body))
            
            # Class duplicate check
            classes = re.findall(r'class\s+(\w+).*?:\s*\n((?:\s{4,}.*\n)*)', content, re.DOTALL)
            for class_name, class_body in classes:
                class_body_hash = hashlib.md5(class_body.encode()).hexdigest()
                class_bodies[class_body_hash].append((file_path, class_name, class_body))
                
        except Exception as e:
            continue
    
    # Count duplicates
    exact_file_dupes = sum(1 for files in file_hashes.values() if len(files) > 1)
    name_dupes = sum(1 for files in file_names.values() if len(files) > 1)
    function_dupes = sum(len(funcs) - 1 for funcs in function_bodies.values() if len(funcs) > 1)
    class_dupes = sum(len(classes) - 1 for classes in class_bodies.values() if len(classes) > 1)
    
    # Results
    print(f"\n📊 DUPLICATION SUMMARY:")
    print(f"   Exact file duplicates: {exact_file_dupes}")
    print(f"   Duplicate file names: {name_dupes}")
    print(f"   Duplicate function bodies: {function_dupes}")
    print(f"   Duplicate class bodies: {class_dupes}")
    
    total_duplicates = exact_file_dupes + function_dupes + class_dupes
    print(f"\n🎯 TOTAL DUPLICATES: {total_duplicates}")
    
    if total_duplicates == 0:
        print("✅ CODEBASE IS FULLY DEDUPLICATED!")
        return True
    else:
        print("❌ CODEBASE STILL HAS DUPLICATES!")
        
        # Show worst offenders
        if exact_file_dupes > 0:
            print(f"\n🔴 EXACT FILE DUPLICATES:")
            for hash_val, files in file_hashes.items():
                if len(files) > 1:
                    print(f"   {len(files)} files with same content:")
                    for file_path in files[:3]:  # Show first 3
                        print(f"     • {file_path.relative_to(backend_path)}")
                    if len(files) > 3:
                        print(f"     ... and {len(files) - 3} more")
        
        if function_dupes > 0:
            print(f"\n🟡 FUNCTION DUPLICATES (top 5):")
            func_groups = [(len(funcs), funcs) for funcs in function_bodies.values() if len(funcs) > 1]
            func_groups.sort(key=lambda x: x[0], reverse=True)
            
            for count, funcs in func_groups[:5]:
                func_name = funcs[0][1]
                print(f"   Function '{func_name}' appears {count} times:")
                for file_path, _, _ in funcs[:3]:
                    print(f"     • {file_path.relative_to(backend_path)}")
                if count > 3:
                    print(f"     ... and {count - 3} more")
        
        return False

if __name__ == "__main__":
    backend_dir = "backend/systems"
    
    if not os.path.exists(backend_dir):
        print(f"❌ Backend directory not found: {backend_dir}")
        exit(1)
    
    is_clean = quick_duplication_check(backend_dir)
    
    if is_clean:
        print(f"\n🎉 SUCCESS: No duplicates found!")
    else:
        print(f"\n⚠️  WARNING: Duplicates detected!")
        print(f"   Consider running additional deduplication scripts.") 