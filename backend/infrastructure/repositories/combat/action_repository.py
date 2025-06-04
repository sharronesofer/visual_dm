"""
Action Definition Repository Infrastructure Implementation

This module provides the infrastructure implementation for action definition management,
loading from JSON configuration and providing actions to the combat system.
"""

import json
import os
from typing import List, Dict, Set, Optional
from uuid import UUID

# Business domain imports
from backend.systems.combat.models import Combatant
from backend.systems.combat.models.combat_action import ActionDefinition, ActionType, ActionTarget, ActionCategory


class ActionDefinitionRepositoryImpl:
    """
    Infrastructure implementation of the ActionDefinitionRepository protocol.
    
    Loads action definitions from JSON configuration files and provides
    filtering based on combatant capabilities.
    """
    
    def __init__(self, data_path: str = "data/systems/combat"):
        self.data_path = data_path
        self._actions: Dict[str, ActionDefinition] = {}
        self._load_actions()
    
    def _load_actions(self) -> None:
        """Load action definitions from JSON files."""
        actions_file = os.path.join(self.data_path, "actions.json")
        
        if not os.path.exists(actions_file):
            # Create default actions if file doesn't exist
            self._create_default_actions()
            return
        
        try:
            with open(actions_file, 'r') as f:
                actions_data = json.load(f)
            
            # Parse action categories
            for category_name, actions in actions_data.items():
                for action_id, action_data in actions.items():
                    action_def = self._parse_action_definition(action_data)
                    self._actions[action_def.id] = action_def
                    
        except Exception as e:
            print(f"Error loading actions from {actions_file}: {e}")
            self._create_default_actions()
    
    def _parse_action_definition(self, data: Dict) -> ActionDefinition:
        """Parse action definition from JSON data."""
        # Map string values to enums
        action_type = ActionType(data["action_type"].lower())
        
        # Map target type (handle both old and new formats)
        target_type_str = data.get("target_type", "single_any").lower()
        if target_type_str == "single":
            target_type = ActionTarget.SINGLE_ANY
        elif target_type_str == "self":
            target_type = ActionTarget.SELF
        elif target_type_str == "area":
            target_type = ActionTarget.AREA
        else:
            try:
                target_type = ActionTarget(target_type_str)
            except ValueError:
                target_type = ActionTarget.SINGLE_ANY
        
        # Determine category from tags or action type
        category_map = {
            "attack": ActionCategory.ATTACK,
            "spell": ActionCategory.SPELL,
            "ability": ActionCategory.ABILITY,
            "item": ActionCategory.ITEM,
            "movement": ActionCategory.MOVEMENT,
            "defensive": ActionCategory.DEFENSE,
            "support": ActionCategory.UTILITY,
            "tactical": ActionCategory.UTILITY
        }
        
        tags = set(data.get("tags", []))
        category = ActionCategory.ABILITY  # default
        
        for tag in tags:
            if tag in category_map:
                category = category_map[tag]
                break
        
        # Parse requirements
        requirements = data.get("requirements", [])
        required_weapons = set()
        required_features = set()
        required_spells = set()
        
        for req in requirements:
            if "weapon" in req:
                required_weapons.add(req)
            elif "spell" in req or "class_" in req:
                if "spell_level" in req:
                    required_spells.add(req)
                else:
                    required_features.add(req)
            else:
                required_features.add(req)
        
        return ActionDefinition(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            action_type=action_type,
            target_type=target_type,
            category=category,
            required_weapon_types=required_weapons,
            required_class_features=required_features,
            required_spells=required_spells,
            range_feet=int(data.get("max_range", 5)),
            base_damage=data.get("base_damage", 0),
            damage_type=data.get("damage_type"),
            resource_cost=data.get("resource_cost", {}),
            cooldown_rounds=data.get("cooldown", 0),
            tags=tags
        )
    
    def _create_default_actions(self) -> None:
        """Create default action definitions if configuration is missing."""
        default_actions = [
            ActionDefinition(
                id="melee_attack",
                name="Melee Attack",
                description="Attack an adjacent enemy with a melee weapon",
                action_type=ActionType.STANDARD,
                target_type=ActionTarget.SINGLE_ENEMY,
                category=ActionCategory.ATTACK,
                range_feet=5,
                base_damage=4,
                damage_type="slashing",
                tags={"attack", "melee", "weapon"}
            ),
            ActionDefinition(
                id="ranged_attack", 
                name="Ranged Attack",
                description="Attack a distant enemy with a ranged weapon",
                action_type=ActionType.STANDARD,
                target_type=ActionTarget.SINGLE_ENEMY,
                category=ActionCategory.ATTACK,
                range_feet=150,
                base_damage=4,
                damage_type="piercing",
                required_weapon_types={"ranged_weapon"},
                tags={"attack", "ranged", "weapon"}
            ),
            ActionDefinition(
                id="cure_wounds",
                name="Cure Wounds",
                description="Heal a creature you touch",
                action_type=ActionType.STANDARD,
                target_type=ActionTarget.SINGLE_ANY,
                category=ActionCategory.SPELL,
                range_feet=5,
                base_damage=0,  # Healing spell
                required_spells={"cure_wounds"},
                resource_cost={"spell_slot_1": 1},
                tags={"spell", "healing", "touch"}
            ),
            ActionDefinition(
                id="magic_missile",
                name="Magic Missile",
                description="Three darts of magical force hit their target",
                action_type=ActionType.STANDARD,
                target_type=ActionTarget.SINGLE_ANY,
                category=ActionCategory.SPELL,
                range_feet=120,
                base_damage=3,  # 3 missiles at 1d4+1 each
                damage_type="force",
                required_spells={"magic_missile"},
                resource_cost={"spell_slot_1": 1},
                tags={"spell", "evocation", "ranged"}
            ),
            ActionDefinition(
                id="dash",
                name="Dash",
                description="Move up to double your speed",
                action_type=ActionType.STANDARD,
                target_type=ActionTarget.SELF,
                category=ActionCategory.MOVEMENT,
                tags={"movement"}
            ),
            ActionDefinition(
                id="dodge",
                name="Dodge", 
                description="Focus on avoiding attacks until your next turn",
                action_type=ActionType.STANDARD,
                target_type=ActionTarget.SELF,
                category=ActionCategory.DEFENSE,
                tags={"defensive"}
            ),
            ActionDefinition(
                id="help",
                name="Help",
                description="Grant advantage on an ally's next ability check or attack",
                action_type=ActionType.STANDARD,
                target_type=ActionTarget.SINGLE_ALLY,
                category=ActionCategory.UTILITY,
                range_feet=5,
                tags={"support"}
            ),
            ActionDefinition(
                id="opportunity_attack",
                name="Opportunity Attack",
                description="Attack an enemy that moves out of your reach",
                action_type=ActionType.REACTION,
                target_type=ActionTarget.SINGLE_ENEMY,
                category=ActionCategory.ATTACK,
                range_feet=5,
                base_damage=4,
                tags={"attack", "melee", "opportunity"}
            )
        ]
        
        for action in default_actions:
            self._actions[action.id] = action
    
    def get_action_by_id(self, action_id: str) -> Optional[ActionDefinition]:
        """Get action definition by ID."""
        return self._actions.get(action_id)
    
    def get_actions_for_combatant(self, combatant: Combatant) -> List[ActionDefinition]:
        """Get available actions for a combatant based on their capabilities."""
        available_actions = []
        
        for action in self._actions.values():
            if self._can_combatant_use_action(combatant, action):
                available_actions.append(action)
        
        return available_actions
    
    def list_all_actions(self) -> List[ActionDefinition]:
        """Get all action definitions."""
        return list(self._actions.values())
    
    def _can_combatant_use_action(self, combatant: Combatant, action: ActionDefinition) -> bool:
        """Check if a combatant meets the requirements to use an action."""
        # Check weapon requirements
        if action.required_weapon_types:
            combatant_weapons = set(combatant.equipped_weapons)
            if not action.required_weapon_types.intersection(combatant_weapons):
                return False
        
        # Check class feature requirements
        if action.required_class_features:
            combatant_features = set(combatant.class_features)
            if not action.required_class_features.issubset(combatant_features):
                return False
        
        # Check spell requirements
        if action.required_spells:
            combatant_spells = set(combatant.available_spells)
            if not action.required_spells.intersection(combatant_spells):
                return False
        
        return True
    
    def get_actions_by_category(self, category: ActionCategory) -> List[ActionDefinition]:
        """Get all actions of a specific category."""
        return [action for action in self._actions.values() if action.category == category]
    
    def get_actions_by_type(self, action_type: ActionType) -> List[ActionDefinition]:
        """Get all actions of a specific type."""
        return [action for action in self._actions.values() if action.action_type == action_type]
    
    def get_actions_with_tags(self, tags: Set[str]) -> List[ActionDefinition]:
        """Get all actions that have any of the specified tags."""
        matching_actions = []
        for action in self._actions.values():
            if action.tags.intersection(tags):
                matching_actions.append(action)
        return matching_actions
    
    def reload_actions(self) -> None:
        """Reload action definitions from JSON files."""
        self._actions.clear()
        self._load_actions()


def create_action_repository(data_path: str = "data/systems/combat") -> ActionDefinitionRepositoryImpl:
    """Factory function to create action definition repository."""
    return ActionDefinitionRepositoryImpl(data_path)


__all__ = ["ActionDefinitionRepositoryImpl", "create_action_repository"] 