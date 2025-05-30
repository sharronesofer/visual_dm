"""
Motif system integration for the dialogue system.

This module provides functionality for connecting dialogue with the motif system,
allowing dialogue style and tone to be influenced by active narrative motifs.
"""

from typing import Dict, Any, List, Optional, Set
import logging
import random

# Import motif system components
from backend.systems.motifs.motif_manager import MotifManager

# Configure logger
logger = logging.getLogger(__name__)


class DialogueMotifIntegration:
    """
    Integration between dialogue and motif systems.
    
    Allows for adapting dialogue style, tone, and vocabulary based
    on active narrative motifs in a location or situation.
    """
    
    def __init__(self, motif_manager=None):
        """
        Initialize the dialogue motif integration.
        
        Args:
            motif_manager: Optional motif manager instance
        """
        self.motif_manager = motif_manager or MotifManager.get_instance()
        
        # Canonical motifs with their dialogue characteristics
        # These would be loaded from a database or configuration in a real implementation
        self.motif_data = {
            "tragic": {
                "tone": "somber",
                "themes": ["sorrow", "loss", "fate", "ruin"],
                "keywords": ["doom", "loss", "grief", "sorrowful", "alas", "woe"]
            },
            "heroic": {
                "tone": "inspiring",
                "themes": ["bravery", "justice", "honor", "triumph"],
                "keywords": ["honor", "courage", "noble", "valor", "righteous", "glory"]
            },
            "romantic": {
                "tone": "passionate",
                "themes": ["love", "desire", "connection", "emotion"],
                "keywords": ["passion", "heart", "beauty", "desire", "devoted", "enchanted"]
            },
            "mysterious": {
                "tone": "cryptic",
                "themes": ["secrets", "unknown", "hidden", "enigmatic"],
                "keywords": ["secrets", "whispers", "shadows", "curious", "mysterious", "riddle"]
            },
            "comedic": {
                "tone": "lighthearted",
                "themes": ["humor", "absurdity", "folly", "wit"],
                "keywords": ["amusing", "jest", "laugh", "jolly", "merry", "delightful"]
            },
            "horrific": {
                "tone": "dreadful",
                "themes": ["fear", "dread", "terror", "darkness"],
                "keywords": ["dread", "terror", "horror", "fear", "unspeakable", "gruesome"]
            },
            "historical": {
                "tone": "scholarly",
                "themes": ["time", "legacy", "tradition", "ancestry"],
                "keywords": ["ancient", "legacy", "tradition", "ancestors", "chronicles", "bygone"]
            },
            "magical": {
                "tone": "wondrous",
                "themes": ["enchantment", "power", "mystical", "arcane"],
                "keywords": ["arcane", "enchanted", "magical", "mystical", "wondrous", "spellbound"]
            },
            "political": {
                "tone": "diplomatic",
                "themes": ["power", "control", "influence", "conflict"],
                "keywords": ["influence", "authority", "alliance", "faction", "decree", "diplomatic"]
            },
            "religious": {
                "tone": "reverent",
                "themes": ["faith", "divinity", "belief", "worship"],
                "keywords": ["divine", "blessed", "sacred", "holy", "faithful", "providence"]
            },
            "military": {
                "tone": "disciplined",
                "themes": ["conflict", "strategy", "loyalty", "duty"],
                "keywords": ["duty", "strategy", "command", "ranks", "discipline", "battle"]
            },
            "natural": {
                "tone": "harmonious",
                "themes": ["nature", "harmony", "cycles", "elements"],
                "keywords": ["natural", "harmony", "elements", "cycles", "balance", "wilderness"]
            },
            "deceptive": {
                "tone": "misleading",
                "themes": ["lies", "betrayal", "masks", "secrecy"],
                "keywords": ["deception", "hidden", "secrets", "masks", "misleading", "shrouded"]
            },
            "corrupt": {
                "tone": "ominous",
                "themes": ["deterioration", "greed", "moral decay", "power"],
                "keywords": ["corruption", "decay", "tainted", "foul", "fallen", "corrupted"]
            },
            "redemptive": {
                "tone": "hopeful",
                "themes": ["forgiveness", "renewal", "second chances", "transformation"],
                "keywords": ["redemption", "forgiveness", "renewal", "hope", "dawn", "cleansed"]
            }
        }
    
    def add_motifs_to_context(
        self,
        context: Dict[str, Any],
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add active motifs to dialogue context.
        
        Args:
            context: The existing dialogue context
            location_id: Optional ID of the location to get motifs for
            
        Returns:
            Updated context with motif information added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Get active motifs
        active_motifs = self.get_active_motifs(location_id)
        
        if active_motifs:
            # Add the motifs to the context
            if "motifs" not in updated_context:
                updated_context["motifs"] = []
                
            # Add each motif with its data
            for motif_id in active_motifs:
                motif_info = {
                    "id": motif_id,
                    "data": self.motif_data.get(motif_id, {})
                }
                updated_context["motifs"].append(motif_info)
            
            logger.debug(f"Added {len(active_motifs)} motifs to context")
        
        return updated_context
    
    def apply_motif_style(
        self,
        message: str,
        location_id: Optional[str] = None
    ) -> str:
        """
        Apply motif-influenced styling to a dialogue message.
        
        Args:
            message: The original message to style
            location_id: Optional ID of the location to get active motifs from
            
        Returns:
            Styled message influenced by active motifs
        """
        # Get active motifs
        active_motifs = self.get_active_motifs(location_id)
        
        if not active_motifs:
            return message
            
        # Get a random active motif to apply (in a real implementation, would be more sophisticated)
        motif_id = random.choice(active_motifs)
        motif_data = self.motif_data.get(motif_id, {})
        
        if not motif_data:
            return message
            
        # Apply styling based on motif characteristics
        styled_message = self._apply_motif_characteristics(message, motif_data)
        
        return styled_message
    
    def get_active_motifs(
        self,
        location_id: Optional[str] = None
    ) -> List[str]:
        """
        Get active motifs for a specific location or globally.
        
        Args:
            location_id: Optional ID of the location to get motifs for
            
        Returns:
            List of active motif IDs
        """
        try:
            # First try to get location-specific motifs
            if location_id:
                location_motifs = self.motif_manager.get_active_motifs_for_location(location_id)
                if location_motifs:
                    return location_motifs
            
            # Fall back to global motifs
            global_motifs = self.motif_manager.get_active_global_motifs()
            return global_motifs
            
        except Exception as e:
            logger.error(f"Failed to get active motifs: {e}")
            # Return a default subset in case of error
            return ["mysterious", "political"]
    
    def _apply_motif_characteristics(
        self,
        message: str,
        motif_data: Dict[str, Any]
    ) -> str:
        """
        Apply motif characteristics to style a message.
        
        Args:
            message: The original message to style
            motif_data: Data about the motif to apply
            
        Returns:
            Styled message
        """
        # This is a simplified implementation
        # A more sophisticated version would use NLP techniques
        
        # Create a copy of the message
        styled_message = message
        
        # Get the keywords for the motif
        keywords = motif_data.get("keywords", [])
        
        # 20% chance to add a thematic keyword if the message is substantial in length
        if len(message) > 20 and keywords and random.random() < 0.2:
            keyword = random.choice(keywords)
            
            # Decide where to add the keyword (beginning, middle, end)
            position = random.choice(["beginning", "middle", "end"])
            
            if position == "beginning" and not any(message.startswith(prefix) for prefix in ["I ", "The ", "A ", "In ", "By ", "When "]):
                styled_message = f"By {keyword} means, {message.lower()}"
            elif position == "middle" and ", " in message:
                parts = message.split(", ", 1)
                styled_message = f"{parts[0]}, {keyword}, {parts[1]}"
            elif position == "end" and not message.endswith((".", "!", "?")):
                styled_message = f"{message}, {keyword}."
            
        # 30% chance to subtly transform tone based on the motif's tone
        if random.random() < 0.3:
            tone = motif_data.get("tone")
            if tone == "somber":
                styled_message = styled_message.replace("great", "solemn").replace("good", "grave")
            elif tone == "inspiring":
                styled_message = styled_message.replace("good", "noble").replace("help", "aid")
            elif tone == "passionate":
                styled_message = styled_message.replace("like", "love").replace("friend", "dear one")
            elif tone == "cryptic":
                styled_message = styled_message.replace("know", "sense").replace("tell", "reveal")
            elif tone == "lighthearted":
                styled_message = styled_message.replace("hello", "well met").replace("yes", "indeed")
            elif tone == "dreadful":
                styled_message = styled_message.replace("problem", "terror").replace("issue", "horror")
            elif tone == "scholarly":
                styled_message = styled_message.replace("old", "ancient").replace("story", "chronicle")
            elif tone == "wondrous":
                styled_message = styled_message.replace("unusual", "mystical").replace("strange", "magical")
            elif tone == "diplomatic":
                styled_message = styled_message.replace("tell", "inform").replace("group", "faction")
            elif tone == "reverent":
                styled_message = styled_message.replace("lucky", "blessed").replace("important", "sacred")
            elif tone == "disciplined":
                styled_message = styled_message.replace("job", "duty").replace("group", "unit")
            elif tone == "harmonious":
                styled_message = styled_message.replace("good", "balanced").replace("world", "realm")
            elif tone == "misleading":
                styled_message = styled_message.replace("perhaps", "seemingly").replace("appears", "seems")
            elif tone == "ominous":
                styled_message = styled_message.replace("bad", "corrupted").replace("sick", "tainted")
            elif tone == "hopeful":
                styled_message = styled_message.replace("better", "redeemed").replace("change", "transform")
                
        return styled_message 