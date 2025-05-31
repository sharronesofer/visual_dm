#!/usr/bin/env python3
"""
Task 55: Integration Script for Modular Extraction

This script updates the original combat_class.py to use the extracted modular components,
ensuring backward compatibility while leveraging the new modular architecture.

Phase 1b: Combat System Integration
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any

class ModularIntegrator:
    """Integrate extracted modules back into the main combat system."""
    
    def __init__(self, backend_path: str = None):
        if backend_path:
            self.backend_path = Path(backend_path)
        else:
            self.backend_path = Path.cwd()
        self.systems_path = self.backend_path / "systems"
        
    def integrate_combat_system(self):
        """Integrate extracted modules into combat_class.py."""
        print("🔗 Phase 1b: Integrating Combat System Modules")
        
        combat_file = self.systems_path / "combat" / "combat_class.py"
        if not combat_file.exists():
            print(f"❌ Combat file not found: {combat_file}")
            return
            
        # Create backup
        backup_file = combat_file.with_suffix('.py.backup')
        if not backup_file.exists():
            backup_file.write_text(combat_file.read_text())
            print(f"📁 Created backup: {backup_file}")
        
        # Read current content
        content = combat_file.read_text()
        
        # Add imports for extracted modules
        updated_content = self._add_modular_imports(content)
        
        # Initialize extracted modules in Combat.__init__
        updated_content = self._initialize_modules(updated_content)
        
        # Replace extracted method calls with module calls
        updated_content = self._replace_method_calls(updated_content)
        
        # Write updated content
        combat_file.write_text(updated_content)
        print("✅ Combat system integration complete")
        
    def _add_modular_imports(self, content: str) -> str:
        """Add imports for the extracted modules."""
        
        # Find the existing imports section
        import_pattern = r'(from backend\.systems\.events import.*?)\n'
        
        # New modular imports
        modular_imports = """
# Import extracted modular components
from backend.systems.combat.calculators.initiative_calculator import InitiativeCalculator
from backend.systems.combat.calculators.damage_calculator import DamageCalculator
from backend.systems.combat.services.state_service import StateService
from backend.systems.combat.services.damage_service import DamageService
from backend.systems.combat.repositories.combat_serializer import CombatSerializer
from backend.systems.combat.utils.perception_utils import PerceptionUtils
"""
        
        # Add modular imports after existing imports
        match = re.search(import_pattern, content)
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + modular_imports + content[insert_pos:]
        else:
            # Fallback: add after logger setup
            logger_pattern = r'(logger = logging\.getLogger\(__name__\))\n'
            match = re.search(logger_pattern, content)
            if match:
                insert_pos = match.end()
                content = content[:insert_pos] + modular_imports + content[insert_pos:]
        
        return content
        
    def _initialize_modules(self, content: str) -> str:
        """Initialize the extracted modules in Combat.__init__."""
        
        # Find Combat.__init__ method
        init_pattern = r'(def __init__\(self[^)]*\):.*?)(self\.debug_mode = False)'
        
        # Module initialization code
        module_init = """
        
        # Initialize extracted modular components
        self.initiative_calculator = InitiativeCalculator()
        self.damage_calculator = DamageCalculator()
        self.state_service = StateService(self.combat_state)
        self.damage_service = DamageService()
        self.combat_serializer = CombatSerializer()
        self.perception_utils = PerceptionUtils()"""
        
        # Add module initialization
        match = re.search(init_pattern, content, re.DOTALL)
        if match:
            replacement = match.group(1) + match.group(2) + module_init
            content = content.replace(match.group(0), replacement)
        
        return content
        
    def _replace_method_calls(self, content: str) -> str:
        """Replace direct method calls with module calls."""
        
        # Define method mappings
        method_mappings = {
            # Initiative calculations
            'self._calculate_initiative(': 'self.initiative_calculator.calculate_initiative(',
            'self._calculate_initiative_for_character(': 'self.initiative_calculator.calculate_initiative_for_character(',
            
            # State management
            'self.pause_combat()': 'self.state_service.pause_combat(self.combat_state)',
            'self.resume_combat()': 'self.state_service.resume_combat(self.combat_state)',
            'self.handle_state_transition(': 'self.state_service.handle_state_transition(self.combat_state, ',
            'self.get_state_history()': 'self.state_service.get_state_history(self.combat_state)',
            'self.undo_last_action()': 'self.state_service.undo_last_action(self.combat_state)',
            
            # Damage and effects
            'self.apply_effect(': 'self.damage_service.apply_effect(self.combat_state, self.effect_pipeline, ',
            'self.remove_effect(': 'self.damage_service.remove_effect(self.combat_state, self.effect_pipeline, ',
            'self.apply_damage(': 'self.damage_service.apply_damage(self.combat_state, self.effect_pipeline, ',
            'self.apply_healing(': 'self.damage_service.apply_healing(self.combat_state, self.effect_pipeline, ',
            'self.handle_status_effects(': 'self.damage_service.handle_status_effects(self.combat_state, self.effect_pipeline, ',
            
            # Serialization
            'self.serialize()': 'self.combat_serializer.serialize(self.combat_state)',
            'self.deserialize(': 'self.combat_serializer.deserialize(self.combat_state, ',
            'self.to_json()': 'self.combat_serializer.to_json(self.combat_state)',
            'self.from_json(': 'self.combat_serializer.from_json(self.combat_state, ',
            'self.save_to_file(': 'self.combat_serializer.save_to_file(self.combat_state, ',
            'self.load_from_file(': 'self.combat_serializer.load_from_file(self.combat_state, ',
            
            # Perception
            'self.get_visible_entities(': 'self.perception_utils.get_visible_entities(',
            'self.execute_perception_check(': 'self.perception_utils.execute_perception_check(',
        }
        
        # Apply replacements
        for old_call, new_call in method_mappings.items():
            content = content.replace(old_call, new_call)
        
        return content

def main():
    """Main integration function."""
    print("🚀 Starting Task 55: Modular Integration - Phase 1b")
    print("="*60)
    
    integrator = ModularIntegrator()
    integrator.integrate_combat_system()
    
    print("="*60)
    print("🎉 Task 55 Phase 1b Complete!")
    print("Next steps:")
    print("1. Test integration functionality")
    print("2. Run comprehensive unit tests")
    print("3. Proceed to Phase 2 (other systems)")

if __name__ == "__main__":
    main() 