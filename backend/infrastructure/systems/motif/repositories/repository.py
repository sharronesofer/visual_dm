from typing import List, Dict, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import json
import os
import uuid
from pathlib import Path

from backend.infrastructure.systems.motif.models import Motif, MotifFilter, MotifScope, MotifLifecycle, LocationInfo

class Vector2:
    """Simple 2D vector class for position handling."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def distance_to(self, other: 'Vector2') -> float:
        """Calculate Euclidean distance to another point."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

class MotifRepository:
    """Repository for managing motif data storage and retrieval."""
    
    def __init__(self, data_path: str = None):
        """Initialize the repository with the data storage path."""
        self.data_path = data_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data", "motifs"
        )
        self._ensure_data_dir_exists()
        self._motifs: Dict[int, Motif] = {}
        self._next_id = 1
        self._load_motifs()
    
    def _ensure_data_dir_exists(self) -> None:
        """Ensure the data directory exists."""
        os.makedirs(self.data_path, exist_ok=True)
    
    def _get_motif_path(self, motif_id: int) -> str:
        """Get the file path for a motif."""
        return os.path.join(self.data_path, f"motif_{motif_id}.json")
    
    def _load_motifs(self) -> None:
        """Load all motifs from storage."""
        self._motifs = {}
        self._next_id = 1
        
        if not os.path.exists(self.data_path):
            return
        
        for file_name in os.listdir(self.data_path):
            if not file_name.startswith("motif_") or not file_name.endswith(".json"):
                continue
            
            file_path = os.path.join(self.data_path, file_name)
            try:
                with open(file_path, "r") as f:
                    motif_dict = json.load(f)
                    motif = Motif.parse_obj(motif_dict)
                    self._motifs[motif.id] = motif
                    self._next_id = max(self._next_id, motif.id + 1)
            except Exception as e:
                print(f"Error loading motif from {file_path}: {e}")
    
    def _save_motif(self, motif: Motif) -> None:
        """Save a motif to storage."""
        file_path = self._get_motif_path(motif.id)
        with open(file_path, "w") as f:
            json.dump(motif.dict(), f, indent=2, default=str)
    
    def create_motif(self, motif: Motif) -> Motif:
        """Create a new motif."""
        if motif.id is None:
            motif.id = self._next_id
            self._next_id += 1
        
        now = datetime.now()
        motif.created_at = now
        motif.updated_at = now
        
        if motif.start_time is None:
            motif.start_time = now
        
        if motif.end_time is None and motif.duration_days > 0:
            motif.end_time = now + timedelta(days=motif.duration_days)
        
        self._motifs[motif.id] = motif
        self._save_motif(motif)
        return motif
    
    def get_motif(self, motif_id: int) -> Optional[Motif]:
        """Get a motif by ID."""
        return self._motifs.get(motif_id)
    
    def update_motif(self, motif_id: int, motif_update: Dict[str, Any]) -> Optional[Motif]:
        """Update an existing motif."""
        existing_motif = self.get_motif(motif_id)
        if not existing_motif:
            return None
        
        # Update the motif with the provided fields
        motif_dict = existing_motif.dict()
        for key, value in motif_update.items():
            if key in motif_dict:
                motif_dict[key] = value
        
        updated_motif = Motif.parse_obj(motif_dict)
        updated_motif.updated_at = datetime.now()
        
        self._motifs[motif_id] = updated_motif
        self._save_motif(updated_motif)
        return updated_motif
    
    def delete_motif(self, motif_id: int) -> bool:
        """Delete a motif."""
        if motif_id not in self._motifs:
            return False
        
        file_path = self._get_motif_path(motif_id)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        del self._motifs[motif_id]
        return True
    
    def get_all_motifs(self) -> List[Motif]:
        """Get all motifs."""
        return list(self._motifs.values())
    
    def get_global_motifs(self) -> List[Motif]:
        """Get all global motifs."""
        return [
            motif for motif in self._motifs.values()
            if motif.scope == MotifScope.GLOBAL and motif.lifecycle != MotifLifecycle.DORMANT
        ]
    
    def get_regional_motifs(self, region_id: str) -> List[Motif]:
        """Get all motifs for a specific region."""
        return [
            motif for motif in self._motifs.values()
            if motif.scope == MotifScope.REGIONAL and 
            motif.location and motif.location.region_id == region_id and
            motif.lifecycle != MotifLifecycle.DORMANT
        ]
    
    def get_motifs_at_position(self, position: Vector2, radius: float = 0) -> List[Motif]:
        """Get all motifs that affect a specific position."""
        result = []
        
        # First, include all global motifs
        result.extend(self.get_global_motifs())
        
        # Then, include regional and local motifs that affect the position
        for motif in self._motifs.values():
            if motif.lifecycle == MotifLifecycle.DORMANT:
                continue
                
            if motif.scope != MotifScope.GLOBAL and motif.location:
                if motif.scope == MotifScope.REGIONAL:
                    # For regional motifs, just check the region ID if we have one
                    # This is a simplified approach
                    if motif.location.region_id:
                        # This would need to be implemented with proper region boundary checking
                        # For now, we'll just pretend all positions are valid for all regions
                        result.append(motif)
                elif motif.scope == MotifScope.LOCAL:
                    # For local motifs, check if the position is within the radius
                    if (motif.location.position_x is not None and 
                        motif.location.position_y is not None):
                        
                        motif_pos = Vector2(motif.location.position_x, motif.location.position_y)
                        motif_radius = motif.location.radius
                        
                        if position.distance_to(motif_pos) <= (motif_radius + radius):
                            result.append(motif)
        
        return result
    
    def filter_motifs(self, filter_params: MotifFilter) -> List[Motif]:
        """Filter motifs by various criteria."""
        all_motifs = self.get_all_motifs()
        filtered_motifs = all_motifs
        
        # Filter by IDs if specified
        if filter_params.ids:
            filtered_motifs = [m for m in filtered_motifs if m.id in filter_params.ids]
        
        # Filter by category
        if filter_params.category:
            categories = filter_params.category
            if not isinstance(categories, list):
                categories = [categories]
            filtered_motifs = [m for m in filtered_motifs if m.category in categories]
        
        # Filter by scope
        if filter_params.scope:
            scopes = filter_params.scope
            if not isinstance(scopes, list):
                scopes = [scopes]
            filtered_motifs = [m for m in filtered_motifs if m.scope in scopes]
        
        # Filter by lifecycle
        if filter_params.lifecycle:
            lifecycles = filter_params.lifecycle
            if not isinstance(lifecycles, list):
                lifecycles = [lifecycles]
            filtered_motifs = [m for m in filtered_motifs if m.lifecycle in lifecycles]
        elif filter_params.active_only:
            # If active_only is True and no specific lifecycle filter, exclude dormant
            filtered_motifs = [m for m in filtered_motifs if m.lifecycle != MotifLifecycle.DORMANT]
        
        # Filter by intensity range
        if filter_params.min_intensity is not None:
            filtered_motifs = [m for m in filtered_motifs if m.intensity >= filter_params.min_intensity]
        if filter_params.max_intensity is not None:
            filtered_motifs = [m for m in filtered_motifs if m.intensity <= filter_params.max_intensity]
        
        # Filter by region
        if filter_params.region_id:
            filtered_motifs = [m for m in filtered_motifs 
                               if m.location and m.location.region_id == filter_params.region_id]
        
        # Filter by multiple regions
        if filter_params.region_ids:
            filtered_motifs = [m for m in filtered_motifs 
                               if m.location and m.location.region_id in filter_params.region_ids]
        
        # Filter by global flag
        if filter_params.is_global is not None:
            filtered_motifs = [m for m in filtered_motifs if (m.scope == MotifScope.GLOBAL) == filter_params.is_global]
        
        # Filter by effect type
        if filter_params.effect_type:
            filtered_motifs = [m for m in filtered_motifs 
                               if any(e.effect_type == filter_params.effect_type for e in m.effects)]
        
        # Filter by metadata
        if filter_params.metadata:
            filtered_motifs = self._filter_by_metadata(filtered_motifs, filter_params.metadata)
        
        # Filter by tags
        if filter_params.tags:
            filtered_motifs = [m for m in filtered_motifs 
                               if any(tag in m.tags for tag in filter_params.tags)]
        
        # Filter by creation time
        if filter_params.created_after:
            filtered_motifs = [m for m in filtered_motifs if m.created_at >= filter_params.created_after]
        if filter_params.created_before:
            filtered_motifs = [m for m in filtered_motifs if m.created_at <= filter_params.created_before]
        
        # Filter by update time
        if filter_params.updated_after:
            filtered_motifs = [m for m in filtered_motifs if m.updated_at >= filter_params.updated_after]
        if filter_params.updated_before:
            filtered_motifs = [m for m in filtered_motifs if m.updated_at <= filter_params.updated_before]
        
        # Sort results if specified
        if filter_params.sort_by:
            reverse = filter_params.sort_order == "desc"
            filtered_motifs = sorted(
                filtered_motifs,
                key=lambda m: getattr(m, filter_params.sort_by, 0) if hasattr(m, filter_params.sort_by) else 0,
                reverse=reverse
            )
        
        return filtered_motifs
    
    def _filter_by_metadata(self, motifs: List[Motif], metadata_filters: Dict[str, Any]) -> List[Motif]:
        """
        Filter motifs by metadata key-value pairs.
        
        Args:
            motifs: List of motifs to filter
            metadata_filters: Dict of metadata key-value pairs to match
            
        Returns:
            List of motifs with matching metadata
        """
        filtered = []
        
        for motif in motifs:
            if not motif.metadata:
                continue
                
            # Check if all metadata filters match
            matches_all = True
            for key, value in metadata_filters.items():
                # Skip motifs that don't have the metadata key
                if key not in motif.metadata:
                    matches_all = False
                    break
                    
                # If the value is None, just check if the key exists
                if value is None:
                    continue
                    
                # Check if the values match
                if motif.metadata[key] != value:
                    matches_all = False
                    break
            
            if matches_all:
                filtered.append(motif)
        
        return filtered
    
    def cleanup_expired_motifs(self) -> int:
        """Mark motifs that have passed their end_time as dormant."""
        count = 0
        now = datetime.now()
        
        for motif in self._motifs.values():
            if (motif.lifecycle != MotifLifecycle.DORMANT and
                motif.end_time and motif.end_time <= now):
                
                motif.lifecycle = MotifLifecycle.DORMANT
                motif.updated_at = now
                self._save_motif(motif)
                count += 1
        
        return count
        
    # ==== Entity Data Methods ====
    
    def get_entity_data_path(self, entity_id: str) -> str:
        """Get the file path for entity motif data."""
        return os.path.join(self.data_path, "entities", f"{entity_id}.json")
        
    async def get_entity_data(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Get motif-related data for an entity (NPC, PC, etc.)
        
        Args:
            entity_id: The entity's unique identifier
            
        Returns:
            Dict containing entity motif data or None if not found
        """
        file_path = self.get_entity_data_path(entity_id)
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading entity data from {file_path}: {e}")
            return None
    
    async def update_entity_data(self, entity_id: str, data: Dict[str, Any]) -> bool:
        """
        Update motif-related data for an entity
        
        Args:
            entity_id: The entity's unique identifier
            data: The updated entity data
            
        Returns:
            True if successful, False otherwise
        """
        # Ensure entity data directory exists
        entity_dir = os.path.join(self.data_path, "entities")
        os.makedirs(entity_dir, exist_ok=True)
        
        file_path = self.get_entity_data_path(entity_id)
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving entity data to {file_path}: {e}")
            return False
            
    # ==== World Log Methods ====
    
    def get_world_log_path(self) -> str:
        """Get the file path for the world log."""
        return os.path.join(self.data_path, "world_log.json")
        
    async def get_world_log(self) -> List[Dict[str, Any]]:
        """
        Get the world event log
        
        Returns:
            List of world events
        """
        file_path = self.get_world_log_path()
        if not os.path.exists(file_path):
            return []
            
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading world log from {file_path}: {e}")
            return []
    
    async def add_to_world_log(self, event_id: str, event_data: Dict[str, Any]) -> bool:
        """
        Add an event to the world log
        
        Args:
            event_id: Unique identifier for the event
            event_data: Event data to log
            
        Returns:
            True if successful, False otherwise
        """
        log = await self.get_world_log()
        log.append(event_data)
        
        # Keep only the most recent 1000 events
        if len(log) > 1000:
            log = log[-1000:]
            
        file_path = self.get_world_log_path()
        try:
            with open(file_path, "w") as f:
                json.dump(log, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving world log to {file_path}: {e}")
            return False
    
    async def get_world_log_events(self, 
                             event_type: Optional[str] = None,
                             limit: int = 100,
                             offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get filtered events from the world log
        
        Args:
            event_type: Optional type to filter by
            limit: Maximum number of events to return
            offset: Number of events to skip
            
        Returns:
            List of matching events
        """
        log = await self.get_world_log()
        
        # Filter by event type if specified
        if event_type:
            log = [event for event in log if event.get("type") == event_type]
            
        # Apply offset and limit
        return log[offset:offset+limit] 