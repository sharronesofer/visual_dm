"""
Enhanced Loot-Skill Integration - Pure Business Logic
----------------------------------------------------
Enhanced integration between noncombat skills and the loot identification system.
Provides richer skill-based mechanics for item discovery, identification, and evaluation.
Pure business logic with no technical dependencies.
"""

from typing import Dict, List, Optional, Any, Tuple, Protocol
from enum import Enum
from dataclasses import dataclass

from backend.systems.character.models.character import Character
from backend.systems.character.services.skill_check_service import (
    skill_check_service, SkillCheckDifficulty, SkillCheckModifiers
)
from backend.systems.character.services.noncombat_skills import (
    noncombat_skill_service, PerceptionType, SocialInteractionType
)

# Import existing loot identification system
try:
    from backend.systems.loot.utils.identification_system import (
        TieredIdentificationSystem, IdentificationMethod, IdentificationResult
    )
    from backend.systems.loot.services.loot_manager import LootBusinessManager
except ImportError:
    # Fallback if loot system not available
    TieredIdentificationSystem = None
    IdentificationMethod = None
    IdentificationResult = None
    LootBusinessManager = None


class ItemDiscoveryMethod(Enum):
    """Methods for discovering hidden items."""
    PASSIVE_PERCEPTION = "passive_perception"
    ACTIVE_SEARCH = "active_search"
    INVESTIGATION = "investigation"
    SURVIVAL_TRACKING = "survival_tracking"
    ARCANE_DETECTION = "arcane_detection"
    MERCHANT_APPRAISAL = "merchant_appraisal"


class IdentificationSkillType(Enum):
    """Skills used for item identification."""
    APPRAISE = "appraise"
    ARCANA = "arcana"
    HISTORY = "history"
    INVESTIGATION = "investigation"
    NATURE = "nature"
    RELIGION = "religion"
    SURVIVAL = "survival"


@dataclass
class SkillBasedDiscovery:
    """Result of skill-based item discovery."""
    discovery_method: ItemDiscoveryMethod
    skill_check_result: Any
    items_found: List[Dict[str, Any]]
    additional_information: List[str]
    hidden_items_missed: List[Dict[str, Any]]
    environmental_clues: List[str]


@dataclass
class EnhancedIdentificationResult:
    """Enhanced identification result with skill details."""
    base_identification_result: Any
    skill_used: str
    skill_check_result: Any
    additional_properties_revealed: List[str]
    crafting_insights: List[str]
    historical_context: List[str]
    estimated_value_accuracy: float  # 0.0 to 1.0
    confidence_level: str


# Business Logic Protocols
class IdentificationEventPublisher(Protocol):
    """Protocol for publishing identification events"""
    
    def publish_identification_event(self, event_data: Dict[str, Any]) -> None:
        """Publish identification event"""
        ...


class EnhancedLootSkillService:
    """Enhanced service integrating skills with loot mechanics - Pure Business Logic."""
    
    def __init__(self, 
                 loot_manager: Optional[LootBusinessManager] = None,
                 identification_system: Optional[TieredIdentificationSystem] = None,
                 event_publisher: Optional[IdentificationEventPublisher] = None):
        self.loot_manager = loot_manager
        self.identification_system = identification_system
        self.event_publisher = event_publisher
        
        # Skill-to-item-type mappings for identification bonuses
        self.skill_item_bonuses = {
            "arcana": ["magical", "enchanted", "artifact", "wand", "staff", "scroll"],
            "nature": ["natural", "herb", "poison", "beast_part", "wood", "stone"],
            "religion": ["holy", "unholy", "divine", "cursed", "blessed", "relic"],
            "history": ["ancient", "artifact", "relic", "cultural", "noble"],
            "survival": ["tools", "weapons", "armor", "outdoor_gear", "provisions"],
            "investigation": ["mechanical", "trap", "device", "lock", "gear"],
            "appraise": ["gem", "jewelry", "art", "valuable", "trade_good"]
        }
        
        # Item discovery DCs by rarity and concealment
        self.discovery_dcs = {
            "common": {
                "obvious": 5,
                "hidden": 10,
                "well_hidden": 15,
                "secret": 20
            },
            "uncommon": {
                "obvious": 8,
                "hidden": 13,
                "well_hidden": 18,
                "secret": 23
            },
            "rare": {
                "obvious": 12,
                "hidden": 17,
                "well_hidden": 22,
                "secret": 27
            },
            "epic": {
                "obvious": 15,
                "hidden": 20,
                "well_hidden": 25,
                "secret": 30
            },
            "legendary": {
                "obvious": 18,
                "hidden": 23,
                "well_hidden": 28,
                "secret": 35
            }
        }
    
    def skill_based_item_discovery(
        self,
        character: Character,
        discovery_method: ItemDiscoveryMethod,
        location_data: Dict[str, Any],
        available_items: List[Dict[str, Any]],
        environmental_conditions: List[str] = None
    ) -> SkillBasedDiscovery:
        """
        Discover items using specific skill-based methods.
        
        Args:
            character: Character performing the discovery
            discovery_method: Method being used to discover items
            location_data: Information about the current location
            available_items: Items that might be found
            environmental_conditions: Environmental modifiers
            
        Returns:
            SkillBasedDiscovery result
        """
        if environmental_conditions is None:
            environmental_conditions = []
        
        # Determine skill and base mechanics based on discovery method
        skill_mapping = {
            ItemDiscoveryMethod.PASSIVE_PERCEPTION: "perception",
            ItemDiscoveryMethod.ACTIVE_SEARCH: "search",
            ItemDiscoveryMethod.INVESTIGATION: "investigation",
            ItemDiscoveryMethod.SURVIVAL_TRACKING: "survival",
            ItemDiscoveryMethod.ARCANE_DETECTION: "arcana",
            ItemDiscoveryMethod.MERCHANT_APPRAISAL: "appraise"
        }
        
        skill_name = skill_mapping.get(discovery_method, "perception")
        
        items_found = []
        items_missed = []
        additional_information = []
        environmental_clues = []
        
        # Handle passive perception differently
        if discovery_method == ItemDiscoveryMethod.PASSIVE_PERCEPTION:
            passive_score = noncombat_skill_service.get_passive_perception(
                character, environmental_conditions
            )
            
            # Check each item against passive perception
            for item in available_items:
                concealment = item.get("concealment_level", "obvious")
                rarity = item.get("rarity", "common")
                dc = self.discovery_dcs.get(rarity, {}).get(concealment, 15)
                
                if passive_score >= dc:
                    items_found.append(item)
                    if passive_score >= dc + 5:
                        additional_information.append(f"You immediately notice details about the {item.get('name', 'item')}")
                else:
                    items_missed.append(item)
            
            # Create mock skill check result for passive
            skill_check_result = type('PassiveResult', (), {
                'total_roll': passive_score,
                'success': len(items_found) > 0,
                'skill_name': 'perception',
                'description': 'Passive perception check'
            })()
        
        else:
            # Active skill checks
            modifiers = SkillCheckModifiers()
            
            # Apply environmental modifiers
            env_modifier = self._calculate_environmental_discovery_modifier(
                location_data, environmental_conditions, discovery_method
            )
            modifiers.circumstance_modifier += env_modifier
            
            # Determine difficulty based on best available item
            base_dc = 15
            if available_items:
                best_item = max(available_items, key=lambda x: self.discovery_dcs.get(x.get("rarity", "common"), {}).get(x.get("concealment_level", "obvious"), 15))
                concealment = best_item.get("concealment_level", "obvious")
                rarity = best_item.get("rarity", "common")
                base_dc = self.discovery_dcs.get(rarity, {}).get(concealment, 15)
            
            difficulty = SkillCheckDifficulty.from_dc(base_dc)
            
            # Make the skill check
            skill_check_result = skill_check_service.make_skill_check(
                character, skill_name, difficulty, modifiers
            )
            
            # Determine what was found based on the result
            for item in available_items:
                concealment = item.get("concealment_level", "obvious")
                rarity = item.get("rarity", "common")
                dc = self.discovery_dcs.get(rarity, {}).get(concealment, 15)
                
                if skill_check_result.total_roll >= dc:
                    items_found.append(item)
                    # Extra information for excellent rolls
                    if skill_check_result.total_roll >= dc + 10:
                        additional_information.append(f"You discover significant details about the {item.get('name', 'item')}")
                    elif skill_check_result.total_roll >= dc + 5:
                        additional_information.append(f"You notice interesting details about the {item.get('name', 'item')}")
                else:
                    items_missed.append(item)
        
        # Generate environmental clues based on the discovery method and results
        environmental_clues = self._generate_environmental_clues(
            discovery_method, location_data, items_found, skill_check_result
        )
        
        # Publish event if publisher available
        if self.event_publisher:
            event_data = {
                "event_type": "item.discovery",
                "character_id": character.id if hasattr(character, 'id') else 0,
                "discovery_method": discovery_method.value,
                "skill_used": skill_name,
                "items_found_count": len(items_found),
                "skill_check_total": getattr(skill_check_result, 'total_roll', 0),
                "location": location_data.get('name', 'Unknown Location')
            }
            self.event_publisher.publish_identification_event(event_data)
        
        return SkillBasedDiscovery(
            discovery_method=discovery_method,
            skill_check_result=skill_check_result,
            items_found=items_found,
            additional_information=additional_information,
            hidden_items_missed=items_missed,
            environmental_clues=environmental_clues
        )
    
    def enhanced_item_identification(
        self,
        character: Character,
        item: Dict[str, Any],
        identification_skill: IdentificationSkillType,
        time_spent_minutes: int = 10,
        use_tools: bool = False,
        environmental_conditions: List[str] = None
    ) -> EnhancedIdentificationResult:
        """
        Enhanced item identification using specific skills.
        
        Args:
            character: Character identifying the item
            item: Item to identify
            identification_skill: Skill being used for identification
            time_spent_minutes: Time spent on identification
            use_tools: Whether using identification tools
            environmental_conditions: Environmental factors
            
        Returns:
            EnhancedIdentificationResult with detailed information
        """
        if environmental_conditions is None:
            environmental_conditions = []
        
        skill_name = identification_skill.value
        
        # Calculate modifiers
        modifiers = SkillCheckModifiers()
        
        # Time modifiers
        if time_spent_minutes >= 30:
            modifiers.time_modifier = 2
        elif time_spent_minutes >= 60:
            modifiers.time_modifier = 4
        elif time_spent_minutes < 5:
            modifiers.time_modifier = -3
        
        # Tool bonus
        if use_tools:
            modifiers.equipment_bonus = 3
        
        # Skill-item synergy bonus
        if self._skill_has_item_synergy(skill_name, item):
            modifiers.circumstance_bonus = 5
        
        # Base identification check
        item_rarity = item.get("rarity", "common")
        base_dc = {
            "common": 10,
            "uncommon": 15,
            "rare": 20,
            "epic": 25,
            "legendary": 30
        }.get(item_rarity, 15)
        
        skill_check_result = skill_check_service.make_skill_check(
            character=character,
            skill_name=skill_name,
            dc=base_dc,
            modifiers=modifiers,
            description=f"Identifying {item.get('name', 'unknown item')} using {skill_name}"
        )
        
        # Use existing identification system if available
        base_identification_result = None
        if self.identification_system:
            try:
                base_identification_result, result_type, message = self.identification_system.identify_item_comprehensive(
                    item=item,
                    method=IdentificationMethod.SKILL_CHECK,
                    character_id=getattr(character, 'id', 0),
                    character_level=getattr(character, 'level', 1),
                    character_skill=skill_check_result.total_roll - 10  # Convert to skill bonus
                )
            except Exception as e:
                logger.error(f"Error with base identification system: {e}")
        
        # Generate skill-specific insights
        additional_properties = self._generate_skill_specific_insights(
            skill_name, item, skill_check_result
        )
        
        crafting_insights = self._generate_crafting_insights(
            skill_name, item, skill_check_result
        )
        
        historical_context = self._generate_historical_context(
            skill_name, item, skill_check_result
        )
        
        # Calculate value estimation accuracy
        value_accuracy = self._calculate_value_accuracy(
            skill_name, item, skill_check_result
        )
        
        # Determine confidence level
        confidence_level = self._determine_confidence_level(skill_check_result)
        
        return EnhancedIdentificationResult(
            base_identification_result=base_identification_result,
            skill_used=skill_name,
            skill_check_result=skill_check_result,
            additional_properties_revealed=additional_properties,
            crafting_insights=crafting_insights,
            historical_context=historical_context,
            estimated_value_accuracy=value_accuracy,
            confidence_level=confidence_level
        )
    
    def skill_based_item_evaluation(
        self,
        character: Character,
        item: Dict[str, Any],
        evaluation_purpose: str = "general"
    ) -> Dict[str, Any]:
        """
        Evaluate an item for specific purposes using appropriate skills.
        
        Args:
            character: Character evaluating the item
            item: Item to evaluate
            evaluation_purpose: Purpose of evaluation (trade, combat, crafting, etc.)
            
        Returns:
            Evaluation results
        """
        results = {}
        
        # Trade value evaluation
        if evaluation_purpose in ["trade", "general"]:
            appraise_result = skill_check_service.make_skill_check(
                character=character,
                skill_name="appraise",
                dc=10 + (item.get("rarity_bonus", 0) * 3),
                description=f"Appraising {item.get('name', 'item')} for trade value"
            )
            
            if appraise_result.success:
                # Accurate value assessment
                accuracy = min(0.95, 0.5 + (appraise_result.degree_of_success * 0.05))
                base_value = item.get("value", 100)
                estimated_value = int(base_value * accuracy)
                
                results["trade_evaluation"] = {
                    "estimated_value": estimated_value,
                    "accuracy": accuracy,
                    "confidence": "High" if appraise_result.degree_of_success >= 10 else "Medium",
                    "market_insights": self._generate_market_insights(item, appraise_result)
                }
        
        # Combat utility evaluation
        if evaluation_purpose in ["combat", "general"]:
            if item.get("type") in ["weapon", "armor", "shield"]:
                investigation_result = skill_check_service.make_skill_check(
                    character=character,
                    skill_name="investigation",
                    dc=12,
                    description=f"Evaluating {item.get('name', 'item')} for combat effectiveness"
                )
                
                results["combat_evaluation"] = {
                    "effectiveness_rating": self._calculate_combat_effectiveness(item, investigation_result),
                    "tactical_advantages": self._identify_tactical_advantages(item, investigation_result),
                    "weaknesses": self._identify_weaknesses(item, investigation_result)
                }
        
        # Magical properties evaluation
        if item.get("magical", False) or item.get("type") == "magical":
            arcana_result = skill_check_service.make_skill_check(
                character=character,
                skill_name="arcana",
                dc=15,
                description=f"Analyzing magical properties of {item.get('name', 'item')}"
            )
            
            results["magical_evaluation"] = {
                "magical_school": self._identify_magical_school(item, arcana_result),
                "power_level": self._assess_magical_power(item, arcana_result),
                "magical_risks": self._identify_magical_risks(item, arcana_result),
                "activation_methods": self._identify_activation_methods(item, arcana_result)
            }
        
        return results
    
    # === UTILITY METHODS ===
    
    def _skill_has_item_synergy(self, skill_name: str, item: Dict[str, Any]) -> bool:
        """Check if a skill has synergy with an item type."""
        item_tags = item.get("tags", [])
        item_type = item.get("type", "")
        
        synergy_items = self.skill_item_bonuses.get(skill_name, [])
        
        return any(tag in synergy_items for tag in item_tags) or item_type in synergy_items
    
    def _calculate_environmental_discovery_modifier(
        self,
        location_data: Dict[str, Any],
        environmental_conditions: List[str],
        discovery_method: ItemDiscoveryMethod
    ) -> int:
        """Calculate environmental modifiers for item discovery."""
        modifier = 0
        
        # Location-based modifiers
        location_type = location_data.get("type", "")
        
        if discovery_method == ItemDiscoveryMethod.SURVIVAL_TRACKING:
            if location_type in ["forest", "wilderness"]:
                modifier += 2
            elif location_type in ["urban", "indoor"]:
                modifier -= 3
        
        # Environmental condition modifiers
        for condition in environmental_conditions:
            if condition == "dim_light" and discovery_method != ItemDiscoveryMethod.PASSIVE_PERCEPTION:
                modifier -= 2
            elif condition == "darkness":
                modifier -= 5
            elif condition == "bright_light":
                modifier += 1
        
        return modifier
    
    def _generate_environmental_clues(
        self,
        discovery_method: ItemDiscoveryMethod,
        location_data: Dict[str, Any],
        items_found: List[Dict[str, Any]],
        skill_check_result: Any
    ) -> List[str]:
        """Generate environmental clues based on discovery method and success."""
        clues = []
        
        if not hasattr(skill_check_result, 'success') or not skill_check_result.success:
            return clues
        
        if discovery_method == ItemDiscoveryMethod.SURVIVAL_TRACKING:
            clues.extend([
                "You notice signs of recent activity in the area",
                "Animal tracks suggest this location is frequently visited",
                "The vegetation shows signs of disturbance"
            ])
        
        elif discovery_method == ItemDiscoveryMethod.INVESTIGATION:
            clues.extend([
                "The dust patterns suggest items were recently moved",
                "You detect faint traces of different materials",
                "The arrangement of objects seems intentional"
            ])
        
        elif discovery_method == ItemDiscoveryMethod.ARCANE_DETECTION:
            clues.extend([
                "You sense residual magical energy in the area",
                "The ambient magical field fluctuates near certain locations",
                "Arcane symbols are subtly carved into nearby surfaces"
            ])
        
        return clues[:3]  # Limit to 3 clues
    
    def _generate_skill_specific_insights(
        self,
        skill_name: str,
        item: Dict[str, Any],
        skill_check_result: Any
    ) -> List[str]:
        """Generate insights specific to the skill used for identification."""
        insights = []
        
        if not hasattr(skill_check_result, 'success') or not skill_check_result.success:
            return insights
        
        if skill_name == "arcana":
            insights.extend([
                "You understand the magical principles behind this item",
                "The enchantment pattern suggests a specific magical tradition",
                "You can sense the item's magical resonance frequency"
            ])
        
        elif skill_name == "history":
            insights.extend([
                "This item bears the craftsmanship marks of a specific era",
                "You recognize the cultural significance of this design",
                "Historical records mention similar items in ancient texts"
            ])
        
        elif skill_name == "nature":
            insights.extend([
                "The natural materials show signs of specific environmental origins",
                "You identify rare components that enhance the item's properties",
                "The crafting method respects natural growth patterns"
            ])
        
        return insights[:2]  # Limit insights
    
    def _generate_crafting_insights(
        self,
        skill_name: str,
        item: Dict[str, Any],
        skill_check_result: Any
    ) -> List[str]:
        """Generate crafting-related insights."""
        insights = []
        
        if hasattr(skill_check_result, 'degree_of_success') and skill_check_result.degree_of_success >= 5:
            insights.extend([
                "You understand the crafting techniques used to create this item",
                "You identify the quality of materials and workmanship",
                "You can estimate the time and skill required to replicate this"
            ])
        
        return insights
    
    def _generate_historical_context(
        self,
        skill_name: str,
        item: Dict[str, Any],
        skill_check_result: Any
    ) -> List[str]:
        """Generate historical context for the item."""
        context = []
        
        if skill_name in ["history", "religion", "arcana"]:
            if hasattr(skill_check_result, 'success') and skill_check_result.success:
                context.extend([
                    "This item has historical significance in its region of origin",
                    "Similar items were used during important historical events",
                    "The design reflects the aesthetic preferences of its era"
                ])
        
        return context[:2]
    
    def _calculate_value_accuracy(
        self,
        skill_name: str,
        item: Dict[str, Any],
        skill_check_result: Any
    ) -> float:
        """Calculate how accurate the value estimation is."""
        base_accuracy = 0.5
        
        if skill_name == "appraise":
            base_accuracy = 0.8
        elif skill_name in ["investigation", "history"]:
            base_accuracy = 0.6
        
        if hasattr(skill_check_result, 'degree_of_success'):
            accuracy_bonus = skill_check_result.degree_of_success * 0.02
            return min(0.95, base_accuracy + accuracy_bonus)
        
        return base_accuracy
    
    def _determine_confidence_level(self, skill_check_result: Any) -> str:
        """Determine confidence level based on skill check result."""
        if not hasattr(skill_check_result, 'degree_of_success'):
            return "Low"
        
        if skill_check_result.degree_of_success >= 15:
            return "Very High"
        elif skill_check_result.degree_of_success >= 10:
            return "High"
        elif skill_check_result.degree_of_success >= 5:
            return "Medium"
        else:
            return "Low"
    
    def _generate_market_insights(self, item: Dict[str, Any], appraise_result: Any) -> List[str]:
        """Generate market-related insights for trade."""
        insights = []
        
        if hasattr(appraise_result, 'degree_of_success') and appraise_result.degree_of_success >= 5:
            insights.extend([
                "This item would be particularly valuable to collectors",
                "Demand for this type of item fluctuates seasonally",
                "Certain merchants specialize in items like this"
            ])
        
        return insights
    
    def _calculate_combat_effectiveness(self, item: Dict[str, Any], investigation_result: Any) -> str:
        """Calculate combat effectiveness rating."""
        base_rating = item.get("combat_rating", "Average")
        
        if hasattr(investigation_result, 'degree_of_success'):
            if investigation_result.degree_of_success >= 10:
                return "Excellent"
            elif investigation_result.degree_of_success >= 5:
                return "Good"
        
        return base_rating
    
    def _identify_tactical_advantages(self, item: Dict[str, Any], investigation_result: Any) -> List[str]:
        """Identify tactical advantages of the item."""
        advantages = []
        
        if hasattr(investigation_result, 'success') and investigation_result.success:
            item_type = item.get("type", "")
            
            if item_type == "weapon":
                advantages.extend([
                    "Well-balanced for quick strikes",
                    "Grip designed for extended combat",
                    "Weight distribution favors offensive techniques"
                ])
            elif item_type == "armor":
                advantages.extend([
                    "Joint protection allows full range of motion",
                    "Weight distribution minimizes fatigue",
                    "Design deflects strikes to non-vital areas"
                ])
        
        return advantages[:2]
    
    def _identify_weaknesses(self, item: Dict[str, Any], investigation_result: Any) -> List[str]:
        """Identify potential weaknesses of the item."""
        weaknesses = []
        
        if hasattr(investigation_result, 'degree_of_success') and investigation_result.degree_of_success >= 5:
            weaknesses.extend([
                "Shows signs of wear that could affect performance",
                "Material composition has some vulnerabilities",
                "Design has minor flaws that could be exploited"
            ])
        
        return weaknesses[:1]
    
    def _identify_magical_school(self, item: Dict[str, Any], arcana_result: Any) -> str:
        """Identify the magical school or tradition."""
        schools = ["Evocation", "Abjuration", "Transmutation", "Enchantment", "Divination", "Illusion", "Necromancy", "Conjuration"]
        
        if hasattr(arcana_result, 'success') and arcana_result.success:
            # Simplified - in real implementation would be based on item properties
            return schools[hash(item.get("name", "")) % len(schools)]
        
        return "Unknown"
    
    def _assess_magical_power(self, item: Dict[str, Any], arcana_result: Any) -> str:
        """Assess the magical power level of the item."""
        if hasattr(arcana_result, 'degree_of_success'):
            if arcana_result.degree_of_success >= 15:
                return "Very High"
            elif arcana_result.degree_of_success >= 10:
                return "High"
            elif arcana_result.degree_of_success >= 5:
                return "Moderate"
        
        return "Low"
    
    def _identify_magical_risks(self, item: Dict[str, Any], arcana_result: Any) -> List[str]:
        """Identify potential magical risks."""
        risks = []
        
        if item.get("cursed", False):
            risks.append("Item may be cursed - use with caution")
        
        if hasattr(arcana_result, 'degree_of_success') and arcana_result.degree_of_success >= 5:
            risks.extend([
                "Magical energy could interact unpredictably with other magic",
                "Overuse might drain the item's magical properties"
            ])
        
        return risks
    
    def _identify_activation_methods(self, item: Dict[str, Any], arcana_result: Any) -> List[str]:
        """Identify methods to activate the item's magical properties."""
        methods = []
        
        if hasattr(arcana_result, 'success') and arcana_result.success:
            methods.extend([
                "Command word activation",
                "Physical gesture required",
                "Touch activation"
            ])
        
        return methods[:2]

# Global service instance
enhanced_loot_skill_service = EnhancedLootSkillService() 