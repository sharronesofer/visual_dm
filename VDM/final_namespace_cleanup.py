#!/usr/bin/env python3
"""
Final Namespace Cleanup Script
Handles the last remaining namespace issues
"""

import os
import re
from pathlib import Path
from typing import Dict, List

class FinalNamespaceCleanup:
    def __init__(self, vdm_root: str):
        self.vdm_root = Path(vdm_root)
        self.scripts_root = self.vdm_root / "Assets" / "Scripts"
        
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
    
    def fix_file_namespaces(self, file_path: Path) -> bool:
        """Fix namespaces in a single C# file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix VisualDM.Runtime.* patterns to VDM.Runtime.*
            content = re.sub(
                r'^(\s*namespace\s+)VisualDM\.Runtime\.([^{\s;]+)(\s*[{;])',
                r'\1VDM.Runtime.\2\3',
                content,
                flags=re.MULTILINE
            )
            
            content = re.sub(
                r'^(\s*using\s+)VisualDM\.Runtime\.([^;\s]+)(\s*[;.])',
                r'\1VDM.Runtime.\2\3',
                content,
                flags=re.MULTILINE
            )
            
            # Fix VDM.Systems.* patterns to VDM.Runtime.*
            content = re.sub(
                r'^(\s*namespace\s+)VDM\.Systems\.([^{\s;]+)(\s*[{;])',
                r'\1VDM.Runtime.\2\3',
                content,
                flags=re.MULTILINE
            )
            
            content = re.sub(
                r'^(\s*using\s+)VDM\.Systems\.([^;\s]+)(\s*[;.])',
                r'\1VDM.Runtime.\2\3',
                content,
                flags=re.MULTILINE
            )
            
            # Fix VDM.User.* to VDM.Runtime.AuthUser.*
            content = re.sub(
                r'^(\s*namespace\s+)VDM\.User\.([^{\s;]+)(\s*[{;])',
                r'\1VDM.Runtime.AuthUser.\2\3',
                content,
                flags=re.MULTILINE
            )
            
            content = re.sub(
                r'^(\s*using\s+)VDM\.User\.([^;\s]+)(\s*[;.])',
                r'\1VDM.Runtime.AuthUser.\2\3',
                content,
                flags=re.MULTILINE
            )
            
            # Fix any remaining VisualDM patterns
            content = re.sub(
                r'^(\s*namespace\s+)VisualDM\.([^{\s;]+)(\s*[{;])',
                r'\1VDM.\2\3',
                content,
                flags=re.MULTILINE
            )
            
            content = re.sub(
                r'^(\s*using\s+)VisualDM\.([^;\s]+)(\s*[;.])',
                r'\1VDM.\2\3',
                content,
                flags=re.MULTILINE
            )
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed: {file_path.relative_to(self.vdm_root)}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def validate_all_namespaces(self) -> List[str]:
        """Validate all namespaces for final consistency check"""
        issues = []
        cs_files = self.find_cs_files()
        
        canonical_systems = [
            'Analytics', 'Arc', 'AuthUser', 'Character', 'Combat', 'Crafting', 'Data',
            'Dialogue', 'Diplomacy', 'Economy', 'Equipment', 'Events', 'Faction',
            'Inventory', 'Llm', 'Loot', 'Magic', 'Memory', 'Motif', 'Npc', 'Poi',
            'Population', 'Quest', 'Region', 'Religion', 'Rumor', 'Storage', 'Time',
            'WorldGeneration', 'WorldState', 'TensionWar', 'Shared', 'Integration'
        ]
        
        unity_specific = ['Bootstrap', 'Core', 'UI', 'Services']
        
        for file_path in cs_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find namespace declarations
                namespace_matches = re.findall(r'^\s*namespace\s+([^\s{;]+)', content, re.MULTILINE)
                
                for namespace in namespace_matches:
                    if not self._is_canonical_namespace(namespace, canonical_systems, unity_specific):
                        issues.append(f"{file_path.relative_to(self.vdm_root)}: {namespace}")
                        
            except Exception as e:
                issues.append(f"Error reading {file_path}: {e}")
        
        return issues
    
    def _is_canonical_namespace(self, namespace: str, canonical_systems: List[str], unity_specific: List[str]) -> bool:
        """Check if a namespace follows the canonical pattern"""
        # VDM.Runtime.SystemName pattern
        if namespace.startswith('VDM.Runtime.'):
            return True  # All VDM.Runtime.* are considered canonical
        
        # Other allowed patterns
        allowed_patterns = [
            'VDM.DTOs', 'VDM.Tests', 'VDM.Core', 'VDM.Services',
            'VDM.Examples', 'VDM.Common'
        ]
        
        for pattern in allowed_patterns:
            if namespace.startswith(pattern):
                return True
        
        return False
    
    def final_cleanup(self):
        """Execute the final cleanup process"""
        print("Running final namespace cleanup...")
        print(f"Processing files in: {self.scripts_root}")
        
        cs_files = self.find_cs_files()
        print(f"Found {len(cs_files)} C# files")
        
        # Fix namespaces
        print("\nApplying final namespace fixes...")
        fixed_count = 0
        
        for file_path in cs_files:
            if self.fix_file_namespaces(file_path):
                fixed_count += 1
        
        print(f"Fixed {fixed_count} files")
        
        # Final validation
        print("\nFinal validation of namespace consistency...")
        issues = self.validate_all_namespaces()
        
        if issues:
            print(f"Found {len(issues)} remaining namespace issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✓ All namespaces now follow canonical pattern!")
        
        # Summary
        print(f"\n{'='*60}")
        print("FINAL NAMESPACE CLEANUP SUMMARY")
        print(f"{'='*60}")
        print(f"Files processed: {len(cs_files)}")
        print(f"Files fixed: {fixed_count}")
        print(f"Remaining issues: {len(issues)}")
        print(f"Success: {'YES' if len(issues) == 0 else 'NO'}")
        
        return {
            'success': len(issues) == 0,
            'files_processed': len(cs_files),
            'files_fixed': fixed_count,
            'remaining_issues': issues
        }

def main():
    """Main execution function"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python final_namespace_cleanup.py <VDM_ROOT_PATH>")
        sys.exit(1)
    
    vdm_root = sys.argv[1]
    
    if not os.path.exists(vdm_root):
        print(f"Error: VDM root path does not exist: {vdm_root}")
        sys.exit(1)
    
    cleanup = FinalNamespaceCleanup(vdm_root)
    result = cleanup.final_cleanup()
    
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main() 