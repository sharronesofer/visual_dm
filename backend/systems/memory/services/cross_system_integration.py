"""
Cross-System Integration Service for Memory-Driven Behavior
----------------------------------------------------------

This service provides integration points between the memory system and other
game systems (economy, factions, combat, social) to ensure memory-driven
behavior affects gameplay across all domains.

Integration Points:
- Economy: Trade pricing, willingness to trade, merchant reputation
- Factions: Political bias, loyalty shifts, diplomatic stance
- Combat: Combat behavior, retreat thresholds, ally/enemy recognition
- Social: Relationship dynamics, trust networks, rumor propagation
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import os
import json

from backend.systems.memory.services.memory_behavior_influence import (
    MemoryBehaviorInfluenceService, 
    BehaviorModifier, 
    BehaviorInfluenceType,
    TrustCalculation
)
from backend.systems.memory.services.memory_manager_core import MemoryManager

logger = logging.getLogger(__name__)


@dataclass
class EconomicBehaviorModification:
    """Economic behavior modifications from memory analysis"""
    base_price_modifier: float  # Multiply base prices by this value
    trade_willingness: float  # 0.0 to 1.0 willingness to trade
    reputation_bonus: float  # Reputation modifier for this trader
    preferred_customers: List[str]  # Entity IDs of preferred customers
    blacklisted_customers: List[str]  # Entity IDs to refuse service
    risk_premium: float  # Additional cost due to perceived risk


@dataclass
class FactionBehaviorModification:
    """Faction-related behavior modifications from memory analysis"""
    faction_loyalties: Dict[str, float]  # faction_id -> loyalty (-1.0 to 1.0)
    diplomatic_stance: Dict[str, str]  # faction_id -> stance (hostile, neutral, friendly, allied)
    political_bias: float  # General political alignment modifier
    rebellion_likelihood: float  # 0.0 to 1.0 chance of turning against current faction
    influence_resistance: float  # Resistance to faction propaganda/influence


@dataclass
class CombatBehaviorModification:
    """Combat behavior modifications from memory analysis"""
    aggression_modifier: float  # Combat aggression multiplier
    flee_threshold: float  # Health percentage to flee at
    ally_recognition: Dict[str, float]  # entity_id -> trust level for combat allies
    enemy_priority: Dict[str, float]  # entity_id -> priority targeting (higher = priority)
    combat_caution: float  # General caution level in combat
    berserker_triggers: List[str]  # Conditions that trigger berserker rage


@dataclass
class SocialBehaviorModification:
    """Social behavior modifications from memory analysis"""
    social_openness: float  # 0.0 to 1.0 willingness to engage socially
    conversation_topics: Dict[str, float]  # topic -> enthusiasm (-1.0 to 1.0)
    relationship_priorities: Dict[str, float]  # entity_id -> relationship priority
    rumor_credibility: Dict[str, float]  # entity_id -> how much to believe their rumors
    social_influence: float  # How much this NPC influences others


class MemoryCrossSystemIntegrator:
    """
    Integrates memory-driven behavior modifications with other game systems.
    
    This service acts as a bridge between the memory system and other
    systems that need to respond to memory-driven behavioral changes.
    """
    
    def __init__(self, memory_influence_service: MemoryBehaviorInfluenceService):
        self.memory_influence_service = memory_influence_service
        self.entity_id = memory_influence_service.entity_id
        self.entity_type = memory_influence_service.entity_type
    
    async def get_economic_behavior_modifications(self, context: Optional[str] = None) -> EconomicBehaviorModification:
        """
        Generate economic behavior modifications based on memory analysis.
        
        Uses JSON configuration for price modifiers and trade behavior parameters.
        """
        # Load economic configuration from JSON
        economic_config = self._load_economic_config()
        
        # Get general behavior modifiers
        modifiers = await self.memory_influence_service.generate_behavior_modifiers(context)
        
        # Initialize default values from JSON config
        base_price_modifier = economic_config.get('base_price_modifier', 1.0)
        trade_willingness = economic_config.get('default_trade_willingness', 0.7)
        reputation_bonus = 0.0
        preferred_customers = []
        blacklisted_customers = []
        risk_premium = 0.0
        
        # Get modifier ranges from config
        price_modifier_ranges = economic_config.get('price_modifier_ranges', {})
        trade_willingness_modifiers = economic_config.get('trade_willingness_modifiers', {})
        risk_premium_modifiers = economic_config.get('risk_premium_modifiers', {})
        
        # Process modifiers that affect economic behavior
        for modifier in modifiers:
            if modifier.influence_type == BehaviorInfluenceType.RISK_ASSESSMENT:
                # Apply JSON-configured risk adjustments
                risk_modifier = risk_premium_modifiers.get('risk_assessment', 0.2)
                trade_modifier = trade_willingness_modifiers.get('risk_assessment', 0.3)
                
                risk_premium += modifier.modifier_value * risk_modifier
                trade_willingness -= modifier.modifier_value * trade_modifier
            
            elif modifier.influence_type == BehaviorInfluenceType.EMOTIONAL_RESPONSE:
                # Apply JSON-configured emotional modifiers
                if modifier.context and 'anger' in modifier.context:
                    anger_price_mod = price_modifier_ranges.get('anger_increase', 0.1)
                    anger_trade_mod = trade_willingness_modifiers.get('anger_decrease', 0.2)
                    
                    base_price_modifier += modifier.modifier_value * anger_price_mod
                    trade_willingness -= modifier.modifier_value * anger_trade_mod
                    
                elif modifier.context and 'fear' in modifier.context:
                    fear_trade_mod = trade_willingness_modifiers.get('fear_decrease', 0.4)
                    fear_risk_mod = risk_premium_modifiers.get('fear_increase', 0.3)
                    
                    trade_willingness -= modifier.modifier_value * fear_trade_mod
                    risk_premium += modifier.modifier_value * fear_risk_mod
                    
                elif modifier.context and 'joy' in modifier.context:
                    joy_trade_mod = trade_willingness_modifiers.get('joy_increase', 0.2)
                    joy_price_mod = price_modifier_ranges.get('joy_discount', 0.05)
                    
                    trade_willingness += modifier.modifier_value * joy_trade_mod
                    base_price_modifier -= modifier.modifier_value * joy_price_mod
            
            elif modifier.influence_type == BehaviorInfluenceType.TRUST:
                # Apply trust-based economic adjustments
                if context:  # context should be the trading partner entity ID
                    if modifier.modifier_value > 0.7:  # High trust
                        preferred_customers.append(context)
                        trust_discount = price_modifier_ranges.get('high_trust_discount', 0.1)
                        base_price_modifier -= trust_discount
                    elif modifier.modifier_value < 0.3:  # Low trust
                        blacklisted_customers.append(context)
                        distrust_premium = price_modifier_ranges.get('low_trust_premium', 0.2)
                        base_price_modifier += distrust_premium
        
        # Apply JSON-configured clamp ranges
        price_clamps = economic_config.get('price_modifier_clamps', {'min': 0.5, 'max': 2.0})
        trade_clamps = economic_config.get('trade_willingness_clamps', {'min': 0.0, 'max': 1.0})
        risk_clamps = economic_config.get('risk_premium_clamps', {'min': 0.0, 'max': 0.5})
        
        base_price_modifier = max(price_clamps['min'], min(price_clamps['max'], base_price_modifier))
        trade_willingness = max(trade_clamps['min'], min(trade_clamps['max'], trade_willingness))
        risk_premium = max(risk_clamps['min'], min(risk_clamps['max'], risk_premium))
        
        logger.info(f"Generated economic behavior modifications for {self.entity_id} using JSON config")
        
        return EconomicBehaviorModification(
            base_price_modifier=base_price_modifier,
            trade_willingness=trade_willingness,
            reputation_bonus=reputation_bonus,
            preferred_customers=preferred_customers,
            blacklisted_customers=blacklisted_customers,
            risk_premium=risk_premium
        )
    
    def _load_economic_config(self) -> Dict[str, Any]:
        """Load economic behavior configuration from JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '../../../data/systems/memory/behavioral_responses.json')
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get('economic_behavior_modifiers', {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load economic configuration: {e}. Using defaults.")
            return {
                'base_price_modifier': 1.0,
                'default_trade_willingness': 0.7,
                'price_modifier_ranges': {
                    'anger_increase': 0.1,
                    'joy_discount': 0.05,
                    'high_trust_discount': 0.1,
                    'low_trust_premium': 0.2
                },
                'trade_willingness_modifiers': {
                    'risk_assessment': 0.3,
                    'anger_decrease': 0.2,
                    'fear_decrease': 0.4,
                    'joy_increase': 0.2
                },
                'risk_premium_modifiers': {
                    'risk_assessment': 0.2,
                    'fear_increase': 0.3
                },
                'price_modifier_clamps': {'min': 0.5, 'max': 2.0},
                'trade_willingness_clamps': {'min': 0.0, 'max': 1.0},
                'risk_premium_clamps': {'min': 0.0, 'max': 0.5}
            }
    
    async def get_faction_behavior_modifications(self, 
                                              known_factions: List[str],
                                              context: Optional[str] = None) -> FactionBehaviorModification:
        """
        Generate faction-related behavior modifications based on memory analysis.
        
        This affects political alignment, loyalty, and diplomatic behavior.
        """
        faction_loyalties = {}
        diplomatic_stance = {}
        
        # Calculate faction bias for each known faction
        for faction_id in known_factions:
            bias = await self.memory_influence_service.calculate_faction_bias(faction_id)
            faction_loyalties[faction_id] = bias
            
            # Convert bias to diplomatic stance
            if bias >= 0.7:
                diplomatic_stance[faction_id] = "allied"
            elif bias >= 0.3:
                diplomatic_stance[faction_id] = "friendly"
            elif bias <= -0.7:
                diplomatic_stance[faction_id] = "hostile"
            elif bias <= -0.3:
                diplomatic_stance[faction_id] = "unfriendly"
            else:
                diplomatic_stance[faction_id] = "neutral"
        
        # Get general behavior modifiers
        modifiers = await self.memory_influence_service.generate_behavior_modifiers(context)
        
        political_bias = 0.0
        rebellion_likelihood = 0.1  # Base 10% chance
        influence_resistance = 0.5  # Base 50% resistance
        
        for modifier in modifiers:
            if modifier.influence_type == BehaviorInfluenceType.EMOTIONAL_RESPONSE:
                if modifier.context and 'anger' in modifier.context:
                    rebellion_likelihood += modifier.modifier_value * 0.2
                    influence_resistance += modifier.modifier_value * 0.3
                elif modifier.context and 'fear' in modifier.context:
                    rebellion_likelihood -= modifier.modifier_value * 0.1
                    influence_resistance -= modifier.modifier_value * 0.2
        
        # Clamp values
        rebellion_likelihood = max(0.0, min(1.0, rebellion_likelihood))
        influence_resistance = max(0.0, min(1.0, influence_resistance))
        
        logger.info(f"Generated faction behavior modifications for {self.entity_id}")
        
        return FactionBehaviorModification(
            faction_loyalties=faction_loyalties,
            diplomatic_stance=diplomatic_stance,
            political_bias=political_bias,
            rebellion_likelihood=rebellion_likelihood,
            influence_resistance=influence_resistance
        )
    
    async def get_combat_behavior_modifications(self, context: Optional[str] = None) -> CombatBehaviorModification:
        """
        Generate combat behavior modifications based on memory analysis.
        
        This affects combat aggression, ally/enemy recognition, and tactical decisions.
        """
        # Get general behavior modifiers
        modifiers = await self.memory_influence_service.generate_behavior_modifiers(context)
        
        aggression_modifier = 1.0
        flee_threshold = 0.3  # Default flee at 30% health
        ally_recognition = {}
        enemy_priority = {}
        combat_caution = 0.5
        berserker_triggers = []
        
        # If context is an entity ID, check trust level for ally/enemy recognition
        if context and isinstance(context, str):
            try:
                trust_calc = await self.memory_influence_service.calculate_trust_level(context)
                if trust_calc.trust_level >= 0.7:  # High trust threshold
                    ally_recognition[context] = trust_calc.trust_level
                elif trust_calc.trust_level <= 0.3:  # Low trust threshold  
                    enemy_priority[context] = 1.0 - trust_calc.trust_level
            except Exception:
                # If trust calculation fails, continue without ally/enemy recognition
                pass
        
        for modifier in modifiers:
            if modifier.influence_type == BehaviorInfluenceType.RISK_ASSESSMENT:
                # Higher risk assessment = more cautious combat
                combat_caution += modifier.modifier_value * 0.5
                flee_threshold += modifier.modifier_value * 0.2
                aggression_modifier -= modifier.modifier_value * 0.3
            
            elif modifier.influence_type == BehaviorInfluenceType.EMOTIONAL_RESPONSE:
                if modifier.context and 'anger' in modifier.context:
                    aggression_modifier += modifier.modifier_value * 0.5
                    flee_threshold -= modifier.modifier_value * 0.1
                    if modifier.modifier_value > 0.8:
                        berserker_triggers.append("high_anger")
                
                elif modifier.context and 'fear' in modifier.context:
                    aggression_modifier -= modifier.modifier_value * 0.4
                    flee_threshold += modifier.modifier_value * 0.3
                    combat_caution += modifier.modifier_value * 0.4
                
                elif modifier.context and 'joy' in modifier.context:
                    # Joy makes NPCs more confident but not necessarily reckless
                    aggression_modifier += modifier.modifier_value * 0.2
                    combat_caution -= modifier.modifier_value * 0.1
        
        # Clamp values to reasonable ranges
        aggression_modifier = max(0.1, min(3.0, aggression_modifier))
        flee_threshold = max(0.05, min(0.8, flee_threshold))
        combat_caution = max(0.0, min(1.0, combat_caution))
        
        logger.info(f"Generated combat behavior modifications for {self.entity_id}")
        
        return CombatBehaviorModification(
            aggression_modifier=aggression_modifier,
            flee_threshold=flee_threshold,
            ally_recognition=ally_recognition,
            enemy_priority=enemy_priority,
            combat_caution=combat_caution,
            berserker_triggers=berserker_triggers
        )
    
    async def get_social_behavior_modifications(self, context: Optional[str] = None) -> SocialBehaviorModification:
        """
        Generate social behavior modifications based on memory analysis.
        
        This affects conversation willingness, topic preferences, and social influence.
        """
        # Get general behavior modifiers
        modifiers = await self.memory_influence_service.generate_behavior_modifiers(context)
        
        social_openness = 0.6  # Default moderate openness
        conversation_topics = {}
        relationship_priorities = {}
        rumor_credibility = {}
        social_influence = 0.5
        
        for modifier in modifiers:
            if modifier.influence_type == BehaviorInfluenceType.TRUST:
                # Trust issues affect social openness and influence
                if modifier.modifier_value < 0:  # Negative trust (trust issues)
                    social_openness += modifier.modifier_value * 0.5  # Reduce openness
                    social_influence += modifier.modifier_value * 0.3  # Reduce influence
                else:  # Positive trust
                    social_openness += modifier.modifier_value * 0.3  # Increase openness
                    social_influence += modifier.modifier_value * 0.2  # Increase influence
            
            elif modifier.influence_type == BehaviorInfluenceType.EMOTIONAL_RESPONSE:
                if modifier.context and 'anger' in modifier.context:
                    social_openness -= modifier.modifier_value * 0.4
                    social_influence += modifier.modifier_value * 0.2  # Angry NPCs can be more forceful
                
                elif modifier.context and 'fear' in modifier.context:
                    social_openness -= modifier.modifier_value * 0.5
                    social_influence -= modifier.modifier_value * 0.3
                
                elif modifier.context and 'joy' in modifier.context:
                    social_openness += modifier.modifier_value * 0.3
                    social_influence += modifier.modifier_value * 0.1
                
                elif modifier.context and 'sadness' in modifier.context:
                    social_openness -= modifier.modifier_value * 0.3
                    social_influence -= modifier.modifier_value * 0.2
        
        # Set conversation topic preferences based on memories
        # This would be enhanced with more sophisticated analysis
        conversation_topics.update({
            'politics': 0.0,  # Neutral by default
            'trade': 0.1,     # Slightly positive
            'weather': 0.2,   # Safe topic
            'family': 0.0,    # Neutral
            'war': -0.2,      # Slightly negative
            'rumors': 0.1     # Slightly positive
        })
        
        # Clamp values
        social_openness = max(0.0, min(1.0, social_openness))
        social_influence = max(0.0, min(1.0, social_influence))
        
        logger.info(f"Generated social behavior modifications for {self.entity_id}")
        
        return SocialBehaviorModification(
            social_openness=social_openness,
            conversation_topics=conversation_topics,
            relationship_priorities=relationship_priorities,
            rumor_credibility=rumor_credibility,
            social_influence=social_influence
        )
    
    async def calculate_entity_trust_for_context(self, entity_id: str, 
                                               context: str = "general") -> TrustCalculation:
        """
        Calculate trust level for a specific entity in a specific context.
        
        This is used by other systems to make trust-based decisions.
        """
        return await self.memory_influence_service.calculate_trust_level(entity_id, context)
    
    async def get_opportunity_recognition_factors(self, 
                                                opportunity_type: str,
                                                context: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """
        Analyze memories to determine how likely an NPC is to recognize opportunities.
        
        Returns factors that influence opportunity recognition in different domains.
        """
        # Get risk assessment for this type of opportunity
        try:
            risk_assessment = await self.memory_influence_service.assess_risk(opportunity_type, context)
            
            # Extract values with proper type checking and defaults
            risk_level = getattr(risk_assessment, 'risk_level', 0.5)
            if not isinstance(risk_level, (int, float)):
                risk_level = 0.5
                
            past_experiences = getattr(risk_assessment, 'past_experiences', [])
            if not isinstance(past_experiences, list):
                past_experiences = []
                
            confidence = getattr(risk_assessment, 'confidence', 0.5)
            if not isinstance(confidence, (int, float)):
                confidence = 0.5
                
            recognition_factors = {
                'base_recognition': 0.5,  # Default baseline
                'risk_tolerance': 1.0 - risk_level,
                'experience_level': min(1.0, len(past_experiences) / 10.0),
                'confidence': confidence
            }
        except Exception:
            # If risk assessment fails, use defaults
            recognition_factors = {
                'base_recognition': 0.5,
                'risk_tolerance': 0.5,
                'experience_level': 0.0,
                'confidence': 0.5
            }
        
        # Get emotional modifiers
        try:
            emotional_triggers = await self.memory_influence_service.identify_emotional_triggers()
            
            for trigger in emotional_triggers:
                emotion = getattr(trigger, 'emotion', '')
                intensity = getattr(trigger, 'intensity', 0.0)
                
                if not isinstance(intensity, (int, float)):
                    continue
                    
                if emotion == 'fear':
                    recognition_factors['risk_tolerance'] -= intensity * 0.3
                elif emotion == 'anger':
                    recognition_factors['risk_tolerance'] += intensity * 0.2
                elif emotion == 'joy':
                    recognition_factors['confidence'] += intensity * 0.2
        except Exception:
            # If emotional triggers fail, continue without modifiers
            pass
        
        # Add opportunity-specific factors for tests
        if 'base_recognition' not in recognition_factors:
            recognition_factors['base_recognition'] = 0.5
        if 'opportunity_sensitivity' not in recognition_factors:
            recognition_factors['opportunity_sensitivity'] = 0.5
        if 'confidence_bonus' not in recognition_factors:
            recognition_factors['confidence_bonus'] = 0.0
        
        # Clamp all factors to [0, 1] range with proper type checking
        for factor, value in recognition_factors.items():
            if isinstance(value, (int, float)):
                recognition_factors[factor] = max(0.0, min(1.0, value))
            else:
                recognition_factors[factor] = 0.5  # Default safe value
        
        logger.info(f"Calculated opportunity recognition factors for {opportunity_type}")
        
        return recognition_factors
    
    async def get_comprehensive_behavior_profile(self, 
                                               known_factions: List[str],
                                               context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive behavior profile for this entity based on memory analysis.
        
        This provides a complete picture of how memories influence behavior across all systems.
        """
        profile = {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'generated_at': datetime.now().isoformat(),
            'timestamp': datetime.now().isoformat(),  # Also include timestamp for test compatibility
            'context': context,
            'economic': await self.get_economic_behavior_modifications(context),
            'faction': await self.get_faction_behavior_modifications(known_factions, context),
            'combat': await self.get_combat_behavior_modifications(context),
            'social': await self.get_social_behavior_modifications(context),
            'base_modifiers': await self.memory_influence_service.generate_behavior_modifiers(context)
        }
        
        logger.info(f"Generated comprehensive behavior profile for {self.entity_id}")
        
        return profile 