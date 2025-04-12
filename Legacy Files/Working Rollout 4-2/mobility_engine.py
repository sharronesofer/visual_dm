from firebase_admin import db
import random
import math
from datetime import datetime

def update_npc_location(npc_id):
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc = npc_ref.get()

    if not npc:
        return {"error": "NPC not found"}

    mobility = npc.get("mobility", {})
    home = mobility.get("home_poi")
    current = mobility.get("current_poi", home)
    radius = mobility.get("radius", 1)
    travel_chance = mobility.get("travel_chance", 0.15)

    if random.random() > travel_chance:
        return {"npc_id": npc_id, "stayed": True}

    # Find all POIs within range
    all_pois = db.reference("/locations").get() or {}
    valid = []

    try:
        cx, cy = map(int, current.split("_"))
    except:
        return {"error": "Invalid current_poi"}

    for key, poi in all_pois.items():
        if not poi.get("POI"):
            continue
        try:
            x, y = map(int, key.split("_"))
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            if 0 < dist <= radius:
                valid.append(key)
        except:
            continue

    if not valid:
        return {"npc_id": npc_id, "stayed": True, "reason": "no valid POIs"}

    new_location = random.choice(valid)
    npc["mobility"]["current_poi"] = new_location
    npc["mobility"]["last_moved"] = datetime.utcnow().isoformat()
    npc_ref.set(npc)

    return {"npc_id": npc_id, "moved_to": new_location}
