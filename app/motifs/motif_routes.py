from flask import Blueprint, request, jsonify
from app.motifs.motif_engine_class import MotifEngine
from app.motifs.chaos_utils import trigger_chaos_if_needed, force_chaos

motif_bp = Blueprint("motif", __name__)

# === MOTIF ENDPOINTS ===

@motif_bp.route("/motif/<npc_id>/init", methods=["POST"])
def init_motifs(npc_id):
    engine = MotifEngine(npc_id)
    engine.initialize().save()
    return jsonify({"message": f"Motifs initialized for {npc_id}", "pool": engine.get_pool()})


@motif_bp.route("/motif/<npc_id>/tick_daily", methods=["POST"])
def tick_daily(npc_id):
    engine = MotifEngine(npc_id)
    engine.tick_all().rotate().save()
    return jsonify({"message": f"Daily tick completed for {npc_id}", "pool": engine.get_pool()})


@motif_bp.route("/motif/<npc_id>/tick_longrest", methods=["POST"])
def tick_long_rest(npc_id):
    engine = MotifEngine(npc_id)
    engine.tick_random(chance=20).rotate().save()
    return jsonify({"message": f"Long rest tick (with entropy) processed for {npc_id}", "pool": engine.get_pool()})


@motif_bp.route("/motif/<npc_id>/describe", methods=["GET"])
def describe_motifs(npc_id):
    engine = MotifEngine(npc_id)
    return jsonify(engine.describe())


# === CHAOS TRIGGERS ===

@motif_bp.route("/chaos/<npc_id>/trigger", methods=["POST"])
def trigger_chaos(npc_id):
    region = request.json.get("region")
    result = trigger_chaos_if_needed(npc_id, region)
    return jsonify(result)


@motif_bp.route("/chaos/<npc_id>/force", methods=["POST"])
def force_chaos_endpoint(npc_id):
    region = request.json.get("region")
    result = force_chaos(npc_id, region)
    return jsonify(result)
