# from firebase_admin import db  # TODO: Replace with proper database integration
import random
from .npc_loyalty_class import LoyaltyManager

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
            # Use LoyaltyManager to handle loyalty changes
            loyalty_manager = LoyaltyManager(npc_id)
            loyalty_manager.apply_event({"loyalty": -random.randint(1, 2)})
            loyalty_manager.save_to_firebase()

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
