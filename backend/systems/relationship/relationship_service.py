"""
Relationship Service
--------------------
Service layer for managing relationships between entities.
"""
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime
import random
from sqlalchemy.orm import Session  # If using SQLAlchemy

from backend.systems.relationship.relationship_model import (
    RelationshipCreate, 
    RelationshipInDB, 
    RelationshipUpdate, 
    RelationshipType
)
from backend.core.database import get_db_session  # Or however session is managed
from backend.core.utils.error import NotFoundError, DatabaseError

# Placeholder for the actual Relationship ORM model if using SQLAlchemy
# from backend.systems.relationship.relationship_model import Relationship as RelationshipORM

class RelationshipService:
    """Service for managing entity relationships including creation, updates, and queries."""
    
    # Relationship tier names for classification
    RELATIONSHIP_TIERS = {
        (-10, -7): "Hostile",
        (-6, -3): "Unfriendly",
        (-2, 2): "Neutral",
        (3, 6): "Friendly",
        (7, 10): "Allied"
    }
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the relationship service.
        
        Args:
            db_session: Optional database session for persistence
        """
        self.db = db_session  # if db_session else next(get_db_session())  # Adapt if not using SQLAlchemy
        # For non-SQLAlchemy, self.db might be a connection to a NoSQL DB or a list for in-memory
        self._relationships_store: List[RelationshipInDB] = []  # In-memory store for now

    def _find_relationship_in_store(self, relationship_id: UUID) -> Optional[int]:
        """
        Helper method to find a relationship by ID in the in-memory store.
        
        Args:
            relationship_id: UUID of the relationship to find
            
        Returns:
            Optional index of the relationship in the store, or None if not found
        """
        for i, rel in enumerate(self._relationships_store):
            if rel.id == relationship_id:
                return i
        return None

    def add_relationship(self, character_id: UUID, target_id: UUID, type: RelationshipType, data: Optional[Dict[str, Any]] = None) -> RelationshipInDB:
        """
        Creates a new relationship.
        
        Args:
            character_id: UUID of the source entity (typically a character)
            target_id: UUID of the target entity (faction, quest, etc.)
            type: Type of relationship
            data: Optional type-specific data payload
            
        Returns:
            The created relationship object
        """
        rel_create = RelationshipCreate(
            source_id=character_id, 
            target_id=target_id, 
            type=type, 
            data=data or {}
        )
        
        # In a real scenario with SQLAlchemy:
        # new_rel_orm = RelationshipORM(**rel_create.dict())
        # self.db.add(new_rel_orm)
        # try:
        #     self.db.commit()
        #     self.db.refresh(new_rel_orm)
        #     return RelationshipInDB.from_orm(new_rel_orm)
        # except Exception as e:
        #     self.db.rollback()
        #     raise DatabaseError(f"Failed to create relationship: {str(e)}")
        
        # In-memory implementation:
        new_rel_db = RelationshipInDB(**rel_create.dict())
        self._relationships_store.append(new_rel_db)
        return new_rel_db

    def get_relationship_by_id(self, relationship_id: UUID) -> Optional[RelationshipInDB]:
        """
        Retrieves a specific relationship by its ID.
        
        Args:
            relationship_id: UUID of the relationship to retrieve
            
        Returns:
            The relationship object if found, None otherwise
        """
        # SQLAlchemy: 
        # rel_orm = self.db.query(RelationshipORM).filter(RelationshipORM.id == relationship_id).first()
        # if not rel_orm: return None
        # return RelationshipInDB.from_orm(rel_orm)

        # In-memory:
        idx = self._find_relationship_in_store(relationship_id)
        if idx is not None:
            return self._relationships_store[idx]
        return None

    def get_relationships_for_source(self, source_id: UUID, type: Optional[RelationshipType] = None) -> List[RelationshipInDB]:
        """
        Retrieves all relationships for a given source entity, optionally filtered by type.
        
        Args:
            source_id: UUID of the source entity
            type: Optional relationship type filter
            
        Returns:
            List of matching relationship objects
        """
        # SQLAlchemy:
        # query = self.db.query(RelationshipORM).filter(RelationshipORM.source_id == source_id)
        # if type:
        #     query = query.filter(RelationshipORM.type == type)
        # results_orm = query.all()
        # return [RelationshipInDB.from_orm(r) for r in results_orm]

        # In-memory:
        results = []
        for rel in self._relationships_store:
            if rel.source_id == source_id:
                if type is None or rel.type == type:
                    results.append(rel)
        return results
    
    def get_relationships_by_target(self, target_id: UUID, type: Optional[RelationshipType] = None) -> List[RelationshipInDB]:
        """
        Retrieves all relationships for a given target entity, optionally filtered by type.
        
        Args:
            target_id: UUID of the target entity
            type: Optional relationship type filter
            
        Returns:
            List of matching relationship objects
        """
        # In-memory:
        results = []
        for rel in self._relationships_store:
            if rel.target_id == target_id:
                if type is None or rel.type == type:
                    results.append(rel)
        return results

    def update_relationship_data(self, relationship_id: UUID, update_data: Dict[str, Any]) -> Optional[RelationshipInDB]:
        """
        Updates the data payload of an existing relationship.
        
        Args:
            relationship_id: UUID of the relationship to update
            update_data: Dictionary of data values to update or add
            
        Returns:
            Updated relationship object
            
        Raises:
            NotFoundError: If the relationship doesn't exist
        """
        # SQLAlchemy:
        # rel_orm = self.db.query(RelationshipORM).filter(RelationshipORM.id == relationship_id).first()
        # if not rel_orm:
        #     raise NotFoundError(f"Relationship {relationship_id} not found")
        # if rel_orm.data:
        #     rel_orm.data.update(update_data) # If JSON, direct update might need mutable_json_type
        # else:
        #     rel_orm.data = update_data
        # try:
        #     self.db.commit()
        #     self.db.refresh(rel_orm)
        #     return RelationshipInDB.from_orm(rel_orm)
        # except Exception as e:
        #     self.db.rollback()
        #     raise DatabaseError(f"Failed to update relationship {relationship_id}: {str(e)}")

        # In-memory:
        idx = self._find_relationship_in_store(relationship_id)
        if idx is not None:
            current_rel = self._relationships_store[idx]
            if current_rel.data:
                current_rel.data.update(update_data)
            else:
                current_rel.data = update_data
            current_rel.updated_at = datetime.utcnow()  # Manually update timestamp
            self._relationships_store[idx] = current_rel  # Re-assign if Pydantic model is immutable-like
            return current_rel
        raise NotFoundError(f"Relationship {relationship_id} not found for update.")

    def delete_relationship(self, relationship_id: UUID) -> bool:
        """
        Deletes a relationship by its ID.
        
        Args:
            relationship_id: UUID of the relationship to delete
            
        Returns:
            True if deleted successfully, False if not found
            
        Raises:
            DatabaseError: If deletion fails
        """
        # SQLAlchemy:
        # rel_orm = self.db.query(RelationshipORM).filter(RelationshipORM.id == relationship_id).first()
        # if not rel_orm:
        #     return False
        # try:
        #     self.db.delete(rel_orm)
        #     self.db.commit()
        #     return True
        # except Exception as e:
        #     self.db.rollback()
        #     raise DatabaseError(f"Failed to delete relationship {relationship_id}: {str(e)}")

        # In-memory:
        idx = self._find_relationship_in_store(relationship_id)
        if idx is not None:
            del self._relationships_store[idx]
            return True
        return False
    
    def find_specific_relationship(self, source_id: UUID, target_id: UUID, type: RelationshipType) -> Optional[RelationshipInDB]:
        """
        Finds a specific relationship between source and target of a given type.
        
        Args:
            source_id: UUID of the source entity
            target_id: UUID of the target entity
            type: Type of relationship
            
        Returns:
            The relationship object if found, None otherwise
        """
        # SQLAlchemy:
        # rel_orm = self.db.query(RelationshipORM).filter(
        #     RelationshipORM.source_id == source_id,
        #     RelationshipORM.target_id == target_id,
        #     RelationshipORM.type == type
        # ).first()
        # if not rel_orm: return None
        # return RelationshipInDB.from_orm(rel_orm)

        # In-memory:
        for rel in self._relationships_store:
            if rel.source_id == source_id and rel.target_id == target_id and rel.type == type:
                return rel
        return None

    def get_character_faction_relationships(self, character_id: UUID) -> List[RelationshipInDB]:
        """
        Retrieves all faction relationships for a given character.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            List of faction relationship objects
        """
        return self.get_relationships_for_source(character_id, RelationshipType.FACTION)

    def get_character_quest_relationships(self, character_id: UUID) -> List[RelationshipInDB]:
        """
        Retrieves all quest relationships for a given character.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            List of quest relationship objects
        """
        return self.get_relationships_for_source(character_id, RelationshipType.QUEST)
    
    def get_relationship_tier(self, relationship: RelationshipInDB) -> str:
        """
        Determines the relationship tier (Hostile, Unfriendly, Neutral, Friendly, Allied)
        based on the trust_score or reputation in the relationship data.
        
        Args:
            relationship: A relationship object
            
        Returns:
            String representing the relationship tier
        """
        trust_score = 0
        if relationship.data:
            trust_score = relationship.data.get("trust_score", relationship.data.get("reputation", 0))
        
        for (min_val, max_val), tier_name in self.RELATIONSHIP_TIERS.items():
            if min_val <= trust_score <= max_val:
                return tier_name
        
        return "Neutral"  # Default if not in any range

    def run_daily_relationship_tick(self) -> List[Dict[str, Any]]:
        """
        Performs daily drift on all relationships to simulate natural changes over time.
        Trust/reputation drifts slightly toward neutral (0) each day with a small random factor.
        
        Returns:
            List of changed relationships with old and new tier information
        """
        changes = []
        
        for rel in self._relationships_store:
            # Skip non-interpersonal or non-faction relationships
            if rel.type not in [RelationshipType.INTERPERSONAL, RelationshipType.FACTION]:
                continue
                
            old_tier = self.get_relationship_tier(rel)
            
            # Get and update trust score
            trust_score = rel.data.get("trust_score", rel.data.get("reputation", 0))
            
            # Drift trust toward 0
            if trust_score > 0:
                trust_score -= 1
            elif trust_score < 0:
                trust_score += 1
                
            # Random modifier for variability
            trust_score += random.choice([-1, 0, 1])
            trust_score = max(-10, min(10, trust_score))  # Clamp between -10 and 10
            
            # Update the relationship data
            if "trust_score" in rel.data:
                rel.data["trust_score"] = trust_score
            elif "reputation" in rel.data:
                rel.data["reputation"] = trust_score
            else:
                rel.data["trust_score"] = trust_score
                
            rel.updated_at = datetime.utcnow()  # Update timestamp
            
            new_tier = self.get_relationship_tier(rel)
            
            # Record significant changes (tier shifts)
            if new_tier != old_tier:
                changes.append({
                    "relationship_id": str(rel.id),
                    "source_id": str(rel.source_id),
                    "target_id": str(rel.target_id),
                    "old_tier": old_tier,
                    "new_tier": new_tier,
                    "new_score": trust_score
                })
                
                # Here we would typically log this change to the entity's memory
                # This is a placeholder for memory integration
                # memory_service.add_memory(rel.source_id, f"Relationship with {rel.target_id} shifted from {old_tier} to {new_tier}")
        
        return changes

    def update_faction_reputation(self, 
                                 character_id: UUID, 
                                 faction_id: UUID, 
                                 reputation_change: Optional[int] = None, 
                                 new_reputation: Optional[int] = None, 
                                 new_standing: Optional[str] = None) -> RelationshipInDB:
        """
        Updates a character's reputation with a faction.
        
        Args:
            character_id: UUID of the character
            faction_id: UUID of the faction
            reputation_change: Optional amount to adjust reputation by
            new_reputation: Optional specific reputation value to set
            new_standing: Optional standing label to set
            
        Returns:
            Updated relationship object
            
        Raises:
            NotFoundError: If the relationship doesn't exist and can't be created
        """
        # Find existing relationship or create new one
        relationship = self.find_specific_relationship(character_id, faction_id, RelationshipType.FACTION)
        
        if not relationship:
            # Create new relationship with default values
            data = {"reputation": 0, "standing": "Neutral"}
            relationship = self.add_relationship(character_id, faction_id, RelationshipType.FACTION, data)
        
        # Update data based on parameters
        update_data = {}
        
        if reputation_change is not None:
            current_rep = relationship.data.get("reputation", 0)
            new_rep = max(-10, min(10, current_rep + reputation_change))  # Clamp between -10 and 10
            update_data["reputation"] = new_rep
        
        if new_reputation is not None:
            update_data["reputation"] = max(-10, min(10, new_reputation))  # Clamp between -10 and 10
            
        if new_standing is not None:
            update_data["standing"] = new_standing
        elif "reputation" in update_data:
            # Automatically update standing based on new reputation
            for (min_val, max_val), tier_name in self.RELATIONSHIP_TIERS.items():
                if min_val <= update_data["reputation"] <= max_val:
                    update_data["standing"] = tier_name
                    break
        
        # Apply updates
        if update_data:
            updated_rel = self.update_relationship_data(relationship.id, update_data)
            return updated_rel
        
        return relationship

    def update_quest_progress(self,
                             character_id: UUID,
                             quest_id: UUID,
                             progress: Optional[float] = None,
                             status: Optional[str] = None) -> RelationshipInDB:
        """
        Updates a character's progress or status on a quest.
        
        Args:
            character_id: UUID of the character
            quest_id: UUID of the quest
            progress: Optional progress value (0.0 to 1.0)
            status: Optional status string (e.g., "active", "completed", "failed")
            
        Returns:
            Updated relationship object
            
        Raises:
            NotFoundError: If the relationship doesn't exist and can't be created
            ValueError: If progress is outside the valid range
        """
        # Validate progress
        if progress is not None and (progress < 0.0 or progress > 1.0):
            raise ValueError("Progress must be between 0.0 and 1.0")
        
        # Find existing relationship or create new one
        relationship = self.find_specific_relationship(character_id, quest_id, RelationshipType.QUEST)
        
        if not relationship:
            # Create new relationship with default values
            data = {"progress": 0.0, "status": "inactive"}
            relationship = self.add_relationship(character_id, quest_id, RelationshipType.QUEST, data)
        
        # Update data based on parameters
        update_data = {}
        
        if progress is not None:
            update_data["progress"] = progress
            
        if status is not None:
            update_data["status"] = status
        
        # Apply updates
        if update_data:
            updated_rel = self.update_relationship_data(relationship.id, update_data)
            return updated_rel
        
        return relationship
    
    def update_loyalty(self, 
                      character_id: UUID, 
                      npc_id: UUID,
                      cha_score: int = 10,
                      context_tags: List[str] = None) -> RelationshipInDB:
        """
        Updates loyalty, goodwill, and relationship status between a character and an NPC.
        Used for tracking NPC companions/followers and their loyalty over time.
        
        Args:
            character_id: UUID of the character
            npc_id: UUID of the NPC
            cha_score: Character's Charisma score, affects loyalty regeneration
            context_tags: Optional list of contextual tags affecting the relationship
            
        Returns:
            Updated relationship object
        """
        # Find existing relationship or create new one
        relationship = self.find_specific_relationship(npc_id, character_id, RelationshipType.INTERPERSONAL)
        
        if not relationship:
            # Create new relationship with default values
            data = {
                "loyalty": 0,
                "goodwill": 18,  # Default starting value
                "tags": context_tags or [],
                "auto_abandon": False
            }
            relationship = self.add_relationship(npc_id, character_id, RelationshipType.INTERPERSONAL, data)
        
        # Get current values
        data = relationship.data
        loyalty = data.get("loyalty", 0)
        goodwill = data.get("goodwill", 18)
        tags = data.get("tags", [])
        auto_abandon = data.get("auto_abandon", False)
        
        # Add any new context tags
        if context_tags:
            new_tags = set(tags + context_tags)
            tags = list(new_tags)
        
        # Calculate goodwill regeneration (influenced by CHA)
        cha_mod = max(-5, min(5, (cha_score - 10) // 2))  # Calculate CHA modifier
        base_regen = 3 if loyalty >= 10 else 1 if loyalty > 0 else 0
        regen = base_regen + cha_mod
        
        goodwill = min(36, goodwill + regen)  # Cap at 36
        
        # Loyalty adjusts based on goodwill
        if loyalty < 10 and goodwill >= 30:
            loyalty += 1
        elif loyalty > -10 and goodwill <= 6:
            loyalty -= 1
            
        # Auto-abandonment logic
        if goodwill <= 0 and loyalty <= -5:
            auto_abandon = True
        elif loyalty >= 10:
            auto_abandon = False
            
        # Prepare update data
        update_data = {
            "loyalty": max(-10, min(10, loyalty)),  # Clamp between -10 and 10
            "goodwill": max(0, min(36, goodwill)),  # Clamp between 0 and 36
            "tags": tags,
            "auto_abandon": auto_abandon,
            "last_tick": datetime.utcnow().isoformat()
        }
        
        # Apply updates
        updated_rel = self.update_relationship_data(relationship.id, update_data)
        return updated_rel
        
    def check_betrayal(self, 
                       character_id: UUID, 
                       npc_id: UUID, 
                       cha_score: int = 10) -> Tuple[bool, str]:
        """
        Checks if an NPC will betray a character based on loyalty, goodwill, and a die roll.
        
        Args:
            character_id: UUID of the character
            npc_id: UUID of the NPC
            cha_score: Character's Charisma score, affects betrayal check
            
        Returns:
            Tuple of (will_betray: bool, reason: str) indicating betrayal result and reason
        """
        # Find existing relationship
        relationship = self.find_specific_relationship(npc_id, character_id, RelationshipType.INTERPERSONAL)
        
        if not relationship:
            return False, "No relationship exists"
            
        # Get values
        loyalty = relationship.data.get("loyalty", 0)
        goodwill = relationship.data.get("goodwill", 18)
        
        # If loyalty and goodwill are good, no betrayal
        if loyalty > 0 or goodwill > 0:
            return False, "Loyalty/goodwill too high for betrayal"
            
        # Calculate betrayal chance
        cha_mod = max(-5, min(5, (cha_score - 10) // 2))  # Calculate CHA modifier
        
        # Roll 1d20 + CHA modifier vs DC of (10 + abs(loyalty))
        roll = random.randint(1, 20) + cha_mod
        dc = 10 + abs(loyalty)
        
        if roll >= dc:
            return False, f"Betrayal check passed (rolled {roll} vs DC {dc})"
        else:
            return True, f"Betrayal! (rolled {roll} vs DC {dc})" 