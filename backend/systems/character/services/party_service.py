"""
Party Service
------------
Service layer for party-related operations, encapsulating business logic.
Separates business logic from data access.
"""
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4
from datetime import datetime

# Business logic imports
from backend.systems.character.models.character import Character
from backend.infrastructure.database_services.party_repository import PartyRepository
from backend.infrastructure.shared.exceptions import NotFoundError, RepositoryError, ValidationError
from backend.infrastructure.memory_utils.memory_utilities import log_permanent_memory

import logging

logger = logging.getLogger(__name__)


class PartyService:
    """Service for managing parties with pure business logic"""
    
    def __init__(self, party_repository: PartyRepository):
        self.party_repository = party_repository
        logger.info("PartyService initialized")
    
    def create_party(self, player_id: Union[str, UUID], npc_ids: List[Union[str, UUID]]) -> str:
        """
        Create a new party with a player and NPCs.
        
        Args:
            player_id: ID of the player character
            npc_ids: List of NPC IDs to add to the party
            
        Returns:
            Party ID
            
        Raises:
            RepositoryError: If there's an issue with the database operation
        """
        party_id = f"party_{player_id}"
        
        try:
            # Update character party references
            player_char = self.party_repository.get_character_by_id(player_id)
            if not player_char:
                raise NotFoundError(f"Player character {player_id} not found")
            
            self.party_repository.update_character_party(player_id, party_id)
            
            for npc_id in npc_ids:
                npc_char = self.party_repository.get_character_by_id(npc_id)
                if not npc_char:
                    raise NotFoundError(f"NPC character {npc_id} not found")
                
                self.party_repository.update_character_party(npc_id, party_id)
                
                # Log memory
                log_permanent_memory(
                    npc_id, 
                    f"Joined party with player {player_id} on {datetime.utcnow().isoformat()}"
                )
                
            self.party_repository.commit()
            logger.info(f"Created party {party_id} with player {player_id} and {len(npc_ids)} NPCs")
            return party_id
            
        except Exception as e:
            self.party_repository.rollback()
            raise RepositoryError(f"Failed to create party: {str(e)}")
    
    def add_to_party(self, party_id: str, npc_id: Union[str, UUID]) -> bool:
        """
        Add an NPC to an existing party.
        
        Args:
            party_id: ID of the party
            npc_id: ID of the NPC to add
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            NotFoundError: If the party doesn't exist
            RepositoryError: If there's an issue with the database operation
        """
        try:
            # Check if party exists by getting its members
            party_members = self.party_repository.get_party_members(party_id)
            if not party_members:
                raise NotFoundError(f"Party {party_id} not found")
            
            # Check if NPC exists
            npc_char = self.party_repository.get_character_by_id(npc_id)
            if not npc_char:
                raise NotFoundError(f"NPC character {npc_id} not found")
            
            # Check if NPC is already in a party
            if npc_char.party_id:
                logger.warning(f"NPC {npc_id} is already in party {npc_char.party_id}")
                return False
            
            # Add NPC to party
            self.party_repository.update_character_party(npc_id, party_id)
            
            # Log memory
            log_permanent_memory(
                npc_id, 
                f"Added to party {party_id} on {datetime.utcnow().isoformat()}"
            )
            
            self.party_repository.commit()
            logger.info(f"Added NPC {npc_id} to party {party_id}")
            return True
            
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            self.party_repository.rollback()
            raise RepositoryError(f"Failed to add to party: {str(e)}")
    
    def remove_from_party(self, party_id: str, member_id: Union[str, UUID]) -> bool:
        """
        Remove a member from a party.
        
        Args:
            party_id: ID of the party
            member_id: ID of the member to remove
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            NotFoundError: If the party doesn't exist
            RepositoryError: If there's an issue with the database operation
        """
        try:
            # Check if member exists and is in the party
            member_char = self.party_repository.get_character_by_id(member_id)
            if not member_char:
                raise NotFoundError(f"Character {member_id} not found")
            
            if member_char.party_id != party_id:
                logger.warning(f"Character {member_id} is not in party {party_id}")
                return False
            
            # Remove from party
            self.party_repository.update_character_party(member_id, None)
            
            # Log memory
            log_permanent_memory(
                member_id, 
                f"Removed from party {party_id} on {datetime.utcnow().isoformat()}"
            )
            
            self.party_repository.commit()
            logger.info(f"Removed member {member_id} from party {party_id}")
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            self.party_repository.rollback()
            raise RepositoryError(f"Failed to remove from party: {str(e)}")
    
    def get_total_party_level(self, party_id: str, mode: str = "sum") -> int:
        """
        Get the total or average level of a party.
        
        Args:
            party_id: ID of the party
            mode: "sum" for total, "avg" for average
            
        Returns:
            Total or average party level
            
        Raises:
            NotFoundError: If the party doesn't exist
        """
        party_members = self.party_repository.get_party_members(party_id)
        if not party_members:
            raise NotFoundError(f"Party {party_id} not found or has no members")
        
        member_levels = [member.level for member in party_members]
        
        if not member_levels:
            return 0
            
        total_level = sum(member_levels)
        return total_level if mode == "sum" else total_level // len(member_levels)
    
    def award_xp_to_party(self, party_id: str, amount: int) -> Dict[str, int]:
        """
        Award XP to all members of a party.
        
        Args:
            party_id: ID of the party
            amount: Amount of XP to award
            
        Returns:
            Dictionary mapping member IDs to their new XP totals
            
        Raises:
            NotFoundError: If the party doesn't exist
            RepositoryError: If there's an issue with the database operation
        """
        try:
            party_members = self.party_repository.get_party_members(party_id)
            if not party_members:
                raise NotFoundError(f"Party {party_id} not found or has no members")
            
            xp_results = {}
            
            for member in party_members:
                updated_member = self.party_repository.update_character_xp(member.id, amount)
                xp_results[str(member.id)] = getattr(updated_member, 'xp', amount)
                
                # Log memory for NPCs (assuming player characters handle their own logging)
                if member.id != party_members[0].id:  # Assume first member is player
                    log_permanent_memory(
                        member.id,
                        f"Gained {amount} XP in party {party_id} on {datetime.utcnow().isoformat()}"
                    )
            
            self.party_repository.commit()
            logger.info(f"Awarded {amount} XP to {len(party_members)} members of party {party_id}")
            return xp_results
            
        except NotFoundError:
            raise
        except Exception as e:
            self.party_repository.rollback()
            raise RepositoryError(f"Failed to award XP to party: {str(e)}")
    
    def abandon_party(self, npc_id: Union[str, UUID]) -> bool:
        """
        Have an NPC abandon their current party.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            True if successful, False if NPC wasn't in a party
            
        Raises:
            NotFoundError: If the NPC doesn't exist
            RepositoryError: If there's an issue with the database operation
        """
        try:
            npc_char = self.party_repository.get_character_by_id(npc_id)
            if not npc_char:
                raise NotFoundError(f"NPC character {npc_id} not found")
            
            if not npc_char.party_id:
                logger.info(f"NPC {npc_id} is not in a party")
                return False
            
            old_party_id = npc_char.party_id
            self.party_repository.update_character_party(npc_id, None)
            
            # Log memory
            log_permanent_memory(
                npc_id,
                f"Abandoned party {old_party_id} on {datetime.utcnow().isoformat()}"
            )
            
            self.party_repository.commit()
            logger.info(f"NPC {npc_id} abandoned party {old_party_id}")
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            self.party_repository.rollback()
            raise RepositoryError(f"Failed to abandon party: {str(e)}")
    
    def get_party_members(self, party_id: str) -> List[Character]:
        """
        Get all members of a party.
        
        Args:
            party_id: ID of the party
            
        Returns:
            List of Character instances
            
        Raises:
            NotFoundError: If the party doesn't exist
        """
        party_members = self.party_repository.get_party_members(party_id)
        if not party_members:
            raise NotFoundError(f"Party {party_id} not found or has no members")
        return party_members
    
    def get_party_summary(self, party_id: str) -> Dict[str, Any]:
        """
        Get a summary of a party including members and stats.
        
        Args:
            party_id: ID of the party
            
        Returns:
            Dictionary with party information
        """
        members = self.get_party_members(party_id)
        
        return {
            "party_id": party_id,
            "member_count": len(members),
            "members": [
                {
                    "id": str(member.id),
                    "name": member.name,
                    "level": member.level,
                    "race": getattr(member, 'race', 'Unknown')
                }
                for member in members
            ],
            "total_level": self.get_total_party_level(party_id, "sum"),
            "average_level": self.get_total_party_level(party_id, "avg")
        } 