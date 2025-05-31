"""
Population system integration for the dialogue system.

This module provides functionality for integrating dialogue with the population system,
making NPCs aware of regional demographics, occupations, and social dynamics.
"""

from typing import Dict, Any, List, Optional, Set
import logging
import random

# Import population system components
from backend.systems.population.population_manager import PopulationManager

# Configure logger
logger = logging.getLogger(__name__)

class DialoguePopulationIntegration:
    """
    Integration between dialogue and population systems.
    
    Allows dialogue to reflect awareness of population demographics,
    occupations, social relationships, and migration patterns.
    """
    
    def __init__(self, population_manager=None):
        """
        Initialize the dialogue population integration.
        
        Args:
            population_manager: Optional population manager instance
        """
        self.population_manager = population_manager or PopulationManager.get_instance()
    
    def add_population_data_to_context(
        self,
        context: Dict[str, Any],
        location_id: str
    ) -> Dict[str, Any]:
        """
        Add population data to dialogue context for a specific location.
        
        Args:
            context: The existing dialogue context
            location_id: ID of the location to get population data for
            
        Returns:
            Updated context with population information added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Get population data for the location
        population_data = self.get_location_population_data(location_id)
        
        if population_data:
            updated_context["population_data"] = population_data
            logger.debug(f"Added population data for location {location_id} to context")
        
        return updated_context
    
    def get_location_population_data(
        self,
        location_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get population data for a specific location.
        
        Args:
            location_id: ID of the location to get population data for
            
        Returns:
            Dictionary with population information or None if not available
        """
        try:
            # Get demographics and occupations
            demographics = self.population_manager.get_location_demographics(location_id)
            occupations = self.population_manager.get_location_occupations(location_id)
            
            # Get social dynamics
            notable_npcs = self.population_manager.get_location_notable_npcs(location_id)
            social_classes = self.population_manager.get_location_social_classes(location_id)
            
            # Get migration patterns
            recent_migrations = self.population_manager.get_recent_migrations(location_id)
            
            # Compile population data
            population_data = {
                "demographics": demographics,
                "occupations": occupations,
                "notable_npcs": notable_npcs,
                "social_classes": social_classes,
                "recent_migrations": recent_migrations
            }
            
            return population_data
            
        except Exception as e:
            logger.error(f"Failed to get population data for location {location_id}: {e}")
            return None
    
    def get_occupation_dialogue(
        self,
        character_id: str,
        occupation_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get occupation-specific dialogue options for a character.
        
        Args:
            character_id: ID of the character
            occupation_type: Optional occupation type to override character's occupation
            
        Returns:
            Dictionary with occupation-specific dialogue options
        """
        try:
            # Get character occupation if not specified
            if not occupation_type:
                character_data = self.population_manager.get_character(character_id)
                if character_data and "occupation" in character_data:
                    occupation_type = character_data.get("occupation", {}).get("type")
                else:
                    occupation_type = "commoner"  # Default occupation
            
            # Generate occupation-specific dialogue options
            dialogue_options = self._generate_occupation_dialogue(occupation_type)
            return dialogue_options
            
        except Exception as e:
            logger.error(f"Failed to get occupation dialogue for character {character_id}: {e}")
            
            # Return default dialogue options
            return {
                "greetings": ["Hello.", "Greetings.", "Welcome."],
                "farewells": ["Goodbye.", "Farewell.", "Until next time."],
                "topics": ["weather", "local_events"],
                "phrases": {
                    "weather": ["Nice weather today.", "Weather's been strange lately."],
                    "local_events": ["Nothing much happening around here."]
                }
            }
    
    def get_social_status_dialogue(
        self,
        character_id: str,
        target_id: str
    ) -> Dict[str, str]:
        """
        Get dialogue modifiers based on social status difference between characters.
        
        Args:
            character_id: ID of the speaking character
            target_id: ID of the target character
            
        Returns:
            Dictionary with social status modifiers for dialogue
        """
        try:
            # Get social status for both characters
            character_status = self._get_character_social_status(character_id)
            target_status = self._get_character_social_status(target_id)
            
            # Calculate status difference
            status_diff = character_status - target_status
            
            # Define dialogue modifiers based on status difference
            if status_diff > 1.5:
                # Character is much higher status than target
                return {
                    "formality": "condescending",
                    "politeness": "minimal",
                    "address_terms": ["peasant", "commoner", "lowborn"],
                    "tone": "commanding"
                }
            elif status_diff > 0.5:
                # Character is higher status than target
                return {
                    "formality": "formal",
                    "politeness": "moderate",
                    "address_terms": ["good fellow", "citizen", "you there"],
                    "tone": "authoritative"
                }
            elif status_diff > -0.5:
                # Characters are similar status
                return {
                    "formality": "casual",
                    "politeness": "standard",
                    "address_terms": ["friend", "neighbor", "companion"],
                    "tone": "friendly"
                }
            elif status_diff > -1.5:
                # Character is lower status than target
                return {
                    "formality": "respectful",
                    "politeness": "high",
                    "address_terms": ["sir", "ma'am", "my good person"],
                    "tone": "deferential"
                }
            else:
                # Character is much lower status than target
                return {
                    "formality": "subservient",
                    "politeness": "excessive",
                    "address_terms": ["my lord", "my lady", "your excellency"],
                    "tone": "humble"
                }
                
        except Exception as e:
            logger.error(f"Failed to get social status dialogue modifiers: {e}")
            
            # Return default equal-status modifiers
            return {
                "formality": "casual",
                "politeness": "standard",
                "address_terms": ["friend", "neighbor"],
                "tone": "neutral"
            }
    
    def modify_dialogue_for_demographics(
        self,
        message: str,
        location_id: str
    ) -> str:
        """
        Modify dialogue to reflect awareness of local demographics.
        
        Args:
            message: Original message content
            location_id: ID of the location for demographic context
            
        Returns:
            Modified message with demographic awareness
        """
        # Get demographic data
        population_data = self.get_location_population_data(location_id)
        if not population_data or "demographics" not in population_data:
            return message
            
        demographics = population_data["demographics"]
        
        # Check for demographic references to modify
        modified_message = message
        
        # Check for generic references to replace with specific demographic info
        if "people here" in modified_message.lower():
            # Get dominant groups
            dominant_groups = []
            for group, percentage in demographics.items():
                if percentage > 30:  # Arbitrary threshold for "dominant"
                    dominant_groups.append(group)
            
            if dominant_groups:
                if len(dominant_groups) == 1:
                    replacement = f"the {dominant_groups[0]} folk here"
                else:
                    replacement = f"the {' and '.join(dominant_groups)} folk here"
                modified_message = modified_message.replace("people here", replacement)
        
        # Add demographic awareness to statements about the town/city
        town_references = ["this town", "this city", "this village", "this settlement"]
        for ref in town_references:
            if ref in modified_message.lower():
                # Get most notable demographic shift or feature
                notable_demo = self._get_most_notable_demographic(demographics)
                if notable_demo:
                    if "mostly" not in modified_message and "primarily" not in modified_message:
                        modified_message = modified_message.replace(
                            ref, 
                            f"{ref}, primarily {notable_demo},"
                        )
        
        return modified_message
    
    def generate_demographic_comment(
        self,
        location_id: str
    ) -> str:
        """
        Generate a comment about the local demographics.
        
        Args:
            location_id: ID of the location to comment on
            
        Returns:
            Comment about local demographics
        """
        # Get demographic data
        population_data = self.get_location_population_data(location_id)
        if not population_data or "demographics" not in population_data:
            return "There are all sorts of folk around here."
            
        demographics = population_data["demographics"]
        
        # Find dominant and minority groups
        dominant_groups = []
        minority_groups = []
        
        for group, percentage in demographics.items():
            if percentage > 30:
                dominant_groups.append((group, percentage))
            elif percentage < 10 and percentage > 0:
                minority_groups.append((group, percentage))
        
        # Sort by percentage (highest first)
        dominant_groups.sort(key=lambda x: x[1], reverse=True)
        
        # Generate comment based on demographic makeup
        if len(dominant_groups) == 1:
            dominant = dominant_groups[0][0]
            percentage = dominant_groups[0][1]
            
            if percentage > 80:
                return f"Almost everyone here is {dominant}. That's just how it's always been."
            elif percentage > 60:
                return f"This is primarily a {dominant} settlement, though you'll find others as well."
            else:
                return f"The {dominant} make up the largest group here, but we're fairly diverse."
                
        elif len(dominant_groups) == 2:
            group1, pct1 = dominant_groups[0]
            group2, pct2 = dominant_groups[1]
            return f"This place is a mix of mainly {group1} and {group2} folk living together."
            
        elif len(dominant_groups) > 2:
            groups = [g[0] for g in dominant_groups[:3]]
            return f"We're quite diverse here - {', '.join(groups)}, and others all call this place home."
            
        if minority_groups:
            minority = minority_groups[0][0]
            return f"We don't have many {minority} folk around here, they tend to settle elsewhere."
            
        return "The makeup of our community has been stable for generations."
    
    def generate_occupation_comment(
        self,
        location_id: str
    ) -> str:
        """
        Generate a comment about common occupations in the area.
        
        Args:
            location_id: ID of the location to comment on
            
        Returns:
            Comment about local occupations
        """
        # Get occupation data
        population_data = self.get_location_population_data(location_id)
        if not population_data or "occupations" not in population_data:
            return "People do all sorts of work around here."
            
        occupations = population_data["occupations"]
        
        # Find the top occupations
        if not occupations:
            return "Work is hard to come by these days."
            
        top_occupations = sorted(occupations.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Generate comment based on occupational makeup
        if len(top_occupations) == 1:
            occupation, percentage = top_occupations[0]
            
            if percentage > 70:
                return f"Almost everyone here works as a {occupation}. It's our way of life."
            elif percentage > 40:
                return f"Most folk here make their living as {occupation}s, though there are other trades too."
            else:
                return f"Being a {occupation} is the most common profession here, but we have plenty of others."
                
        elif len(top_occupations) >= 2:
            occupations_list = [o[0] for o in top_occupations]
            
            if sum(o[1] for o in top_occupations) > 70:
                occupation_str = ", ".join(occupations_list[:-1]) + f" and {occupations_list[-1]}"
                return f"Most people here work as {occupation_str}. Those are the main trades in these parts."
            else:
                occupation_str = " and ".join(occupations_list[:2])
                return f"You'll find many {occupation_str} here, but plenty of other trades as well."
        
        return "People find all sorts of ways to make a living around here."
    
    def _generate_occupation_dialogue(
        self,
        occupation_type: str
    ) -> Dict[str, Any]:
        """
        Generate occupation-specific dialogue options.
        
        Args:
            occupation_type: Type of occupation
            
        Returns:
            Dictionary with occupation-specific dialogue options
        """
        # Define dialogue options for different occupations
        occupation_dialogue = {
            "blacksmith": {
                "greetings": [
                    "Welcome to the forge. What can I hammer out for you?",
                    "Looking for steel? You've come to the right place.",
                    "Mind the heat! What brings you to my forge?"
                ],
                "farewells": [
                    "Safe travels. Come back when you need something sturdy.",
                    "May your blade stay sharp and your armor hold true.",
                    "If it breaks, bring it back. That's a promise."
                ],
                "topics": ["metalwork", "weapons", "armor", "tools"],
                "phrases": {
                    "metalwork": [
                        "Good steel needs both fire and patience.",
                        "I've been working the forge for twenty years now.",
                        "The difference between a novice and a master is a thousand broken hammers."
                    ],
                    "weapons": [
                        "A good blade is an extension of your arm.",
                        "Balance matters more than sharpness sometimes.",
                        "I don't just make weapons, I make survival tools."
                    ],
                    "armor": [
                        "Armor's no good if you can't move in it.",
                        "The joints are always the weakness in any design.",
                        "I fit each piece to the wearer. No exceptions."
                    ],
                    "tools": [
                        "A farmer with a broken plow is a hungry farmer.",
                        "I take as much pride in a good hammer as in a fine sword.",
                        "Tools built this town, not weapons."
                    ]
                }
            },
            "merchant": {
                "greetings": [
                    "Welcome, welcome! Please browse my wares.",
                    "A discerning customer! What catches your eye today?",
                    "Greetings! Special prices just for you today."
                ],
                "farewells": [
                    "Thank you for your business. Return soon!",
                    "Your patronage is appreciated. Safe travels.",
                    "Remember my shop when you need quality goods!"
                ],
                "topics": ["trade", "goods", "prices", "competition"],
                "phrases": {
                    "trade": [
                        "Trade routes have been disrupted by the troubles in the east.",
                        "I get my goods from all over. Quality is my priority.",
                        "A good merchant knows both product and customer."
                    ],
                    "goods": [
                        "This item came all the way from across the sea.",
                        "You won't find better quality anywhere in the region.",
                        "I personally inspect everything I sell."
                    ],
                    "prices": [
                        "These prices are fair - I have to eat too, you know.",
                        "I could go lower, but the quality would suffer.",
                        "The price reflects the difficulty in acquiring such fine items."
                    ],
                    "competition": [
                        "That shop down the street? Inferior goods at inflated prices.",
                        "My competitors cut corners. I never do.",
                        "I've been in business here longer than anyone else."
                    ]
                }
            },
            "farmer": {
                "greetings": [
                    "Good day to you. What brings you to these parts?",
                    "Welcome, stranger. Don't see many unfamiliar faces around here.",
                    "Well met. Taking a break from the fields to chat a bit."
                ],
                "farewells": [
                    "Daylight's burning. Best get back to it.",
                    "Good talking with you. The crops won't tend themselves.",
                    "Stop by again if you're passing through."
                ],
                "topics": ["crops", "weather", "harvest", "land"],
                "phrases": {
                    "crops": [
                        "The wheat's coming in strong this season.",
                        "Pests got into the eastern field. It's always something.",
                        "You can tell a lot about the coming winter by how the crops grow in summer."
                    ],
                    "weather": [
                        "We could use some rain soon. The soil's getting dry.",
                        "Too much rain now would ruin the harvest.",
                        "You learn to read the skies when your livelihood depends on it."
                    ],
                    "harvest": [
                        "Harvest time is hard work but rewarding.",
                        "Everyone pitches in when it's time to bring in the crops.",
                        "A good harvest means a comfortable winter."
                    ],
                    "land": [
                        "This land's been in my family for generations.",
                        "Good soil is worth more than gold to a farmer.",
                        "They're not making any more land, that's what my father always said."
                    ]
                }
            },
            "guard": {
                "greetings": [
                    "Halt. State your business.",
                    "Keep your weapons sheathed while in town.",
                    "Eyes open, stranger. I'm watching you."
                ],
                "farewells": [
                    "Move along now, citizen.",
                    "Keep out of trouble, and we'll get along fine.",
                    "Remember: I've got my eye on you."
                ],
                "topics": ["security", "crime", "patrol", "threats"],
                "phrases": {
                    "security": [
                        "My job is to keep the peace. Don't make that difficult.",
                        "These streets are safe because we make them that way.",
                        "Follow the laws, and you'll have no trouble from me."
                    ],
                    "crime": [
                        "Been some thefts in the market district lately.",
                        "The captain's cracking down on smuggling this month.",
                        "Report any suspicious activity immediately."
                    ],
                    "patrol": [
                        "I walk these streets every day. I notice everything.",
                        "Night patrol is the worst shift, especially in winter.",
                        "Twenty years on patrol, and I still find surprises."
                    ],
                    "threats": [
                        "Bandits have been spotted on the north road.",
                        "It's not just thieves we worry about these days.",
                        "Stay alert, especially after dark."
                    ]
                }
            },
            "innkeeper": {
                "greetings": [
                    "Welcome to my establishment! Can I offer you a room or a meal?",
                    "Come in, come in! Rest your weary feet by the fire.",
                    "A new face! What brings you to our humble inn?"
                ],
                "farewells": [
                    "Safe travels, friend. Our door is always open to you.",
                    "Rest well. Breakfast is served at dawn.",
                    "Any friend of yours is welcome here too."
                ],
                "topics": ["accommodations", "food", "guests", "gossip"],
                "phrases": {
                    "accommodations": [
                        "Clean sheets and a solid roof - best in town.",
                        "The room upstairs has a view of the square.",
                        "We're full when the traders come through, so book ahead."
                    ],
                    "food": [
                        "The stew is my grandmother's recipe.",
                        "We get our ale from the local brewery. Freshest you'll find.",
                        "Cook's special tonight is herbed lamb. Mouthwatering."
                    ],
                    "guests": [
                        "All sorts pass through here. I've seen it all.",
                        "Had a nobleman stay last week. Tipped well.",
                        "I remember every face that walks through that door."
                    ],
                    "gossip": [
                        "You hear all sorts of things running an inn.",
                        "The mayor and the merchant guild are at odds again.",
                        "Travelers bring news from all over. Troubling times ahead, I fear."
                    ]
                }
            }
        }
        
        # Add a generic "commoner" option for any occupation not specifically defined
        commoner_dialogue = {
            "greetings": [
                "Hello there.",
                "Good day to you.",
                "Well met, stranger."
            ],
            "farewells": [
                "Farewell, then.",
                "Safe travels to you.",
                "May our paths cross again."
            ],
            "topics": ["weather", "local_news", "daily_life"],
            "phrases": {
                "weather": [
                    "Weather's been strange lately.",
                    "Hope the rain holds off until after the festival.",
                    "Cold night like this makes you appreciate a warm hearth."
                ],
                "local_news": [
                    "Not much happens around here, to be honest.",
                    "The council raised taxes again. Always taking, never giving.",
                    "They're rebuilding the old bridge finally."
                ],
                "daily_life": [
                    "Just trying to get by, same as everyone.",
                    "Work is hard, but it puts food on the table.",
                    "Been the same routine for years now."
                ]
            }
        }
        
        # Return occupation-specific dialogue or default to commoner
        return occupation_dialogue.get(occupation_type, commoner_dialogue)
    
    def _get_character_social_status(
        self,
        character_id: str
    ) -> float:
        """
        Calculate social status score for a character.
        
        Args:
            character_id: ID of the character
            
        Returns:
            Social status score (0.0-3.0, higher is higher status)
        """
        try:
            # Get character data
            character_data = self.population_manager.get_character(character_id)
            
            if not character_data:
                return 1.0  # Default average status
            
            # Base status from social class if available
            social_class = character_data.get("social_class", "commoner")
            
            base_status = {
                "nobility": 3.0,
                "aristocrat": 2.5,
                "wealthy": 2.0,
                "merchant": 1.5,
                "commoner": 1.0,
                "worker": 0.8,
                "poor": 0.5,
                "beggar": 0.2,
                "outcast": 0.1
            }.get(social_class, 1.0)
            
            # Adjust for occupation
            occupation = character_data.get("occupation", {}).get("type", "")
            occupation_modifier = {
                "ruler": 1.0,
                "noble": 0.8,
                "official": 0.5,
                "priest": 0.4,
                "guard_captain": 0.3,
                "merchant": 0.2,
                "artisan": 0.1,
                "guard": 0.1,
                "entertainer": 0.0,
                "farmer": -0.1,
                "laborer": -0.2,
                "servant": -0.3
            }.get(occupation, 0.0)
            
            # Adjust for wealth if available
            wealth = character_data.get("wealth", 50)  # Default average wealth
            wealth_modifier = (wealth - 50) / 100  # -0.5 to 0.5
            
            # Calculate final status
            status = base_status + occupation_modifier + wealth_modifier
            
            # Ensure within valid range
            return max(0.1, min(status, 3.0))
            
        except Exception as e:
            logger.error(f"Failed to calculate social status for character {character_id}: {e}")
            return 1.0  # Default average status
    
    def _get_most_notable_demographic(
        self,
        demographics: Dict[str, float]
    ) -> Optional[str]:
        """
        Get the most notable demographic characteristic worth mentioning.
        
        Args:
            demographics: Dictionary mapping demographic groups to percentages
            
        Returns:
            Most notable demographic feature or None if nothing notable
        """
        if not demographics:
            return None
            
        # If one group is very dominant (>70%)
        for group, percentage in demographics.items():
            if percentage > 70:
                return f"{group}"
        
        # If there's a diverse mix with no clear majority (<40%)
        max_percentage = max(demographics.values())
        if max_percentage < 40:
            groups = list(demographics.keys())[:3]  # Top 3 groups
            if len(groups) >= 3:
                return f"a diverse mix of {', '.join(groups)}"
            elif len(groups) == 2:
                return f"a mix of {' and '.join(groups)}"
        
        return None 