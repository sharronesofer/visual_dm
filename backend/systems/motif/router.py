from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query

from .models import (
    Motif, MotifCreate, MotifUpdate, MotifFilter, 
    MotifScope, MotifLifecycle, MotifResponse
)
from .service import MotifService
from .repository import MotifRepository, Vector2

router = APIRouter(prefix="/motifs", tags=["motifs"])

# Dependency to get MotifService instance
def get_motif_service():
    """Dependency to get MotifService instance."""
    repository = MotifRepository()
    return MotifService(repository)

@router.post("/", response_model=Motif)
async def create_motif(
    motif: MotifCreate, 
    service: MotifService = Depends(get_motif_service)
):
    """Create a new motif."""
    return await service.create_motif(motif)

@router.get("/", response_model=List[Motif])
async def list_motifs(
    category: Optional[str] = None,
    scope: Optional[str] = None,
    lifecycle: Optional[str] = None,
    min_intensity: Optional[float] = None,
    max_intensity: Optional[float] = None,
    region_id: Optional[str] = None,
    effect_type: Optional[str] = None,
    active_only: bool = True,
    service: MotifService = Depends(get_motif_service)
):
    """List motifs with optional filtering."""
    filter_params = MotifFilter(
        category=category,
        scope=scope,
        lifecycle=lifecycle,
        min_intensity=min_intensity,
        max_intensity=max_intensity,
        region_id=region_id,
        effect_type=effect_type,
        active_only=active_only
    )
    return await service.list_motifs(filter_params)

@router.get("/{motif_id}", response_model=Motif)
async def get_motif(
    motif_id: int, 
    service: MotifService = Depends(get_motif_service)
):
    """Get a specific motif by ID."""
    motif = await service.get_motif(motif_id)
    if not motif:
        raise HTTPException(status_code=404, detail="Motif not found")
    return motif

@router.put("/{motif_id}", response_model=Motif)
async def update_motif(
    motif_id: int, 
    motif: MotifUpdate,
    service: MotifService = Depends(get_motif_service)
):
    """Update a motif."""
    updated_motif = await service.update_motif(motif_id, motif)
    if not updated_motif:
        raise HTTPException(status_code=404, detail="Motif not found")
    return updated_motif

@router.delete("/{motif_id}", response_model=MotifResponse)
async def delete_motif(
    motif_id: int, 
    service: MotifService = Depends(get_motif_service)
):
    """Delete a motif."""
    result = await service.delete_motif(motif_id)
    if not result:
        raise HTTPException(status_code=404, detail="Motif not found")
    return MotifResponse(
        success=True,
        message=f"Motif {motif_id} deleted successfully",
        data=None
    )

@router.get("/global", response_model=List[Motif])
async def get_global_motifs(
    service: MotifService = Depends(get_motif_service)
):
    """Get all active global motifs."""
    return await service.get_global_motifs()

@router.get("/region/{region_id}", response_model=List[Motif])
async def get_region_motifs(
    region_id: str, 
    service: MotifService = Depends(get_motif_service)
):
    """Get all active motifs for a specific region."""
    return await service.get_regional_motifs(region_id)

@router.get("/position", response_model=List[Motif])
async def get_motifs_at_position(
    x: float,
    y: float,
    radius: float = 0,
    service: MotifService = Depends(get_motif_service)
):
    """Get all motifs that affect a specific position."""
    return await service.get_motifs_at_position(x, y, radius)

@router.get("/context", response_model=Dict[str, Any])
async def get_motif_context(
    x: Optional[float] = None,
    y: Optional[float] = None,
    region_id: Optional[str] = None,
    service: MotifService = Depends(get_motif_service)
):
    """
    Get a context dictionary describing the active motifs at a position or region.
    This is useful for narrative generation.
    """
    return await service.get_motif_context(x, y, region_id)

@router.post("/random", response_model=Motif)
async def generate_random_motif(
    scope: MotifScope,
    region_id: Optional[str] = None,
    service: MotifService = Depends(get_motif_service)
):
    """Generate a random motif with specified scope."""
    return await service.generate_random_motif(scope, region_id)

@router.post("/advance-lifecycles", response_model=MotifResponse)
async def advance_motif_lifecycles(
    service: MotifService = Depends(get_motif_service)
):
    """
    Advance the lifecycle of all motifs based on time.
    Returns the count of updated motifs.
    """
    count = await service.advance_motif_lifecycles()
    return MotifResponse(
        success=True,
        message=f"Advanced {count} motifs to new lifecycle states",
        data={"count": count}
    )

@router.post("/blend", response_model=Dict[str, Any])
async def blend_motifs(
    motif_ids: List[int],
    service: MotifService = Depends(get_motif_service)
):
    """
    Blend multiple motifs to create a composite narrative effect.
    Returns a dictionary with the blended narrative context.
    """
    motifs = []
    for motif_id in motif_ids:
        motif = await service.get_motif(motif_id)
        if motif:
            motifs.append(motif)
    
    if not motifs:
        raise HTTPException(status_code=404, detail="No valid motifs found")
    
    blend = await service.blend_motifs(motifs)
    if not blend:
        raise HTTPException(status_code=400, detail="Failed to blend motifs")
    
    return blend

@router.post("/sequences/generate", response_model=Dict[str, Any])
async def generate_motif_sequence(
    sequence_length: int = Query(3, ge=2, le=10),
    category: Optional[str] = None,
    region_id: Optional[str] = None,
    progressive_intensity: bool = True
):
    """
    Generate a sequence of thematically related motifs for long-term narrative arcs.
    
    Parameters:
    - sequence_length: Number of motifs in the sequence (2-10)
    - category: Optional specific starting category
    - region_id: Optional region ID for regional motifs
    - progressive_intensity: If True, intensity will increase through the sequence
    
    Returns the generated sequence of motifs along with metadata.
    """
    # Get the motif manager
    from .manager import MotifManager
    manager = MotifManager.get_instance()
    
    # Convert category string to enum if provided
    starting_category = None
    if category:
        try:
            starting_category = MotifCategory(category.lower())
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid category: {category}. Must be one of: {[c.value for c in MotifCategory]}"
            )
    
    # Generate the sequence
    motifs = await manager.generate_motif_sequence(
        sequence_length=sequence_length,
        starting_category=starting_category,
        region_id=region_id,
        progressive_intensity=progressive_intensity
    )
    
    return {
        "sequence_id": motifs[0].metadata["sequence_id"],
        "length": len(motifs),
        "progression": [
            {
                "id": m.id,
                "name": m.name,
                "category": m.category.value,
                "intensity": m.intensity,
                "lifecycle": m.lifecycle.value,
                "position": i + 1,
                "is_active": m.lifecycle != MotifLifecycle.DORMANT
            }
            for i, m in enumerate(motifs)
        ],
        "motifs": [m.dict() for m in motifs]
    }

@router.get("/sequences/{sequence_id}", response_model=Dict[str, Any])
async def get_motif_sequence(sequence_id: str):
    """
    Get all motifs that are part of a specific sequence.
    
    Parameters:
    - sequence_id: The unique identifier for the sequence
    
    Returns all motifs in the sequence with their progression info.
    """
    # Get the motif manager
    from .manager import MotifManager
    manager = MotifManager.get_instance()
    
    # Get all motifs with this sequence ID
    motifs = await manager.get_motifs(MotifFilter(
        metadata={"sequence_id": sequence_id}
    ))
    
    if not motifs:
        raise HTTPException(status_code=404, detail=f"Sequence '{sequence_id}' not found")
    
    # Sort by sequence position
    motifs.sort(key=lambda m: m.metadata.get("sequence_position", 0))
    
    return {
        "sequence_id": sequence_id,
        "length": len(motifs),
        "current_position": next((i+1 for i, m in enumerate(motifs) 
                                 if m.lifecycle != MotifLifecycle.DORMANT), 1),
        "progression": [
            {
                "id": m.id,
                "name": m.name,
                "category": m.category.value,
                "intensity": m.intensity,
                "lifecycle": m.lifecycle.value,
                "position": i + 1,
                "is_active": m.lifecycle != MotifLifecycle.DORMANT
            }
            for i, m in enumerate(motifs)
        ],
        "motifs": [m.dict() for m in motifs]
    }

@router.post("/sequences/{sequence_id}/advance", response_model=Dict[str, Any])
async def advance_motif_sequence(sequence_id: str, force: bool = False):
    """
    Advance a motif sequence to its next step.
    
    This moves the sequence forward by:
    1. Setting the current active motif to waning/dormant
    2. Activating the next motif in the sequence
    
    Parameters:
    - sequence_id: The unique identifier for the sequence
    - force: If True, force the advancement even if the current motif isn't ready to transition
    
    Returns the updated sequence info.
    """
    # Get the motif manager
    from .manager import MotifManager
    manager = MotifManager.get_instance()
    
    # Get all motifs with this sequence ID
    motifs = await manager.get_motifs(MotifFilter(
        metadata={"sequence_id": sequence_id}
    ))
    
    if not motifs:
        raise HTTPException(status_code=404, detail=f"Sequence '{sequence_id}' not found")
    
    # Sort by sequence position
    motifs.sort(key=lambda m: m.metadata.get("sequence_position", 0))
    
    # Find the currently active motif
    active_index = next((i for i, m in enumerate(motifs) 
                      if m.lifecycle != MotifLifecycle.DORMANT), None)
    
    if active_index is None:
        # No active motifs - activate the first one
        if motifs:
            await manager.update_motif(
                motifs[0].id,
                MotifUpdate(lifecycle=MotifLifecycle.EMERGING)
            )
    else:
        # Check if there's a next motif to activate
        if active_index < len(motifs) - 1:
            # Set current motif to waning
            current_motif = motifs[active_index]
            if current_motif.lifecycle != MotifLifecycle.WANING or force:
                await manager.update_motif(
                    current_motif.id,
                    MotifUpdate(lifecycle=MotifLifecycle.WANING)
                )
            
            # Activate next motif
            next_motif = motifs[active_index + 1]
            await manager.update_motif(
                next_motif.id,
                MotifUpdate(lifecycle=MotifLifecycle.EMERGING)
            )
        else:
            # This is the last motif - just set to waning if not already
            current_motif = motifs[active_index]
            if current_motif.lifecycle != MotifLifecycle.WANING or force:
                await manager.update_motif(
                    current_motif.id,
                    MotifUpdate(lifecycle=MotifLifecycle.WANING)
                )
    
    # Get updated sequence
    motifs = await manager.get_motifs(MotifFilter(
        metadata={"sequence_id": sequence_id}
    ))
    motifs.sort(key=lambda m: m.metadata.get("sequence_position", 0))
    
    return {
        "sequence_id": sequence_id,
        "length": len(motifs),
        "current_position": next((i+1 for i, m in enumerate(motifs) 
                                 if m.lifecycle != MotifLifecycle.DORMANT), 1),
        "progression": [
            {
                "id": m.id,
                "name": m.name,
                "category": m.category.value,
                "intensity": m.intensity,
                "lifecycle": m.lifecycle.value,
                "position": i + 1,
                "is_active": m.lifecycle != MotifLifecycle.DORMANT
            }
            for i, m in enumerate(motifs)
        ],
        "status": "advanced"
    }

# ==== Chaos-related Endpoints ====

@router.get("/chaos/event", tags=["motifs", "chaos"])
async def get_random_chaos_event():
    """Get a random chaos event from the predefined table."""
    manager = get_motif_manager()
    return {"event": manager.roll_chaos_event()}

@router.post("/chaos/inject", tags=["motifs", "chaos"])
async def inject_chaos_event(
    event_type: Optional[str] = None,
    region_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
):
    """Inject a chaos event into the world."""
    manager = get_motif_manager()
    
    # If no event type specified, generate a random one
    if not event_type:
        event_type = manager.roll_chaos_event()
    
    event = await manager.inject_chaos_event(event_type, region_id, context)
    return {"success": True, "event": event}

@router.post("/chaos/trigger/{entity_id}", tags=["motifs", "chaos"])
async def trigger_chaos_if_needed(
    entity_id: str,
    region_id: Optional[str] = None
):
    """Check if chaos should be triggered based on entity's motif state and trigger if needed."""
    manager = get_motif_manager()
    result = await manager.trigger_chaos_if_needed(entity_id, region_id)
    return result

@router.post("/chaos/force/{entity_id}", tags=["motifs", "chaos"])
async def force_chaos(
    entity_id: str,
    region_id: Optional[str] = None
):
    """Force a chaos event to occur for an entity, regardless of current motif state."""
    manager = get_motif_manager()
    result = await manager.force_chaos(entity_id, region_id)
    return result

@router.get("/chaos/log", tags=["motifs", "chaos"])
async def get_chaos_log(
    limit: int = 10,
    offset: int = 0
):
    """Get the most recent chaos events from the world log."""
    manager = get_motif_manager()
    repository = manager.repository
    events = await repository.get_world_log_events("narrative_chaos", limit, offset)
    return {"events": events}

@router.get("/narrative-context", response_model=Dict[str, Any])
async def get_narrative_context(
    x: Optional[float] = None,
    y: Optional[float] = None,
    region_id: Optional[str] = None,
    from_manager: bool = True
):
    """
    Get enhanced narrative context information based on active motifs.
    This is optimized for direct use in GPT prompts for narrative generation.
    
    Parameters:
    - x, y: Optional coordinates to get context for a specific location
    - region_id: Optional region ID to get context for a specific region
    - from_manager: If True, use the MotifManager's enhanced context; otherwise use basic service context
    
    Returns a rich context dictionary with themes, tone, and narrative guidance.
    """
    if from_manager:
        # Use enhanced context from manager
        from .manager import MotifManager
        manager = MotifManager.get_instance()
        return await manager.get_narrative_context(x, y, region_id)
    else:
        # Use basic context from service
        service = get_motif_service()
        return await service.get_motif_context(x, y, region_id)

@router.post("/apply-effects/{motif_id}", response_model=Dict[str, Any])
async def apply_motif_effects(
    motif_id: int,
    target_systems: Optional[List[str]] = None
):
    """
    Manually apply a motif's effects to target systems.
    
    Parameters:
    - motif_id: ID of the motif to apply
    - target_systems: Optional list of systems to target. If not provided, all systems will be affected.
      Possible values: "npc", "event", "quest", "faction", "environment", "economy", "narrative"
    
    Returns the results of applying the motif effects.
    """
    # Get the motif manager
    from .manager import MotifManager
    manager = MotifManager.get_instance()
    
    # Get the motif
    motif = await manager.get_motif(motif_id)
    if not motif:
        raise HTTPException(status_code=404, detail=f"Motif with ID {motif_id} not found")
    
    # Apply the effects
    results = await manager.apply_motif_effects(motif, target_systems)
    
    return {
        "motif_id": motif_id,
        "motif_name": motif.name,
        "results": results
    }

@router.post("/batch/apply-effects", response_model=Dict[str, Any])
async def apply_all_active_motif_effects(
    target_systems: Optional[List[str]] = None,
    scope: Optional[MotifScope] = None,
    region_id: Optional[str] = None
):
    """
    Apply effects for all active motifs, optionally filtered by scope and region.
    
    Parameters:
    - target_systems: Optional list of systems to target. If not provided, all systems will be affected.
    - scope: Optional scope filter (GLOBAL, REGIONAL, LOCAL)
    - region_id: Optional region ID filter
    
    Returns a summary of all applied effects.
    """
    # Get the motif manager
    from .manager import MotifManager
    manager = MotifManager.get_instance()
    
    # Build filter
    filter_params = MotifFilter(
        scope=scope,
        region_id=region_id,
        lifecycle=[MotifLifecycle.EMERGING, MotifLifecycle.STABLE, MotifLifecycle.WANING],
        active_only=True
    )
    
    # Get active motifs
    motifs = await manager.get_motifs(filter_params)
    
    # Apply effects for each motif
    results = {}
    for motif in motifs:
        motif_results = await manager.apply_motif_effects(motif, target_systems)
        results[str(motif.id)] = {
            "name": motif.name,
            "category": motif.category.value,
            "results": motif_results
        }
    
    return {
        "applied_count": len(results),
        "results": results
    }

@router.get("/gpt-context", response_model=Dict[str, Any])
async def get_gpt_context(
    entity_id: Optional[str] = None,
    region_id: Optional[str] = None,
    x: Optional[float] = None,
    y: Optional[float] = None,
    context_size: str = Query("medium", enum=["small", "medium", "large"])
):
    """
    Generate a comprehensive GPT context for narrative generation, incorporating motifs
    with entity data, location, region, and world state.
    
    Parameters:
    - entity_id: Optional ID of entity (character, NPC, etc.) to include specific context for
    - region_id: Optional region ID for regional context
    - x, y: Optional coordinates for positional context
    - context_size: Size of context to generate ('small', 'medium', 'large')
    
    Returns a rich context dictionary formatted for direct use in GPT prompts.
    """
    # Get the motif manager
    from .manager import MotifManager
    manager = MotifManager.get_instance()
    
    # Prepare location data if coordinates provided
    location = None
    if x is not None and y is not None:
        location = {"x": x, "y": y}
    
    # Get the contextualized GPT context
    context = await manager.get_gpt_context(
        entity_id=entity_id,
        location=location,
        region_id=region_id,
        context_size=context_size
    )
    
    return context

@router.post("/generate-event", response_model=Dict[str, Any], tags=["motifs", "events"])
async def generate_world_event(
    region_id: Optional[str] = None,
    x: Optional[float] = None,
    y: Optional[float] = None,
    event_type: Optional[str] = None
):
    """
    Generate a world event influenced by active motifs in the specified region or location.
    
    Parameters:
    - region_id: Optional region ID to place the event
    - x, y: Optional coordinates to place the event
    - event_type: Optional specific event type to generate, otherwise random
    
    Returns a world event with narrative context influenced by active motifs.
    """
    # Get the motif manager
    from .manager import MotifManager
    manager = MotifManager.get_instance()
    
    # Convert coordinates if provided
    coordinates = None
    if x is not None and y is not None:
        coordinates = (x, y)
    
    # Generate the event
    event = await manager.generate_world_event(
        region_id=region_id,
        coordinates=coordinates,
        event_type=event_type
    )
    
    return event 