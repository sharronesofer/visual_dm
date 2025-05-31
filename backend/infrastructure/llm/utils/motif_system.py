"""
Motif System for the DM module.

This module implements narrative motifs and themes that recur throughout the game world,
following the design described in the Development Bible.
"""

from typing import Dict, Any, List, Optional, Set, Union
import logging
from datetime import datetime, timedelta
import json
import math
import random
from uuid import uuid4
# from firebase_admin import db  # TODO: Replace with proper database integration
from pydantic import BaseModel, Field, ConfigDict

# TODO: Fix when DM event system is properly implemented
# from backend.systems.dm.event_integration import (
#     EventDispatcher, MotifEvent
# )

# ===== Motif Models =====

class MotifOccurrence(BaseModel):
    """
    Represents a single occurrence of a motif.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    motif_id: str
    entity_id: Optional[str] = None
    region_id: Optional[str] = None
    event_id: Optional[str] = None
    strength: float = 1.0  # 0.0 (background) to 2.0 (overwhelming)
    narrative_text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class Motif(BaseModel):
    """
    Represents a recurring motif/theme in the game world.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    category: str
    intensity: float = 1.0  # Base intensity of this motif (0.1 to 2.0)
    associated_emotions: List[str] = []
    opposing_motifs: List[str] = []
    complementary_motifs: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = True
    narrative_patterns: List[str] = []
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

# ===== Motif System =====

class MotifSystem:
    """
    Singleton manager for motif creation, tracking, and narrative pattern recognition.
    
    Implements the Motif Recurrence and Thematic Development mechanisms.
    """
    _instance = None
    
    # Motif categories
    MOTIF_CATEGORIES = [
        "element",      # Fire, water, earth, air
        "celestial",    # Sun, moon, stars
        "animal",       # Animals or creatures with symbolic meaning
        "object",       # Swords, cups, keys, etc.
        "place",        # Forest, mountain, sea, ruins
        "concept",      # Love, death, rebirth, betrayal
        "weather",      # Storm, fog, sunshine, wind
        "color",        # Red, black, gold, etc.
        "number",       # Three, seven, thirteen
        "direction",    # North, east, downward
        "time",         # Dawn, midnight, seasons
        "sound"         # Bell, whisper, thunder
    ]
    
    # Common emotions for association
    EMOTIONS = [
        "fear", "joy", "sadness", "anger", "disgust", 
        "surprise", "anticipation", "trust", "hope", "despair",
        "confusion", "curiosity", "pride", "shame", "envy",
        "contempt", "love", "hatred", "awe", "satisfaction",
        "disappointment", "relief", "nostalgia", "yearning"
    ]
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the MotifSystem."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the motif system."""
        if MotifSystem._instance is not None:
            raise Exception("This class is a singleton. Use get_instance() instead.")
        
        MotifSystem._instance = self
        # self.event_dispatcher = EventDispatcher.get_instance()
        
        # System parameters
        self.recurrence_threshold = 3  # Occurrences needed to detect a pattern
        self.intensity_decay = 0.1  # Per day decay rate for motif intensity
        self.amplification_factor = 1.2  # Multiplier for related motifs
        
        # Cache settings
        self.motif_cache = {}
        self.occurrence_cache = {}
        self.cache_ttl = timedelta(minutes=10)
        self.cache_timestamps = {}
    
    def create_motif(self, name: str, description: str, category: str,
                     intensity: float = 1.0, associated_emotions: List[str] = None,
                     narrative_patterns: List[str] = None, tags: List[str] = None,
                     opposing_motifs: List[str] = None, complementary_motifs: List[str] = None,
                     metadata: Dict[str, Any] = None) -> Motif:
        """
        Create a new motif.
        
        Args:
            name: Unique name for the motif
            description: Description of what this motif represents
            category: Category of the motif (from MOTIF_CATEGORIES)
            intensity: Base intensity (0.1 to 2.0)
            associated_emotions: List of emotions associated with this motif
            narrative_patterns: Example narrative expressions of this motif
            tags: Search tags for the motif
            opposing_motifs: IDs of motifs that oppose this one
            complementary_motifs: IDs of motifs that strengthen this one
            metadata: Additional data for the motif
            
        Returns:
            The created Motif object
        """
        # Validate category
        if category not in self.MOTIF_CATEGORIES:
            raise ValueError(f"Invalid motif category: {category}")
        
        # Validate emotions
        if associated_emotions:
            for emotion in associated_emotions:
                if emotion not in self.EMOTIONS:
                    raise ValueError(f"Invalid emotion: {emotion}")
        
        # Validate intensity
        intensity = max(0.1, min(2.0, intensity))
        
        # Create motif
        motif = Motif(
            name=name,
            description=description,
            category=category,
            intensity=intensity,
            associated_emotions=associated_emotions or [],
            opposing_motifs=opposing_motifs or [],
            complementary_motifs=complementary_motifs or [],
            narrative_patterns=narrative_patterns or [],
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Store in Firebase
        self._store_motif(motif)
        
        # Clear cache
        self._clear_motif_cache(motif.id)
        
        # Emit event
        # self.event_dispatcher.publish(MotifEvent(
        #     event_type="motif.created",
        #     motif_id=motif.id,
        #     motif_name=motif.name,
        #     motif_category=motif.category
        # ))
        
        return motif
    
    def record_occurrence(self, motif_id: str, narrative_text: str,
                          entity_id: Optional[str] = None, region_id: Optional[str] = None,
                          event_id: Optional[str] = None, strength: float = 1.0) -> MotifOccurrence:
        """
        Record an occurrence of a motif.
        
        Args:
            motif_id: ID of the motif
            narrative_text: Text description of how the motif appears in narrative
            entity_id: Optional entity associated with this occurrence
            region_id: Optional region associated with this occurrence
            event_id: Optional event ID associated with this occurrence
            strength: Strength of this occurrence (0.0 to 2.0)
            
        Returns:
            The created MotifOccurrence object
        """
        # Get motif to validate it exists
        motif = self.get_motif(motif_id)
        if not motif:
            raise ValueError(f"Motif {motif_id} not found")
        
        # Validate strength
        strength = max(0.0, min(2.0, strength))
        
        # Create occurrence
        occurrence = MotifOccurrence(
            motif_id=motif_id,
            entity_id=entity_id,
            region_id=region_id,
            event_id=event_id,
            strength=strength,
            narrative_text=narrative_text
        )
        
        # Store in Firebase
        self._store_occurrence(occurrence)
        
        # Update related motifs (opposing and complementary)
        self._update_related_motif_strengths(motif, strength)
        
        # Emit event
        # self.event_dispatcher.publish(MotifEvent(
        #     event_type="motif.occurrence",
        #     motif_id=motif_id,
        #     motif_name=motif.name,
        #     motif_category=motif.category,
        #     entity_id=entity_id,
        #     region_id=region_id,
        #     occurrence_id=occurrence.id,
        #     strength=strength
        # ))
        
        return occurrence
    
    def get_motif(self, motif_id: str) -> Optional[Motif]:
        """
        Get a motif by ID.
        
        Args:
            motif_id: The ID of the motif
            
        Returns:
            The Motif object or None if not found
        """
        # Check cache first
        if self._is_motif_cached(motif_id):
            motif_dict = self._get_motif_from_cache(motif_id)
            if motif_dict:
                return self._dict_to_motif(motif_dict)
        
        # Fetch from Firebase
        motif_ref = db.reference(f"/motifs/{motif_id}")
        motif_data = motif_ref.get()
        
        if not motif_data:
            return None
        
        # Cache it
        self._cache_motif(motif_id, motif_data)
        
        return self._dict_to_motif(motif_data)
    
    def get_motifs_by_category(self, category: str) -> List[Motif]:
        """
        Get all motifs in a specific category.
        
        Args:
            category: The category to filter by
            
        Returns:
            List of Motif objects in the category
        """
        # Validate category
        if category not in self.MOTIF_CATEGORIES:
            raise ValueError(f"Invalid motif category: {category}")
        
        # Query Firebase
        motifs_ref = db.reference("/motifs")
        all_motifs = motifs_ref.get() or {}
        
        result = []
        for motif_id, motif_data in all_motifs.items():
            if motif_data.get("category") == category and motif_data.get("active", True):
                motif_data["id"] = motif_id
                result.append(self._dict_to_motif(motif_data))
        
        return result
    
    def get_entity_motifs(self, entity_id: str, 
                          min_strength: float = 0.0, 
                          limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get motifs associated with a specific entity.
        
        Args:
            entity_id: The ID of the entity
            min_strength: Minimum strength threshold
            limit: Maximum number of motifs to return
            
        Returns:
            List of motif details with aggregated strength
        """
        # Get all occurrences for this entity
        occurrences_ref = db.reference("/motif_occurrences")
        all_occurrences = occurrences_ref.get() or {}
        
        # Group by motif_id and calculate aggregate strength
        motif_strengths = {}
        motif_occurrences = {}
        
        for occ_id, occ_data in all_occurrences.items():
            if occ_data.get("entity_id") == entity_id:
                motif_id = occ_data.get("motif_id")
                
                if motif_id not in motif_strengths:
                    motif_strengths[motif_id] = 0
                    motif_occurrences[motif_id] = []
                
                # Apply time decay
                created_at = datetime.fromisoformat(occ_data.get("created_at"))
                days_old = (datetime.utcnow() - created_at).days
                decay_factor = math.pow(1 - self.intensity_decay, days_old)
                
                # Add to strength
                motif_strengths[motif_id] += occ_data.get("strength", 1.0) * decay_factor
                motif_occurrences[motif_id].append(occ_data)
        
        # Get motif details and build result
        result = []
        for motif_id, strength in motif_strengths.items():
            # Skip if below threshold
            if strength < min_strength:
                continue
            
            motif = self.get_motif(motif_id)
            if motif:
                result.append({
                    "motif": motif.dict(),
                    "aggregate_strength": strength,
                    "occurrence_count": len(motif_occurrences[motif_id])
                })
        
        # Sort by aggregate strength (descending)
        result.sort(key=lambda r: r["aggregate_strength"], reverse=True)
        
        return result[:limit]
    
    def get_regional_motifs(self, region_id: str, 
                            min_strength: float = 0.0, 
                            limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get motifs associated with a specific region.
        
        Args:
            region_id: The ID of the region
            min_strength: Minimum strength threshold
            limit: Maximum number of motifs to return
            
        Returns:
            List of motif details with aggregated strength
        """
        # Get all occurrences for this region
        occurrences_ref = db.reference("/motif_occurrences")
        all_occurrences = occurrences_ref.get() or {}
        
        # Group by motif_id and calculate aggregate strength
        motif_strengths = {}
        motif_occurrences = {}
        
        for occ_id, occ_data in all_occurrences.items():
            if occ_data.get("region_id") == region_id:
                motif_id = occ_data.get("motif_id")
                
                if motif_id not in motif_strengths:
                    motif_strengths[motif_id] = 0
                    motif_occurrences[motif_id] = []
                
                # Apply time decay
                created_at = datetime.fromisoformat(occ_data.get("created_at"))
                days_old = (datetime.utcnow() - created_at).days
                decay_factor = math.pow(1 - self.intensity_decay, days_old)
                
                # Add to strength
                motif_strengths[motif_id] += occ_data.get("strength", 1.0) * decay_factor
                motif_occurrences[motif_id].append(occ_data)
        
        # Get motif details and build result
        result = []
        for motif_id, strength in motif_strengths.items():
            # Skip if below threshold
            if strength < min_strength:
                continue
            
            motif = self.get_motif(motif_id)
            if motif:
                result.append({
                    "motif": motif.dict(),
                    "aggregate_strength": strength,
                    "occurrence_count": len(motif_occurrences[motif_id])
                })
        
        # Sort by aggregate strength (descending)
        result.sort(key=lambda r: r["aggregate_strength"], reverse=True)
        
        return result[:limit]
    
    def get_most_common_motifs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most common motifs across the entire game world.
        
        Args:
            limit: Maximum number of motifs to return
            
        Returns:
            List of motif details with occurrence count and aggregate strength
        """
        # Get all occurrences
        occurrences_ref = db.reference("/motif_occurrences")
        all_occurrences = occurrences_ref.get() or {}
        
        if not all_occurrences:
            return []
        
        # Group by motif_id
        motif_counts = {}
        motif_strengths = {}
        
        for occ_id, occ_data in all_occurrences.items():
            motif_id = occ_data.get("motif_id")
            
            if motif_id not in motif_counts:
                motif_counts[motif_id] = 0
                motif_strengths[motif_id] = 0
            
            motif_counts[motif_id] += 1
            
            # Apply time decay
            created_at = datetime.fromisoformat(occ_data.get("created_at"))
            days_old = (datetime.utcnow() - created_at).days
            decay_factor = math.pow(1 - self.intensity_decay, days_old)
            
            # Add to strength
            motif_strengths[motif_id] += occ_data.get("strength", 1.0) * decay_factor
        
        # Get motif details and build result
        result = []
        for motif_id, count in motif_counts.items():
            motif = self.get_motif(motif_id)
            if motif:
                result.append({
                    "motif": motif.dict(),
                    "occurrence_count": count,
                    "aggregate_strength": motif_strengths[motif_id]
                })
        
        # Sort by occurrence count (descending)
        result.sort(key=lambda r: r["occurrence_count"], reverse=True)
        
        return result[:limit]
    
    def suggest_motifs_for_context(self, entity_id: Optional[str] = None, 
                                  region_id: Optional[str] = None,
                                  limit: int = 3) -> List[Dict[str, Any]]:
        """
        Suggest motifs appropriate for a narrative context.
        
        Args:
            entity_id: Optional entity ID for context
            region_id: Optional region ID for context
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested motifs with narrative patterns
        """
        motifs_to_score = []
        scored_motifs = []
        
        # Get entity motifs if provided
        if entity_id:
            entity_motifs = self.get_entity_motifs(entity_id, min_strength=0.5)
            for em in entity_motifs:
                motifs_to_score.append(em)
        
        # Get regional motifs if provided
        if region_id:
            region_motifs = self.get_regional_motifs(region_id, min_strength=0.5)
            for rm in region_motifs:
                # Check if we already have this motif from entity context
                if not any(m["motif"]["id"] == rm["motif"]["id"] for m in motifs_to_score):
                    motifs_to_score.append(rm)
        
        # If we don't have enough from context, get some common motifs
        if len(motifs_to_score) < limit:
            common_motifs = self.get_most_common_motifs(limit=limit*2)
            for cm in common_motifs:
                # Check if we already have this motif from other contexts
                if not any(m["motif"]["id"] == cm["motif"]["id"] for m in motifs_to_score):
                    motifs_to_score.append(cm)
        
        # Calculate appropriateness score
        for motif_data in motifs_to_score:
            motif = motif_data["motif"]
            base_score = motif_data.get("aggregate_strength", 1.0)
            
            # Check for related motifs
            if entity_id and region_id:
                # Look for complementary motifs in both entity and region
                for complementary_id in motif.get("complementary_motifs", []):
                    if any(m["motif"]["id"] == complementary_id for m in motifs_to_score):
                        base_score *= self.amplification_factor
                
                # Reduce score for opposing motifs
                for opposing_id in motif.get("opposing_motifs", []):
                    if any(m["motif"]["id"] == opposing_id for m in motifs_to_score):
                        base_score /= self.amplification_factor
            
            # Add some randomness
            randomness = random.uniform(0.8, 1.2)
            final_score = base_score * randomness
            
            # Prepare a suggestion
            suggestion = {
                "motif": motif,
                "score": final_score,
                "patterns": motif.get("narrative_patterns", []),
                "suggested_strength": min(2.0, base_score * random.uniform(0.9, 1.1))
            }
            
            scored_motifs.append(suggestion)
        
        # Sort by score
        scored_motifs.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top choices
        return scored_motifs[:limit]
    
    def get_motif_narrative_context(self, entity_id: Optional[str] = None,
                                   region_id: Optional[str] = None,
                                   max_motifs: int = 3) -> str:
        """
        Generate narrative context describing motifs for an entity or region.
        
        Args:
            entity_id: Optional entity ID
            region_id: Optional region ID
            max_motifs: Maximum motifs to include
            
        Returns:
            String of narrative context
        """
        context_lines = []
        
        if entity_id:
            # Get entity's motifs
            entity_motifs = self.get_entity_motifs(entity_id, limit=max_motifs)
            
            if entity_motifs:
                context_lines.append(f"Motifs associated with this character:")
                
                for i, m in enumerate(entity_motifs):
                    motif = m["motif"]
                    strength = m["aggregate_strength"]
                    
                    if strength > 1.5:
                        strength_text = "overwhelmingly present"
                    elif strength > 1.0:
                        strength_text = "strongly present"
                    elif strength > 0.6:
                        strength_text = "clearly present"
                    elif strength > 0.3:
                        strength_text = "subtly present"
                    else:
                        strength_text = "faintly present"
                    
                    context_lines.append(f"{i+1}. The {motif['name']} motif is {strength_text}.")
                    if motif.get("narrative_patterns") and random.random() < 0.7:
                        pattern = random.choice(motif["narrative_patterns"])
                        context_lines.append(f"   {pattern}")
        
        if region_id:
            # Get regional motifs
            region_motifs = self.get_regional_motifs(region_id, limit=max_motifs)
            
            if region_motifs:
                context_lines.append(f"Motifs present in this location:")
                
                for i, m in enumerate(region_motifs):
                    motif = m["motif"]
                    strength = m["aggregate_strength"]
                    
                    if strength > 1.5:
                        strength_text = "dramatically dominates"
                    elif strength > 1.0:
                        strength_text = "strongly influences"
                    elif strength > 0.6:
                        strength_text = "visibly shapes"
                    elif strength > 0.3:
                        strength_text = "subtly affects"
                    else:
                        strength_text = "faintly touches"
                    
                    context_lines.append(f"{i+1}. The {motif['name']} motif {strength_text} this place.")
                    if motif.get("narrative_patterns") and random.random() < 0.7:
                        pattern = random.choice(motif["narrative_patterns"])
                        context_lines.append(f"   {pattern}")
        
        return "\n".join(context_lines)
    
    # ===== Internal Methods =====
    
    def _store_motif(self, motif: Motif):
        """
        Store a motif in Firebase.
        
        Args:
            motif: The Motif object to store
        """
        motif_dict = motif.dict()
        
        # Convert datetime objects to ISO format for Firebase
        motif_dict["created_at"] = motif_dict["created_at"].isoformat()
        
        # Remove id field (it's the key)
        motif_id = motif_dict.pop("id")
        
        # Store in Firebase
        motif_ref = db.reference(f"/motifs/{motif_id}")
        motif_ref.set(motif_dict)
        
        # Update cache
        self._cache_motif(motif_id, motif_dict)
    
    def _store_occurrence(self, occurrence: MotifOccurrence):
        """
        Store a motif occurrence in Firebase.
        
        Args:
            occurrence: The MotifOccurrence object to store
        """
        occ_dict = occurrence.dict()
        
        # Convert datetime objects to ISO format for Firebase
        occ_dict["created_at"] = occ_dict["created_at"].isoformat()
        
        # Remove id field (it's the key)
        occ_id = occ_dict.pop("id")
        
        # Store in Firebase
        occ_ref = db.reference(f"/motif_occurrences/{occ_id}")
        occ_ref.set(occ_dict)
    
    def _update_related_motif_strengths(self, motif: Motif, occurrence_strength: float):
        """
        Update related motifs when a new occurrence is recorded.
        
        Args:
            motif: The motif that had a new occurrence
            occurrence_strength: The strength of the new occurrence
        """
        # Adjust complementary motifs (amplify)
        for complementary_id in motif.complementary_motifs:
            complementary = self.get_motif(complementary_id)
            if complementary:
                # Slightly increase intensity
                new_intensity = complementary.intensity * (1 + (occurrence_strength * 0.05))
                new_intensity = min(2.0, new_intensity)
                
                # Update in Firebase
                motif_ref = db.reference(f"/motifs/{complementary_id}")
                motif_ref.update({"intensity": new_intensity})
                
                # Clear cache
                self._clear_motif_cache(complementary_id)
        
        # Adjust opposing motifs (dampen)
        for opposing_id in motif.opposing_motifs:
            opposing = self.get_motif(opposing_id)
            if opposing:
                # Slightly decrease intensity
                new_intensity = opposing.intensity * (1 - (occurrence_strength * 0.05))
                new_intensity = max(0.1, new_intensity)
                
                # Update in Firebase
                motif_ref = db.reference(f"/motifs/{opposing_id}")
                motif_ref.update({"intensity": new_intensity})
                
                # Clear cache
                self._clear_motif_cache(opposing_id)
    
    def _dict_to_motif(self, motif_dict: Dict[str, Any]) -> Motif:
        """
        Convert a dict to a Motif object.
        
        Args:
            motif_dict: The motif dict
            
        Returns:
            Motif object
        """
        # Convert ISO strings to datetime
        if isinstance(motif_dict.get("created_at"), str):
            motif_dict["created_at"] = datetime.fromisoformat(motif_dict["created_at"])
        
        return Motif(**motif_dict)
    
    # ===== Cache Methods =====
    
    def _is_motif_cached(self, motif_id: str) -> bool:
        """
        Check if a motif is cached and not expired.
        
        Args:
            motif_id: The ID of the motif
            
        Returns:
            True if cached and not expired, False otherwise
        """
        if motif_id not in self.cache_timestamps:
            return False
        
        cache_time = self.cache_timestamps[motif_id]
        now = datetime.utcnow()
        
        return now - cache_time < self.cache_ttl
    
    def _cache_motif(self, motif_id: str, motif_dict: Dict[str, Any]):
        """
        Cache a motif.
        
        Args:
            motif_id: The ID of the motif
            motif_dict: The motif dict
        """
        self.motif_cache[motif_id] = motif_dict
        self.cache_timestamps[motif_id] = datetime.utcnow()
    
    def _clear_motif_cache(self, motif_id: str):
        """
        Clear the cache for a motif.
        
        Args:
            motif_id: The ID of the motif
        """
        if motif_id in self.motif_cache:
            del self.motif_cache[motif_id]
        
        if motif_id in self.cache_timestamps:
            del self.cache_timestamps[motif_id]
    
    def _get_motif_from_cache(self, motif_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a motif from the cache.
        
        Args:
            motif_id: The ID of the motif
            
        Returns:
            Motif dict or None if not found
        """
        if not self._is_motif_cached(motif_id):
            return None
        
        return self.motif_cache.get(motif_id)

# Initialize the motif system
motif_system = MotifSystem.get_instance() 