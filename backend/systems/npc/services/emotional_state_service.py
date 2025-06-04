"""
Emotional State Service for NPCs

Manages NPC emotional states, mood changes, emotional triggers, and their 
impact on behavior, decision-making, and interactions.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID

from backend.infrastructure.systems.npc.models.emotional_state_models import (
    NpcEmotionalState, NpcEmotionalTrigger, NpcEmotionalInfluence, NpcEmotionalMemory,
    EmotionalState, EmotionalTriggerType
)
from backend.infrastructure.systems.npc.models.models import NpcEntity

logger = logging.getLogger(__name__)


class EmotionalStateService:
    """Service for managing NPC emotional states and their behavioral impacts"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        
        # Emotional stability factors
        self.emotional_decay_rate = 0.1  # How quickly emotions return to baseline
        self.trigger_threshold = 3.0     # Minimum trigger severity to change emotion
        self.memory_formation_threshold = 7.0  # Minimum intensity to form emotional memory
        
        # Weather and seasonal effects
        self.weather_effects = {
            "sunny": {"happiness_level": 1.0, "energy_level": 0.5},
            "rainy": {"happiness_level": -0.5, "energy_level": -0.3, "melancholy": 0.4},
            "stormy": {"stress_level": 0.8, "anxiety": 0.6},
            "foggy": {"confidence_level": -0.3, "mystery": 0.2},
            "snow": {"content": 0.3, "nostalgia": 0.4}
        }
    
    def get_or_create_emotional_state(self, npc_id: UUID) -> NpcEmotionalState:
        """Get existing emotional state or create a new one"""
        emotional_state = self.db_session.query(NpcEmotionalState).filter_by(npc_id=npc_id).first()
        
        if not emotional_state:
            # Create new emotional state based on NPC personality
            npc = self.db_session.query(NpcEntity).filter_by(id=npc_id).first()
            if not npc:
                raise ValueError(f"NPC {npc_id} not found")
            
            emotional_state = self._create_initial_emotional_state(npc)
            self.db_session.add(emotional_state)
            self.db_session.commit()
        
        return emotional_state
    
    def _create_initial_emotional_state(self, npc: NpcEntity) -> NpcEmotionalState:
        """Create initial emotional state based on NPC's hidden traits"""
        # Use hidden personality traits to determine baseline emotional characteristics
        baseline_happiness = (npc.hidden_resilience or 5) + (npc.hidden_pragmatism or 5) - 5
        baseline_energy = (npc.hidden_ambition or 5) + (npc.hidden_discipline or 5) - 5
        baseline_stress = (npc.hidden_impulsivity or 5) - (npc.hidden_resilience or 5)
        baseline_confidence = (npc.hidden_integrity or 5) + (npc.hidden_ambition or 5) - 5
        baseline_sociability = 10 - (npc.hidden_impulsivity or 5)  # Less impulsive = more social
        baseline_optimism = (npc.hidden_resilience or 5) + (npc.hidden_pragmatism or 5) - 5
        
        # Determine initial emotion based on overall emotional profile
        if baseline_happiness > 3 and baseline_energy > 2:
            initial_emotion = EmotionalState.JOYFUL
        elif baseline_happiness > 1 and baseline_stress < 2:
            initial_emotion = EmotionalState.CONTENT
        elif baseline_stress > 5:
            initial_emotion = EmotionalState.ANXIOUS
        elif baseline_confidence > 4:
            initial_emotion = EmotionalState.CONFIDENT
        else:
            initial_emotion = EmotionalState.NEUTRAL
        
        return NpcEmotionalState(
            npc_id=npc.id,
            current_emotion=initial_emotion,
            emotion_intensity=random.uniform(3.0, 7.0),
            emotion_stability=random.uniform(4.0, 8.0),
            happiness_level=max(-10, min(10, baseline_happiness)),
            energy_level=max(-10, min(10, baseline_energy)),
            stress_level=max(-10, min(10, baseline_stress)),
            confidence_level=max(-10, min(10, baseline_confidence)),
            sociability_level=max(-10, min(10, baseline_sociability)),
            optimism_level=max(-10, min(10, baseline_optimism)),
            emotional_volatility=random.uniform(3.0, 7.0),
            emotional_recovery_rate=random.uniform(4.0, 8.0),
            weather_sensitivity=random.uniform(1.0, 5.0),
            social_sensitivity=random.uniform(3.0, 8.0),
            stress_tolerance=random.uniform(3.0, 9.0),
            baseline_emotion=initial_emotion
        )
    
    def process_emotional_trigger(self, npc_id: UUID, trigger_type: EmotionalTriggerType, 
                                trigger_description: str, trigger_severity: float = 5.0,
                                related_entity_id: Optional[str] = None,
                                related_entity_type: Optional[str] = None,
                                location: Optional[str] = None) -> Dict[str, Any]:
        """Process an emotional trigger and update NPC's emotional state"""
        emotional_state = self.get_or_create_emotional_state(npc_id)
        
        # Check if trigger is significant enough to cause change
        if trigger_severity < self.trigger_threshold:
            return {"emotion_changed": False, "reason": "trigger_too_weak"}
        
        previous_emotion = emotional_state.current_emotion
        
        # Determine new emotion based on trigger type and NPC's current state
        new_emotion, emotion_change_magnitude = self._calculate_emotional_response(
            emotional_state, trigger_type, trigger_severity
        )
        
        # Apply emotional change
        if new_emotion != previous_emotion:
            emotional_state.current_emotion = new_emotion
            emotional_state.emotion_intensity = min(10.0, trigger_severity + emotion_change_magnitude)
            emotional_state.last_major_emotional_event = datetime.utcnow()
            emotional_state.days_in_current_state = 0
            
            # Update emotional dimensions based on the trigger
            self._update_emotional_dimensions(emotional_state, trigger_type, trigger_severity)
            
            # Create trigger record
            trigger_record = NpcEmotionalTrigger(
                npc_id=npc_id,
                emotional_state_id=emotional_state.id,
                trigger_type=trigger_type,
                trigger_description=trigger_description,
                trigger_severity=trigger_severity,
                previous_emotion=previous_emotion,
                resulting_emotion=new_emotion,
                emotion_change_magnitude=emotion_change_magnitude,
                related_entity_id=related_entity_id,
                related_entity_type=related_entity_type,
                location=location,
                expected_duration_days=self._calculate_trigger_duration(trigger_type, trigger_severity)
            )
            
            self.db_session.add(trigger_record)
            
            # Create emotional memory if significant enough
            if trigger_severity >= self.memory_formation_threshold:
                self._create_emotional_memory(npc_id, trigger_type, trigger_description, 
                                            new_emotion, trigger_severity, location,
                                            related_entity_id, related_entity_type)
            
            self.db_session.commit()
            
            return {
                "emotion_changed": True,
                "previous_emotion": previous_emotion.value,
                "new_emotion": new_emotion.value,
                "emotion_intensity": emotional_state.emotion_intensity,
                "change_magnitude": emotion_change_magnitude,
                "trigger_id": str(trigger_record.id)
            }
        
        return {"emotion_changed": False, "reason": "insufficient_change"}
    
    def _calculate_emotional_response(self, emotional_state: NpcEmotionalState, 
                                    trigger_type: EmotionalTriggerType, 
                                    trigger_severity: float) -> Tuple[EmotionalState, float]:
        """Calculate the emotional response to a trigger"""
        
        # Define trigger -> emotion mappings
        trigger_emotion_map = {
            EmotionalTriggerType.GOAL_SUCCESS: [EmotionalState.JOYFUL, EmotionalState.CONFIDENT, EmotionalState.EXCITED],
            EmotionalTriggerType.GOAL_FAILURE: [EmotionalState.DEPRESSED, EmotionalState.ANGRY, EmotionalState.DETERMINED],
            EmotionalTriggerType.RELATIONSHIP_CHANGE: [EmotionalState.JOYFUL, EmotionalState.ANXIOUS, EmotionalState.LOVE_STRUCK],
            EmotionalTriggerType.BETRAYAL: [EmotionalState.ANGRY, EmotionalState.BITTER, EmotionalState.GRIEF_STRICKEN],
            EmotionalTriggerType.LOSS_OF_LOVED_ONE: [EmotionalState.GRIEF_STRICKEN, EmotionalState.DEPRESSED],
            EmotionalTriggerType.PHYSICAL_DANGER: [EmotionalState.FEARFUL, EmotionalState.ANGRY, EmotionalState.DETERMINED],
            EmotionalTriggerType.SOCIAL_TRIUMPH: [EmotionalState.JOYFUL, EmotionalState.CONFIDENT, EmotionalState.EXCITED],
            EmotionalTriggerType.SOCIAL_HUMILIATION: [EmotionalState.ANGRY, EmotionalState.DEPRESSED, EmotionalState.BITTER],
            EmotionalTriggerType.ECONOMIC_CHANGE: [EmotionalState.ANXIOUS, EmotionalState.HOPEFUL, EmotionalState.ANGRY],
            EmotionalTriggerType.POLITICAL_EVENT: [EmotionalState.ANGRY, EmotionalState.HOPEFUL, EmotionalState.FEARFUL],
            EmotionalTriggerType.LOYALTY_REWARD: [EmotionalState.JOYFUL, EmotionalState.CONFIDENT, EmotionalState.CONTENT],
            EmotionalTriggerType.SEASONAL_CHANGE: [EmotionalState.MELANCHOLY, EmotionalState.HOPEFUL, EmotionalState.CONTENT],
            EmotionalTriggerType.HEALTH_CHANGE: [EmotionalState.FEARFUL, EmotionalState.HOPEFUL, EmotionalState.ANXIOUS]
        }
        
        possible_emotions = trigger_emotion_map.get(trigger_type, [EmotionalState.NEUTRAL])
        
        # Choose emotion based on NPC's personality and current state
        best_emotion = emotional_state.current_emotion
        best_score = 0.0
        
        for emotion in possible_emotions:
            score = self._calculate_emotion_compatibility(emotional_state, emotion, trigger_severity)
            if score > best_score:
                best_score = score
                best_emotion = emotion
        
        # Calculate change magnitude based on emotional volatility and trigger severity
        volatility_factor = emotional_state.emotional_volatility / 10.0
        change_magnitude = trigger_severity * volatility_factor
        
        return best_emotion, change_magnitude
    
    def _calculate_emotion_compatibility(self, emotional_state: NpcEmotionalState, 
                                       target_emotion: EmotionalState, 
                                       trigger_severity: float) -> float:
        """Calculate how compatible a target emotion is with the NPC's current state"""
        base_score = trigger_severity
        
        # Personality factors
        if target_emotion in [EmotionalState.JOYFUL, EmotionalState.EXCITED]:
            # More likely if high optimism and low stress
            base_score += (emotional_state.optimism_level / 10.0) * 2
            base_score -= (emotional_state.stress_level / 10.0) * 1
        
        elif target_emotion in [EmotionalState.ANGRY, EmotionalState.BITTER]:
            # More likely if low stress tolerance and high stress
            base_score += (emotional_state.stress_level / 10.0) * 2
            base_score -= (emotional_state.stress_tolerance / 10.0) * 1
        
        elif target_emotion in [EmotionalState.FEARFUL, EmotionalState.ANXIOUS]:
            # More likely if low confidence and high stress
            base_score -= (emotional_state.confidence_level / 10.0) * 1
            base_score += (emotional_state.stress_level / 10.0) * 1
        
        elif target_emotion in [EmotionalState.CONFIDENT, EmotionalState.DETERMINED]:
            # More likely if high confidence and optimism
            base_score += (emotional_state.confidence_level / 10.0) * 2
            base_score += (emotional_state.optimism_level / 10.0) * 1
        
        # Emotional stability affects resistance to change
        stability_resistance = emotional_state.emotion_stability / 10.0
        if target_emotion != emotional_state.current_emotion:
            base_score -= stability_resistance * 2
        
        return max(0.0, base_score)
    
    def _update_emotional_dimensions(self, emotional_state: NpcEmotionalState, 
                                   trigger_type: EmotionalTriggerType, 
                                   trigger_severity: float):
        """Update emotional dimensions based on trigger"""
        intensity_factor = trigger_severity / 10.0
        
        # Define how different triggers affect emotional dimensions
        dimension_effects = {
            EmotionalTriggerType.GOAL_SUCCESS: {
                "happiness_level": 2.0, "confidence_level": 1.5, "energy_level": 1.0, "stress_level": -1.0
            },
            EmotionalTriggerType.GOAL_FAILURE: {
                "happiness_level": -2.0, "confidence_level": -1.5, "stress_level": 1.5, "optimism_level": -1.0
            },
            EmotionalTriggerType.BETRAYAL: {
                "happiness_level": -3.0, "stress_level": 2.0, "sociability_level": -2.0, "optimism_level": -2.0
            },
            EmotionalTriggerType.LOSS_OF_LOVED_ONE: {
                "happiness_level": -4.0, "energy_level": -2.0, "sociability_level": -2.0, "stress_level": 3.0
            },
            EmotionalTriggerType.SOCIAL_TRIUMPH: {
                "happiness_level": 2.0, "confidence_level": 2.0, "sociability_level": 1.0, "energy_level": 1.0
            },
            EmotionalTriggerType.SOCIAL_HUMILIATION: {
                "happiness_level": -2.0, "confidence_level": -2.5, "sociability_level": -1.5, "stress_level": 2.0
            },
            EmotionalTriggerType.PHYSICAL_DANGER: {
                "stress_level": 3.0, "energy_level": 1.0, "confidence_level": -1.0
            },
            EmotionalTriggerType.LOYALTY_REWARD: {
                "happiness_level": 1.5, "confidence_level": 1.0, "optimism_level": 1.0, "stress_level": -0.5
            }
        }
        
        effects = dimension_effects.get(trigger_type, {})
        
        for dimension, change in effects.items():
            current_value = getattr(emotional_state, dimension)
            new_value = max(-10, min(10, current_value + (change * intensity_factor)))
            setattr(emotional_state, dimension, new_value)
    
    def _calculate_trigger_duration(self, trigger_type: EmotionalTriggerType, 
                                  trigger_severity: float) -> int:
        """Calculate how long an emotional trigger's effects should last"""
        base_duration = {
            EmotionalTriggerType.GOAL_SUCCESS: 3,
            EmotionalTriggerType.GOAL_FAILURE: 7,
            EmotionalTriggerType.BETRAYAL: 30,
            EmotionalTriggerType.LOSS_OF_LOVED_ONE: 90,
            EmotionalTriggerType.SOCIAL_TRIUMPH: 5,
            EmotionalTriggerType.SOCIAL_HUMILIATION: 14,
            EmotionalTriggerType.PHYSICAL_DANGER: 2,
            EmotionalTriggerType.LOYALTY_REWARD: 7,
            EmotionalTriggerType.ECONOMIC_CHANGE: 10,
            EmotionalTriggerType.POLITICAL_EVENT: 5,
            EmotionalTriggerType.SEASONAL_CHANGE: 30,
            EmotionalTriggerType.HEALTH_CHANGE: 14
        }
        
        duration = base_duration.get(trigger_type, 5)
        severity_multiplier = trigger_severity / 5.0
        
        return max(1, int(duration * severity_multiplier))
    
    def _create_emotional_memory(self, npc_id: UUID, trigger_type: EmotionalTriggerType,
                               description: str, emotion: EmotionalState, intensity: float,
                               location: Optional[str], related_entity_id: Optional[str],
                               related_entity_type: Optional[str]):
        """Create a significant emotional memory"""
        
        # Determine memory type
        memory_type_map = {
            EmotionalTriggerType.BETRAYAL: "trauma",
            EmotionalTriggerType.LOSS_OF_LOVED_ONE: "trauma",
            EmotionalTriggerType.GOAL_SUCCESS: "triumph",
            EmotionalTriggerType.SOCIAL_TRIUMPH: "triumph",
            EmotionalTriggerType.LOYALTY_REWARD: "joy",
            EmotionalTriggerType.SOCIAL_HUMILIATION: "trauma",
            EmotionalTriggerType.PHYSICAL_DANGER: "trauma"
        }
        
        memory_type = memory_type_map.get(trigger_type, "significant_event")
        
        # Create memory record
        memory = NpcEmotionalMemory(
            npc_id=npc_id,
            memory_type=memory_type,
            memory_description=description,
            memory_intensity=intensity,
            primary_emotion=emotion,
            memory_location=location,
            memory_clarity=intensity,  # Start with clarity equal to intensity
            emotional_charge=intensity,
            occurred_at=datetime.utcnow()
        )
        
        # Add related entities
        if related_entity_id and related_entity_type:
            memory.related_entities = [{"id": related_entity_id, "type": related_entity_type}]
        
        # Define behavioral effects based on memory type
        if memory_type == "trauma":
            memory.behavioral_effects = {
                "trust_modification": -0.3,
                "risk_aversion": 0.4,
                "social_withdrawal": 0.2
            }
            memory.triggers_on = ["similar_situation", "related_entity_encounter"]
        elif memory_type == "triumph":
            memory.behavioral_effects = {
                "confidence_boost": 0.3,
                "risk_taking": 0.2,
                "social_confidence": 0.2
            }
            memory.triggers_on = ["achievement_opportunity", "recognition_situation"]
        
        self.db_session.add(memory)
    
    def process_daily_emotional_decay(self, npc_id: UUID) -> Dict[str, Any]:
        """Process daily emotional state changes and decay toward baseline"""
        emotional_state = self.get_or_create_emotional_state(npc_id)
        
        # Increment days in current state
        emotional_state.days_in_current_state += 1
        
        # Apply emotional decay toward baseline
        recovery_rate = emotional_state.emotional_recovery_rate / 10.0
        decay_factor = self.emotional_decay_rate * recovery_rate
        
        # Decay emotional dimensions toward neutral (0)
        dimensions = ['happiness_level', 'energy_level', 'stress_level', 
                     'confidence_level', 'sociability_level', 'optimism_level']
        
        changes = {}
        for dimension in dimensions:
            current_value = getattr(emotional_state, dimension)
            if abs(current_value) > 0.1:  # Only decay if not already near neutral
                new_value = current_value * (1.0 - decay_factor)
                setattr(emotional_state, dimension, new_value)
                changes[dimension] = new_value - current_value
        
        # Check if emotion should return to baseline
        if (emotional_state.days_in_current_state > 7 and 
            emotional_state.current_emotion != emotional_state.baseline_emotion):
            
            # Calculate probability of returning to baseline
            baseline_probability = 0.1 + (emotional_state.days_in_current_state * 0.05)
            baseline_probability *= recovery_rate
            
            if random.random() < baseline_probability:
                emotional_state.current_emotion = emotional_state.baseline_emotion
                emotional_state.emotion_intensity = random.uniform(3.0, 6.0)
                emotional_state.days_in_current_state = 0
                changes["returned_to_baseline"] = True
        
        # Update timestamp
        emotional_state.last_updated = datetime.utcnow()
        
        self.db_session.commit()
        
        return {
            "npc_id": str(npc_id),
            "current_emotion": emotional_state.current_emotion.value,
            "days_in_state": emotional_state.days_in_current_state,
            "changes": changes
        }
    
    def apply_environmental_effects(self, npc_id: UUID, weather: str, 
                                  season: str = None) -> Dict[str, Any]:
        """Apply weather and environmental effects to emotional state"""
        emotional_state = self.get_or_create_emotional_state(npc_id)
        
        if weather not in self.weather_effects:
            return {"applied": False, "reason": "unknown_weather"}
        
        weather_sensitivity = emotional_state.weather_sensitivity / 10.0
        effects = self.weather_effects[weather]
        
        applied_effects = {}
        
        # Apply weather effects based on NPC's sensitivity
        for dimension, effect in effects.items():
            if dimension in ['happiness_level', 'energy_level', 'stress_level', 
                           'confidence_level', 'sociability_level', 'optimism_level']:
                current_value = getattr(emotional_state, dimension)
                change = effect * weather_sensitivity
                new_value = max(-10, min(10, current_value + change))
                setattr(emotional_state, dimension, new_value)
                applied_effects[dimension] = change
        
        # Create environmental influence record
        influence = NpcEmotionalInfluence(
            npc_id=npc_id,
            emotional_state_id=emotional_state.id,
            influence_type="weather",
            influence_source=weather,
            influence_description=f"Weather effect: {weather}",
            influence_strength=weather_sensitivity,
            is_temporary=True,
            duration_days=1  # Weather effects last 1 day
        )
        
        # Set specific modifiers based on weather
        for dimension, effect in effects.items():
            if hasattr(influence, f"{dimension}_modifier"):
                setattr(influence, f"{dimension}_modifier", effect)
        
        self.db_session.add(influence)
        self.db_session.commit()
        
        return {
            "applied": True,
            "weather": weather,
            "sensitivity": weather_sensitivity,
            "effects": applied_effects,
            "influence_id": str(influence.id)
        }
    
    def get_emotional_decision_modifiers(self, npc_id: UUID) -> Dict[str, float]:
        """Get decision-making modifiers based on current emotional state"""
        emotional_state = self.get_or_create_emotional_state(npc_id)
        return emotional_state.get_decision_modifiers()
    
    def get_emotional_state_summary(self, npc_id: UUID) -> Dict[str, Any]:
        """Get comprehensive emotional state summary for an NPC"""
        emotional_state = self.get_or_create_emotional_state(npc_id)
        
        # Get recent triggers
        recent_triggers = self.db_session.query(NpcEmotionalTrigger).filter(
            NpcEmotionalTrigger.npc_id == npc_id,
            NpcEmotionalTrigger.occurred_at >= datetime.utcnow() - timedelta(days=30)
        ).order_by(NpcEmotionalTrigger.occurred_at.desc()).limit(5).all()
        
        # Get active influences
        active_influences = self.db_session.query(NpcEmotionalInfluence).filter(
            NpcEmotionalInfluence.npc_id == npc_id,
            NpcEmotionalInfluence.is_active == True
        ).all()
        
        # Get significant memories
        significant_memories = self.db_session.query(NpcEmotionalMemory).filter(
            NpcEmotionalMemory.npc_id == npc_id,
            NpcEmotionalMemory.memory_clarity > 5.0
        ).order_by(NpcEmotionalMemory.emotional_charge.desc()).limit(10).all()
        
        return {
            "npc_id": str(npc_id),
            "current_emotion": emotional_state.current_emotion.value,
            "emotion_intensity": emotional_state.emotion_intensity,
            "mood_description": emotional_state.get_mood_description(),
            "days_in_current_state": emotional_state.days_in_current_state,
            "emotional_dimensions": {
                "happiness": emotional_state.happiness_level,
                "energy": emotional_state.energy_level,
                "stress": emotional_state.stress_level,
                "confidence": emotional_state.confidence_level,
                "sociability": emotional_state.sociability_level,
                "optimism": emotional_state.optimism_level
            },
            "decision_modifiers": emotional_state.get_decision_modifiers(),
            "recent_triggers": [
                {
                    "type": trigger.trigger_type.value,
                    "description": trigger.trigger_description,
                    "severity": trigger.trigger_severity,
                    "days_ago": trigger.days_since_trigger()
                }
                for trigger in recent_triggers
            ],
            "active_influences": [
                {
                    "type": influence.influence_type,
                    "source": influence.influence_source,
                    "strength": influence.calculate_current_strength(),
                    "description": influence.influence_description
                }
                for influence in active_influences
            ],
            "significant_memories": [
                {
                    "type": memory.memory_type,
                    "description": memory.memory_description,
                    "emotion": memory.primary_emotion.value,
                    "intensity": memory.memory_intensity,
                    "clarity": memory.memory_clarity
                }
                for memory in significant_memories
            ]
        } 