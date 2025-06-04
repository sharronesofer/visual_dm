#This route module provides endpoints for motif initialization, progression ticks, and chaos triggering for NPCs. It interfaces directly with the MotifEngine, allowing simulation ticks and developer control.
#It is deeply integrated with motif, npc, chaos, and narrative systems.

from fastapi import APIRouter, Request, Depends
from backend.systems.motif.services.motif_engine_class import MotifEngine
from backend.systems.motif.utils.chaos_utils import trigger_chaos_if_needed, force_chaos

motif_router = APIRouter(prefix="/motif", tags=["motif"])

# === MOTIF ENDPOINTS ===

@motif_router.post("/{npc_id}/init")
def init_motifs(npc_id: str):
    engine = MotifEngine(npc_id)
    engine.initialize().save()
    return {"message": f"Motifs initialized for {npc_id}", "pool": engine.get_pool()}

@motif_router.post("/{npc_id}/tick_daily")
def tick_daily(npc_id: str):
    engine = MotifEngine(npc_id)
    engine.tick().rotate().save()
    return {"message": f"Daily tick completed for {npc_id}", "pool": engine.get_pool()}

@motif_router.post("/{npc_id}/tick_longrest")
def tick_long_rest(npc_id: str):
    engine = MotifEngine(npc_id)
    engine.tick_random(chance=20).rotate().save()
    return {"message": f"Long rest tick (with entropy) processed for {npc_id}", "pool": engine.get_pool()}

# === CHAOS TRIGGERS ===

@motif_router.post("/chaos/{npc_id}/trigger")
def trigger_chaos(npc_id: str, request: Request):
    # Note: In FastAPI, we'd typically use a Pydantic model for the body
    # For now, using Request to access JSON body
    region = request.json().get("region") if hasattr(request, 'json') else None
    result = trigger_chaos_if_needed(npc_id, region)
    return result