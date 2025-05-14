"""
Module for handling flanking mechanics in combat.
This includes position analysis, flanking bonuses, and opportunity attacks.
"""

from typing import List, Tuple, Dict, Any, Optional
from app.core.models.combat import CombatParticipant, Combat
from app.combat.status_effects_utils import check_flanking
from app.combat.combat_utils import calculate_damage
from app.core.database import db

def process_opportunity_attack(
    attacker: CombatParticipant,
    target: CombatParticipant
) -> Dict[str, Any]:
    """
    Process an opportunity attack when a target moves out of an attacker's reach.
    
    Args:
        attacker: The participant making the opportunity attack
        target: The participant being attacked
        
    Returns:
        Dict containing the results of the opportunity attack
    """
    # Calculate base damage with a penalty
    damage = calculate_damage(
        attacker=attacker,
        target=target,
        action_type='opportunity',
        terrain_modifiers={'damage_multiplier': 0.75}  # 75% damage for opportunity attacks
    )
    
    # Apply damage
    target.current_health = max(0, target.current_health - damage)
    
    # Create log entry
    result = {
        'attacker_id': attacker.id,
        'target_id': target.id,
        'damage': damage,
        'target_remaining_health': target.current_health,
        'type': 'opportunity_attack'
    }
    
    # Add to combat log
    combat = Combat.query.get(attacker.combat_id)
    if combat:
        if not combat.log:
            combat.log = []
        combat.log.append(result)
        db.session.commit()
    
    return result

class FlankingHandler:
    def __init__(self, combat_id: int):
        self.combat = Combat.query.get(combat_id)
        if not self.combat:
            raise ValueError(f"Combat with id {combat_id} not found")

    def get_flanking_participants(
        self,
        target_id: int
    ) -> List[CombatParticipant]:
        """
        Get all participants that are flanking a target.
        
        Args:
            target_id: ID of the target participant
            
        Returns:
            List of participants that are flanking the target
        """
        target = CombatParticipant.query.get(target_id)
        if not target:
            return []
            
        flanking_participants = []
        all_participants = CombatParticipant.query.filter_by(
            combat_id=self.combat.id
        ).all()
        
        for p1 in all_participants:
            if p1.id == target_id:
                continue
                
            # Check if this participant is flanking with any other
            for p2 in all_participants:
                if p2.id in (p1.id, target_id):
                    continue
                    
                if check_flanking(p1.position, p2.position, target.position):
                    if p1 not in flanking_participants:
                        flanking_participants.append(p1)
                    if p2 not in flanking_participants:
                        flanking_participants.append(p2)
                        
        return flanking_participants

    def apply_flanking_effects(self, target_id: int) -> None:
        """
        Apply flanking status effects to all participants flanking a target.
        
        Args:
            target_id: ID of the target participant
        """
        flanking_participants = self.get_flanking_participants(target_id)
        
        # Remove old flanking effects from everyone
        all_participants = CombatParticipant.query.filter_by(
            combat_id=self.combat.id
        ).all()
        
        for participant in all_participants:
            if not participant.status_effects:
                participant.status_effects = []
            participant.status_effects = [
                effect for effect in participant.status_effects
                if effect.get('type') != 'flanking'
            ]
        
        # Apply new flanking effects
        for participant in flanking_participants:
            participant.status_effects.append({
                'type': 'flanking',
                'magnitude': 1.5,  # 50% damage bonus
                'duration': 1,  # Lasts until next position change
                'target_id': target_id
            })
            
        db.session.commit()

    def check_opportunity_attack(
        self,
        moving_participant_id: int,
        old_position: Tuple[int, int],
        new_position: Tuple[int, int]
    ) -> List[CombatParticipant]:
        """
        Check if a movement triggers any opportunity attacks.
        
        Args:
            moving_participant_id: ID of the participant moving
            old_position: Starting position (q, r)
            new_position: Ending position (q, r)
            
        Returns:
            List of participants that can make opportunity attacks
        """
        attackers = []
        
        # Get all participants in combat except the moving one
        potential_attackers = CombatParticipant.query.filter(
            CombatParticipant.combat_id == self.combat.id,
            CombatParticipant.id != moving_participant_id
        ).all()
        
        attack_range = 1  # Base melee range
        
        for participant in potential_attackers:
            # Skip if participant is defeated
            if any(effect.get('type') == 'defeated' for effect in (participant.status_effects or [])):
                continue
                
            # Check if participant was in range before the move
            old_distance = self._calculate_distance(participant.position, old_position)
            new_distance = self._calculate_distance(participant.position, new_position)
            
            # Trigger opportunity attack if moving from within range to outside range
            if old_distance <= attack_range and new_distance > attack_range:
                attackers.append(participant)
                
        return attackers

    def _calculate_distance(
        self,
        pos1: Tuple[int, int],
        pos2: Tuple[int, int]
    ) -> int:
        """Calculate the hex grid distance between two positions."""
        q1, r1 = pos1
        q2, r2 = pos2
        return (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) // 2 