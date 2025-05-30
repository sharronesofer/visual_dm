#!/usr/bin/env python3

import os
import re
import glob

def fix_dto_file(file_path):
    """Fix preprocessor directive issues in a DTO file by removing extra #endif"""
    print(f"Processing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Remove duplicate #endif lines that are on their own
    lines = content.split('\n')
    fixed_lines = []
    prev_line = ""
    
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        prev_stripped = prev_line.strip()
        
        # Skip duplicate #endif
        if stripped_line == "#endif" and prev_stripped == "#endif":
            print(f"  Removing duplicate #endif at line {i+1}")
            continue
        
        # For the pattern that should be:
        # #if UNITY_EDITOR || UNITY_STANDALONE
        # [Required]
        # #endif
        # But got extra #endif
        if (stripped_line == "#endif" and 
            len(fixed_lines) >= 2 and
            fixed_lines[-1].strip() == "#endif" and 
            "[Required]" in fixed_lines[-2]):
            print(f"  Removing extra #endif after [Required] at line {i+1}")
            continue
            
        fixed_lines.append(line)
        prev_line = line
    
    fixed_content = '\n'.join(fixed_lines)
    
    # Clean up any remaining issues - remove standalone orphaned #endif
    # that don't have a matching #if above them
    lines = fixed_content.split('\n')
    final_lines = []
    ifdef_stack = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if stripped.startswith('#if'):
            ifdef_stack.append(i)
            final_lines.append(line)
        elif stripped == '#endif':
            if ifdef_stack:
                ifdef_stack.pop()
                final_lines.append(line)
            else:
                print(f"  Removing orphaned #endif at line {i+1}")
                # Skip orphaned #endif
                continue
        else:
            final_lines.append(line)
    
    final_content = '\n'.join(final_lines)
    
    # Only write if content changed
    if final_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print(f"  ✅ Fixed {file_path}")
        return True
    else:
        print(f"  ⏩ No changes needed for {file_path}")
        return False

def main():
    print("🔧 Fixing preprocessor directive issues in DTO files (v2)...")
    print()
    
    # Find all DTO files
    dto_pattern = "VDM/Assets/Scripts/DTOs/**/*.cs"
    dto_files = glob.glob(dto_pattern, recursive=True)
    
    if not dto_files:
        print("❌ No DTO files found!")
        return
    
    print(f"Found {len(dto_files)} DTO files to check:")
    for file in dto_files:
        print(f"  - {file}")
    print()
    
    fixed_count = 0
    for file_path in dto_files:
        if fix_dto_file(file_path):
            fixed_count += 1
    
    print()
    print(f"✅ Processing complete! Fixed {fixed_count} files.")

if __name__ == "__main__":
    main() 