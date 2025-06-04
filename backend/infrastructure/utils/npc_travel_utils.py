# from firebase_admin import db  # TODO: Replace with proper database integration
import random
from datetime import datetime, timedelta
from backend.infrastructure.config_loaders.npc_config_loader import get_npc_config

def simulate_npc_travel(region_name):
    """
    NPCs travel based on their wanderlust value:
    - Wanderlust determines how far, how often, and how long NPCs travel.
    - NPCs with wanderlust 0 never move.
    - Others may temporarily move to nearby POIs or even relocate.
    """
    npc_core = db.reference("/npc_core").get() or {}
    poi_data = db.reference(f"/poi_state/{region_name}").get() or {}

    for npc_id, npc in npc_core.items():
        home_poi = npc.get("home_poi", "")
        if not home_poi.startswith(region_name):
            continue  # only handle NPCs from this region

        wanderlust = npc.get("wanderlust", 0)
        if wanderlust <= 0 or random.random() > (wanderlust / 5.0):
            continue  # not moving this tick

        # Simulate movement
        home_region, home_poi_id = home_poi.split(".")
        all_pois = list(poi_data.keys())
        all_pois.remove(home_poi_id)

        if not all_pois:
            continue

        destination = random.choice(all_pois)
        duration = random.randint(1, wanderlust)  # days away
        may_relocate = wanderlust >= 4 and random.random() < 0.25

        # Set travel data
        travel_record = {
            "current_location": f"{region_name}.{destination}",
            "return_home_day": get_current_game_day() + duration
        }

        if may_relocate:
            travel_record["home_poi"] = f"{region_name}.{destination}"

        db.reference(f"/npc_core/{npc_id}").update(travel_record)

        # Update POI entries
        remove_from_poi(npc_id, home_region, home_poi_id)
        add_to_poi(npc_id, region_name, destination)

def remove_from_poi(npc_id, region, poi_id):
    ref = db.reference(f"/poi_state/{region}/{poi_id}/npcs_present")
    npc_list = ref.get() or []
    if npc_id in npc_list:
        npc_list.remove(npc_id)
        ref.set(npc_list)

def add_to_poi(npc_id, region, poi_id):
    ref = db.reference(f"/poi_state/{region}/{poi_id}/npcs_present")
    npc_list = ref.get() or []
    if npc_id not in npc_list:
        npc_list.append(npc_id)
        ref.set(npc_list)

def get_current_game_day():
    return db.reference("/global_state").get().get("current_day", 0)

def apply_war_pressure_modifiers():
    """
    NPCs react to nearby war zones:
    - Increase faction bias if controlled POI shifts hands
    - Decrease loyalty if home POI is at war
    - Chance to migrate if wanderlust allows
    """
    npc_core = db.reference("/npc_core").get() or {}

    for npc_id, npc in npc_core.items():
        home_poi = npc.get("home_poi", "")
        wanderlust = npc.get("wanderlust", 0)

        if not home_poi or "." not in home_poi:
            continue

        region, poi_id = home_poi.split(".")
        region_data = db.reference(f"/regional_state/{region}").get() or {}
        conflict_status = region_data.get("conflict_status", "peace")

        # Faster loyalty decay under war
        if conflict_status == "war":
            # TODO: Integrate with loyalty system without circular dependencies
            # Use LoyaltyManager to handle loyalty changes
            # loyalty_manager = LoyaltyManager(npc_id)
            # loyalty_manager.apply_event({"loyalty": -random.randint(1, 2)})
            # loyalty_manager.save_to_firebase()
            pass

        # Drift faction bias toward dominant faction
        war_data = region_data.get("war_state", {})
        active_faction = war_data.get("active_faction")
        if active_faction:
            bias_ref = db.reference(f"/npc_opinion_matrix/{npc_id}/{npc_id}/faction_bias")
            bias_data = bias_ref.get() or {}
            bias_data[active_faction] = bias_data.get(active_faction, 0) + random.randint(1, 2)
            bias_ref.set(bias_data)

        # Chance to migrate
        if wanderlust >= 2 and random.random() < (wanderlust / 10.0):
            migrate_npc_to_safe_poi(npc_id, region, poi_id)

def migrate_npc_to_safe_poi(npc_id, region, current_poi_id):
    poi_data = db.reference(f"/poi_state/{region}").get() or {}
    safe_pois = [pid for pid, data in poi_data.items()
                 if data.get("poi_type") == "social" and pid != current_poi_id]

    if not safe_pois:
        return

    target = random.choice(safe_pois)

    # Update NPC state
    db.reference(f"/npc_core/{npc_id}/home_poi").set(f"{region}.{target}")
    db.reference(f"/npc_core/{npc_id}/current_location").set(f"{region}.{target}")

    # Move in POI lists
    remove_from_poi(npc_id, region, current_poi_id)
    add_to_poi(npc_id, region, target)

def calculate_travel_chance(npc_data, world_context=None):
    """
    Calculate the chance an NPC will travel based on their wanderlust level,
    NPC type, and current world events.
    """
    config = get_npc_config()
    travel_config = config.get_travel_behaviors_config()
    
    wanderlust = npc_data.get('wanderlust', 0)
    npc_type = npc_data.get('npc_type', 'unknown')
    
    # Get base travel chance from wanderlust
    wanderlust_behavior = travel_config.get('wanderlust_behaviors', {}).get(str(wanderlust), {})
    base_chance = wanderlust_behavior.get('travel_chance', 0.0)
    
    # Apply NPC type modifiers
    type_modifiers = travel_config.get('npc_type_travel_modifiers', {})
    type_config = type_modifiers.get(npc_type, {})
    chance_modifier = type_config.get('travel_chance_modifier', 1.0)
    
    final_chance = base_chance * chance_modifier
    
    # Apply world context modifiers
    if world_context:
        special_events = travel_config.get('special_events', {})
        for event, effect in special_events.items():
            if world_context.get(event):
                boost = effect.get('travel_chance_boost', 1.0)
                modifier = effect.get('travel_chance_modifier', 1.0)
                final_chance = (final_chance * modifier) + boost - 1.0
    
    return min(1.0, max(0.0, final_chance))

def get_max_travel_distance(npc_data):
    """Get maximum travel distance for an NPC based on wanderlust and type"""
    config = get_npc_config()
    travel_config = config.get_travel_behaviors_config()
    
    wanderlust = npc_data.get('wanderlust', 0)
    npc_type = npc_data.get('npc_type', 'unknown')
    
    # Get base distance from wanderlust
    wanderlust_behavior = travel_config.get('wanderlust_behaviors', {}).get(str(wanderlust), {})
    base_distance = wanderlust_behavior.get('max_distance', 0)
    
    # Apply NPC type modifiers
    type_modifiers = travel_config.get('npc_type_travel_modifiers', {})
    type_config = type_modifiers.get(npc_type, {})
    distance_modifier = type_config.get('max_distance_modifier', 1.0)
    
    return int(base_distance * distance_modifier)

def select_travel_destination(npc_data, available_pois, world_context=None):
    """
    Select a destination POI for an NPC based on their preferences and world state.
    """
    config = get_npc_config()
    travel_config = config.get_travel_behaviors_config()
    
    npc_type = npc_data.get('npc_type', 'unknown')
    
    # Get POI preferences
    poi_preferences = travel_config.get('poi_preferences', {})
    type_modifiers = travel_config.get('npc_type_travel_modifiers', {})
    type_config = type_modifiers.get(npc_type, {})
    preferred_pois = type_config.get('preferred_pois', [])
    
    # Calculate weights for each available POI
    poi_weights = {}
    for poi in available_pois:
        poi_type = poi.get('type', 'unknown')
        
        # Base weight
        weight = 1.0
        
        # Apply category preferences
        for category, pois in poi_preferences.items():
            if poi_type in pois:
                weight *= pois[poi_type]
                break
        
        # Apply type preferences
        if poi_type in preferred_pois:
            weight *= 1.5
        
        # Apply world context effects
        if world_context:
            special_events = travel_config.get('special_events', {})
            for event, effect in special_events.items():
                if world_context.get(event):
                    attractions = effect.get('poi_attraction', {})
                    avoidance = effect.get('poi_avoidance', {})
                    
                    if poi_type in attractions:
                        weight *= attractions[poi_type]
                    elif poi_type in avoidance:
                        weight *= avoidance[poi_type]
        
        poi_weights[poi['id']] = weight
    
    # Weighted random selection
    if not poi_weights:
        return None
    
    total_weight = sum(poi_weights.values())
    if total_weight <= 0:
        return random.choice(available_pois)['id']
    
    rand_val = random.uniform(0, total_weight)
    current_weight = 0
    
    for poi_id, weight in poi_weights.items():
        current_weight += weight
        if rand_val <= current_weight:
            return poi_id
    
    # Fallback
    return random.choice(available_pois)['id']

def apply_war_pressure(npc_data, faction_data, war_context):
    """
    Apply war pressure effects to NPC loyalty and migration behavior.
    """
    config = get_npc_config()
    travel_config = config.get_travel_behaviors_config()
    war_config = travel_config.get('war_responses', {})
    
    # Get current loyalty data
    loyalty_data = npc_data.get('loyalty', {})
    
    # Apply loyalty decay during war
    decay_range = war_config.get('loyalty_decay_rate', {'min': 1, 'max': 2})
    decay_amount = random.randint(decay_range['min'], decay_range['max'])
    
    current_goodwill = loyalty_data.get('goodwill', 18)
    new_goodwill = max(0, current_goodwill - decay_amount)
    
    # Check migration threshold
    migration_threshold = war_config.get('migration_threshold', 2)
    should_migrate = new_goodwill <= migration_threshold
    
    # Update faction bias if applicable
    npc_factions = npc_data.get('faction_affiliations', [])
    faction_bias = war_config.get('faction_bias_increase', {'min': 1, 'max': 2})
    
    for faction_id in npc_factions:
        if faction_id in war_context.get('allied_factions', []):
            # Increase loyalty to allied factions
            bias_increase = random.randint(faction_bias['min'], faction_bias['max'])
            # This would be applied to faction-specific loyalty tracking
    
    return {
        'should_migrate': should_migrate,
        'new_goodwill': new_goodwill,
        'migration_reason': 'war_pressure' if should_migrate else None
    }

def get_travel_duration(npc_data):
    """Calculate how long an NPC should stay away from home"""
    config = get_npc_config()
    travel_config = config.get_travel_behaviors_config()
    
    wanderlust = npc_data.get('wanderlust', 0)
    npc_type = npc_data.get('npc_type', 'unknown')
    
    # Get base duration from wanderlust
    duration_config = travel_config.get('travel_duration', {})
    base_days = duration_config.get('base_days', {})
    wanderlust_key = f'wanderlust_{wanderlust}'
    
    if wanderlust_key in base_days:
        day_range = base_days[wanderlust_key]
        base_duration = random.randint(day_range['min'], day_range['max'])
    else:
        base_duration = 1
    
    # Apply NPC type modifiers
    type_modifiers = duration_config.get('modifiers', {})
    type_modifier = type_modifiers.get(npc_type, 1.0)
    
    return int(base_duration * type_modifier)

def should_return_home(npc_data, days_away):
    """Check if NPC should return home based on time away and other factors"""
    config = get_npc_config()
    travel_config = config.get_travel_behaviors_config()
    return_config = travel_config.get('return_home_mechanics', {})
    
    # Forced return threshold
    forced_threshold = return_config.get('forced_return_threshold', 14)
    if days_away >= forced_threshold:
        return True
    
    # Calculate homesickness factor
    homesickness = return_config.get('homesickness_factor', 0.1)
    time_penalty = return_config.get('time_away_penalty', 0.02)
    
    return_chance = homesickness + (days_away * time_penalty)
    
    return random.random() < return_chance
