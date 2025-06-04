"""
Smart Barter Economics & Relationship Integration Service

Implements dynamic pricing system for NPC bartering that considers:
- NPC type (Peasants, Merchants, Nobles, Guards/Military)
- Relationship status and trust levels
- Faction alignment and relationships
- Economic context (regional supply/demand, wealth levels, conflicts)

This service extends the basic barter functionality with sophisticated economic modeling.
"""

from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from enum import Enum
import logging
from datetime import datetime

# Use canonical imports from infrastructure
from backend.infrastructure.systems.npc.models.models import NpcEntity
from backend.infrastructure.systems.npc.models.barter_types import ItemTier, BarterValidationResult
from backend.infrastructure.database import get_db
from backend.systems.economy.services.economy_manager import EconomyManager
from backend.systems.diplomacy.models.core_models import FactionRelationship
from backend.systems.npc.config import get_npc_config
from backend.infrastructure.shared.exceptions import NpcNotFoundError, NpcValidationError

logger = logging.getLogger(__name__)


class NPCType(Enum):
    """NPC types for differentiated bartering behavior"""
    PEASANT = "peasant"
    COMMONER = "commoner"
    MERCHANT = "merchant"
    TRADER = "trader"
    NOBLE = "noble"
    ARISTOCRAT = "aristocrat"
    GUARD = "guard"
    MILITARY = "military"
    UNKNOWN = "unknown"


class ItemCategory(Enum):
    """Item categories for NPC type preferences"""
    BASIC_NECESSITY = "basic_necessity"  # food, tools, medicine
    LUXURY = "luxury"  # jewelry, art, exotic goods
    MILITARY = "military"  # weapons, armor, tactical gear
    PRACTICAL = "practical"  # everyday tools, supplies
    PRESTIGE = "prestige"  # status symbols, rare items
    COMMON = "common"  # standard trade goods


class EconomicContext:
    """Container for regional economic context affecting barter prices"""
    
    def __init__(self, region_id: Optional[str] = None):
        self.region_id = region_id
        
        # Load economic data from configuration
        config = get_npc_config()
        economic_config = config.get_economic_regions_config()
        
        if region_id:
            region_data = economic_config.get('regions', {}).get(region_id, 
                         economic_config.get('regions', {}).get('default', {}))
        else:
            region_data = economic_config.get('regions', {}).get('default', {})
        
        self.prosperity_level = region_data.get('prosperity_level', 1.0)
        self.conflict_status = region_data.get('conflict_status', False)
        self.trade_volume = region_data.get('trade_volume', 1.0)
        self.supply_demand_ratio = region_data.get('supply_demand', {})
        self.seasonal_effects = region_data.get('seasonal_effects', {})
        self.wealth_distribution = region_data.get('wealth_distribution', 1.0)
        
    def get_supply_demand_modifier(self, item_category: ItemCategory) -> float:
        """Get supply/demand modifier for an item category"""
        return self.supply_demand_ratio.get(item_category.value, 1.0)


class BarterEconomicsService:
    """Advanced bartering service with comprehensive economic modeling"""
    
    def __init__(self, db_session=None):
        """Initialize the economics service"""
        self.db = db_session if db_session else next(get_db())
        self._is_external_session = db_session is not None
        self.economy_manager = EconomyManager(self.db)
        self.config = get_npc_config()
        
    def __del__(self):
        """Clean up database session if we created it"""
        if not self._is_external_session and hasattr(self, 'db'):
            try:
                self.db.close()
            except:
                pass
    
    def determine_npc_type(self, npc: NpcEntity) -> NPCType:
        """Determine NPC type for pricing behavior"""
        try:
            profession = getattr(npc, 'profession', '').lower()
            
            # Map professions to NPC types
            profession_mappings = {
                'farmer': NPCType.PEASANT,
                'laborer': NPCType.PEASANT,
                'peasant': NPCType.PEASANT,
                'worker': NPCType.COMMONER,
                'craftsman': NPCType.COMMONER,
                'artisan': NPCType.COMMONER,
                'merchant': NPCType.MERCHANT,
                'trader': NPCType.TRADER,
                'shopkeeper': NPCType.MERCHANT,
                'noble': NPCType.NOBLE,
                'lord': NPCType.ARISTOCRAT,
                'lady': NPCType.ARISTOCRAT,
                'baron': NPCType.ARISTOCRAT,
                'guard': NPCType.GUARD,
                'soldier': NPCType.MILITARY,
                'captain': NPCType.MILITARY,
                'knight': NPCType.MILITARY,
            }
            
            # Check for exact matches first
            if profession in profession_mappings:
                return profession_mappings[profession]
            
            # Check for partial matches
            for prof_key, npc_type in profession_mappings.items():
                if prof_key in profession:
                    return npc_type
            
            # Fallback based on other attributes
            if hasattr(npc, 'wealth') and getattr(npc, 'wealth', 0) > 1000:
                return NPCType.NOBLE
            elif hasattr(npc, 'faction_id') and npc.faction_id:
                # Could be military or merchant based on faction
                return NPCType.COMMONER
            
            return NPCType.COMMONER
            
        except Exception as e:
            logger.warning(f"Error determining NPC type for {npc.id}: {e}")
            return NPCType.UNKNOWN
    
    def categorize_item(self, item: Dict[str, Any]) -> ItemCategory:
        """Categorize an item for NPC type preference calculations"""
        try:
            # Load item categorization mapping from config
            trading_config = self.config.get_item_trading_rules_config()
            category_mappings = trading_config.get('item_category_mappings', {})
            
            item_type = item.get('item_type', '').lower()
            item_name = item.get('name', '').lower()
            tags = item.get('tags', [])
            
            # Check explicit tags first
            if 'luxury' in tags or 'prestige' in tags:
                return ItemCategory.LUXURY
            elif 'military' in tags or 'weapon' in tags or 'armor' in tags:
                return ItemCategory.MILITARY
            elif 'food' in tags or 'medicine' in tags or 'tool' in tags:
                return ItemCategory.BASIC_NECESSITY
            
            # Check item type using config mappings
            if item_type in category_mappings:
                mapped_category = category_mappings[item_type]
                try:
                    return ItemCategory(mapped_category)
                except ValueError:
                    pass
            
            # Fallback logic for unmapped items
            luxury_keywords = ['silk', 'gold', 'silver', 'gem', 'diamond', 'ruby', 'wine', 'perfume']
            necessity_keywords = ['bread', 'water', 'medicine', 'bandage', 'hammer', 'rope']
            military_keywords = ['sword', 'bow', 'arrow', 'shield', 'helmet', 'armor']
            
            for keyword in luxury_keywords:
                if keyword in item_name:
                    return ItemCategory.LUXURY
            
            for keyword in necessity_keywords:
                if keyword in item_name:
                    return ItemCategory.BASIC_NECESSITY
                    
            for keyword in military_keywords:
                if keyword in item_name:
                    return ItemCategory.MILITARY
            
            return ItemCategory.COMMON
            
        except Exception as e:
            logger.warning(f"Error categorizing item {item.get('name', 'unknown')}: {e}")
            return ItemCategory.COMMON
    
    def get_npc_type_price_modifier(self, npc_type: NPCType, item_category: ItemCategory, 
                                   base_value: float) -> Tuple[float, str]:
        """Get price modifier based on NPC type and item category preferences"""
        try:
            # Load NPC type behavior from configuration
            npc_types_config = self.config.get_npc_types_config()
            npc_config = npc_types_config.get(npc_type.value, npc_types_config.get("unknown", {}))
            
            item_preferences = npc_config.get('item_preferences', {})
            preference_data = item_preferences.get(item_category.value, {"multiplier": 1.0, "reason": "Standard pricing"})
            
            multiplier = preference_data.get('multiplier', 1.0)
            reason = preference_data.get('reason', 'Standard pricing')
            
            return (multiplier, reason)
            
        except Exception as e:
            logger.warning(f"Error getting price modifier for {npc_type.value} and {item_category.value}: {e}")
            return (1.0, "Error in pricing calculation")
    
    def get_relationship_trust_modifier(self, relationship_trust: float) -> Tuple[float, str]:
        """Enhanced relationship trust modifiers following Task 63 specifications"""
        try:
            if relationship_trust >= 0.8:  # Trusted Ally (0.8-1.0)
                return 0.75, "Trusted ally discount (-25%)"
            elif relationship_trust >= 0.6:  # Close Friend (0.6-0.8) 
                return 0.85, "Close friend discount (-15%)"
            elif relationship_trust >= 0.4:  # Friend (0.4-0.6)
                return 1.0, "Friend pricing (standard)"
            elif relationship_trust >= 0.2:  # Acquaintance (0.2-0.4)
                return 1.25, "Acquaintance markup (+25%)"
            else:  # Stranger (0.0-0.2)
                return 1.5, "Stranger markup (+50%)"
                
        except Exception as e:
            logger.error(f"Error calculating relationship modifier: {e}")
            return 1.0, "Error in relationship calculation"
    
    def get_faction_relationship_modifier(self, npc: NpcEntity, character_faction_id: Optional[str]) -> Tuple[float, str]:
        """Calculate faction relationship pricing modifiers"""
        try:
            if not character_faction_id or not hasattr(npc, 'faction_id') or not npc.faction_id:
                return 1.0, "No faction relationships"
            
            # This would integrate with the faction system to get relationship status
            # For now, implementing basic logic that can be enhanced
            
            npc_faction_id = str(npc.faction_id)
            
            # Same faction
            if npc_faction_id == character_faction_id:
                return 0.9, "Same faction discount (-10%)"
            
            # Would need to query faction relationship system here
            # For demonstration, using placeholder logic
            faction_relations = self._get_faction_relationship(npc_faction_id, character_faction_id)
            
            if faction_relations == "allied":
                return 0.9, "Allied faction discount (-10%)"
            elif faction_relations == "friendly": 
                return 0.95, "Friendly faction discount (-5%)"
            elif faction_relations == "neutral":
                return 1.0, "Neutral faction pricing"
            elif faction_relations == "unfriendly":
                return 1.25, "Unfriendly faction markup (+25%)"
            elif faction_relations == "hostile":
                return 2.0, "Hostile faction markup (+100%)"
            elif faction_relations == "enemy":
                return 10.0, "Enemy faction - extreme markup or refusal"
            else:
                return 1.0, "Unknown faction relationship"
                
        except Exception as e:
            logger.error(f"Error calculating faction modifier: {e}")
            return 1.0, "Error in faction calculation"
    
    def _get_faction_relationship(self, faction_a_id: str, faction_b_id: str) -> str:
        """Get relationship status between two factions"""
        try:
            # This would integrate with the actual faction system
            # Placeholder implementation for now
            
            # Would query the faction relationship system here
            # Example: faction_service.get_relationship(faction_a_id, faction_b_id)
            
            # For now, return neutral as default
            return "neutral"
            
        except Exception as e:
            logger.error(f"Error getting faction relationship: {e}")
            return "neutral"
    
    def get_economic_context(self, npc: NpcEntity) -> EconomicContext:
        """Get economic context for the NPC's region"""
        try:
            context = EconomicContext()
            
            # Get region from NPC location
            region_id = getattr(npc, 'region_id', None)
            if region_id:
                context.region_id = str(region_id)
                
                # Get economic data from economy manager
                try:
                    economic_data = self.economy_manager.get_economic_analytics(region_id)
                    
                    if economic_data and 'metrics' in economic_data:
                        price_index = economic_data['metrics'].get('price_index', {})
                        context.prosperity_level = price_index.get('index', 100.0) / 100.0
                        
                        # Market activity affects trade volume
                        market_count = economic_data['metrics'].get('market_count', 1)
                        context.trade_volume = min(2.0, max(0.5, market_count / 5.0))
                        
                except Exception as e:
                    logger.warning(f"Could not get economic data for region {region_id}: {e}")
            
            # Check for conflict status (would integrate with world state/war systems)
            context.conflict_status = self._check_regional_conflicts(region_id)
            
            # Generate supply/demand ratios based on economic context
            context.supply_demand_ratio = self._generate_supply_demand_ratios(context)
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting economic context: {e}")
            return EconomicContext()  # Return default context
    
    def _check_regional_conflicts(self, region_id: Optional[str]) -> bool:
        """Check if region is affected by conflicts"""
        try:
            # This would integrate with tension/war system
            # Placeholder implementation
            return False
            
        except Exception as e:
            logger.error(f"Error checking regional conflicts: {e}")
            return False
    
    def _generate_supply_demand_ratios(self, context: EconomicContext) -> Dict[str, float]:
        """Generate supply/demand ratios based on economic context"""
        try:
            ratios = {}
            
            # Base ratios - can be enhanced with real economic data
            base_ratios = {
                ItemCategory.BASIC_NECESSITY.value: 1.2 if context.conflict_status else 1.0,
                ItemCategory.MILITARY.value: 1.5 if context.conflict_status else 0.9,
                ItemCategory.LUXURY.value: 0.8 if context.conflict_status else 1.1,
                ItemCategory.PRACTICAL.value: 1.1,
                ItemCategory.PRESTIGE.value: context.prosperity_level,
                ItemCategory.COMMON.value: 1.0
            }
            
            # Adjust based on prosperity and trade volume
            for category, base_ratio in base_ratios.items():
                adjusted_ratio = base_ratio * context.prosperity_level * context.trade_volume
                ratios[category] = max(0.3, min(3.0, adjusted_ratio))  # Clamp to reasonable range
            
            return ratios
            
        except Exception as e:
            logger.error(f"Error generating supply/demand ratios: {e}")
            return {}
    
    def calculate_smart_barter_price(self, base_value: float, npc: NpcEntity, item: Dict[str, Any],
                                   relationship_trust: float, character_faction_id: Optional[str] = None,
                                   tier: ItemTier = ItemTier.ALWAYS_AVAILABLE) -> Dict[str, Any]:
        """
        Calculate comprehensive barter price using all economic factors
        
        Args:
            base_value: Base item value
            npc: The NPC entity
            item: Item being traded
            relationship_trust: Trust level (0.0-1.0)
            character_faction_id: Character's faction ID for faction relations
            tier: Item availability tier
            
        Returns:
            Dictionary with price and detailed breakdown
        """
        try:
            # Start with base value
            final_price = base_value
            price_factors = {}
            
            # 1. NPC Type-based pricing
            npc_type = self.determine_npc_type(npc)
            item_category = self.categorize_item(item)
            
            type_modifier, type_reason = self.get_npc_type_price_modifier(npc_type, item_category, base_value)
            final_price *= type_modifier
            price_factors['npc_type'] = {
                'type': npc_type.value,
                'category': item_category.value,
                'modifier': type_modifier,
                'reason': type_reason
            }
            
            # 2. Relationship modifiers
            relationship_modifier, relationship_reason = self.get_relationship_trust_modifier(relationship_trust)
            final_price *= relationship_modifier
            price_factors['relationship'] = {
                'trust_level': relationship_trust,
                'modifier': relationship_modifier,
                'reason': relationship_reason
            }
            
            # 3. Faction relationship modifiers
            faction_modifier, faction_reason = self.get_faction_relationship_modifier(npc, character_faction_id)
            final_price *= faction_modifier
            price_factors['faction'] = {
                'modifier': faction_modifier,
                'reason': faction_reason
            }
            
            # 4. Economic context modifiers
            economic_context = self.get_economic_context(npc)
            supply_demand_modifier = economic_context.get_supply_demand_modifier(item_category)
            final_price *= supply_demand_modifier
            
            # Regional prosperity affects luxury pricing more
            if item_category in [ItemCategory.LUXURY, ItemCategory.PRESTIGE]:
                prosperity_effect = economic_context.prosperity_level
            else:
                prosperity_effect = 0.8 + (economic_context.prosperity_level * 0.2)  # Less effect on necessities
                
            final_price *= prosperity_effect
            
            price_factors['economic_context'] = {
                'region_id': economic_context.region_id,
                'prosperity_level': economic_context.prosperity_level,
                'supply_demand_modifier': supply_demand_modifier,
                'conflict_status': economic_context.conflict_status,
                'trade_volume': economic_context.trade_volume
            }
            
            # 5. Item tier modifiers (from original system)
            tier_modifier = 1.5 if tier == ItemTier.HIGH_PRICE_RELATIONSHIP else 1.0
            final_price *= tier_modifier
            price_factors['tier'] = {
                'tier': tier.value,
                'modifier': tier_modifier
            }
            
            # 6. Additional NPC personality factors (from original system)
            charisma_modifier = (getattr(npc, 'charisma', 10) - 10) * 0.02
            pragmatism_modifier = 1.0
            
            pragmatism = getattr(npc, 'hidden_pragmatism', 0)
            if pragmatism > 5:
                pragmatism_modifier = 1.1
            elif pragmatism < -5:
                pragmatism_modifier = 0.9
                
            final_price *= (1.0 + charisma_modifier) * pragmatism_modifier
            
            price_factors['personality'] = {
                'charisma': getattr(npc, 'charisma', 10),
                'charisma_modifier': charisma_modifier,
                'pragmatism': pragmatism,
                'pragmatism_modifier': pragmatism_modifier
            }
            
            # Ensure minimum price of 1
            final_price = max(1.0, final_price)
            
            return {
                'base_value': base_value,
                'final_price': round(final_price, 2),
                'total_modifier': round(final_price / base_value, 3),
                'price_factors': price_factors,
                'npc_type': npc_type.value,
                'item_category': item_category.value,
                'relationship_trust': relationship_trust
            }
            
        except Exception as e:
            logger.error(f"Error calculating smart barter price: {e}")
            # Return fallback pricing
            return {
                'base_value': base_value,
                'final_price': max(1.0, base_value),
                'total_modifier': 1.0,
                'price_factors': {'error': str(e)},
                'npc_type': 'unknown',
                'item_category': 'common',
                'relationship_trust': relationship_trust
            } 