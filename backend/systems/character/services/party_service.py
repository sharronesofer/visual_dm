"""
Party Service
------------
Service layer for party-related operations, encapsulating business logic
and database interactions.
"""
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID, uuid4
from datetime import datetime

from backend.core.database import get_db_session
from backend.core.utils.error import NotFoundError, DatabaseError, ValidationError
from backend.systems.character.models.character import Character
from backend.systems.memory.memory_utils import log_permanent_memory

class PartyService:
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session if db_session else next(get_db_session())
    
    def create_party(self, player_id: Union[str, UUID], npc_ids: List[Union[str, UUID]]) -> str:
        """
        Create a new party with a player and NPCs.
        
        Args:
            player_id: ID of the player character
            npc_ids: List of NPC IDs to add to the party
            
        Returns:
            Party ID
            
        Raises:
            DatabaseError: If there's an issue with the database operation
        """
        party_id = f"party_{player_id}"
        
        # In a proper ORM setup, we would create a Party model instance here
        # For now, we'll implement the Firebase logic but structured for future migration
        try:
            # Simulate party creation in database
            party_data = {
                "party_id": party_id,
                "members": [str(player_id)] + [str(npc_id) for npc_id in npc_ids],
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Update character party references
            player_char = self._get_character_by_id(player_id)
            player_char.party_id = party_id
            
            for npc_id in npc_ids:
                npc_char = self._get_character_by_id(npc_id)
                npc_char.party_id = party_id
                
                # Log memory
                log_permanent_memory(
                    npc_id, 
                    f"Joined party with player {player_id} on {datetime.utcnow().isoformat()}"
                )
                
            self.db.commit()
            return party_id
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create party: {str(e)}")
    
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
            DatabaseError: If there's an issue with the database operation
        """
        try:
            # Get party data (would be a Party model in proper ORM setup)
            party = self._get_party_by_id(party_id)
            
            if str(npc_id) not in party["members"]:
                party["members"].append(str(npc_id))
                
                # Update character party reference
                npc_char = self._get_character_by_id(npc_id)
                npc_char.party_id = party_id
                
                # Log memory
                log_permanent_memory(
                    npc_id, 
                    f"Added to party {party_id} on {datetime.utcnow().isoformat()}"
                )
                
                self.db.commit()
                return True
            return False
            
        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to add to party: {str(e)}")
    
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
            DatabaseError: If there's an issue with the database operation
        """
        try:
            # Get party data
            party = self._get_party_by_id(party_id)
            
            if str(member_id) in party["members"]:
                party["members"].remove(str(member_id))
                
                # Update character party reference
                member_char = self._get_character_by_id(member_id)
                member_char.party_id = None
                
                # Log memory
                log_permanent_memory(
                    member_id, 
                    f"Removed from party {party_id} on {datetime.utcnow().isoformat()}"
                )
                
                self.db.commit()
                return True
            return False
            
        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to remove from party: {str(e)}")
    
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
        try:
            party = self._get_party_by_id(party_id)
            member_levels = []
            
            for member_id in party["members"]:
                character = self._get_character_by_id(member_id)
                member_levels.append(character.level)
            
            if not member_levels:
                return 0
                
            total_level = sum(member_levels)
            return total_level if mode == "sum" else total_level // len(member_levels)
            
        except NotFoundError:
            raise
    
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
            DatabaseError: If there's an issue with the database operation
        """
        try:
            party = self._get_party_by_id(party_id)
            awarded = {}
            
            for member_id in party["members"]:
                character = self._get_character_by_id(member_id)
                character.xp = character.xp + amount
                awarded[str(member_id)] = character.xp
            
            self.db.commit()
            return awarded
            
        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to award XP: {str(e)}")
    
    def abandon_party(self, npc_id: Union[str, UUID]) -> bool:
        """
        Remove an NPC from any party they're in due to loyalty loss.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            DatabaseError: If there's an issue with the database operation
        """
        try:
            npc_char = self._get_character_by_id(npc_id)
            
            if not npc_char.party_id:
                return False
                
            party_id = npc_char.party_id
            party = self._get_party_by_id(party_id)
            
            if str(npc_id) in party["members"]:
                party["members"].remove(str(npc_id))
                npc_char.party_id = None
                
                # Set status effect
                if not hasattr(npc_char, 'status_effects'):
                    npc_char.status_effects = []
                npc_char.status_effects.append("abandoned")
                
                # Log memory
                log_permanent_memory(
                    npc_id, 
                    f"Abandoned party {party_id} due to loyalty loss on {datetime.utcnow().isoformat()}"
                )
                
                self.db.commit()
                return True
            return False
            
        except NotFoundError:
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to abandon party: {str(e)}")
    
    # === Helper Methods ===
    def _get_character_by_id(self, character_id: Union[str, UUID]) -> Character:
        """Internal helper to fetch a Character by ID."""
        character = self.db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise NotFoundError(f"Character with ID {character_id} not found")
        return character
    
    def _get_party_by_id(self, party_id: str) -> Dict[str, Any]:
        """
        Internal helper to fetch a Party by ID.
        
        Note: This is a placeholder for a future ORM-based implementation.
        Currently simulates Firebase access with a structure compatible with future ORM migration.
        """
        # In a proper ORM setup, this would query the Party model
        # For now, we'll implement a placeholder
        party = {
            "party_id": party_id,
            "members": ["member1", "member2"],  # Placeholder data
            "created_at": datetime.utcnow().isoformat()
        }
        
        # In a real implementation, we would check if party exists
        if not party:
            raise NotFoundError(f"Party with ID {party_id} not found")
        
        return party 