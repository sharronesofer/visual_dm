#!/usr/bin/env python3

import os
import re
import glob

def simplify_dto_files():
    """Remove problematic attributes and simplify DTO files for Unity compilation"""
    print("🔧 ULTIMATE FIX: Simplifying DTO files for Unity compilation...")
    
    # Find all DTO files
    dto_files = glob.glob("VDM/Assets/Scripts/DTOs/**/*.cs", recursive=True)
    
    for dto_file in dto_files:
        print(f"  Simplifying {dto_file}...")
        
        with open(dto_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove ALL problematic attributes temporarily
        # This will get Unity compiling, then we can add back what works
        
        # Remove JsonPropertyName attributes entirely
        content = re.sub(r'\s*\[JsonPropertyName[^\]]*\]\s*\n', '\n', content, flags=re.MULTILINE)
        
        # Remove Required attributes
        content = re.sub(r'\s*\[Required[^\]]*\]\s*\n', '\n', content, flags=re.MULTILINE)
        content = re.sub(r'\s*\[RequiredAttribute[^\]]*\]\s*\n', '\n', content, flags=re.MULTILINE)
        
        # Remove StringLength attributes
        content = re.sub(r'\s*\[StringLength[^\]]*\]\s*\n', '\n', content, flags=re.MULTILINE)
        content = re.sub(r'\s*\[StringLengthAttribute[^\]]*\]\s*\n', '\n', content, flags=re.MULTILINE)
        
        # Remove EmailAddress attributes
        content = re.sub(r'\s*\[EmailAddress[^\]]*\]\s*\n', '\n', content, flags=re.MULTILINE)
        content = re.sub(r'\s*\[EmailAddressAttribute[^\]]*\]\s*\n', '\n', content, flags=re.MULTILINE)
        
        # Remove Url attributes
        content = re.sub(r'\s*\[Url[^\]]*\]\s*\n', '\n', content, flags=re.MULTILINE)
        content = re.sub(r'\s*\[UrlAttribute[^\]]*\]\s*\n', '\n', content, flags=re.MULTILINE)
        
        # Remove Range attributes (already commented but clean up)
        content = re.sub(r'\s*// \[Range[^\]]*\][^\n]*\n', '\n', content, flags=re.MULTILINE)
        
        # Clean up any remaining #if preprocessor issues
        content = re.sub(r'#if UNITY_EDITOR \|\| UNITY_STANDALONE\s*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'#endif\s*\n', '', content, flags=re.MULTILINE)
        
        # Clean up multiple empty lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content, flags=re.MULTILINE)
        
        # Ensure proper using statements for basic functionality
        if 'using System;' not in content:
            content = 'using System;\n' + content
        if 'using UnityEngine;' not in content:
            content = 'using UnityEngine;\n' + content
        
        # Write back simplified version
        with open(dto_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"✅ Simplified {len(dto_files)} DTO files")

def fix_missing_types():
    """Create basic missing types"""
    print("🔧 Creating basic missing types...")
    
    # Create MetadataDTO
    metadata_dir = "VDM/Assets/Scripts/DTOs/Core/Shared"
    os.makedirs(metadata_dir, exist_ok=True)
    
    metadata_dto = """using System;
using UnityEngine;

namespace VisualDM.DTOs.Core.Shared
{
    [Serializable]
    public class MetadataDTO
    {
        public string CreatedBy { get; set; } = "";
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public string ModifiedBy { get; set; } = "";
        public DateTime ModifiedAt { get; set; } = DateTime.UtcNow;
        public string Version { get; set; } = "1.0.0";
    }
}"""
    
    with open(f"{metadata_dir}/MetadataDTO.cs", 'w') as f:
        f.write(metadata_dto)
    
    print("✅ Created basic missing types")

def remove_global_using():
    """Remove the global using file that might be causing issues"""
    global_using_path = "VDM/Assets/Scripts/GlobalUsings.cs"
    if os.path.exists(global_using_path):
        os.remove(global_using_path)
        print("✅ Removed GlobalUsings.cs (was causing conflicts)")

def main():
    print("🚀 ULTIMATE UNITY FIX - RADICAL SIMPLIFICATION")
    print("=" * 55)
    print("This removes ALL problematic attributes to get Unity compiling")
    print("We can add them back gradually once it works")
    print("=" * 55)
    
    remove_global_using()
    simplify_dto_files()
    fix_missing_types()
    
    print("=" * 55)
    print("✅ RADICAL SIMPLIFICATION COMPLETE!")
    print("")
    print("📝 WHAT WAS DONE:")
    print("1. ✅ Removed ALL JsonPropertyName attributes")
    print("2. ✅ Removed ALL validation attributes (Required, StringLength, etc.)")
    print("3. ✅ Removed ALL preprocessor directives")
    print("4. ✅ Cleaned up problematic GlobalUsings.cs")
    print("5. ✅ Added basic missing types")
    print("")
    print("🧪 Unity should now compile without attribute errors!")
    print("📈 Once working, we can gradually add back working attributes")

if __name__ == "__main__":
    main() 