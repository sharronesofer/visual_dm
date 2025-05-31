#!/usr/bin/env python3

import os
import re
import glob

def fix_using_statements():
    """Add missing using statements to files that need stub implementations"""
    print("🔧 Adding missing using statements...")
    
    # Files that need VisualDM.Systems using statements
    system_files = [
        "VDM/Assets/Scripts/Modules/Analytics/AnalyticsController.cs",
        "VDM/Assets/Scripts/Modules/Analytics/AnalyticsService.cs", 
        "VDM/Assets/Scripts/Modules/World/WeatherManager.cs",
        "VDM/Assets/Scripts/Modules/World/WorldTimeSystem.cs",
        "VDM/Assets/Scripts/Modules/Consolidated/LegacyCompatibility.cs",
        "VDM/Assets/Scripts/Runtime/Systems/Data/ModularDataSystem.cs"
    ]
    
    for file_path in system_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add missing using statements at the top
            using_statements = [
                "using VisualDM.Systems;",
                "using VisualDM.Data;", 
                "using VisualDM.Entities;",
                "using VisualDM.Systems.Core;"
            ]
            
            for using_stmt in using_statements:
                if using_stmt not in content:
                    # Find the first namespace or class declaration
                    lines = content.split('\n')
                    insert_index = 0
                    
                    # Find where to insert (after existing usings)
                    for i, line in enumerate(lines):
                        if line.strip().startswith('using '):
                            insert_index = i + 1
                        elif line.strip().startswith('namespace ') or line.strip().startswith('public class'):
                            break
                    
                    lines.insert(insert_index, using_stmt)
                    content = '\n'.join(lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  Added using statements to: {file_path}")

def fix_dto_references():
    """Fix DTO cross-references"""
    print("🔧 Fixing DTO cross-references...")
    
    dto_files = glob.glob("VDM/Assets/Scripts/DTOs/**/*.cs", recursive=True)
    
    for dto_file in dto_files:
        with open(dto_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove invalid using statements
        content = re.sub(r'using VDM\.Assets\.Scripts\.DTOs\.Core;\s*\n', '', content)
        
        # Add proper DTO using statement if not present
        if "using VisualDM.DTOs.Core.Shared;" not in content and "namespace VisualDM.DTOs" in content:
            lines = content.split('\n')
            # Insert after other using statements
            for i, line in enumerate(lines):
                if line.strip().startswith('namespace '):
                    lines.insert(i, "using VisualDM.DTOs.Core.Shared;")
                    lines.insert(i, "")
                    break
            content = '\n'.join(lines)
        
        with open(dto_file, 'w', encoding='utf-8') as f:
            f.write(content)

def fix_websocket_syntax_errors():
    """Fix syntax errors from WebSocket commenting"""
    print("🔧 Fixing WebSocket syntax errors...")
    
    websocket_files = [
        "VDM/Assets/Scripts/Runtime/Systems/Data/ModValidationClient.cs",
        "VDM/Assets/Scripts/Modules/Analytics/AnalyticsClient.cs",
        "VDM/Assets/Scripts/Modules/World/MapWebSocketClient.cs"
    ]
    
    for ws_file in websocket_files:
        if os.path.exists(ws_file):
            with open(ws_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix duplicate 'private' modifiers
            content = re.sub(r'private\s+private\s+', 'private ', content)
            
            # Fix incomplete WebSocket comments that are causing syntax errors
            content = re.sub(r'// WebSocketCloseCode\([^)]*$', '// WebSocketCloseCode.Normal', content, flags=re.MULTILINE)
            
            # Fix any incomplete commented lines
            lines = content.split('\n')
            fixed_lines = []
            
            for line in lines:
                # Fix lines that have incomplete comments causing syntax errors
                if '// WebSocketCloseCode' in line and '(' in line and ')' not in line:
                    line = '// ' + line.split('//')[1].split('(')[0].strip() + ' // Commented out for compilation'
                fixed_lines.append(line)
            
            content = '\n'.join(fixed_lines)
            
            with open(ws_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  Fixed syntax errors in: {ws_file}")

def fix_duplicate_definitions():
    """Remove duplicate type definitions"""
    print("🔧 Removing duplicate definitions...")
    
    # Check for duplicate CoordinateDTO
    coordinate_files = [
        "VDM/Assets/Scripts/DTOs/Core/Shared/CoordinateDTO.cs"
    ]
    
    for coord_file in coordinate_files:
        if os.path.exists(coord_file):
            with open(coord_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove duplicate [Serializable] attributes
            content = re.sub(r'\[Serializable\]\s*\n\s*\[Serializable\]', '[Serializable]', content)
            
            # Check if there are duplicate class definitions in the same file
            if content.count('public class CoordinateDTO') > 1:
                # Keep only the first definition
                parts = content.split('public class CoordinateDTO')
                if len(parts) > 2:
                    # Reconstruct with only first definition
                    content = parts[0] + 'public class CoordinateDTO' + parts[1]
                    # Find the end of the first class and truncate
                    brace_count = 0
                    in_class = False
                    lines = content.split('\n')
                    result_lines = []
                    
                    for line in lines:
                        if 'public class CoordinateDTO' in line:
                            in_class = True
                        
                        if in_class:
                            result_lines.append(line)
                            brace_count += line.count('{') - line.count('}')
                            if brace_count == 0 and '{' in line:
                                # End of class definition
                                break
                        else:
                            result_lines.append(line)
                    
                    content = '\n'.join(result_lines)
            
            with open(coord_file, 'w', encoding='utf-8') as f:
                f.write(content)

def create_missing_dto_implementations():
    """Create complete DTO implementations"""
    print("🔧 Creating missing DTO implementations...")
    
    dto_dir = "VDM/Assets/Scripts/DTOs/Core/Shared"
    os.makedirs(dto_dir, exist_ok=True)
    
    # Create MetadataDTO
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
        public string Description { get; set; } = "";
        public string[] Tags { get; set; } = new string[0];
    }
}"""
    
    # Create SuccessResponseDTO
    success_response_dto = """using System;
using UnityEngine;

namespace VisualDM.DTOs.Core.Shared
{
    [Serializable]
    public class SuccessResponseDTO
    {
        public bool Success { get; set; } = true;
        public string Message { get; set; } = "Operation completed successfully";
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        public object Data { get; set; }
    }
}"""
    
    # Write the files
    with open(f"{dto_dir}/MetadataDTO.cs", 'w') as f:
        f.write(metadata_dto)
    
    with open(f"{dto_dir}/SuccessResponseDTO.cs", 'w') as f:
        f.write(success_response_dto)
    
    print("✅ Created MetadataDTO and SuccessResponseDTO")

def main():
    print("🚀 ULTIMATE FINAL FIX - RESOLVING ALL REMAINING ISSUES")
    print("=" * 60)
    
    fix_using_statements()
    fix_dto_references()
    fix_websocket_syntax_errors()
    fix_duplicate_definitions()
    create_missing_dto_implementations()
    
    print("=" * 60)
    print("✅ ULTIMATE FINAL FIX COMPLETE!")
    print("")
    print("📝 FINAL FIXES APPLIED:")
    print("1. ✅ Added missing using statements for stub implementations")
    print("2. ✅ Fixed DTO cross-references and imports")
    print("3. ✅ Fixed WebSocket syntax errors (duplicate modifiers)")
    print("4. ✅ Removed duplicate type definitions")
    print("5. ✅ Created complete missing DTO implementations")
    print("")
    print("🎯 Unity should now compile with minimal errors!")
    print("📊 Remaining issues should be mostly warnings, not blocking errors")

if __name__ == "__main__":
    main() 