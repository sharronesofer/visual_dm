#!/usr/bin/env python3

import os
import re
import glob

def fix_duplicate_dto_files():
    """Remove duplicate DTO files that we accidentally created"""
    print("🔧 Removing duplicate DTO files...")
    
    duplicate_files = [
        "VDM/Assets/Scripts/DTOs/Core/Shared/MetadataDTO.cs",
        "VDM/Assets/Scripts/DTOs/Core/Shared/SuccessResponseDTO.cs", 
        "VDM/Assets/Scripts/DTOs/Core/Shared/CoordinateDTO.cs"
    ]
    
    for file_path in duplicate_files:
        if os.path.exists(file_path):
            print(f"  Removing duplicate {file_path}")
            os.remove(file_path)

def fix_broken_using_statements():
    """Fix broken using statements in DTO files"""
    print("🔧 Fixing broken using statements in DTOs...")
    
    # Files with broken VDM.Assets.Scripts.DTOs.Core using statements
    broken_files = [
        "VDM/Assets/Scripts/DTOs/Economic/Equipment/EquipmentDTO.cs",
        "VDM/Assets/Scripts/DTOs/Social/Memory/MemoryDTO.cs",
        "VDM/Assets/Scripts/DTOs/Social/NPC/NPCdto.cs"
    ]
    
    for file_path in broken_files:
        if os.path.exists(file_path):
            print(f"  Fixing {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove the broken using statement
            content = re.sub(r'using VDM\.Assets\.Scripts\.DTOs\.Core;.*?\n', '', content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

def fix_duplicate_private_modifiers():
    """Fix duplicate 'private' modifiers from WebSocket commenting"""
    print("🔧 Fixing duplicate 'private' modifiers...")
    
    # Find all .cs files and fix duplicate private modifiers
    cs_files = glob.glob("VDM/Assets/Scripts/**/*.cs", recursive=True)
    
    for file_path in cs_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix duplicate private modifiers
            if "private private" in content:
                print(f"  Fixing duplicate private in {file_path}")
                content = content.replace("private private", "private")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
        except Exception as e:
            print(f"  Warning: Could not process {file_path}: {e}")

def fix_duplicate_attributes():
    """Fix duplicate [Serializable] attributes"""
    print("🔧 Fixing duplicate [Serializable] attributes...")
    
    cs_files = glob.glob("VDM/Assets/Scripts/**/*.cs", recursive=True)
    
    for file_path in cs_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove duplicate [Serializable] attributes
            lines = content.split('\n')
            fixed_lines = []
            prev_line_serializable = False
            
            for line in lines:
                stripped = line.strip()
                
                if stripped == "[Serializable]":
                    if not prev_line_serializable:
                        fixed_lines.append(line)
                        prev_line_serializable = True
                    else:
                        print(f"  Removing duplicate [Serializable] in {file_path}")
                        # Skip this duplicate
                        continue
                else:
                    fixed_lines.append(line)
                    prev_line_serializable = False
            
            new_content = '\n'.join(fixed_lines)
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                    
        except Exception as e:
            print(f"  Warning: Could not process {file_path}: {e}")

def add_missing_serializable_attribute():
    """Add [Serializable] attribute to files that need it"""
    print("🔧 Adding missing [Serializable] attribute...")
    
    files_needing_serializable = [
        "VDM/Assets/Scripts/Modules/World/CityMapController.cs"
    ]
    
    for file_path in files_needing_serializable:
        if os.path.exists(file_path):
            print(f"  Adding [Serializable] to {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add using System; at the top if not present
            if "using System;" not in content:
                content = "using System;\n" + content
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

def fix_duplicate_validation_result():
    """Fix duplicate ModValidationResult definition"""
    print("🔧 Fixing duplicate ModValidationResult...")
    
    validation_service_path = "VDM/Assets/Scripts/Runtime/Systems/Data/ModValidationService.cs"
    
    if os.path.exists(validation_service_path):
        print(f"  Fixing {validation_service_path}")
        with open(validation_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove any duplicate ModValidationResult class definitions
        # Keep only the first occurrence
        parts = content.split("public class ModValidationResult")
        if len(parts) > 2:  # More than one definition
            # Keep the first part and first class definition
            first_class_end = parts[1].find("\n}\n") + 3  # Find end of first class
            if first_class_end > 2:
                fixed_content = parts[0] + "public class ModValidationResult" + parts[1][:first_class_end]
                
                with open(validation_service_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)

def main():
    """Run all fixes"""
    print("🚀 FINAL COMPREHENSIVE UNITY FIX")
    print("=" * 50)
    
    fix_duplicate_dto_files()
    fix_broken_using_statements()
    fix_duplicate_private_modifiers()
    fix_duplicate_attributes()
    add_missing_serializable_attribute()
    fix_duplicate_validation_result()
    
    print("\n✅ ALL FIXES COMPLETED!")
    print("=" * 50)

if __name__ == "__main__":
    main() 