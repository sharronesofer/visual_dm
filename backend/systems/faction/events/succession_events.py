"""
Faction Succession Events

This module defines events related to faction succession crises according to
Task 69 requirements. These events integrate with the broader event system.
"""

import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass

from backend.infrastructure.events.event_base import BaseEvent
from backend.systems.faction.models.succession import SuccessionTrigger, SuccessionType

logger = logging.getLogger(__name__)


@dataclass
class SuccessionCrisisTriggeredEvent(BaseEvent):
    """Event fired when a succession crisis is triggered"""
    
    event_type: str = "succession_crisis_triggered"
    faction_id: UUID = None
    faction_name: str = ""
    trigger: SuccessionTrigger = None
    succession_type: SuccessionType = None
    previous_leader_id: Optional[UUID] = None
    crisis_id: UUID = None
    estimated_duration: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "faction_id": str(self.faction_id),
            "faction_name": self.faction_name,
            "trigger": self.trigger.value if self.trigger else None,
            "succession_type": self.succession_type.value if self.succession_type else None,
            "previous_leader_id": str(self.previous_leader_id) if self.previous_leader_id else None,
            "crisis_id": str(self.crisis_id),
            "estimated_duration": self.estimated_duration,
            "metadata": self.metadata
        }


@dataclass
class SuccessionCandidateAnnouncedEvent(BaseEvent):
    """Event fired when a new candidate announces their bid for leadership"""
    
    event_type: str = "succession_candidate_announced"
    crisis_id: UUID = None
    faction_id: UUID = None
    candidate_id: UUID = None
    candidate_name: str = ""
    succession_type: SuccessionType = None
    campaign_strategy: Optional[str] = None
    qualifications: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "crisis_id": str(self.crisis_id),
            "faction_id": str(self.faction_id),
            "candidate_id": str(self.candidate_id),
            "candidate_name": self.candidate_name,
            "succession_type": self.succession_type.value if self.succession_type else None,
            "campaign_strategy": self.campaign_strategy,
            "qualifications": self.qualifications,
            "metadata": self.metadata
        }


@dataclass
class SuccessionCrisisAdvancedEvent(BaseEvent):
    """Event fired when succession crisis progresses (daily updates)"""
    
    event_type: str = "succession_crisis_advanced"
    crisis_id: UUID = None
    faction_id: UUID = None
    days_elapsed: int = 0
    faction_stability: float = 1.0
    leading_candidate_id: Optional[UUID] = None
    leading_candidate_name: Optional[str] = None
    instability_effects: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "crisis_id": str(self.crisis_id),
            "faction_id": str(self.faction_id),
            "days_elapsed": self.days_elapsed,
            "faction_stability": self.faction_stability,
            "leading_candidate_id": str(self.leading_candidate_id) if self.leading_candidate_id else None,
            "leading_candidate_name": self.leading_candidate_name,
            "instability_effects": self.instability_effects,
            "metadata": self.metadata
        }


@dataclass
class ExternalInterferenceEvent(BaseEvent):
    """Event fired when external faction interferes in succession crisis"""
    
    event_type: str = "external_interference"
    crisis_id: UUID = None
    target_faction_id: UUID = None
    interfering_faction_id: UUID = None
    interfering_faction_name: str = ""
    interference_type: str = ""
    candidate_supported_id: Optional[UUID] = None
    resources_committed: float = 0.0
    interference_details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "crisis_id": str(self.crisis_id),
            "target_faction_id": str(self.target_faction_id),
            "interfering_faction_id": str(self.interfering_faction_id),
            "interfering_faction_name": self.interfering_faction_name,
            "interference_type": self.interference_type,
            "candidate_supported_id": str(self.candidate_supported_id) if self.candidate_supported_id else None,
            "resources_committed": self.resources_committed,
            "interference_details": self.interference_details,
            "metadata": self.metadata
        }


@dataclass
class SuccessionCrisisResolvedEvent(BaseEvent):
    """Event fired when succession crisis is resolved"""
    
    event_type: str = "succession_crisis_resolved"
    crisis_id: UUID = None
    faction_id: UUID = None
    faction_name: str = ""
    winner_id: Optional[UUID] = None
    winner_name: Optional[str] = None
    resolution_method: str = ""
    duration_days: int = 0
    final_stability: float = 1.0
    faction_split: bool = False
    new_factions: Optional[List[UUID]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "crisis_id": str(self.crisis_id),
            "faction_id": str(self.faction_id),
            "faction_name": self.faction_name,
            "winner_id": str(self.winner_id) if self.winner_id else None,
            "winner_name": self.winner_name,
            "resolution_method": self.resolution_method,
            "duration_days": self.duration_days,
            "final_stability": self.final_stability,
            "faction_split": self.faction_split,
            "new_factions": [str(fid) for fid in (self.new_factions or [])],
            "metadata": self.metadata
        }


@dataclass
class FactionSplitEvent(BaseEvent):
    """Event fired when faction splits due to succession crisis"""
    
    event_type: str = "faction_split"
    original_faction_id: UUID = None
    original_faction_name: str = ""
    crisis_id: UUID = None
    new_faction_ids: List[UUID] = None
    new_faction_names: List[str] = None
    split_reason: str = ""
    member_distribution: Optional[Dict[str, List[UUID]]] = None
    territory_distribution: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "original_faction_id": str(self.original_faction_id),
            "original_faction_name": self.original_faction_name,
            "crisis_id": str(self.crisis_id),
            "new_faction_ids": [str(fid) for fid in (self.new_faction_ids or [])],
            "new_faction_names": self.new_faction_names or [],
            "split_reason": self.split_reason,
            "member_distribution": self.member_distribution,
            "territory_distribution": self.territory_distribution,
            "metadata": self.metadata
        }


@dataclass
class CandidateActionEvent(BaseEvent):
    """Event fired when succession candidate takes specific action"""
    
    event_type: str = "candidate_action"
    crisis_id: UUID = None
    candidate_id: UUID = None
    candidate_name: str = ""
    action_type: str = ""
    action_details: Dict[str, Any] = None
    resources_spent: float = 0.0
    effectiveness: Optional[float] = None
    support_change: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "crisis_id": str(self.crisis_id),
            "candidate_id": str(self.candidate_id),
            "candidate_name": self.candidate_name,
            "action_type": self.action_type,
            "action_details": self.action_details,
            "resources_spent": self.resources_spent,
            "effectiveness": self.effectiveness,
            "support_change": self.support_change,
            "metadata": self.metadata
        }


@dataclass
class LeadershipTransferEvent(BaseEvent):
    """Event fired when leadership is officially transferred"""
    
    event_type: str = "leadership_transfer"
    faction_id: UUID = None
    faction_name: str = ""
    old_leader_id: Optional[UUID] = None
    old_leader_name: Optional[str] = None
    new_leader_id: UUID = None
    new_leader_name: str = ""
    transfer_reason: str = ""
    crisis_id: Optional[UUID] = None
    transfer_method: str = ""  # succession, coup, appointment, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "faction_id": str(self.faction_id),
            "faction_name": self.faction_name,
            "old_leader_id": str(self.old_leader_id) if self.old_leader_id else None,
            "old_leader_name": self.old_leader_name,
            "new_leader_id": str(self.new_leader_id),
            "new_leader_name": self.new_leader_name,
            "transfer_reason": self.transfer_reason,
            "crisis_id": str(self.crisis_id) if self.crisis_id else None,
            "transfer_method": self.transfer_method,
            "metadata": self.metadata
        }


# Event Handler Classes
class SuccessionEventHandler:
    """Handler for succession-related events"""
    
    def __init__(self):
        self.event_handlers = {
            "succession_crisis_triggered": self._handle_crisis_triggered,
            "succession_candidate_announced": self._handle_candidate_announced,
            "succession_crisis_advanced": self._handle_crisis_advanced,
            "external_interference": self._handle_external_interference,
            "succession_crisis_resolved": self._handle_crisis_resolved,
            "faction_split": self._handle_faction_split,
            "candidate_action": self._handle_candidate_action,
            "leadership_transfer": self._handle_leadership_transfer
        }
        logger.info("SuccessionEventHandler initialized")
    
    def handle_event(self, event: BaseEvent) -> None:
        """Handle succession event"""
        handler = self.event_handlers.get(event.event_type)
        if handler:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error handling succession event {event.event_type}: {e}")
        else:
            logger.warning(f"No handler found for succession event type: {event.event_type}")
    
    def _handle_crisis_triggered(self, event: SuccessionCrisisTriggeredEvent) -> None:
        """Handle succession crisis triggered event"""
        logger.info(f"Succession crisis triggered for faction {event.faction_name} due to {event.trigger}")
        
        # Could trigger additional events or notifications
        # For example, alerting allied factions or creating opportunities for interference
        
    def _handle_candidate_announced(self, event: SuccessionCandidateAnnouncedEvent) -> None:
        """Handle new candidate announcement"""
        logger.info(f"New succession candidate announced: {event.candidate_name}")
        
        # Could trigger AI responses from other candidates or factions
        
    def _handle_crisis_advanced(self, event: SuccessionCrisisAdvancedEvent) -> None:
        """Handle crisis advancement"""
        if event.faction_stability < 0.5:
            logger.warning(f"Faction stability critically low: {event.faction_stability}")
        
        # Could trigger stability-based events or external faction responses
        
    def _handle_external_interference(self, event: ExternalInterferenceEvent) -> None:
        """Handle external interference"""
        logger.info(f"External interference in succession: {event.interfering_faction_name} -> {event.interference_type}")
        
        # Could escalate diplomatic tensions or trigger counter-interference
        
    def _handle_crisis_resolved(self, event: SuccessionCrisisResolvedEvent) -> None:
        """Handle crisis resolution"""
        if event.faction_split:
            logger.warning(f"Faction {event.faction_name} split during succession crisis")
        else:
            logger.info(f"Succession crisis resolved - new leader: {event.winner_name}")
        
        # Could trigger diplomatic updates or stability recovery events
        
    def _handle_faction_split(self, event: FactionSplitEvent) -> None:
        """Handle faction split"""
        logger.warning(f"Faction split: {event.original_faction_name} -> {len(event.new_faction_ids or [])} new factions")
        
        # Could trigger territorial redistribution or diplomatic realignment
        
    def _handle_candidate_action(self, event: CandidateActionEvent) -> None:
        """Handle candidate action"""
        logger.info(f"Candidate action: {event.candidate_name} -> {event.action_type}")
        
        # Could trigger counter-actions or campaign responses
        
    def _handle_leadership_transfer(self, event: LeadershipTransferEvent) -> None:
        """Handle leadership transfer"""
        logger.info(f"Leadership transfer: {event.old_leader_name} -> {event.new_leader_name} ({event.transfer_method})")
        
        # Could trigger diplomatic updates, membership changes, or policy shifts


# Event Factory Functions
def create_succession_crisis_triggered_event(
    faction_id: UUID,
    faction_name: str,
    trigger: SuccessionTrigger,
    succession_type: SuccessionType,
    crisis_id: UUID,
    previous_leader_id: Optional[UUID] = None,
    estimated_duration: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> SuccessionCrisisTriggeredEvent:
    """Factory function for succession crisis triggered event"""
    return SuccessionCrisisTriggeredEvent(
        faction_id=faction_id,
        faction_name=faction_name,
        trigger=trigger,
        succession_type=succession_type,
        crisis_id=crisis_id,
        previous_leader_id=previous_leader_id,
        estimated_duration=estimated_duration,
        metadata=metadata or {}
    )


def create_candidate_announced_event(
    crisis_id: UUID,
    faction_id: UUID,
    candidate_id: UUID,
    candidate_name: str,
    succession_type: SuccessionType,
    campaign_strategy: Optional[str] = None,
    qualifications: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> SuccessionCandidateAnnouncedEvent:
    """Factory function for candidate announced event"""
    return SuccessionCandidateAnnouncedEvent(
        crisis_id=crisis_id,
        faction_id=faction_id,
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        succession_type=succession_type,
        campaign_strategy=campaign_strategy,
        qualifications=qualifications,
        metadata=metadata or {}
    )


def create_crisis_resolved_event(
    crisis_id: UUID,
    faction_id: UUID,
    faction_name: str,
    winner_id: Optional[UUID],
    winner_name: Optional[str],
    resolution_method: str,
    duration_days: int,
    final_stability: float,
    faction_split: bool = False,
    new_factions: Optional[List[UUID]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> SuccessionCrisisResolvedEvent:
    """Factory function for crisis resolved event"""
    return SuccessionCrisisResolvedEvent(
        crisis_id=crisis_id,
        faction_id=faction_id,
        faction_name=faction_name,
        winner_id=winner_id,
        winner_name=winner_name,
        resolution_method=resolution_method,
        duration_days=duration_days,
        final_stability=final_stability,
        faction_split=faction_split,
        new_factions=new_factions,
        metadata=metadata or {}
    ) 