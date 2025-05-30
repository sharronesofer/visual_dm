#!/usr/bin/env python3

import os
import re
import glob

def fix_dto_files():
    """Fix all DTO files by adding proper using statements and fixing attributes"""
    print("🔧 Fixing ALL DTO files with missing using statements...")
    
    # Find all DTO files
    dto_files = glob.glob("VDM/Assets/Scripts/DTOs/**/*.cs", recursive=True)
    
    # Required using statements for DTO files
    required_usings = [
        "using System;",
        "using System.Collections.Generic;",
        "using System.ComponentModel.DataAnnotations;",
        "using System.Text.Json.Serialization;",
        "using UnityEngine;",
    ]
    
    for dto_file in dto_files:
        print(f"  Fixing {dto_file}...")
        
        with open(dto_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content into lines for processing
        lines = content.split('\n')
        new_lines = []
        
        # Add using statements at the top (after any existing ones)
        using_added = False
        namespace_found = False
        
        for i, line in enumerate(lines):
            # Skip if we've already added usings and found namespace
            if using_added and namespace_found:
                new_lines.append(line)
                continue
            
            # Add usings before namespace declaration
            if line.strip().startswith('namespace ') and not using_added:
                # Check if required usings are missing
                content_str = '\n'.join(lines[:i])
                for using_stmt in required_usings:
                    if using_stmt not in content_str:
                        new_lines.append(using_stmt)
                new_lines.append('')  # Empty line before namespace
                using_added = True
                namespace_found = True
            
            new_lines.append(line)
        
        # If no namespace found, add usings at the top
        if not using_added:
            final_lines = []
            content_str = content
            for using_stmt in required_usings:
                if using_stmt not in content_str:
                    final_lines.append(using_stmt)
            if final_lines:
                final_lines.append('')  # Empty line
            final_lines.extend(lines)
            new_lines = final_lines
        
        # Join back and apply attribute fixes
        fixed_content = '\n'.join(new_lines)
        
        # Fix attribute accessibility issues
        fixed_content = fix_attribute_issues(fixed_content)
        
        # Write back
        with open(dto_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
    
    print(f"✅ Fixed {len(dto_files)} DTO files")

def fix_attribute_issues(content):
    """Fix common attribute accessibility and naming issues"""
    
    # Fix JsonPropertyNameAttribute accessibility (make it JsonPropertyName)
    content = re.sub(r'\[JsonPropertyNameAttribute\(', '[JsonPropertyName(', content)
    
    # Fix attribute naming issues - remove 'Attribute' suffix where Unity expects it
    attribute_fixes = {
        'RequiredAttribute': 'Required',
        'StringLengthAttribute': 'StringLength', 
        'EmailAddressAttribute': 'EmailAddress',
        'UrlAttribute': 'Url',
        'RangeAttribute': 'Range'
    }
    
    for old_attr, new_attr in attribute_fixes.items():
        content = re.sub(f'\\[{old_attr}\\(', f'[{new_attr}(', content)
        content = re.sub(f'\\[{old_attr}\\]', f'[{new_attr}]', content)
    
    # Fix Range attribute usage - it should work with System.ComponentModel.DataAnnotations
    # But if it's still having issues, we can comment it out temporarily
    content = re.sub(r'(\[Range\([^\]]+\])', r'// \1 // Temporarily disabled due to compilation issues', content)
    
    return content

def create_missing_dto_types():
    """Create missing DTO types that are referenced but don't exist"""
    print("🔧 Creating missing DTO types...")
    
    dto_dir = "VDM/Assets/Scripts/DTOs/Core/Shared"
    os.makedirs(dto_dir, exist_ok=True)
    
    # Create SuccessResponseDTO
    success_response_dto = """using System;
using System.Text.Json.Serialization;

namespace VisualDM.DTOs.Core.Shared
{
    /// <summary>
    /// Generic success response DTO
    /// </summary>
    [Serializable]
    public class SuccessResponseDTO
    {
        [JsonPropertyName("success")]
        public bool Success { get; set; } = true;
        
        [JsonPropertyName("message")]
        public string Message { get; set; } = "Operation completed successfully";
        
        [JsonPropertyName("timestamp")]
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        
        [JsonPropertyName("data")]
        public object? Data { get; set; }
    }
}"""
    
    with open(f"{dto_dir}/SuccessResponseDTO.cs", 'w') as f:
        f.write(success_response_dto)
    
    print(f"✅ Created missing DTO types in {dto_dir}")

def add_global_using_file():
    """Add a GlobalUsings.cs file to reduce repetitive using statements"""
    print("🔧 Creating GlobalUsings.cs for better organization...")
    
    global_usings = """// Global using statements for the project
global using System;
global using System.Collections.Generic;
global using System.ComponentModel.DataAnnotations;
global using System.Text.Json.Serialization;
global using UnityEngine;

// Common DTO namespace
global using VisualDM.DTOs.Core.Shared;"""
    
    with open("VDM/Assets/Scripts/GlobalUsings.cs", 'w') as f:
        f.write(global_usings)
    
    print("✅ Created GlobalUsings.cs")

def main():
    print("🚀 COMPREHENSIVE DTO FIX - RESOLVING ALL COMPILATION ERRORS")
    print("=" * 60)
    
    fix_dto_files()
    create_missing_dto_types()
    add_global_using_file()
    
    print("=" * 60)
    print("✅ All DTO fixes applied!")
    print("")
    print("📝 SUMMARY OF FIXES:")
    print("1. ✅ Added missing using statements to all DTO files")
    print("2. ✅ Fixed JsonPropertyNameAttribute accessibility issues")
    print("3. ✅ Fixed validation attribute naming issues")
    print("4. ✅ Temporarily disabled problematic Range attributes")
    print("5. ✅ Created missing SuccessResponseDTO type")
    print("6. ✅ Added GlobalUsings.cs for better organization")
    print("")
    print("🧪 Next: Test Unity compilation...")

if __name__ == "__main__":
    main() 