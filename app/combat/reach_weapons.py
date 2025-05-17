"""
Module for handling reach weapon mechanics in combat.
This includes range calculations, attack validation, and special effects.
"""

from typing import List, Tuple, Dict, Any, Optional
from app.core.database import db

class ReachWeaponHandler:
    def __init__(self, combat_id: int):
        from app.core.models.combat import Combat
        self.combat = Combat.query.get(combat_id)
        if not self.combat:
            raise ValueError(f"Combat with id {combat_id} not found")

    def check_reach_attack_valid(
        self,
        attacker_id: int,
        target_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a reach weapon attack is valid based on distance and line of sight.
        
        Args:
            attacker_id: ID of the attacking participant
            target_id: ID of the target participant
            
        Returns:
            Tuple of (is_valid, reason_if_invalid)
        """
        from app.core.models.combat import CombatParticipant
        attacker = CombatParticipant.query.get(attacker_id)
        target = CombatParticipant.query.get(target_id)
        
        if not attacker or not target:
            return False, "Attacker or target not found"
            
        # Get attack range
        attack_range = self._get_attack_range(attacker)
        
        # Calculate distance
        distance = self._calculate_distance(attacker.position, target.position)
        
        # Check if target is in range
        if distance > attack_range:
            return False, f"Target is out of range ({distance} hexes, range is {attack_range})"
            
        # Check if target is too close (for certain reach weapons)
        if self._has_minimum_range(attacker) and distance < 2:
            return False, "Target is too close for this reach weapon"
            
        # Check line of sight
        if not self._has_line_of_sight(attacker.position, target.position):
            return False, "No clear line of sight to target"
            
        return True, None

    def apply_reach_weapon_effects(
        self,
        attacker_id: int,
        action_type: str
    ) -> Dict[str, float]:
        """
        Apply special effects for reach weapons based on weapon type and action.
        
        Args:
            attacker_id: ID of the attacking participant
            action_type: Type of attack action being performed
            
        Returns:
            Dict of effect modifiers to apply to the attack
        """
        from app.core.models.combat import CombatParticipant
        attacker = CombatParticipant.query.get(attacker_id)
        if not attacker:
            return {}
            
        effects = {}
        
        # Get weapon type and properties
        weapon_type = self._get_reach_weapon_type(attacker)
        if not weapon_type:
            return effects
            
        # Apply weapon-specific effects
        if weapon_type == "spear":
            effects["damage_multiplier"] = 1.2  # 20% damage bonus
            if action_type == "opportunity":
                effects["damage_multiplier"] = 1.5  # 50% bonus on opportunity attacks
                
        elif weapon_type == "halberd":
            effects["armor_penetration"] = 0.2  # 20% armor penetration
            if action_type == "charge":
                effects["damage_multiplier"] = 1.3  # 30% bonus on charge attacks
                
        elif weapon_type == "pike":
            effects["damage_multiplier"] = 1.1  # 10% damage bonus
            effects["critical_range_bonus"] = 1  # Improved critical hit range
            
        elif weapon_type == "whip":
            effects["status_effect_chance"] = 0.2  # 20% chance to apply status effects
            effects["pull_strength"] = 1  # Can pull target 1 hex closer
            
        return effects

    def get_threatened_hexes(self, participant_id: int) -> List[Tuple[int, int]]:
        """
        Get all hex coordinates threatened by a participant's reach weapon.
        
        Args:
            participant_id: ID of the participant
            
        Returns:
            List of (q, r) coordinates that are threatened
        """
        from app.core.models.combat import CombatParticipant
        participant = CombatParticipant.query.get(participant_id)
        if not participant:
            return []
            
        threatened = []
        attack_range = self._get_attack_range(participant)
        pos = participant.position
        
        # Calculate all hexes within range
        for q in range(-attack_range, attack_range + 1):
            for r in range(-attack_range, attack_range + 1):
                candidate = (pos[0] + q, pos[1] + r)
                distance = self._calculate_distance(pos, candidate)
                
                # Check if hex is in range and has line of sight
                if distance <= attack_range and self._has_line_of_sight(pos, candidate):
                    # For weapons with minimum range, exclude hexes that are too close
                    if not self._has_minimum_range(participant) or distance >= 2:
                        threatened.append(candidate)
                        
        return threatened

    def _get_attack_range(self, participant) -> int:
        """Get the attack range for a participant's reach weapon."""
        base_range = 1  # Default melee range
        
        if not participant.status_effects:
            return base_range
            
        # Check for reach weapon effects
        for effect in participant.status_effects:
            if effect.get('type') == 'reach_weapon':
                weapon_type = effect.get('weapon_type', '')
                if weapon_type in ['spear', 'halberd']:
                    base_range = 2
                elif weapon_type == 'pike':
                    base_range = 3
                elif weapon_type == 'whip':
                    base_range = 2
                break
                
        return base_range

    def _has_minimum_range(self, participant) -> bool:
        """Check if the participant's weapon has a minimum range requirement."""
        if not participant.status_effects:
            return False
            
        for effect in participant.status_effects:
            if effect.get('type') == 'reach_weapon':
                weapon_type = effect.get('weapon_type', '')
                # Pike requires minimum range
                return weapon_type == 'pike'
                
        return False

    def _get_reach_weapon_type(self, participant) -> Optional[str]:
        """Get the type of reach weapon a participant is using."""
        if not participant.status_effects:
            return None
            
        for effect in participant.status_effects:
            if effect.get('type') == 'reach_weapon':
                return effect.get('weapon_type')
                
        return None

    def _has_line_of_sight(
        self,
        start_pos: Tuple[int, int],
        end_pos: Tuple[int, int]
    ) -> bool:
        """
        Check if there is a clear line of sight between two positions.
        
        Args:
            start_pos: Starting position (q, r)
            end_pos: Ending position (q, r)
            
        Returns:
            Boolean indicating if there is line of sight
        """
        if not self.combat.tactical_grid:
            return True
            
        # Get blocking terrain and participants
        blocking_positions = set()
        
        # Add terrain obstacles
        for pos, cell in self.combat.tactical_grid.items():
            if cell.get('blocks_sight', False):
                blocking_positions.add(pos)
                
        # Add other participants
        participants = CombatParticipant.query.filter_by(
            combat_id=self.combat.id
        ).all()
        
        for p in participants:
            if p.position != start_pos and p.position != end_pos:
                blocking_positions.add(p.position)
                
        # Check if line is blocked
        line = self._get_line(start_pos, end_pos)
        return not any(pos in blocking_positions for pos in line)

    def _calculate_distance(
        self,
        pos1: Tuple[int, int],
        pos2: Tuple[int, int]
    ) -> int:
        """Calculate the hex grid distance between two positions."""
        q1, r1 = pos1
        q2, r2 = pos2
        return (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) // 2

    def _get_line(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """
        Get all hex coordinates in a line between two positions.
        Uses a modified Bresenham's line algorithm for hex grids.
        
        Args:
            start: Starting position (q, r)
            end: Ending position (q, r)
            
        Returns:
            List of (q, r) coordinates along the line
        """
        line = []
        q1, r1 = start
        q2, r2 = end
        
        # Calculate hex coordinates
        N = self._calculate_distance(start, end)
        if N == 0:
            return [start]
            
        # Step through line
        for i in range(N + 1):
            t = 0.0 if N == 0 else i / N
            q = round(q1 + (q2 - q1) * t)
            r = round(r1 + (r2 - r1) * t)
            line.append((q, r))
            
        return line 