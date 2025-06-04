"""
Procedural Rumor Content Generator

This module provides sophisticated rumor content generation using templates,
variables, and contextual substitution to create varied and believable rumors.
"""

import random
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from backend.systems.rumor.utils.rumor_rules import get_rumor_config


class RumorCategory(Enum):
    """Categories of rumors for template selection"""
    POLITICAL = "political"
    MILITARY = "military" 
    ECONOMIC = "economic"
    SOCIAL = "social"
    SUPERNATURAL = "supernatural"
    CRIME = "crime"
    DISASTER = "disaster"
    ROMANCE = "romance"
    TRADE = "trade"
    RELIGION = "religion"


@dataclass
class RumorContext:
    """Context information for rumor generation"""
    location: Optional[str] = None
    faction: Optional[str] = None
    time_period: Optional[str] = None
    season: Optional[str] = None
    current_events: Optional[List[str]] = None
    prominent_figures: Optional[List[str]] = None
    economic_state: Optional[str] = None
    political_climate: Optional[str] = None


class ProceduralRumorGenerator:
    """Generates varied rumor content using templates and smart substitution"""
    
    def __init__(self):
        self.config = get_rumor_config()
        self.templates = self._load_rumor_templates()
        self.variables = self._load_rumor_variables()
        
    def _load_rumor_templates(self) -> Dict[str, List[str]]:
        """Load rumor templates organized by category"""
        return {
            RumorCategory.POLITICAL.value: [
                "The {ruler} is secretly planning to {political_action} the {target_group}",
                "{political_figure} was seen meeting with {foreign_entity} at {secret_location}",
                "New laws will soon {legal_change} all {affected_group} in the {region}",
                "The {government_body} is hiding the truth about {political_scandal}",
                "{noble_title} {noble_name} is plotting to {political_scheme} against {rival}",
                "Secret documents reveal {ruler} plans to {policy_change} within {timeframe}",
                "A rebellion is brewing among the {discontented_group} in {region}",
                "{political_figure} has been {corruption_type} public funds for {corrupt_purpose}"
            ],
            
            RumorCategory.MILITARY.value: [
                "The {enemy_faction} is amassing troops near {strategic_location}",
                "{military_leader} plans to attack {target_location} at {attack_time}",
                "New weapons have been spotted in the {military_unit} arsenal",
                "Spies from {foreign_power} have infiltrated the {local_institution}",
                "The garrison at {fortress_name} is {military_state} and vulnerable",
                "{war_hero} was {military_fate} during the last {military_engagement}",
                "Secret military supplies are being moved through {trade_route}",
                "Mercenary companies are being hired for {mysterious_purpose}"
            ],
            
            RumorCategory.ECONOMIC.value: [
                "Prices of {commodity} will {price_change} dramatically {timeframe}",
                "The {merchant_guild} is {business_action} to control {trade_good} trade",
                "{wealthy_merchant} has {financial_fate} and lost their {asset_type}",
                "A new trade route through {route_location} will {economic_impact} local prices",
                "The {currency_name} is being {currency_manipulation} by {economic_actor}",
                "{trade_good} shortages are caused by {shortage_reason} in {affected_region}",
                "Secret contracts between {trader_a} and {trader_b} will {market_effect}",
                "The {economic_institution} is {financial_scandal} customer {asset_type}"
            ],
            
            RumorCategory.SOCIAL.value: [
                "{social_figure} was caught {scandalous_behavior} with {scandal_target}",
                "The {social_event} will be {event_disruption} by {disruptive_force}",
                "{community_leader} is secretly {hidden_identity} from {origin_place}",
                "A {social_phenomenon} is spreading among {affected_demographic} in {location}",
                "{family_name} and {rival_family} are {family_conflict} over {conflict_cause}",
                "The {religious_figure} has been {religious_scandal} sacred {religious_object}",
                "{social_institution} will soon {institutional_change} all {member_group}",
                "Strange {social_behavior} has been observed among {behavioral_group}"
            ],
            
            RumorCategory.SUPERNATURAL.value: [
                "{magical_entity} has been sighted near {mystical_location}",
                "The {magical_artifact} is said to {magical_effect} anyone who {interaction_type}",
                "{supernatural_being} is {supernatural_action} people in {affected_area}",
                "Ancient {mystical_phenomenon} are appearing around {sacred_site}",
                "The {magical_practitioner} has discovered {magical_secret} in {hidden_place}",
                "{cursed_object} is bringing {supernatural_misfortune} to {victim_group}",
                "Strange {magical_occurrence} happen every {time_pattern} at {specific_location}",
                "{legendary_creature} has awakened from {resting_place} and seeks {creature_goal}"
            ],
            
            RumorCategory.CRIME.value: [
                "The {criminal_group} is planning to {criminal_action} the {target_establishment}",
                "{criminal_figure} has been {criminal_fate} by {law_enforcement}",
                "Stolen {valuable_item} from {theft_location} is hidden in {hiding_place}",
                "A {crime_type} ring operates from {criminal_base} targeting {victim_type}",
                "{authority_figure} is secretly {corruption_type} with {criminal_organization}",
                "The {recent_crime} was actually {crime_truth} not what people believe",
                "{witness_type} saw {criminal_activity} near {crime_scene} at {crime_time}",
                "Evidence of {major_crime} has been {evidence_state} by {evidence_actor}"
            ]
        }
    
    def _load_rumor_variables(self) -> Dict[str, List[str]]:
        """Load variable substitutions for template filling"""
        return {
            # Political Variables
            "ruler": ["the king", "the queen", "the duke", "the regent", "the chancellor"],
            "political_figure": ["Lord Blackwood", "Lady Silverton", "Count Redmane", "Baron Ashford"],
            "political_action": ["exile", "tax heavily", "conscript", "redistribute land from"],
            "target_group": ["merchants", "farmers", "nobles", "clergy", "foreigners"],
            "foreign_entity": ["enemy spies", "foreign diplomats", "mysterious strangers"],
            "secret_location": ["the old mill", "midnight in the ruins", "the abandoned tower"],
            "legal_change": ["restrict", "grant new rights to", "heavily tax", "conscript"],
            "government_body": ["the council", "the senate", "the royal court"],
            "political_scandal": ["missing tax revenue", "illegal land seizures", "secret treaties"],
            
            # Military Variables  
            "enemy_faction": ["the Northern Alliance", "Crimson Raiders", "Iron Legion"],
            "military_leader": ["General Ironside", "Commander Steelhart", "Captain Bloodaxe"],
            "target_location": ["Fort Whitestone", "the Capital", "the Harbor District"],
            "attack_time": ["dawn", "the next full moon", "winter's end"],
            "military_unit": ["Royal Guard", "City Watch", "Border Patrol"],
            "foreign_power": ["the Eastern Empire", "Shadow Cult", "Merchant Princes"],
            "local_institution": ["the barracks", "the council chambers", "the treasury"],
            "military_state": ["understaffed", "poorly supplied", "demoralized"],
            
            # Economic Variables
            "commodity": ["grain", "iron", "salt", "wool", "spices"],
            "price_change": ["increase", "decrease", "fluctuate", "stabilize"],
            "timeframe": ["next month", "before winter", "after the harvest"],
            "merchant_guild": ["Traders Union", "Golden Coin Society", "Merchant's Circle"],
            "business_action": ["conspiring", "negotiating", "planning"],
            "trade_good": ["silk", "weapons", "food", "luxury goods"],
            "wealthy_merchant": ["Master Goldweaver", "Lady Coinsworth", "Baron Tradeheart"],
            "financial_fate": ["gone bankrupt", "been robbed", "lost a fortune"],
            
            # Social Variables
            "social_figure": ["Lady Roseheart", "Sir Charming", "Madam Peacock"],
            "scandalous_behavior": ["dancing inappropriately", "gambling", "drinking heavily"],
            "scandal_target": ["a married person", "someone beneath their station", "their rival"],
            "social_event": ["harvest festival", "royal wedding", "market day"],
            "event_disruption": ["disrupted", "canceled", "moved"],
            "community_leader": ["the village elder", "the guild master", "the town mayor"],
            
            # Supernatural Variables
            "magical_entity": ["a dragon", "an ancient spirit", "a powerful wizard"],
            "mystical_location": ["the Whispering Woods", "Crystal Cave", "the Haunted Ruins"],
            "magical_artifact": ["the Crown of Souls", "Bleeding Sword", "Mirror of Truth"],
            "magical_effect": ["curse", "grant power to", "reveal the secrets of"],
            "supernatural_being": ["a vampire", "a shape-shifter", "a demon"],
            "supernatural_action": ["stalking", "possessing", "blessing"],
            
            # Crime Variables
            "criminal_group": ["the Thieves Guild", "Shadow Brotherhood", "Cutthroat Gang"],
            "criminal_action": ["rob", "burn down", "kidnap someone from"],
            "target_establishment": ["royal treasury", "merchant warehouse", "noble's manor"],
            "criminal_figure": ["Black Jack", "the Hooded Thief", "Scarface Pete"],
            "criminal_fate": ["captured", "killed", "gone into hiding"],
            "law_enforcement": ["the city guard", "royal investigators", "bounty hunters"],
            
            # Time and Location Variables
            "time_pattern": ["full moon", "midnight", "dawn", "sunset"],
            "specific_location": ["the old cemetery", "market square", "the docks"],
            "affected_area": ["the poor district", "noble quarter", "the countryside"],
            "region": ["the northern provinces", "eastern territories", "the capital region"]
        }
    
    def generate_rumor(
        self, 
        category: Optional[RumorCategory] = None,
        context: Optional[RumorContext] = None,
        severity: str = "moderate"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a procedural rumor with context-aware content
        
        Returns:
            Tuple of (rumor_content, metadata)
        """
        # Select category
        if category is None:
            category = random.choice(list(RumorCategory))
        
        # Get templates for category
        category_templates = self.templates.get(category.value, [])
        if not category_templates:
            category = RumorCategory.SOCIAL  # Fallback
            category_templates = self.templates[category.value]
        
        # Select template
        template = random.choice(category_templates)
        
        # Apply context-aware variable selection
        variables = self._get_contextual_variables(context, category)
        
        # Fill template with variables
        content = self._fill_template(template, variables)
        
        # Apply severity-based modifications
        content = self._apply_severity_modifications(content, severity)
        
        # Create metadata
        metadata = {
            "category": category.value,
            "template_used": template,
            "variables_used": {var: val for var, val in variables.items() if f"{{{var}}}" in template},
            "generation_method": "procedural_template",
            "context_applied": context is not None
        }
        
        return content, metadata
    
    def _get_contextual_variables(
        self, 
        context: Optional[RumorContext], 
        category: RumorCategory
    ) -> Dict[str, str]:
        """Select variables based on context"""
        variables = {}
        
        for var_name, var_options in self.variables.items():
            if context:
                # Apply context-aware selection
                selected = self._select_contextual_variable(
                    var_name, var_options, context, category
                )
            else:
                # Random selection
                selected = random.choice(var_options)
            
            variables[var_name] = selected
        
        return variables
    
    def _select_contextual_variable(
        self,
        var_name: str,
        options: List[str],
        context: RumorContext,
        category: RumorCategory
    ) -> str:
        """Select variable based on context"""
        
        # Location-based selection
        if context.location and var_name in ["specific_location", "target_location"]:
            location_influenced = [opt for opt in options if context.location.lower() in opt.lower()]
            if location_influenced:
                return random.choice(location_influenced)
        
        # Faction-based selection
        if context.faction and var_name in ["enemy_faction", "foreign_power"]:
            # Avoid self-references
            faction_excluded = [opt for opt in options if context.faction.lower() not in opt.lower()]
            if faction_excluded:
                return random.choice(faction_excluded)
        
        # Economic state influence
        if context.economic_state and var_name in ["price_change", "financial_fate"]:
            if context.economic_state == "recession":
                negative_options = [opt for opt in options if any(neg in opt for neg in ["decrease", "lost", "bankrupt"])]
                if negative_options:
                    return random.choice(negative_options)
        
        # Political climate influence
        if context.political_climate and var_name in ["political_action", "legal_change"]:
            if context.political_climate == "tense":
                harsh_options = [opt for opt in options if any(harsh in opt for harsh in ["exile", "restrict", "tax heavily"])]
                if harsh_options:
                    return random.choice(harsh_options)
        
        # Default random selection
        return random.choice(options)
    
    def _fill_template(self, template: str, variables: Dict[str, str]) -> str:
        """Fill template with variables"""
        content = template
        
        # Find all placeholder variables in template
        placeholders = re.findall(r'\{([^}]+)\}', template)
        
        for placeholder in placeholders:
            if placeholder in variables:
                # Replace placeholder with variable
                content = content.replace(f"{{{placeholder}}}", variables[placeholder])
            else:
                # Generate fallback for unknown placeholder
                fallback = self._generate_fallback_variable(placeholder)
                content = content.replace(f"{{{placeholder}}}", fallback)
        
        return content
    
    def _generate_fallback_variable(self, placeholder: str) -> str:
        """Generate fallback content for unknown placeholders"""
        fallbacks = {
            "unknown_person": "someone",
            "unknown_place": "somewhere",
            "unknown_thing": "something",
            "unknown_action": "doing something",
            "unknown_time": "soon"
        }
        
        # Try to categorize the placeholder
        if any(person_word in placeholder for person_word in ["person", "figure", "leader", "name"]):
            return "someone important"
        elif any(place_word in placeholder for place_word in ["location", "place", "area", "region"]):
            return "somewhere significant"
        elif any(time_word in placeholder for time_word in ["time", "when", "period"]):
            return "soon"
        elif any(action_word in placeholder for action_word in ["action", "doing", "activity"]):
            return "something suspicious"
        else:
            return "something"
    
    def _apply_severity_modifications(self, content: str, severity: str) -> str:
        """Apply severity-based content modifications"""
        severity_modifiers = {
            "trivial": {
                "prefix": ["I heard ", "Someone mentioned ", "Word is "],
                "suffix": [", or so they say", ", though it might not be true", ", but who knows"]
            },
            "minor": {
                "prefix": ["People are saying ", "There's talk that ", "I've heard "],
                "suffix": [", apparently", ", from what I understand", ""]
            },
            "moderate": {
                "prefix": ["", "They say ", "Word has it that "],
                "suffix": ["", ", according to reliable sources", ", or so I'm told"]
            },
            "major": {
                "prefix": ["", "It's confirmed that ", "Multiple sources report "],
                "suffix": ["", ", and it's causing quite a stir", ", which explains recent events"]
            },
            "critical": {
                "prefix": ["URGENT: ", "Breaking news: ", "Confirmed reports state "],
                "suffix": [" - this changes everything", " - immediate action required", " - the implications are staggering"]
            }
        }
        
        modifiers = severity_modifiers.get(severity, severity_modifiers["moderate"])
        
        prefix = random.choice(modifiers["prefix"]) if modifiers["prefix"] else ""
        suffix = random.choice(modifiers["suffix"]) if modifiers["suffix"] else ""
        
        return f"{prefix}{content}{suffix}"
    
    def generate_rumor_batch(
        self, 
        count: int,
        context: Optional[RumorContext] = None,
        category_weights: Optional[Dict[RumorCategory, float]] = None
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Generate multiple rumors with optional category weighting"""
        
        if category_weights is None:
            # Default weights
            category_weights = {cat: 1.0 for cat in RumorCategory}
        
        rumors = []
        
        for _ in range(count):
            # Weighted category selection
            categories = list(category_weights.keys())
            weights = list(category_weights.values())
            category = random.choices(categories, weights=weights)[0]
            
            rumor, metadata = self.generate_rumor(category, context)
            rumors.append((rumor, metadata))
        
        return rumors
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """Get statistics about available templates"""
        stats = {
            "total_templates": sum(len(templates) for templates in self.templates.values()),
            "categories": len(self.templates),
            "templates_per_category": {
                category: len(templates) 
                for category, templates in self.templates.items()
            },
            "total_variables": len(self.variables),
            "variables_per_type": {
                var_name: len(options) 
                for var_name, options in self.variables.items()
            }
        }
        
        return stats


# Factory function
def create_procedural_rumor_generator() -> ProceduralRumorGenerator:
    """Create procedural rumor generator instance"""
    return ProceduralRumorGenerator() 