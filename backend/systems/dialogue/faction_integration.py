"""
Faction and War/Tension integration for the dialogue system.

This module provides functionality for connecting dialogue with the Faction systems,
allowing dialogue to reference and be influenced by faction relationships, tensions,
war states, and political dynamics.
"""

from typing import Dict, Any, List, Optional, Set
import logging

# Import faction system components
from backend.systems.factions.faction_manager import FactionManager
from backend.systems.factions.tension_manager import TensionManager
from backend.systems.factions.war_manager import WarManager

# Configure logger
logger = logging.getLogger(__name__)


class DialogueFactionIntegration:
    """
    Integration between dialogue and faction systems.
    
    Allows dialogue to reference and be influenced by faction relationships,
    tensions, war states, and political dynamics.
    """
    
    def __init__(self, faction_manager=None, tension_manager=None, war_manager=None):
        """
        Initialize the dialogue faction integration.
        
        Args:
            faction_manager: Optional faction manager instance
            tension_manager: Optional tension manager instance
            war_manager: Optional war manager instance
        """
        self.faction_manager = faction_manager or FactionManager.get_instance()
        self.tension_manager = tension_manager or TensionManager.get_instance()
        self.war_manager = war_manager or WarManager.get_instance()
    
    def add_faction_context_to_dialogue(
        self,
        context: Dict[str, Any],
        faction_id: str,
        character_id: Optional[str] = None,
        include_relations: bool = True,
        include_wars: bool = True,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Add faction information to dialogue context.
        
        Args:
            context: The existing dialogue context
            faction_id: ID of the faction
            character_id: Optional character ID for perspective
            include_relations: Whether to include faction relationships
            include_wars: Whether to include war information
            include_details: Whether to include detailed faction information
            
        Returns:
            Updated context with faction information added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Create faction context if it doesn't exist
        if "factions" not in updated_context:
            updated_context["factions"] = {}
            
        # Get faction info
        faction = self._get_faction_info(faction_id, include_details)
        
        if faction:
            updated_context["factions"]["current"] = faction
            
            # Add character's perspective if provided
            if character_id:
                character_perspective = self._get_character_faction_perspective(character_id, faction_id)
                if character_perspective:
                    updated_context["factions"]["character_perspective"] = character_perspective
            
            # Add faction relationships if requested
            if include_relations:
                relations = self._get_faction_relationships(faction_id)
                tensions = self._get_faction_tensions(faction_id)
                
                if relations:
                    updated_context["factions"]["relationships"] = relations
                    
                if tensions:
                    updated_context["factions"]["tensions"] = tensions
                    
            # Add wars if requested
            if include_wars:
                wars = self._get_faction_wars(faction_id)
                
                if wars:
                    updated_context["factions"]["wars"] = wars
        
        return updated_context
    
    def get_faction_relationship_for_dialogue(
        self,
        faction1_id: str,
        faction2_id: str
    ) -> Dict[str, Any]:
        """
        Get relationship between two factions for dialogue.
        
        Args:
            faction1_id: ID of the first faction
            faction2_id: ID of the second faction
            
        Returns:
            Dictionary with faction relationship information
        """
        try:
            # Get the relationship
            relationship = self.faction_manager.get_faction_relationship(
                faction1_id=faction1_id,
                faction2_id=faction2_id
            )
            
            if not relationship:
                logger.warning(f"No relationship found between factions: {faction1_id}, {faction2_id}")
                return {}
                
            # Get tension
            tension = self.tension_manager.get_tension_level(
                faction1_id=faction1_id,
                faction2_id=faction2_id
            )
            
            # Format for dialogue
            relationship_info = {
                "faction1_id": faction1_id,
                "faction2_id": faction2_id,
                "status": relationship.get("status", "neutral"),
                "stance": relationship.get("stance", "neutral"),
                "treaties": relationship.get("treaties", []),
                "tension": {
                    "level": tension.get("level", 0),
                    "trend": tension.get("trend", "stable"),
                    "causes": tension.get("causes", [])
                },
                "public_opinion": relationship.get("public_opinion", "neutral"),
                "trade_status": relationship.get("trade_status", "none"),
                "recent_events": relationship.get("recent_events", [])[:3]  # Just the most recent
            }
            
            return relationship_info
            
        except Exception as e:
            logger.error(f"Error getting faction relationship for '{faction1_id}' and '{faction2_id}': {e}")
            return {}
    
    def get_war_dialogue_context(
        self,
        war_id: str,
        faction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get dialogue context for a specific war.
        
        Args:
            war_id: ID of the war
            faction_id: Optional faction ID for perspective
            
        Returns:
            War context for dialogue
        """
        try:
            # Get the war
            war = self.war_manager.get_war(war_id)
            
            if not war:
                logger.warning(f"War not found: {war_id}")
                return {}
                
            # Format for dialogue
            war_context = {
                "id": war.get("id"),
                "name": war.get("name"),
                "description": war.get("description", ""),
                "start_date": war.get("start_date"),
                "end_date": war.get("end_date"),
                "status": war.get("status", "ongoing"),
                "aggressors": war.get("aggressors", []),
                "defenders": war.get("defenders", []),
                "allies": war.get("allies", {}),
                "casus_belli": war.get("casus_belli", ""),
                "major_battles": war.get("major_battles", []),
                "casualties": war.get("casualties", {}),
                "war_goals": war.get("war_goals", {}),
                "current_territories": war.get("current_territories", {}),
                "contested_territories": war.get("contested_territories", [])
            }
            
            # Add faction perspective if provided
            if faction_id:
                faction_role = self._get_faction_war_role(faction_id, war_id)
                war_context["faction_role"] = faction_role
                
                faction_perspective = self._get_faction_war_perspective(faction_id, war_id)
                if faction_perspective:
                    war_context["faction_perspective"] = faction_perspective
            
            return war_context
            
        except Exception as e:
            logger.error(f"Error getting war dialogue context for '{war_id}': {e}")
            return {}
    
    def get_tension_dialogue_references(
        self,
        faction1_id: str,
        faction2_id: str,
        reference_type: str = "general"
    ) -> List[str]:
        """
        Get tension-related dialogue references between factions.
        
        Args:
            faction1_id: ID of the first faction
            faction2_id: ID of the second faction
            reference_type: Type of references ('general', 'causes', 'outcomes', 'opinions')
            
        Returns:
            List of tension-related dialogue references
        """
        try:
            # Get the tension
            tension = self.tension_manager.get_tension_level(
                faction1_id=faction1_id,
                faction2_id=faction2_id
            )
            
            if not tension:
                return []
                
            # Get factions
            faction1 = self.faction_manager.get_faction(faction1_id)
            faction2 = self.faction_manager.get_faction(faction2_id)
            
            if not faction1 or not faction2:
                return []
                
            faction1_name = faction1.get("name", faction1_id)
            faction2_name = faction2.get("name", faction2_id)
            
            # Get level and causes
            level = tension.get("level", 0)
            causes = tension.get("causes", [])
            trend = tension.get("trend", "stable")
            
            # Create references based on type
            references = []
            
            if reference_type == "general":
                if level <= 20:
                    references.append(f"Relations between {faction1_name} and {faction2_name} are cordial.")
                    references.append(f"There is little tension between {faction1_name} and {faction2_name}.")
                elif level <= 40:
                    references.append(f"There is some diplomatic friction between {faction1_name} and {faction2_name}.")
                    references.append(f"{faction1_name} and {faction2_name} maintain formal but strained relations.")
                elif level <= 60:
                    references.append(f"Tensions between {faction1_name} and {faction2_name} have been escalating.")
                    references.append(f"Diplomatic incidents between {faction1_name} and {faction2_name} are increasingly common.")
                elif level <= 80:
                    references.append(f"Relations between {faction1_name} and {faction2_name} are severely strained.")
                    references.append(f"Many fear conflict between {faction1_name} and {faction2_name} is inevitable.")
                else:
                    references.append(f"{faction1_name} and {faction2_name} are on the brink of open conflict.")
                    references.append(f"War between {faction1_name} and {faction2_name} seems imminent.")
                    
                # Add trend
                if trend == "increasing":
                    references.append(f"Tensions between {faction1_name} and {faction2_name} are rising.")
                elif trend == "decreasing":
                    references.append(f"Relations between {faction1_name} and {faction2_name} have been improving lately.")
            
            elif reference_type == "causes":
                if causes:
                    for cause in causes[:3]:  # Limit to 3 causes
                        references.append(f"{cause.get('description', '')}")
                        
                    if level > 50:
                        references.append(f"These issues could lead to conflict if not addressed.")
            
            elif reference_type == "outcomes":
                if level <= 30:
                    references.append(f"Trade between {faction1_name} and {faction2_name} continues unaffected.")
                elif level <= 60:
                    references.append(f"Some merchants are reluctant to trade across the border due to tensions.")
                    references.append(f"Diplomatic missions between {faction1_name} and {faction2_name} have been reduced.")
                else:
                    references.append(f"Border skirmishes between {faction1_name} and {faction2_name} have been reported.")
                    references.append(f"Many citizens have fled the border regions, fearing conflict.")
            
            elif reference_type == "opinions":
                if level <= 30:
                    references.append(f"Most citizens see {faction2_name} as a trusted ally or neutral party.")
                elif level <= 60:
                    references.append(f"Public opinion about {faction2_name} has soured in recent times.")
                else:
                    references.append(f"Many in {faction1_name} openly express hostility toward {faction2_name}.")
                    references.append(f"Some extremists have called for war against {faction2_name}.")
            
            return references
            
        except Exception as e:
            logger.error(f"Error getting tension dialogue references for '{faction1_id}' and '{faction2_id}': {e}")
            return []
    
    def get_faction_description_for_dialogue(
        self,
        faction_id: str,
        perspective: str = "neutral",
        include_history: bool = True
    ) -> str:
        """
        Get a narrative description of a faction suitable for dialogue.
        
        Args:
            faction_id: ID of the faction
            perspective: Perspective to describe from ('neutral', 'ally', 'rival', 'member')
            include_history: Whether to include faction history
            
        Returns:
            Narrative description of the faction
        """
        try:
            # Get the faction
            faction = self.faction_manager.get_faction(faction_id)
            
            if not faction:
                logger.warning(f"Faction not found: {faction_id}")
                return "This faction is unknown."
                
            # Basic description
            name = faction.get("name", "")
            basic_desc = faction.get("description", "")
            
            # Get history if requested
            history_desc = ""
            if include_history:
                history = faction.get("history", "")
                if history:
                    history_desc = f" Historically, {history}"
            
            # Different description based on perspective
            if perspective == "neutral":
                return f"The faction known as {name} is {basic_desc}.{history_desc}".strip()
            elif perspective == "ally":
                ally_desc = faction.get("ally_perspective", "")
                return f"Your allies, {name}, are {basic_desc} {ally_desc}.{history_desc}".strip()
            elif perspective == "rival":
                rival_desc = faction.get("rival_perspective", "")
                return f"Your rivals, {name}, are {basic_desc} {rival_desc}.{history_desc}".strip()
            elif perspective == "member":
                member_desc = faction.get("member_perspective", "")
                return f"Your faction, {name}, is {basic_desc} {member_desc}.{history_desc}".strip()
            else:
                return f"The faction known as {name} is {basic_desc}.{history_desc}".strip()
            
        except Exception as e:
            logger.error(f"Error getting faction description for '{faction_id}': {e}")
            return "Information about this faction is unavailable."
    
    def get_war_status_summary(
        self,
        war_id: str,
        faction_id: Optional[str] = None
    ) -> str:
        """
        Get a summary of the current war status suitable for dialogue.
        
        Args:
            war_id: ID of the war
            faction_id: Optional faction ID for perspective
            
        Returns:
            Summary of the war status
        """
        try:
            # Get the war
            war = self.war_manager.get_war(war_id)
            
            if not war:
                logger.warning(f"War not found: {war_id}")
                return "This conflict is unknown."
                
            # Basic information
            name = war.get("name", "")
            status = war.get("status", "ongoing")
            
            # Get faction names
            aggressors = war.get("aggressors", [])
            defenders = war.get("defenders", [])
            
            aggressor_names = []
            for faction_id in aggressors:
                faction = self.faction_manager.get_faction(faction_id)
                if faction:
                    aggressor_names.append(faction.get("name", faction_id))
                else:
                    aggressor_names.append(faction_id)
                    
            defender_names = []
            for faction_id in defenders:
                faction = self.faction_manager.get_faction(faction_id)
                if faction:
                    defender_names.append(faction.get("name", faction_id))
                else:
                    defender_names.append(faction_id)
            
            # Format sides
            aggressor_side = " and ".join(aggressor_names)
            defender_side = " and ".join(defender_names)
            
            # Get current progress
            progress = war.get("progress", {})
            aggressor_advantage = progress.get("aggressor_advantage", 0)
            territories_captured = len(progress.get("captured_territories", []))
            
            # Build status string
            if status == "ongoing":
                if aggressor_advantage > 30:
                    status_desc = f"The war is going in favor of {aggressor_side}."
                elif aggressor_advantage < -30:
                    status_desc = f"The war is going in favor of {defender_side}."
                else:
                    status_desc = "The war is currently at a stalemate."
                    
                summary = f"The {name} between {aggressor_side} and {defender_side} continues. {status_desc} So far, {territories_captured} territories have changed hands."
            
            elif status == "ended":
                winner = war.get("winner", "")
                if winner in aggressors:
                    summary = f"The {name} ended with victory for {aggressor_side} over {defender_side}."
                elif winner in defenders:
                    summary = f"The {name} ended with victory for {defender_side} over {aggressor_side}."
                else:
                    terms = war.get("peace_terms", "")
                    summary = f"The {name} between {aggressor_side} and {defender_side} has ended in a settlement. {terms}"
            
            else:
                summary = f"The {name} between {aggressor_side} and {defender_side} is {status}."
            
            # Add faction perspective if provided
            if faction_id:
                perspective = self._get_faction_war_perspective(faction_id, war_id)
                if perspective:
                    summary += f" From your perspective, {perspective}"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting war status summary for '{war_id}': {e}")
            return "Information about this conflict is unavailable."
    
    def _get_faction_info(
        self,
        faction_id: str,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Get information about a faction for dialogue context.
        
        Args:
            faction_id: ID of the faction
            include_details: Whether to include detailed faction information
            
        Returns:
            Dictionary with faction information
        """
        try:
            # Get the faction
            faction = self.faction_manager.get_faction(faction_id)
            
            if not faction:
                logger.warning(f"Faction not found: {faction_id}")
                return {}
                
            # Basic faction info
            faction_info = {
                "id": faction.get("id"),
                "name": faction.get("name"),
                "type": faction.get("type", "faction")
            }
            
            # Add details if requested
            if include_details:
                faction_info.update({
                    "description": faction.get("description", ""),
                    "ideology": faction.get("ideology", ""),
                    "strength": faction.get("strength", "moderate"),
                    "territories": faction.get("territories", []),
                    "leaders": faction.get("leaders", []),
                    "notable_members": faction.get("notable_members", []),
                    "values": faction.get("values", [])
                })
            
            return faction_info
            
        except Exception as e:
            logger.error(f"Error getting faction info for '{faction_id}': {e}")
            return {}
    
    def _get_character_faction_perspective(
        self,
        character_id: str,
        faction_id: str
    ) -> Dict[str, Any]:
        """
        Get a character's perspective on a faction.
        
        Args:
            character_id: ID of the character
            faction_id: ID of the faction
            
        Returns:
            Character's perspective on the faction
        """
        try:
            # Get character's faction
            character_faction = self._get_character_faction(character_id)
            
            if not character_faction:
                return {}
                
            # Get the relationship between factions
            relationship = self.faction_manager.get_faction_relationship(
                faction1_id=character_faction,
                faction2_id=faction_id
            )
            
            if not relationship:
                return {}
                
            # Get perspective based on relationship
            status = relationship.get("status", "neutral")
            
            perspective = {
                "character_faction": character_faction,
                "stance": status,
                "opinion": relationship.get("opinion", "neutral")
            }
            
            # Add specific perspective content based on stance
            if status == "ally":
                perspective["view"] = "favorable"
                perspective["description"] = "You see them as a valuable ally."
            elif status == "friendly":
                perspective["view"] = "positive"
                perspective["description"] = "You have a positive view of this faction."
            elif status == "neutral":
                perspective["view"] = "neutral"
                perspective["description"] = "You have no strong feelings about this faction."
            elif status == "unfriendly":
                perspective["view"] = "negative"
                perspective["description"] = "You are wary of this faction."
            elif status == "hostile":
                perspective["view"] = "hostile"
                perspective["description"] = "You consider them enemies."
            
            return perspective
            
        except Exception as e:
            logger.error(f"Error getting character faction perspective for '{character_id}' on '{faction_id}': {e}")
            return {}
    
    def _get_faction_relationships(
        self,
        faction_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get relationships for a faction.
        
        Args:
            faction_id: ID of the faction
            
        Returns:
            List of faction relationships
        """
        try:
            # Get faction relationships
            relationships = self.faction_manager.get_faction_relationships(faction_id)
            
            # Format for dialogue
            formatted_relationships = []
            for relationship in relationships:
                other_faction_id = relationship.get("faction_id")
                other_faction = self.faction_manager.get_faction(other_faction_id)
                
                if not other_faction:
                    continue
                    
                relationship_info = {
                    "faction_id": other_faction_id,
                    "faction_name": other_faction.get("name"),
                    "status": relationship.get("status", "neutral"),
                    "treaties": relationship.get("treaties", [])
                }
                formatted_relationships.append(relationship_info)
            
            return formatted_relationships
            
        except Exception as e:
            logger.error(f"Error getting faction relationships for '{faction_id}': {e}")
            return []
    
    def _get_faction_tensions(
        self,
        faction_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get tensions for a faction.
        
        Args:
            faction_id: ID of the faction
            
        Returns:
            List of faction tensions
        """
        try:
            # Get faction tensions
            tensions = self.tension_manager.get_faction_tensions(faction_id)
            
            # Format for dialogue
            formatted_tensions = []
            for tension in tensions:
                other_faction_id = tension.get("faction_id")
                other_faction = self.faction_manager.get_faction(other_faction_id)
                
                if not other_faction:
                    continue
                    
                tension_info = {
                    "faction_id": other_faction_id,
                    "faction_name": other_faction.get("name"),
                    "level": tension.get("level", 0),
                    "trend": tension.get("trend", "stable"),
                    "causes": tension.get("causes", [])
                }
                formatted_tensions.append(tension_info)
            
            # Sort by tension level
            formatted_tensions.sort(key=lambda x: x.get("level", 0), reverse=True)
            
            return formatted_tensions
            
        except Exception as e:
            logger.error(f"Error getting faction tensions for '{faction_id}': {e}")
            return []
    
    def _get_faction_wars(
        self,
        faction_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get wars involving a faction.
        
        Args:
            faction_id: ID of the faction
            
        Returns:
            List of faction wars
        """
        try:
            # Get faction wars
            wars = self.war_manager.get_faction_wars(faction_id)
            
            # Format for dialogue
            formatted_wars = []
            for war in wars:
                war_info = {
                    "id": war.get("id"),
                    "name": war.get("name"),
                    "status": war.get("status", "ongoing"),
                    "role": self._get_faction_war_role(faction_id, war.get("id")),
                    "start_date": war.get("start_date"),
                    "against": self._get_war_opponents(faction_id, war)
                }
                formatted_wars.append(war_info)
            
            return formatted_wars
            
        except Exception as e:
            logger.error(f"Error getting faction wars for '{faction_id}': {e}")
            return []
    
    def _get_character_faction(
        self,
        character_id: str
    ) -> Optional[str]:
        """
        Get a character's faction.
        
        Args:
            character_id: ID of the character
            
        Returns:
            ID of the character's faction
        """
        # This would connect to a character system to get faction
        # In a real implementation, you'd have a proper lookup
        
        # Placeholder implementation
        try:
            # This is a simplified version that assumes characters
            # have a faction_id property accessible somewhere
            from backend.systems.characters.character_manager import CharacterManager
            
            character_manager = CharacterManager.get_instance()
            character = character_manager.get_character(character_id)
            
            if character:
                return character.get("faction_id")
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting character faction for '{character_id}': {e}")
            return None
    
    def _get_faction_war_role(
        self,
        faction_id: str,
        war_id: str
    ) -> str:
        """
        Get a faction's role in a war.
        
        Args:
            faction_id: ID of the faction
            war_id: ID of the war
            
        Returns:
            Role of the faction in the war ('aggressor', 'defender', 'ally', 'neutral')
        """
        try:
            # Get the war
            war = self.war_manager.get_war(war_id)
            
            if not war:
                return "unknown"
                
            # Check roles
            if faction_id in war.get("aggressors", []):
                return "aggressor"
            elif faction_id in war.get("defenders", []):
                return "defender"
            
            # Check allies
            allies = war.get("allies", {})
            for side, ally_list in allies.items():
                if faction_id in ally_list:
                    return f"ally_{side}"
            
            return "neutral"
            
        except Exception as e:
            logger.error(f"Error getting faction war role for '{faction_id}' in war '{war_id}': {e}")
            return "unknown"
    
    def _get_faction_war_perspective(
        self,
        faction_id: str,
        war_id: str
    ) -> str:
        """
        Get a faction's perspective on a war.
        
        Args:
            faction_id: ID of the faction
            war_id: ID of the war
            
        Returns:
            Faction's perspective on the war
        """
        try:
            # Get the war
            war = self.war_manager.get_war(war_id)
            
            if not war:
                return ""
                
            # Get role
            role = self._get_faction_war_role(faction_id, war_id)
            
            # Get perspective based on role
            perspectives = war.get("perspectives", {})
            faction_perspective = perspectives.get(faction_id)
            
            if faction_perspective:
                return faction_perspective
                
            # Default perspectives based on role
            if role == "aggressor":
                return "This is a just and necessary conflict to achieve our goals."
            elif role == "defender":
                return "We are defending ourselves against unprovoked aggression."
            elif role.startswith("ally_aggressor"):
                return "We support our allies in this conflict."
            elif role.startswith("ally_defender"):
                return "We stand with our allies against aggression."
            else:
                return "This conflict does not directly involve us."
            
        except Exception as e:
            logger.error(f"Error getting faction war perspective for '{faction_id}' in war '{war_id}': {e}")
            return ""
    
    def _get_war_opponents(
        self,
        faction_id: str,
        war: Dict[str, Any]
    ) -> List[str]:
        """
        Get a list of opposing faction names in a war.
        
        Args:
            faction_id: ID of the faction
            war: War data
            
        Returns:
            List of opposing faction names
        """
        role = self._get_faction_war_role(faction_id, war.get("id"))
        
        opponents = []
        if role == "aggressor" or role.startswith("ally_aggressor"):
            # Opponents are defenders and their allies
            opponent_ids = war.get("defenders", []) + war.get("allies", {}).get("defender", [])
        elif role == "defender" or role.startswith("ally_defender"):
            # Opponents are aggressors and their allies
            opponent_ids = war.get("aggressors", []) + war.get("allies", {}).get("aggressor", [])
        else:
            return []
            
        # Get faction names
        for opponent_id in opponent_ids:
            faction = self.faction_manager.get_faction(opponent_id)
            if faction:
                opponents.append(faction.get("name", opponent_id))
            else:
                opponents.append(opponent_id)
                
        return opponents 