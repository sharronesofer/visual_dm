"""
Reputation service for factions in the Visual DM system.

This module handles the reputation system for factions, including region-specific, 
character-specific, and global reputation tracking and modification.

Pure business logic implementation.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from backend.infrastructure.faction_services import ReputationDatabaseService
from backend.infrastructure.shared.exceptions import (
    FactionNotFoundError,
    ValidationError
)


def get_reputation_bracket(reputation: float) -> str:
    """
    Determine reputation bracket based on numerical score - pure function.
    
    Args:
        reputation: Numerical reputation score (-100 to 100)
        
    Returns:
        String representation of reputation bracket
    """
    if reputation >= 80:
        return "heroic"
    elif reputation >= 60:
        return "respected"
    elif reputation >= 40:
        return "trusted"
    elif reputation >= 20:
        return "neutral_positive"
    elif reputation >= -20:
        return "neutral"
    elif reputation >= -40:
        return "mistrusted"
    elif reputation >= -60:
        return "disliked"
    elif reputation >= -80:
        return "despised"
    else:
        return "reviled"


class FactionReputationService:
    """Service for managing faction reputation systems - pure business logic."""
    
    def __init__(self, database_service: ReputationDatabaseService):
        self.db_service = database_service

    def modify_global_reputation(
        self,
        faction_id: int,
        amount: float,
        reason: str,
        source: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Modify a faction's global reputation score with business rules.
        
        Args:
            faction_id: Faction ID
            amount: Amount to modify reputation by (positive or negative)
            reason: Reason for reputation change
            source: Optional data about the source of the reputation change
            
        Returns:
            Dict with details of the reputation change
            
        Raises:
            FactionNotFoundError: If faction not found
            ValidationError: If amount is invalid
        """
        # Business rules validation
        if not reason or not reason.strip():
            raise ValidationError("Reason for reputation change is required")
        
        if abs(amount) > 50:  # Business rule: prevent extreme single changes
            raise ValidationError("Single reputation change cannot exceed 50 points")
        
        faction = self.db_service.get_faction_for_reputation(faction_id)
        if not faction:
            raise FactionNotFoundError(f"Faction with ID {faction_id} not found")
            
        # Store previous reputation for business logic
        previous_reputation = faction.reputation
        
        # Apply business rules for reputation calculation
        new_reputation = self._calculate_new_reputation(previous_reputation, amount)
        faction.reputation = new_reputation
        
        # Business logic for reputation history tracking
        reputation_event = self._create_reputation_event(
            previous_reputation, new_reputation, amount, reason, source
        )
        
        # Update reputation history using business rules
        self._update_reputation_history(faction, reputation_event)
        
        # Business logic for reputation bracket tracking
        previous_bracket = get_reputation_bracket(previous_reputation)
        current_bracket = get_reputation_bracket(new_reputation)
        bracket_changed = self._update_reputation_brackets(
            faction, previous_bracket, current_bracket, reason
        )
        
        # Persist changes via database service
        self.db_service.update_faction_reputation(faction)
        
        # Return business logic results
        return {
            "faction_id": faction_id,
            "previous_reputation": previous_reputation,
            "new_reputation": new_reputation,
            "change": amount,
            "previous_bracket": previous_bracket,
            "current_bracket": current_bracket,
            "bracket_changed": bracket_changed,
            "reason": reason
        }
    
    def modify_regional_reputation(
        self,
        faction_id: int,
        region_id: int,
        amount: float,
        reason: str,
        source: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Modify a faction's reputation in a specific region with business rules.
        
        Args:
            faction_id: Faction ID
            region_id: Region ID
            amount: Amount to modify reputation by (positive or negative)
            reason: Reason for reputation change
            source: Optional data about the source of the reputation change
            
        Returns:
            Dict with details of the reputation change
            
        Raises:
            FactionNotFoundError: If faction not found
            ValidationError: If parameters are invalid
        """
        # Business rules validation
        if not reason or not reason.strip():
            raise ValidationError("Reason for reputation change is required")
        
        if region_id <= 0:
            raise ValidationError("Region ID must be positive")
        
        if abs(amount) > 50:
            raise ValidationError("Single reputation change cannot exceed 50 points")
        
        faction = self.db_service.get_faction_for_reputation(faction_id)
        if not faction:
            raise FactionNotFoundError(f"Faction with ID {faction_id} not found")
            
        # Business logic for regional reputation management
        regional_reps = self._ensure_regional_reputations(faction)
        region_id_str = str(region_id)
        
        # Initialize region if not present (business rule)
        if region_id_str not in regional_reps:
            regional_reps[region_id_str] = 0.0
        
        # Apply business rules for regional reputation
        previous_reputation = regional_reps[region_id_str]
        new_reputation = self._calculate_new_reputation(previous_reputation, amount)
        regional_reps[region_id_str] = new_reputation
        
        # Business logic for regional history tracking
        reputation_event = self._create_reputation_event(
            previous_reputation, new_reputation, amount, reason, source
        )
        
        self._update_regional_reputation_history(faction, region_id_str, reputation_event)
        
        # Business rule: Regional changes influence global reputation
        global_influence = self._calculate_global_influence(amount)
        if abs(global_influence) >= 0.1:  # Business threshold
            global_reason = f"Regional reputation change in region {region_id}"
            global_source = {
                "type": "regional_influence",
                "region_id": region_id,
                "original_reason": reason,
                "original_amount": amount
            }
            
            # Recursive call for global reputation (business rule)
            self.modify_global_reputation(
                faction_id=faction_id,
                amount=global_influence,
                reason=global_reason,
                source=global_source
            )
        else:
            # Persist changes if no global update
            self.db_service.update_faction_reputation(faction)
        
        return {
            "faction_id": faction_id,
            "region_id": region_id,
            "previous_reputation": previous_reputation,
            "new_reputation": new_reputation,
            "change": amount,
            "global_influence": global_influence,
            "reason": reason
        }

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
        Modify faction reputation with specific character with business rules.
        
        Args:
            faction_id: Faction ID
            character_id: Character ID
            amount: Amount to modify reputation by
            reason: Reason for reputation change
            source: Optional source information
            affect_membership: Whether to affect membership status
            
        Returns:
            Dict with reputation change details
        """
        # Business rules validation
        if not reason or not reason.strip():
            raise ValidationError("Reason for reputation change is required")
        
        if character_id <= 0:
            raise ValidationError("Character ID must be positive")
        
        if abs(amount) > 30:  # Business rule: character interactions are more limited
            raise ValidationError("Character reputation change cannot exceed 30 points")
        
        faction = self.db_service.get_faction_for_reputation(faction_id)
        if not faction:
            raise FactionNotFoundError(f"Faction with ID {faction_id} not found")
        
        # Business logic for character-specific reputation
        char_reps = self._ensure_character_reputations(faction)
        character_id_str = str(character_id)
        
        if character_id_str not in char_reps:
            char_reps[character_id_str] = 0.0
        
        previous_reputation = char_reps[character_id_str]
        new_reputation = self._calculate_new_reputation(previous_reputation, amount)
        char_reps[character_id_str] = new_reputation
        
        # Business logic for character reputation history
        reputation_event = self._create_reputation_event(
            previous_reputation, new_reputation, amount, reason, source
        )
        
        self._update_character_reputation_history(faction, character_id_str, reputation_event)
        
        # Business rule: Character reputation affects membership
        membership_effects = {}
        if affect_membership:
            membership_effects = self._apply_character_reputation_to_membership(
                faction_id, character_id, new_reputation
            )
        
        # Business rule: Character interactions have smaller global influence
        global_influence = self._calculate_global_influence(amount) * 0.3  # 30% influence
        if abs(global_influence) >= 0.05:
            global_reason = f"Character {character_id} reputation change"
            global_source = {
                "type": "character_influence",
                "character_id": character_id,
                "original_reason": reason,
                "original_amount": amount
            }
            
            self.modify_global_reputation(
                faction_id=faction_id,
                amount=global_influence,
                reason=global_reason,
                source=global_source
            )
        else:
            self.db_service.update_faction_reputation(faction)
        
        return {
            "faction_id": faction_id,
            "character_id": character_id,
            "previous_reputation": previous_reputation,
            "new_reputation": new_reputation,
            "change": amount,
            "membership_effects": membership_effects,
            "global_influence": global_influence,
            "reason": reason
        }

    def get_regional_reputation_summary(self, faction_id: int) -> Dict[str, Any]:
        """
        Get comprehensive regional reputation summary with business insights.
        
        Args:
            faction_id: Faction ID
            
        Returns:
            Dict with regional reputation analysis
        """
        faction = self.db_service.get_faction_for_reputation(faction_id)
        if not faction:
            raise FactionNotFoundError(f"Faction with ID {faction_id} not found")
        
        regional_reps = self._ensure_regional_reputations(faction)
        
        # Business logic for reputation analysis
        if not regional_reps:
            return {
                "faction_id": faction_id,
                "total_regions": 0,
                "average_reputation": faction.reputation,
                "reputation_range": 0,
                "strongest_region": None,
                "weakest_region": None
            }
        
        reputations = list(regional_reps.values())
        strongest_region = max(regional_reps.items(), key=lambda x: x[1])
        weakest_region = min(regional_reps.items(), key=lambda x: x[1])
        
        return {
            "faction_id": faction_id,
            "total_regions": len(regional_reps),
            "average_reputation": sum(reputations) / len(reputations),
            "reputation_range": max(reputations) - min(reputations),
            "strongest_region": {
                "region_id": int(strongest_region[0]),
                "reputation": strongest_region[1],
                "bracket": get_reputation_bracket(strongest_region[1])
            },
            "weakest_region": {
                "region_id": int(weakest_region[0]),
                "reputation": weakest_region[1],
                "bracket": get_reputation_bracket(weakest_region[1])
            },
            "regional_details": {
                int(region_id): {
                    "reputation": rep,
                    "bracket": get_reputation_bracket(rep)
                }
                for region_id, rep in regional_reps.items()
            }
        }

    def calculate_faction_reputation_modifiers(self, faction_id: int) -> Dict[str, float]:
        """
        Calculate reputation-based modifiers for faction interactions.
        
        Args:
            faction_id: Faction ID
            
        Returns:
            Dict with calculated modifiers based on reputation
        """
        faction = self.db_service.get_faction_for_reputation(faction_id)
        if not faction:
            raise FactionNotFoundError(f"Faction with ID {faction_id} not found")
        
        global_rep = faction.reputation
        
        # Business rules for reputation modifiers
        modifiers = {
            "diplomacy_bonus": self._calculate_diplomacy_modifier(global_rep),
            "trade_bonus": self._calculate_trade_modifier(global_rep),
            "recruitment_bonus": self._calculate_recruitment_modifier(global_rep),
            "territory_defense_bonus": self._calculate_defense_modifier(global_rep),
            "information_gathering_bonus": self._calculate_info_modifier(global_rep)
        }
        
        return modifiers

    # Private business logic methods
    
    def _calculate_new_reputation(self, current: float, change: float) -> float:
        """Apply business rules for reputation calculation"""
        new_value = current + change
        return max(-100.0, min(100.0, new_value))  # Cap between -100 and 100
    
    def _calculate_global_influence(self, regional_amount: float) -> float:
        """Business rule: Regional changes influence global at 20% rate"""
        return regional_amount * 0.2
    
    def _create_reputation_event(self, previous: float, new: float, 
                               change: float, reason: str, 
                               source: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create reputation event record with business data"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "previous_reputation": previous,
            "new_reputation": new,
            "change": change,
            "reason": reason,
            "source": source or {}
        }
    
    def _ensure_regional_reputations(self, faction) -> Dict[str, float]:
        """Ensure regional reputations structure exists"""
        if "regional_reputations" not in faction.state:
            faction.state["regional_reputations"] = {}
        return faction.state["regional_reputations"]
    
    def _ensure_character_reputations(self, faction) -> Dict[str, float]:
        """Ensure character reputations structure exists"""
        if "character_reputations" not in faction.state:
            faction.state["character_reputations"] = {}
        return faction.state["character_reputations"]
    
    def _update_reputation_history(self, faction, event: Dict[str, Any]) -> None:
        """Update reputation history with business logic"""
        if "reputation_history" not in faction.state:
            faction.state["reputation_history"] = []
        faction.state["reputation_history"].append(event)
    
    def _update_regional_reputation_history(self, faction, region_id: str, event: Dict[str, Any]) -> None:
        """Update regional reputation history"""
        if "regional_reputation_history" not in faction.state:
            faction.state["regional_reputation_history"] = {}
        if region_id not in faction.state["regional_reputation_history"]:
            faction.state["regional_reputation_history"][region_id] = []
        faction.state["regional_reputation_history"][region_id].append(event)
    
    def _update_character_reputation_history(self, faction, character_id: str, event: Dict[str, Any]) -> None:
        """Update character reputation history"""
        if "character_reputation_history" not in faction.state:
            faction.state["character_reputation_history"] = {}
        if character_id not in faction.state["character_reputation_history"]:
            faction.state["character_reputation_history"][character_id] = []
        faction.state["character_reputation_history"][character_id].append(event)
    
    def _update_reputation_brackets(self, faction, previous_bracket: str, 
                                  current_bracket: str, reason: str) -> bool:
        """Update reputation brackets with business logic"""
        if "reputation_brackets" not in faction.state:
            faction.state["reputation_brackets"] = {
                "current": current_bracket,
                "history": []
            }
        
        faction.state["reputation_brackets"]["current"] = current_bracket
        
        if previous_bracket != current_bracket:
            faction.state["reputation_brackets"]["history"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "from_bracket": previous_bracket,
                "to_bracket": current_bracket,
                "reason": reason
            })
            return True
        return False
    
    def _apply_character_reputation_to_membership(self, faction_id: int, 
                                                character_id: int, 
                                                reputation: float) -> Dict[str, Any]:
        """Apply character reputation effects to membership (business rule)"""
        # This is a placeholder for business logic that would interact with membership
        effects = {}
        
        if reputation < -50:
            effects["suggested_action"] = "consider_exile"
        elif reputation > 70:
            effects["suggested_action"] = "eligible_for_promotion"
        elif reputation < -20:
            effects["suggested_action"] = "restrict_privileges"
        
        return effects
    
    def _calculate_diplomacy_modifier(self, reputation: float) -> float:
        """Business rule for diplomacy modifier based on reputation"""
        return reputation / 200.0  # -0.5 to +0.5 modifier
    
    def _calculate_trade_modifier(self, reputation: float) -> float:
        """Business rule for trade modifier based on reputation"""
        return max(0, reputation / 100.0)  # 0 to +1.0 modifier
    
    def _calculate_recruitment_modifier(self, reputation: float) -> float:
        """Business rule for recruitment modifier based on reputation"""
        return reputation / 100.0  # -1.0 to +1.0 modifier
    
    def _calculate_defense_modifier(self, reputation: float) -> float:
        """Business rule for defense modifier based on reputation"""
        return max(0, reputation / 150.0)  # 0 to +0.67 modifier
    
    def _calculate_info_modifier(self, reputation: float) -> float:
        """Business rule for information gathering modifier"""
        return abs(reputation) / 200.0  # 0 to +0.5 modifier (both extremes help)


def create_faction_reputation_service(database_service: ReputationDatabaseService) -> FactionReputationService:
    """Factory function to create faction reputation service"""
    return FactionReputationService(database_service) 