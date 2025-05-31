#!/usr/bin/env python3
"""
Fix Remaining Namespace Issues Script
Addresses specific namespace patterns that weren't handled by the initial update
"""

import os
import re
from pathlib import Path
from typing import Dict, List

class RemainingNamespaceFixer:
    def __init__(self, vdm_root: str):
        self.vdm_root = Path(vdm_root)
        self.scripts_root = self.vdm_root / "Assets" / "Scripts"
        
        # Additional namespace mappings for remaining issues
        self.additional_mappings = self._create_additional_mappings()
        
    def _create_additional_mappings(self) -> Dict[str, str]:
        """Create mappings for the remaining namespace issues"""
        mappings = {}
        
        # Combat system mappings
        mappings['VDM.CombatSystem'] = 'VDM.Runtime.Combat'
        
        # Validation mappings
        mappings['VDM.Validation'] = 'VDM.Runtime.Core'
        
        # UI namespace mappings
        mappings['VDM.UI.Core'] = 'VDM.Runtime.UI.Core'
        mappings['VDM.UI.Framework'] = 'VDM.Runtime.UI.Framework'
        mappings['VDM.UI.Screens'] = 'VDM.Runtime.UI.Screens'
        mappings['VDM.UI.Components'] = 'VDM.Runtime.UI.Components'
        
        # System-specific model and service namespaces
        system_subdirs = ['Models', 'Services', 'Integration', 'UI']
        canonical_systems = [
            'Analytics', 'Arc', 'AuthUser', 'Character', 'Combat', 'Crafting', 'Data',
            'Dialogue', 'Diplomacy', 'Economy', 'Equipment', 'Events', 'Faction',
            'Inventory', 'Llm', 'Loot', 'Magic', 'Memory', 'Motif', 'Npc', 'Poi',
            'Population', 'Quest', 'Region', 'Religion', 'Rumor', 'Storage', 'Time',
            'WorldGeneration', 'WorldState'
        ]
        
        for system in canonical_systems:
            for subdir in system_subdirs:
                old_pattern = f"VDM.{system}.{subdir}"
                new_pattern = f"VDM.Runtime.{system}.{subdir}"
                mappings[old_pattern] = new_pattern
        
        # Core system mappings
        mappings['VDM.Core'] = 'VDM.Runtime.Core'
        mappings['VDM.Core.Events'] = 'VDM.Runtime.Events'
        mappings['VDM.Core.Utils'] = 'VDM.Runtime.Core'
        
        # Service mappings
        mappings['VDM.Services.HTTP'] = 'VDM.Runtime.Services'
        mappings['VDM.Services.WebSocket'] = 'VDM.Runtime.Services'
        mappings['VDM.Services.Mock'] = 'VDM.Runtime.Services.Mock'
        
        # Integration mappings
        mappings['VDM.Integration'] = 'VDM.Runtime.Integration'
        
        # Test mappings
        mappings['VDM.Tests.Net'] = 'VDM.Tests.Services'
        mappings['VDM.Tests.Integration'] = 'VDM.Tests.Integration'
        
        # Debug and utility mappings
        mappings['VDM.Debug'] = 'VDM.Runtime.Core'
        mappings['VDM.Utils'] = 'VDM.Runtime.Core'
        
        # Examples mappings
        mappings['VDM.Examples'] = 'VDM.Examples'
        mappings['VisualDM.Examples'] = 'VDM.Examples'
        mappings['VisualDM.Demo'] = 'VDM.Examples'
        
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
    
    def fix_file_namespaces(self, file_path: Path) -> bool:
        """Fix namespaces in a single C# file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Update namespace declarations
            for old_ns, new_ns in self.additional_mappings.items():
                # Match namespace declarations
                pattern = rf'^(\s*namespace\s+){re.escape(old_ns)}(\s*[{{;])'
                replacement = rf'\1{new_ns}\2'
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            # Update using statements
            for old_ns, new_ns in self.additional_mappings.items():
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
                print(f"Fixed: {file_path.relative_to(self.vdm_root)}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def validate_remaining_issues(self) -> List[str]:
        """Validate remaining namespace issues after fixes"""
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
            parts = namespace.split('.')
            if len(parts) >= 3:
                system_part = parts[2]
                return system_part in canonical_systems or system_part in unity_specific
        
        # Other allowed patterns
        allowed_patterns = [
            'VDM.DTOs', 'VDM.Tests', 'VDM.Core', 'VDM.Services',
            'VDM.Examples', 'VDM.Common'
        ]
        
        for pattern in allowed_patterns:
            if namespace.startswith(pattern):
                return True
        
        return False
    
    def fix_all_remaining_namespaces(self):
        """Execute the remaining namespace fixes"""
        print("Fixing remaining namespace issues...")
        print(f"Processing files in: {self.scripts_root}")
        
        cs_files = self.find_cs_files()
        print(f"Found {len(cs_files)} C# files")
        
        # Fix namespaces
        print("\nFixing namespace declarations and using statements...")
        fixed_count = 0
        
        for file_path in cs_files:
            if self.fix_file_namespaces(file_path):
                fixed_count += 1
        
        print(f"Fixed {fixed_count} files")
        
        # Validation
        print("\nValidating namespace consistency...")
        issues = self.validate_remaining_issues()
        
        if issues:
            print(f"Found {len(issues)} remaining namespace issues:")
            for issue in issues[:20]:  # Show first 20 issues
                print(f"  - {issue}")
            if len(issues) > 20:
                print(f"  ... and {len(issues) - 20} more")
        else:
            print("✓ All namespaces now follow canonical pattern")
        
        # Summary
        print(f"\n{'='*60}")
        print("REMAINING NAMESPACE FIX SUMMARY")
        print(f"{'='*60}")
        print(f"Files processed: {len(cs_files)}")
        print(f"Files fixed: {fixed_count}")
        print(f"Remaining issues: {len(issues)}")
        
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
        print("Usage: python fix_remaining_namespaces.py <VDM_ROOT_PATH>")
        sys.exit(1)
    
    vdm_root = sys.argv[1]
    
    if not os.path.exists(vdm_root):
        print(f"Error: VDM root path does not exist: {vdm_root}")
        sys.exit(1)
    
    fixer = RemainingNamespaceFixer(vdm_root)
    result = fixer.fix_all_remaining_namespaces()
    
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main() 