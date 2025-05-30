#!/usr/bin/env python3

import os
import re
import glob

def fix_dto_file(file_path):
    """Fix missing #endif directives in a DTO file"""
    print(f"Processing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to find #if UNITY_EDITOR || UNITY_STANDALONE followed by [Required] but missing #endif
    # We'll look for the pattern and add #endif after the [Required] line
    pattern = r'(#if UNITY_EDITOR \|\| UNITY_STANDALONE\s*\n\s*\[Required\]\s*\n)'
    replacement = r'\1#endif\n'
    
    # Apply the fix
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Also handle cases where there might be other attributes after [Required]
    # Look for #if without matching #endif before next property or class
    lines = content.split('\n')
    fixed_lines = []
    in_if_block = False
    if_line_index = -1
    
    for i, line in enumerate(lines):
        if '#if UNITY_EDITOR || UNITY_STANDALONE' in line:
            in_if_block = True
            if_line_index = i
            fixed_lines.append(line)
        elif in_if_block and '[Required]' in line:
            fixed_lines.append(line)
            # Add #endif after the [Required] line
            fixed_lines.append('#endif')
            in_if_block = False
        elif in_if_block and line.strip().startswith('public ') and '{' in line:
            # We hit a property declaration without seeing [Required], add #endif before it
            fixed_lines.append('#endif')
            fixed_lines.append(line)
            in_if_block = False
        else:
            fixed_lines.append(line)
    
    fixed_content = '\n'.join(fixed_lines)
    
    # Only write if content changed
    if fixed_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"  ✅ Fixed {file_path}")
        return True
    else:
        print(f"  ⏩ No changes needed for {file_path}")
        return False

def main():
    print("🔧 Fixing #endif directive issues in DTO files...")
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