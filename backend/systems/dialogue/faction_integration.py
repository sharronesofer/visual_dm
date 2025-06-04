"""
Faction integration for the dialogue system.

This module provides functionality for connecting dialogue with faction relationships,
reputation, and dynamics to create faction-aware conversations.
"""

from typing import Dict, Any, List, Optional, Tuple
import logging

# Import faction system components
from backend.systems.faction.faction_manager import FactionManager

# Configure logger
logger = logging.getLogger(__name__)


class DialogueFactionIntegration:
    """
    Integration between dialogue and faction systems.
    
    Enables dialogue to:
    - Reference faction relationships and reputation
    - Modify faction standing through conversation
    - Provide faction-specific dialogue options
    - Handle faction conflicts in conversation
    """
    
    def __init__(self, faction_manager=None):
        """
        Initialize the dialogue faction integration.
        
        Args:
            faction_manager: Optional faction manager instance
        """
        self.faction_manager = faction_manager or FactionManager.get_instance()
        self.reputation_thresholds = {
            "hostile": -75,
            "unfriendly": -25,
            "neutral": 25,
            "friendly": 75,
            "allied": 100
        }
    
    def add_faction_context_to_dialogue(
        self,
        context: Dict[str, Any],
        character_id: str,
        player_id: Optional[str] = None,
        include_reputation: bool = True,
        include_conflicts: bool = True,
        include_alliances: bool = True
    ) -> Dict[str, Any]:
        """
        Add faction information to dialogue context.
        
        Args:
            context: The existing dialogue context
            character_id: ID of the NPC character
            player_id: Optional player ID for reputation info
            include_reputation: Whether to include reputation data
            include_conflicts: Whether to include conflict information
            include_alliances: Whether to include alliance data
            
        Returns:
            Updated context with faction information added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Create faction context if it doesn't exist
        if "faction_context" not in updated_context:
            updated_context["faction_context"] = {}
        
        faction_context = updated_context["faction_context"]
        
        # Get character's faction affiliation
        character_faction = self._get_character_faction(character_id)
        if character_faction:
            faction_context["character_faction"] = character_faction
            
            # Get faction reputation with player
            if include_reputation and player_id:
                reputation_data = self._get_faction_reputation_data(
                    character_faction["id"], player_id
                )
                faction_context["reputation"] = reputation_data
            
            # Get faction conflicts
            if include_conflicts:
                conflicts = self._get_faction_conflicts(character_faction["id"])
                if conflicts:
                    faction_context["conflicts"] = conflicts
            
            # Get faction alliances
            if include_alliances:
                alliances = self._get_faction_alliances(character_faction["id"])
                if alliances:
                    faction_context["alliances"] = alliances
            
            # Add faction-specific dialogue modifiers
            faction_context["dialogue_modifiers"] = self._get_faction_dialogue_modifiers(
                character_faction["id"], player_id
            )
        
        return updated_context
    
    def get_faction_dialogue_options(
        self,
        character_id: str,
        player_id: Optional[str] = None,
        faction_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get faction-specific dialogue options.
        
        Args:
            character_id: ID of the NPC character
            player_id: Optional player ID for personalized options
            faction_filter: Optional faction ID filter
            
        Returns:
            List of faction-related dialogue options
        """
        dialogue_options = []
        
        try:
            character_faction = self._get_character_faction(character_id)
            if not character_faction:
                return dialogue_options
            
            faction_id = character_faction["id"]
            
            # Filter by faction if specified
            if faction_filter and faction_id != faction_filter:
                return dialogue_options
            
            # Get reputation-based options
            if player_id:
                reputation_data = self._get_faction_reputation_data(faction_id, player_id)
                reputation_options = self._get_reputation_dialogue_options(
                    faction_id, reputation_data
                )
                dialogue_options.extend(reputation_options)
            
            # Get faction conflict options
            conflict_options = self._get_conflict_dialogue_options(faction_id, player_id)
            dialogue_options.extend(conflict_options)
            
            # Get faction service options
            service_options = self._get_faction_service_options(faction_id, player_id)
            dialogue_options.extend(service_options)
            
            # Get faction recruitment options
            recruitment_options = self._get_recruitment_dialogue_options(faction_id, player_id)
            dialogue_options.extend(recruitment_options)
            
        except Exception as e:
            logger.error(f"Error getting faction dialogue options for character {character_id}: {e}")
        
        return dialogue_options
    
    def modify_faction_reputation(
        self,
        faction_id: str,
        player_id: str,
        reputation_change: int,
        reason: str,
        dialogue_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Modify faction reputation based on dialogue choice.
        
        Args:
            faction_id: ID of the faction
            player_id: ID of the player
            reputation_change: Amount to change reputation (can be negative)
            reason: Reason for the reputation change
            dialogue_context: Optional dialogue context
            
        Returns:
            Dictionary with reputation change results
        """
        try:
            # Apply reputation change
            result = self.faction_manager.modify_reputation(
                faction_id=faction_id,
                entity_id=player_id,
                change=reputation_change,
                reason=reason
            )
            
            # Check for reputation threshold changes
            old_standing = self._get_reputation_standing(result.get("old_reputation", 0))
            new_standing = self._get_reputation_standing(result.get("new_reputation", 0))
            
            standing_changed = old_standing != new_standing
            
            # Get consequence information
            consequences = []
            if standing_changed:
                consequences = self._get_standing_change_consequences(
                    faction_id, old_standing, new_standing
                )
            
            return {
                "success": True,
                "faction_id": faction_id,
                "old_reputation": result.get("old_reputation", 0),
                "new_reputation": result.get("new_reputation", 0),
                "reputation_change": reputation_change,
                "old_standing": old_standing,
                "new_standing": new_standing,
                "standing_changed": standing_changed,
                "consequences": consequences,
                "reason": reason
            }
            
        except Exception as e:
            logger.error(f"Error modifying faction reputation for {faction_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_faction_specific_responses(
        self,
        character_id: str,
        faction_context: Dict[str, Any],
        dialogue_context: Dict[str, Any]
    ) -> List[str]:
        """
        Get character responses specific to faction context.
        
        Args:
            character_id: ID of the NPC character
            faction_context: Faction-related context
            dialogue_context: Current dialogue context
            
        Returns:
            List of faction-specific response options
        """
        responses = []
        
        try:
            character_faction = faction_context.get("character_faction")
            if not character_faction:
                return responses
            
            faction_id = character_faction["id"]
            reputation_data = faction_context.get("reputation", {})
            reputation_standing = reputation_data.get("standing", "neutral")
            
            # Get responses based on reputation standing
            standing_responses = self._get_standing_based_responses(
                faction_id, reputation_standing
            )
            responses.extend(standing_responses)
            
            # Get faction conflict responses
            conflicts = faction_context.get("conflicts", [])
            if conflicts:
                conflict_responses = self._get_conflict_based_responses(
                    faction_id, conflicts, dialogue_context
                )
                responses.extend(conflict_responses)
            
            # Get faction alliance responses
            alliances = faction_context.get("alliances", [])
            if alliances:
                alliance_responses = self._get_alliance_based_responses(
                    faction_id, alliances, dialogue_context
                )
                responses.extend(alliance_responses)
            
            # Get faction mission responses
            mission_responses = self._get_faction_mission_responses(
                faction_id, reputation_standing
            )
            responses.extend(mission_responses)
            
        except Exception as e:
            logger.error(f"Error getting faction responses for character {character_id}: {e}")
        
        return responses[:7]  # Limit to 7 most relevant responses
    
    def check_faction_dialogue_restrictions(
        self,
        character_id: str,
        player_id: str,
        dialogue_option: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if player can access a faction-restricted dialogue option.
        
        Args:
            character_id: ID of the NPC character
            player_id: ID of the player
            dialogue_option: The dialogue option to check
            
        Returns:
            Dictionary with access information
        """
        try:
            character_faction = self._get_character_faction(character_id)
            if not character_faction:
                return {"accessible": True, "reason": "No faction restrictions"}
            
            faction_id = character_faction["id"]
            
            # Check reputation requirements
            required_reputation = dialogue_option.get("required_reputation")
            if required_reputation:
                player_reputation = self.faction_manager.get_reputation(faction_id, player_id)
                if player_reputation < required_reputation:
                    standing_needed = self._get_reputation_standing(required_reputation)
                    return {
                        "accessible": False,
                        "reason": f"Requires {standing_needed} standing with {character_faction['name']}",
                        "current_reputation": player_reputation,
                        "required_reputation": required_reputation
                    }
            
            # Check faction membership requirements
            required_membership = dialogue_option.get("required_membership")
            if required_membership:
                is_member = self.faction_manager.is_member(faction_id, player_id)
                if not is_member:
                    return {
                        "accessible": False,
                        "reason": f"Must be a member of {character_faction['name']}",
                        "membership_required": True
                    }
            
            # Check hostile faction restrictions
            hostile_factions = dialogue_option.get("restricted_if_member_of", [])
            for hostile_faction_id in hostile_factions:
                if self.faction_manager.is_member(hostile_faction_id, player_id):
                    hostile_faction = self.faction_manager.get_faction(hostile_faction_id)
                    return {
                        "accessible": False,
                        "reason": f"Restricted due to membership in {hostile_faction.get('name', 'enemy faction')}",
                        "conflicting_faction": hostile_faction_id
                    }
            
            return {"accessible": True, "reason": "All requirements met"}
            
        except Exception as e:
            logger.error(f"Error checking faction dialogue restrictions: {e}")
            return {"accessible": False, "reason": "Error checking restrictions"}
    
    def _get_character_faction(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Get faction affiliation for a character."""
        try:
            # This would integrate with character/NPC system
            # For now, simulate character faction lookup
            character_factions = self.faction_manager.get_character_factions(character_id)
            
            # Return primary faction (first one)
            if character_factions:
                faction_id = character_factions[0]
                faction_data = self.faction_manager.get_faction(faction_id)
                if faction_data:
                    return {
                        "id": faction_id,
                        "name": faction_data.get("name", "Unknown Faction"),
                        "type": faction_data.get("type", "general"),
                        "rank": faction_data.get("character_rank", {}).get(character_id, "member")
                    }
            
            return None
        except Exception as e:
            logger.error(f"Error getting character faction for {character_id}: {e}")
            return None
    
    def _get_faction_reputation_data(self, faction_id: str, player_id: str) -> Dict[str, Any]:
        """Get comprehensive reputation data for a faction."""
        try:
            reputation = self.faction_manager.get_reputation(faction_id, player_id)
            standing = self._get_reputation_standing(reputation)
            
            return {
                "value": reputation,
                "standing": standing,
                "standing_description": self._get_standing_description(standing),
                "thresholds": self.reputation_thresholds,
                "next_threshold": self._get_next_reputation_threshold(reputation),
                "can_improve": reputation < 100,
                "can_worsen": reputation > -100
            }
        except Exception as e:
            logger.error(f"Error getting reputation data for faction {faction_id}: {e}")
            return {"value": 0, "standing": "neutral"}
    
    def _get_faction_conflicts(self, faction_id: str) -> List[Dict[str, Any]]:
        """Get active conflicts for a faction."""
        try:
            conflicts = self.faction_manager.get_faction_conflicts(faction_id)
            return [
                {
                    "enemy_faction_id": conflict.get("enemy_faction_id"),
                    "enemy_faction_name": conflict.get("enemy_faction_name", "Unknown"),
                    "conflict_type": conflict.get("type", "rivalry"),
                    "intensity": conflict.get("intensity", "medium"),
                    "reason": conflict.get("reason", "Unknown conflict")
                }
                for conflict in conflicts
            ]
        except Exception as e:
            logger.error(f"Error getting faction conflicts for {faction_id}: {e}")
            return []
    
    def _get_faction_alliances(self, faction_id: str) -> List[Dict[str, Any]]:
        """Get alliances for a faction."""
        try:
            alliances = self.faction_manager.get_faction_alliances(faction_id)
            return [
                {
                    "ally_faction_id": alliance.get("ally_faction_id"),
                    "ally_faction_name": alliance.get("ally_faction_name", "Unknown"),
                    "alliance_type": alliance.get("type", "cooperation"),
                    "strength": alliance.get("strength", "medium"),
                    "purpose": alliance.get("purpose", "Mutual cooperation")
                }
                for alliance in alliances
            ]
        except Exception as e:
            logger.error(f"Error getting faction alliances for {faction_id}: {e}")
            return []
    
    def _get_faction_dialogue_modifiers(self, faction_id: str, player_id: Optional[str]) -> Dict[str, Any]:
        """Get dialogue modifiers based on faction relationships."""
        modifiers = {
            "tone": "neutral",
            "formality": "standard",
            "trust_level": "cautious",
            "information_sharing": "limited"
        }
        
        if not player_id:
            return modifiers
        
        try:
            reputation = self.faction_manager.get_reputation(faction_id, player_id)
            standing = self._get_reputation_standing(reputation)
            
            # Modify based on standing
            if standing == "hostile":
                modifiers.update({
                    "tone": "aggressive",
                    "formality": "cold",
                    "trust_level": "none",
                    "information_sharing": "none"
                })
            elif standing == "unfriendly":
                modifiers.update({
                    "tone": "unfriendly",
                    "formality": "formal",
                    "trust_level": "suspicious",
                    "information_sharing": "minimal"
                })
            elif standing == "friendly":
                modifiers.update({
                    "tone": "friendly",
                    "formality": "relaxed",
                    "trust_level": "trusting",
                    "information_sharing": "open"
                })
            elif standing == "allied":
                modifiers.update({
                    "tone": "warm",
                    "formality": "casual",
                    "trust_level": "complete",
                    "information_sharing": "unrestricted"
                })
            
        except Exception as e:
            logger.error(f"Error getting dialogue modifiers: {e}")
        
        return modifiers
    
    def _get_reputation_standing(self, reputation: int) -> str:
        """Convert reputation value to standing."""
        if reputation >= self.reputation_thresholds["allied"]:
            return "allied"
        elif reputation >= self.reputation_thresholds["friendly"]:
            return "friendly"
        elif reputation >= self.reputation_thresholds["neutral"]:
            return "neutral"
        elif reputation >= self.reputation_thresholds["unfriendly"]:
            return "unfriendly"
        else:
            return "hostile"
    
    def _get_standing_description(self, standing: str) -> str:
        """Get description of reputation standing."""
        descriptions = {
            "hostile": "They consider you an enemy",
            "unfriendly": "They don't trust you",
            "neutral": "They have no strong opinion of you",
            "friendly": "They like and trust you",
            "allied": "They consider you a valued ally"
        }
        return descriptions.get(standing, "Unknown standing")
    
    def _get_next_reputation_threshold(self, current_reputation: int) -> Optional[Dict[str, Any]]:
        """Get information about the next reputation threshold."""
        for standing, threshold in self.reputation_thresholds.items():
            if current_reputation < threshold:
                return {
                    "standing": standing,
                    "threshold": threshold,
                    "points_needed": threshold - current_reputation
                }
        return None
    
    def _get_reputation_dialogue_options(self, faction_id: str, reputation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get dialogue options based on reputation."""
        options = []
        standing = reputation_data.get("standing", "neutral")
        
        if standing in ["friendly", "allied"]:
            options.append({
                "type": "faction_favor",
                "text": "I need your faction's assistance",
                "option_text": "Can your faction help me?",
                "consequence": "request_favor",
                "required_reputation": self.reputation_thresholds["friendly"]
            })
        
        if standing == "allied":
            options.append({
                "type": "faction_secrets",
                "text": "Tell me what you know about faction affairs",
                "option_text": "Share faction intelligence",
                "consequence": "share_secrets",
                "required_reputation": self.reputation_thresholds["allied"]
            })
        
        if standing in ["neutral", "unfriendly"]:
            options.append({
                "type": "reputation_improvement",
                "text": "How can I improve my standing with your faction?",
                "option_text": "I want to improve relations",
                "consequence": "discuss_reputation"
            })
        
        return options
    
    def _get_conflict_dialogue_options(self, faction_id: str, player_id: Optional[str]) -> List[Dict[str, Any]]:
        """Get dialogue options related to faction conflicts."""
        options = []
        
        try:
            conflicts = self._get_faction_conflicts(faction_id)
            
            for conflict in conflicts:
                enemy_faction_id = conflict["enemy_faction_id"]
                
                # Check if player is member of enemy faction
                if player_id and self.faction_manager.is_member(enemy_faction_id, player_id):
                    options.append({
                        "type": "faction_conflict",
                        "text": f"We know you're with {conflict['enemy_faction_name']}",
                        "option_text": f"About my ties to {conflict['enemy_faction_name']}...",
                        "consequence": "discuss_conflict",
                        "metadata": {"conflict": conflict}
                    })
                else:
                    options.append({
                        "type": "faction_enemy_info",
                        "text": f"What can you tell me about {conflict['enemy_faction_name']}?",
                        "option_text": f"Tell me about your enemies",
                        "consequence": "enemy_information",
                        "metadata": {"conflict": conflict}
                    })
        
        except Exception as e:
            logger.error(f"Error getting conflict dialogue options: {e}")
        
        return options
    
    def _get_faction_service_options(self, faction_id: str, player_id: Optional[str]) -> List[Dict[str, Any]]:
        """Get dialogue options for faction services."""
        options = []
        
        try:
            if player_id:
                reputation = self.faction_manager.get_reputation(faction_id, player_id)
                
                # Services available based on reputation
                if reputation >= self.reputation_thresholds["neutral"]:
                    options.append({
                        "type": "faction_services",
                        "text": "What services does your faction offer?",
                        "option_text": "I'm interested in your services",
                        "consequence": "show_services"
                    })
                
                if reputation >= self.reputation_thresholds["friendly"]:
                    options.append({
                        "type": "faction_missions",
                        "text": "Do you have any missions for me?",
                        "option_text": "I'm looking for work",
                        "consequence": "offer_missions"
                    })
        
        except Exception as e:
            logger.error(f"Error getting faction service options: {e}")
        
        return options
    
    def _get_recruitment_dialogue_options(self, faction_id: str, player_id: Optional[str]) -> List[Dict[str, Any]]:
        """Get dialogue options for faction recruitment."""
        options = []
        
        try:
            if player_id and not self.faction_manager.is_member(faction_id, player_id):
                reputation = self.faction_manager.get_reputation(faction_id, player_id)
                
                if reputation >= self.reputation_thresholds["friendly"]:
                    options.append({
                        "type": "faction_join",
                        "text": "I'm interested in joining your faction",
                        "option_text": "Can I join your faction?",
                        "consequence": "discuss_membership",
                        "required_reputation": self.reputation_thresholds["friendly"]
                    })
        
        except Exception as e:
            logger.error(f"Error getting recruitment dialogue options: {e}")
        
        return options
    
    def _get_standing_based_responses(self, faction_id: str, standing: str) -> List[str]:
        """Get responses based on reputation standing."""
        responses = {
            "hostile": [
                "You're not welcome here",
                "I have nothing to say to you",
                "You should leave before there's trouble"
            ],
            "unfriendly": [
                "What do you want?",
                "Make it quick",
                "I don't have time for you"
            ],
            "neutral": [
                "How can I help you?",
                "What brings you here?",
                "State your business"
            ],
            "friendly": [
                "Good to see you again",
                "How can I assist you today?",
                "What can I do for a friend?"
            ],
            "allied": [
                "Welcome, trusted ally",
                "It's always a pleasure to see you",
                "How can our faction serve you?"
            ]
        }
        return responses.get(standing, responses["neutral"])
    
    def _get_conflict_based_responses(self, faction_id: str, conflicts: List[Dict[str, Any]], dialogue_context: Dict[str, Any]) -> List[str]:
        """Get responses based on faction conflicts."""
        responses = []
        
        for conflict in conflicts:
            enemy_name = conflict["enemy_faction_name"]
            responses.append(f"Watch out for {enemy_name} agents in the area")
            responses.append(f"The {enemy_name} can't be trusted")
        
        return responses[:2]  # Limit to prevent overwhelming dialogue
    
    def _get_alliance_based_responses(self, faction_id: str, alliances: List[Dict[str, Any]], dialogue_context: Dict[str, Any]) -> List[str]:
        """Get responses based on faction alliances."""
        responses = []
        
        for alliance in alliances:
            ally_name = alliance["ally_faction_name"]
            responses.append(f"Our allies in {ally_name} speak highly of recent events")
            responses.append(f"The {ally_name} have been invaluable partners")
        
        return responses[:2]  # Limit to prevent overwhelming dialogue
    
    def _get_faction_mission_responses(self, faction_id: str, standing: str) -> List[str]:
        """Get responses related to faction missions."""
        if standing in ["friendly", "allied"]:
            return [
                "We have important work that needs doing",
                "Your skills could be useful to our cause",
                "There are tasks that require someone we can trust"
            ]
        elif standing == "neutral":
            return [
                "We occasionally have work for reliable freelancers",
                "Prove yourself, and we might have opportunities"
            ]
        else:
            return []
    
    def _get_standing_change_consequences(self, faction_id: str, old_standing: str, new_standing: str) -> List[str]:
        """Get consequences of reputation standing changes."""
        consequences = []
        
        # Standing improved
        if self.reputation_thresholds.get(new_standing, 0) > self.reputation_thresholds.get(old_standing, 0):
            consequences.append(f"Your standing with the faction has improved to {new_standing}")
            
            if new_standing == "friendly":
                consequences.append("You now have access to faction services")
            elif new_standing == "allied":
                consequences.append("You can now access restricted faction areas and information")
        
        # Standing worsened
        else:
            consequences.append(f"Your standing with the faction has declined to {new_standing}")
            
            if new_standing == "hostile":
                consequences.append("Faction members will now attack you on sight")
            elif new_standing == "unfriendly":
                consequences.append("Faction services are no longer available to you")
        
        return consequences
