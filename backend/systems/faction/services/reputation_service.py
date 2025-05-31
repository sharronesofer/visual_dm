"""
Reputation service for factions in the Visual DM system.

This module handles the reputation system for factions, including region-specific, 
character-specific, and global reputation tracking and modification.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session

from backend.systems.faction.models.faction import Faction, FactionMembership
from backend.systems.faction.services.faction_service import FactionNotFoundError

class FactionReputationService:
    """Service for managing faction reputation systems."""
    
    @staticmethod
    def modify_global_reputation(
        db: Session,
        faction_id: int,
        amount: float,
        reason: str,
        source: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Modify a faction's global reputation score.
        
        Args:
            db: Database session
            faction_id: Faction ID
            amount: Amount to modify reputation by (positive or negative)
            reason: Reason for reputation change
            source: Optional data about the source of the reputation change
            
        Returns:
            Dict with details of the reputation change
            
        Raises:
            FactionNotFoundError: If faction not found
        """
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction with ID {faction_id} not found")
            
        # Store previous reputation for reporting
        previous_reputation = faction.reputation
        
        # Update reputation
        faction.reputation += amount
        
        # Cap reputation between -100 and 100
        faction.reputation = max(-100.0, min(100.0, faction.reputation))
        
        # Record reputation change in history
        if "reputation_history" not in faction.state:
            faction.state["reputation_history"] = []
            
        reputation_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "previous_reputation": previous_reputation,
            "new_reputation": faction.reputation,
            "change": amount,
            "reason": reason,
            "source": source or {}
        }
        
        faction.state["reputation_history"].append(reputation_event)
        
        # Record reputation bracket changes for significant shifts
        if "reputation_brackets" not in faction.state:
            faction.state["reputation_brackets"] = {
                "current": get_reputation_bracket(faction.reputation),
                "history": []
            }
        
        previous_bracket = faction.state["reputation_brackets"]["current"]
        current_bracket = get_reputation_bracket(faction.reputation)
        
        if previous_bracket != current_bracket:
            faction.state["reputation_brackets"]["current"] = current_bracket
            faction.state["reputation_brackets"]["history"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "from_bracket": previous_bracket,
                "to_bracket": current_bracket,
                "reason": reason
            })
        
        # Commit changes
        db.commit()
        
        # Return details of the change
        return {
            "faction_id": faction_id,
            "previous_reputation": previous_reputation,
            "new_reputation": faction.reputation,
            "change": amount,
            "previous_bracket": previous_bracket,
            "current_bracket": current_bracket,
            "bracket_changed": previous_bracket != current_bracket,
            "reason": reason
        }
    
    @staticmethod
    def modify_regional_reputation(
        db: Session,
        faction_id: int,
        region_id: int,
        amount: float,
        reason: str,
        source: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Modify a faction's reputation in a specific region.
        
        Args:
            db: Database session
            faction_id: Faction ID
            region_id: Region ID
            amount: Amount to modify reputation by (positive or negative)
            reason: Reason for reputation change
            source: Optional data about the source of the reputation change
            
        Returns:
            Dict with details of the reputation change
            
        Raises:
            FactionNotFoundError: If faction not found
        """
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction with ID {faction_id} not found")
            
        # Initialize regional reputations if not present
        if "regional_reputations" not in faction.state:
            faction.state["regional_reputations"] = {}
            
        region_id_str = str(region_id)
        
        # Initialize this region's reputation if not present
        if region_id_str not in faction.state["regional_reputations"]:
            faction.state["regional_reputations"][region_id_str] = 0.0
            
        # Store previous reputation for reporting
        previous_reputation = faction.state["regional_reputations"][region_id_str]
        
        # Update reputation
        faction.state["regional_reputations"][region_id_str] += amount
        
        # Cap reputation between -100 and 100
        faction.state["regional_reputations"][region_id_str] = max(
            -100.0, 
            min(100.0, faction.state["regional_reputations"][region_id_str])
        )
        
        current_reputation = faction.state["regional_reputations"][region_id_str]
        
        # Record regional reputation change in history
        if "regional_reputation_history" not in faction.state:
            faction.state["regional_reputation_history"] = {}
            
        if region_id_str not in faction.state["regional_reputation_history"]:
            faction.state["regional_reputation_history"][region_id_str] = []
            
        reputation_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "previous_reputation": previous_reputation,
            "new_reputation": current_reputation,
            "change": amount,
            "reason": reason,
            "source": source or {}
        }
        
        faction.state["regional_reputation_history"][region_id_str].append(reputation_event)
        
        # Update global reputation with a small effect
        # Regional reputation changes influence global reputation at a reduced rate
        global_amount = amount * 0.2  # 20% influence on global reputation
        
        if abs(global_amount) >= 0.1:  # Only update if the change is significant
            global_reason = f"Regional reputation change in region {region_id}"
            global_source = {
                "type": "regional_influence",
                "region_id": region_id,
                "original_reason": reason,
                "original_amount": amount
            }
            
            FactionReputationService.modify_global_reputation(
                db=db,
                faction_id=faction_id,
                amount=global_amount,
                reason=global_reason,
                source=global_source
            )
        else:
            # Commit changes if we didn't call the global method (which would commit)
            db.commit()
        
        # Record if this is now the most positive or negative regional reputation
        current_extremes = faction.state.get("regional_reputation_extremes", {
            "most_positive": {"region_id": None, "value": -100.0},
            "most_negative": {"region_id": None, "value": 100.0}
        })
        
        if current_reputation > current_extremes["most_positive"]["value"]:
            current_extremes["most_positive"] = {
                "region_id": region_id,
                "value": current_reputation
            }
            
        if current_reputation < current_extremes["most_negative"]["value"]:
            current_extremes["most_negative"] = {
                "region_id": region_id,
                "value": current_reputation
            }
            
        faction.state["regional_reputation_extremes"] = current_extremes
        
        # Get reputation brackets
        previous_bracket = get_reputation_bracket(previous_reputation)
        current_bracket = get_reputation_bracket(current_reputation)
        
        # Return details of the change
        return {
            "faction_id": faction_id,
            "region_id": region_id,
            "previous_reputation": previous_reputation,
            "new_reputation": current_reputation,
            "change": amount,
            "previous_bracket": previous_bracket,
            "current_bracket": current_bracket,
            "bracket_changed": previous_bracket != current_bracket,
            "reason": reason
        }
    
    @staticmethod
    def modify_character_reputation(
        db: Session,
        faction_id: int,
        character_id: int,
        amount: float,
        reason: str,
        source: Optional[Dict[str, Any]] = None,
        affect_membership: bool = True
    ) -> Dict[str, Any]:
        """
        Modify a faction's reputation with a specific character.
        
        This differs from membership reputation, which is about a character's standing
        within a faction. This tracks how a faction views a character.
        
        Args:
            db: Database session
            faction_id: Faction ID
            character_id: Character ID
            amount: Amount to modify reputation by (positive or negative)
            reason: Reason for reputation change
            source: Optional data about the source of the reputation change
            affect_membership: Whether to also affect membership reputation if applicable
            
        Returns:
            Dict with details of the reputation change
            
        Raises:
            FactionNotFoundError: If faction not found
        """
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction with ID {faction_id} not found")
            
        # Initialize character reputations if not present
        if "character_reputations" not in faction.state:
            faction.state["character_reputations"] = {}
            
        character_id_str = str(character_id)
        
        # Initialize this character's reputation if not present
        if character_id_str not in faction.state["character_reputations"]:
            faction.state["character_reputations"][character_id_str] = 0.0
            
        # Store previous reputation for reporting
        previous_reputation = faction.state["character_reputations"][character_id_str]
        
        # Update reputation
        faction.state["character_reputations"][character_id_str] += amount
        
        # Cap reputation between -100 and 100
        faction.state["character_reputations"][character_id_str] = max(
            -100.0, 
            min(100.0, faction.state["character_reputations"][character_id_str])
        )
        
        current_reputation = faction.state["character_reputations"][character_id_str]
        
        # Record character reputation change in history
        if "character_reputation_history" not in faction.state:
            faction.state["character_reputation_history"] = {}
            
        if character_id_str not in faction.state["character_reputation_history"]:
            faction.state["character_reputation_history"][character_id_str] = []
            
        reputation_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "previous_reputation": previous_reputation,
            "new_reputation": current_reputation,
            "change": amount,
            "reason": reason,
            "source": source or {}
        }
        
        faction.state["character_reputation_history"][character_id_str].append(reputation_event)
        
        # If the character is a member, also update their membership reputation
        if affect_membership:
            membership = db.query(FactionMembership).filter(
                FactionMembership.faction_id == faction_id,
                FactionMembership.character_id == character_id,
                FactionMembership.is_active == True
            ).first()
            
            if membership:
                # Update membership reputation (at a reduced rate)
                membership_amount = amount * 0.5  # 50% influence on membership reputation
                previous_member_rep = membership.reputation
                
                # Update and cap
                membership.reputation += membership_amount
                membership.reputation = max(-100.0, min(100.0, membership.reputation))
                
                # Record in membership history
                if not membership.history:
                    membership.history = []
                    
                membership.history.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "reputation_change",
                    "previous_reputation": previous_member_rep,
                    "new_reputation": membership.reputation,
                    "change": membership_amount,
                    "reason": reason,
                    "source": "faction_perception_change"
                })
        
        # Commit changes
        db.commit()
        
        # Get reputation brackets
        previous_bracket = get_reputation_bracket(previous_reputation)
        current_bracket = get_reputation_bracket(current_reputation)
        
        # Return details of the change
        return {
            "faction_id": faction_id,
            "character_id": character_id,
            "previous_reputation": previous_reputation,
            "new_reputation": current_reputation,
            "change": amount,
            "previous_bracket": previous_bracket,
            "current_bracket": current_bracket,
            "bracket_changed": previous_bracket != current_bracket,
            "reason": reason,
            "membership_updated": affect_membership and membership is not None
        }
    
    @staticmethod
    def get_regional_reputation_summary(
        db: Session,
        faction_id: int
    ) -> Dict[str, Any]:
        """
        Get a summary of a faction's regional reputations.
        
        Args:
            db: Database session
            faction_id: Faction ID
            
        Returns:
            Dict with regional reputation summary
            
        Raises:
            FactionNotFoundError: If faction not found
        """
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction with ID {faction_id} not found")
            
        regional_reputations = faction.state.get("regional_reputations", {})
        
        # Generate statistics
        regions_count = len(regional_reputations)
        
        # Calculate averages and extremes
        if regions_count > 0:
            values = list(regional_reputations.values())
            avg_reputation = sum(values) / regions_count
            most_positive = max(values)
            most_negative = min(values)
            
            # Find the regions with extreme values
            most_positive_region = next(
                (region_id for region_id, rep in regional_reputations.items() 
                 if rep == most_positive),
                None
            )
            most_negative_region = next(
                (region_id for region_id, rep in regional_reputations.items() 
                 if rep == most_negative),
                None
            )
            
            # Group by brackets
            bracket_counts = {
                "revered": 0,
                "respected": 0,
                "friendly": 0,
                "neutral": 0,
                "unfriendly": 0,
                "hostile": 0,
                "reviled": 0
            }
            
            for rep in values:
                bracket = get_reputation_bracket(rep)
                bracket_counts[bracket] += 1
        else:
            avg_reputation = 0
            most_positive = 0
            most_negative = 0
            most_positive_region = None
            most_negative_region = None
            bracket_counts = {
                "revered": 0,
                "respected": 0,
                "friendly": 0,
                "neutral": 0,
                "unfriendly": 0,
                "hostile": 0,
                "reviled": 0
            }
        
        return {
            "faction_id": faction_id,
            "global_reputation": faction.reputation,
            "global_bracket": get_reputation_bracket(faction.reputation),
            "regional_count": regions_count,
            "average_regional_reputation": avg_reputation,
            "most_positive": {
                "region_id": most_positive_region,
                "value": most_positive,
                "bracket": get_reputation_bracket(most_positive)
            },
            "most_negative": {
                "region_id": most_negative_region,
                "value": most_negative,
                "bracket": get_reputation_bracket(most_negative)
            },
            "bracket_distribution": bracket_counts,
            "regional_extremes": faction.state.get("regional_reputation_extremes", {
                "most_positive": {"region_id": None, "value": -100.0},
                "most_negative": {"region_id": None, "value": 100.0}
            })
        }
    
    @staticmethod
    def calculate_faction_reputation_modifiers(
        db: Session,
        faction_id: int
    ) -> Dict[str, float]:
        """
        Calculate faction-wide modifiers based on reputation.
        
        These modifiers can be used for mechanical effects in gameplay.
        
        Args:
            db: Database session
            faction_id: Faction ID
            
        Returns:
            Dict of modifier name to float value
            
        Raises:
            FactionNotFoundError: If faction not found
        """
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction with ID {faction_id} not found")
            
        # Base modifiers
        modifiers = {
            "trade_price": 1.0,  # Multiplier for trade prices
            "quest_reward": 1.0,  # Multiplier for quest rewards
            "recruiting_cost": 1.0,  # Cost to recruit from this faction
            "diplomatic_leverage": 1.0,  # Modifier for diplomatic actions
            "information_access": 1.0,  # Access to faction information
            "favor_cost": 1.0,  # Cost to request favors from faction
        }
        
        # Apply reputation-based modifiers
        reputation = faction.reputation
        bracket = get_reputation_bracket(reputation)
        
        # Calculate normalized value from -1.0 to 1.0 for easier calculations
        normalized_rep = reputation / 100.0
        
        # Apply specific modifiers
        modifiers["trade_price"] = max(0.5, 1.0 - (normalized_rep * 0.25))
        modifiers["quest_reward"] = min(1.5, 1.0 + (normalized_rep * 0.25))
        modifiers["recruiting_cost"] = max(0.5, 1.0 - (normalized_rep * 0.25))
        modifiers["diplomatic_leverage"] = min(2.0, 1.0 + (normalized_rep * 0.5))
        modifiers["information_access"] = min(2.0, 1.0 + (normalized_rep * 0.5))
        modifiers["favor_cost"] = max(0.5, 1.0 - (normalized_rep * 0.25))
        
        # Additional bracket-specific bonuses
        if bracket == "revered":
            modifiers["trade_price"] -= 0.1
            modifiers["quest_reward"] += 0.2
            modifiers["recruiting_cost"] -= 0.2
            modifiers["diplomatic_leverage"] += 0.3
            modifiers["information_access"] += 0.3
            modifiers["favor_cost"] -= 0.2
        elif bracket == "respected":
            modifiers["trade_price"] -= 0.05
            modifiers["quest_reward"] += 0.1
            modifiers["diplomatic_leverage"] += 0.1
        elif bracket == "hostile":
            modifiers["trade_price"] += 0.2
            modifiers["quest_reward"] -= 0.2
            modifiers["recruiting_cost"] += 0.3
        elif bracket == "reviled":
            modifiers["trade_price"] += 0.5
            modifiers["quest_reward"] -= 0.5
            modifiers["recruiting_cost"] += 0.5
            modifiers["diplomatic_leverage"] -= 0.5
            modifiers["information_access"] -= 0.5
            modifiers["favor_cost"] += 0.5
        
        # Ensure bounds
        for key, value in modifiers.items():
            if key == "diplomatic_leverage" or key == "information_access":
                modifiers[key] = max(0.1, min(3.0, value))
            else:
                modifiers[key] = max(0.1, min(2.0, value))
                
        return modifiers

def get_reputation_bracket(reputation: float) -> str:
    """
    Get a string representation of a reputation bracket.
    
    Args:
        reputation: Reputation value (-100 to +100)
        
    Returns:
        String bracket name
    """
    if reputation >= 90:
        return "revered"
    elif reputation >= 70:
        return "respected"
    elif reputation >= 30:
        return "friendly"
    elif reputation >= -30:
        return "neutral"
    elif reputation >= -70:
        return "unfriendly"
    elif reputation >= -90:
        return "hostile"
    else:
        return "reviled" 