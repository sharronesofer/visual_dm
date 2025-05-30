"""
Service layer for managing faction relationships.

This module provides the FactionRelationshipService class for creating, retrieving,
and managing diplomatic relationships between factions.
"""

from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
import random

from backend.systems.faction.models.faction import Faction, FactionRelationship, FactionMembership
from backend.systems.faction.schemas.faction_types import DiplomaticStance
from backend.systems.faction.services.faction_service import FactionNotFoundError


class InvalidRelationshipError(Exception):
    """Raised when an invalid relationship operation is attempted."""
    pass


class FactionRelationshipService:
    """Service for managing relationships between factions."""
    
    @staticmethod
    def set_diplomatic_stance(
        db: Session,
        faction_id: int,
        other_faction_id: int,
        stance: DiplomaticStance,
        treaties: List[Dict] = None,
        metadata: Dict = None
    ) -> FactionRelationship:
        """
        Set or update the diplomatic stance between two factions.
        
        Args:
            db: Database session
            faction_id: ID of the first faction
            other_faction_id: ID of the second faction
            stance: The diplomatic stance (see DiplomaticStance enum)
            treaties: List of treaties (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            FactionRelationship instance
            
        Raises:
            FactionNotFoundError: If either faction doesn't exist
        """
        # Verify both factions exist
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        other_faction = db.query(Faction).filter(Faction.id == other_faction_id).first()
        
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")
        if not other_faction:
            raise FactionNotFoundError(f"Faction {other_faction_id} not found")
            
        # Get or create relationship
        relationship = db.query(FactionRelationship).filter(
            FactionRelationship.faction_id == faction_id,
            FactionRelationship.other_faction_id == other_faction_id
        ).first()
        
        stance_value = stance.value if isinstance(stance, DiplomaticStance) else stance
        
        if relationship:
            # Update existing relationship
            relationship.diplomatic_stance = stance_value
            
            # Update tension based on stance
            if stance_value == DiplomaticStance.ALLIED.value:
                relationship.tension = -80.0
            elif stance_value == DiplomaticStance.FRIENDLY.value:
                relationship.tension = -40.0
            elif stance_value == DiplomaticStance.NEUTRAL.value:
                relationship.tension = 0.0
            elif stance_value == DiplomaticStance.UNFRIENDLY.value:
                relationship.tension = 40.0
            elif stance_value == DiplomaticStance.HOSTILE.value:
                relationship.tension = 80.0
            elif stance_value == DiplomaticStance.AT_WAR.value:
                relationship.tension = 100.0
                relationship.war_state["at_war"] = True
                
            # Add to history
            event = {
                "type": "stance_changed",
                "stance": stance_value,
                "timestamp": datetime.utcnow().isoformat()
            }
            relationship.history.append(event)
            
            # Update treaties if provided
            if treaties:
                relationship.treaties = treaties
                
            # Update metadata if provided
            if metadata:
                if not relationship.metadata:
                    relationship.metadata = {}
                relationship.metadata.update(metadata)
        else:
            # Create new relationship
            tension = 0.0
            at_war = False
            
            # Set tension based on stance
            if stance_value == DiplomaticStance.ALLIED.value:
                tension = -80.0
            elif stance_value == DiplomaticStance.FRIENDLY.value:
                tension = -40.0
            elif stance_value == DiplomaticStance.NEUTRAL.value:
                tension = 0.0
            elif stance_value == DiplomaticStance.UNFRIENDLY.value:
                tension = 40.0
            elif stance_value == DiplomaticStance.HOSTILE.value:
                tension = 80.0
            elif stance_value == DiplomaticStance.AT_WAR.value:
                tension = 100.0
                at_war = True
                
            # Create history
            history = [{
                "type": "relationship_established",
                "stance": stance_value,
                "timestamp": datetime.utcnow().isoformat()
            }]
            
            # Create relationship
            relationship = FactionRelationship(
                faction_id=faction_id,
                other_faction_id=other_faction_id,
                diplomatic_stance=stance_value,
                tension=tension,
                treaties=treaties or [],
                war_state={"at_war": at_war, "war_details": {}},
                history=history,
                metadata=metadata or {}
            )
            db.add(relationship)
            
        # Create or update the reciprocal relationship
        reciprocal = db.query(FactionRelationship).filter(
            FactionRelationship.faction_id == other_faction_id,
            FactionRelationship.other_faction_id == faction_id
        ).first()
        
        if reciprocal:
            # Update existing reciprocal relationship
            reciprocal.diplomatic_stance = stance_value
            reciprocal.tension = relationship.tension
            reciprocal.war_state["at_war"] = relationship.war_state["at_war"]
            
            # Add to history
            event = {
                "type": "stance_changed",
                "stance": stance_value,
                "timestamp": datetime.utcnow().isoformat()
            }
            reciprocal.history.append(event)
        else:
            # Create new reciprocal relationship
            reciprocal = FactionRelationship(
                faction_id=other_faction_id,
                other_faction_id=faction_id,
                diplomatic_stance=stance_value,
                tension=relationship.tension,
                treaties=treaties or [],
                war_state={"at_war": relationship.war_state["at_war"], "war_details": {}},
                history=[{
                    "type": "relationship_established",
                    "stance": stance_value,
                    "timestamp": datetime.utcnow().isoformat()
                }],
                metadata=metadata or {}
            )
            db.add(reciprocal)
            
        db.commit()
        db.refresh(relationship)
        return relationship

    @staticmethod
    def get_relationship(
        db: Session,
        faction_id: int,
        other_faction_id: int
    ) -> Optional[FactionRelationship]:
        """
        Get the relationship between two factions.
        
        Args:
            db: Database session
            faction_id: ID of the first faction
            other_faction_id: ID of the second faction
            
        Returns:
            FactionRelationship instance or None if not found
        """
        return db.query(FactionRelationship).filter(
            FactionRelationship.faction_id == faction_id,
            FactionRelationship.other_faction_id == other_faction_id
        ).first()

    @staticmethod
    def get_faction_relationships(
        db: Session,
        faction_id: int,
        stance: Optional[DiplomaticStance] = None,
        at_war: Optional[bool] = None,
        min_tension: Optional[float] = None,
        max_tension: Optional[float] = None
    ) -> List[FactionRelationship]:
        """
        Get all relationships for a faction with optional filters.
        
        Args:
            db: Database session
            faction_id: ID of the faction
            stance: Filter by diplomatic stance (optional)
            at_war: Filter by war status (optional)
            min_tension: Filter by minimum tension value (optional)
            max_tension: Filter by maximum tension value (optional)
            
        Returns:
            List of FactionRelationship instances matching filters
        """
        query = db.query(FactionRelationship).filter(
            FactionRelationship.faction_id == faction_id
        )
        
        if stance:
            stance_value = stance.value if isinstance(stance, DiplomaticStance) else stance
            query = query.filter(FactionRelationship.diplomatic_stance == stance_value)
            
        if at_war is not None:
            # Need to filter JSON column for war state
            if at_war:
                query = query.filter(FactionRelationship.diplomatic_stance == DiplomaticStance.AT_WAR.value)
            else:
                query = query.filter(FactionRelationship.diplomatic_stance != DiplomaticStance.AT_WAR.value)
                
        if min_tension is not None:
            query = query.filter(FactionRelationship.tension >= min_tension)
            
        if max_tension is not None:
            query = query.filter(FactionRelationship.tension <= max_tension)
            
        return query.all()

    @staticmethod
    def update_tension(
        db: Session,
        faction_id: int,
        other_faction_id: int,
        delta: float,
        metadata: Optional[Dict] = None
    ) -> Tuple[FactionRelationship, FactionRelationship]:
        """
        Update the tension between two factions.
        
        Args:
            db: Database session
            faction_id: ID of the first faction
            other_faction_id: ID of the second faction
            delta: Change in tension value
            metadata: Additional metadata for history entry (optional)
            
        Returns:
            Tuple of (relationship, reciprocal_relationship)
            
        Raises:
            FactionNotFoundError: If either faction doesn't exist
        """
        # Get both relationships
        rel = FactionRelationshipService.get_relationship(db, faction_id, other_faction_id)
        recip = FactionRelationshipService.get_relationship(db, other_faction_id, faction_id)
        
        # If either doesn't exist, create them with neutral stance
        if not rel or not recip:
            rel = FactionRelationshipService.set_diplomatic_stance(
                db, faction_id, other_faction_id, DiplomaticStance.NEUTRAL
            )
            recip = FactionRelationshipService.get_relationship(db, other_faction_id, faction_id)
        
        # Update tension
        old_tension = rel.tension
        new_tension = max(-100.0, min(100.0, old_tension + delta))
        rel.tension = new_tension
        recip.tension = new_tension
        
        # Record history
        event = {
            "type": "tension_changed",
            "old_tension": old_tension,
            "new_tension": new_tension,
            "delta": delta,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            event["metadata"] = metadata
            
        rel.history.append(event)
        recip.history.append(event)
        
        # Potentially update diplomatic stance based on tension
        if old_tension < 80.0 and new_tension >= 80.0 and rel.diplomatic_stance != DiplomaticStance.AT_WAR.value:
            # Has reached war threshold
            rel.diplomatic_stance = DiplomaticStance.HOSTILE.value
            recip.diplomatic_stance = DiplomaticStance.HOSTILE.value
            
            stance_event = {
                "type": "stance_changed",
                "old_stance": rel.diplomatic_stance,
                "new_stance": DiplomaticStance.HOSTILE.value,
                "reason": "tension_threshold",
                "timestamp": datetime.utcnow().isoformat()
            }
            rel.history.append(stance_event)
            recip.history.append(stance_event)
        elif old_tension >= 0.0 and new_tension < 0.0:
            # Crossed from positive to negative
            rel.diplomatic_stance = DiplomaticStance.FRIENDLY.value
            recip.diplomatic_stance = DiplomaticStance.FRIENDLY.value
            
            stance_event = {
                "type": "stance_changed",
                "old_stance": rel.diplomatic_stance,
                "new_stance": DiplomaticStance.FRIENDLY.value,
                "reason": "tension_threshold",
                "timestamp": datetime.utcnow().isoformat()
            }
            rel.history.append(stance_event)
            recip.history.append(stance_event)
            
        db.commit()
        db.refresh(rel)
        db.refresh(recip)
        return rel, recip

    @staticmethod
    def declare_war(
        db: Session,
        faction_id: int,
        other_faction_id: int,
        reason: str = "unspecified",
        war_details: Dict = None
    ) -> Tuple[FactionRelationship, FactionRelationship]:
        """
        Declare war between two factions.
        
        Args:
            db: Database session
            faction_id: ID of the first faction (declarer)
            other_faction_id: ID of the second faction (target)
            reason: Reason for war declaration (optional)
            war_details: Additional war details (optional)
            
        Returns:
            Tuple of (relationship, reciprocal_relationship)
        """
        # Get both relationships
        rel = FactionRelationshipService.get_relationship(db, faction_id, other_faction_id)
        recip = FactionRelationshipService.get_relationship(db, other_faction_id, faction_id)
        
        # If either doesn't exist, create them
        if not rel or not recip:
            rel = FactionRelationshipService.set_diplomatic_stance(
                db, faction_id, other_faction_id, DiplomaticStance.NEUTRAL
            )
            recip = FactionRelationshipService.get_relationship(db, other_faction_id, faction_id)
        
        # Update to war state
        rel.diplomatic_stance = DiplomaticStance.AT_WAR.value
        recip.diplomatic_stance = DiplomaticStance.AT_WAR.value
        rel.tension = 100.0
        recip.tension = 100.0
        
        # Update war state
        war_info = {
            "at_war": True,
            "war_details": war_details or {},
            "declared_by": faction_id,
            "declared_at": datetime.utcnow().isoformat(),
            "reason": reason
        }
        rel.war_state = war_info
        recip.war_state = war_info
        
        # Record history
        event = {
            "type": "war_declared",
            "declarer_id": faction_id,
            "target_id": other_faction_id,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if war_details:
            event["war_details"] = war_details
            
        rel.history.append(event)
        recip.history.append(event)
        
        # Update faction state
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        other_faction = db.query(Faction).filter(Faction.id == other_faction_id).first()
        
        if faction and "active_wars" in faction.state:
            if other_faction_id not in faction.state["active_wars"]:
                faction.state["active_wars"].append(other_faction_id)
                
        if other_faction and "active_wars" in other_faction.state:
            if faction_id not in other_faction.state["active_wars"]:
                other_faction.state["active_wars"].append(faction_id)
        
        db.commit()
        db.refresh(rel)
        db.refresh(recip)
        return rel, recip

    @staticmethod
    def make_peace(
        db: Session,
        faction_id: int,
        other_faction_id: int,
        terms: Dict = None,
        new_stance: DiplomaticStance = DiplomaticStance.NEUTRAL
    ) -> Tuple[FactionRelationship, FactionRelationship]:
        """
        End war between two factions.
        
        Args:
            db: Database session
            faction_id: ID of the first faction
            other_faction_id: ID of the second faction
            terms: Peace treaty terms (optional)
            new_stance: New diplomatic stance after peace (default: NEUTRAL)
            
        Returns:
            Tuple of (relationship, reciprocal_relationship)
        """
        # Get both relationships
        rel = FactionRelationshipService.get_relationship(db, faction_id, other_faction_id)
        recip = FactionRelationshipService.get_relationship(db, other_faction_id, faction_id)
        
        if not rel or not recip:
            raise InvalidRelationshipError("Cannot make peace when no relationship exists")
            
        # Verify they are at war
        if rel.diplomatic_stance != DiplomaticStance.AT_WAR.value:
            raise InvalidRelationshipError("Cannot make peace when not at war")
            
        # Update war state
        rel.war_state["at_war"] = False
        recip.war_state["at_war"] = False
        
        if "peace_terms" not in rel.war_state:
            rel.war_state["peace_terms"] = []
        if "peace_terms" not in recip.war_state:
            recip.war_state["peace_terms"] = []
            
        peace_info = {
            "ended_at": datetime.utcnow().isoformat(),
            "terms": terms or {}
        }
        
        rel.war_state["peace_terms"].append(peace_info)
        recip.war_state["peace_terms"].append(peace_info)
        
        # Update diplomatic stance
        new_stance_value = new_stance.value if isinstance(new_stance, DiplomaticStance) else new_stance
        rel.diplomatic_stance = new_stance_value
        recip.diplomatic_stance = new_stance_value
        
        # Update tension based on stance
        tension = 0.0  # Default for NEUTRAL
        if new_stance_value == DiplomaticStance.ALLIED.value:
            tension = -80.0
        elif new_stance_value == DiplomaticStance.FRIENDLY.value:
            tension = -40.0
        elif new_stance_value == DiplomaticStance.UNFRIENDLY.value:
            tension = 40.0
        elif new_stance_value == DiplomaticStance.HOSTILE.value:
            tension = 80.0
            
        rel.tension = tension
        recip.tension = tension
        
        # Record history
        event = {
            "type": "peace_established",
            "new_stance": new_stance_value,
            "terms": terms or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        rel.history.append(event)
        recip.history.append(event)
        
        # Update faction state
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        other_faction = db.query(Faction).filter(Faction.id == other_faction_id).first()
        
        if faction and "active_wars" in faction.state:
            if other_faction_id in faction.state["active_wars"]:
                faction.state["active_wars"].remove(other_faction_id)
                
        if other_faction and "active_wars" in other_faction.state:
            if faction_id in other_faction.state["active_wars"]:
                other_faction.state["active_wars"].remove(faction_id)
        
        db.commit()
        db.refresh(rel)
        db.refresh(recip)
        return rel, recip

    @staticmethod
    def check_for_schism(
        db: Session,
        faction_id: int,
        internal_tension: float = None,
        ideological_divide: Dict = None,
        trigger_event: Dict = None,
        schism_threshold: float = 80.0
    ) -> Dict:
        """
        Check if conditions are right for a faction schism and create a new faction if so.
        
        Args:
            db: Database session
            faction_id: ID of the faction to check for schism
            internal_tension: Explicit internal tension value (optional)
            ideological_divide: Details of ideological division (optional)
            trigger_event: Event that might trigger schism (optional)
            schism_threshold: Tension threshold for schism (default: 80.0)
            
        Returns:
            Dict with schism details or empty dict if no schism occurred
        """
        # Get the faction
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction with ID {faction_id} not found")
            
        # Calculate internal tension if not provided
        if internal_tension is None:
            # Check if faction has internal_tension in state
            if "internal_tension" in faction.state:
                internal_tension = faction.state["internal_tension"]
            else:
                # Default to computing from member loyalty variance
                memberships = db.query(FactionMembership).filter(
                    FactionMembership.faction_id == faction_id,
                    FactionMembership.is_active == True
                ).all()
                
                if not memberships or len(memberships) < 5:
                    # Not enough members for a meaningful schism
                    return {}
                    
                # Calculate tension based on loyalty variance and other factors
                loyalties = [m.reputation for m in memberships]
                loyalty_variance = max(loyalties) - min(loyalties)
                internal_tension = min(100.0, loyalty_variance * 5)  # Scale to 0-100
                
                # Consider ideological factors if provided
                if ideological_divide:
                    if "strength" in ideological_divide:
                        internal_tension += ideological_divide["strength"]
                    
                # Consider trigger event if provided
                if trigger_event and "tension_modifier" in trigger_event:
                    internal_tension += trigger_event["tension_modifier"]
                    
                # Cap at 100
                internal_tension = min(100.0, internal_tension)
                
                # Update faction state
                if "internal_tension" not in faction.state:
                    faction.state["internal_tension"] = 0.0
                faction.state["internal_tension"] = internal_tension
                db.commit()
        
        # Check if threshold for schism is reached
        if internal_tension < schism_threshold:
            return {}
            
        # Determine which members will join the new faction
        # Higher tension means more members are likely to split
        split_probability = (internal_tension - schism_threshold) / (100 - schism_threshold)
        
        # Get members sorted by loyalty (lowest first)
        memberships = db.query(FactionMembership).filter(
            FactionMembership.faction_id == faction_id,
            FactionMembership.is_active == True
        ).all()
        
        memberships.sort(key=lambda m: m.reputation)
        
        # Calculate how many members will split
        # Bias toward lower loyalty members
        rebel_count = 0
        rebel_members = []
        
        # First 20% most likely to rebel
        first_tier = int(len(memberships) * 0.2)
        for i in range(first_tier):
            if i < len(memberships) and random.random() < (0.6 + split_probability * 0.4):
                rebel_members.append(memberships[i])
                rebel_count += 1
                
        # Next 30% somewhat likely to rebel
        second_tier = int(len(memberships) * 0.3)
        for i in range(first_tier, first_tier + second_tier):
            if i < len(memberships) and random.random() < (0.3 + split_probability * 0.4):
                rebel_members.append(memberships[i])
                rebel_count += 1
                
        # Everyone else less likely
        for i in range(first_tier + second_tier, len(memberships)):
            if random.random() < (0.1 + split_probability * 0.2):
                rebel_members.append(memberships[i])
                rebel_count += 1
                
        # If not enough members to form a breakaway faction, no schism
        if rebel_count < 3 or rebel_count < len(memberships) * 0.1:
            return {}
            
        # Create the new breakaway faction
        # Generate a name based on the original and the cause of schism
        name_options = [
            f"Reformed {faction.name}",
            f"True {faction.name}",
            f"Separatist {faction.name}",
            f"{faction.name} Purists",
            f"New {faction.name}",
            f"Breakaway {faction.name}",
            f"Dissident {faction.name}"
        ]
        
        # Use cause if available
        if ideological_divide and "cause" in ideological_divide:
            cause = ideological_divide["cause"]
            name_options.extend([
                f"{cause} {faction.name}",
                f"{faction.name} of {cause}",
                f"{cause} Faction"
            ])
            
        new_name = random.choice(name_options)
        
        # Create a description based on the schism
        description = f"A breakaway faction that split from {faction.name} due to "
        if ideological_divide and "cause" in ideological_divide:
            description += f"ideological differences regarding {ideological_divide['cause']}."
        elif trigger_event and "description" in trigger_event:
            description += f"tensions arising from {trigger_event['description']}."
        else:
            description += "internal tensions and disagreements."
            
        # Create the new faction with similar properties but modified values
        from backend.systems.faction.services.faction_service import FactionService
        
        new_faction = FactionService.create_faction(
            db=db,
            name=new_name,
            description=description,
            faction_type=faction.type,
            alignment=faction.alignment,
            influence=max(10.0, faction.influence * 0.4),  # Start with less influence
            resources=faction.resources.copy() if faction.resources else {},
            territory={},  # No territory initially
            metadata={
                "parent_faction_id": faction_id,
                "schism_date": datetime.utcnow().isoformat(),
                "schism_cause": ideological_divide["cause"] if ideological_divide and "cause" in ideological_divide else "internal_tension",
                "original_member_count": rebel_count
            }
        )
        
        # Transfer members to the new faction
        for membership in rebel_members:
            # Record leaving the old faction
            membership.is_active = False
            membership.status = "defected"
            membership.history.append({
                "type": "defection",
                "to_faction_id": new_faction.id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Create new membership in the breakaway faction
            from backend.systems.faction.services.membership_service import FactionMembershipService
            
            FactionMembershipService.create_membership(
                db=db,
                faction_id=new_faction.id,
                character_id=membership.character_id,
                role="founding_member",
                reputation=min(100, membership.reputation + 30),  # Higher initial loyalty
                metadata={
                    "former_faction_id": faction_id,
                    "former_role": membership.role,
                    "founding_member": True
                }
            )
        
        # Establish initial relationship between factions (usually hostile)
        initial_stance = DiplomaticStance.HOSTILE
        initial_tension = 75.0
        
        # For religious or ideological schisms, might be less hostile
        if ideological_divide and "type" in ideological_divide:
            if ideological_divide["type"] == "religious" or ideological_divide["type"] == "peaceful":
                initial_stance = DiplomaticStance.UNFRIENDLY
                initial_tension = 50.0
                
        # Set up the relationship in both directions
        FactionRelationshipService.set_diplomatic_stance(
            db=db,
            faction_id=faction_id,
            other_faction_id=new_faction.id,
            stance=initial_stance,
            metadata={
                "schism": True,
                "parent_faction": True
            }
        )
        
        FactionRelationshipService.set_diplomatic_stance(
            db=db,
            faction_id=new_faction.id,
            other_faction_id=faction_id,
            stance=initial_stance,
            metadata={
                "schism": True,
                "breakaway_faction": True
            }
        )
        
        # Update tensions
        FactionRelationshipService.update_tension(
            db=db,
            faction_id=faction_id,
            other_faction_id=new_faction.id,
            delta=initial_tension
        )
        
        # Update the original faction's state
        if "schisms" not in faction.state:
            faction.state["schisms"] = []
            
        faction.state["schisms"].append({
            "date": datetime.utcnow().isoformat(),
            "new_faction_id": new_faction.id,
            "members_lost": rebel_count,
            "cause": ideological_divide["cause"] if ideological_divide and "cause" in ideological_divide else "internal_tension"
        })
        
        # Reset internal tension after schism
        faction.state["internal_tension"] = max(0, internal_tension - 50)
        
        # Update influence to reflect loss of members
        faction.influence = max(10, faction.influence * (1 - (rebel_count / len(memberships)) * 0.5))
        
        db.commit()
        
        # Return schism details
        return {
            "original_faction_id": faction_id,
            "new_faction_id": new_faction.id,
            "members_transferred": rebel_count,
            "internal_tension_before": internal_tension,
            "new_tension": faction.state["internal_tension"],
            "initial_stance": initial_stance.value,
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def resolve_war_outcome(
        db: Session, 
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
        changes. This method handles those consequences.
        
        Args:
            db: Database session
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
        # Verify that the factions are at war
        rel = FactionRelationshipService.get_relationship(db, faction_id, other_faction_id)
        recip = FactionRelationshipService.get_relationship(db, other_faction_id, faction_id)
        
        if not rel or not recip:
            raise InvalidRelationshipError("Relationship does not exist between the factions")
            
        if rel.diplomatic_stance != DiplomaticStance.AT_WAR.value or not rel.war_state.get("at_war", False):
            raise InvalidRelationshipError("Cannot resolve war when factions are not at war")
            
        # Get faction details
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        other_faction = db.query(Faction).filter(Faction.id == other_faction_id).first()
        
        if not faction or not other_faction:
            raise InvalidRelationshipError("One or both factions do not exist")
            
        # Process outcome type
        post_war_stance = DiplomaticStance.NEUTRAL  # Default stance after war
        applied_consequences = []
        
        # Determine victor if not provided but outcome requires it
        if outcome_type in ["victory", "defeat"] and not victor_id:
            raise ValueError("victor_id must be provided for victory/defeat outcomes")
            
        if outcome_type == "victory" and victor_id not in [faction_id, other_faction_id]:
            raise ValueError("victor_id must be one of the factions involved in the war")
            
        # Process specific outcome types
        if outcome_type == "victory" or outcome_type == "defeat":
            # Ensure victor_id is correct
            if outcome_type == "victory":
                victor_id = faction_id
                loser_id = other_faction_id
            else:  # defeat
                victor_id = other_faction_id
                loser_id = faction_id
                
            victor = db.query(Faction).filter(Faction.id == victor_id).first()
            loser = db.query(Faction).filter(Faction.id == loser_id).first()
            
            # Set post-war stance based on victory/defeat
            post_war_stance = DiplomaticStance.UNFRIENDLY
            
            # Apply mechanical consequences if enabled
            if mechanical_consequences:
                # 1. Resource transfer
                resource_transfer_pct = terms.get("resource_transfer_pct", 20) if terms else 20
                if "resources" in loser.resources and "gold" in loser.resources:
                    gold_to_transfer = int(loser.resources["gold"] * (resource_transfer_pct / 100.0))
                    
                    # Transfer
                    loser.resources["gold"] -= gold_to_transfer
                    victor.resources.setdefault("gold", 0)
                    victor.resources["gold"] += gold_to_transfer
                    
                    applied_consequences.append({
                        "type": "resource_transfer",
                        "resource": "gold",
                        "amount": gold_to_transfer,
                        "from_faction_id": loser_id,
                        "to_faction_id": victor_id
                    })
                    
                # 2. Territory changes
                if terms and "territories" in terms:
                    for territory_id in terms["territories"]:
                        # Here we would transfer territory control
                        # This is a placeholder - actual implementation would
                        # interact with the territory/region system
                        applied_consequences.append({
                            "type": "territory_transfer",
                            "territory_id": territory_id,
                            "from_faction_id": loser_id,
                            "to_faction_id": victor_id
                        })
                        
                # 3. Population shifts
                population_shift_pct = terms.get("population_shift_pct", 10) if terms else 10
                
                # This is a placeholder - actual implementation would
                # interact with the population system
                applied_consequences.append({
                    "type": "population_shift",
                    "percentage": population_shift_pct,
                    "from_faction_id": loser_id,
                    "to_faction_id": victor_id
                })
                
                # 4. Influence changes
                victor.influence = min(100, victor.influence + 10)
                loser.influence = max(10, loser.influence - 15)
                
                applied_consequences.append({
                    "type": "influence_change",
                    "victor_change": "+10",
                    "loser_change": "-15"
                })
                
        elif outcome_type == "negotiated":
            # For negotiated outcomes, the terms determine consequences
            post_war_stance = DiplomaticStance.NEUTRAL
            
            if mechanical_consequences and terms:
                # Apply any resource transfers in the terms
                if "resource_transfers" in terms:
                    for transfer in terms["resource_transfers"]:
                        from_id = transfer.get("from_faction_id")
                        to_id = transfer.get("to_faction_id")
                        resource = transfer.get("resource")
                        amount = transfer.get("amount")
                        
                        if all([from_id, to_id, resource, amount]):
                            from_faction = db.query(Faction).filter(Faction.id == from_id).first()
                            to_faction = db.query(Faction).filter(Faction.id == to_id).first()
                            
                            if from_faction and to_faction:
                                from_faction.resources.setdefault(resource, 0)
                                to_faction.resources.setdefault(resource, 0)
                                
                                # Transfer amount without going below 0
                                actual_amount = min(from_faction.resources[resource], amount)
                                from_faction.resources[resource] -= actual_amount
                                to_faction.resources[resource] += actual_amount
                                
                                applied_consequences.append({
                                    "type": "resource_transfer",
                                    "resource": resource,
                                    "amount": actual_amount,
                                    "from_faction_id": from_id,
                                    "to_faction_id": to_id
                                })
                
                # Apply territory transfers in the terms
                if "territory_transfers" in terms:
                    for transfer in terms["territory_transfers"]:
                        territory_id = transfer.get("territory_id")
                        from_id = transfer.get("from_faction_id")
                        to_id = transfer.get("to_faction_id")
                        
                        if all([territory_id, from_id, to_id]):
                            # Placeholder for territory transfer logic
                            applied_consequences.append({
                                "type": "territory_transfer",
                                "territory_id": territory_id,
                                "from_faction_id": from_id,
                                "to_faction_id": to_id
                            })
                
                # Apply any other consequences defined in terms
                if "other_consequences" in terms:
                    for consequence in terms["other_consequences"]:
                        applied_consequences.append(consequence)
                        
        elif outcome_type == "stalemate":
            # For stalemates, minimal consequences
            post_war_stance = DiplomaticStance.UNFRIENDLY
            
            if mechanical_consequences:
                # Both sides lose some resources due to war attrition
                for side_id in [faction_id, other_faction_id]:
                    side = db.query(Faction).filter(Faction.id == side_id).first()
                    if side and "resources" in side.resources and "gold" in side.resources:
                        attrition = int(side.resources["gold"] * 0.1)  # 10% attrition
                        side.resources["gold"] -= attrition
                        
                        applied_consequences.append({
                            "type": "war_attrition",
                            "faction_id": side_id,
                            "resource": "gold",
                            "amount": attrition
                        })
                        
                    # Small influence decrease for both sides
                    side.influence = max(10, side.influence - 5)
                    
                    applied_consequences.append({
                        "type": "influence_change",
                        "faction_id": side_id,
                        "change": "-5"
                    })
        
        # End the war using the make_peace method
        rel_result, recip_result = FactionRelationshipService.make_peace(
            db=db,
            faction_id=faction_id,
            other_faction_id=other_faction_id,
            terms=terms,
            new_stance=post_war_stance
        )
        
        # Record the outcome details in the war history
        outcome_details = {
            "outcome_type": outcome_type,
            "resolved_at": datetime.utcnow().isoformat(),
            "victor_id": victor_id if outcome_type in ["victory", "defeat"] else None,
            "terms": terms or {},
            "consequences": applied_consequences
        }
        
        # Add to relationship war history
        if "outcomes" not in rel.war_state:
            rel.war_state["outcomes"] = []
        if "outcomes" not in recip.war_state:
            recip.war_state["outcomes"] = []
            
        rel.war_state["outcomes"].append(outcome_details)
        recip.war_state["outcomes"].append(outcome_details)
        
        # Add to faction state
        for f_id in [faction_id, other_faction_id]:
            faction = db.query(Faction).filter(Faction.id == f_id).first()
            if faction:
                if "war_history" not in faction.state:
                    faction.state["war_history"] = []
                    
                faction.state["war_history"].append({
                    "against_faction_id": faction_id if f_id == other_faction_id else other_faction_id,
                    "outcome_type": outcome_type,
                    "victor_id": victor_id if outcome_type in ["victory", "defeat"] else None,
                    "resolved_at": datetime.utcnow().isoformat()
                })
        
        # Commit changes
        db.commit()
        
        # Return outcome details and applied consequences
        return {
            "outcome_type": outcome_type,
            "faction_id": faction_id,
            "other_faction_id": other_faction_id,
            "victor_id": victor_id if outcome_type in ["victory", "defeat"] else None,
            "post_war_stance": post_war_stance.value,
            "applied_consequences": applied_consequences,
            "terms": terms or {}
        } 