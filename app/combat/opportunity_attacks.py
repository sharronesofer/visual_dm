"""
Module for handling opportunity attack mechanics in combat.
This includes movement-based triggers, reach weapons, and special abilities.
"""

from typing import List, Tuple, Dict, Any, Optional
from app.core.database import db

class OpportunityAttackHandler:
    def __init__(self, combat_id: int):
        from app.core.models.combat import Combat
        self.combat = Combat.query.get(combat_id)
        if not self.combat:
            raise ValueError(f"Combat with id {combat_id} not found")

    def check_opportunity_attack_triggers(
        self,
        moving_participant_id: int,
        movement_path: List[Tuple[int, int]]
    ) -> List[Dict[str, Any]]:
        """
        Check if a movement path triggers any opportunity attacks.
        
        Args:
            moving_participant_id: ID of the participant moving
            movement_path: List of (q, r) positions in movement path
            
        Returns:
            List of dicts containing attacker info and trigger positions
        """
        from app.core.models.combat import CombatParticipant
        if len(movement_path) < 2:
            return []
            
        triggers = []
        moving_participant = CombatParticipant.query.get(moving_participant_id)
        
        # Get all potential attackers
        potential_attackers = CombatParticipant.query.filter(
            CombatParticipant.combat_id == self.combat.id,
            CombatParticipant.id != moving_participant_id
        ).all()
        
        # Check each segment of movement
        for i in range(len(movement_path) - 1):
            start_pos = movement_path[i]
            end_pos = movement_path[i + 1]
            
            for attacker in potential_attackers:
                # Skip if attacker has already made an opportunity attack this round
                if self._has_made_opportunity_attack(attacker):
                    continue
                    
                # Get attack range (considering reach weapons)
                attack_range = self._get_attack_range(attacker)
                
                # Check if movement triggers an attack
                if self._movement_triggers_attack(
                    attacker.position,
                    start_pos,
                    end_pos,
                    attack_range
                ):
                    triggers.append({
                        'attacker': attacker,
                        'trigger_position': start_pos,
                        'target_position': end_pos
                    })
                    
        return triggers

    def process_opportunity_attacks(
        self,
        moving_participant_id: int,
        triggers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process all triggered opportunity attacks.
        
        Args:
            moving_participant_id: ID of the participant being attacked
            triggers: List of trigger dicts from check_opportunity_attack_triggers
            
        Returns:
            List of attack results
        """
        from app.core.models.combat import CombatParticipant
        results = []
        target = CombatParticipant.query.get(moving_participant_id)
        
        for trigger in triggers:
            attacker = trigger['attacker']
            
            # Process the attack
            result = self._execute_opportunity_attack(
                attacker=attacker,
                target=target,
                trigger_position=trigger['trigger_position']
            )
            
            # Record that attacker has used their opportunity attack
            self._mark_opportunity_attack_used(attacker)
            
            results.append(result)
            
            # Check if target was defeated
            if target.current_health <= 0:
                break
                
        return results

    def reset_opportunity_attacks(self) -> None:
        """Reset opportunity attack usage for all participants at start of round."""
        from app.core.models.combat import CombatParticipant
        participants = CombatParticipant.query.filter_by(
            combat_id=self.combat.id
        ).all()
        
        for participant in participants:
            if not participant.status_effects:
                participant.status_effects = []
                
            participant.status_effects = [
                effect for effect in participant.status_effects
                if effect.get('type') != 'used_opportunity_attack'
            ]
            
        db.session.commit()

    def _has_made_opportunity_attack(self, participant) -> bool:
        """Check if a participant has already made an opportunity attack this round."""
        if not participant.status_effects:
            return False
            
        return any(
            effect.get('type') == 'used_opportunity_attack'
            for effect in participant.status_effects
        )

    def _mark_opportunity_attack_used(self, participant) -> None:
        """Mark that a participant has used their opportunity attack this round."""
        if not participant.status_effects:
            participant.status_effects = []
            
        participant.status_effects.append({
            'type': 'used_opportunity_attack',
            'duration': 1  # Resets at start of next round
        })
        
        db.session.commit()

    def _get_attack_range(self, participant) -> int:
        """Get the attack range for a participant, considering equipment and effects."""
        base_range = 1  # Default melee range
        
        # Check for reach weapons
        if participant.status_effects:
            for effect in participant.status_effects:
                if effect.get('type') == 'reach_weapon':
                    base_range = 2
                    break
                    
        return base_range

    def _movement_triggers_attack(
        self,
        attacker_pos: Tuple[int, int],
        start_pos: Tuple[int, int],
        end_pos: Tuple[int, int],
        attack_range: int
    ) -> bool:
        """
        Check if a movement segment triggers an opportunity attack.
        
        Args:
            attacker_pos: Position of potential attacker
            start_pos: Starting position of movement
            end_pos: Ending position of movement
            attack_range: Attack range of the attacker
            
        Returns:
            Boolean indicating if movement triggers an attack
        """
        # Calculate distances
        start_distance = self._calculate_distance(attacker_pos, start_pos)
        end_distance = self._calculate_distance(attacker_pos, end_pos)
        
        # Trigger if moving from within range to outside range
        return start_distance <= attack_range and end_distance > attack_range

    def _execute_opportunity_attack(
        self,
        attacker,
        target,
        trigger_position: Tuple[int, int]
    ) -> Dict[str, Any]:
        """
        Execute an opportunity attack.
        
        Args:
            attacker: The participant making the attack
            target: The participant being attacked
            trigger_position: Position where attack was triggered
            
        Returns:
            Dict containing attack results
        """
        # Calculate damage with opportunity attack penalty
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
            'type': 'opportunity_attack',
            'attacker_id': attacker.id,
            'target_id': target.id,
            'damage': damage,
            'trigger_position': trigger_position,
            'target_remaining_health': target.current_health
        }
        
        # Add to combat log
        if not self.combat.log:
            self.combat.log = []
        self.combat.log.append(result)
        
        db.session.commit()
        
        return result

    def _calculate_distance(
        self,
        pos1: Tuple[int, int],
        pos2: Tuple[int, int]
    ) -> int:
        """Calculate the hex grid distance between two positions."""
        q1, r1 = pos1
        q2, r2 = pos2
        return (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) // 2 