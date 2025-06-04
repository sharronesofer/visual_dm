"""
Personality Evolution Service

Handles dynamic personality changes based on experiences and allows 
the LLM to modify NPC hidden attributes organically over time.
"""

import logging
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID

from backend.infrastructure.systems.npc.models.personality_evolution_models import (
    NpcPersonalityEvolution, NpcPersonalitySnapshot, NpcMemoryEvolution, 
    NpcCrisisResponse, PersonalityChangeType
)
from backend.infrastructure.systems.npc.models.models import NpcEntity
from backend.infrastructure.systems.npc.models.autonomous_lifecycle_models import NpcGoal, NpcLifeEvent

logger = logging.getLogger(__name__)


class PersonalityEvolutionService:
    """Service for managing dynamic personality evolution"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        
        # Evolution parameters
        self.personality_change_threshold = 7.0  # Event severity needed for personality change
        self.max_attribute_change = 3.0          # Maximum change to any attribute per event
        self.snapshot_frequency_days = 90        # How often to take personality snapshots
        
        # Attribute change probabilities by event type
        self.change_probabilities = {
            "goal_success": {"hidden_ambition": 0.3, "hidden_resilience": 0.2, "hidden_discipline": 0.1},
            "goal_failure": {"hidden_resilience": 0.4, "hidden_impulsivity": 0.2, "hidden_pragmatism": 0.3},
            "betrayal": {"hidden_integrity": 0.5, "hidden_pragmatism": 0.4, "hidden_resilience": 0.3},
            "leadership_success": {"hidden_ambition": 0.4, "hidden_integrity": 0.2, "hidden_discipline": 0.3},
            "trauma": {"hidden_resilience": 0.6, "hidden_impulsivity": 0.3, "hidden_integrity": 0.2},
            "relationship_loss": {"hidden_resilience": 0.4, "hidden_integrity": 0.2},
            "economic_success": {"hidden_ambition": 0.3, "hidden_pragmatism": 0.2, "hidden_discipline": 0.1},
            "social_triumph": {"hidden_ambition": 0.2, "hidden_integrity": 0.1},
            "crisis_survival": {"hidden_resilience": 0.5, "hidden_pragmatism": 0.4, "hidden_discipline": 0.3}
        }
    
    def evaluate_personality_change(self, npc_id: UUID, event_type: str, 
                                   event_description: str, event_severity: float,
                                   event_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Evaluate if an event should trigger personality changes"""
        
        if event_severity < self.personality_change_threshold:
            return {"change_triggered": False, "reason": "insufficient_severity"}
        
        npc = self.db_session.query(NpcEntity).filter_by(id=npc_id).first()
        if not npc:
            return {"change_triggered": False, "reason": "npc_not_found"}
        
        # Check if this NPC is prone to personality changes
        change_resistance = self._calculate_change_resistance(npc)
        base_probability = self.change_probabilities.get(event_type, {})
        
        if not base_probability:
            return {"change_triggered": False, "reason": "no_change_mapping"}
        
        # Determine which attributes might change
        potential_changes = {}
        for attribute, probability in base_probability.items():
            # Adjust probability based on event severity and NPC resistance
            adjusted_probability = probability * (event_severity / 10.0) * (1.0 / change_resistance)
            
            if random.random() < adjusted_probability:
                current_value = getattr(npc, attribute, 5.0) or 5.0
                change_amount = self._calculate_attribute_change(event_type, attribute, event_severity)
                new_value = max(1.0, min(10.0, current_value + change_amount))
                
                potential_changes[attribute] = {
                    "from": current_value,
                    "to": new_value,
                    "change": change_amount
                }
        
        if not potential_changes:
            return {"change_triggered": False, "reason": "no_changes_passed_probability"}
        
        # Create personality evolution record
        change_type = self._determine_change_type(event_type, event_severity)
        evolution_record = self._create_personality_evolution(
            npc_id, change_type, event_description, event_severity, 
            potential_changes, event_type, event_context
        )
        
        # Take snapshot before changes
        self._take_personality_snapshot(npc_id, "milestone", f"before_{event_type}")
        
        return {
            "change_triggered": True,
            "evolution_id": str(evolution_record.id),
            "attributes_changing": potential_changes,
            "change_type": change_type.value,
            "estimated_completion_days": evolution_record.adaptation_period_days
        }
    
    def _calculate_change_resistance(self, npc: NpcEntity) -> float:
        """Calculate how resistant an NPC is to personality changes"""
        # Higher discipline and integrity = more resistance to change
        discipline = getattr(npc, 'hidden_discipline', 5.0) or 5.0
        integrity = getattr(npc, 'hidden_integrity', 5.0) or 5.0
        
        # Age factor - older NPCs resist change more
        age_factor = 1.0
        if hasattr(npc, 'age') and npc.age:
            if npc.age > 50:
                age_factor = 1.5
            elif npc.age > 30:
                age_factor = 1.2
        
        resistance = ((discipline + integrity) / 2.0) * age_factor / 5.0
        return max(0.5, min(3.0, resistance))
    
    def _calculate_attribute_change(self, event_type: str, attribute: str, 
                                  event_severity: float) -> float:
        """Calculate how much an attribute should change"""
        
        # Base change amount based on severity
        base_change = (event_severity - 5.0) / 5.0 * self.max_attribute_change
        
        # Event-specific modifiers
        event_modifiers = {
            "betrayal": {"hidden_integrity": -1.0, "hidden_pragmatism": 1.0},
            "goal_success": {"hidden_ambition": 0.5, "hidden_resilience": 0.3},
            "goal_failure": {"hidden_resilience": 0.4, "hidden_impulsivity": 0.2},
            "trauma": {"hidden_resilience": 0.6, "hidden_impulsivity": -0.3},
            "leadership_success": {"hidden_ambition": 0.4, "hidden_integrity": 0.2}
        }
        
        modifier = event_modifiers.get(event_type, {}).get(attribute, 0.0)
        final_change = base_change + modifier
        
        return max(-self.max_attribute_change, min(self.max_attribute_change, final_change))
    
    def _determine_change_type(self, event_type: str, event_severity: float) -> PersonalityChangeType:
        """Determine the type of personality change"""
        
        if event_severity >= 9.0:
            return PersonalityChangeType.TRAUMATIC_CHANGE
        elif event_type in ["crisis_survival", "betrayal", "trauma"]:
            return PersonalityChangeType.CRISIS_RESPONSE
        elif event_type in ["goal_success", "leadership_success"]:
            return PersonalityChangeType.SUCCESS_ADAPTATION
        elif event_type.startswith("relationship"):
            return PersonalityChangeType.RELATIONSHIP_INFLUENCE
        else:
            return PersonalityChangeType.GRADUAL_SHIFT
    
    def _create_personality_evolution(self, npc_id: UUID, change_type: PersonalityChangeType,
                                    description: str, severity: float, 
                                    attribute_changes: Dict[str, Dict],
                                    trigger_event_type: str, 
                                    context: Dict[str, Any] = None) -> NpcPersonalityEvolution:
        """Create a personality evolution record"""
        
        npc = self.db_session.query(NpcEntity).filter_by(id=npc_id).first()
        
        # Calculate adaptation period based on change magnitude and type
        total_change = sum(abs(change["change"]) for change in attribute_changes.values())
        base_period = 30  # days
        
        if change_type == PersonalityChangeType.TRAUMATIC_CHANGE:
            adaptation_period = base_period * 3
        elif change_type == PersonalityChangeType.CRISIS_RESPONSE:
            adaptation_period = base_period * 2
        else:
            adaptation_period = base_period
        
        adaptation_period = int(adaptation_period * (total_change / 2.0))  # Scale by change amount
        
        evolution = NpcPersonalityEvolution(
            npc_id=npc_id,
            change_type=change_type,
            change_description=description,
            change_magnitude=total_change,
            attributes_changed=attribute_changes,
            trigger_event_type=trigger_event_type,
            life_stage_at_change=getattr(npc, 'lifecycle_phase', 'unknown'),
            age_at_change=getattr(npc, 'age', 0),
            social_context=context.get('social_context', '') if context else '',
            change_resistance=self._calculate_change_resistance(npc),
            adaptation_period_days=adaptation_period
        )
        
        self.db_session.add(evolution)
        self.db_session.commit()
        
        return evolution
    
    def process_daily_personality_evolution(self, npc_id: UUID) -> Dict[str, Any]:
        """Process ongoing personality changes for an NPC"""
        
        active_evolutions = self.db_session.query(NpcPersonalityEvolution).filter(
            NpcPersonalityEvolution.npc_id == npc_id,
            NpcPersonalityEvolution.is_complete == False
        ).all()
        
        if not active_evolutions:
            return {"evolutions_processed": 0}
        
        npc = self.db_session.query(NpcEntity).filter_by(id=npc_id).first()
        changes_applied = {}
        completed_evolutions = []
        
        for evolution in active_evolutions:
            # Calculate daily progression
            daily_progress = evolution.calculate_daily_progression()
            evolution.progress_percentage += daily_progress
            evolution.last_progression = datetime.utcnow()
            
            # Apply current attribute values to NPC
            current_values = evolution.get_current_attribute_values()
            for attribute, value in current_values.items():
                if hasattr(npc, attribute):
                    setattr(npc, attribute, round(value, 2))
                    changes_applied[attribute] = value
            
            # Check if evolution is complete
            if evolution.progress_percentage >= 100.0:
                evolution.is_complete = True
                evolution.completed_at = datetime.utcnow()
                evolution.progress_percentage = 100.0
                completed_evolutions.append(evolution.id)
                
                # Create completion memory
                self._create_evolution_memory(npc_id, evolution)
        
        # Take periodic snapshot if needed
        self._check_for_periodic_snapshot(npc_id)
        
        self.db_session.commit()
        
        return {
            "evolutions_processed": len(active_evolutions),
            "completed_evolutions": len(completed_evolutions),
            "current_attribute_changes": changes_applied,
            "completed_evolution_ids": [str(eid) for eid in completed_evolutions]
        }
    
    def _create_evolution_memory(self, npc_id: UUID, evolution: NpcPersonalityEvolution):
        """Create a memory record for completed personality evolution"""
        
        memory_content = f"I have grown and changed as a person. {evolution.change_description} " \
                        f"This experience has made me more {self._describe_attribute_changes(evolution.attributes_changed)}."
        
        memory = NpcMemoryEvolution(
            npc_id=npc_id,
            memory_category="personality_growth",
            memory_content=memory_content,
            memory_importance=min(10.0, evolution.change_magnitude + 3.0),
            learned_from_entity_type="experience",
            learning_context=f"{evolution.change_type.value} triggered by {evolution.trigger_event_type}",
            behavior_modifications=self._calculate_behavior_modifications(evolution.attributes_changed),
            decision_weight=evolution.change_magnitude / 5.0
        )
        
        self.db_session.add(memory)
    
    def _describe_attribute_changes(self, attribute_changes: Dict[str, Dict]) -> str:
        """Create a human-readable description of attribute changes"""
        descriptions = []
        
        for attribute, change_data in attribute_changes.items():
            change_amount = change_data["to"] - change_data["from"]
            
            if attribute == "hidden_resilience":
                if change_amount > 0:
                    descriptions.append("resilient and able to bounce back from setbacks")
                else:
                    descriptions.append("more vulnerable to stress and challenges")
            elif attribute == "hidden_ambition":
                if change_amount > 0:
                    descriptions.append("driven and ambitious in pursuing my goals")
                else:
                    descriptions.append("content with simpler achievements")
            elif attribute == "hidden_integrity":
                if change_amount > 0:
                    descriptions.append("principled and committed to doing what's right")
                else:
                    descriptions.append("pragmatic about bending rules when necessary")
            elif attribute == "hidden_discipline":
                if change_amount > 0:
                    descriptions.append("disciplined and methodical in my approach")
                else:
                    descriptions.append("spontaneous and flexible in my methods")
            elif attribute == "hidden_pragmatism":
                if change_amount > 0:
                    descriptions.append("practical and realistic about what can be achieved")
                else:
                    descriptions.append("idealistic about possibilities")
            elif attribute == "hidden_impulsivity":
                if change_amount > 0:
                    descriptions.append("quick to act on my instincts")
                else:
                    descriptions.append("careful and deliberate in my decisions")
        
        return ", ".join(descriptions)
    
    def _calculate_behavior_modifications(self, attribute_changes: Dict[str, Dict]) -> Dict[str, float]:
        """Calculate how attribute changes affect behavior patterns"""
        
        modifications = {}
        
        for attribute, change_data in attribute_changes.items():
            change_amount = change_data["to"] - change_data["from"]
            change_magnitude = abs(change_amount) / 10.0  # Normalize to 0-1
            
            if attribute == "hidden_resilience":
                modifications["stress_tolerance"] = change_amount * 0.2
                modifications["recovery_speed"] = change_amount * 0.15
            elif attribute == "hidden_ambition":
                modifications["goal_pursuit_intensity"] = change_amount * 0.25
                modifications["risk_taking"] = change_amount * 0.15
            elif attribute == "hidden_integrity":
                modifications["honesty_preference"] = change_amount * 0.3
                modifications["loyalty_strength"] = change_amount * 0.2
            elif attribute == "hidden_discipline":
                modifications["planning_tendency"] = change_amount * 0.25
                modifications["consistency"] = change_amount * 0.2
            elif attribute == "hidden_pragmatism":
                modifications["practical_focus"] = change_amount * 0.2
                modifications["idealism"] = -change_amount * 0.15
            elif attribute == "hidden_impulsivity":
                modifications["quick_decisions"] = change_amount * 0.2
                modifications["spontaneity"] = change_amount * 0.15
        
        return modifications
    
    def _take_personality_snapshot(self, npc_id: UUID, snapshot_type: str, 
                                 triggered_by: str) -> NpcPersonalitySnapshot:
        """Take a snapshot of NPC's current personality"""
        
        npc = self.db_session.query(NpcEntity).filter_by(id=npc_id).first()
        if not npc:
            return None
        
        # Gather current personality attributes
        personality_attributes = {}
        for attr in ['hidden_resilience', 'hidden_ambition', 'hidden_integrity', 
                    'hidden_discipline', 'hidden_pragmatism', 'hidden_impulsivity']:
            personality_attributes[attr] = getattr(npc, attr, 5.0) or 5.0
        
        # Get current goals
        current_goals = self.db_session.query(NpcGoal).filter(
            NpcGoal.npc_id == npc_id,
            NpcGoal.is_active == True
        ).limit(5).all()
        
        major_goals = [{"id": str(goal.id), "description": goal.goal_description} 
                      for goal in current_goals]
        
        # Get recent life events
        recent_events = self.db_session.query(NpcLifeEvent).filter(
            NpcLifeEvent.npc_id == npc_id,
            NpcLifeEvent.event_date >= datetime.utcnow() - timedelta(days=90)
        ).order_by(NpcLifeEvent.event_date.desc()).limit(5).all()
        
        life_events_summary = "; ".join([event.event_description for event in recent_events])
        
        snapshot = NpcPersonalitySnapshot(
            npc_id=npc_id,
            npc_age_at_snapshot=getattr(npc, 'age', 0),
            life_stage_at_snapshot=getattr(npc, 'lifecycle_phase', 'unknown'),
            personality_attributes=personality_attributes,
            major_goals=major_goals,
            life_events_summary=life_events_summary[:500],  # Truncate if too long
            snapshot_type=snapshot_type,
            triggered_by=triggered_by
        )
        
        self.db_session.add(snapshot)
        self.db_session.commit()
        
        return snapshot
    
    def _check_for_periodic_snapshot(self, npc_id: UUID):
        """Check if it's time for a periodic personality snapshot"""
        
        last_snapshot = self.db_session.query(NpcPersonalitySnapshot).filter(
            NpcPersonalitySnapshot.npc_id == npc_id,
            NpcPersonalitySnapshot.snapshot_type == "periodic"
        ).order_by(NpcPersonalitySnapshot.snapshot_date.desc()).first()
        
        if not last_snapshot:
            # Take first snapshot
            self._take_personality_snapshot(npc_id, "periodic", "initial_snapshot")
        else:
            days_since_last = (datetime.utcnow() - last_snapshot.snapshot_date).days
            if days_since_last >= self.snapshot_frequency_days:
                self._take_personality_snapshot(npc_id, "periodic", "scheduled_snapshot")
    
    def create_learned_memory(self, npc_id: UUID, memory_category: str, 
                            memory_content: str, learned_from_entity_id: str = None,
                            learned_from_entity_type: str = None, 
                            learning_context: str = None,
                            importance: float = 5.0) -> NpcMemoryEvolution:
        """Create a new learned memory for an NPC"""
        
        memory = NpcMemoryEvolution(
            npc_id=npc_id,
            memory_category=memory_category,
            memory_content=memory_content,
            memory_importance=importance,
            learned_from_entity_id=learned_from_entity_id,
            learned_from_entity_type=learned_from_entity_type,
            learning_context=learning_context,
            decision_weight=importance / 10.0
        )
        
        self.db_session.add(memory)
        self.db_session.commit()
        
        return memory
    
    def recall_memories(self, npc_id: UUID, context: str, limit: int = 5) -> List[NpcMemoryEvolution]:
        """Recall relevant memories based on context"""
        
        memories = self.db_session.query(NpcMemoryEvolution).filter(
            NpcMemoryEvolution.npc_id == npc_id,
            NpcMemoryEvolution.memory_strength > 2.0  # Only recall memories that aren't too faded
        ).order_by(
            NpcMemoryEvolution.memory_importance.desc(),
            NpcMemoryEvolution.last_recalled.desc().nullslast()
        ).limit(limit * 2).all()  # Get more than needed for filtering
        
        # Simple relevance scoring based on keyword matching
        relevant_memories = []
        context_words = set(context.lower().split())
        
        for memory in memories:
            memory_words = set(memory.memory_content.lower().split())
            relevance_score = len(context_words.intersection(memory_words))
            
            if relevance_score > 0 or memory.memory_importance > 8.0:
                memory.recall_memory()  # This updates recall count and strength
                relevant_memories.append(memory)
                
                if len(relevant_memories) >= limit:
                    break
        
        self.db_session.commit()
        return relevant_memories
    
    def process_memory_fade(self, npc_id: UUID, days_passed: int = 1) -> Dict[str, Any]:
        """Process memory fading over time"""
        
        memories = self.db_session.query(NpcMemoryEvolution).filter(
            NpcMemoryEvolution.npc_id == npc_id,
            NpcMemoryEvolution.memory_strength > 0.1
        ).all()
        
        faded_memories = []
        forgotten_memories = []
        
        for memory in memories:
            old_strength = memory.memory_strength
            memory.fade_memory(days_passed)
            
            if memory.memory_strength <= 0.1:
                forgotten_memories.append(memory.id)
            elif old_strength - memory.memory_strength > 0.5:
                faded_memories.append({
                    "id": memory.id,
                    "old_strength": old_strength,
                    "new_strength": memory.memory_strength
                })
        
        self.db_session.commit()
        
        return {
            "processed_memories": len(memories),
            "faded_memories": len(faded_memories),
            "forgotten_memories": len(forgotten_memories)
        }
    
    def get_personality_evolution_summary(self, npc_id: UUID) -> Dict[str, Any]:
        """Get comprehensive personality evolution summary"""
        
        # Get personality changes
        recent_changes = self.db_session.query(NpcPersonalityEvolution).filter(
            NpcPersonalityEvolution.npc_id == npc_id,
            NpcPersonalityEvolution.started_at >= datetime.utcnow() - timedelta(days=365)
        ).order_by(NpcPersonalityEvolution.started_at.desc()).all()
        
        # Get personality snapshots
        snapshots = self.db_session.query(NpcPersonalitySnapshot).filter(
            NpcPersonalitySnapshot.npc_id == npc_id
        ).order_by(NpcPersonalitySnapshot.snapshot_date.desc()).limit(5).all()
        
        # Get recent memories
        recent_memories = self.db_session.query(NpcMemoryEvolution).filter(
            NpcMemoryEvolution.npc_id == npc_id,
            NpcMemoryEvolution.memory_strength > 3.0
        ).order_by(NpcMemoryEvolution.memory_importance.desc()).limit(10).all()
        
        return {
            "npc_id": str(npc_id),
            "recent_personality_changes": [
                {
                    "type": change.change_type.value,
                    "description": change.change_description,
                    "attributes_changed": change.attributes_changed,
                    "progress": change.progress_percentage,
                    "started": change.started_at.isoformat()
                }
                for change in recent_changes
            ],
            "personality_snapshots": [
                {
                    "date": snapshot.snapshot_date.isoformat(),
                    "type": snapshot.snapshot_type,
                    "attributes": snapshot.personality_attributes,
                    "life_stage": snapshot.life_stage_at_snapshot
                }
                for snapshot in snapshots
            ],
            "significant_memories": [
                {
                    "category": memory.memory_category,
                    "content": memory.memory_content[:200] + "..." if len(memory.memory_content) > 200 else memory.memory_content,
                    "importance": memory.memory_importance,
                    "strength": memory.memory_strength,
                    "recall_count": memory.recall_count
                }
                for memory in recent_memories
            ]
        } 