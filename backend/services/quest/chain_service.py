"""
Quest Chain Business Service

Pure business logic for managing quest chains, progression, and unlocking mechanics.
Handles the logic for connected quests and story progression.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
from uuid import UUID, uuid4

from .models import (
    QuestData, QuestChainData, QuestChainProgressData, QuestStatus, 
    QuestDifficulty, QuestTheme, QuestRewardData
)
from .exceptions import (
    QuestSystemError, QuestNotFoundError, QuestValidationError,
    QuestDependencyError, QuestAccessError
)


class QuestChainBusinessService:
    """Business logic for quest chain management"""
    
    def __init__(self):
        self.chain_types = ["sequential", "branching", "parallel"]
    
    def create_quest_chain(self, chain_data: QuestChainData) -> QuestChainData:
        """
        Create a new quest chain
        
        Args:
            chain_data: Quest chain data to create
            
        Returns:
            Created quest chain data
            
        Raises:
            QuestValidationError: If chain data is invalid
        """
        # Validate chain structure
        validation_errors = chain_data.validate_chain_structure()
        if validation_errors:
            raise QuestValidationError(
                {"chain_validation": validation_errors},
                "Quest chain validation failed"
            )
        
        # Set creation timestamp
        if not chain_data.created_at:
            chain_data.created_at = datetime.now()
        
        return chain_data
    
    def add_quest_to_chain(self, chain: QuestChainData, quest: QuestData, 
                          position: Optional[int] = None) -> QuestChainData:
        """
        Add a quest to an existing chain
        
        Args:
            chain: Quest chain to modify
            quest: Quest to add to the chain
            position: Position in chain (None = append to end)
            
        Returns:
            Updated quest chain
            
        Raises:
            QuestValidationError: If quest cannot be added to chain
        """
        quest_id = str(quest.id)
        
        # Validate quest is not already in chain
        if quest_id in chain.quest_ids:
            raise QuestValidationError(
                {"quest_id": quest_id},
                f"Quest {quest_id} is already in chain {chain.id}"
            )
        
        # Validate quest level is within chain range
        if quest.level < chain.min_level:
            raise QuestValidationError(
                {"level": quest.level, "min_level": chain.min_level},
                f"Quest level {quest.level} is below chain minimum {chain.min_level}"
            )
        
        if chain.max_level and quest.level > chain.max_level:
            raise QuestValidationError(
                {"level": quest.level, "max_level": chain.max_level},
                f"Quest level {quest.level} is above chain maximum {chain.max_level}"
            )
        
        # Add quest to chain
        if position is None:
            chain.quest_ids.append(quest_id)
            position = len(chain.quest_ids) - 1
        else:
            chain.quest_ids.insert(position, quest_id)
        
        # Update quest with chain information
        quest.chain_id = chain.id
        quest.chain_position = position
        
        # Set up prerequisites and unlocks based on chain type
        self._update_quest_chain_relationships(chain, quest, position)
        
        return chain
    
    def remove_quest_from_chain(self, chain: QuestChainData, quest_id: str) -> QuestChainData:
        """
        Remove a quest from a chain
        
        Args:
            chain: Quest chain to modify
            quest_id: ID of quest to remove
            
        Returns:
            Updated quest chain
            
        Raises:
            QuestNotFoundError: If quest is not in chain
        """
        if quest_id not in chain.quest_ids:
            raise QuestNotFoundError(quest_id, f"Quest {quest_id} not found in chain {chain.id}")
        
        # Remove quest from chain
        position = chain.quest_ids.index(quest_id)
        chain.quest_ids.remove(quest_id)
        
        # Update positions for remaining quests
        for i, remaining_quest_id in enumerate(chain.quest_ids[position:], position):
            # This would need to update the actual quest objects
            # In a real implementation, this would involve database updates
            pass
        
        return chain
    
    def start_quest_chain(self, chain: QuestChainData, player_id: str) -> QuestChainProgressData:
        """
        Start a quest chain for a player
        
        Args:
            chain: Quest chain to start
            player_id: Player starting the chain
            
        Returns:
            Quest chain progress data
        """
        # Create progress tracking
        progress = QuestChainProgressData(
            id=str(uuid4()),
            chain_id=chain.id,
            player_id=player_id,
            status="active",
            started_at=datetime.now()
        )
        
        # Determine first available quest(s)
        available_quests = self._get_initial_available_quests(chain)
        progress.available_quests = available_quests
        
        if available_quests:
            progress.current_quest_id = available_quests[0]
        
        return progress
    
    def complete_quest_in_chain(self, progress: QuestChainProgressData, 
                               completed_quest_id: str, chain: QuestChainData) -> QuestChainProgressData:
        """
        Mark a quest as completed and update chain progression
        
        Args:
            progress: Current chain progress
            completed_quest_id: ID of completed quest
            chain: Quest chain data
            
        Returns:
            Updated chain progress
            
        Raises:
            QuestValidationError: If quest cannot be completed
        """
        if completed_quest_id not in chain.quest_ids:
            raise QuestValidationError(
                {"quest_id": completed_quest_id},
                f"Quest {completed_quest_id} is not part of chain {chain.id}"
            )
        
        if completed_quest_id in progress.completed_quests:
            raise QuestValidationError(
                {"quest_id": completed_quest_id},
                f"Quest {completed_quest_id} is already completed"
            )
        
        # Mark quest as completed
        progress.completed_quests.append(completed_quest_id)
        
        # Remove from available quests
        if completed_quest_id in progress.available_quests:
            progress.available_quests.remove(completed_quest_id)
        
        # Determine newly available quests
        newly_available = self._get_newly_available_quests(
            progress, chain, completed_quest_id
        )
        
        # Add newly available quests
        for quest_id in newly_available:
            if quest_id not in progress.available_quests:
                progress.available_quests.append(quest_id)
        
        # Update current quest
        if progress.available_quests:
            progress.current_quest_id = progress.available_quests[0]
        else:
            progress.current_quest_id = None
        
        # Check if chain is completed
        if len(progress.completed_quests) == len(chain.quest_ids):
            progress.status = "completed"
            progress.completed_at = datetime.now()
        
        return progress
    
    def get_available_quests_in_chain(self, progress: QuestChainProgressData, 
                                    chain: QuestChainData) -> List[str]:
        """
        Get list of quests that are currently available to the player
        
        Args:
            progress: Current chain progress
            chain: Quest chain data
            
        Returns:
            List of available quest IDs
        """
        return progress.available_quests.copy()
    
    def get_chain_completion_percentage(self, progress: QuestChainProgressData, 
                                      chain: QuestChainData) -> float:
        """
        Calculate completion percentage for a quest chain
        
        Args:
            progress: Current chain progress
            chain: Quest chain data
            
        Returns:
            Completion percentage (0.0 to 1.0)
        """
        if not chain.quest_ids:
            return 1.0
        
        return len(progress.completed_quests) / len(chain.quest_ids)
    
    def can_player_start_chain(self, chain: QuestChainData, player_level: int, 
                              completed_quests: Set[str] = None) -> Tuple[bool, List[str]]:
        """
        Check if a player can start a quest chain
        
        Args:
            chain: Quest chain to check
            player_level: Player's current level
            completed_quests: Set of quest IDs player has completed
            
        Returns:
            Tuple of (can_start, list_of_blocking_reasons)
        """
        if completed_quests is None:
            completed_quests = set()
        
        blocking_reasons = []
        
        # Check level requirements
        if player_level < chain.min_level:
            blocking_reasons.append(f"Player level {player_level} below required {chain.min_level}")
        
        if chain.max_level and player_level > chain.max_level:
            blocking_reasons.append(f"Player level {player_level} above maximum {chain.max_level}")
        
        # Check prerequisite quests (if any are defined in metadata)
        prerequisite_quests = chain.metadata.get("prerequisite_quests", [])
        missing_prerequisites = [q for q in prerequisite_quests if q not in completed_quests]
        if missing_prerequisites:
            blocking_reasons.append(f"Missing prerequisite quests: {missing_prerequisites}")
        
        return len(blocking_reasons) == 0, blocking_reasons
    
    def _update_quest_chain_relationships(self, chain: QuestChainData, quest: QuestData, position: int):
        """Update quest prerequisites and unlocks based on chain type"""
        if chain.chain_type == "sequential":
            # Sequential: each quest depends on the previous one
            if position > 0:
                previous_quest_id = chain.quest_ids[position - 1]
                quest.chain_prerequisites = [previous_quest_id]
            
            if position < len(chain.quest_ids) - 1:
                next_quest_id = chain.quest_ids[position + 1]
                quest.chain_unlocks = [next_quest_id]
            
            # Mark final quest
            quest.is_chain_final = (position == len(chain.quest_ids) - 1)
        
        elif chain.chain_type == "parallel":
            # Parallel: all quests can be done simultaneously
            quest.chain_prerequisites = []
            quest.chain_unlocks = []
            quest.is_chain_final = True  # All parallel quests are "final"
        
        elif chain.chain_type == "branching":
            # Branching: custom logic based on metadata
            # This would be defined in chain metadata
            branching_rules = chain.metadata.get("branching_rules", {})
            quest_rules = branching_rules.get(str(quest.id), {})
            
            quest.chain_prerequisites = quest_rules.get("prerequisites", [])
            quest.chain_unlocks = quest_rules.get("unlocks", [])
            quest.is_chain_final = quest_rules.get("is_final", False)
    
    def _get_initial_available_quests(self, chain: QuestChainData) -> List[str]:
        """Get the initial quests that are available when starting a chain"""
        if not chain.quest_ids:
            return []
        
        if chain.chain_type == "sequential":
            # Only first quest is available
            return [chain.quest_ids[0]]
        
        elif chain.chain_type == "parallel":
            # All quests are available
            return chain.quest_ids.copy()
        
        elif chain.chain_type == "branching":
            # Find quests with no prerequisites
            branching_rules = chain.metadata.get("branching_rules", {})
            available = []
            
            for quest_id in chain.quest_ids:
                quest_rules = branching_rules.get(quest_id, {})
                prerequisites = quest_rules.get("prerequisites", [])
                
                if not prerequisites:
                    available.append(quest_id)
            
            return available
        
        return []
    
    def _get_newly_available_quests(self, progress: QuestChainProgressData, 
                                  chain: QuestChainData, completed_quest_id: str) -> List[str]:
        """Get quests that become available after completing a specific quest"""
        newly_available = []
        
        if chain.chain_type == "sequential":
            # Next quest in sequence becomes available
            try:
                current_index = chain.quest_ids.index(completed_quest_id)
                if current_index + 1 < len(chain.quest_ids):
                    next_quest_id = chain.quest_ids[current_index + 1]
                    if next_quest_id not in progress.completed_quests:
                        newly_available.append(next_quest_id)
            except ValueError:
                pass  # Quest not found in chain
        
        elif chain.chain_type == "parallel":
            # No new quests become available (all were available from start)
            pass
        
        elif chain.chain_type == "branching":
            # Check which quests this completion unlocks
            branching_rules = chain.metadata.get("branching_rules", {})
            
            for quest_id in chain.quest_ids:
                if quest_id in progress.completed_quests:
                    continue
                
                quest_rules = branching_rules.get(quest_id, {})
                prerequisites = quest_rules.get("prerequisites", [])
                
                # Check if all prerequisites are now met
                if prerequisites and completed_quest_id in prerequisites:
                    if all(prereq in progress.completed_quests for prereq in prerequisites):
                        newly_available.append(quest_id)
        
        return newly_available
    
    def validate_chain_structure(self, chain: QuestChainData, quest_data: Dict[str, QuestData]) -> List[str]:
        """
        Validate the overall structure of a quest chain
        
        Args:
            chain: Quest chain to validate
            quest_data: Dictionary of quest ID to quest data
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Basic validation
        errors.extend(chain.validate_chain_structure())
        
        # Check that all referenced quests exist
        for quest_id in chain.quest_ids:
            if quest_id not in quest_data:
                errors.append(f"Quest {quest_id} referenced in chain but not found")
        
        # Validate chain-specific logic
        if chain.chain_type == "sequential":
            errors.extend(self._validate_sequential_chain(chain, quest_data))
        elif chain.chain_type == "branching":
            errors.extend(self._validate_branching_chain(chain, quest_data))
        
        return errors
    
    def _validate_sequential_chain(self, chain: QuestChainData, quest_data: Dict[str, QuestData]) -> List[str]:
        """Validate a sequential quest chain"""
        errors = []
        
        # Check level progression makes sense
        for i in range(len(chain.quest_ids) - 1):
            current_quest = quest_data.get(chain.quest_ids[i])
            next_quest = quest_data.get(chain.quest_ids[i + 1])
            
            if current_quest and next_quest:
                if next_quest.level < current_quest.level:
                    errors.append(
                        f"Quest {next_quest.id} level {next_quest.level} is lower "
                        f"than previous quest {current_quest.id} level {current_quest.level}"
                    )
        
        return errors
    
    def _validate_branching_chain(self, chain: QuestChainData, quest_data: Dict[str, QuestData]) -> List[str]:
        """Validate a branching quest chain"""
        errors = []
        
        branching_rules = chain.metadata.get("branching_rules", {})
        
        # Check for circular dependencies
        def has_circular_dependency(quest_id: str, visited: Set[str]) -> bool:
            if quest_id in visited:
                return True
            
            visited.add(quest_id)
            quest_rules = branching_rules.get(quest_id, {})
            prerequisites = quest_rules.get("prerequisites", [])
            
            for prereq in prerequisites:
                if has_circular_dependency(prereq, visited.copy()):
                    return True
            
            return False
        
        for quest_id in chain.quest_ids:
            if has_circular_dependency(quest_id, set()):
                errors.append(f"Circular dependency detected involving quest {quest_id}")
        
        # Check that all prerequisite quests are in the chain
        for quest_id in chain.quest_ids:
            quest_rules = branching_rules.get(quest_id, {})
            prerequisites = quest_rules.get("prerequisites", [])
            
            for prereq in prerequisites:
                if prereq not in chain.quest_ids:
                    errors.append(
                        f"Quest {quest_id} has prerequisite {prereq} "
                        f"which is not in the chain"
                    )
        
        return errors 