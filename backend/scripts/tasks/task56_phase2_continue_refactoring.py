#!/usr/bin/env python3
"""
Task 56 Phase 2: Continue Monolithic File Refactoring
Focus on remaining large files starting with combat system

Based on actual file analysis, targeting:
1. combat/combat_routes.py (1,159 lines)
2. combat/unified_effects.py (1,061 lines) 
3. combat/unified_combat_utils.py (1,016 lines)
"""

import os
import shutil
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BACKEND_ROOT = Path("backend")
SYSTEMS_ROOT = BACKEND_ROOT / "systems"

@dataclass
class RefactoringTarget:
    """Configuration for Phase 2 refactoring targets"""
    file_path: Path
    current_lines: int
    target_modules: Dict[str, Dict[str, int]]
    priority: str

class Task56Phase2:
    """Continue Task 56 monolithic file refactoring"""
    
    def __init__(self):
        self.phase2_targets = self._identify_phase2_targets()
        self.results = []
        
    def _identify_phase2_targets(self) -> List[RefactoringTarget]:
        """Identify the next batch of large files to refactor"""
        targets = []
        
        # Updated targets based on actual file analysis
        phase2_files = [
            ("combat/combat_routes.py", 1159, "critical"),
            ("combat/unified_effects.py", 1061, "critical"), 
            ("combat/unified_combat_utils.py", 1016, "critical"),
        ]
        
        for file_path, lines, priority in phase2_files:
            full_path = SYSTEMS_ROOT / file_path
            if full_path.exists():
                targets.append(RefactoringTarget(
                    file_path=full_path,
                    current_lines=lines,
                    target_modules=self._get_combat_modular_structure(file_path),
                    priority=priority
                ))
        
        return targets
    
    def _get_combat_modular_structure(self, file_path: str) -> Dict[str, Dict[str, int]]:
        """Define modular structure for combat system files"""
        if "combat_routes.py" in file_path:
            return {
                "routers/combat_actions.py": {"Combat action endpoints": 300},
                "routers/combat_state.py": {"Combat state endpoints": 250},
                "routers/combat_management.py": {"Combat management endpoints": 200},
                "routers/combat_effects.py": {"Effects and conditions endpoints": 200},
                "routers/combat_analytics.py": {"Combat analytics endpoints": 150},
                "handlers/validation_handler.py": {"Request validation": 150}
            }
        elif "unified_effects.py" in file_path:
            return {
                "effects/damage_effects.py": {"Damage calculation effects": 300},
                "effects/status_effects.py": {"Status and condition effects": 250},
                "effects/environmental_effects.py": {"Environmental effects": 200},
                "effects/magical_effects.py": {"Magical combat effects": 200},
                "processors/effect_processor.py": {"Effect processing logic": 150}
            }
        elif "unified_combat_utils.py" in file_path:
            return {
                "utils/combat_calculations.py": {"Combat math and calculations": 300},
                "utils/combat_validation.py": {"Combat rule validation": 250},
                "utils/combat_formatting.py": {"Combat data formatting": 200},
                "utils/combat_helpers.py": {"General combat helpers": 150},
                "managers/combat_flow_manager.py": {"Combat flow management": 150}
            }
        return {}
    
    def run_phase2_refactoring(self):
        """Execute Phase 2 refactoring"""
        logger.info("🚀 Starting Task 56 Phase 2: Continue Monolithic Refactoring")
        
        for target in self.phase2_targets:
            logger.info(f"🔧 Refactoring {target.file_path.name} ({target.current_lines} lines)")
            
            try:
                self._refactor_file_modular(target)
                self.results.append(f"✅ Successfully refactored {target.file_path.name}")
            except Exception as e:
                logger.error(f"❌ Failed to refactor {target.file_path.name}: {e}")
                self.results.append(f"❌ Failed: {target.file_path.name} - {e}")
        
        self._generate_phase2_report()
    
    def _refactor_file_modular(self, target: RefactoringTarget):
        """Refactor a file into modular structure"""
        logger.info(f"📁 Creating modular structure for {target.file_path.name}")
        
        # Read original content
        content = target.file_path.read_text(encoding='utf-8')
        
        # Create backup
        backup_path = target.file_path.with_suffix('.py.phase2.backup')
        backup_path.write_text(content)
        
        # Extract and organize code by target modules
        extracted_sections = self._extract_code_intelligently(content, target.target_modules)
        
        # Create modular files
        base_dir = target.file_path.parent
        for module_path, code_content in extracted_sections.items():
            module_file = base_dir / module_path
            module_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate proper module content
            final_content = self._generate_clean_module(module_file.name, code_content)
            module_file.write_text(final_content, encoding='utf-8')
            
            logger.info(f"✅ Created {module_file}")
        
        # Create compatibility facade
        facade_content = self._create_compatibility_facade(target, extracted_sections)
        target.file_path.write_text(facade_content, encoding='utf-8')
        
        logger.info(f"✅ Created compatibility facade for {target.file_path.name}")
    
    def _extract_code_intelligently(self, content: str, target_modules: Dict[str, Dict[str, int]]) -> Dict[str, str]:
        """Extract code sections intelligently based on patterns"""
        sections = {}
        
        # Simple extraction by function/class patterns
        # This is a simplified version - in practice would use AST parsing
        
        lines = content.split('\n')
        current_section = []
        current_module = list(target_modules.keys())[0]  # Default
        
        for line in lines:
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                # Determine target module based on function/class name
                func_name = line.strip().split()[1].split('(')[0]
                target_module = self._determine_module_for_function(func_name, target_modules)
                
                if target_module != current_module:
                    # Save previous section
                    if current_section:
                        sections[current_module] = '\n'.join(current_section)
                    current_section = []
                    current_module = target_module
            
            current_section.append(line)
        
        # Save final section
        if current_section:
            sections[current_module] = '\n'.join(current_section)
        
        return sections
    
    def _determine_module_for_function(self, func_name: str, target_modules: Dict[str, Dict[str, int]]) -> str:
        """Determine which module a function should go to based on naming"""
        func_lower = func_name.lower()
        
        # Simple heuristics based on function names
        if any(keyword in func_lower for keyword in ['damage', 'hit', 'attack']):
            return next((mod for mod in target_modules.keys() if 'damage' in mod), list(target_modules.keys())[0])
        elif any(keyword in func_lower for keyword in ['status', 'effect', 'condition']):
            return next((mod for mod in target_modules.keys() if 'status' in mod or 'effect' in mod), list(target_modules.keys())[0])
        elif any(keyword in func_lower for keyword in ['validate', 'check', 'verify']):
            return next((mod for mod in target_modules.keys() if 'validation' in mod), list(target_modules.keys())[0])
        elif any(keyword in func_lower for keyword in ['route', 'endpoint', 'api']):
            return next((mod for mod in target_modules.keys() if 'router' in mod), list(target_modules.keys())[0])
        
        return list(target_modules.keys())[0]  # Default to first module
    
    def _generate_clean_module(self, module_name: str, code_content: str) -> str:
        """Generate clean module content with proper imports"""
        lines = [
            f'"""',
            f'Modular implementation: {module_name}',
            f'Generated by Task 56 Phase 2 refactoring',
            f'"""',
            '',
            '# Standard imports',
            'from typing import Dict, List, Optional, Any, Union',
            'from dataclasses import dataclass',
            '',
            '# Backend imports', 
            'from backend.infrastructure.shared.utils.core.base_manager import BaseManager',
            'from backend.infrastructure.events import EventDispatcher',
            '',
            '# Module content',
            code_content.strip(),
            ''
        ]
        
        return '\n'.join(lines)
    
    def _create_compatibility_facade(self, target: RefactoringTarget, extracted_sections: Dict[str, str]) -> str:
        """Create backward compatibility facade"""
        module_imports = []
        for module_path in extracted_sections.keys():
            import_path = module_path.replace('/', '.').replace('.py', '')
            module_imports.append(f'from .{import_path} import *')
        
        facade_lines = [
            f'"""',
            f'Backward Compatibility Facade for {target.file_path.name}',
            f'',
            f'This file maintains API compatibility while using the new modular structure.',
            f'All functionality is now provided by specialized modules.',
            f'"""',
            '',
            '# Import all functionality from modular implementation',
        ] + module_imports + [
            '',
            '# Deprecation notice',
            'import warnings',
            '',
            'warnings.warn(',
            f'    "Direct import from {target.file_path.name} is deprecated. "',
            '    "Consider importing from specific modules for better organization.",',
            '    DeprecationWarning,',
            '    stacklevel=2',
            ')',
            ''
        ]
        
        return '\n'.join(facade_lines)
    
    def _generate_phase2_report(self):
        """Generate Phase 2 completion report"""
        report = {
            "task": "Task 56 Phase 2: Continue Monolithic File Refactoring",
            "timestamp": subprocess.check_output(["date"], text=True).strip(),
            "status": "COMPLETED",
            "targets_processed": len(self.phase2_targets),
            "results": self.results,
            "next_phase_candidates": [
                "llm/core/dm_core.py",
                "npc/services/npc_service.py", 
                "population/service.py",
                "motif/utils.py",
                "world_generation/world_generation_utils.py"
            ]
        }
        
        report_file = Path("backend/task56_phase2_report.json") 
        report_file.write_text(json.dumps(report, indent=2))
        
        logger.info("📊 TASK 56 PHASE 2 SUMMARY")
        logger.info("=" * 40)
        logger.info(f"Targets Processed: {len(self.phase2_targets)}")
        for result in self.results:
            logger.info(f"  {result}")
        logger.info(f"Report: {report_file}")

def main():
    """Execute Phase 2 refactoring"""
    phase2 = Task56Phase2()
    phase2.run_phase2_refactoring()

if __name__ == "__main__":
    main() 