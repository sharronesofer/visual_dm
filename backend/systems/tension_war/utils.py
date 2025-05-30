"""
Tension and War Utilities

This module provides utility functions for tension and war operations, including:
- Tension calculation helpers
- Border tension calculation
- Geographic war factors
- War outcome probability calculations

These utilities support the core TensionManager and WarManager services.
"""

from typing import Dict, List, Optional, Tuple, Any
import math
import random
from datetime import datetime, timedelta

from app.core.logging import logger

# --- Begin Legacy backward compatibility ---
# These functions provide backward compatibility with the old tension_utils and war_utils interfaces
# They delegate to the new TensionManager and WarManager implementations

def get_tension(region_id: str) -> Dict[str, Any]:
    """Backward compatibility function for old tension_utils.get_tension"""
    from .services import TensionManager
    
    tm = TensionManager()
    # In the new system, tension is between factions, not regions
    # This is a simplification for backward compatibility
    # We'll treat each region as its own faction for this compatibility layer
    tension_value = tm.get_tension(f"region_{region_id}", f"central_faction")
    tension_level = tm.get_tension_level(tension_value)
    
    return {
        "region": region_id,
        "level": int(tension_value),
        "label": tension_level.value.lower(),
        "modifiers": {}  # Simplified compatibility
    }

def modify_tension(region_id: str, source: str, amount: float) -> Dict[str, Any]:
    """Backward compatibility function for old tension_utils.modify_tension"""
    from .services import TensionManager
    
    tm = TensionManager()
    # Simplification for backward compatibility
    new_tension = tm.update_tension(f"region_{region_id}", f"central_faction", amount, source)
    return get_tension(region_id)

def reset_tension(region_id: str) -> Dict[str, Any]:
    """Backward compatibility function for old tension_utils.reset_tension"""
    from .services import TensionManager
    
    tm = TensionManager()
    # Simplification for backward compatibility
    tm.update_tension(f"region_{region_id}", f"central_faction", -100.0, "reset")
    return get_tension(region_id)

def decay_tension(region_id: str, decay_rate: float = 1.0) -> Dict[str, Any]:
    """Backward compatibility function for old tension_utils.decay_tension"""
    # The new TensionManager has automatic decay built in
    # This function is a no-op now that just returns the current state
    return get_tension(region_id)

def check_for_region_conflict(tension_threshold: float = 50, friction_threshold: float = 0.4) -> List[Tuple[str, str, str]]:
    """Backward compatibility function for old tension_utils.check_for_region_conflict"""
    # This would need to be implemented based on the specific requirements
    # For now, returning an empty list
    logger.warning("check_for_region_conflict called; compatibility function returns empty list")
    return []

def initialize_war(region_a: str, region_b: str, faction_a: str, faction_b: str) -> Dict[str, Any]:
    """Backward compatibility function for old war_utils.initialize_war"""
    from .services import WarManager
    
    wm = WarManager()
    war = wm.declare_war(faction_a, faction_b)
    return {"message": f"War initialized between {region_a} and {region_b}"}

def advance_war_day(region: str) -> Dict[str, Any]:
    """Backward compatibility function for old war_utils.advance_war_day"""
    from .services import WarManager
    
    # This is a simplified version - in reality, we would need to look up the war state
    # associated with this region
    logger.warning(f"advance_war_day called for {region}; partial compatibility only")
    return {"message": f"Day advanced for {region} (compatibility mode)"}

def record_poi_conquest(region: str, poi_id: str, conquering_faction: str) -> None:
    """Backward compatibility function for old war_utils.record_poi_conquest"""
    logger.warning(f"record_poi_conquest called for {region}/{poi_id}; compatibility function")
    # This would need to be implemented based on the specific requirements

def generate_daily_raids(region_name: str) -> List[str]:
    """Backward compatibility function for old war_utils.generate_daily_raids"""
    logger.warning(f"generate_daily_raids called for {region_name}; compatibility function returns empty list")
    return []
# --- End Legacy backward compatibility ---

def calculate_border_tension(
    faction_a_regions: List[str],
    faction_b_regions: List[str],
    region_borders: Dict[str, List[str]],
    base_factor: float = 0.5
) -> float:
    """Calculate tension contribution from bordering regions.
    
    Args:
        faction_a_regions: List of region IDs controlled by faction A
        faction_b_regions: List of region IDs controlled by faction B
        region_borders: Dict mapping region IDs to list of bordering region IDs
        base_factor: Base tension factor for bordering regions
        
    Returns:
        float: Tension contribution from bordering regions
    """
    border_count = 0
    
    # Count shared borders
    for region_a in faction_a_regions:
        if region_a not in region_borders:
            continue
            
        for neighbor in region_borders[region_a]:
            if neighbor in faction_b_regions:
                border_count += 1
                
    # Calculate tension contribution (diminishing returns for many borders)
    if border_count == 0:
        return 0.0
        
    return min(25.0, base_factor * math.sqrt(border_count) * 10)


def calculate_event_tension(
    recent_events: List[Dict[str, Any]],
    decay_days: int = 30
) -> float:
    """Calculate tension contribution from recent events.
    
    Args:
        recent_events: List of event dictionaries with 'impact' and 'timestamp' keys
        decay_days: Number of days over which event impact decays to zero
        
    Returns:
        float: Tension contribution from events
    """
    now = datetime.utcnow()
    total_impact = 0.0
    
    for event in recent_events:
        # Skip events without required data
        if 'impact' not in event or 'timestamp' not in event:
            continue
            
        # Parse timestamp
        try:
            if isinstance(event['timestamp'], str):
                timestamp = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
            else:
                timestamp = event['timestamp']
        except (ValueError, TypeError):
            logger.warning(f"Invalid timestamp in event: {event.get('id', 'unknown')}")
            continue
            
        # Calculate age-based decay factor
        age_days = (now - timestamp).total_seconds() / (24 * 3600)
        
        if age_days > decay_days:
            continue  # Event too old to matter
            
        decay_factor = 1.0 - (age_days / decay_days)
        impact = event['impact'] * decay_factor
        
        # Add to total
        total_impact += impact
        
    # Cap the impact
    return max(-50.0, min(50.0, total_impact))


def calculate_disputed_regions(
    faction_a_id: str,
    faction_b_id: str,
    faction_a_regions: List[str],
    faction_b_regions: List[str],
    region_borders: Dict[str, List[str]],
    historical_claims: Dict[str, List[str]] = None
) -> List[str]:
    """Identify disputed regions between two factions.
    
    Args:
        faction_a_id: ID of the first faction
        faction_b_id: ID of the second faction
        faction_a_regions: List of region IDs controlled by faction A
        faction_b_regions: List of region IDs controlled by faction B
        region_borders: Dict mapping region IDs to list of bordering region IDs
        historical_claims: Optional dict mapping faction IDs to lists of claimed region IDs
        
    Returns:
        List[str]: List of disputed region IDs
    """
    disputed = []
    
    # First identify border regions
    for region_a in faction_a_regions:
        if region_a not in region_borders:
            continue
            
        # Check if this region borders any faction B regions
        for neighbor in region_borders[region_a]:
            if neighbor in faction_b_regions:
                disputed.append(region_a)
                break
                
    # Then add any historically claimed regions
    if historical_claims:
        faction_a_claims = historical_claims.get(faction_a_id, [])
        faction_b_claims = historical_claims.get(faction_b_id, [])
        
        # Add regions controlled by B but claimed by A
        for region in faction_b_regions:
            if region in faction_a_claims and region not in disputed:
                disputed.append(region)
                
        # Add regions controlled by A but claimed by B
        for region in faction_a_regions:
            if region in faction_b_claims and region not in disputed:
                disputed.append(region)
                
    return disputed


def calculate_war_chances(
    tension: float,
    faction_a_traits: Dict[str, Any],
    faction_b_traits: Dict[str, Any]
) -> float:
    """Calculate probability of war declaration.
    
    Args:
        tension: Current tension level between factions (-100 to 100)
        faction_a_traits: Dictionary of faction A traits
        faction_b_traits: Dictionary of faction B traits
        
    Returns:
        float: Probability of war declaration (0.0 to 1.0)
    """
    # Base chance depends on tension level
    if tension < 50:
        return 0.0  # No chance below threshold
        
    # Normalize tension to 0-1 range (50-100 -> 0-1)
    normalized_tension = (tension - 50) / 50
    base_chance = normalized_tension * 0.2  # Max 20% chance at tension 100
    
    # Adjust based on faction traits
    aggression_a = faction_a_traits.get('aggression', 0.0)
    aggression_b = faction_b_traits.get('aggression', 0.0)
    
    # Average aggression factor (0.5 to 2.0)
    aggression_factor = 0.5 + (aggression_a + aggression_b) / 2
    
    # Final chance
    chance = base_chance * aggression_factor
    
    # Cap at reasonable limits
    return max(0.0, min(0.5, chance))


def evaluate_battle_outcome(
    faction_a_id: str,
    faction_b_id: str,
    faction_a_strength: float,
    faction_b_strength: float,
    battle_location: Optional[str] = None,
    home_advantage: float = 1.2
) -> Dict[str, Any]:
    """Evaluate the outcome of a battle between two factions.
    
    Args:
        faction_a_id: ID of the first faction
        faction_b_id: ID of the second faction
        faction_a_strength: Military strength of faction A
        faction_b_strength: Military strength of faction B
        battle_location: Optional ID of region where battle takes place
        home_advantage: Strength multiplier for home territory advantage
        
    Returns:
        Dict containing battle outcome details
    """
    effective_a = faction_a_strength
    effective_b = faction_b_strength
    
    # Apply home advantage if battle location is specified
    # and is controlled by one of the factions
    if battle_location:
        # This would require checking region ownership
        # For demonstration, assuming 50% chance each faction owns the region
        if random.random() < 0.5:
            effective_a *= home_advantage
            home_faction = faction_a_id
        else:
            effective_b *= home_advantage
            home_faction = faction_b_id
    else:
        home_faction = None
        
    # Calculate win probability based on relative strength
    a_win_prob = effective_a / (effective_a + effective_b)
    
    # Apply some randomness
    roll = random.random()
    
    # Determine victor
    if roll < a_win_prob:
        victor = faction_a_id
        loser = faction_b_id
        victor_strength = effective_a
        loser_strength = effective_b
    else:
        victor = faction_b_id
        loser = faction_a_id
        victor_strength = effective_b
        loser_strength = effective_a
        
    # Calculate losses
    # Higher relative strength = fewer losses for victor
    strength_ratio = victor_strength / loser_strength
    victor_loss_pct = random.uniform(0.05, 0.15) / min(2.0, strength_ratio)
    loser_loss_pct = random.uniform(0.15, 0.30) * min(2.0, strength_ratio)
    
    victor_losses = int(victor_strength * victor_loss_pct)
    loser_losses = int(loser_strength * loser_loss_pct)
    
    # Determine battle type
    if loser_losses > loser_strength * 0.25:
        battle_type = "decisive"
    elif loser_losses > loser_strength * 0.15:
        battle_type = "major"
    else:
        battle_type = "minor"
        
    # Create battle outcome
    return {
        "victor": victor,
        "loser": loser,
        "location": battle_location,
        "home_faction": home_faction,
        "victor_losses": victor_losses,
        "loser_losses": loser_losses,
        "battle_type": battle_type,
        "timestamp": datetime.utcnow().isoformat()
    }


def calculate_resource_changes(
    victor_id: str,
    loser_id: str,
    outcome_type: str,
    victor_faction_data: Dict[str, Any],
    loser_faction_data: Dict[str, Any]
) -> Dict[str, Dict[str, int]]:
    """Calculate resource changes resulting from war outcome.
    
    Args:
        victor_id: ID of the victorious faction
        loser_id: ID of the losing faction
        outcome_type: Type of war outcome (decisive_victory, victory, stalemate, etc.)
        victor_faction_data: Data dict for victor faction
        loser_faction_data: Data dict for loser faction
        
    Returns:
        Dict mapping faction IDs to dicts of resource changes
    """
    resource_changes = {
        victor_id: {},
        loser_id: {}
    }
    
    # Extract loser resources
    loser_resources = loser_faction_data.get("resources", {})
    
    # Calculate transfer amount based on outcome type
    if outcome_type == "DECISIVE_VICTORY":
        transfer_pct = 0.30  # 30% of loser's resources
    elif outcome_type == "VICTORY":
        transfer_pct = 0.15  # 15% of loser's resources
    elif outcome_type == "STALEMATE":
        transfer_pct = 0.05  # 5% of loser's resources as reparations
    else:
        transfer_pct = 0.0  # No transfer for ceasefire or white peace
        
    # Calculate transfers
    for resource, amount in loser_resources.items():
        transfer = int(amount * transfer_pct)
        if transfer > 0:
            resource_changes[victor_id][resource] = transfer
            resource_changes[loser_id][resource] = -transfer
            
    # Add war costs to both sides
    war_cost_gold = random.randint(500, 2000)
    war_cost_supplies = random.randint(100, 500)
    
    # Victor pays less in war costs
    victor_cost_multiplier = 0.7 if outcome_type in ["DECISIVE_VICTORY", "VICTORY"] else 0.9
    
    for resource, cost in [("gold", war_cost_gold), ("supplies", war_cost_supplies)]:
        # Deduct costs from victor
        victor_cost = int(cost * victor_cost_multiplier)
        resource_changes[victor_id][resource] = resource_changes[victor_id].get(resource, 0) - victor_cost
        
        # Deduct costs from loser
        loser_cost = cost
        resource_changes[loser_id][resource] = resource_changes[loser_id].get(resource, 0) - loser_cost
            
    return resource_changes 