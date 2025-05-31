"""
NPC Event Publisher
------------------
Utility class for publishing NPC events to the event system.
This centralizes event publishing and ensures consistent event handling.
"""

import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

logger = logging.getLogger(__name__)

# Import event dispatcher
try:
    from backend.infrastructure.events import get_dispatcher
    HAS_EVENT_DISPATCHER = True
except ImportError:
    logger.warning("Event dispatcher not available, NPC events will not be published")
    HAS_EVENT_DISPATCHER = False

# Import NPC events - Fixed circular import by importing directly from events module
from .events import (
    # Core events
    NPCCreated, NPCUpdated, NPCDeleted, NPCStatusChanged,
    # Movement events
    NPCMoved, NPCMigrationScheduled,
    # Memory events
    NPCMemoryCreated, NPCMemoryRecalled, NPCMemoryForgotten,
    # Faction events
    NPCFactionJoined, NPCFactionLeft, NPCFactionLoyaltyChanged,
    # Rumor events
    NPCRumorLearned, NPCRumorShared, NPCRumorForgotten,
    # Motif events
    NPCMotifApplied, NPCMotifCompleted, NPCMotifEvolved,
    # Goal events
    NPCGoalCreated, NPCGoalCompleted, NPCGoalAbandoned,
    # Social events
    NPCRelationshipFormed, NPCRelationshipChanged, NPCInteractionOccurred,
    # Task events
    NPCTaskScheduled, NPCTaskCompleted, NPCLoyaltyChanged,
    # Population events
    NPCPopulationChanged, NPCSystemStatistics,
    # System events
    NPCError, NPCDebugEvent,
)

class NPCEventPublisher:
    """Centralized event publisher for NPC system events."""
    
    def __init__(self):
        """Initialize the event publisher."""
        self.enabled = HAS_EVENT_DISPATCHER
        if self.enabled:
            self.dispatcher = get_dispatcher()
        else:
            self.dispatcher = None
            
    def _publish(self, event) -> bool:
        """Internal method to publish events."""
        if not self.enabled or not self.dispatcher:
            logger.debug(f"Event publishing disabled, skipping: {event.event_type}")
            return False
            
        try:
            self.dispatcher.publish_sync(event)
            logger.debug(f"Published event: {event.event_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type}: {e}")
            return False
    
    # Core NPC Events
    def publish_npc_created(self, npc_id: UUID, name: str, race: str, 
                           region_id: Optional[str] = None, location: Optional[str] = None,
                           npc_data: Optional[Dict[str, Any]] = None) -> bool:
        """Publish NPC created event."""
        event = NPCCreated(
            npc_id=npc_id,
            name=name,
            race=race,
            region_id=region_id,
            location=location,
            npc_data=npc_data
        )
        return self._publish(event)
    
    def publish_npc_updated(self, npc_id: UUID, changes: Dict[str, Any], 
                           old_values: Optional[Dict[str, Any]] = None) -> bool:
        """Publish NPC updated event."""
        event = NPCUpdated(
            npc_id=npc_id,
            changes=changes,
            old_values=old_values
        )
        return self._publish(event)
    
    def publish_npc_deleted(self, npc_id: UUID, name: str, soft_delete: bool = True) -> bool:
        """Publish NPC deleted event."""
        event = NPCDeleted(
            npc_id=npc_id,
            name=name,
            soft_delete=soft_delete
        )
        return self._publish(event)
    
    def publish_npc_status_changed(self, npc_id: UUID, old_status: str, new_status: str,
                                  reason: Optional[str] = None) -> bool:
        """Publish NPC status changed event."""
        event = NPCStatusChanged(
            npc_id=npc_id,
            old_status=old_status,
            new_status=new_status,
            reason=reason
        )
        return self._publish(event)
    
    # Movement Events
    def publish_npc_moved(self, npc_id: UUID, old_region_id: Optional[str], 
                         new_region_id: str, old_location: Optional[str], 
                         new_location: str, travel_motive: str = "wander",
                         activity: Optional[str] = None) -> bool:
        """Publish NPC moved event."""
        event = NPCMoved(
            npc_id=npc_id,
            old_region_id=old_region_id,
            new_region_id=new_region_id,
            old_location=old_location,
            new_location=new_location,
            travel_motive=travel_motive,
            activity=activity
        )
        return self._publish(event)
    
    def publish_npc_migration_scheduled(self, npc_ids: List[UUID], source_region: str,
                                      target_region: str, migration_reason: Optional[str] = None,
                                      estimated_arrival: Optional[datetime] = None) -> bool:
        """Publish NPC migration scheduled event."""
        event = NPCMigrationScheduled(
            npc_ids=npc_ids,
            source_region=source_region,
            target_region=target_region,
            migration_reason=migration_reason,
            estimated_arrival=estimated_arrival
        )
        return self._publish(event)
    
    # Memory Events
    def publish_npc_memory_created(self, npc_id: UUID, memory_id: str, content: str,
                                  memory_type: str, importance: float, emotion: Optional[str] = None,
                                  location: Optional[str] = None, participants: List[str] = None) -> bool:
        """Publish NPC memory created event."""
        event = NPCMemoryCreated(
            npc_id=npc_id,
            memory_id=memory_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            emotion=emotion,
            location=location,
            participants=participants or []
        )
        return self._publish(event)
    
    def publish_npc_memory_recalled(self, npc_id: UUID, memory_id: str, 
                                   recalled_count: int, importance: float) -> bool:
        """Publish NPC memory recalled event."""
        event = NPCMemoryRecalled(
            npc_id=npc_id,
            memory_id=memory_id,
            recalled_count=recalled_count,
            importance=importance
        )
        return self._publish(event)
    
    def publish_npc_memory_forgotten(self, npc_id: UUID, memory_id: str, reason: str) -> bool:
        """Publish NPC memory forgotten event."""
        event = NPCMemoryForgotten(
            npc_id=npc_id,
            memory_id=memory_id,
            reason=reason
        )
        return self._publish(event)
    
    # Faction Events
    def publish_npc_faction_joined(self, npc_id: UUID, faction_id: UUID, 
                                  role: str = "member", loyalty: float = 5.0) -> bool:
        """Publish NPC faction joined event."""
        event = NPCFactionJoined(
            npc_id=npc_id,
            faction_id=faction_id,
            role=role,
            loyalty=loyalty
        )
        return self._publish(event)
    
    def publish_npc_faction_left(self, npc_id: UUID, faction_id: UUID, role: str,
                                final_loyalty: float, reason: str) -> bool:
        """Publish NPC faction left event."""
        event = NPCFactionLeft(
            npc_id=npc_id,
            faction_id=faction_id,
            role=role,
            final_loyalty=final_loyalty,
            reason=reason
        )
        return self._publish(event)
    
    def publish_npc_faction_loyalty_changed(self, npc_id: UUID, faction_id: UUID,
                                          old_loyalty: float, new_loyalty: float,
                                          reason: Optional[str] = None) -> bool:
        """Publish NPC faction loyalty changed event."""
        event = NPCFactionLoyaltyChanged(
            npc_id=npc_id,
            faction_id=faction_id,
            old_loyalty=old_loyalty,
            new_loyalty=new_loyalty,
            reason=reason
        )
        return self._publish(event)
    
    # Rumor Events
    def publish_npc_rumor_learned(self, npc_id: UUID, rumor_id: str, content: str,
                                 credibility: float, source: Optional[str] = None) -> bool:
        """Publish NPC rumor learned event."""
        event = NPCRumorLearned(
            npc_id=npc_id,
            rumor_id=rumor_id,
            content=content,
            source=source,
            credibility=credibility
        )
        return self._publish(event)
    
    def publish_npc_rumor_shared(self, npc_id: UUID, rumor_id: str, credibility: float,
                                times_shared: int, target_npc_id: Optional[UUID] = None) -> bool:
        """Publish NPC rumor shared event."""
        event = NPCRumorShared(
            npc_id=npc_id,
            target_npc_id=target_npc_id,
            rumor_id=rumor_id,
            credibility=credibility,
            times_shared=times_shared
        )
        return self._publish(event)
    
    def publish_npc_rumor_forgotten(self, npc_id: UUID, rumor_id: str, reason: str) -> bool:
        """Publish NPC rumor forgotten event."""
        event = NPCRumorForgotten(
            npc_id=npc_id,
            rumor_id=rumor_id,
            reason=reason
        )
        return self._publish(event)
    
    # Motif Events
    def publish_npc_motif_applied(self, npc_id: UUID, motif_id: str, motif_type: str,
                                 strength: float, description: Optional[str] = None) -> bool:
        """Publish NPC motif applied event."""
        event = NPCMotifApplied(
            npc_id=npc_id,
            motif_id=motif_id,
            motif_type=motif_type,
            strength=strength,
            description=description
        )
        return self._publish(event)
    
    def publish_npc_motif_completed(self, npc_id: UUID, motif_id: str, motif_type: str,
                                   final_strength: float, outcome: str) -> bool:
        """Publish NPC motif completed event."""
        event = NPCMotifCompleted(
            npc_id=npc_id,
            motif_id=motif_id,
            motif_type=motif_type,
            final_strength=final_strength,
            outcome=outcome
        )
        return self._publish(event)
    
    def publish_npc_motif_evolved(self, npc_id: UUID, motif_id: str, old_strength: float,
                                 new_strength: float, entropy_change: float) -> bool:
        """Publish NPC motif evolved event."""
        event = NPCMotifEvolved(
            npc_id=npc_id,
            motif_id=motif_id,
            old_strength=old_strength,
            new_strength=new_strength,
            entropy_change=entropy_change
        )
        return self._publish(event)
    
    # Goal Events
    def publish_npc_goal_created(self, npc_id: UUID, goal_id: str, goal_type: str,
                                description: str, priority: str, 
                                estimated_duration: Optional[int] = None) -> bool:
        """Publish NPC goal created event."""
        event = NPCGoalCreated(
            npc_id=npc_id,
            goal_id=goal_id,
            goal_type=goal_type,
            description=description,
            priority=priority,
            estimated_duration=estimated_duration
        )
        return self._publish(event)
    
    def publish_npc_goal_completed(self, npc_id: UUID, goal_id: str, goal_type: str,
                                  success: bool, outcome_description: Optional[str] = None) -> bool:
        """Publish NPC goal completed event."""
        event = NPCGoalCompleted(
            npc_id=npc_id,
            goal_id=goal_id,
            goal_type=goal_type,
            success=success,
            outcome_description=outcome_description
        )
        return self._publish(event)
    
    def publish_npc_goal_abandoned(self, npc_id: UUID, goal_id: str, goal_type: str,
                                  reason: str, progress_lost: float = 0.0) -> bool:
        """Publish NPC goal abandoned event."""
        event = NPCGoalAbandoned(
            npc_id=npc_id,
            goal_id=goal_id,
            goal_type=goal_type,
            reason=reason,
            progress_lost=progress_lost
        )
        return self._publish(event)
    
    # Task Events
    def publish_npc_task_scheduled(self, npc_id: UUID, task_id: str, task_type: str,
                                  scheduled_time: datetime, estimated_duration: Optional[int] = None,
                                  task_data: Optional[Dict[str, Any]] = None) -> bool:
        """Publish NPC task scheduled event."""
        event = NPCTaskScheduled(
            npc_id=npc_id,
            task_id=task_id,
            task_type=task_type,
            scheduled_time=scheduled_time,
            estimated_duration=estimated_duration,
            task_data=task_data
        )
        return self._publish(event)
    
    def publish_npc_task_completed(self, npc_id: UUID, task_id: str, task_type: str,
                                  success: bool, duration_actual: int,
                                  rewards: Optional[Dict[str, Any]] = None) -> bool:
        """Publish NPC task completed event."""
        event = NPCTaskCompleted(
            npc_id=npc_id,
            task_id=task_id,
            task_type=task_type,
            success=success,
            duration_actual=duration_actual,
            rewards=rewards
        )
        return self._publish(event)
    
    def publish_npc_loyalty_changed(self, npc_id: UUID, old_loyalty: int, new_loyalty: int,
                                   goodwill_change: int = 0, target_id: Optional[str] = None,
                                   trigger: Optional[str] = None) -> bool:
        """Publish NPC loyalty changed event."""
        event = NPCLoyaltyChanged(
            npc_id=npc_id,
            target_id=target_id,
            old_loyalty=old_loyalty,
            new_loyalty=new_loyalty,
            goodwill_change=goodwill_change,
            trigger=trigger
        )
        return self._publish(event)
    
    # Population Events
    def publish_npc_population_changed(self, region_id: str, old_population: int,
                                      new_population: int, change_reason: str,
                                      affected_npcs: Optional[List[UUID]] = None) -> bool:
        """Publish NPC population changed event."""
        event = NPCPopulationChanged(
            region_id=region_id,
            old_population=old_population,
            new_population=new_population,
            change_reason=change_reason,
            affected_npcs=affected_npcs
        )
        return self._publish(event)
    
    def publish_npc_system_statistics(self, total_npcs: int, active_npcs: int,
                                     npcs_by_region: Dict[str, int], average_loyalty: float,
                                     total_memories: int, total_rumors: int, 
                                     total_motifs: int) -> bool:
        """Publish NPC system statistics event."""
        event = NPCSystemStatistics(
            total_npcs=total_npcs,
            active_npcs=active_npcs,
            npcs_by_region=npcs_by_region,
            average_loyalty=average_loyalty,
            total_memories=total_memories,
            total_rumors=total_rumors,
            total_motifs=total_motifs
        )
        return self._publish(event)
    
    # System Events
    def publish_npc_error(self, error_type: str, error_message: str, operation: str,
                         npc_id: Optional[UUID] = None, stack_trace: Optional[str] = None) -> bool:
        """Publish NPC error event."""
        event = NPCError(
            npc_id=npc_id,
            error_type=error_type,
            error_message=error_message,
            operation=operation,
            stack_trace=stack_trace
        )
        return self._publish(event)
    
    def publish_npc_debug_event(self, debug_type: str, debug_data: Dict[str, Any],
                               operation: str, npc_id: Optional[UUID] = None) -> bool:
        """Publish NPC debug event."""
        event = NPCDebugEvent(
            npc_id=npc_id,
            debug_type=debug_type,
            debug_data=debug_data,
            operation=operation
        )
        return self._publish(event)


# Global instance for easy access
_event_publisher = None

def get_npc_event_publisher() -> NPCEventPublisher:
    """Get the global NPC event publisher instance."""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = NPCEventPublisher()
    return _event_publisher 