"""
Tension-NPC System Integration

Modifies NPC behavior based on local tension levels:
- Personality traits affected by tension (anxiety, aggression, fear)
- Movement patterns (fleeing high-tension areas)
- Trade behavior (price markups, item availability)
- Dialogue options and responses
- AI-generated character development based on tension exposure

This follows the integration patterns from the economy system.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from enum import Enum
from datetime import datetime, timedelta

from backend.systems.tension import UnifiedTensionManager
from backend.infrastructure.events import event_bus

logger = logging.getLogger(__name__)


class TensionResponse(Enum):
    """How NPCs respond to different tension levels"""
    CALM = "calm"           # 0.0-0.2: Normal behavior
    ANXIOUS = "anxious"     # 0.2-0.4: Slightly nervous
    FEARFUL = "fearful"     # 0.4-0.6: Worried, cautious
    PANICKED = "panicked"   # 0.6-0.8: Highly distressed
    FLEEING = "fleeing"     # 0.8-1.0: Attempting to escape


class NPCTensionEffect:
    """Represents how tension affects a specific NPC"""
    def __init__(self, npc_id: UUID, base_tension: float, personal_modifiers: Dict[str, float]):
        self.npc_id = npc_id
        self.base_tension = base_tension
        self.personal_modifiers = personal_modifiers
        self.effective_tension = self._calculate_effective_tension()
        self.response_level = self._determine_response_level()
        
    def _calculate_effective_tension(self) -> float:
        """Calculate how much tension this NPC actually feels"""
        # Base tension modified by personality traits
        courage = self.personal_modifiers.get('courage', 0.5)
        stress_tolerance = self.personal_modifiers.get('stress_tolerance', 0.5)
        local_knowledge = self.personal_modifiers.get('local_knowledge', 0.5)
        
        # Brave NPCs feel less tension
        tension_modifier = 1.0 - (courage * 0.3)
        # Stress-tolerant NPCs handle tension better
        tension_modifier *= 1.0 - (stress_tolerance * 0.2)
        # Local knowledge helps cope with familiar dangers
        tension_modifier *= 1.0 - (local_knowledge * 0.1)
        
        return min(1.0, self.base_tension * tension_modifier)
    
    def _determine_response_level(self) -> TensionResponse:
        """Determine NPC's response to their effective tension level"""
        if self.effective_tension < 0.2:
            return TensionResponse.CALM
        elif self.effective_tension < 0.4:
            return TensionResponse.ANXIOUS
        elif self.effective_tension < 0.6:
            return TensionResponse.FEARFUL
        elif self.effective_tension < 0.8:
            return TensionResponse.PANICKED
        else:
            return TensionResponse.FLEEING


class TensionNPCIntegration:
    """Integrates tension system with NPC behavior"""
    
    def __init__(self, tension_manager: Optional[UnifiedTensionManager] = None):
        self.tension_manager = tension_manager or UnifiedTensionManager()
        self.npc_effects_cache: Dict[UUID, NPCTensionEffect] = {}
        self.last_update = datetime.utcnow()
        
        # Register for tension events
        self._register_event_handlers()
    
    def _register_event_handlers(self) -> None:
        """Register event handlers for tension changes"""
        event_bus.subscribe("tension:level_changed", self._handle_tension_change)
        event_bus.subscribe("tension:conflict_triggered", self._handle_conflict_started)
        event_bus.subscribe("npc:location_changed", self._handle_npc_moved)
    
    async def _handle_tension_change(self, event_data: Dict[str, Any]) -> None:
        """Handle tension level changes affecting NPCs"""
        region_id = event_data.get('region_id')
        poi_id = event_data.get('poi_id')
        new_tension = event_data.get('tension_level', 0.0)
        
        if region_id and poi_id:
            await self.update_npcs_in_location(region_id, poi_id, new_tension)
    
    async def _handle_conflict_started(self, event_data: Dict[str, Any]) -> None:
        """Handle conflict events that cause mass NPC reactions"""
        region_id = event_data.get('region_id')
        conflict_severity = event_data.get('severity', 1.0)
        
        if region_id:
            await self.trigger_mass_npc_reaction(region_id, conflict_severity)
    
    async def _handle_npc_moved(self, event_data: Dict[str, Any]) -> None:
        """Handle NPCs moving to new locations with different tension"""
        npc_id = event_data.get('npc_id')
        new_region = event_data.get('new_region_id')
        new_poi = event_data.get('new_poi_id')
        
        if npc_id and new_region and new_poi:
            await self.update_npc_tension_response(UUID(npc_id), new_region, new_poi)
    
    def get_npc_tension_effect(self, npc_id: UUID, region_id: str, poi_id: str, 
                              npc_traits: Optional[Dict[str, Any]] = None) -> NPCTensionEffect:
        """Get how tension affects a specific NPC"""
        # Check cache first
        if npc_id in self.npc_effects_cache:
            effect = self.npc_effects_cache[npc_id]
            # Update if tension has changed significantly
            current_tension = self.tension_manager.calculate_tension(region_id, poi_id)
            if abs(current_tension - effect.base_tension) > 0.1:
                effect = self._calculate_npc_effect(npc_id, region_id, poi_id, npc_traits)
                self.npc_effects_cache[npc_id] = effect
        else:
            effect = self._calculate_npc_effect(npc_id, region_id, poi_id, npc_traits)
            self.npc_effects_cache[npc_id] = effect
        
        return effect
    
    def _calculate_npc_effect(self, npc_id: UUID, region_id: str, poi_id: str,
                             npc_traits: Optional[Dict[str, Any]] = None) -> NPCTensionEffect:
        """Calculate tension effect for an NPC"""
        base_tension = self.tension_manager.calculate_tension(region_id, poi_id)
        
        # Default personality modifiers if not provided
        if npc_traits is None:
            npc_traits = {
                'courage': 0.5,
                'stress_tolerance': 0.5,
                'local_knowledge': 0.5,
                'loyalty': 0.5
            }
        
        return NPCTensionEffect(npc_id, base_tension, npc_traits)
    
    def get_npc_behavior_modifiers(self, npc_id: UUID, region_id: str, poi_id: str,
                                  npc_traits: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get behavior modifiers for an NPC based on tension"""
        effect = self.get_npc_tension_effect(npc_id, region_id, poi_id, npc_traits)
        
        modifiers = {
            'tension_level': effect.effective_tension,
            'response_type': effect.response_level.value,
            'price_modifier': 1.0,
            'item_availability_modifier': 1.0,
            'dialogue_mood': 'neutral',
            'movement_probability': 0.0,
            'aggression_modifier': 1.0,
            'cooperation_modifier': 1.0
        }
        
        # Apply response-specific modifiers
        if effect.response_level == TensionResponse.CALM:
            modifiers.update({
                'price_modifier': 1.0,
                'item_availability_modifier': 1.0,
                'dialogue_mood': 'friendly',
                'cooperation_modifier': 1.1
            })
        
        elif effect.response_level == TensionResponse.ANXIOUS:
            modifiers.update({
                'price_modifier': 1.05,  # 5% markup due to nervousness
                'item_availability_modifier': 0.95,  # Slightly less willing to sell
                'dialogue_mood': 'nervous',
                'cooperation_modifier': 0.95
            })
        
        elif effect.response_level == TensionResponse.FEARFUL:
            modifiers.update({
                'price_modifier': 1.15,  # 15% markup
                'item_availability_modifier': 0.8,  # More reluctant to trade
                'dialogue_mood': 'worried',
                'movement_probability': 0.1,  # 10% chance to relocate
                'cooperation_modifier': 0.8
            })
        
        elif effect.response_level == TensionResponse.PANICKED:
            modifiers.update({
                'price_modifier': 1.3,   # 30% panic markup
                'item_availability_modifier': 0.6,  # Much less willing to trade
                'dialogue_mood': 'panicked',
                'movement_probability': 0.3,  # 30% chance to relocate
                'aggression_modifier': 1.2,  # More likely to lash out
                'cooperation_modifier': 0.6
            })
        
        elif effect.response_level == TensionResponse.FLEEING:
            modifiers.update({
                'price_modifier': 2.0,   # Extreme markup for emergency trades
                'item_availability_modifier': 0.3,  # Only selling essentials
                'dialogue_mood': 'desperate',
                'movement_probability': 0.8,  # 80% chance to flee
                'aggression_modifier': 0.5,  # Fight-or-flight: might flee instead
                'cooperation_modifier': 0.3
            })
        
        return modifiers
    
    def get_tension_dialogue_options(self, npc_id: UUID, region_id: str, poi_id: str,
                                   npc_traits: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get tension-specific dialogue options"""
        effect = self.get_npc_tension_effect(npc_id, region_id, poi_id, npc_traits)
        
        dialogue_options = []
        
        if effect.response_level == TensionResponse.ANXIOUS:
            dialogue_options.extend([
                {
                    "text": "You seem a bit on edge. Everything alright?",
                    "response": "These are troubling times. I can feel the tension in the air.",
                    "mood": "concerned"
                },
                {
                    "text": "Is there anything I can do to help?",
                    "response": "Just... be careful out there. Things don't feel safe anymore.",
                    "mood": "worried"
                }
            ])
        
        elif effect.response_level == TensionResponse.FEARFUL:
            dialogue_options.extend([
                {
                    "text": "You look frightened. What's wrong?",
                    "response": "Can't you feel it? The danger lurking everywhere? I don't know who to trust.",
                    "mood": "fearful"
                },
                {
                    "text": "Should we be concerned about safety here?",
                    "response": "Absolutely! I'm thinking of leaving soon. This place isn't safe anymore.",
                    "mood": "warning"
                }
            ])
        
        elif effect.response_level == TensionResponse.PANICKED:
            dialogue_options.extend([
                {
                    "text": "Calm down! What's happening?",
                    "response": "Calm down?! How can I be calm when everything's falling apart?!",
                    "mood": "panicked"
                },
                {
                    "text": "Take a deep breath. Tell me what's wrong.",
                    "response": "We need to get out of here! It's not safe! Violence could break out any moment!",
                    "mood": "urgent"
                }
            ])
        
        elif effect.response_level == TensionResponse.FLEEING:
            dialogue_options.extend([
                {
                    "text": "Wait! Where are you going?",
                    "response": "Away from here! You should come too if you're smart!",
                    "mood": "desperate"
                },
                {
                    "text": "Is it really that bad?",
                    "response": "That bad? It's worse! I won't stick around to find out what happens next!",
                    "mood": "fleeing"
                }
            ])
        
        return dialogue_options
    
    async def update_npcs_in_location(self, region_id: str, poi_id: str, new_tension: float) -> None:
        """Update all NPCs in a location when tension changes"""
        try:
            # This would integrate with the actual NPC system to get NPCs in location
            # For now, implementing the integration pattern
            
            logger.info(f"Updating NPCs in {region_id}/{poi_id} for tension level {new_tension}")
            
            # Clear cache for this location to force recalculation
            npcs_to_update = []
            for npc_id, effect in self.npc_effects_cache.items():
                # In a full implementation, we'd check if NPC is in this location
                npcs_to_update.append(npc_id)
            
            # Remove cached effects so they get recalculated
            for npc_id in npcs_to_update:
                if npc_id in self.npc_effects_cache:
                    del self.npc_effects_cache[npc_id]
            
            # Emit event for NPC system to respond
            event_bus.emit("tension:npcs_affected", {
                'region_id': region_id,
                'poi_id': poi_id,
                'tension_level': new_tension,
                'affected_npcs': [str(npc_id) for npc_id in npcs_to_update]
            })
            
        except Exception as e:
            logger.error(f"Error updating NPCs for tension change: {e}")
    
    async def trigger_mass_npc_reaction(self, region_id: str, conflict_severity: float) -> None:
        """Trigger region-wide NPC reactions to major conflicts"""
        try:
            # Calculate how many NPCs might flee or react strongly
            base_flee_probability = min(0.6, conflict_severity * 0.3)
            
            logger.info(f"Triggering mass NPC reaction in {region_id}, severity {conflict_severity}")
            
            # This would integrate with population/NPC systems to:
            # 1. Identify NPCs in the region
            # 2. Calculate individual responses based on personality
            # 3. Trigger appropriate behaviors (fleeing, hiding, fighting, etc.)
            
            event_bus.emit("tension:mass_npc_reaction", {
                'region_id': region_id,
                'conflict_severity': conflict_severity,
                'estimated_flee_probability': base_flee_probability,
                'reaction_type': 'conflict_response'
            })
            
        except Exception as e:
            logger.error(f"Error triggering mass NPC reaction: {e}")
    
    async def update_npc_tension_response(self, npc_id: UUID, region_id: str, poi_id: str) -> None:
        """Update an NPC's tension response when they move locations"""
        try:
            # Remove old cached effect
            if npc_id in self.npc_effects_cache:
                del self.npc_effects_cache[npc_id]
            
            # Calculate new effect (will be cached)
            new_effect = self.get_npc_tension_effect(npc_id, region_id, poi_id)
            
            logger.info(f"NPC {npc_id} tension response updated: {new_effect.response_level.value}")
            
            # Emit event for other systems
            event_bus.emit("tension:npc_response_updated", {
                'npc_id': str(npc_id),
                'region_id': region_id,
                'poi_id': poi_id,
                'tension_level': new_effect.effective_tension,
                'response_level': new_effect.response_level.value
            })
            
        except Exception as e:
            logger.error(f"Error updating NPC tension response: {e}")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of tension-NPC integration"""
        return {
            'cached_npc_effects': len(self.npc_effects_cache),
            'last_update': self.last_update.isoformat(),
            'integration_active': True,
            'tension_response_levels': [response.value for response in TensionResponse]
        } 