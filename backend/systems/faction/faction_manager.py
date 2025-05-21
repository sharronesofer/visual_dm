"""
Faction system manager module.

This module provides the main FactionManager class that serves as the
entry point for faction functionality in the Visual DM system.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from backend.systems.faction.models.faction import Faction, FactionRelationship, FactionMembership
from backend.systems.faction.services.faction_service import (
    FactionService, 
    FactionRelationshipService,
    FactionMembershipService,
    FactionNotFoundError
)
from backend.systems.faction.schemas.faction_types import (
    FactionType, 
    FactionAlignment, 
    DiplomaticStance
)


class FactionManager:
    """
    Main manager for the faction system.
    
    This class serves as the primary interface for other systems to interact
    with the faction system.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the faction manager.
        
        Args:
            db: Database session
        """
        self.db = db
        
    # Faction operations
    
    def create_faction(
        self,
        name: str,
        description: str,
        faction_type: Union[FactionType, str],
        alignment: Optional[FactionAlignment] = None,
        influence: float = 50.0,
        resources: Dict[str, Any] = None,
        territory: Dict[str, Any] = None,
        leader_id: Optional[int] = None,
        headquarters_id: Optional[int] = None,
        parent_faction_id: Optional[int] = None,
        metadata: Dict[str, Any] = None
    ) -> Faction:
        """
        Create a new faction.
        
        Args:
            name: Faction name
            description: Faction description
            faction_type: Type of faction
            alignment: Moral alignment (optional)
            influence: Initial influence value (optional)
            resources: Initial resources (optional)
            territory: Initial territories (optional)
            leader_id: ID of NPC leader (optional)
            headquarters_id: ID of headquarters location (optional)
            parent_faction_id: ID of parent faction (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            Created Faction instance
        """
        # Convert string to enum if needed
        if isinstance(faction_type, str):
            faction_type = FactionType(faction_type)
            
        return FactionService.create_faction(
            db=self.db,
            name=name,
            description=description,
            faction_type=faction_type,
            alignment=alignment,
            influence=influence,
            resources=resources,
            territory=territory,
            leader_id=leader_id,
            headquarters_id=headquarters_id,
            parent_faction_id=parent_faction_id,
            metadata=metadata
        )
    
    def get_faction(self, faction_id: int) -> Optional[Faction]:
        """
        Get a faction by ID.
        
        Args:
            faction_id: ID of faction to retrieve
            
        Returns:
            Faction instance or None if not found
        """
        return FactionService.get_faction(self.db, faction_id)
    
    def get_faction_by_name(self, name: str) -> Optional[Faction]:
        """
        Get a faction by name.
        
        Args:
            name: Name of faction to retrieve
            
        Returns:
            Faction instance or None if not found
        """
        return FactionService.get_faction_by_name(self.db, name)
    
    def get_factions(self, **filters) -> List[Faction]:
        """
        Get factions with optional filters.
        
        Args:
            **filters: Filter criteria
            
        Returns:
            List of matching Faction instances
        """
        return FactionService.get_factions(self.db, **filters)
    
    def update_faction(self, faction_id: int, **updates) -> Faction:
        """
        Update a faction.
        
        Args:
            faction_id: ID of faction to update
            **updates: Attributes to update
            
        Returns:
            Updated Faction instance
            
        Raises:
            FactionNotFoundError: If faction not found
        """
        return FactionService.update_faction(self.db, faction_id, **updates)
    
    def delete_faction(self, faction_id: int) -> None:
        """
        Delete a faction.
        
        Args:
            faction_id: ID of faction to delete
            
        Raises:
            FactionNotFoundError: If faction not found
        """
        FactionService.delete_faction(self.db, faction_id)
        
    # Relationship operations
    
    def set_diplomatic_stance(
        self,
        faction_id: int,
        other_faction_id: int,
        stance: Union[DiplomaticStance, str],
        **kwargs
    ) -> FactionRelationship:
        """
        Set diplomatic stance between factions.
        
        Args:
            faction_id: ID of first faction
            other_faction_id: ID of second faction
            stance: Diplomatic stance to set
            **kwargs: Additional relationship attributes
            
        Returns:
            Created/updated FactionRelationship instance
        """
        # Convert string to enum if needed
        if isinstance(stance, str):
            stance = DiplomaticStance(stance)
            
        return FactionRelationshipService.set_diplomatic_stance(
            db=self.db,
            faction_id=faction_id,
            other_faction_id=other_faction_id,
            stance=stance,
            **kwargs
        )
    
    def get_relationship(
        self, 
        faction_id: int, 
        other_faction_id: int
    ) -> Optional[FactionRelationship]:
        """
        Get relationship between factions.
        
        Args:
            faction_id: ID of first faction
            other_faction_id: ID of second faction
            
        Returns:
            FactionRelationship instance or None if not found
        """
        return FactionRelationshipService.get_relationship(
            self.db, faction_id, other_faction_id
        )
    
    def get_faction_relationships(
        self, 
        faction_id: int,
        **filters
    ) -> List[FactionRelationship]:
        """
        Get all relationships for a faction.
        
        Args:
            faction_id: ID of the faction
            **filters: Filter criteria
            
        Returns:
            List of FactionRelationship instances
        """
        return FactionRelationshipService.get_faction_relationships(
            self.db, faction_id, **filters
        )
    
    def update_tension(
        self,
        faction_id: int,
        other_faction_id: int,
        delta: float,
        metadata: Optional[Dict] = None
    ) -> tuple:
        """
        Update tension between factions.
        
        Args:
            faction_id: ID of first faction
            other_faction_id: ID of second faction
            delta: Change in tension value
            metadata: Additional metadata for history
            
        Returns:
            Tuple of (relationship, reciprocal_relationship)
        """
        return FactionRelationshipService.update_tension(
            self.db, faction_id, other_faction_id, delta, metadata
        )
    
    def declare_war(
        self,
        faction_id: int,
        other_faction_id: int,
        reason: str = "unspecified",
        war_details: Optional[Dict] = None
    ) -> tuple:
        """
        Declare war between factions.
        
        Args:
            faction_id: ID of first faction (declarer)
            other_faction_id: ID of second faction (target)
            reason: Reason for war declaration
            war_details: Additional war details
            
        Returns:
            Tuple of (relationship, reciprocal_relationship)
        """
        return FactionRelationshipService.declare_war(
            self.db, faction_id, other_faction_id, reason, war_details
        )
    
    def make_peace(
        self,
        faction_id: int,
        other_faction_id: int,
        terms: Optional[Dict] = None,
        new_stance: DiplomaticStance = DiplomaticStance.NEUTRAL
    ) -> tuple:
        """
        Make peace between factions.
        
        Args:
            faction_id: ID of first faction
            other_faction_id: ID of second faction
            terms: Peace treaty terms
            new_stance: New diplomatic stance after peace
            
        Returns:
            Tuple of (relationship, reciprocal_relationship)
        """
        return FactionRelationshipService.make_peace(
            self.db, faction_id, other_faction_id, terms, new_stance
        )
      
    # Membership operations
    
    def assign_faction_to_character(
        self, 
        faction_id: int, 
        character_id: int,
        loyalty: int = 1,
        role: str = "member",
        is_public: bool = True,
        metadata: Optional[Dict] = None
    ) -> FactionMembership:
        """
        Assign a character to a faction.
        
        Args:
            faction_id: ID of the faction
            character_id: ID of the character/NPC
            loyalty: Loyalty level (-3 to 3)
            role: Role within faction
            is_public: Whether membership is public
            metadata: Additional membership data
            
        Returns:
            Created/updated FactionMembership instance
        """
        return FactionMembershipService.assign_faction(
            db=self.db,
            faction_id=faction_id,
            character_id=character_id,
            loyalty=loyalty,
            role=role,
            is_public=is_public,
            metadata=metadata
        )
    
    def get_faction_members(
        self, 
        faction_id: int,
        min_loyalty: Optional[int] = None,
        role: Optional[str] = None,
        is_public: Optional[bool] = None
    ) -> List[FactionMembership]:
        """
        Get all members of a faction with optional filters.
        
        Args:
            faction_id: ID of the faction
            min_loyalty: Minimum loyalty level
            role: Filter by role
            is_public: Filter by public status
            
        Returns:
            List of FactionMembership instances
        """
        return FactionMembershipService.get_faction_members(
            self.db, faction_id, min_loyalty, role, is_public
        )
    
    def get_character_factions(
        self, 
        character_id: int,
        min_loyalty: Optional[int] = None,
        include_secret: bool = False
    ) -> List[FactionMembership]:
        """
        Get all factions a character belongs to.
        
        Args:
            character_id: ID of the character/NPC
            min_loyalty: Minimum loyalty level
            include_secret: Whether to include non-public memberships
            
        Returns:
            List of FactionMembership instances
        """
        return FactionMembershipService.get_character_factions(
            self.db, character_id, min_loyalty, include_secret
        )
        
    def update_character_loyalty(
        self,
        faction_id: int,
        character_id: int,
        delta: int,
        reason: Optional[str] = None
    ) -> FactionMembership:
        """
        Update a character's loyalty to a faction.
        
        Args:
            faction_id: ID of the faction
            character_id: ID of the character/NPC
            delta: Change in loyalty (-3 to 3)
            reason: Reason for loyalty change
            
        Returns:
            Updated FactionMembership instance
        """
        return FactionMembershipService.update_loyalty(
            self.db, faction_id, character_id, delta, reason
        )
    
    def remove_character_from_faction(
        self,
        faction_id: int,
        character_id: int,
        reason: Optional[str] = None
    ) -> bool:
        """
        Remove a character from a faction.
        
        Args:
            faction_id: ID of the faction
            character_id: ID of the character/NPC
            reason: Reason for removal
            
        Returns:
            True if membership was deleted, False if not found
        """
        return FactionMembershipService.remove_from_faction(
            self.db, faction_id, character_id, reason
        )
    
    # Faction influence operations
    
    def assign_faction_to_poi(
        self,
        faction_id: int,
        poi_id: int,
        control_level: int = 10,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Assign a faction to a POI with a control level.
        
        Args:
            faction_id: ID of the faction
            poi_id: ID of the POI
            control_level: Control/influence level (0-10)
            metadata: Additional control metadata
            
        Returns:
            POI control data
        """
        return FactionService.assign_faction_to_poi(
            self.db, faction_id, poi_id, control_level, metadata
        )
    
    def propagate_faction_influence(self) -> List[Dict]:
        """
        Run faction influence propagation across POIs.
        Simulates faction influence spreading outward from origin POIs.
        
        Returns:
            List of propagation events
        """
        return FactionService.propagate_faction_influence(self.db)
    
    def calculate_affinity(
        self,
        character_id: int,
        faction_id: int
    ) -> int:
        """
        Calculate affinity score between a character and faction.
        Compares character traits against faction traits.
        
        Args:
            character_id: ID of the character/NPC
            faction_id: ID of the faction
            
        Returns:
            Affinity score (0-36)
        """
        return FactionService.calculate_affinity(
            self.db, character_id, faction_id
        )
        
    def drift_character_opinions(self) -> List[Dict]:
        """
        Apply natural drift to character opinions of factions.
        
        Returns:
            List of results for each change that occurred
        """
        # This is a placeholder for now
        # Would implement drift based on relationships, motifs, etc.
        return []
        
    def check_faction_schism(
        self,
        faction_id: int,
        internal_tension: float = None,
        ideological_divide: Dict[str, Any] = None,
        trigger_event: Dict[str, Any] = None,
        schism_threshold: float = 80.0
    ) -> Dict[str, Any]:
        """
        Check if conditions are right for a faction schism and create a new faction if so.
        
        This implements the faction schism functionality described in the development bible,
        allowing factions to split based on tension, ideology, or events.
        
        Args:
            faction_id: ID of the faction to check for schism
            internal_tension: Explicit internal tension value (optional)
            ideological_divide: Details of ideological division (optional)
            trigger_event: Event that might trigger schism (optional)
            schism_threshold: Tension threshold for schism (default: 80.0)
            
        Returns:
            Dict with schism details or empty dict if no schism occurred
            
        Usage Example:
            # Check if a schism occurs due to religious differences
            schism_details = faction_manager.check_faction_schism(
                faction_id=5,
                ideological_divide={
                    "cause": "religious reformation",
                    "strength": 30.0,
                    "type": "religious"
                }
            )
            
            # Or trigger a schism from a specific event
            schism_details = faction_manager.check_faction_schism(
                faction_id=5,
                trigger_event={
                    "description": "assassination of faction leader",
                    "tension_modifier": 40.0
                }
            )
        """
        return FactionRelationshipService.check_for_schism(
            db=self.db,
            faction_id=faction_id,
            internal_tension=internal_tension,
            ideological_divide=ideological_divide,
            trigger_event=trigger_event,
            schism_threshold=schism_threshold
        )
        
    def switch_character_faction(
        self,
        character_id: int,
        current_faction_id: int,
        target_faction_id: int,
        affinity_score: Optional[int] = None,
        min_affinity_threshold: int = 60,
        contextual_restrictions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Switch a character's faction membership based on affinity score.
        
        Implements affinity-based faction switching as described in the development bible,
        allowing entities to switch factions based on affinity.
        
        Args:
            character_id: Character making the switch
            current_faction_id: Current faction ID
            target_faction_id: Target faction ID
            affinity_score: Pre-calculated affinity score (optional)
            min_affinity_threshold: Minimum affinity needed to switch (default: 60)
            contextual_restrictions: Optional restrictions on switching
            
        Returns:
            Dict with switch details or error information
            
        Usage Example:
            # Switch a character to a new faction if they have sufficient affinity
            switch_result = faction_manager.switch_character_faction(
                character_id=42,
                current_faction_id=5,
                target_faction_id=8
            )
            
            # Check for success
            if switch_result["success"]:
                print(f"Character switched to faction {switch_result['to_faction_id']}")
            else:
                print(f"Switch failed: {switch_result['message']}")
                
            # With contextual restrictions
            switch_result = faction_manager.switch_character_faction(
                character_id=42,
                current_faction_id=5,
                target_faction_id=8,
                contextual_restrictions={
                    "check_war": True,
                    "check_leadership": True,
                    "check_loyalty_period": True,
                    "min_days_before_switch": 60
                }
            )
        """
        # If affinity score isn't provided, calculate it first
        if affinity_score is None:
            affinity_score = self.calculate_affinity(character_id, target_faction_id)
            
        # Call the service method for switching
        from backend.systems.faction.services.membership_service import FactionMembershipService
        
        return FactionMembershipService.switch_faction_by_affinity(
            db=self.db,
            character_id=character_id,
            current_faction_id=current_faction_id,
            target_faction_id=target_faction_id,
            affinity_score=affinity_score,
            min_affinity_threshold=min_affinity_threshold,
            contextual_restrictions=contextual_restrictions
        )
        
    def process_tension_decay(
        self,
        decay_rate_positive: float = 0.5,
        decay_rate_negative: float = 0.5,
        min_decay: float = 0.1,
        max_decay: float = 2.5
    ) -> Dict[str, Any]:
        """
        Process natural decay of tensions between all factions.
        
        As described in the development bible, tension decays naturally over time 
        in both directions: positive tensions (conflict) decay toward neutral, and 
        negative tensions (alliances) decay toward neutral as well.
        
        This method should be called on a regular interval, such as once per game day
        or week, depending on the desired decay rate.
        
        Args:
            decay_rate_positive: Base decay rate for positive tensions (0-100, conflict) (default: 0.5)
            decay_rate_negative: Base decay rate for negative tensions (-100-0, alliance) (default: 0.5)
            min_decay: Minimum decay amount per process (default: 0.1)
            max_decay: Maximum decay amount per process (default: 2.5)
            
        Returns:
            Dict with statistics about the decay operations
            
        Usage Example:
            # Run tension decay as part of a daily game cycle
            decay_stats = faction_manager.process_tension_decay()
            print(f"Processed {decay_stats['relationships_processed']} relationships")
            print(f"Decayed {decay_stats['tensions_decayed']} tensions")
            print(f"Total decay amount: {decay_stats['total_decay_amount']:.2f}")
        """
        from backend.systems.faction.faction_tick_utils import decay_faction_tensions
        
        return decay_faction_tensions(
            session=self.db,
            decay_rate_positive=decay_rate_positive,
            decay_rate_negative=decay_rate_negative,
            min_decay=min_decay,
            max_decay=max_decay
        )
        
    def apply_tension_decay(
        self,
        decay_rate: float = 0.1,
        min_decay: float = 1.0,
        max_decay: float = 5.0,
        target_factions: List[int] = None,
        excluded_factions: List[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Apply natural tension decay between factions over time.
        
        As described in the development bible, tensions naturally decay over time
        when no new provocations occur.
        
        Args:
            decay_rate: Base rate of tension decay (default: 0.1)
            min_decay: Minimum tension reduction amount (default: 1.0)
            max_decay: Maximum tension reduction amount (default: 5.0)
            target_factions: Optional list of faction IDs to target specifically
            excluded_factions: Optional list of faction IDs to exclude
            
        Returns:
            List of decay results with details of tension changes
        """
        with self.db_service.get_session() as session:
            return decay_faction_tensions(
                db=session,
                decay_rate=decay_rate,
                min_decay=min_decay,
                max_decay=max_decay,
                target_factions=target_factions,
                excluded_factions=excluded_factions
            )
            
    def resolve_war_outcome(
        self,
        faction_id: int,
        other_faction_id: int,
        victor_id: Optional[int] = None,
        outcome_type: str = "negotiated",  # "victory", "defeat", "negotiated", "stalemate"
        terms: Optional[Dict[str, Any]] = None,
        mechanical_consequences: bool = True
    ) -> Dict[str, Any]:
        """
        Resolve a war between factions with mechanical consequences.
        
        As described in the development bible, war outcomes can have mechanical
        consequences such as resource changes, population shifts, and territory
        changes.
        
        Args:
            faction_id: ID of the first faction
            other_faction_id: ID of the second faction
            victor_id: ID of the victor faction (optional, for victory/defeat outcomes)
            outcome_type: Type of war resolution (default: "negotiated")
            terms: Specific terms of resolution (optional)
            mechanical_consequences: Whether to apply mechanical consequences (default: True)
            
        Returns:
            Dict with outcome details and applied consequences
            
        Raises:
            InvalidRelationshipError: If the factions are not at war
        """
        with self.db_service.get_session() as session:
            from backend.systems.faction.services.relationship_service import FactionRelationshipService
            
            outcome = FactionRelationshipService.resolve_war_outcome(
                db=session,
                faction_id=faction_id,
                other_faction_id=other_faction_id,
                victor_id=victor_id,
                outcome_type=outcome_type,
                terms=terms,
                mechanical_consequences=mechanical_consequences
            )
            
            # Emit faction.war_resolved event
            self.event_dispatcher.emit(
                "faction.war_resolved",
                {
                    "faction_id": faction_id,
                    "other_faction_id": other_faction_id,
                    "outcome_type": outcome_type,
                    "victor_id": victor_id if outcome_type in ["victory", "defeat"] else None,
                    "applied_consequences": outcome.get("applied_consequences", []),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            return outcome
            
    def modify_faction_reputation(
        self,
        faction_id: int,
        amount: float,
        reason: str,
        source: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Modify a faction's global reputation.
        
        As described in the development bible, factions have reputation scores
        that affect how they are perceived by the world at large.
        
        Args:
            faction_id: ID of the faction
            amount: Amount to modify (positive or negative)
            reason: Reason for the change
            source: Optional data about the source of the change
            
        Returns:
            Dict with details of the reputation change
        """
        with self.db_service.get_session() as session:
            from backend.systems.faction.services.reputation_service import FactionReputationService
            
            result = FactionReputationService.modify_global_reputation(
                db=session,
                faction_id=faction_id,
                amount=amount,
                reason=reason,
                source=source
            )
            
            # Emit faction.reputation_changed event
            self.event_dispatcher.emit(
                "faction.reputation_changed",
                {
                    "faction_id": faction_id,
                    "change_amount": amount,
                    "new_reputation": result["new_reputation"],
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            return result
    
    def modify_regional_reputation(
        self,
        faction_id: int,
        region_id: int,
        amount: float,
        reason: str,
        source: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Modify a faction's reputation in a specific region.
        
        Regional reputation affects how a faction is perceived in that region,
        which can be different from their global reputation.
        
        Args:
            faction_id: ID of the faction
            region_id: ID of the region
            amount: Amount to modify (positive or negative)
            reason: Reason for the change
            source: Optional data about the source of the change
            
        Returns:
            Dict with details of the reputation change
        """
        with self.db_service.get_session() as session:
            from backend.systems.faction.services.reputation_service import FactionReputationService
            
            result = FactionReputationService.modify_regional_reputation(
                db=session,
                faction_id=faction_id,
                region_id=region_id,
                amount=amount,
                reason=reason,
                source=source
            )
            
            # Emit faction.regional_reputation_changed event
            self.event_dispatcher.emit(
                "faction.regional_reputation_changed",
                {
                    "faction_id": faction_id,
                    "region_id": region_id,
                    "change_amount": amount,
                    "new_reputation": result["new_reputation"],
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            return result
    
    def modify_character_reputation(
        self,
        faction_id: int,
        character_id: int,
        amount: float,
        reason: str,
        source: Optional[Dict[str, Any]] = None,
        affect_membership: bool = True
    ) -> Dict[str, Any]:
        """
        Modify a faction's reputation with a specific character.
        
        This tracks how a faction views a character, which may differ from
        how a character is perceived by the faction they are a member of.
        
        Args:
            faction_id: ID of the faction
            character_id: ID of the character
            amount: Amount to modify (positive or negative)
            reason: Reason for the change
            source: Optional data about the source of the change
            affect_membership: Whether to also affect membership reputation if applicable
            
        Returns:
            Dict with details of the reputation change
        """
        with self.db_service.get_session() as session:
            from backend.systems.faction.services.reputation_service import FactionReputationService
            
            result = FactionReputationService.modify_character_reputation(
                db=session,
                faction_id=faction_id,
                character_id=character_id,
                amount=amount,
                reason=reason,
                source=source,
                affect_membership=affect_membership
            )
            
            # Emit faction.character_reputation_changed event
            self.event_dispatcher.emit(
                "faction.character_reputation_changed",
                {
                    "faction_id": faction_id,
                    "character_id": character_id,
                    "change_amount": amount,
                    "new_reputation": result["new_reputation"],
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            return result
    
    def get_regional_reputation_summary(
        self,
        faction_id: int
    ) -> Dict[str, Any]:
        """
        Get a summary of a faction's reputation across different regions.
        
        This provides an overview of a faction's standing in various regions,
        with statistics and extremes.
        
        Args:
            faction_id: ID of the faction
            
        Returns:
            Dict with regional reputation summary
        """
        with self.db_service.get_session() as session:
            from backend.systems.faction.services.reputation_service import FactionReputationService
            
            return FactionReputationService.get_regional_reputation_summary(
                db=session,
                faction_id=faction_id
            )
    
    def calculate_faction_reputation_modifiers(
        self,
        faction_id: int
    ) -> Dict[str, float]:
        """
        Calculate gameplay modifiers based on faction reputation.
        
        As described in the development bible, reputation affects numerous
        mechanical aspects of gameplay, including prices, rewards, and more.
        
        Args:
            faction_id: ID of the faction
            
        Returns:
            Dict of modifier name to float value
        """
        with self.db_service.get_session() as session:
            from backend.systems.faction.services.reputation_service import FactionReputationService
            
            return FactionReputationService.calculate_faction_reputation_modifiers(
                db=session,
                faction_id=faction_id
            ) 