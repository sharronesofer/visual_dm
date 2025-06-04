"""
Combat Encounter Domain Model

This module defines the CombatEncounter domain model according to
the Development Bible standards. Pure business logic with no infrastructure concerns.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field

from .combatant import Combatant
from .combat_action import CombatAction


@dataclass
class CombatEncounter:
    """
    Domain model representing a complete combat encounter.
    
    Encapsulates all state and business rules for a combat encounter,
    including participants, turn order, round tracking, and combat log.
    """
    
    # Identity
    id: UUID = field(default_factory=uuid4)
    name: str = "Combat Encounter"
    description: Optional[str] = None
    
    # Combat State
    status: str = "pending"  # pending, active, completed, aborted
    round_number: int = 1
    current_turn: int = 0
    
    # Participants
    participants: List[Combatant] = field(default_factory=list)
    initiative_order: List[Combatant] = field(default_factory=list)
    
    # History and Logging
    combat_log: List[Dict[str, Any]] = field(default_factory=list)
    actions_taken: List[CombatAction] = field(default_factory=list)
    
    # Metadata
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def add_participant(self, combatant: Combatant) -> None:
        """Add a participant to the combat encounter."""
        if combatant not in self.participants:
            self.participants.append(combatant)
            combatant.combat_encounter_id = self.id
    
    def remove_participant(self, combatant: Combatant) -> None:
        """Remove a participant from the combat encounter."""
        if combatant in self.participants:
            self.participants.remove(combatant)
            combatant.combat_encounter_id = None
            
        if combatant in self.initiative_order:
            self.initiative_order.remove(combatant)
    
    def set_initiative_order(self, ordered_participants: List[Combatant]) -> None:
        """Set the initiative order for combat."""
        # Validate all participants are in the encounter
        for participant in ordered_participants:
            if participant not in self.participants:
                raise ValueError(f"Participant {participant.name} not in encounter")
        
        self.initiative_order = ordered_participants.copy()
    
    def get_current_participant(self) -> Optional[Combatant]:
        """Get the participant whose turn it currently is."""
        if (self.initiative_order and 
            0 <= self.current_turn < len(self.initiative_order)):
            return self.initiative_order[self.current_turn]
        return None
    
    def advance_turn(self) -> bool:
        """
        Advance to the next participant's turn.
        
        Returns:
            True if still in the same round, False if a new round started
        """
        if not self.initiative_order:
            return False
            
        self.current_turn += 1
        
        # Check if we've completed the round
        if self.current_turn >= len(self.initiative_order):
            self.current_turn = 0
            self.round_number += 1
            return False  # New round started
        
        return True  # Same round continues
    
    def start_combat(self) -> None:
        """Start the combat encounter."""
        if self.status != "pending":
            raise ValueError(f"Cannot start combat in status: {self.status}")
        
        if not self.participants:
            raise ValueError("Cannot start combat with no participants")
            
        if not self.initiative_order:
            raise ValueError("Cannot start combat without initiative order")
        
        self.status = "active"
        self.started_at = datetime.utcnow()
        self.log_event("Combat started", {"participants": len(self.participants)})
    
    def end_combat(self, reason: str = "completed") -> None:
        """End the combat encounter."""
        if self.status not in ["active", "pending"]:
            raise ValueError(f"Cannot end combat in status: {self.status}")
        
        self.status = "completed" if reason == "completed" else "aborted"
        self.ended_at = datetime.utcnow()
        self.log_event(f"Combat ended: {reason}")
    
    def log_event(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Add an event to the combat log."""
        log_entry = {
            "round": self.round_number,
            "turn": self.current_turn,
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "data": data or {}
        }
        self.combat_log.append(log_entry)
    
    def record_action(self, action: CombatAction) -> None:
        """Record a combat action that was taken."""
        action.encounter_id = self.id
        action.round_number = self.round_number
        action.turn_number = self.current_turn
        self.actions_taken.append(action)
        
        # Also log the action
        self.log_event(
            f"{action.actor_name} used {action.action_name}",
            {
                "action_id": str(action.id),
                "target": action.target_name,
                "success": action.success
            }
        )
    
    def get_active_participants(self) -> List[Combatant]:
        """Get all participants that are still active in combat."""
        return [p for p in self.participants if p.is_active]
    
    def get_team_participants(self, team: str) -> List[Combatant]:
        """Get all participants from a specific team."""
        return [p for p in self.participants if p.team == team]
    
    def is_combat_over(self) -> bool:
        """Check if combat should end due to victory conditions."""
        active_teams = set()
        for participant in self.get_active_participants():
            if participant.current_hp > 0:
                active_teams.add(participant.team)
        
        # Combat is over if only one team (or fewer) remains
        return len(active_teams) <= 1
    
    def get_combat_summary(self) -> Dict[str, Any]:
        """Get a summary of the combat encounter."""
        active_participants = self.get_active_participants()
        
        return {
            "id": str(self.id),
            "name": self.name,
            "status": self.status,
            "round": self.round_number,
            "total_participants": len(self.participants),
            "active_participants": len(active_participants),
            "actions_taken": len(self.actions_taken),
            "duration_seconds": self._get_duration_seconds(),
            "teams": self._get_team_summary()
        }
    
    def _get_duration_seconds(self) -> Optional[float]:
        """Calculate combat duration in seconds."""
        if not self.started_at:
            return None
        
        end_time = self.ended_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()
    
    def _get_team_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary information about each team."""
        teams = {}
        
        for participant in self.participants:
            team = participant.team
            if team not in teams:
                teams[team] = {
                    "total_members": 0,
                    "active_members": 0,
                    "total_hp": 0,
                    "current_hp": 0
                }
            
            teams[team]["total_members"] += 1
            teams[team]["total_hp"] += participant.max_hp
            teams[team]["current_hp"] += participant.current_hp
            
            if participant.is_active and participant.current_hp > 0:
                teams[team]["active_members"] += 1
        
        return teams

    def get_next_participant(self) -> Optional[Combatant]:
        """Get the next participant in initiative order."""
        if not self.initiative_order:
            return None
            
        next_turn = (self.current_turn + 1) % len(self.initiative_order)
        return self.initiative_order[next_turn]

    def remove_participant(self, combatant_id: UUID) -> bool:
        """Remove a participant from the encounter."""
        for i, participant in enumerate(self.participants):
            if participant.id == combatant_id:
                self.participants.pop(i)
                # Also remove from initiative order
                self.initiative_order = [p for p in self.initiative_order if p.id != combatant_id]
                return True
        return False


__all__ = ["CombatEncounter"] 