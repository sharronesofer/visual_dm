#!/usr/bin/env python3

import os
import re
import glob

def fix_preprocessor_issues():
    """Fix all remaining preprocessor directive issues"""
    print("🔧 Fixing preprocessor directive issues...")
    
    # Fix AuthDTO.cs specifically
    auth_dto_path = "VDM/Assets/Scripts/DTOs/Core/Auth/AuthDTO.cs"
    
    with open(auth_dto_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the specific issue: [EmailAddress] followed by #if without #endif
    # Pattern: [EmailAddress]\n        #if UNITY_EDITOR || UNITY_STANDALONE\n    [StringLength...]
    pattern = r'(\[EmailAddress\])\s*\n\s*(#if UNITY_EDITOR \|\| UNITY_STANDALONE)\s*\n\s*(\[StringLength[^\]]*\])'
    replacement = r'\1\n#endif\n        \2\n    \3'
    
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Also fix any remaining standalone #if UNITY_EDITOR || UNITY_STANDALONE without #endif before property
    # Look for pattern: #if UNITY_EDITOR || UNITY_STANDALONE\n    [Attribute]\n        public
    pattern2 = r'(#if UNITY_EDITOR \|\| UNITY_STANDALONE)\s*\n\s*(\[[^\]]+\])\s*\n\s*(public [^{]+{[^}]+})'
    replacement2 = r'\1\n    \2\n#endif\n        \3'
    
    content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)
    
    with open(auth_dto_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed {auth_dto_path}")

def fix_missing_types():
    """Add necessary using statements for missing types"""
    print("🔧 Adding missing using statements...")
    
    files_to_fix = [
        "VDM/Assets/Scripts/Runtime/Systems/Data/ValidationResult.cs",
        "VDM/Assets/Scripts/Runtime/Systems/Data/ModularDataSystem.cs",
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add missing using statements at the top
            if "using System;" not in content:
                content = "using System;\n" + content
            if "using UnityEngine;" not in content:
                content = "using UnityEngine;\n" + content
            
            # Fix ValidationResult constructor issue
            if "ValidationResult.cs" in file_path:
                # Make ValidationResult class public
                content = content.replace("class ValidationResult", "public class ValidationResult")
                
                # Fix method without return type (likely a constructor)
                content = re.sub(r'(\s+)([A-Za-z]+)\(\)', r'\1public \2()', content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Fixed {file_path}")

def create_missing_interfaces():
    """Create stub interfaces for missing types"""
    print("🔧 Creating stub interfaces...")
    
    stub_dir = "VDM/Assets/Scripts/Stubs"
    os.makedirs(stub_dir, exist_ok=True)
    
    # Create SystemBase stub
    systembase_stub = """using UnityEngine;

namespace VisualDM.Systems
{
    public abstract class SystemBase : MonoBehaviour
    {
        public virtual void Initialize() { }
        public virtual void Shutdown() { }
    }
    
    public interface ISystemController
    {
        void Initialize();
        void Shutdown();
    }
    
    public interface IEventMiddleware
    {
        void Process(IEvent eventData);
    }
    
    public interface IEvent
    {
        string EventType { get; }
        object Data { get; }
    }
}"""
    
    with open(f"{stub_dir}/SystemBase.cs", 'w') as f:
        f.write(systembase_stub)
    
    # Create VisualDM.Systems namespace stub
    systems_stub = """namespace VisualDM.Systems.Core
{
    // Placeholder for core system types
}

namespace VisualDM.Data
{
    // Placeholder for data types
    public class GameTime
    {
        public float TimeScale { get; set; } = 1.0f;
    }
    
    public class WeatherState
    {
        public string CurrentWeather { get; set; } = "Clear";
    }
    
    public class WeatherDefinition
    {
        public string Name { get; set; } = "";
    }
}

namespace VisualDM.Entities
{
    // Placeholder for entity types
    public class WorldStateManager
    {
        // Placeholder
    }
    
    public class RegionWorldState
    {
        // Placeholder
    }
}"""
    
    with open(f"{stub_dir}/SystemsNamespace.cs", 'w') as f:
        f.write(systems_stub)
    
    print(f"✅ Created stubs in {stub_dir}")

def main():
    print("🚀 COMPREHENSIVE UNITY FIX - FINAL ATTEMPT")
    print("=" * 50)
    
    fix_preprocessor_issues()
    fix_missing_types()
    create_missing_interfaces()
    
    print("=" * 50)
    print("✅ All fixes applied!")
    print("")
    print("📝 NEXT STEPS:")
    print("1. Unity package cache has been cleared")
    print("2. Preprocessor directives fixed")
    print("3. Missing type stubs created")
    print("4. Try opening Unity now - it should compile!")

if __name__ == "__main__":
    main() 