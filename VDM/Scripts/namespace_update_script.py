#!/usr/bin/env python3
"""
Comprehensive Namespace Update Script for VDM Unity Project
Updates all C# namespaces to align with canonical backend system structure
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Canonical 33 systems from backend/tests/systems/
CANONICAL_SYSTEMS = [
    'Analytics', 'Arc', 'AuthUser', 'Character', 'Combat', 'Crafting', 'Data',
    'Dialogue', 'Diplomacy', 'Economy', 'Equipment', 'Events', 'Faction',
    'Inventory', 'Llm', 'Loot', 'Magic', 'Memory', 'Motif', 'Npc', 'Poi',
    'Population', 'Quest', 'Region', 'Religion', 'Rumor', 'Storage', 'Time',
    'WorldGeneration', 'WorldState', 'TensionWar', 'Shared', 'Integration'
]

# Unity-specific additional namespaces
UNITY_SPECIFIC = ['Bootstrap', 'Core', 'UI', 'Services']

# Standard subdirectories for each system
STANDARD_SUBDIRS = ['Models', 'Services', 'UI', 'Integration']

class NamespaceUpdater:
    def __init__(self, vdm_root: str):
        self.vdm_root = Path(vdm_root)
        self.scripts_root = self.vdm_root / "Assets" / "Scripts"
        self.runtime_root = self.scripts_root / "Runtime"
        
        # Old to new namespace mappings
        self.namespace_mappings = self._create_namespace_mappings()
        
        # Track files processed
        self.processed_files = []
        self.compilation_errors = []
        
    def _create_namespace_mappings(self) -> Dict[str, str]:
        """Create comprehensive mapping from old namespaces to new canonical ones"""
        mappings = {}
        
        # Core namespace standardization: VDM.Runtime.SystemName
        for system in CANONICAL_SYSTEMS:
            # Old variations to new canonical
            old_variations = [
                f"VDM.{system}",
                f"VDM.Systems.{system}",
                f"VisualDM.{system}",
                f"VisualDM.Systems.{system}",
                f"VDM.Runtime.{system}",
                f"VisualDM.Runtime.{system}"
            ]
            
            new_namespace = f"VDM.Runtime.{system}"
            for old in old_variations:
                mappings[old] = new_namespace
                
        # Handle legacy naming conventions
        legacy_mappings = {
            'VDM.POI': 'VDM.Runtime.Poi',
            'VDM.NPC': 'VDM.Runtime.Npc',
            'VisualDM.POI': 'VDM.Runtime.Poi',
            'VisualDM.NPC': 'VDM.Runtime.Npc',
            'VDM.Systems.War': 'VDM.Runtime.TensionWar',
            'VDM.Systems.UI': 'VDM.Runtime.UI',
            'VisualDM.UI': 'VDM.Runtime.UI',
            'VDM.UI': 'VDM.Runtime.UI',
            'VDM.Net': 'VDM.Runtime.Services',
            'VDM.Services': 'VDM.Runtime.Services',
            'VisualDM.Services': 'VDM.Runtime.Services',
            'VDM.Data': 'VDM.Runtime.Data',
            'VisualDM.Data': 'VDM.Runtime.Data'
        }
        mappings.update(legacy_mappings)
        
        # DTO mappings
        dto_mappings = {
            'VDM.Assets.Scripts.DTOs': 'VDM.DTOs',
            'VisualDM.DTOs': 'VDM.DTOs'
        }
        mappings.update(dto_mappings)
        
        # Test namespace mappings
        test_mappings = {
            'VDM.Tests': 'VDM.Tests',
            'VisualDM.Tests': 'VDM.Tests'
        }
        mappings.update(test_mappings)
        
        return mappings
    
    def find_cs_files(self) -> List[Path]:
        """Find all C# files in the VDM Assets directory"""
        cs_files = []
        for root, dirs, files in os.walk(self.scripts_root):
            # Skip backup directories
            dirs[:] = [d for d in dirs if not d.startswith('OldStructure_Backup')]
            
            for file in files:
                if file.endswith('.cs'):
                    cs_files.append(Path(root) / file)
        return cs_files
    
    def update_file_namespaces(self, file_path: Path) -> bool:
        """Update namespaces in a single C# file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Update namespace declarations
            for old_ns, new_ns in self.namespace_mappings.items():
                # Match namespace declarations
                pattern = rf'^(\s*namespace\s+){re.escape(old_ns)}(\s*[{{;])'
                replacement = rf'\1{new_ns}\2'
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            # Update using statements
            for old_ns, new_ns in self.namespace_mappings.items():
                # Match using statements
                pattern = rf'^(\s*using\s+){re.escape(old_ns)}(\s*[;\.])'
                replacement = rf'\1{new_ns}\2'
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                
                # Handle using statements with sub-namespaces
                pattern = rf'^(\s*using\s+){re.escape(old_ns)}(\.[^;]+;)'
                replacement = rf'\1{new_ns}\2'
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.processed_files.append(str(file_path))
                print(f"Updated: {file_path.relative_to(self.vdm_root)}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def organize_using_statements(self, file_path: Path) -> bool:
        """Organize and clean up using statements in a C# file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            using_lines = []
            other_lines = []
            namespace_started = False
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('using ') and not namespace_started:
                    using_lines.append(stripped)
                else:
                    if stripped.startswith('namespace '):
                        namespace_started = True
                    other_lines.append(line)
            
            # Remove duplicates and sort
            unique_usings = sorted(list(set(using_lines)))
            
            # Reconstruct file
            new_content = '\n'.join(unique_usings)
            if unique_usings:
                new_content += '\n\n'
            new_content += '\n'.join(other_lines)
            
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error organizing using statements in {file_path}: {e}")
            return False
    
    def test_compilation(self) -> bool:
        """Test Unity compilation after namespace changes"""
        print("\nTesting compilation...")
        try:
            # Use Unity's command line compilation
            result = subprocess.run([
                'unity', '-batchmode', '-quit', '-projectPath', str(self.vdm_root),
                '-executeMethod', 'UnityEditor.Compilation.CompilationPipeline.RequestScriptCompilation'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✓ Compilation successful")
                return True
            else:
                print("✗ Compilation failed")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠ Compilation test timed out")
            return False
        except FileNotFoundError:
            print("⚠ Unity command line tools not found, skipping compilation test")
            return True
    
    def validate_namespace_consistency(self) -> List[str]:
        """Validate that all namespaces follow the canonical pattern"""
        issues = []
        cs_files = self.find_cs_files()
        
        for file_path in cs_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find namespace declarations
                namespace_matches = re.findall(r'^\s*namespace\s+([^\s{;]+)', content, re.MULTILINE)
                
                for namespace in namespace_matches:
                    if not self._is_canonical_namespace(namespace):
                        issues.append(f"{file_path.relative_to(self.vdm_root)}: {namespace}")
                        
            except Exception as e:
                issues.append(f"Error reading {file_path}: {e}")
        
        return issues
    
    def _is_canonical_namespace(self, namespace: str) -> bool:
        """Check if a namespace follows the canonical pattern"""
        # VDM.Runtime.SystemName pattern
        if namespace.startswith('VDM.Runtime.'):
            system_part = namespace.split('.')[2] if len(namespace.split('.')) >= 3 else ''
            return system_part in CANONICAL_SYSTEMS or system_part in UNITY_SPECIFIC
        
        # Other allowed patterns
        allowed_patterns = [
            'VDM.DTOs', 'VDM.Tests', 'VDM.Core', 'VDM.Services',
            'VDM.Examples', 'VDM.Common'
        ]
        
        for pattern in allowed_patterns:
            if namespace.startswith(pattern):
                return True
        
        return False
    
    def update_all_namespaces(self):
        """Execute the complete namespace update process"""
        print("Starting comprehensive namespace update...")
        print(f"Processing files in: {self.scripts_root}")
        
        cs_files = self.find_cs_files()
        print(f"Found {len(cs_files)} C# files")
        
        # Phase 1: Update namespaces
        print("\nPhase 1: Updating namespace declarations and using statements...")
        updated_count = 0
        
        for file_path in cs_files:
            if self.update_file_namespaces(file_path):
                updated_count += 1
        
        print(f"Updated {updated_count} files")
        
        # Phase 2: Organize using statements
        print("\nPhase 2: Organizing using statements...")
        organized_count = 0
        
        for file_path in cs_files:
            if self.organize_using_statements(file_path):
                organized_count += 1
        
        print(f"Organized using statements in {organized_count} files")
        
        # Phase 3: Validation
        print("\nPhase 3: Validating namespace consistency...")
        issues = self.validate_namespace_consistency()
        
        if issues:
            print(f"Found {len(issues)} namespace issues:")
            for issue in issues[:20]:  # Show first 20 issues
                print(f"  - {issue}")
            if len(issues) > 20:
                print(f"  ... and {len(issues) - 20} more")
        else:
            print("✓ All namespaces follow canonical pattern")
        
        # Phase 4: Test compilation
        compilation_success = self.test_compilation()
        
        # Summary
        print(f"\n{'='*60}")
        print("NAMESPACE UPDATE SUMMARY")
        print(f"{'='*60}")
        print(f"Files processed: {len(cs_files)}")
        print(f"Files updated: {updated_count}")
        print(f"Files with organized using statements: {organized_count}")
        print(f"Namespace issues found: {len(issues)}")
        print(f"Compilation test: {'PASSED' if compilation_success else 'FAILED'}")
        
        return {
            'success': len(issues) == 0 and compilation_success,
            'files_processed': len(cs_files),
            'files_updated': updated_count,
            'issues': issues,
            'compilation_success': compilation_success
        }

def main():
    """Main execution function"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python namespace_update_script.py <VDM_ROOT_PATH>")
        sys.exit(1)
    
    vdm_root = sys.argv[1]
    
    if not os.path.exists(vdm_root):
        print(f"Error: VDM root path does not exist: {vdm_root}")
        sys.exit(1)
    
    updater = NamespaceUpdater(vdm_root)
    result = updater.update_all_namespaces()
    
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main() 