"""
Tension-Combat System Integration

Modifies combat mechanics based on regional tension levels:
- Combat difficulty scaling with tension (more aggressive enemies)
- Encounter spawn rates affected by tension
- Different enemy types in high-tension areas
- Combat aftermath affects local tension
- Faction warfare mechanics triggered by extreme tension

This follows the integration patterns from the combat action system.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from datetime import datetime

from backend.systems.tension import UnifiedTensionManager
from backend.infrastructure.events import event_bus

logger = logging.getLogger(__name__)


class TensionCombatEffect(Enum):
    """Types of combat effects based on tension"""
    PEACEFUL = "peaceful"           # 0.0-0.2: Reduced spawn rates, friendly encounters
    WATCHFUL = "watchful"           # 0.2-0.4: Normal encounters, alert guards
    AGGRESSIVE = "aggressive"       # 0.4-0.6: Increased spawn rates, hostile attitude
    HOSTILE = "hostile"             # 0.6-0.8: Frequent encounters, combat-ready NPCs
    WARFARE = "warfare"             # 0.8-1.0: Constant danger, faction conflicts


class CombatDifficultyModifier:
    """Represents how tension affects combat difficulty"""
    def __init__(self, tension_level: float):
        self.tension_level = tension_level
        self.effect_type = self._determine_effect_type()
        self.modifiers = self._calculate_modifiers()
    
    def _determine_effect_type(self) -> TensionCombatEffect:
        """Determine combat effect type based on tension level"""
        if self.tension_level < 0.2:
            return TensionCombatEffect.PEACEFUL
        elif self.tension_level < 0.4:
            return TensionCombatEffect.WATCHFUL
        elif self.tension_level < 0.6:
            return TensionCombatEffect.AGGRESSIVE
        elif self.tension_level < 0.8:
            return TensionCombatEffect.HOSTILE
        else:
            return TensionCombatEffect.WARFARE
    
    def _calculate_modifiers(self) -> Dict[str, float]:
        """Calculate specific combat modifiers"""
        base_modifiers = {
            'spawn_rate_multiplier': 1.0,
            'enemy_aggression': 1.0,
            'enemy_damage_multiplier': 1.0,
            'enemy_health_multiplier': 1.0,
            'encounter_frequency': 1.0,
            'faction_conflict_chance': 0.0,
            'guard_response_time': 1.0,
            'civilian_flee_chance': 0.1
        }
        
        if self.effect_type == TensionCombatEffect.PEACEFUL:
            base_modifiers.update({
                'spawn_rate_multiplier': 0.5,
                'enemy_aggression': 0.8,
                'encounter_frequency': 0.6,
                'guard_response_time': 1.5,  # Slower response (more relaxed)
                'civilian_flee_chance': 0.05
            })
        
        elif self.effect_type == TensionCombatEffect.WATCHFUL:
            base_modifiers.update({
                'spawn_rate_multiplier': 0.8,
                'enemy_aggression': 1.0,
                'encounter_frequency': 0.9,
                'guard_response_time': 1.0,
                'civilian_flee_chance': 0.1
            })
        
        elif self.effect_type == TensionCombatEffect.AGGRESSIVE:
            base_modifiers.update({
                'spawn_rate_multiplier': 1.2,
                'enemy_aggression': 1.3,
                'enemy_damage_multiplier': 1.1,
                'encounter_frequency': 1.3,
                'faction_conflict_chance': 0.1,
                'guard_response_time': 0.8,
                'civilian_flee_chance': 0.3
            })
        
        elif self.effect_type == TensionCombatEffect.HOSTILE:
            base_modifiers.update({
                'spawn_rate_multiplier': 1.5,
                'enemy_aggression': 1.6,
                'enemy_damage_multiplier': 1.2,
                'enemy_health_multiplier': 1.1,
                'encounter_frequency': 1.6,
                'faction_conflict_chance': 0.3,
                'guard_response_time': 0.6,
                'civilian_flee_chance': 0.6
            })
        
        elif self.effect_type == TensionCombatEffect.WARFARE:
            base_modifiers.update({
                'spawn_rate_multiplier': 2.0,
                'enemy_aggression': 2.0,
                'enemy_damage_multiplier': 1.4,
                'enemy_health_multiplier': 1.3,
                'encounter_frequency': 2.5,
                'faction_conflict_chance': 0.8,
                'guard_response_time': 0.3,  # Very fast response
                'civilian_flee_chance': 0.9
            })
        
        return base_modifiers


class TensionCombatIntegration:
    """Integrates tension system with combat mechanics"""
    
    def __init__(self, tension_manager: Optional[UnifiedTensionManager] = None):
        self.tension_manager = tension_manager or UnifiedTensionManager()
        self.combat_modifiers_cache: Dict[str, CombatDifficultyModifier] = {}
        self.active_conflicts: Dict[str, Dict[str, Any]] = {}
        
        # Register for combat and tension events
        self._register_event_handlers()
    
    def _register_event_handlers(self) -> None:
        """Register event handlers for combat and tension events"""
        event_bus.subscribe("combat:started", self._handle_combat_started)
        event_bus.subscribe("combat:ended", self._handle_combat_ended)
        event_bus.subscribe("tension:level_changed", self._handle_tension_changed)
        event_bus.subscribe("tension:conflict_triggered", self._handle_conflict_triggered)
    
    async def _handle_combat_started(self, event_data: Dict[str, Any]) -> None:
        """Handle combat start events to apply tension modifiers"""
        region_id = event_data.get('region_id')
        poi_id = event_data.get('poi_id')
        combat_id = event_data.get('combat_id')
        
        if region_id and poi_id and combat_id:
            modifiers = self.get_combat_modifiers(region_id, poi_id)
            await self.apply_tension_combat_modifiers(combat_id, modifiers)
    
    async def _handle_combat_ended(self, event_data: Dict[str, Any]) -> None:
        """Handle combat end events to update tension based on outcome"""
        region_id = event_data.get('region_id')
        poi_id = event_data.get('poi_id')
        outcome = event_data.get('outcome', 'unknown')
        casualties = event_data.get('casualties', 0)
        was_lethal = event_data.get('lethal', False)
        
        if region_id and poi_id:
            await self.apply_combat_tension_effects(region_id, poi_id, outcome, casualties, was_lethal)
    
    async def _handle_tension_changed(self, event_data: Dict[str, Any]) -> None:
        """Handle tension changes that affect combat parameters"""
        region_id = event_data.get('region_id')
        poi_id = event_data.get('poi_id')
        new_tension = event_data.get('tension_level', 0.0)
        
        if region_id and poi_id:
            location_key = f"{region_id}:{poi_id}"
            # Clear cache to force recalculation
            if location_key in self.combat_modifiers_cache:
                del self.combat_modifiers_cache[location_key]
            
            # Check if new tension level triggers warfare
            if new_tension >= 0.8:
                await self.evaluate_warfare_trigger(region_id, poi_id, new_tension)
    
    async def _handle_conflict_triggered(self, event_data: Dict[str, Any]) -> None:
        """Handle major conflicts that affect combat across a region"""
        region_id = event_data.get('region_id')
        conflict_type = event_data.get('conflict_type')
        severity = event_data.get('severity', 1.0)
        
        if region_id:
            await self.activate_regional_conflict(region_id, conflict_type, severity)
    
    def get_combat_modifiers(self, region_id: str, poi_id: str) -> CombatDifficultyModifier:
        """Get combat difficulty modifiers for a location"""
        location_key = f"{region_id}:{poi_id}"
        
        # Check cache first
        if location_key in self.combat_modifiers_cache:
            return self.combat_modifiers_cache[location_key]
        
        # Calculate new modifiers
        tension_level = self.tension_manager.calculate_tension(region_id, poi_id)
        modifiers = CombatDifficultyModifier(tension_level)
        
        # Cache for future use
        self.combat_modifiers_cache[location_key] = modifiers
        
        return modifiers
    
    async def apply_tension_combat_modifiers(self, combat_id: str, modifiers: CombatDifficultyModifier) -> None:
        """Apply tension-based modifiers to an active combat"""
        try:
            modifier_data = {
                'combat_id': combat_id,
                'tension_level': modifiers.tension_level,
                'effect_type': modifiers.effect_type.value,
                'modifiers': modifiers.modifiers,
                'source': 'tension_system'
            }
            
            # Emit event for combat system to apply modifiers
            event_bus.emit("combat:apply_tension_modifiers", modifier_data)
            
            logger.info(f"Applied {modifiers.effect_type.value} tension modifiers to combat {combat_id}")
            
        except Exception as e:
            logger.error(f"Error applying combat modifiers: {e}")
    
    async def apply_combat_tension_effects(self, region_id: str, poi_id: str, 
                                         outcome: str, casualties: int, was_lethal: bool) -> None:
        """Apply tension effects based on combat outcome"""
        try:
            tension_change = 0.0
            
            # Base tension increase from combat
            if was_lethal:
                tension_change += 0.15  # Lethal combat significantly increases tension
            else:
                tension_change += 0.05  # Non-lethal combat minor increase
            
            # Casualties affect tension more
            if casualties > 0:
                tension_change += min(0.2, casualties * 0.05)  # Up to 0.2 additional
            
            # Outcome affects final tension
            if outcome == 'player_victory':
                tension_change *= 0.8  # Reduced if player wins
            elif outcome == 'enemy_victory':
                tension_change *= 1.3  # Increased if enemies win
            elif outcome == 'civilian_casualties':
                tension_change *= 1.8  # Much higher if civilians hurt
            
            # Apply the tension change
            if tension_change > 0.01:  # Only apply if significant
                event_bus.emit("tension:apply_modifier", {
                    'region_id': region_id,
                    'poi_id': poi_id,
                    'tension_change': tension_change,
                    'source': f'combat_{outcome}',
                    'duration_hours': 6.0  # Combat effects last 6 hours
                })
                
                logger.info(f"Combat in {region_id}/{poi_id} increased tension by {tension_change:.3f}")
            
        except Exception as e:
            logger.error(f"Error applying combat tension effects: {e}")
    
    async def evaluate_warfare_trigger(self, region_id: str, poi_id: str, tension_level: float) -> None:
        """Evaluate whether to trigger faction warfare based on extreme tension"""
        try:
            if tension_level >= 0.9:  # Critical tension
                warfare_probability = min(0.8, (tension_level - 0.8) * 4.0)  # 0.8 to 80% chance
                
                import random
                if random.random() < warfare_probability:
                    await self.trigger_faction_warfare(region_id, poi_id, tension_level)
            
        except Exception as e:
            logger.error(f"Error evaluating warfare trigger: {e}")
    
    async def trigger_faction_warfare(self, region_id: str, poi_id: str, tension_level: float) -> None:
        """Trigger faction warfare in a high-tension area"""
        try:
            warfare_data = {
                'region_id': region_id,
                'poi_id': poi_id,
                'tension_level': tension_level,
                'warfare_type': 'tension_triggered',
                'severity': min(2.0, tension_level * 1.5),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Store active conflict
            conflict_key = f"{region_id}:{poi_id}"
            self.active_conflicts[conflict_key] = warfare_data
            
            # Emit warfare event
            event_bus.emit("combat:faction_warfare_triggered", warfare_data)
            event_bus.emit("tension:conflict_triggered", warfare_data)
            
            logger.warning(f"Faction warfare triggered in {region_id}/{poi_id} due to extreme tension")
            
        except Exception as e:
            logger.error(f"Error triggering faction warfare: {e}")
    
    async def activate_regional_conflict(self, region_id: str, conflict_type: str, severity: float) -> None:
        """Activate region-wide conflict affecting all combat"""
        try:
            conflict_data = {
                'region_id': region_id,
                'conflict_type': conflict_type,
                'severity': severity,
                'start_time': datetime.utcnow(),
                'active': True
            }
            
            # Store regional conflict
            self.active_conflicts[f"region_{region_id}"] = conflict_data
            
            # Clear all cached modifiers in this region to force recalculation
            keys_to_remove = [key for key in self.combat_modifiers_cache.keys() 
                             if key.startswith(f"{region_id}:")]
            for key in keys_to_remove:
                del self.combat_modifiers_cache[key]
            
            # Emit regional conflict event
            event_bus.emit("combat:regional_conflict_activated", conflict_data)
            
            logger.warning(f"Regional conflict activated in {region_id}: {conflict_type}")
            
        except Exception as e:
            logger.error(f"Error activating regional conflict: {e}")
    
    def get_encounter_spawn_rate(self, region_id: str, poi_id: str, base_rate: float = 1.0) -> float:
        """Get modified encounter spawn rate based on tension"""
        modifiers = self.get_combat_modifiers(region_id, poi_id)
        return base_rate * modifiers.modifiers['spawn_rate_multiplier']
    
    def get_enemy_difficulty_multiplier(self, region_id: str, poi_id: str) -> Dict[str, float]:
        """Get enemy difficulty multipliers based on tension"""
        modifiers = self.get_combat_modifiers(region_id, poi_id)
        return {
            'damage_multiplier': modifiers.modifiers['enemy_damage_multiplier'],
            'health_multiplier': modifiers.modifiers['enemy_health_multiplier'],
            'aggression_multiplier': modifiers.modifiers['enemy_aggression']
        }
    
    def should_trigger_faction_encounter(self, region_id: str, poi_id: str) -> Tuple[bool, Optional[str]]:
        """Check if a faction conflict encounter should be triggered"""
        modifiers = self.get_combat_modifiers(region_id, poi_id)
        faction_chance = modifiers.modifiers['faction_conflict_chance']
        
        import random
        if random.random() < faction_chance:
            # Determine which type of faction encounter
            encounter_types = ['faction_patrol', 'faction_skirmish', 'faction_standoff']
            return True, random.choice(encounter_types)
        
        return False, None
    
    def get_guard_response_modifier(self, region_id: str, poi_id: str) -> float:
        """Get guard response time modifier based on tension"""
        modifiers = self.get_combat_modifiers(region_id, poi_id)
        return modifiers.modifiers['guard_response_time']
    
    def get_civilian_behavior_modifiers(self, region_id: str, poi_id: str) -> Dict[str, float]:
        """Get civilian behavior modifiers during combat"""
        modifiers = self.get_combat_modifiers(region_id, poi_id)
        return {
            'flee_chance': modifiers.modifiers['civilian_flee_chance'],
            'panic_threshold': 1.0 - (modifiers.tension_level * 0.5),  # Lower threshold = panic easier
            'cooperation_chance': max(0.1, 1.0 - modifiers.tension_level)  # Less cooperative in high tension
        }
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of tension-combat integration"""
        return {
            'cached_modifiers': len(self.combat_modifiers_cache),
            'active_conflicts': len(self.active_conflicts),
            'conflict_regions': list(self.active_conflicts.keys()),
            'combat_effect_types': [effect.value for effect in TensionCombatEffect],
            'integration_active': True
        } 