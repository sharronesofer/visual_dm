"""
Loot Economic Integration - Infrastructure Layer

This module provides economic system integration for loot pricing and supply/demand,
handling all technical aspects of interfacing with the economy system.
"""

from typing import Dict, Any
import hashlib


def get_current_supply(item_name: str, region_id: int) -> int:
    """Get current supply level for an item in a region (0-100)"""
    try:
        # Import here to avoid circular import
        from backend.systems.economy.services.economy_manager import EconomyManager
        
        economy_manager = EconomyManager.get_instance()
        
        # Get markets in the region
        markets = economy_manager.get_markets_by_region(region_id)
        if not markets:
            return 50  # Default neutral supply if no markets
            
        # Try to map item name to resource ID (this would need proper mapping logic)
        resource_id = _map_item_to_resource_id(item_name)
        
        total_supply = 0
        market_count = 0
        
        for market in markets:
            if hasattr(market, 'supply_demand') and market.supply_demand:
                resource_supply_data = market.supply_demand.get(str(resource_id), {})
                supply = resource_supply_data.get('supply', 50)
                total_supply += supply
                market_count += 1
        
        if market_count > 0:
            average_supply = total_supply / market_count
            # Convert to 0-100 scale
            return int(max(0, min(100, average_supply)))
        else:
            return 50  # Default neutral supply
            
    except Exception as e:
        print(f"Warning: Could not get real supply data for {item_name} in region {region_id}: {e}")
        # Fallback to reasonable default based on item rarity
        try:
            from backend.infrastructure.config_loaders.loot_config_loader import config_loader
            rarity_config = config_loader.get_rarity_config()
            
            # Estimate supply based on rarity (rarer items have lower supply)
            rarities = rarity_config.get("rarities", {})
            for rarity_name, rarity_data in rarities.items():
                if rarity_data.get('chance', 0) > 0:
                    # Lower drop chance = rarer = lower supply
                    estimated_supply = int(rarity_data.get('chance', 0.1) * 200)
                    return max(10, min(90, estimated_supply))
        except Exception:
            pass
        
        return 50


def get_current_demand(item_name: str, region_id: int) -> int:
    """Get current demand level for an item in a region (0-100)"""
    try:
        # Import here to avoid circular import
        from backend.systems.economy.services.economy_manager import EconomyManager
        
        economy_manager = EconomyManager.get_instance()
        
        # Get markets in the region
        markets = economy_manager.get_markets_by_region(region_id)
        if not markets:
            return 50  # Default neutral demand if no markets
            
        # Try to map item name to resource ID
        resource_id = _map_item_to_resource_id(item_name)
        
        total_demand = 0
        market_count = 0
        
        for market in markets:
            if hasattr(market, 'supply_demand') and market.supply_demand:
                resource_demand_data = market.supply_demand.get(str(resource_id), {})
                demand = resource_demand_data.get('demand', 50)
                total_demand += demand
                market_count += 1
        
        if market_count > 0:
            average_demand = total_demand / market_count
            # Convert to 0-100 scale
            return int(max(0, min(100, average_demand)))
        else:
            return 50  # Default neutral demand
            
    except Exception as e:
        print(f"Warning: Could not get real demand data for {item_name} in region {region_id}: {e}")
        # Fallback to reasonable default based on item utility
        try:
            from backend.infrastructure.config_loaders.loot_config_loader import config_loader
            rarity_config = config_loader.get_rarity_config()
            
            # Estimate demand based on rarity (rarer items often have higher demand from collectors)
            rarities = rarity_config.get("rarities", {})
            for rarity_name, rarity_data in rarities.items():
                base_demand = rarity_data.get('value_multiplier', 1.0)
                estimated_demand = int(min(90, max(20, base_demand * 40)))
                return estimated_demand
        except Exception:
            pass
        
        return 50


def apply_economic_factors_to_price(base_price: int, region_id: int, item_name: str) -> int:
    """Apply economic factors from the real economy system to adjust pricing"""
    try:
        # Import here to avoid circular import
        from backend.systems.economy.services.economy_manager import EconomyManager
        
        economy_manager = EconomyManager.get_instance()
        
        # Get economic analytics for the region
        economic_data = economy_manager.get_economic_analytics(region_id)
        
        adjusted_price = base_price
        
        if economic_data and 'metrics' in economic_data:
            metrics = economic_data['metrics']
            
            # Apply price index
            price_index = metrics.get('price_index', {})
            price_multiplier = price_index.get('index', 100.0) / 100.0
            adjusted_price = int(adjusted_price * price_multiplier)
            
            # Apply inflation rate if available
            inflation_rate = metrics.get('inflation_rate', 0.0)
            if inflation_rate:
                adjusted_price = int(adjusted_price * (1.0 + inflation_rate))
        
        # Get supply/demand data for additional adjustment
        supply = get_current_supply(item_name, region_id)
        demand = get_current_demand(item_name, region_id)
        
        # Apply supply/demand ratio
        if supply > 0:
            ratio = demand / supply
            supply_demand_multiplier = 0.5 + (ratio * 0.5)  # Range from 0.5 to 1.5
            adjusted_price = int(adjusted_price * supply_demand_multiplier)
        
        return max(1, adjusted_price)  # Ensure minimum price of 1
        
    except Exception as e:
        print(f"Warning: Could not apply economic factors for {item_name} in region {region_id}: {e}")
        # Fallback to simple supply/demand adjustment
        return adjust_price_for_supply_demand_simple(base_price, item_name, region_id)


def adjust_price_for_supply_demand_simple(base_price: int, item_name: str, region_id: int) -> int:
    """Simple supply/demand adjustment as fallback"""
    supply = get_current_supply(item_name, region_id)
    demand = get_current_demand(item_name, region_id)
    
    # Basic supply/demand calculation
    if supply == 0:
        supply = 1  # Avoid division by zero
    
    ratio = demand / supply
    
    # Simple price adjustment
    if ratio > 1.2:  # High demand, low supply
        multiplier = 1.0 + ((ratio - 1.0) * 0.3)
    elif ratio < 0.8:  # Low demand, high supply
        multiplier = 1.0 - ((1.0 - ratio) * 0.2)
    else:
        multiplier = 1.0  # Balanced
    
    # Clamp to reasonable bounds
    multiplier = max(0.5, min(2.0, multiplier))
    
    adjusted_price = int(base_price * multiplier)
    return max(1, adjusted_price)


def _map_item_to_resource_id(item_name: str) -> str:
    """Map loot item names to economy system resource IDs
    
    This is a simplified mapping function. In a real system, this would
    be more sophisticated, potentially using a lookup table or item categories.
    """
    # Simple hash-based mapping for now
    # In practice, this would use proper item -> resource mapping
    
    # Create a consistent ID based on item name
    item_hash = hashlib.md5(item_name.lower().encode()).hexdigest()
    
    # Map common item types to known resource categories
    item_lower = item_name.lower()
    
    # Weapon mappings
    if any(weapon_type in item_lower for weapon_type in ['sword', 'axe', 'bow', 'staff', 'wand']):
        return f"weapon_{item_hash[:8]}"
    
    # Armor mappings  
    elif any(armor_type in item_lower for armor_type in ['armor', 'helm', 'shield', 'boot', 'glove']):
        return f"armor_{item_hash[:8]}"
    
    # Jewelry mappings
    elif any(jewelry_type in item_lower for jewelry_type in ['ring', 'amulet', 'necklace', 'pendant']):
        return f"jewelry_{item_hash[:8]}"
    
    # Consumable mappings
    elif any(consumable_type in item_lower for consumable_type in ['potion', 'scroll', 'food', 'drink']):
        return f"consumable_{item_hash[:8]}"
    
    # Material mappings
    elif any(material_type in item_lower for material_type in ['ore', 'wood', 'cloth', 'leather', 'gem']):
        return f"material_{item_hash[:8]}"
    
    # Default mapping
    else:
        return f"misc_{item_hash[:8]}" 