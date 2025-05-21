from typing import List, Dict, Optional, Union, Any, Tuple
from datetime import datetime, timedelta
import logging
import random
import asyncio
from pathlib import Path
from uuid import uuid4

from .models import (
    Motif, MotifCreate, MotifUpdate, MotifFilter, 
    MotifScope, MotifLifecycle, MotifCategory, MotifEffect,
    LocationInfo
)
from .service import MotifService
from .repository import MotifRepository, Vector2
from .utils import (
    generate_motif_name, generate_motif_description,
    estimate_motif_compatibility, generate_realistic_duration,
    motif_to_narrative_context, calculate_motif_spread,
    roll_chaos_event, NARRATIVE_CHAOS_TABLE  # Import the table from utils
)

logger = logging.getLogger(__name__)

class MotifManager:
    """
    Manager class for the Motif system that handles high-level operations
    and coordinates with other systems through events.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls, data_path: str = None) -> 'MotifManager':
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls(data_path)
        return cls._instance
    
    def __init__(self, data_path: str = None):
        """Initialize the MotifManager."""
        if MotifManager._instance is not None:
            logger.warning("MotifManager should be accessed via get_instance()")
        
        self.repository = MotifRepository(data_path)
        self.service = MotifService(self.repository)
        
        # Cache for active motifs to avoid frequent disk I/O
        self._active_motifs_cache = None
        self._cache_timestamp = None
        self._cache_valid_duration = timedelta(minutes=5)
        
        # Event listeners
        self._event_listeners = []
        
        # Background tasks
        self._background_tasks = set()
        
        logger.info("MotifManager initialized")
    
    # ==== Core Motif Operations ====
    
    async def create_motif(self, motif_data: Union[Dict[str, Any], MotifCreate]) -> Motif:
        """
        Create a new motif. If motif_data is a dict, it will be converted to a MotifCreate object.
        Returns the created motif.
        """
        if isinstance(motif_data, dict):
            # If name is not provided, generate one
            if "name" not in motif_data and "category" in motif_data and "scope" in motif_data:
                category = MotifCategory(motif_data["category"])
                scope = MotifScope(motif_data["scope"])
                motif_data["name"] = generate_motif_name(category, scope)
            
            # If description is not provided, generate one
            if "description" not in motif_data and "category" in motif_data and "scope" in motif_data and "intensity" in motif_data:
                category = MotifCategory(motif_data["category"])
                scope = MotifScope(motif_data["scope"])
                intensity = float(motif_data["intensity"])
                motif_data["description"] = generate_motif_description(category, scope, intensity)
            
            # Create the proper MotifCreate object
            motif_data = MotifCreate(**motif_data)
        
        # Create the motif
        motif = await self.service.create_motif(motif_data)
        
        # Invalidate cache
        self._invalidate_cache()
        
        # Emit event for the new motif
        await self._emit_event("motif_created", {"motif": motif.dict()})
        
        return motif
    
    async def get_motifs(self, filter_params: Union[Dict[str, Any], MotifFilter, None] = None) -> List[Motif]:
        """
        Get all motifs matching the filter criteria.
        If filter_params is a dict, it will be converted to a MotifFilter object.
        """
        # Use cached motifs if available and valid
        if self._should_use_cache() and filter_params is None:
            return self._active_motifs_cache
        
        # Convert dict to filter object if needed
        if isinstance(filter_params, dict):
            filter_params = MotifFilter(**filter_params)
        
        motifs = await self.service.get_motifs(filter_params)
        
        # Cache results if no filter was applied
        if filter_params is None:
            self._active_motifs_cache = motifs
            self._cache_timestamp = datetime.now()
        
        return motifs
    
    async def get_motif(self, motif_id: str) -> Optional[Motif]:
        """Get a specific motif by ID."""
        return await self.service.get_motif(motif_id)
    
    async def update_motif(self, motif_id: str, update_data: Union[Dict[str, Any], MotifUpdate]) -> Optional[Motif]:
        """
        Update an existing motif. If update_data is a dict, it will be converted to a MotifUpdate object.
        Returns the updated motif, or None if motif was not found.
        """
        if isinstance(update_data, dict):
            update_data = MotifUpdate(**update_data)
        
        motif = await self.service.update_motif(motif_id, update_data)
        
        if motif:
            # Invalidate cache
            self._invalidate_cache()
            
            # Emit event for the updated motif
            await self._emit_event("motif_updated", {"motif": motif.dict()})
        
        return motif
    
    async def delete_motif(self, motif_id: str) -> bool:
        """Delete a motif by ID. Returns True if successful, False otherwise."""
        result = await self.service.delete_motif(motif_id)
        
        if result:
            # Invalidate cache
            self._invalidate_cache()
            
            # Emit event for the deleted motif
            await self._emit_event("motif_deleted", {"motif_id": motif_id})
        
        return result
    
    # ==== Advanced Motif Operations ====
    
    async def get_dominant_motifs(self, limit: int = 3) -> List[Motif]:
        """Get the most dominant/intense motifs in the world."""
        # First get all active motifs
        all_motifs = await self.get_motifs(MotifFilter(
            lifecycle=[MotifLifecycle.EMERGING, MotifLifecycle.STABLE]
        ))
        
        # Sort by intensity in descending order
        sorted_motifs = sorted(all_motifs, key=lambda m: m.intensity, reverse=True)
        
        # Return the top N motifs
        return sorted_motifs[:limit]
    
    async def get_motifs_by_location(
        self, 
        x: float, 
        y: float, 
        max_distance: float = 100.0
    ) -> List[Tuple[Motif, float]]:
        """
        Get all motifs that affect a specific location, with their effective intensity.
        Returns a list of (motif, effective_intensity) tuples.
        """
        target_position = Vector2(x, y)
        result = []
        
        # Get all active motifs
        all_motifs = await self.get_motifs(MotifFilter(
            lifecycle=[MotifLifecycle.EMERGING, MotifLifecycle.STABLE]
        ))
        
        for motif in all_motifs:
            # Skip motifs without location data
            if not motif.location:
                continue
                
            # Calculate distance from target position
            motif_position = Vector2(motif.location.x, motif.location.y)
            distance = motif_position.distance_to(target_position)
            
            # Calculate decay based on distance and scope
            scope_multiplier = {
                MotifScope.LOCAL: 0.5,      # Local motifs decay faster
                MotifScope.REGIONAL: 1.0,   # Regional motifs decay at normal rate
                MotifScope.GLOBAL: 2.0,     # Global motifs decay slower
            }.get(motif.scope, 1.0)
            
            effective_distance = distance / scope_multiplier
            
            # Skip if out of range
            if effective_distance > max_distance:
                continue
                
            # Linear decay: intensity = original * (1 - distance/max_distance)
            intensity_multiplier = max(0.0, 1.0 - (effective_distance / max_distance))
            effective_intensity = motif.intensity * intensity_multiplier
            
            # Only include if significant effect (intensity > 1.0)
            if effective_intensity > 1.0:
                result.append((motif, effective_intensity))
        
        # Sort by effective intensity in descending order
        result.sort(key=lambda x: x[1], reverse=True)
        
        return result
    
    async def generate_random_motif(
        self, 
        location: Optional[Dict[str, Union[float, str]]] = None,
        category: Optional[MotifCategory] = None,
        scope: Optional[MotifScope] = None,
        intensity_range: Tuple[float, float] = (3.0, 8.0)
    ) -> Motif:
        """
        Generate a random motif based on provided parameters.
        Any unspecified parameter will be randomly generated.
        """
        # Randomize category if not specified
        if category is None:
            all_categories = list(MotifCategory)
            category = random.choice(all_categories)
        
        # Randomize scope if not specified
        if scope is None:
            # Weight the random choice - local most common, global least common
            scope_weights = {
                MotifScope.LOCAL: 0.6,
                MotifScope.REGIONAL: 0.3,
                MotifScope.GLOBAL: 0.1,
            }
            scope_items = list(scope_weights.items())
            scopes, weights = zip(*scope_items)
            scope = random.choices(scopes, weights=weights, k=1)[0]
        
        # Generate random intensity within range
        intensity = random.uniform(intensity_range[0], intensity_range[1])
        
        # Generate name and description
        name = generate_motif_name(category, scope)
        description = generate_motif_description(category, scope, intensity)
        
        # Set lifecycle (new motifs start as emerging)
        lifecycle = MotifLifecycle.EMERGING
        
        # Set duration based on scope and intensity
        duration_days = generate_realistic_duration(scope, intensity)
        start_time = datetime.now()
        end_time = start_time + timedelta(days=duration_days)
        
        # Create location info if provided
        location_info = None
        if location:
            location_info = LocationInfo(
                x=location.get("x", 0.0),
                y=location.get("y", 0.0),
                region=location.get("region", ""),
                name=location.get("name", "")
            )
        
        # Generate 1-3 random effects
        effects = []
        effect_types = ["npc_behavior", "event_frequency", "narrative_flavor"]
        num_effects = random.randint(1, 3)
        
        for _ in range(num_effects):
            effect_type = random.choice(effect_types)
            effect_intensity = intensity * random.uniform(0.7, 1.0)  # Effect intensity is similar to motif intensity
            
            effect = MotifEffect(
                effect_type=effect_type,
                intensity=effect_intensity,
                target="general"  # Using general target for simplicity
            )
            effects.append(effect)
        
        # Create and return the motif
        motif_data = MotifCreate(
            name=name,
            description=description,
            category=category,
            scope=scope,
            intensity=intensity,
            lifecycle=lifecycle,
            start_time=start_time,
            end_time=end_time,
            location=location_info,
            effects=effects
        )
        
        return await self.create_motif(motif_data)
    
    async def update_motif_lifecycle(self, motif_id: str, force_transition: bool = False) -> Optional[Motif]:
        """
        Update a motif's lifecycle based on its duration and start/end times.
        
        Returns the updated motif if changed, None if no change.
        
        Lifecycle progression:
        - EMERGING -> STABLE (after 1/3 of duration)
        - STABLE -> WANING (after 2/3 of duration)
        - WANING -> DORMANT (after full duration/end_time)
        
        If force_transition is True, it will force the motif to the next state
        regardless of timing.
        """
        motif = await self.get_motif(motif_id)
        if not motif:
            return None
        
        # Skip if already dormant unless forcing
        if motif.lifecycle == MotifLifecycle.DORMANT and not force_transition:
            return None
        
        # Calculate time thresholds
        now = datetime.now()
        
        # If no end time set, calculate one based on duration
        if not motif.end_time and motif.start_time and motif.duration_days > 0:
            motif.end_time = motif.start_time + timedelta(days=motif.duration_days)
        
        # If still no valid times, skip this motif
        if not motif.start_time or not motif.end_time:
            logger.warning(f"Motif {motif_id} has invalid time data, skipping lifecycle update")
            return None
        
        # Calculate time thresholds
        duration = motif.end_time - motif.start_time
        one_third = motif.start_time + (duration / 3)
        two_thirds = motif.start_time + (duration * 2 / 3)
        
        # Determine the new lifecycle state based on thresholds
        new_lifecycle = motif.lifecycle
        
        if force_transition:
            # Force to next state
            if motif.lifecycle == MotifLifecycle.EMERGING:
                new_lifecycle = MotifLifecycle.STABLE
            elif motif.lifecycle == MotifLifecycle.STABLE:
                new_lifecycle = MotifLifecycle.WANING
            elif motif.lifecycle == MotifLifecycle.WANING:
                new_lifecycle = MotifLifecycle.DORMANT
        else:
            # Natural progression based on time
            if now >= motif.end_time and motif.lifecycle != MotifLifecycle.DORMANT:
                new_lifecycle = MotifLifecycle.DORMANT
            elif now >= two_thirds and motif.lifecycle == MotifLifecycle.STABLE:
                new_lifecycle = MotifLifecycle.WANING
            elif now >= one_third and motif.lifecycle == MotifLifecycle.EMERGING:
                new_lifecycle = MotifLifecycle.STABLE
        
        # If no change, return None
        if new_lifecycle == motif.lifecycle:
            return None
        
        # Update the motif with the new lifecycle
        updated_motif = await self.update_motif(
            motif_id, 
            MotifUpdate(lifecycle=new_lifecycle)
        )
        
        if updated_motif:
            # If transitioning to dormant, check if we need to generate a replacement
            if new_lifecycle == MotifLifecycle.DORMANT:
                if motif.scope == MotifScope.GLOBAL:
                    # For global motifs, ensure we maintain exactly one
                    await self._ensure_one_global_motif()
                
                elif motif.scope == MotifScope.REGIONAL and motif.location and motif.location.region_id:
                    # For regional motifs, consider replacing it
                    region_id = motif.location.region_id
                    await self._ensure_minimum_motifs_per_region()
            
            # Emit lifecycle change event
            await self._emit_event("motif_lifecycle_changed", {
                "motif_id": motif_id,
                "previous": motif.lifecycle.value,
                "current": new_lifecycle.value
            })
        
        return updated_motif
    
    # ==== Background Tasks and Maintenance ====
    
    async def start_background_tasks(self):
        """Start any background tasks needed for the motif system."""
        if not self._background_tasks:
            # Schedule the lifecycle update task
            task = asyncio.create_task(self._run_lifecycle_updates())
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)
            
            logger.info("MotifManager background tasks started")

    def stop_background_tasks(self):
        """Stop all background tasks."""
        for task in self._background_tasks:
            task.cancel()
        self._background_tasks.clear()
        logger.info("MotifManager background tasks stopped")
    
    async def _run_lifecycle_updates(self):
        """Background task that periodically updates motif lifecycles."""
        while True:
            try:
                # Get all motifs that are not dormant
                active_motifs = await self.get_motifs(MotifFilter(
                    lifecycle=[MotifLifecycle.EMERGING, MotifLifecycle.STABLE, MotifLifecycle.WANING]
                ))
                
                # Check each motif for lifecycle updates
                for motif in active_motifs:
                    updated_motif = await self.update_motif_lifecycle(motif.id)
                    
                    # If the motif was updated or is still active, apply its effects
                    if updated_motif or motif.lifecycle != MotifLifecycle.DORMANT:
                        await self.apply_motif_effects(motif if not updated_motif else updated_motif)
                
                # Check for regions with no motifs and generate new ones if needed
                await self._ensure_minimum_motifs_per_region()
                
                # Check for global motif and ensure exactly one is active
                await self._ensure_one_global_motif()
                
                # Log lifecycle update completion
                logger.debug(f"Updated lifecycles for {len(active_motifs)} motifs")
                
            except Exception as e:
                logger.error(f"Error in motif lifecycle update: {e}")
            
            # Wait before next update cycle (every 1 hour)
            await asyncio.sleep(3600)  # 3600 seconds = 1 hour

    async def apply_motif_effects(self, motif: Motif, target_systems: List[str] = None) -> Dict[str, Any]:
        """
        Apply a motif's effects to target systems.
        If target_systems is not provided, all applicable systems will be affected.
        
        Possible target systems:
        - "npc" - Affects NPC behavior, dialogue, etc.
        - "event" - Influences event generation and frequency
        - "quest" - Modifies quest/arc generation and outcomes
        - "faction" - Adjusts faction relationships and tension
        - "environment" - Alters weather patterns, ambient effects
        - "economy" - Impacts economic factors like prices, resource availability
        - "narrative" - Provides context for narrative generation
        
        Returns a dictionary of results from the effect application to each system.
        """
        # Skip dormant motifs
        if motif.lifecycle == MotifLifecycle.DORMANT:
            return {"status": "skipped", "reason": "dormant motif"}
        
        try:
            # Call into service to apply effects
            effect_results = await self.service.apply_motif_effects(motif, target_systems)
            
            # Emit event for motif effects application
            await self._emit_event("motif_effects_applied", {
                "motif_id": motif.id,
                "motif_name": motif.name,
                "category": motif.category.value,
                "scope": motif.scope.value,
                "lifecycle": motif.lifecycle.value,
                "intensity": motif.intensity,
                "effects_summary": {
                    system: results.get("applied", False)
                    for system, results in effect_results.items()
                }
            })
            
            return effect_results
        except Exception as e:
            logger.error(f"Error applying motif effects for motif {motif.id}: {e}")
            return {"status": "error", "error": str(e)}

    async def _ensure_minimum_motifs_per_region(self, min_motifs: int = 2):
        """Ensure each region has at least a minimum number of active motifs."""
        # This would require region data, likely from another system
        # For now, we'll implement a placeholder that can be expanded later
        
        # Get all regions (placeholder implementation)
        # In a real implementation, you would get this from a region repository
        regions = ["region1", "region2", "region3"]  # Placeholder
        
        for region_id in regions:
            # Get regional motifs for this region
            regional_motifs = await self.get_motifs(MotifFilter(
                scope=[MotifScope.REGIONAL],
                region_id=region_id,
                lifecycle=[MotifLifecycle.EMERGING, MotifLifecycle.STABLE]
            ))
            
            # If fewer than minimum, generate new ones
            if len(regional_motifs) < min_motifs:
                motifs_to_create = min_motifs - len(regional_motifs)
                for _ in range(motifs_to_create):
                    await self.generate_random_motif(
                        location={"region_id": region_id},
                        category=None,  # Random
                        scope=MotifScope.REGIONAL,
                        intensity_range=(1.0, 6.0)
                    )
                
                logger.info(f"Generated {motifs_to_create} new regional motifs for {region_id}")

    async def _ensure_one_global_motif(self):
        """Ensure exactly one global motif is active at all times."""
        # Get active global motifs
        global_motifs = await self.get_motifs(MotifFilter(
            scope=[MotifScope.GLOBAL],
            lifecycle=[MotifLifecycle.EMERGING, MotifLifecycle.STABLE]
        ))
        
        if len(global_motifs) == 0:
            # No global motif - create one
            await self.generate_random_motif(
                location=None,
                category=None,  # Random
                scope=MotifScope.GLOBAL,
                intensity_range=(7.0, 7.0)  # Global motifs always intensity 7
            )
            logger.info("Generated new global motif")
        
        elif len(global_motifs) > 1:
            # Too many global motifs - keep the newest and make others wane
            # Sort by created_at (newest first)
            sorted_motifs = sorted(global_motifs, key=lambda m: m.created_at, reverse=True)
            
            # Keep the newest, update the rest to waning
            for i, motif in enumerate(sorted_motifs):
                if i > 0:  # Skip the first (newest) one
                    await self.update_motif(motif.id, MotifUpdate(
                        lifecycle=MotifLifecycle.WANING
                    ))
            
            logger.info(f"Set {len(sorted_motifs) - 1} excess global motifs to waning")

    # ==== Event Handling ====
    
    def register_event_listener(self, callback):
        """Register a callback for motif events."""
        if callback not in self._event_listeners:
            self._event_listeners.append(callback)
    
    def unregister_event_listener(self, callback):
        """Unregister a callback for motif events."""
        if callback in self._event_listeners:
            self._event_listeners.remove(callback)
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit an event to all registered listeners."""
        event = {
            "type": f"motif.{event_type}",
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        for listener in self._event_listeners:
            try:
                # Accept both sync and async callbacks
                if asyncio.iscoroutinefunction(listener):
                    await listener(event)
                else:
                    listener(event)
            except Exception as e:
                logger.error(f"Error in motif event listener: {e}")
    
    # ==== Utility Methods ====
    
    def _should_use_cache(self) -> bool:
        """Check if the cache is valid and should be used."""
        if self._active_motifs_cache is None or self._cache_timestamp is None:
            return False
            
        time_since_cache = datetime.now() - self._cache_timestamp
        return time_since_cache < self._cache_valid_duration
    
    def _invalidate_cache(self):
        """Invalidate the motif cache."""
        self._active_motifs_cache = None
        self._cache_timestamp = None
    
    async def get_narrative_context(self, x: Optional[float] = None, y: Optional[float] = None, region_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a comprehensive narrative context dictionary based on active motifs at a position or region.
        This is designed to be used directly in GPT prompts for narrative generation.
        
        Args:
            x, y: Optional coordinates to get motifs at a specific position
            region_id: Optional region ID to get regional motifs
            
        Returns:
            A dictionary with narrative context information based on active motifs
        """
        # Get the basic motif context
        motif_context = await self.service.get_motif_context(x, y, region_id)
        
        # Get actual motif objects for effect application
        motifs = []
        if x is not None and y is not None:
            motifs = await self.service.get_motifs_at_position(x, y)
        elif region_id is not None:
            # Get regional and global motifs
            regional_motifs = await self.service.get_regional_motifs(region_id)
            global_motifs = await self.service.get_global_motifs()
            motifs = regional_motifs + global_motifs
        else:
            # Just get global motifs
            motifs = await self.service.get_global_motifs()
        
        # Apply narrative effects to enrich the context
        narrative_effects = {}
        for motif in motifs:
            if motif.lifecycle != MotifLifecycle.DORMANT:
                # Only apply to narrative system
                effects = await self.service.apply_motif_effects(motif, target_systems=["narrative"])
                if "narrative" in effects and effects["narrative"].get("applied", False):
                    narrative_effects[motif.name] = effects["narrative"]
        
        # Enhance the motif context with narrative effects
        if narrative_effects:
            # Extract and combine narrative themes
            all_themes = []
            for effect_data in narrative_effects.values():
                for detail in effect_data.get("details", []):
                    if "Narrative modifiers" in detail and "themes" in eval(detail.split("Narrative modifiers: ")[1]):
                        all_themes.extend(eval(detail.split("Narrative modifiers: ")[1])["themes"])
            
            # Add unique themes to the context
            motif_context["narrative_themes"] = list(set(motif_context.get("narrative_themes", []) + all_themes))
            
            # Add effects to context
            motif_context["narrative_effects"] = narrative_effects
        
        # Add a world tone based on dominant motifs
        if motifs:
            # Sort by intensity
            sorted_motifs = sorted(motifs, key=lambda m: m.intensity, reverse=True)
            dominant = sorted_motifs[0]
            
            motif_context["world_tone"] = {
                "primary_influence": dominant.category.value,
                "intensity": dominant.intensity,
                "description": self._get_tone_description(dominant)
            }
        
        return motif_context

    def _get_tone_description(self, motif: Motif) -> str:
        """Generate a tone description based on motif attributes."""
        intensity_desc = "overwhelming" if motif.intensity >= 7 else (
            "strong" if motif.intensity >= 5 else (
            "moderate" if motif.intensity >= 3 else "subtle"
        ))
        
        # Map categories to tone descriptions
        tone_map = {
            MotifCategory.BETRAYAL: f"An {intensity_desc} atmosphere of mistrust and treachery",
            MotifCategory.CHAOS: f"An {intensity_desc} sense of unpredictability and disorder",
            MotifCategory.HOPE: f"An {intensity_desc} feeling of optimism despite challenges",
            MotifCategory.FEAR: f"An {intensity_desc} undercurrent of dread and apprehension",
            MotifCategory.VENGEANCE: f"An {intensity_desc} drive for retribution",
            # Add more mappings as needed
        }
        
        # Return mapped description or fallback
        return tone_map.get(
            motif.category, 
            f"An {intensity_desc} manifestation of {motif.category.value}"
        )
    
    # ==== Chaos System Integration (Migrated from chaos_utils.py) ====
    
    def roll_chaos_event(self):
        """Generate a random chaos event from the predefined table."""
        return roll_chaos_event()
        
    async def inject_chaos_event(self, event_type, region=None, context=None):
        """
        Inject a chaos event into the world log.
        
        Args:
            event_type: The type of chaos event
            region: Optional region where the event occurs
            context: Additional context data for the event
            
        Returns:
            Dict containing the created event data
        """
        context = context or {}
        event_id = f"chaos_{int(datetime.now().timestamp())}"
        summary = f"[CHAOS EVENT] {event_type}"

        event_data = {
            "event_id": event_id,
            "summary": summary,
            "type": "narrative_chaos",
            "timestamp": datetime.now().isoformat(),
            "context": context
        }

        # Add to world log (using repository instead of direct DB write)
        await self.repository.add_to_world_log(event_id, event_data)

        # Sync event beliefs if region is provided
        if region:
            await self._emit_event("sync_beliefs", {
                "region": region,
                "event_data": event_data
            })

        # Emit chaos event
        await self._emit_event("chaos_event", event_data)
        
        return event_data

    async def trigger_chaos_if_needed(self, entity_id, region=None):
        """
        Check if chaos should be triggered based on entity aggression threshold.
        
        Args:
            entity_id: ID of the entity (usually an NPC)
            region: Optional region for context
            
        Returns:
            Dict with event data if chaos was triggered
        """
        # Get entity motif data
        entity_data = await self.repository.get_entity_data(entity_id)
        if not entity_data:
            return {"message": "Entity not found"}
            
        # Check aggression threshold (moved from MotifEngine)
        threshold = None
        if "active_motifs" in entity_data:
            weights = [m.get("weight", 0) for m in entity_data.get("active_motifs", [])]
            if any(w >= 5 for w in weights):
                threshold = "aggression_5"
            elif len([w for w in weights if w >= 4]) >= 2:
                threshold = "dual_pressure"
        
        if not threshold:
            return {"message": "No chaos triggered"}

        # Roll and inject chaos event
        chaos_type = self.roll_chaos_event()
        event = await self.inject_chaos_event(
            chaos_type, 
            region, 
            context={"entity_id": entity_id, "threshold": threshold}
        )
        
        return {"chaos_triggered": True, "event": event}

    async def force_chaos(self, entity_id, region=None):
        """
        Force a chaos event for an entity regardless of threshold.
        
        Args:
            entity_id: ID of the entity
            region: Optional region for context
            
        Returns:
            Dict with event data and new motif
        """
        # Get entity data
        entity_data = await self.repository.get_entity_data(entity_id)
        if not entity_data:
            entity_data = {
                "active_motifs": [],
                "motif_history": [],
                "last_rotated": datetime.now().isoformat()
            }
        
        # Generate a new chaos motif
        new_motif = await self.generate_random_motif(
            category=MotifCategory.CHAOS,
            intensity_range=(6.0, 9.0)
        )
        
        # Add to entity's motifs
        entity_data.setdefault("active_motifs", []).append(new_motif.dict())
        entity_data.setdefault("motif_history", []).append(new_motif.name)
        entity_data["last_rotated"] = datetime.now().isoformat()
        
        # Save updated entity data
        await self.repository.update_entity_data(entity_id, entity_data)
        
        # Roll and inject chaos event
        chaos_type = self.roll_chaos_event()
        event = await self.inject_chaos_event(
            chaos_type, 
            region, 
            context={"entity_id": entity_id, "forced": True}
        )
        
        return {"forced_motif": new_motif.dict(), "event": event}

    async def get_gpt_context(self, entity_id: str = None, location: Dict[str, Any] = None, region_id: str = None, context_size: str = "medium") -> Dict[str, Any]:
        """
        Generate a complete GPT context for narrative generation that incorporates motifs.
        
        Parameters:
        - entity_id: Optional entity ID (NPC, PC, etc.) for character-specific context
        - location: Optional location info with x, y coordinates for positional context
        - region_id: Optional region ID for regional context
        - context_size: Size of context to generate ('small', 'medium', 'large')
        
        Returns a comprehensive context dictionary for GPT narrative generation.
        """
        # Get basic entity data if provided
        entity_data = None
        if entity_id:
            try:
                entity_data = await self.repository.get_entity_data(entity_id)
            except Exception as e:
                logger.warning(f"Failed to get entity data for {entity_id}: {e}")
        
        # Get location-based motifs if coordinates provided
        x, y = None, None
        if location and isinstance(location, dict):
            x = location.get("x")
            y = location.get("y")
        
        # Get enhanced narrative context from motifs
        motif_context = await self.get_narrative_context(x, y, region_id)
        
        # Combine with recent world events
        recent_events = []
        try:
            # Get 5-10 recent events based on context size
            event_limit = {"small": 5, "medium": 7, "large": 10}.get(context_size, 7)
            recent_events = await self.repository.get_world_log_events(limit=event_limit)
        except Exception as e:
            logger.warning(f"Failed to get recent events: {e}")
        
        # Build comprehensive GPT context
        gpt_context = {
            "world_state": {
                "current_motifs": motif_context.get("active_motifs", []),
                "world_tone": motif_context.get("world_tone", {"primary_influence": "neutral", "intensity": 0}),
                "narrative_themes": motif_context.get("narrative_themes", []),
                "recent_events": recent_events
            }
        }
        
        # Add entity-specific context if available
        if entity_data:
            # Map entity motifs to narrative impacts (if entity has motif data)
            entity_motifs = entity_data.get("motifs", [])
            motif_impacts = []
            
            for motif in entity_motifs:
                if isinstance(motif, dict) and "theme" in motif:
                    theme = motif.get("theme")
                    weight = motif.get("weight", 1)
                    
                    impact = {
                        "theme": theme,
                        "strength": weight,
                        "influence": "strong" if weight >= 4 else "moderate" if weight >= 2 else "subtle",
                        "description": f"The {theme.lower()} theme {'dominates' if weight >= 4 else 'influences' if weight >= 2 else 'subtly affects'} this entity's behavior and perspective."
                    }
                    motif_impacts.append(impact)
            
            # Add entity data to context
            gpt_context["entity"] = {
                "id": entity_id,
                "data": entity_data,
                "motif_impacts": motif_impacts
            }
        
        # Add location-specific context if available
        if x is not None and y is not None:
            gpt_context["location"] = {
                "x": x,
                "y": y,
                "local_motifs": [m for m in motif_context.get("active_motifs", []) if m.get("scope") == "local"]
            }
        
        # Add region-specific context if available
        if region_id:
            # Get regional motifs
            regional_motifs = [m for m in motif_context.get("active_motifs", []) if m.get("scope") == "regional"]
            
            gpt_context["region"] = {
                "id": region_id,
                "regional_motifs": regional_motifs
            }
        
        # Adjust context based on requested size
        if context_size == "small":
            # Simplify to just the essentials
            if "world_state" in gpt_context:
                # Limit to top 2 motifs and themes
                gpt_context["world_state"]["current_motifs"] = gpt_context["world_state"]["current_motifs"][:2]
                gpt_context["world_state"]["narrative_themes"] = gpt_context["world_state"]["narrative_themes"][:2]
                gpt_context["world_state"]["recent_events"] = gpt_context["world_state"]["recent_events"][:3]
        
        elif context_size == "large":
            # Add additional historical context
            try:
                # Get more historical events
                historical_events = await self.repository.get_world_log_events(limit=20, offset=10)
                
                # Add world history section
                gpt_context["world_history"] = {
                    "historical_events": historical_events,
                    "motif_progression": await self._get_motif_progression()
                }
            except Exception as e:
                logger.warning(f"Failed to get historical context: {e}")
        
        return gpt_context

    async def _get_motif_progression(self) -> List[Dict[str, Any]]:
        """Get a summary of recent motif progressions for historical context."""
        # Get dormant motifs that recently ended (within last 7 days)
        # This would pull from historical data
        
        # This is a placeholder implementation
        # In a full implementation, you would track motif history and get actual progression
        return [
            {
                "period": "recent",
                "dominant_motifs": ["Chaos", "Betrayal"],
                "narrative_impact": "The world has been through significant upheaval and mistrust."
            },
            {
                "period": "previous",
                "dominant_motifs": ["Hope", "Unity"],
                "narrative_impact": "Prior to recent events, there was a period of optimism and cooperation."
            }
        ]

    async def generate_motif_sequence(
        self,
        sequence_length: int = 3,
        starting_category: Optional[MotifCategory] = None,
        region_id: Optional[str] = None,
        progressive_intensity: bool = True
    ) -> List[Motif]:
        """
        Generate a sequence of thematically related motifs for long-term narrative arcs.
        
        This creates a series of motifs that can evolve over time, representing the progression
        of a story arc or world event.
        
        Args:
            sequence_length: Number of motifs in the sequence (default: 3)
            starting_category: Optional starting category, or random if None
            region_id: Optional region ID for regional motifs
            progressive_intensity: If True, intensity will increase through the sequence
            
        Returns:
            List of created motifs in sequence order
        """
        sequence = []
        
        # Pick a starting category if not provided
        if starting_category is None:
            starting_category = random.choice(list(MotifCategory))
        
        # Generate sequence ID for tracking
        sequence_id = f"seq_{uuid4().hex[:8]}"
        
        # Generate related categories (thematic progression)
        categories = self._generate_related_categories(starting_category, sequence_length)
        
        # Define base intensity - will progress through sequence if progressive_intensity is True
        base_intensity = random.uniform(3.0, 5.0)
        
        # Generate each motif in the sequence
        for i, category in enumerate(categories):
            # Progressive intensity if enabled
            if progressive_intensity:
                # Intensity increases with each motif in sequence
                intensity = min(10.0, base_intensity + (i * 1.5))
            else:
                # Random intensity with slight variation
                intensity = base_intensity + random.uniform(-1.0, 1.0)
            
            # Vary duration slightly
            duration_days = random.randint(10, 20)
            
            # Determine scope - mix of regional and global
            scope = MotifScope.GLOBAL if random.random() < 0.3 else MotifScope.REGIONAL
            
            # Location data for regional motifs
            location_info = None
            if scope == MotifScope.REGIONAL and region_id:
                location_info = LocationInfo(
                    region_id=region_id,
                    # No specific coordinates for regional motifs
                )
            
            # Generate 1-3 random effects appropriate for the category
            effects = self._generate_effects_for_category(category, intensity)
            
            # Create name and description with sequence context
            name = f"{category.value.capitalize()} {i+1}/{sequence_length}"
            description = f"Part {i+1} of a {sequence_length}-part narrative sequence. "
            
            if i == 0:
                description += "This initiating motif begins the arc."
            elif i == sequence_length - 1:
                description += "This concluding motif completes the arc."
            else:
                description += "This transitional motif advances the arc."
            
            # Create the motif data
            motif_data = MotifCreate(
                name=name,
                description=description,
                category=category,
                scope=scope,
                lifecycle=MotifLifecycle.DORMANT if i > 0 else MotifLifecycle.EMERGING,
                intensity=intensity,
                duration_days=duration_days,
                location=location_info,
                effects=effects,
                metadata={
                    "sequence_id": sequence_id,
                    "sequence_position": i,
                    "sequence_length": sequence_length,
                    "previous_motif": sequence[i-1].id if i > 0 else None
                }
            )
            
            # Create the motif
            motif = await self.create_motif(motif_data)
            sequence.append(motif)
            
            # If not the first motif, add a dependency relationship
            if i > 0:
                prev_motif = sequence[i-1]
                # Update previous motif's metadata to point to this one
                await self.update_motif(
                    prev_motif.id,
                    MotifUpdate(
                        metadata={
                            **prev_motif.metadata,
                            "next_motif": motif.id
                        }
                    )
                )
        
        # Log the sequence creation
        logger.info(f"Created motif sequence '{sequence_id}' with {len(sequence)} motifs starting with {starting_category.value}")
        
        return sequence
    
    def _generate_related_categories(self, starting_category: MotifCategory, count: int) -> List[MotifCategory]:
        """
        Generate a list of thematically related categories for a motif sequence.
        
        Args:
            starting_category: The category to start from
            count: Number of categories to generate
            
        Returns:
            List of MotifCategory objects forming a narrative progression
        """
        # Define thematic relationship map (category -> [related categories])
        # These map narrative progressions that make thematic sense
        thematic_relationships = {
            MotifCategory.HOPE: [MotifCategory.UNITY, MotifCategory.REBIRTH, MotifCategory.TRANSFORMATION],
            MotifCategory.BETRAYAL: [MotifCategory.VENGEANCE, MotifCategory.REGRET, MotifCategory.REDEMPTION],
            MotifCategory.CHAOS: [MotifCategory.COLLAPSE, MotifCategory.MADNESS, MotifCategory.TRANSFORMATION],
            MotifCategory.VENGEANCE: [MotifCategory.JUSTICE, MotifCategory.DEATH, MotifCategory.GUILT],
            MotifCategory.FEAR: [MotifCategory.PARANOIA, MotifCategory.OBSESSION, MotifCategory.DEFIANCE],
            MotifCategory.REVELATION: [MotifCategory.TRUTH, MotifCategory.TRANSFORMATION, MotifCategory.REDEMPTION],
            # Add more relationships as needed
        }
        
        # Add reverse relationships for completeness
        reverse_relationships = {}
        for src, targets in thematic_relationships.items():
            for target in targets:
                if target not in reverse_relationships:
                    reverse_relationships[target] = []
                reverse_relationships[target].append(src)
        
        # Merge to get complete relationship map
        for category, related in reverse_relationships.items():
            if category in thematic_relationships:
                thematic_relationships[category].extend(related)
            else:
                thematic_relationships[category] = related
            
            # Remove duplicates
            thematic_relationships[category] = list(set(thematic_relationships[category]))
        
        # Initialize the sequence with starting category
        categories = [starting_category]
        
        # Generate remaining categories
        for i in range(count - 1):
            current = categories[-1]
            
            # Determine next category
            if current in thematic_relationships and random.random() < 0.8:
                # 80% chance to follow a thematic relationship
                next_category = random.choice(thematic_relationships[current])
            else:
                # 20% chance for a random category (unexpected twist)
                all_categories = list(MotifCategory)
                next_category = random.choice(all_categories)
                # Avoid repeating the current category
                while next_category == current:
                    next_category = random.choice(all_categories)
            
            categories.append(next_category)
        
        return categories
    
    def _generate_effects_for_category(self, category: MotifCategory, intensity: float) -> List[MotifEffect]:
        """Generate appropriate effects for a given motif category"""
        effects = []
        
        # Common effect types for all categories
        common_effect_types = ["narrative_flavor"]
        
        # Category-specific effect types
        category_effects = {
            MotifCategory.HOPE: ["npc_behavior", "event_frequency"],
            MotifCategory.BETRAYAL: ["faction_tension", "relationship_change"],
            MotifCategory.CHAOS: ["event_frequency", "weather_pattern"],
            MotifCategory.VENGEANCE: ["npc_behavior", "relationship_change"],
            MotifCategory.FEAR: ["npc_behavior", "weather_pattern"],
            # Add more category-specific effects
        }
        
        # Get effect types for this category
        effect_types = common_effect_types.copy()
        if category in category_effects:
            effect_types.extend(category_effects[category])
        
        # Number of effects based on intensity (1-3)
        effect_count = 1
        if intensity > 5:
            effect_count = 2
        if intensity > 8:
            effect_count = 3
        
        # Create effects
        for _ in range(effect_count):
            effect_type = random.choice(effect_types)
            
            # Effect target depends on effect type
            target = "general"
            if effect_type == "npc_behavior":
                target = "npc"
            elif effect_type == "weather_pattern":
                target = "environment"
            elif effect_type == "event_frequency":
                target = "event"
            
            # Create effect with appropriate description
            effect = MotifEffect(
                effect_type=effect_type,
                intensity=intensity * random.uniform(0.8, 1.2),  # Slight variation
                target=target,
                description=f"Effect of {category.value} on {effect_type}"
            )
            
            effects.append(effect)
        
        return effects

    async def generate_world_event(
        self, 
        region_id: Optional[str] = None, 
        coordinates: Optional[Tuple[float, float]] = None,
        event_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a world event influenced by the active motifs in a region or coordinates.
        
        This function blends motif themes with event generation to create events 
        that align with the current narrative context.
        
        Args:
            region_id: Optional region ID to specify where the event occurs
            coordinates: Optional (x, y) coordinates to specify where the event occurs
            event_type: Optional specific event type to generate, or random if None
            
        Returns:
            Dictionary containing the generated event data
        """
        # Get active motifs based on region or coordinates
        active_motifs = []
        
        if coordinates:
            x, y = coordinates
            motif_pairs = await self.get_motifs_by_location(x, y)
            active_motifs = [m for m, _ in motif_pairs]
        elif region_id:
            # Get regional and global motifs
            active_motifs = await self.get_motifs(MotifFilter(
                region_ids=[region_id],
                lifecycle=[MotifLifecycle.EMERGING, MotifLifecycle.STABLE],
                active_only=True
            ))
            
            # Add global motifs
            global_motifs = await self.get_motifs(MotifFilter(
                scope=[MotifScope.GLOBAL],
                lifecycle=[MotifLifecycle.EMERGING, MotifLifecycle.STABLE],
                active_only=True
            ))
            active_motifs.extend(global_motifs)
        else:
            # Just get global motifs
            active_motifs = await self.get_motifs(MotifFilter(
                scope=[MotifScope.GLOBAL],
                lifecycle=[MotifLifecycle.EMERGING, MotifLifecycle.STABLE],
                active_only=True
            ))
        
        # Synthesize motifs to get blended narrative context
        from .motif_utils import synthesize_motifs
        synthesis = synthesize_motifs(active_motifs)
        
        # Default event types
        default_event_types = [
            "discovery", "conflict", "arrival", "departure", 
            "transformation", "celebration", "disaster", "revelation"
        ]
        
        # Get event types influenced by motif themes
        influenced_event_types = self._get_motif_influenced_event_types(synthesis, active_motifs)
        
        # Select event type
        if event_type:
            # Use specified event type
            selected_event_type = event_type
        else:
            # Weighted random selection based on motif influence
            # 70% chance to select a motif-influenced event type, 30% chance for random default type
            if influenced_event_types and random.random() < 0.7:
                selected_event_type = random.choice(influenced_event_types)
            else:
                selected_event_type = random.choice(default_event_types)
        
        # Generate event description based on synthesis and selected type
        event_description = self._generate_event_description(selected_event_type, synthesis)
        
        # Generate event intensity (1-10 scale) influenced by motif intensity
        base_intensity = random.randint(3, 7)  # Base randomness
        motif_intensity_modifier = 0
        
        if active_motifs:
            # Average motif intensity, weighted by each motif's intensity
            total_weight = sum(m.intensity for m in active_motifs)
            avg_intensity = sum(m.intensity * m.intensity for m in active_motifs) / total_weight
            
            # Map avg intensity (1-10) to a modifier (-2 to +3)
            motif_intensity_modifier = round((avg_intensity - 5) / 2)
        
        event_intensity = max(1, min(10, base_intensity + motif_intensity_modifier))
        
        # Determine if this is a major event based on intensity
        is_major = event_intensity >= 8
        
        # Generate event data
        event_id = f"evt_{uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        event_data = {
            "id": event_id,
            "type": selected_event_type,
            "description": event_description,
            "intensity": event_intensity,
            "is_major": is_major,
            "timestamp": timestamp,
            "region_id": region_id,
            "coordinates": coordinates,
            "influenced_by": [
                {
                    "motif_id": m.id,
                    "name": m.name,
                    "category": m.category.value,
                    "weight": m.intensity / sum(motif.intensity for motif in active_motifs) if active_motifs else 0
                }
                for m in active_motifs[:3]  # Top 3 most influential motifs
            ],
            "narrative_context": {
                "theme": synthesis.get("theme", "neutral"),
                "tone": synthesis.get("tone", "neutral"),
                "direction": synthesis.get("narrative_direction", "steady")
            }
        }
        
        # Add to the world log
        await self.repository.add_to_world_log(event_id, event_data)
        
        # Emit event
        await self._emit_event("world_event_generated", {
            "event_id": event_id,
            "event_type": selected_event_type,
            "region_id": region_id,
            "coordinates": coordinates,
            "influenced_by_motifs": [m.id for m in active_motifs[:3]]
        })
        
        return event_data
    
    def _get_motif_influenced_event_types(self, synthesis: Dict[str, Any], motifs: List[Motif]) -> List[str]:
        """
        Get event types that would be influenced by the current motif themes.
        
        Args:
            synthesis: The synthesized motif data
            motifs: List of active motifs
            
        Returns:
            List of event types appropriate for the current motifs
        """
        theme = synthesis.get("theme", "").lower()
        tone = synthesis.get("tone", "neutral")
        
        # Default base events for any theme
        event_types = ["discovery", "conflict", "transformation"]
        
        # Add theme-specific event types
        if "hope" in theme or "rebirth" in theme or "unity" in theme:
            event_types.extend(["celebration", "alliance", "reconciliation", "recovery"])
            
        elif "betrayal" in theme or "deception" in theme:
            event_types.extend(["betrayal", "conspiracy", "revelation", "accusation"])
            
        elif "chaos" in theme or "madness" in theme:
            event_types.extend(["disaster", "upheaval", "accident", "spontaneous"])
            
        elif "death" in theme or "ruin" in theme:
            event_types.extend(["loss", "mourning", "decline", "destruction"])
            
        elif "vengeance" in theme or "justice" in theme:
            event_types.extend(["confrontation", "judgment", "retribution", "arrest"])
            
        # Add tone-influenced events
        if tone == "dark":
            event_types.extend(["omen", "disappearance", "attack"])
        elif tone == "light":
            event_types.extend(["miracle", "reunion", "breakthrough"])
            
        # Add events influenced by highest intensity motifs
        sorted_motifs = sorted(motifs, key=lambda m: m.intensity, reverse=True)
        for motif in sorted_motifs[:2]:  # Consider top 2 motifs by intensity
            if motif.category == MotifCategory.FEAR:
                event_types.extend(["panic", "flight", "sighting", "warning"])
            elif motif.category == MotifCategory.OBSESSION:
                event_types.extend(["discovery", "breakthrough", "expedition"])
            # Add more for other categories
            
        # Return unique event types
        return list(set(event_types))
    
    def _generate_event_description(self, event_type: str, synthesis: Dict[str, Any]) -> str:
        """
        Generate a description for an event based on its type and the motif synthesis.
        
        Args:
            event_type: The type of event
            synthesis: The synthesized motif data
            
        Returns:
            A description for the event
        """
        theme = synthesis.get("theme", "").lower()
        tone = synthesis.get("tone", "neutral")
        descriptors = synthesis.get("descriptors", [])
        
        # Base descriptions for event types
        base_descriptions = {
            "discovery": [
                "New information has been uncovered",
                "An important find has been made",
                "Something hidden has been revealed"
            ],
            "conflict": [
                "Tensions have erupted into open hostility",
                "A dispute has turned violent",
                "Forces have clashed"
            ],
            "arrival": [
                "Someone or something significant has arrived",
                "A new presence makes itself known",
                "An unexpected visitor has appeared"
            ],
            "departure": [
                "A notable absence has been created",
                "Someone or something important has left",
                "A departure marks a significant change"
            ],
            "transformation": [
                "A fundamental change has occurred",
                "Something has been altered at its core",
                "A metamorphosis has taken place"
            ],
            "celebration": [
                "A joyous occasion is marked",
                "People gather in celebration",
                "A festive atmosphere has emerged"
            ],
            "disaster": [
                "Calamity has struck",
                "A catastrophic event has occurred",
                "Devastation has been wrought"
            ],
            "revelation": [
                "A truth has been unveiled",
                "Hidden knowledge has come to light",
                "Something important has been disclosed"
            ]
        }
        
        # Get base description
        base_desc = random.choice(base_descriptions.get(
            event_type, ["A significant event has occurred"]
        ))
        
        # Add thematic elements
        if descriptors:
            # Use 1-2 descriptors
            used_descriptors = random.sample(descriptors, min(2, len(descriptors)))
            thematic_desc = f", characterized by {' and '.join(used_descriptors)}"
        else:
            thematic_desc = f", influenced by the {theme} motif"
        
        # Add tone
        if tone == "dark":
            tone_desc = ", casting a shadow over the affected area"
        elif tone == "light":
            tone_desc = ", bringing a sense of hope to the affected area"
        else:
            tone_desc = ""
        
        # Final description
        return f"{base_desc}{thematic_desc}{tone_desc}." 