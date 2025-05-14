from typing import List, Dict, Optional, Any, Tuple
import random
from datetime import datetime
from app.core.models.combat import CombatState, CombatParticipant
from app.core.database import db

class InitiativeTracker:
    """
    Tracks initiative order, current turn, and round for combat participants.
    Handles rolling, sorting, and advancing initiative, as well as ready/delay actions.
    Provides integration with the combat state database and event logging.
    """
    def __init__(self, participants: List[Dict[str, Any]], combat_state_id: Optional[int] = None):
        """
        Initialize the tracker with a list of participants.
        Each participant should have at least 'id', 'dexterity', and optionally 'initiative_bonus'.
        
        Args:
            participants: List of participant dictionaries
            combat_state_id: Optional ID of associated CombatState for database integration
        """
        self.participants = participants.copy()
        self.initiative_order: List[str] = []  # List of participant IDs in order
        self.current_turn: int = 0
        self.round_number: int = 1
        self.combat_state_id = combat_state_id
        self.initiative_log: List[Dict[str, Any]] = []  # Track initiative rolls and modifiers
        self._roll_and_sort_initiative()

    def _roll_and_sort_initiative(self):
        """
        Roll initiative for all participants and sort them in descending order.
        Records initiative rolls and modifiers for logging.
        """
        initiatives = []
        self.initiative_log.clear()
        
        for p in self.participants:
            dex = p.get('dexterity', 10)
            bonus = p.get('initiative_bonus', 0)
            base_roll = random.randint(1, 20)
            initiative = self.calculate_initiative(dex, bonus, base_roll)
            
            p['initiative'] = initiative
            initiatives.append((p['id'], initiative))
            
            # Log initiative details
            self.initiative_log.append({
                'participant_id': p['id'],
                'name': p.get('name', f"Participant {p['id']}"),
                'base_roll': base_roll,
                'dexterity_mod': (dex - 10) // 2,
                'bonus': bonus,
                'total': initiative,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Sort by initiative (highest first), break ties with dexterity
        initiatives.sort(key=lambda x: (
            x[1],  # Initiative total
            next((p['dexterity'] for p in self.participants if p['id'] == x[0]), 0)  # Dexterity tiebreaker
        ), reverse=True)
        
        self.initiative_order = [pid for pid, _ in initiatives]
        
        # Update database if combat state is linked
        if self.combat_state_id:
            self._update_combat_state()

    @staticmethod
    def calculate_initiative(dexterity: int, bonus: int = 0, base_roll: Optional[int] = None) -> int:
        """
        Calculate initiative for a character.
        
        Args:
            dexterity: Character's dexterity score
            bonus: Additional initiative bonus
            base_roll: Optional pre-rolled d20 value (for testing/fixed scenarios)
            
        Returns:
            Total initiative value
        """
        dex_mod = (dexterity - 10) // 2
        if base_roll is None:
            base_roll = random.randint(1, 20)
        return base_roll + dex_mod + bonus

    def get_current_participant(self) -> Optional[Dict[str, Any]]:
        """Return the participant whose turn it is."""
        if not self.initiative_order:
            return None
        current_id = self.initiative_order[self.current_turn]
        return next((p for p in self.participants if p['id'] == current_id), None)

    def advance_turn(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Advance to the next participant. Increment round if at the end of the order.
        
        Returns:
            Tuple of (round_changed: bool, next_participant: Optional[Dict])
        """
        if not self.initiative_order:
            return False, None
            
        self.current_turn += 1
        round_changed = False
        
        if self.current_turn >= len(self.initiative_order):
            self.current_turn = 0
            self.round_number += 1
            round_changed = True
            
        # Update database if combat state is linked
        if self.combat_state_id:
            self._update_combat_state()
            
        next_participant = self.get_current_participant()
        return round_changed, next_participant

    def ready_action(self, participant_id: str) -> bool:
        """
        Move the participant to act later in the round (ready action).
        
        Args:
            participant_id: ID of the participant readying their action
            
        Returns:
            True if the action was readied successfully
        """
        if participant_id not in self.initiative_order:
            return False
            
        # Can't ready if not your turn
        current = self.get_current_participant()
        if not current or current['id'] != participant_id:
            return False
            
        self.initiative_order.remove(participant_id)
        self.initiative_order.append(participant_id)
        
        # Update database if combat state is linked
        if self.combat_state_id:
            self._update_combat_state()
            
        return True

    def delay_action(self, participant_id: str) -> bool:
        """
        Move the participant to act later in the round (delay action).
        Functionally identical to ready_action for now, but kept separate
        for future rule differentiation.
        """
        return self.ready_action(participant_id)

    def reset(self):
        """
        Reset turn and round counters, and reroll initiative.
        """
        self.current_turn = 0
        self.round_number = 1
        self.initiative_log.clear()
        self._roll_and_sort_initiative()

    def get_initiative_order(self) -> List[str]:
        """
        Return the current initiative order (list of participant IDs).
        """
        return self.initiative_order.copy()

    def get_round_number(self) -> int:
        """Get the current round number."""
        return self.round_number

    def get_turn_index(self) -> int:
        """Get the current turn index."""
        return self.current_turn

    def get_initiative_log(self) -> List[Dict[str, Any]]:
        """
        Get the log of initiative rolls and modifiers.
        Useful for combat logging and UI display.
        """
        return self.initiative_log.copy()

    def insert_participant(self, participant: Dict[str, Any], position: Optional[int] = None) -> bool:
        """
        Insert a new participant into combat at a specific initiative position.
        
        Args:
            participant: Participant data dictionary
            position: Optional position in initiative order (None for automatic based on roll)
            
        Returns:
            True if participant was added successfully
        """
        if not all(key in participant for key in ['id', 'dexterity']):
            return False
            
        # Add to participants list
        self.participants.append(participant)
        
        if position is None:
            # Roll initiative normally
            dex = participant.get('dexterity', 10)
            bonus = participant.get('initiative_bonus', 0)
            initiative = self.calculate_initiative(dex, bonus)
            participant['initiative'] = initiative
            
            # Find correct position
            for i, pid in enumerate(self.initiative_order):
                other = next(p for p in self.participants if p['id'] == pid)
                if initiative > other.get('initiative', 0):
                    position = i
                    break
            else:
                position = len(self.initiative_order)
        
        # Insert at position
        self.initiative_order.insert(position, participant['id'])
        
        # Update database if combat state is linked
        if self.combat_state_id:
            self._update_combat_state()
            
        return True

    def remove_participant(self, participant_id: str) -> bool:
        """
        Remove a participant from combat.
        
        Args:
            participant_id: ID of participant to remove
            
        Returns:
            True if participant was removed successfully
        """
        if participant_id not in self.initiative_order:
            return False
            
        # Remove from initiative order
        self.initiative_order.remove(participant_id)
        
        # Remove from participants list
        self.participants = [p for p in self.participants if p['id'] != participant_id]
        
        # Adjust current turn if needed
        if self.current_turn >= len(self.initiative_order):
            self.current_turn = 0
            self.round_number += 1
            
        # Update database if combat state is linked
        if self.combat_state_id:
            self._update_combat_state()
            
        return True

    def _update_combat_state(self):
        """Update the associated CombatState in the database."""
        try:
            combat_state = db.session.query(CombatState).get(self.combat_state_id)
            if combat_state:
                combat_state.round_number = self.round_number
                combat_state.current_turn = self.current_turn
                combat_state.initiative_order = self.initiative_order
                combat_state.updated_at = datetime.utcnow()
                db.session.commit()
        except Exception as e:
            # Log error but don't crash
            print(f"Error updating combat state: {e}")
            db.session.rollback() 