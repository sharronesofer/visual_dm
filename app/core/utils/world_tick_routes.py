#This module defines the /advance_day endpoint, which acts as the core simulation heartbeat for daily progression. It updates:
#Faction territory influence
#NPC faction alignment
#NPC emotional motif pressure
#Global tick timestamp
#It connects with npc, motif, faction, chaos, region, and world systems.

from flask import Blueprint, jsonify
from app.factions.faction_tick_utils import propagate_faction_influence
from app.npcs.npc_loyalty_utils import drift_npc_faction_opinions
from app.motifs.motif_engine_class import MotifEngine
from firebase_admin import db
from datetime import datetime

world_tick_bp = Blueprint("world_tick", __name__)

@world_tick_bp.route("/advance_day", methods=["POST"])
def advance_day():
    # === Faction Expansion ===
    propagate_faction_influence()

    # === NPC Faction Opinion Drift ===
    drift_npc_faction_opinions()

    # === NPC Motif Tick (Daily) ===
    all_npcs = db.reference("/npcs").get() or {}
    for npc_id in all_npcs:
        engine = MotifEngine(npc_id)
        engine.tick_all().rotate().save()

    # === Timestamp
    db.reference("/global_state/last_tick").set(datetime.utcnow().isoformat())

    return jsonify({"message": "World tick complete — day advanced."})
