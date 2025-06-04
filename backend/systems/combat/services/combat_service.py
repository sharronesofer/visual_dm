"""
Combat Service - Pure Business Logic

This module provides business logic services for the combat system
according to the Development Bible standards.
"""

from typing import Optional, List, Dict, Any, Tuple, Protocol
from uuid import UUID, uuid4
from datetime import datetime

# Business domain models
from ..models import CombatEncounter, Combatant, CombatAction, StatusEffect
from ..models.combat_action import ActionDefinition, ActionResult, CombatantActionState


# Business Logic Protocols (dependency injection interfaces)
class CombatRepository(Protocol):
    """Protocol for combat data access"""
    
    def create_encounter(self, encounter: CombatEncounter) -> CombatEncounter:
        """Create a new combat encounter"""
        ...
    
    def get_encounter_by_id(self, encounter_id: UUID) -> Optional[CombatEncounter]:
        """Get encounter by ID"""
        ...
    
    def update_encounter(self, encounter: CombatEncounter) -> CombatEncounter:
        """Update existing encounter"""
        ...
    
    def delete_encounter(self, encounter_id: UUID) -> bool:
        """Delete encounter"""
        ...
    
    def list_encounters(self, 
                       page: int = 1, 
                       size: int = 50, 
                       status: Optional[str] = None) -> Tuple[List[CombatEncounter], int]:
        """List encounters with pagination"""
        ...


class ActionDefinitionRepository(Protocol):
    """Protocol for action definition data access"""
    
    def get_action_by_id(self, action_id: str) -> Optional[ActionDefinition]:
        """Get action definition by ID"""
        ...
    
    def get_actions_for_combatant(self, combatant: Combatant) -> List[ActionDefinition]:
        """Get available actions for a combatant"""
        ...
    
    def list_all_actions(self) -> List[ActionDefinition]:
        """Get all action definitions"""
        ...


class DiceRollingService(Protocol):
    """Protocol for dice rolling and randomization"""
    
    def roll_d20(self) -> int:
        """Roll a d20"""
        ...
    
    def roll_dice(self, count: int, sides: int) -> List[int]:
        """Roll multiple dice"""
        ...
    
    def roll_damage(self, damage_expr: str) -> int:
        """Roll damage from expression like '2d6+3'"""
        ...


class ActionResult:
    """Result data from executing a combat action."""
    
    def __init__(self):
        self.success: bool = False
        self.message: str = ""
        self.damage_dealt: int = 0
        self.healing_applied: int = 0
        self.targets_affected: List[UUID] = []
        self.status_effects_applied: List[str] = []
        self.additional_data: Dict[str, Any] = {}


class CombatService:
    """Service class for combat business logic - pure business rules"""
    
    def __init__(self,
                 combat_repository: CombatRepository,
                 action_repository: ActionDefinitionRepository,
                 dice_service: DiceRollingService):
        self.combat_repository = combat_repository
        self.action_repository = action_repository
        self.dice_service = dice_service
    
    def create_encounter(self, 
                        name: str, 
                        description: Optional[str] = None,
                        properties: Optional[Dict[str, Any]] = None) -> CombatEncounter:
        """Create a new combat encounter with business validation."""
        # Business rule: Name is required and must be unique (for active encounters)
        if not name or not name.strip():
            raise ValueError("Encounter name is required")
        
        encounter = CombatEncounter(
            name=name.strip(),
            description=description,
            properties=properties or {}
        )
        
        return self.combat_repository.create_encounter(encounter)
    
    def add_combatant_to_encounter(self, 
                                 encounter_id: UUID, 
                                 combatant: Combatant) -> CombatEncounter:
        """Add a combatant to an existing encounter with business rules."""
        encounter = self.combat_repository.get_encounter_by_id(encounter_id)
        if not encounter:
            raise ValueError(f"Encounter {encounter_id} not found")
        
        # Business rule: Cannot add combatants to completed encounters
        if encounter.status in ["completed", "aborted"]:
            raise ValueError(f"Cannot add combatants to {encounter.status} encounter")
        
        # Business rule: Combatant names must be unique within encounter
        existing_names = [p.name for p in encounter.participants]
        if combatant.name in existing_names:
            raise ValueError(f"Combatant name '{combatant.name}' already exists in encounter")
        
        encounter.add_participant(combatant)
        return self.combat_repository.update_encounter(encounter)
    
    def remove_combatant_from_encounter(self, 
                                      encounter_id: UUID, 
                                      combatant_id: UUID) -> CombatEncounter:
        """Remove a combatant from an encounter with business rules."""
        encounter = self.combat_repository.get_encounter_by_id(encounter_id)
        if not encounter:
            raise ValueError(f"Encounter {encounter_id} not found")
        
        combatant = next((p for p in encounter.participants if p.id == combatant_id), None)
        if not combatant:
            raise ValueError(f"Combatant {combatant_id} not found in encounter")
        
        # Business rule: Cannot remove combatants during active combat
        if encounter.status == "active":
            # Mark as inactive instead of removing
            combatant.is_active = False
            encounter.log_event(f"{combatant.name} removed from combat")
        else:
            encounter.remove_participant(combatant)
        
        return self.combat_repository.update_encounter(encounter)
    
    def set_initiative_order(self, 
                           encounter_id: UUID, 
                           initiative_rolls: Dict[UUID, int]) -> CombatEncounter:
        """Set initiative order for combat with business rules."""
        encounter = self.combat_repository.get_encounter_by_id(encounter_id)
        if not encounter:
            raise ValueError(f"Encounter {encounter_id} not found")
        
        # Business rule: Can only set initiative for pending encounters
        if encounter.status != "pending":
            raise ValueError(f"Cannot set initiative for {encounter.status} encounter")
        
        # Business rule: All participants must have initiative rolls
        participant_ids = {p.id for p in encounter.participants}
        provided_ids = set(initiative_rolls.keys())
        
        if participant_ids != provided_ids:
            missing = participant_ids - provided_ids
            extra = provided_ids - participant_ids
            errors = []
            if missing:
                errors.append(f"Missing initiative for: {missing}")
            if extra:
                errors.append(f"Extra initiative for: {extra}")
            raise ValueError("; ".join(errors))
        
        # Sort participants by initiative (highest first, break ties with dex modifier)
        sorted_participants = sorted(
            encounter.participants,
            key=lambda p: (initiative_rolls[p.id], p.dex_modifier),
            reverse=True
        )
        
        # Set initiative values on combatants and order
        for participant in encounter.participants:
            participant.initiative = initiative_rolls[participant.id]
        
        encounter.set_initiative_order(sorted_participants)
        encounter.log_event("Initiative order set", {
            "order": [{"name": p.name, "initiative": p.initiative} for p in sorted_participants]
        })
        
        return self.combat_repository.update_encounter(encounter)
    
    def start_combat(self, encounter_id: UUID) -> CombatEncounter:
        """Start combat with business validation."""
        encounter = self.combat_repository.get_encounter_by_id(encounter_id)
        if not encounter:
            raise ValueError(f"Encounter {encounter_id} not found")
        
        # Business rules are enforced by the domain model
        encounter.start_combat()
        
        # Reset all combatants' action economy for first turn
        for participant in encounter.participants:
            participant.reset_action_economy()
        
        return self.combat_repository.update_encounter(encounter)
    
    def end_combat(self, encounter_id: UUID, reason: str = "completed") -> CombatEncounter:
        """End combat with business validation."""
        encounter = self.combat_repository.get_encounter_by_id(encounter_id)
        if not encounter:
            raise ValueError(f"Encounter {encounter_id} not found")
        
        encounter.end_combat(reason)
        return self.combat_repository.update_encounter(encounter)
    
    def advance_turn(self, encounter_id: UUID) -> CombatEncounter:
        """Advance to the next turn with business logic."""
        encounter = self.combat_repository.get_encounter_by_id(encounter_id)
        if not encounter:
            raise ValueError(f"Encounter {encounter_id} not found")
        
        # Business rule: Can only advance turns in active combat
        if encounter.status != "active":
            raise ValueError(f"Cannot advance turn in {encounter.status} encounter")
        
        current_participant = encounter.get_current_participant()
        if current_participant:
            # Process end-of-turn effects for current participant
            self._process_end_of_turn_effects(current_participant, encounter)
        
        new_round_started = not encounter.advance_turn()
        
        # If new round started, process round-based effects
        if new_round_started:
            self._process_start_of_round_effects(encounter)
        
        # Process start-of-turn effects for new current participant
        next_participant = encounter.get_current_participant()
        if next_participant:
            next_participant.reset_action_economy()
            self._process_start_of_turn_effects(next_participant, encounter)
        
        # Check if combat should end
        if encounter.is_combat_over():
            encounter.end_combat("victory_condition_met")
            encounter.log_event("Combat ended due to victory conditions")
        
        return self.combat_repository.update_encounter(encounter)
    
    def execute_action(
        self, 
        encounter_id: UUID, 
        actor_id: UUID, 
        action_id: str, 
        target_ids: List[UUID], 
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[CombatEncounter, "ActionResult"]:
        """Execute an action in combat with comprehensive business logic."""
        # Get encounter and validate
        encounter = self.combat_repository.get_encounter_by_id(encounter_id)
        if not encounter:
            raise ValueError(f"Encounter {encounter_id} not found")
        
        if encounter.status != "active":
            raise ValueError("Cannot execute actions in inactive encounter")
        
        # Get actor
        actor = next((p for p in encounter.participants if p.id == actor_id), None)
        if not actor:
            raise ValueError(f"Actor {actor_id} not found in encounter")
        
        # Get action definition
        action = self.action_repository.get_action_by_id(action_id)
        if not action:
            raise ValueError(f"Action {action_id} not found")
        
        # Validate action usage
        validation_errors = self.validate_action_usage(actor, action)
        if validation_errors:
            raise ValueError(f"Action validation failed: {'; '.join(validation_errors)}")
        
        # Get targets
        targets = []
        for target_id in target_ids:
            target = next((p for p in encounter.participants if p.id == target_id), None)
            if target:
                targets.append(target)
        
        # Execute action based on category
        action_result = ActionResult()
        
        if action.category.value == "attack":
            # Handle attack actions
            if not targets:
                raise ValueError("Attack actions require at least one target")
            
            target = targets[0]  # Single target for now
            
            # Use new damage calculation method
            attack_data = additional_data or {}
            advantage = attack_data.get("advantage", False)
            disadvantage = attack_data.get("disadvantage", False)
            
            damage_result = self.calculate_damage_and_apply_attack(
                actor, target, action, None, advantage, disadvantage
            )
            
            action_result.success = damage_result["hit"]
            action_result.damage_dealt = damage_result["damage"]
            action_result.message = damage_result["message"]
            action_result.targets_affected = [target.id]
            action_result.additional_data = {
                "attack_roll": damage_result["attack_roll"],
                "critical": damage_result["critical"],
                "target_ac": damage_result["target_ac"]
            }
            
        elif action.category.value == "spell":
            # Handle spell actions
            if action.id == "cure_wounds":
                if targets:
                    target = targets[0]
                    healing_amount = self.dice_service.roll_damage("1d8+3")
                    healing_result = self.apply_healing(target, healing_amount)
                    
                    action_result.success = True
                    action_result.healing_applied = healing_result["healing_applied"]
                    action_result.message = healing_result["message"]
                    action_result.targets_affected = [target.id]
            else:
                # Generic spell handling
                action_result.success = True
                action_result.message = f"{actor.name} casts {action.name}"
                
        elif action.category.value == "utility":
            # Handle utility actions
            if action.id == "dash":
                # Double movement for this turn
                actor.remaining_movement *= 2
                action_result.success = True
                action_result.message = f"{actor.name} dashes (movement doubled)"
                
            elif action.id == "dodge":
                # Apply dodge status effect (simplified)
                action_result.success = True
                action_result.message = f"{actor.name} takes the dodge action"
                
        else:
            # Default action handling
            action_result.success = True
            action_result.message = f"{actor.name} uses {action.name}"
        
        # Update action economy
        if action.action_type.value == "standard":
            actor.has_used_standard_action = True
        elif action.action_type.value == "bonus":
            actor.has_used_bonus_action = True
        elif action.action_type.value == "reaction":
            actor.has_used_reaction = True
        
        # Create action record
        combat_action = CombatAction(
            id=uuid4(),
            action_id=action.id,
            action_name=action.name,
            actor_id=actor.id,
            actor_name=actor.name,
            action_type=action.action_type,
            category=action.category,
            encounter_id=encounter.id,
            round_number=encounter.round_number,
            turn_number=encounter.current_turn,
            target_ids=target_ids,
            target_name=", ".join([t.name for t in targets]) if targets else None,
            success=action_result.success,
            total_damage=action_result.damage_dealt,
            damage_type=action.damage_type,
            healing_applied=action_result.healing_applied,
            description=action_result.message,
            execution_data=action_result.additional_data or {}
        )
        
        # Add to encounter records
        encounter.actions_taken.append(combat_action)
        encounter.combat_log.append(f"Round {encounter.round_number}: {action_result.message}")
        
        # Check for encounter end conditions
        end_reason = self.check_encounter_end_conditions(encounter)
        if end_reason:
            encounter.status = "completed"
            encounter.ended_at = datetime.utcnow()
            encounter.combat_log.append(f"Combat ended: {end_reason}")
        
        # Save encounter
        updated_encounter = self.combat_repository.update_encounter(encounter)
        
        return updated_encounter, action_result
    
    def _can_actor_use_action(self, actor: Combatant, action_def: ActionDefinition) -> bool:
        """Check if actor meets requirements to use an action."""
        # Check if actor is active and conscious
        if not actor.is_active or not actor.is_conscious:
            return False
        
        # Check action economy
        if not actor.can_take_action(action_def.action_type.value):
            return False
        
        # Check equipment requirements
        if action_def.required_weapon_types:
            actor_weapons = set(actor.equipped_weapons)
            if not action_def.required_weapon_types.intersection(actor_weapons):
                return False
        
        # Check class features
        if action_def.required_class_features:
            actor_features = set(actor.class_features)
            if not action_def.required_class_features.issubset(actor_features):
                return False
        
        # Check spell requirements
        if action_def.required_spells:
            actor_spells = set(actor.available_spells)
            if not action_def.required_spells.intersection(actor_spells):
                return False
        
        return True
    
    def _validate_action_targets(self, action_def: ActionDefinition, actor: Combatant, targets: List[Combatant]) -> bool:
        """Validate that targets are appropriate for the action."""
        target_type = action_def.target_type.value
        
        if target_type == "no_target":
            return len(targets) == 0
        
        if target_type == "self":
            return len(targets) == 1 and targets[0].id == actor.id
        
        if target_type in ["single_ally", "single_enemy", "single_any"]:
            if len(targets) != 1:
                return False
            
            target = targets[0]
            if target_type == "single_ally":
                return actor.is_ally_of(target)
            elif target_type == "single_enemy":
                return actor.is_enemy_of(target)
            # single_any allows any target
        
        # For multi-target actions, validate each target
        if target_type in ["multiple_allies", "multiple_enemies"]:
            if not targets:
                return False
            
            for target in targets:
                if target_type == "multiple_allies" and not actor.is_ally_of(target):
                    return False
                elif target_type == "multiple_enemies" and not actor.is_enemy_of(target):
                    return False
        
        return True
    
    def _execute_action_mechanics(self, 
                                action_def: ActionDefinition, 
                                actor: Combatant, 
                                targets: List[Combatant],
                                additional_data: Dict[str, Any]) -> ActionResult:
        """Execute the mechanical effects of an action."""
        result = ActionResult(success=False, message="Action failed")
        
        # Handle different action types
        if action_def.category.value == "attack":
            return self._execute_attack_action(action_def, actor, targets, additional_data)
        elif action_def.category.value == "spell":
            return self._execute_spell_action(action_def, actor, targets, additional_data)
        elif action_def.category.value == "utility":
            return self._execute_utility_action(action_def, actor, targets, additional_data)
        else:
            # Generic action execution
            result.success = True
            result.message = f"{actor.name} used {action_def.name}"
            result.targets_affected = [t.id for t in targets]
        
        return result
    
    def _execute_attack_action(self, 
                             action_def: ActionDefinition, 
                             actor: Combatant, 
                             targets: List[Combatant],
                             additional_data: Dict[str, Any]) -> ActionResult:
        """Execute an attack action with hit rolls and damage."""
        if not targets:
            return ActionResult(success=False, message="No targets for attack")
        
        target = targets[0]  # Attacks typically target one combatant
        
        # Roll to hit
        hit_roll = self.dice_service.roll_d20()
        attack_bonus = additional_data.get("attack_bonus", 0)
        total_attack = hit_roll + attack_bonus
        
        target_ac = target.get_effective_armor_class()
        hit = total_attack >= target_ac
        
        result = ActionResult(
            success=hit,
            message=f"{actor.name} {'hits' if hit else 'misses'} {target.name}",
            targets_affected=[target.id]
        )
        
        if hit:
            # Roll damage
            damage_rolls = self.dice_service.roll_dice(1, 8)  # Default 1d8
            total_damage = sum(damage_rolls) + additional_data.get("damage_bonus", 0)
            
            # Apply damage
            damage_result = target.take_damage(total_damage)
            result.damage_dealt = damage_result["damage_dealt"]
            
            # Check for critical hit
            if hit_roll == 20:
                result.additional_data["critical_hit"] = True
                result.message += " (CRITICAL HIT!)"
        
        return result
    
    def _execute_spell_action(self, 
                            action_def: ActionDefinition, 
                            actor: Combatant, 
                            targets: List[Combatant],
                            additional_data: Dict[str, Any]) -> ActionResult:
        """Execute a spell action."""
        # Simplified spell execution
        result = ActionResult(
            success=True,
            message=f"{actor.name} casts {action_def.name}",
            targets_affected=[t.id for t in targets]
        )
        
        # Apply spell effects to targets
        for target in targets:
            if action_def.base_damage > 0:
                damage = action_def.base_damage
                damage_result = target.take_damage(damage)
                result.damage_dealt += damage_result["damage_dealt"]
            
            # Apply status effects
            for effect_name in action_def.applies_status_effects:
                effect = StatusEffect.create_from_template(effect_name)
                target.add_status_effect(effect)
                result.status_effects_applied.append(effect_name)
        
        return result
    
    def _execute_utility_action(self, 
                              action_def: ActionDefinition, 
                              actor: Combatant, 
                              targets: List[Combatant],
                              additional_data: Dict[str, Any]) -> ActionResult:
        """Execute a utility action."""
        return ActionResult(
            success=True,
            message=f"{actor.name} uses {action_def.name}",
            targets_affected=[t.id for t in targets]
        )
    
    def _process_start_of_turn_effects(self, combatant: Combatant, encounter: CombatEncounter) -> None:
        """Process effects that trigger at the start of a turn."""
        # Tick status effects and remove expired ones
        expired_effects = combatant.tick_status_effects()
        
        for effect_name in expired_effects:
            encounter.log_event(f"{effect_name} effect expired on {combatant.name}")
        
        # Apply damage/healing over time
        for effect in combatant.status_effects:
            dot_damage = effect.apply_damage_over_time()
            if dot_damage:
                damage_result = combatant.take_damage(dot_damage["damage"])
                encounter.log_event(
                    f"{combatant.name} takes {damage_result['damage_dealt']} {dot_damage['damage_type']} damage from {effect.name}"
                )
            
            hot_healing = effect.apply_healing_over_time()
            if hot_healing:
                heal_result = combatant.heal(hot_healing["healing"])
                encounter.log_event(
                    f"{combatant.name} heals {heal_result['healing_applied']} HP from {effect.name}"
                )
    
    def _process_end_of_turn_effects(self, combatant: Combatant, encounter: CombatEncounter) -> None:
        """Process effects that trigger at the end of a turn."""
        # Currently no end-of-turn effects, but framework is here
        pass
    
    def _process_start_of_round_effects(self, encounter: CombatEncounter) -> None:
        """Process effects that trigger at the start of each round."""
        encounter.log_event(f"Round {encounter.round_number} begins")
    
    def get_encounter_by_id(self, encounter_id: UUID) -> Optional[CombatEncounter]:
        """Get encounter by ID."""
        return self.combat_repository.get_encounter_by_id(encounter_id)
    
    def get_available_actions_for_combatant(self, combatant: Combatant) -> List[ActionDefinition]:
        """Get all actions available to a combatant."""
        all_actions = self.action_repository.get_actions_for_combatant(combatant)
        return [action for action in all_actions if self._can_actor_use_action(combatant, action)]
    
    def calculate_damage_and_apply_attack(
        self, 
        attacker: Combatant, 
        target: Combatant, 
        action: ActionDefinition,
        attack_roll: int = None,
        advantage: bool = False,
        disadvantage: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate damage and apply attack results with proper business rules.
        
        Args:
            attacker: The combatant making the attack
            target: The combatant being attacked
            action: The action definition being used
            attack_roll: Pre-rolled attack value (if None, will roll)
            advantage: Whether attack has advantage
            disadvantage: Whether attack has disadvantage
            
        Returns:
            Dict containing attack results and damage information
        """
        # Business rule: Validate attack prerequisites
        if not attacker.is_conscious:
            raise ValueError("Unconscious combatants cannot attack")
        
        if not target.is_active:
            raise ValueError("Cannot attack inactive targets")
        
        # Calculate attack roll if not provided
        if attack_roll is None:
            attack_bonus = self._calculate_attack_bonus(attacker, action)
            attack_roll, is_critical = self.dice_service.roll_attack(
                attack_bonus, advantage, disadvantage
            )
        else:
            is_critical = attack_roll >= 20
        
        # Check if attack hits
        hits = attack_roll >= target.armor_class or is_critical
        
        if not hits:
            return {
                "hit": False,
                "damage": 0,
                "critical": False,
                "attack_roll": attack_roll,
                "target_ac": target.armor_class,
                "message": f"{attacker.name} misses {target.name} (rolled {attack_roll} vs AC {target.armor_class})"
            }
        
        # Calculate damage
        damage_expr = f"{action.base_damage}d6" if action.base_damage > 0 else "1d4"
        if action.damage_type:
            damage_expr = f"{action.base_damage}d6"  # Use action's base damage
        
        if is_critical:
            damage = self.dice_service.roll_critical_damage(damage_expr)
        else:
            damage = self.dice_service.roll_damage(damage_expr)
        
        # Apply damage modifiers (strength for melee, dex for ranged)
        modifier = self._get_damage_modifier(attacker, action)
        total_damage = max(0, damage + modifier)
        
        # Apply damage to target
        target.current_hp = max(0, target.current_hp - total_damage)
        
        # Update consciousness status
        if target.current_hp <= 0:
            target.is_conscious = False
        
        hit_type = "critical hit" if is_critical else "hit"
        return {
            "hit": True,
            "damage": total_damage,
            "critical": is_critical,
            "attack_roll": attack_roll,
            "target_ac": target.armor_class,
            "message": f"{attacker.name} {hit_type}s {target.name} for {total_damage} damage!"
        }
    
    def _calculate_attack_bonus(self, attacker: Combatant, action: ActionDefinition) -> int:
        """Calculate attack bonus for a combatant using an action."""
        # Base attack bonus (simplified - in real D&D this would include proficiency)
        base_bonus = 2  # Simplified proficiency bonus
        
        # Add ability modifier based on action type
        if "melee" in action.tags:
            ability_modifier = 2  # Simplified strength modifier
        elif "ranged" in action.tags:
            ability_modifier = 2  # Simplified dexterity modifier
        else:
            ability_modifier = 1  # Default modifier
        
        return base_bonus + ability_modifier
    
    def _get_damage_modifier(self, attacker: Combatant, action: ActionDefinition) -> int:
        """Get damage modifier based on action type."""
        if "melee" in action.tags:
            return 2  # Simplified strength modifier
        elif "ranged" in action.tags:
            return 2  # Simplified dexterity modifier
        else:
            return 0
    
    def apply_healing(self, target: Combatant, healing_amount: int) -> Dict[str, Any]:
        """
        Apply healing to a combatant with business rules.
        
        Args:
            target: The combatant receiving healing
            healing_amount: Amount of healing to apply
            
        Returns:
            Dict containing healing results
        """
        if healing_amount < 0:
            raise ValueError("Healing amount cannot be negative")
        
        previous_hp = target.current_hp
        
        # Apply healing, but don't exceed max HP
        target.current_hp = min(target.max_hp, target.current_hp + healing_amount)
        
        # If target was unconscious and now has HP, they regain consciousness
        if previous_hp <= 0 and target.current_hp > 0:
            target.is_conscious = True
        
        actual_healing = target.current_hp - previous_hp
        
        return {
            "success": True,
            "previous_hp": previous_hp,
            "new_hp": target.current_hp,
            "healing_applied": actual_healing,
            "regained_consciousness": previous_hp <= 0 and target.current_hp > 0,
            "message": f"{target.name} heals for {actual_healing} HP (now {target.current_hp}/{target.max_hp})"
        }
    
    def roll_initiative_for_combatant(self, combatant: Combatant) -> int:
        """
        Roll initiative for a combatant and update their initiative value.
        
        Args:
            combatant: The combatant to roll initiative for
            
        Returns:
            The rolled initiative value
        """
        initiative = self.dice_service.roll_initiative(combatant.dex_modifier)
        combatant.initiative = initiative
        return initiative
    
    def get_combat_summary(self, encounter: CombatEncounter) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of the combat encounter.
        
        Args:
            encounter: The combat encounter to summarize
            
        Returns:
            Dict containing formatted combat summary data
        """
        # Categorize participants by team
        teams = {}
        for participant in encounter.participants:
            team = participant.team
            if team not in teams:
                teams[team] = []
            teams[team].append({
                "name": participant.name,
                "hp": f"{participant.current_hp}/{participant.max_hp}",
                "status": "conscious" if participant.is_conscious else "unconscious",
                "initiative": participant.initiative
            })
        
        # Get current turn info
        current_participant = None
        if encounter.initiative_order and encounter.current_turn < len(encounter.initiative_order):
            current_participant = encounter.initiative_order[encounter.current_turn]
        
        return {
            "encounter_id": str(encounter.id),
            "name": encounter.name,
            "status": encounter.status,
            "round_number": encounter.round_number,
            "current_turn": encounter.current_turn,
            "current_participant": {
                "name": current_participant.name,
                "team": current_participant.team
            } if current_participant else None,
            "teams": teams,
            "total_participants": len(encounter.participants),
            "conscious_participants": len([p for p in encounter.participants if p.is_conscious]),
            "recent_log_entries": encounter.combat_log[-5:],  # Last 5 entries
            "actions_this_round": len([a for a in encounter.actions_taken if a.round_number == encounter.round_number])
        }
    
    def check_encounter_end_conditions(self, encounter: CombatEncounter) -> Optional[str]:
        """
        Check if the encounter should end based on business rules.
        
        Args:
            encounter: The combat encounter to check
            
        Returns:
            End reason string if encounter should end, None otherwise
        """
        # Group conscious participants by team
        teams_with_conscious = set()
        for participant in encounter.participants:
            if participant.is_conscious:
                teams_with_conscious.add(participant.team)
        
        # Check victory conditions
        if len(teams_with_conscious) <= 1:
            if not teams_with_conscious:
                return "all_participants_defeated"
            else:
                winning_team = next(iter(teams_with_conscious))
                return f"victory_{winning_team}"
        
        # Check for other end conditions (time limits, special objectives, etc.)
        # This can be extended based on specific encounter rules
        
        return None
    
    def validate_action_usage(self, combatant: Combatant, action: ActionDefinition) -> List[str]:
        """
        Validate whether a combatant can use a specific action.
        
        Args:
            combatant: The combatant attempting the action
            action: The action to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check consciousness
        if not combatant.is_conscious:
            errors.append("Combatant is unconscious and cannot act")
        
        # Check action economy
        if action.action_type.value == "standard" and combatant.has_used_standard_action:
            errors.append("Standard action already used this turn")
        elif action.action_type.value == "bonus" and combatant.has_used_bonus_action:
            errors.append("Bonus action already used this turn")
        elif action.action_type.value == "reaction" and combatant.has_used_reaction:
            errors.append("Reaction already used this round")
        
        # Check resource costs
        for resource, cost in action.resource_cost.items():
            # This would need to be expanded based on actual resource tracking
            # For now, just a placeholder for spell slots, class features, etc.
            pass
        
        # Check weapon requirements
        if action.required_weapon_types:
            combatant_weapons = set(combatant.equipped_weapons)
            if not action.required_weapon_types.intersection(combatant_weapons):
                errors.append(f"Requires one of: {', '.join(action.required_weapon_types)}")
        
        # Check class feature requirements
        if action.required_class_features:
            combatant_features = set(combatant.class_features)
            missing_features = action.required_class_features - combatant_features
            if missing_features:
                errors.append(f"Missing class features: {', '.join(missing_features)}")
        
        # Check spell requirements
        if action.required_spells:
            combatant_spells = set(combatant.available_spells)
            if not action.required_spells.intersection(combatant_spells):
                errors.append(f"Requires one of: {', '.join(action.required_spells)}")
        
        return errors
    
    def sort_initiative_order(self, encounter: CombatEncounter) -> CombatEncounter:
        """
        Sort the initiative order based on combatant initiative values.
        
        Args:
            encounter: The combat encounter to sort
            
        Returns:
            Updated encounter with sorted initiative order
        """
        # Sort participants by initiative (highest first), then by dex modifier if tied
        encounter.initiative_order = sorted(
            encounter.participants,
            key=lambda p: (p.initiative, p.dex_modifier),
            reverse=True
        )
        
        # Reset current turn to 0 
        encounter.current_turn = 0
        
        # Update encounter in repository
        return self.combat_repository.update_encounter(encounter)
    
    def start_encounter(self, encounter_id: UUID) -> CombatEncounter:
        """
        Start a combat encounter, transitioning from pending to active.
        
        Args:
            encounter_id: ID of the encounter to start
            
        Returns:
            Updated encounter
        """
        encounter = self.combat_repository.get_encounter_by_id(encounter_id)
        if not encounter:
            raise ValueError(f"Encounter {encounter_id} not found")
        
        if encounter.status != "pending":
            raise ValueError(f"Cannot start encounter with status {encounter.status}")
        
        if not encounter.participants:
            raise ValueError("Cannot start encounter with no participants")
        
        # Business rules for starting combat
        encounter.status = "active"
        encounter.started_at = datetime.utcnow()
        encounter.round_number = 1
        encounter.current_turn = 0
        
        # Ensure initiative order is set
        if not encounter.initiative_order:
            encounter = self.sort_initiative_order(encounter)
        
        # Reset action economy for all participants
        for participant in encounter.participants:
            participant.has_used_standard_action = False
            participant.has_used_bonus_action = False
            participant.has_used_reaction = False
            participant.remaining_movement = 30.0  # Default movement speed
        
        # Add combat start log entry
        encounter.combat_log.append(f"Combat started: {encounter.name}")
        if encounter.initiative_order:
            current = encounter.initiative_order[0]
            encounter.combat_log.append(f"Round {encounter.round_number}: {current.name}'s turn")
        
        return self.combat_repository.update_encounter(encounter)
    
    def end_encounter(self, encounter_id: UUID, reason: str = "manually_ended") -> CombatEncounter:
        """
        End a combat encounter.
        
        Args:
            encounter_id: ID of the encounter to end
            reason: Reason for ending the encounter
            
        Returns:
            Updated encounter
        """
        encounter = self.combat_repository.get_encounter_by_id(encounter_id)
        if not encounter:
            raise ValueError(f"Encounter {encounter_id} not found")
        
        if encounter.status == "completed":
            return encounter  # Already ended
        
        # Business rules for ending combat
        encounter.status = "completed"
        encounter.ended_at = datetime.utcnow()
        encounter.combat_log.append(f"Combat ended: {reason}")
        
        return self.combat_repository.update_encounter(encounter)


__all__ = ["CombatService", "CombatRepository", "ActionDefinitionRepository", "DiceRollingService"] 