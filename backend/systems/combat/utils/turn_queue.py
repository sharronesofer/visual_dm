"""
TurnQueue module for the Visual DM combat system.

This module implements a flexible, efficient turn management system for combatants
in the Visual DM combat system. It supports priority-based sorting, dynamic 
join/leave operations, and turn advancement with hooks for turn start/end events.

Following the design principles from the Development Bible, this implementation:
1. Maintains a sorted list of combatants
2. Supports dynamic join/leave operations 
3. Handles reordering of combatants mid-combat
4. Provides hooks for turn start/end events

This is pure business logic - no I/O or database operations.
"""

import logging
from typing import List, Dict, Optional, Callable, Any, Set, Tuple

# Set up logging
logger = logging.getLogger(__name__)

class TurnQueue:
    """
    Maintains a sorted queue of combatants for turn-based combat.
    
    Supports dynamic join/leave operations, reordering, and turn advancement
    with hooks for turn start/end events.
    """
    
    def __init__(self):
        """Initialize an empty turn queue."""
        self._queue: List[Any] = []  # The combatant queue
        self._current_index: int = -1  # Index of current combatant (-1 means not started)
        self._initiative_order: Dict[Any, int] = {}  # Combatant to initiative value mapping
        self._delayed_combatants: Set[Any] = set()  # Combatants who delayed their turn
        
        # Event callbacks
        self._on_turn_start: List[Callable[[Any], None]] = []
        self._on_turn_end: List[Callable[[Any], None]] = []
        
    @property
    def current_combatant(self) -> Optional[Any]:
        """Get the current active combatant."""
        if not self._queue or self._current_index < 0 or self._current_index >= len(self._queue):
            return None
        return self._queue[self._current_index]
    
    @property
    def queue(self) -> List[Any]:
        """Get a copy of the current queue."""
        return self._queue.copy()
    
    @property
    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self._queue) == 0
    
    def initialize_queue(self, combatants: List[Any]) -> None:
        """
        Initialize the queue with a list of combatants.
        
        Args:
            combatants: List of combatants to add to the queue
        """
        if not combatants:
            logger.warning("Attempted to initialize TurnQueue with no combatants")
            return
            
        self._queue = []
        self._initiative_order = {}
        self._current_index = -1
        self._delayed_combatants.clear()
        
        # We'll use simple initiative logic initially, can be enhanced later
        for combatant in combatants:
            # Use DEX attribute for initiative if available, otherwise use a default value
            initiative = getattr(combatant, 'attributes', {}).get('DEX', 10)
            if hasattr(combatant, 'calculate_initiative'):
                initiative = combatant.calculate_initiative()
            
            self._initiative_order[combatant] = initiative
            self._queue.append(combatant)
        
        # Sort the queue by initiative (highest first)
        self._sort_queue()
        
        logger.info(f"TurnQueue initialized with {len(self._queue)} combatants")
    
    def _sort_queue(self) -> None:
        """Sort the queue by initiative values (highest first)."""
        self._queue.sort(key=lambda c: self._initiative_order.get(c, 0), reverse=True)
    
    def add_combatant(self, combatant: Any, initiative: Optional[int] = None) -> None:
        """
        Add a new combatant to the queue.
        
        Args:
            combatant: The combatant to add
            initiative: Optional initiative value (uses combatant's DEX if not provided)
        """
        if combatant in self._queue:
            logger.warning(f"Combatant {combatant} is already in the queue")
            return
        
        # Determine initiative if not provided
        if initiative is None:
            initiative = getattr(combatant, 'attributes', {}).get('DEX', 10)
            if hasattr(combatant, 'calculate_initiative'):
                initiative = combatant.calculate_initiative()
        
        # Add to queue and initiative mapping
        self._initiative_order[combatant] = initiative
        self._queue.append(combatant)
        self._sort_queue()
        
        logger.info(f"Added combatant {combatant} to the queue with initiative {initiative}")
        
        # If the new combatant should go before the current one, update the current index
        if self._current_index >= 0:
            current_initiative = self._initiative_order.get(self.current_combatant, 0)
            if initiative > current_initiative:
                self._current_index += 1
    
    def remove_combatant(self, combatant: Any) -> bool:
        """
        Remove a combatant from the queue.
        
        Args:
            combatant: The combatant to remove
            
        Returns:
            True if the combatant was removed, False otherwise
        """
        if combatant not in self._queue:
            logger.warning(f"Attempted to remove combatant {combatant} not in the queue")
            return False
        
        # Get index of the combatant
        index = self._queue.index(combatant)
        
        # Remove from queue, initiative mapping, and delayed set
        self._queue.remove(combatant)
        if combatant in self._initiative_order:
            del self._initiative_order[combatant]
        if combatant in self._delayed_combatants:
            self._delayed_combatants.remove(combatant)
        
        # Adjust current index if needed
        if index <= self._current_index and self._current_index > 0:
            self._current_index -= 1
        
        logger.info(f"Removed combatant {combatant} from the queue")
        return True
    
    def advance_queue(self) -> Tuple[Any, Any]:
        """
        Advance to the next combatant in the queue.
        
        Returns:
            Tuple of (previous combatant, next combatant)
        """
        previous = self.current_combatant
        
        # If the queue is empty, return None for both
        if not self._queue:
            return None, None
        
        # End the current turn if one is active
        if previous and self._on_turn_end:
            for callback in self._on_turn_end:
                callback(previous)
        
        # Move to the next combatant
        self._current_index = (self._current_index + 1) % len(self._queue)
        next_combatant = self.current_combatant
        
        # Start the next turn
        if next_combatant and self._on_turn_start:
            for callback in self._on_turn_start:
                callback(next_combatant)
        
        return previous, next_combatant
    
    def delay_turn(self, combatant: Any) -> bool:
        """
        Delay a combatant's turn until the end of the round.
        
        Args:
            combatant: The combatant delaying their turn
            
        Returns:
            True if the turn was delayed, False otherwise
        """
        if combatant != self.current_combatant:
            logger.warning(f"Only the current combatant can delay their turn")
            return False
        
        # Add to delayed set and move to the next combatant
        self._delayed_combatants.add(combatant)
        self.advance_queue()
        return True
    
    def recompute_initiative(self, combatant: Any, new_initiative: int) -> None:
        """
        Update a combatant's initiative and reorder the queue.
        
        Args:
            combatant: The combatant to update
            new_initiative: The new initiative value
        """
        if combatant not in self._queue:
            logger.warning(f"Combatant {combatant} not in the queue")
            return
        
        self._initiative_order[combatant] = new_initiative
        
        # Remember the current combatant before resorting
        current = self.current_combatant
        
        # Resort the queue
        self._sort_queue()
        
        # Update the current index to point to the same combatant
        if current:
            self._current_index = self._queue.index(current)
    
    def clear(self) -> None:
        """Clear the queue and reset state."""
        self._queue.clear()
        self._initiative_order.clear()
        self._delayed_combatants.clear()
        self._current_index = -1
    
    def register_turn_start_callback(self, callback: Callable[[Any], None]) -> None:
        """
        Register a callback to be called when a turn starts.
        
        Args:
            callback: Function to call with the combatant as the argument
        """
        if callback not in self._on_turn_start:
            self._on_turn_start.append(callback)
    
    def register_turn_end_callback(self, callback: Callable[[Any], None]) -> None:
        """
        Register a callback to be called when a turn ends.
        
        Args:
            callback: Function to call with the combatant as the argument
        """
        if callback not in self._on_turn_end:
            self._on_turn_end.append(callback)
    
    def unregister_turn_start_callback(self, callback: Callable[[Any], None]) -> None:
        """
        Unregister a turn start callback.
        
        Args:
            callback: The callback to remove
        """
        if callback in self._on_turn_start:
            self._on_turn_start.remove(callback)
    
    def unregister_turn_end_callback(self, callback: Callable[[Any], None]) -> None:
        """
        Unregister a turn end callback.
        
        Args:
            callback: The callback to remove
        """
        if callback in self._on_turn_end:
            self._on_turn_end.remove(callback) 