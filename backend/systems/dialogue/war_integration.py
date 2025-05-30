"""
War & Conflict integration for the dialogue system.

This module provides functionality for connecting dialogue with the War and Tension systems,
allowing dialogue to reference and be influenced by faction wars, tensions, and conflicts.
"""

from typing import Dict, Any, List, Optional, Set
import logging
from datetime import datetime

# Import war and tension system components
from backend.systems.factions.war_manager import WarManager
from backend.systems.factions.tension_manager import TensionManager

# Configure logger
logger = logging.getLogger(__name__)


class DialogueWarIntegration:
    """
    Integration between dialogue and war/tension systems.
    
    Allows dialogue to reference and be influenced by faction wars,
    tensions, conflicts, and diplomatic relationships.
    """
    
    def __init__(self, war_manager=None, tension_manager=None):
        """
        Initialize the dialogue war integration.
        
        Args:
            war_manager: Optional war manager instance
            tension_manager: Optional tension manager instance
        """
        self.war_manager = war_manager or WarManager.get_instance()
        self.tension_manager = tension_manager or TensionManager.get_instance()
    
    def add_war_context_to_dialogue(
        self,
        context: Dict[str, Any],
        faction_id: Optional[str] = None,
        location_id: Optional[str] = None,
        include_local_only: bool = False,
        include_tensions: bool = True
    ) -> Dict[str, Any]:
        """
        Add war and tension information to dialogue context.
        
        Args:
            context: The existing dialogue context
            faction_id: Optional faction ID to filter wars by participants
            location_id: Optional location ID to filter wars by affected areas
            include_local_only: Whether to only include wars affecting the location
            include_tensions: Whether to include pre-war tensions
            
        Returns:
            Updated context with war and tension information added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Create wars context if it doesn't exist
        if "wars" not in updated_context:
            updated_context["wars"] = {}
            
        # Get active wars
        active_wars = self._get_active_wars(faction_id, location_id, include_local_only)
        
        if active_wars:
            updated_context["wars"]["active"] = active_wars
            
            # Get the most significant war
            if active_wars:
                most_significant = max(active_wars, key=lambda w: w.get("significance", 0))
                updated_context["wars"]["most_significant"] = most_significant
        
        # Add tensions if requested
        if include_tensions:
            tensions = self._get_significant_tensions(faction_id, location_id)
            
            if tensions:
                updated_context["wars"]["tensions"] = tensions
                
                # Get the highest tension
                if tensions:
                    highest_tension = max(tensions, key=lambda t: t.get("value", 0))
                    updated_context["wars"]["highest_tension"] = highest_tension
        
        return updated_context
    
    def get_war_dialogue_options(
        self,
        war_id: str,
        faction_id: str,
        dialogue_type: str = "news",
        relation_to_war: str = "neutral"
    ) -> List[Dict[str, Any]]:
        """
        Get dialogue options related to a specific war.
        
        Args:
            war_id: ID of the war
            faction_id: ID of the faction speaking
            dialogue_type: Type of war dialogue ('news', 'propaganda', 'peace', 'threat')
            relation_to_war: Relation to the war ('participant', 'ally', 'neutral', 'victim')
            
        Returns:
            List of war-related dialogue options
        """
        try:
            # Get the war
            war = self.war_manager.get_war(war_id)
            
            if not war:
                logger.warning(f"War not found: {war_id}")
                return []
                
            # Get faction's perspective on the war
            faction_perspective = self._get_faction_war_perspective(faction_id, war)
            
            # Get dialogue options based on type
            options = []
            
            if dialogue_type == "news":
                # War news dialogue
                options = self._get_war_news_dialogue(war, faction_id, relation_to_war)
                
            elif dialogue_type == "propaganda":
                # War propaganda dialogue
                options = self._get_war_propaganda_dialogue(war, faction_id, relation_to_war)
                
            elif dialogue_type == "peace":
                # Peace negotiations dialogue
                options = self._get_peace_dialogue(war, faction_id, relation_to_war)
                
            elif dialogue_type == "threat":
                # Threat or ultimatum dialogue
                options = self._get_threat_dialogue(war, faction_id, relation_to_war)
            
            return options
            
        except Exception as e:
            logger.error(f"Error getting war dialogue options for '{war_id}': {e}")
            return []
    
    def get_tension_dialogue_context(
        self,
        faction1_id: str,
        faction2_id: str
    ) -> Dict[str, Any]:
        """
        Get dialogue context for tension between two factions.
        
        Args:
            faction1_id: ID of the first faction
            faction2_id: ID of the second faction
            
        Returns:
            Tension context for dialogue
        """
        try:
            # Get the tension
            tension = self.tension_manager.get_tension(faction1_id, faction2_id)
            
            if not tension:
                logger.warning(f"Tension not found between: {faction1_id} and {faction2_id}")
                return {}
                
            # Format for dialogue
            tension_context = {
                "faction1_id": faction1_id,
                "faction2_id": faction2_id,
                "value": tension.get("value", 0),
                "state": self._get_tension_state(tension.get("value", 0)),
                "reasons": tension.get("reasons", []),
                "recent_events": tension.get("recent_events", []),
                "war_risk": self._calculate_war_risk(tension.get("value", 0)),
                "description": self._get_tension_description(tension.get("value", 0))
            }
            
            return tension_context
            
        except Exception as e:
            logger.error(f"Error getting tension dialogue context between '{faction1_id}' and '{faction2_id}': {e}")
            return {}
    
    def get_war_narrative_description(
        self,
        war_id: str,
        faction_id: Optional[str] = None,
        include_history: bool = True
    ) -> str:
        """
        Get a narrative description of a war suitable for dialogue.
        
        Args:
            war_id: ID of the war
            faction_id: Optional faction ID for perspective
            include_history: Whether to include war history
            
        Returns:
            Narrative description of the war
        """
        try:
            # Get the war
            war = self.war_manager.get_war(war_id)
            
            if not war:
                logger.warning(f"War not found: {war_id}")
                return "This conflict is unknown."
                
            # Basic description
            name = war.get("name", "The conflict")
            basic_desc = war.get("description", "")
            state = war.get("state", "ongoing")
            state_desc = self._get_war_state_description(state)
            
            # Get participating factions
            sides = self._get_war_sides_description(war)
            
            # Include war history if requested
            history_desc = ""
            if include_history:
                history = war.get("history", [])
                if history:
                    # Format latest history entries
                    latest_entries = history[-2:] if len(history) > 1 else history
                    history_points = [f"{entry.get('event')}" for entry in latest_entries]
                    history_desc = " Recently, " + ". ".join(history_points) + "."
            
            # Different perspective based on faction
            perspective_desc = ""
            if faction_id:
                perspective = self._get_faction_war_perspective(faction_id, war)
                if perspective:
                    perspective_desc = perspective
            
            # Build the narrative description
            narrative = f"{name} is a conflict between {sides}. {basic_desc} {perspective_desc} {state_desc} {history_desc}".strip()
            return narrative
            
        except Exception as e:
            logger.error(f"Error getting war narrative description for '{war_id}': {e}")
            return "Information about this conflict is unavailable."
    
    def _get_active_wars(
        self,
        faction_id: Optional[str] = None,
        location_id: Optional[str] = None,
        local_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get active wars for dialogue context.
        
        Args:
            faction_id: Optional faction ID to filter by participants
            location_id: Optional location ID to filter by affected areas
            local_only: Whether to only include wars affecting the location
            
        Returns:
            List of active wars
        """
        try:
            # Query conditions
            conditions = {"state": "active"}
            
            if faction_id:
                conditions["faction_id"] = faction_id
                
            if location_id and local_only:
                conditions["location_id"] = location_id
                
            # Get wars
            wars = self.war_manager.get_wars_by_conditions(conditions)
            
            # Format for dialogue
            formatted_wars = []
            for war in wars:
                war_info = {
                    "id": war.get("id"),
                    "name": war.get("name"),
                    "description": war.get("description"),
                    "state": war.get("state", "ongoing"),
                    "factions": self._get_war_factions(war),
                    "start_date": war.get("start_date"),
                    "duration": war.get("duration", 0),
                    "significance": war.get("significance", 0),
                    "affected_locations": war.get("affected_locations", [])
                }
                
                # Add faction perspective if provided
                if faction_id:
                    perspective = self._get_faction_war_perspective(faction_id, war)
                    if perspective:
                        war_info["faction_perspective"] = perspective
                
                formatted_wars.append(war_info)
            
            return formatted_wars
            
        except Exception as e:
            logger.error(f"Error getting active wars: {e}")
            return []
    
    def _get_significant_tensions(
        self,
        faction_id: Optional[str] = None,
        location_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get significant tensions between factions for dialogue context.
        
        Args:
            faction_id: Optional faction ID to filter by
            location_id: Optional location ID to filter by affected areas
            
        Returns:
            List of significant tensions
        """
        try:
            # Query conditions
            conditions = {"min_value": 50}  # Only significant tensions
            
            if faction_id:
                conditions["faction_id"] = faction_id
                
            if location_id:
                conditions["location_id"] = location_id
                
            # Get tensions
            tensions = self.tension_manager.get_tensions_by_conditions(conditions)
            
            # Format for dialogue
            formatted_tensions = []
            for tension in tensions:
                tension_info = {
                    "faction1_id": tension.get("faction1_id"),
                    "faction2_id": tension.get("faction2_id"),
                    "value": tension.get("value", 0),
                    "state": self._get_tension_state(tension.get("value", 0)),
                    "reasons": tension.get("reasons", []),
                    "war_risk": self._calculate_war_risk(tension.get("value", 0)),
                    "description": self._get_tension_description(tension.get("value", 0))
                }
                formatted_tensions.append(tension_info)
            
            # Sort by tension value (highest first)
            formatted_tensions.sort(key=lambda t: t.get("value", 0), reverse=True)
            
            return formatted_tensions
            
        except Exception as e:
            logger.error(f"Error getting significant tensions: {e}")
            return []
    
    def _get_war_factions(
        self, 
        war: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Get participating factions in a war.
        
        Args:
            war: War data
            
        Returns:
            Dictionary with sides and their factions
        """
        sides = {
            "side1": war.get("side1", []),
            "side2": war.get("side2", [])
        }
        
        return sides
    
    def _get_faction_war_perspective(
        self, 
        faction_id: str, 
        war: Dict[str, Any]
    ) -> Optional[str]:
        """
        Get a faction's perspective on a war.
        
        Args:
            faction_id: ID of the faction
            war: War data
            
        Returns:
            Faction's perspective on the war
        """
        # Determine the faction's side
        side = None
        if faction_id in war.get("side1", []):
            side = "side1"
        elif faction_id in war.get("side2", []):
            side = "side2"
        
        # Get perspective based on side
        if side:
            perspectives = war.get("faction_perspectives", {})
            perspective = perspectives.get(faction_id)
            
            if not perspective:
                # Fallback to side perspective
                side_perspectives = war.get("side_perspectives", {})
                perspective = side_perspectives.get(side)
            
            return perspective
        
        # Check for neutral perspective
        neutral_perspective = war.get("neutral_perspective")
        if neutral_perspective:
            return neutral_perspective
            
        return None
    
    def _get_war_sides_description(
        self, 
        war: Dict[str, Any]
    ) -> str:
        """
        Get a description of the sides in a war.
        
        Args:
            war: War data
            
        Returns:
            Description of war sides
        """
        side1 = war.get("side1", [])
        side2 = war.get("side2", [])
        
        if not side1 or not side2:
            return "unknown parties"
            
        # Get faction names (would need a faction system integration)
        side1_names = [self._get_faction_name(faction_id) for faction_id in side1]
        side2_names = [self._get_faction_name(faction_id) for faction_id in side2]
        
        # Format sides
        side1_str = " and ".join(side1_names) if side1_names else "unknown factions"
        side2_str = " and ".join(side2_names) if side2_names else "unknown factions"
        
        return f"{side1_str} against {side2_str}"
    
    def _get_faction_name(
        self, 
        faction_id: str
    ) -> str:
        """
        Get the name of a faction.
        
        Args:
            faction_id: ID of the faction
            
        Returns:
            Name of the faction
        """
        # This would connect to a faction system
        # In a real implementation, you'd fetch the faction name
        
        # Placeholder implementation
        return f"the faction of {faction_id}"
    
    def _get_war_state_description(
        self, 
        state: str
    ) -> str:
        """
        Get a description for a war state.
        
        Args:
            state: The war state
            
        Returns:
            Description of the state
        """
        descriptions = {
            "escalating": "The conflict is intensifying with increasing hostilities.",
            "ongoing": "The war continues with active fighting between the sides.",
            "stalemate": "The war has reached a stalemate with neither side making progress.",
            "de-escalating": "The intensity of the conflict is decreasing, though fighting continues.",
            "ceasefire": "A temporary ceasefire is in effect, though tensions remain high.",
            "resolved": "The conflict has been formally resolved through peace treaty or surrender.",
            "dormant": "Active hostilities have ceased, but no formal resolution has been reached."
        }
        
        return descriptions.get(state, "The current state of the conflict is unclear.")
    
    def _get_tension_state(
        self, 
        tension_value: float
    ) -> str:
        """
        Get the state description for a tension value.
        
        Args:
            tension_value: Tension value (-100 to +100)
            
        Returns:
            Tension state description
        """
        if tension_value < -75:
            return "alliance"
        elif tension_value < -25:
            return "friendly"
        elif tension_value < 25:
            return "neutral"
        elif tension_value < 50:
            return "rivalry"
        elif tension_value < 75:
            return "hostile"
        else:
            return "war_imminent"
    
    def _calculate_war_risk(
        self, 
        tension_value: float
    ) -> float:
        """
        Calculate the risk of war based on tension value.
        
        Args:
            tension_value: Tension value (-100 to +100)
            
        Returns:
            War risk (0.0 to 1.0)
        """
        if tension_value <= 0:
            return 0.0
            
        # Simple linear scaling from 0% at 0 tension to 100% at 100 tension
        return min(1.0, max(0.0, tension_value / 100.0))
    
    def _get_tension_description(
        self, 
        tension_value: float
    ) -> str:
        """
        Get a narrative description for a tension value.
        
        Args:
            tension_value: Tension value (-100 to +100)
            
        Returns:
            Narrative description of the tension
        """
        if tension_value < -75:
            return "These factions share a deep alliance built on mutual trust and cooperation."
        elif tension_value < -25:
            return "Relations between these factions are friendly and cooperative."
        elif tension_value < 25:
            return "These factions maintain neutral diplomatic relations."
        elif tension_value < 50:
            return "A rivalry exists between these factions, with some diplomatic tensions."
        elif tension_value < 75:
            return "Relations are hostile, with frequent diplomatic incidents and posturing."
        else:
            return "War seems imminent as tensions have reached a breaking point."
    
    def _get_war_news_dialogue(
        self, 
        war: Dict[str, Any], 
        faction_id: str,
        relation_to_war: str
    ) -> List[Dict[str, Any]]:
        """
        Get news dialogue options for a war.
        
        Args:
            war: War data
            faction_id: Faction ID
            relation_to_war: Relation to the war
            
        Returns:
            List of dialogue options
        """
        # In a real implementation, this would pull from a dialogue database
        # with war news templates, or generate context-specific dialogue
        
        # Sample dialogue options
        name = war.get("name", "The conflict")
        state = war.get("state", "ongoing")
        
        options = []
        
        if relation_to_war == "participant":
            options.append({
                "text": f"Our forces continue to fight bravely in {name}. The latest reports indicate {self._get_war_progress_description(war, faction_id)}.",
                "war_action": "news",
                "war_id": war.get("id")
            })
        elif relation_to_war == "ally":
            options.append({
                "text": f"Our allies are engaged in {name}. We're providing support as needed. The situation is {self._get_war_progress_description(war, faction_id)}.",
                "war_action": "news",
                "war_id": war.get("id")
            })
        elif relation_to_war == "neutral":
            options.append({
                "text": f"We've been monitoring the conflict known as {name}. The situation appears to be {self._get_war_progress_description(war, faction_id)}.",
                "war_action": "news",
                "war_id": war.get("id")
            })
        elif relation_to_war == "victim":
            options.append({
                "text": f"Our people continue to suffer due to {name}. {self._get_war_victim_description(war)}.",
                "war_action": "news",
                "war_id": war.get("id")
            })
        
        return options
    
    def _get_war_propaganda_dialogue(
        self, 
        war: Dict[str, Any], 
        faction_id: str,
        relation_to_war: str
    ) -> List[Dict[str, Any]]:
        """
        Get propaganda dialogue options for a war.
        
        Args:
            war: War data
            faction_id: Faction ID
            relation_to_war: Relation to the war
            
        Returns:
            List of dialogue options
        """
        # Sample dialogue options
        name = war.get("name", "The conflict")
        
        options = []
        
        if relation_to_war == "participant":
            options.append({
                "text": f"Our righteous cause in {name} will prevail! The enemy's forces are weakening by the day, and victory is assured.",
                "war_action": "propaganda",
                "war_id": war.get("id")
            })
            options.append({
                "text": f"The people stand united behind our leaders in this conflict. The enemy underestimated our resolve!",
                "war_action": "propaganda",
                "war_id": war.get("id")
            })
        elif relation_to_war == "ally":
            options.append({
                "text": f"We stand firmly with our allies in {name}. Their cause is just, and we will support them until victory is achieved.",
                "war_action": "propaganda",
                "war_id": war.get("id")
            })
        
        return options
    
    def _get_peace_dialogue(
        self, 
        war: Dict[str, Any], 
        faction_id: str,
        relation_to_war: str
    ) -> List[Dict[str, Any]]:
        """
        Get peace dialogue options for a war.
        
        Args:
            war: War data
            faction_id: Faction ID
            relation_to_war: Relation to the war
            
        Returns:
            List of dialogue options
        """
        # Sample dialogue options
        name = war.get("name", "The conflict")
        
        options = []
        
        if relation_to_war == "participant":
            options.append({
                "text": f"We are open to discussing terms that could bring an end to {name}, provided our key interests are protected.",
                "war_action": "peace",
                "war_id": war.get("id")
            })
        elif relation_to_war == "neutral":
            options.append({
                "text": f"We would be willing to serve as neutral mediators to help bring {name} to a peaceful resolution.",
                "war_action": "mediate",
                "war_id": war.get("id")
            })
        
        return options
    
    def _get_threat_dialogue(
        self, 
        war: Dict[str, Any], 
        faction_id: str,
        relation_to_war: str
    ) -> List[Dict[str, Any]]:
        """
        Get threat dialogue options for a war.
        
        Args:
            war: War data
            faction_id: Faction ID
            relation_to_war: Relation to the war
            
        Returns:
            List of dialogue options
        """
        # Sample dialogue options
        name = war.get("name", "The conflict")
        
        options = []
        
        if relation_to_war == "participant":
            options.append({
                "text": f"Surrender now, or face the full might of our forces! There will be no mercy for those who continue to resist.",
                "war_action": "threat",
                "war_id": war.get("id")
            })
        
        return options
    
    def _get_war_progress_description(
        self, 
        war: Dict[str, Any],
        faction_id: str
    ) -> str:
        """
        Get a description of war progress.
        
        Args:
            war: War data
            faction_id: Faction ID
            
        Returns:
            Description of war progress
        """
        # Determine the faction's side
        side = None
        if faction_id in war.get("side1", []):
            side = "side1"
        elif faction_id in war.get("side2", []):
            side = "side2"
        
        # Get progress based on side and state
        state = war.get("state", "ongoing")
        advantage = war.get("advantage", "equal")
        
        if state == "stalemate":
            return "at a stalemate, with neither side making significant progress"
            
        if side:
            if (side == "side1" and advantage == "side1") or (side == "side2" and advantage == "side2"):
                return "progressing in our favor, though challenges remain"
            elif (side == "side1" and advantage == "side2") or (side == "side2" and advantage == "side1"):
                return "currently challenging, with the enemy holding an advantage"
            else:
                return "balanced, with both sides evenly matched"
        else:
            # Neutral perspective
            if advantage == "side1":
                return "favoring the forces of " + self._get_faction_name(war.get("side1", [""])[0])
            elif advantage == "side2":
                return "favoring the forces of " + self._get_faction_name(war.get("side2", [""])[0])
            else:
                return "evenly matched between the opposing forces"
    
    def _get_war_victim_description(
        self, 
        war: Dict[str, Any]
    ) -> str:
        """
        Get a description of war impact on victims.
        
        Args:
            war: War data
            
        Returns:
            Description of war impact
        """
        # Get war intensity and duration
        intensity = war.get("intensity", "medium")
        duration = war.get("duration", 0)
        
        if intensity == "high":
            return "The devastation has been severe, with many casualties and displaced citizens"
        elif intensity == "medium":
            return "The fighting has caused significant hardship and disruption to daily life"
        else:
            return "While the effects have been manageable, we continue to face challenges due to the conflict" 