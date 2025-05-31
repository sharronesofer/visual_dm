from typing import List, Dict, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import random
import math
import logging
import json
import asyncio
from fastapi import HTTPException, Depends, status

from backend.systems.motif.models import (
    Motif, MotifCreate, MotifUpdate, MotifFilter, 
    MotifScope, MotifLifecycle, MotifCategory, MotifEffect, MotifEffectTarget
)
from backend.systems.motif.repositories import MotifRepository, Vector2
from backend.systems.motif import motif_utils
from backend.infrastructure.shared.utils.time import get_current_time

logger = logging.getLogger(__name__)

class MotifService:
    """Service for motif business logic and operations."""
    
    def __init__(self, repository: MotifRepository = None):
        """Initialize the service with a repository."""
        self.repository = repository or MotifRepository()
    
    async def create_motif(self, motif_data: MotifCreate) -> Motif:
        """Create a new motif."""
        motif = Motif(**motif_data.dict())
        
        # Set start/end times based on duration
        start_time = get_current_time()
        end_time = start_time + timedelta(days=motif.duration_days)
        
        motif.start_time = start_time
        motif.end_time = end_time
        motif.created_at = start_time
        motif.updated_at = start_time
        
        # Add descriptors based on the theme if not provided
        if not motif.descriptors:
            motif.descriptors = motif_utils.generate_descriptors_from_theme(motif.theme)
        
        # Determine tone and narrative direction if not provided
        if not motif.tone:
            motif.tone = motif_utils.determine_tone_from_theme(motif.theme)
        
        if not motif.narrative_direction:
            motif.narrative_direction = motif_utils.determine_narrative_direction(motif.theme)
        
        return await self.repository.create_motif(motif)
    
    async def get_motif(self, motif_id: str) -> Optional[Motif]:
        """Get a motif by ID."""
        return await self.repository.get_motif(motif_id)
    
    async def update_motif(self, motif_id: str, motif_update: MotifUpdate) -> Optional[Motif]:
        """Update a motif."""
    async def update_motif(self, motif_id: int, motif_data: MotifUpdate) -> Optional[Motif]:
        """Update an existing motif."""
        # Convert to dict and remove None values
        update_data = {k: v for k, v in motif_data.dict().items() if v is not None}
        return self.repository.update_motif(motif_id, update_data)
    
    async def delete_motif(self, motif_id: int) -> bool:
        """Delete a motif."""
        return self.repository.delete_motif(motif_id)
    
    async def list_motifs(self, filter_params: MotifFilter = None) -> List[Motif]:
        """List motifs with optional filtering."""
        if filter_params is None:
            return self.repository.get_all_motifs()
        return self.repository.filter_motifs(filter_params)
    
    async def get_global_motifs(self) -> List[Motif]:
        """Get all active global motifs."""
        return self.repository.get_global_motifs()
    
    async def get_regional_motifs(self, region_id: str) -> List[Motif]:
        """Get all active motifs for a specific region."""
        return self.repository.get_regional_motifs(region_id)
    
    async def get_motifs_at_position(
        self, x: float, y: float, radius: float = 0
    ) -> List[Motif]:
        """Get all motifs that affect a specific position."""
        position = Vector2(x, y)
        return self.repository.get_motifs_at_position(position, radius)
    
    async def get_motif_context(
        self, x: Optional[float] = None, y: Optional[float] = None, region_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a context dictionary describing the active motifs at a position or region.
        This is useful for narrative generation.
        """
        motifs = []
        
        # If position is provided, get motifs at that position
        if x is not None and y is not None:
            motifs = await self.get_motifs_at_position(x, y)
        # If only region is provided, get regional motifs
        elif region_id is not None:
            motifs = await self.get_regional_motifs(region_id)
            # Include global motifs too
            motifs.extend(await self.get_global_motifs())
        # Otherwise, just get global motifs
        else:
            motifs = await self.get_global_motifs()
        
        # Sort motifs by intensity (highest first)
        motifs.sort(key=lambda m: m.intensity, reverse=True)
        
        # Build the context
        context = {
            "active_motifs": [
                {
                    "name": motif.name,
                    "description": motif.description,
                    "category": motif.category.value,
                    "intensity": motif.intensity,
                    "scope": motif.scope.value,
                }
                for motif in motifs
            ],
            "dominant_motif": motifs[0].name if motifs else None,
            "narrative_themes": self._extract_narrative_themes(motifs),
            "motif_count": len(motifs),
        }
        
        return context
    
    def _extract_narrative_themes(self, motifs: List[Motif]) -> List[str]:
        """Extract narrative themes from a list of motifs."""
        themes = []
        
        # Extract key narrative themes based on motif categories
        for motif in motifs:
            if motif.category == MotifCategory.BETRAYAL:
                themes.append("trust is fragile")
            elif motif.category == MotifCategory.CHAOS:
                themes.append("unpredictability and disorder")
            elif motif.category == MotifCategory.DEATH:
                themes.append("mortality and loss")
            elif motif.category == MotifCategory.HOPE:
                themes.append("optimism despite adversity")
            # Add more mappings as needed
            
            # Use intensity to determine the strength of the theme
            if motif.intensity >= 7:
                themes.append(f"overwhelming {motif.category.value}")
            elif motif.intensity >= 4:
                themes.append(f"prominent {motif.category.value}")
        
        return themes
    
    async def get_enhanced_narrative_context(
        self, x: Optional[float] = None, y: Optional[float] = None, 
        region_id: Optional[str] = None, context_size: str = "medium"
    ) -> Dict[str, Any]:
        """
        Get enhanced narrative context information suitable for direct use in GPT prompts.
        
        Parameters:
        - x, y: Optional coordinates to get context for a specific location
        - region_id: Optional region ID to get context for a specific region
        - context_size: Size of context to generate ('small', 'medium', 'large')
        
        Returns a rich context dictionary with themes, tone, and narrative guidance.
        """
        # Get active motifs based on region or coordinates
        motifs = []
        location_type = "unknown"
        location_name = "this area"
        
        # If position is provided, get motifs at that position
        if x is not None and y is not None:
            motifs = await self.get_motifs_at_position(x, y)
            location_type = "location"
            location_name = f"this location ({x:.1f}, {y:.1f})"
        # If only region is provided, get regional motifs
        elif region_id is not None:
            motifs = await self.get_regional_motifs(region_id)
            # Include global motifs too
            motifs.extend(await self.get_global_motifs())
            location_type = "region"
            location_name = f"the {region_id} region"
        # Otherwise, just get global motifs
        else:
            motifs = await self.get_global_motifs()
            location_type = "world"
            location_name = "the world"
        
        if not motifs:
            return {
                "has_motifs": False,
                "prompt_text": f"In {location_name}, events unfold naturally without any overarching thematic influence.",
                "themes": [],
                "location_type": location_type,
                "location_name": location_name
            }
        
        # Use motif_utils to synthesize motifs
        synthesis = motif_utils.synthesize_motifs(motifs)
        
        # Create descriptive text based on context size
        if context_size == "small":
            prompt_text = (
                f"In {location_name}, the theme of {synthesis['theme']} "
                f"(intensity: {synthesis['intensity']}) influences events with a {synthesis['tone']} tone."
            )
        elif context_size == "large":
            descriptors = ", ".join(synthesis['descriptors']) if synthesis['descriptors'] else "no strong descriptors"
            conflict_text = ""
            if synthesis['conflicts']:
                conflict_text = " Thematic tension is present."
                
            prompt_text = (
                f"In {location_name}, the dominant theme is {synthesis['theme']} "
                f"with an intensity of {synthesis['intensity']}. "
                f"The narrative tone is {synthesis['tone']} with a {synthesis['narrative_direction']} trajectory. "
                f"Key descriptors include: {descriptors}.{conflict_text} {synthesis['synthesis_summary']}"
            )
        else:  # medium (default)
            descriptors = ", ".join(synthesis['descriptors'][:3]) if synthesis['descriptors'] else "neutral elements"
            prompt_text = (
                f"In {location_name}, the {synthesis['theme']} theme "
                f"(intensity: {synthesis['intensity']}) creates a {synthesis['tone']} atmosphere "
                f"with a {synthesis['narrative_direction']} trend. "
                f"Characterized by {descriptors}."
            )
        
        # Generate specific narrative guidance based on synthesis
        narrative_guidance = self._generate_narrative_guidance(synthesis, motifs, location_type)
        
        return {
            "has_motifs": True,
            "prompt_text": prompt_text,
            "synthesis": synthesis,
            "narrativeGuidance": narrative_guidance,
            "location_type": location_type,
            "location_name": location_name,
            "active_motifs": [
                {
                    "id": motif.id,
                    "name": motif.name,
                    "theme": motif.category.value,
                    "intensity": motif.intensity,
                    "tone": getattr(motif, 'tone', 'neutral'),
                    "lifecycle": motif.lifecycle.value
                }
                for motif in motifs
            ]
        }
    
    def _generate_narrative_guidance(self, synthesis: Dict[str, Any], motifs: List[Motif], location_type: str) -> Dict[str, Any]:
        """Generate specific narrative guidance for GPT based on synthesized motifs"""
        # Extract dominant theme and properties
        theme = synthesis['theme']
        intensity = synthesis['intensity']
        tone = synthesis['tone']
        direction = synthesis['narrative_direction']
        
        # Base guidance structure
        guidance = {
            "theme": theme,
            "npcBehavior": {},
            "events": {},
            "environment": {},
            "dialogue": {},
        }
        
        # Add NPC behavior guidance
        if tone == "dark":
            guidance["npcBehavior"]["general"] = "NPCs tend to be cautious, suspicious, or pessimistic."
            guidance["npcBehavior"]["motivations"] = "Self-preservation is common."
        elif tone == "light":
            guidance["npcBehavior"]["general"] = "NPCs tend to be more cooperative and optimistic."
            guidance["npcBehavior"]["motivations"] = "Community-oriented goals are common."
        else:
            guidance["npcBehavior"]["general"] = "NPCs display a mix of attitudes and outlooks."
            
        # Add event guidance based on narrative direction
        if direction == "ascending":
            guidance["events"]["trend"] = "Events are trending toward resolution or improvement."
            guidance["events"]["pacing"] = "Increasing momentum toward positive outcomes."
        elif direction == "descending":
            guidance["events"]["trend"] = "Events are trending toward complication or deterioration."
            guidance["events"]["pacing"] = "Increasing stakes and tension."
        else:
            guidance["events"]["trend"] = "Events maintain their current trajectory without major shifts."
            
        # Add intensity-based guidance
        if intensity >= 7:
            guidance["intensity"] = "overwhelming"
            guidance["environment"] = "Physical environment strongly reflects the thematic elements."
            guidance["dialogue"]["emotion"] = "Dialogue should be emotionally charged."
        elif intensity >= 4:
            guidance["intensity"] = "significant"
            guidance["environment"] = "Physical environment notably reflects the thematic elements."
            guidance["dialogue"]["emotion"] = "Dialogue should contain noticeable emotional undertones."
        else:
            guidance["intensity"] = "subtle"
            guidance["environment"] = "Physical environment subtly hints at the thematic elements."
            guidance["dialogue"]["emotion"] = "Dialogue can contain subtle hints of the theme."
            
        # Theme-specific guidance (for major themes)
        if "hope" in theme.lower():
            guidance["dialogue"]["keywords"] = ["future", "possibility", "chance", "opportunity"]
            guidance["events"]["suggestions"] = ["Small victories", "Unexpected aid", "Discovery of resources"]
        elif "betrayal" in theme.lower():
            guidance["dialogue"]["keywords"] = ["trust", "loyalty", "deception", "suspicion"]
            guidance["events"]["suggestions"] = ["Revelations of hidden motives", "Broken alliances", "False information"]
        elif "chaos" in theme.lower():
            guidance["dialogue"]["keywords"] = ["unpredictable", "random", "disorder", "confusion"]
            guidance["events"]["suggestions"] = ["Unexpected complications", "Sudden changes", "Disrupted plans"]
            
        return guidance
    
    async def generate_random_motif(
        self, scope: MotifScope, region_id: Optional[str] = None
    ) -> Motif:
        """Generate a random motif with specified scope."""
        # Select a random category
        category = random.choice(list(MotifCategory))
        
        # Determine intensity based on scope
        intensity = 0
        if scope == MotifScope.GLOBAL:
            intensity = 7.0  # Global motifs always have intensity 7
            duration_days = random.randint(18, 38)  # 28 ±10 days
        else:
            # Regional or local motifs have intensity 1-6
            intensity = random.randint(1, 6)
            # Duration proportional to intensity
            duration_factor = random.randint(3, 6)
            duration_days = intensity * duration_factor
        
        # Build location info
        location = None
        if scope != MotifScope.GLOBAL:
            location = {
                "region_id": region_id,
                "position_x": None,
                "position_y": None,
                "radius": 0.0,
            }
            if scope == MotifScope.LOCAL:
                # For local motifs, we'd need specific coordinates
                # This is a placeholder; in practice you'd use real coordinates
                location["position_x"] = random.uniform(-100, 100)
                location["position_y"] = random.uniform(-100, 100)
                location["radius"] = random.uniform(1, 10)
        
        # Generate random effects
        effects = []
        effect_count = random.randint(1, 3)
        effect_types = [
            "npc_behavior", "event_frequency", "resource_yield",
            "relationship_change", "arc_development", "faction_tension",
            "weather_pattern", "economic_shift", "narrative_flavor"
        ]
        
        for _ in range(effect_count):
            effect_type = random.choice(effect_types)
            effect = MotifEffect(
                effect_type=effect_type,
                intensity=intensity * random.uniform(0.8, 1.2),  # Slight variation
                target=random.choice(["general", "npc", "environment", "event", "dialogue"]),
                data={}
            )
            effects.append(effect)
        
        # Create the motif
        motif_data = MotifCreate(
            name=f"{category.value.capitalize()} {scope.value.capitalize()}",
            description=f"A {category.value} motif with {scope.value} scope",
            category=category,
            scope=scope,
            lifecycle=MotifLifecycle.EMERGING,
            intensity=intensity,
            duration_days=duration_days,
            location=location,
            effects=effects,
        )
        
        return await self.create_motif(motif_data)
    
    async def advance_motif_lifecycles(self) -> int:
        """
        Advance the lifecycle of all motifs based on time.
        Returns the count of updated motifs.
        """
        all_motifs = self.repository.get_all_motifs()
        count = 0
        now = datetime.now()
        
        for motif in all_motifs:
            if motif.lifecycle == MotifLifecycle.DORMANT:
                continue
                
            if not motif.start_time or not motif.end_time:
                continue
                
            # Calculate progress through lifecycle (0.0 to 1.0)
            total_duration = (motif.end_time - motif.start_time).total_seconds()
            elapsed = (now - motif.start_time).total_seconds()
            progress = min(1.0, max(0.0, elapsed / total_duration))
            
            # Determine the appropriate lifecycle state
            new_lifecycle = None
            if progress < 0.25:
                new_lifecycle = MotifLifecycle.EMERGING
            elif progress < 0.75:
                new_lifecycle = MotifLifecycle.STABLE
            elif progress < 1.0:
                new_lifecycle = MotifLifecycle.WANING
            else:
                new_lifecycle = MotifLifecycle.DORMANT
            
            # Update if changed
            if new_lifecycle != motif.lifecycle:
                self.repository.update_motif(motif.id, {"lifecycle": new_lifecycle})
                count += 1
                
        # Also clean up any expired motifs
        count += self.repository.cleanup_expired_motifs()
        
        return count
    
    async def blend_motifs(self, motifs: List[Motif]) -> Optional[Dict[str, Any]]:
        """
        Blend multiple motifs to create a composite narrative effect.
        Returns a dictionary with the blended narrative context.
        """
        if not motifs:
            return None
            
        # Sort by intensity
        motifs.sort(key=lambda m: m.intensity, reverse=True)
        
        # Get the dominant motif (highest intensity)
        dominant = motifs[0]
        
        # Calculate the average intensity, weighted by each motif's individual intensity
        total_weight = sum(m.intensity for m in motifs)
        if total_weight == 0:
            return None
        
        # Combine all effects into a single list
        all_effects = []
        for motif in motifs:
            all_effects.extend(motif.effects)
        
        # Group effects by type and target
        effect_groups = {}
        for effect in all_effects:
            key = f"{effect.effect_type}:{effect.target}"
            if key not in effect_groups:
                effect_groups[key] = []
            effect_groups[key].append(effect)
        
        # Average each effect group
        blended_effects = []
        for key, effects in effect_groups.items():
            effect_type, target = key.split(":")
            avg_intensity = sum(e.intensity for e in effects) / len(effects)
            blended_effects.append({
                "effect_type": effect_type,
                "target": target,
                "intensity": avg_intensity,
            })
        
        # Create the blended result
        blend = {
            "dominant_motif": {
                "name": dominant.name,
                "category": dominant.category.value,
                "intensity": dominant.intensity,
            },
            "blended_intensity": total_weight / len(motifs),
            "contributing_motifs": [m.name for m in motifs],
            "motif_count": len(motifs),
            "blended_effects": blended_effects,
            "narrative_themes": self._extract_narrative_themes(motifs),
        }
        
        return blend
    
    async def generate_motif_sequence(
        self, sequence_length: int, region_id: Optional[str] = None
    ) -> List[Motif]:
        """
        Generate a sequence of related motifs for long-term narrative arcs.
        Returns a list of motifs in sequence.
        """
        sequence = []
        
        # Pick a starting category
        starting_category = random.choice(list(MotifCategory))
        
        # Generate related categories (thematic progression)
        categories = self._generate_related_categories(starting_category, sequence_length)
        
        # Generate motifs with these categories
        for i, category in enumerate(categories):
            # Determine scope - first one is global, others vary
            scope = MotifScope.GLOBAL if i == 0 else random.choice(list(MotifScope))
            
            # Create motif data
            motif_data = MotifCreate(
                name=f"{category.value.capitalize()} {scope.value.capitalize()}",
                description=f"Part {i+1} of a sequence starting with {starting_category.value}",
                category=category,
                scope=scope,
                lifecycle=MotifLifecycle.EMERGING,
                intensity=7.0 if scope == MotifScope.GLOBAL else random.randint(1, 6),
                duration_days=random.randint(18, 38) if scope == MotifScope.GLOBAL else None,
                location={"region_id": region_id} if scope != MotifScope.GLOBAL else None,
                metadata={"sequence_id": id(categories), "sequence_position": i},
            )
            
            # Create and store the motif
            motif = await self.create_motif(motif_data)
            sequence.append(motif)
        
        return sequence
    
    def _generate_related_categories(
        self, starting_category: MotifCategory, count: int
    ) -> List[MotifCategory]:
        """Generate a list of thematically related categories."""
        categories = [starting_category]
        all_categories = list(MotifCategory)
        
        # Define some thematic relationships (this is a simplified example)
        related_categories = {
            MotifCategory.BETRAYAL: [MotifCategory.VENGEANCE, MotifCategory.REDEMPTION],
            MotifCategory.HOPE: [MotifCategory.REBIRTH, MotifCategory.TRANSFORMATION],
            MotifCategory.FEAR: [MotifCategory.PARANOIA, MotifCategory.OBSESSION],
            # Add more relationships as needed
        }
        
        for _ in range(count - 1):
            current = categories[-1]
            if current in related_categories and random.random() < 0.7:
                # 70% chance to follow a thematic relationship
                next_category = random.choice(related_categories[current])
            else:
                # 30% chance for a random shift
                next_category = random.choice(all_categories)
                while next_category == current:
                    next_category = random.choice(all_categories)
            
            categories.append(next_category)
        
        return categories
    
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
        if target_systems is None:
            # Default to all systems
            target_systems = [
                "npc", "event", "quest", "faction", "environment", "economy", "narrative"
            ]
        
        result = {system: {"applied": False, "details": []} for system in target_systems}
        
        # Skip dormant motifs
        if motif.lifecycle == MotifLifecycle.DORMANT:
            return result
        
        # Calculate effect intensity based on lifecycle
        intensity_multiplier = {
            MotifLifecycle.EMERGING: 0.7,   # 70% effect while emerging
            MotifLifecycle.STABLE: 1.0,     # 100% effect while stable
            MotifLifecycle.WANING: 0.4,     # 40% effect while waning
        }.get(motif.lifecycle, 0.0)
        
        # Apply each effect to appropriate systems
        for effect in motif.effects:
            effective_intensity = effect.intensity * intensity_multiplier
            
            # Skip effects with negligible intensity
            if effective_intensity < 0.1:
                continue
            
            # Apply effect to each target system as appropriate
            if effect.effect_type == "npc_behavior" and "npc" in target_systems:
                result["npc"] = await self._apply_to_npc_system(motif, effect, effective_intensity)
            
            elif effect.effect_type == "event_frequency" and "event" in target_systems:
                result["event"] = await self._apply_to_event_system(motif, effect, effective_intensity)
            
            elif effect.effect_type == "arc_development" and "quest" in target_systems:
                result["quest"] = await self._apply_to_quest_system(motif, effect, effective_intensity)
            
            elif effect.effect_type == "faction_tension" and "faction" in target_systems:
                result["faction"] = await self._apply_to_faction_system(motif, effect, effective_intensity)
            
            elif effect.effect_type == "weather_pattern" and "environment" in target_systems:
                result["environment"] = await self._apply_to_environment_system(motif, effect, effective_intensity)
            
            elif effect.effect_type == "economic_shift" and "economy" in target_systems:
                result["economy"] = await self._apply_to_economy_system(motif, effect, effective_intensity)
            
            elif effect.effect_type == "narrative_flavor" and "narrative" in target_systems:
                result["narrative"] = await self._apply_to_narrative_system(motif, effect, effective_intensity)
        
        return result
    
    async def _apply_to_npc_system(self, motif: Motif, effect: MotifEffect, intensity: float) -> Dict[str, Any]:
        """Apply a motif effect to the NPC system."""
        # This would integrate with the NPC system to alter NPC behavior
        # For now, we'll implement a placeholder that can be expanded later
        
        result = {"applied": True, "details": []}
        
        try:
            # Example logic for NPC behavior modification
            mood_modifier = 0
            aggression_modifier = 0
            cooperation_modifier = 0
            
            # Different motif categories affect NPC behavior differently
            if motif.category == MotifCategory.BETRAYAL:
                mood_modifier -= intensity * 0.5
                aggression_modifier += intensity * 0.3
                cooperation_modifier -= intensity * 0.8
            elif motif.category == MotifCategory.CHAOS:
                mood_modifier -= intensity * 0.2
                aggression_modifier += intensity * 0.7
                cooperation_modifier -= intensity * 0.5
            elif motif.category == MotifCategory.HOPE:
                mood_modifier += intensity * 0.8
                aggression_modifier -= intensity * 0.4
                cooperation_modifier += intensity * 0.6
            # Add more category-specific logic as needed
            
            # Here you would call into the NPC system to apply these modifiers
            # Since we don't have direct references to other systems, 
            # we'll just record what would have happened
            
            behavior_changes = {
                "mood_modifier": mood_modifier,
                "aggression_modifier": aggression_modifier,
                "cooperation_modifier": cooperation_modifier,
                "source_motif": motif.name,
                "intensity": intensity
            }
            
            # Log the behavior changes to the result
            result["details"].append(f"NPC behavior modifiers: {behavior_changes}")
            
            # Example event dispatch for NPC system
            # In a real implementation, this might call an API endpoint or use an event bus
            # await self._emit_event("npc_behavior_modifiers", behavior_changes)
            
        except Exception as e:
            result["applied"] = False
            result["error"] = str(e)
        
        return result
    
    async def _apply_to_event_system(self, motif: Motif, effect: MotifEffect, intensity: float) -> Dict[str, Any]:
        """Apply a motif effect to the event generation system."""
        # This would integrate with the Event system to influence event frequency and types
        
        result = {"applied": True, "details": []}
        
        try:
            # Different motif categories affect event generation differently
            event_type_boosts = []
            frequency_modifier = 1.0  # Default: no change
            
            if motif.category == MotifCategory.BETRAYAL:
                event_type_boosts.append(("betrayal", intensity * 0.2))
                event_type_boosts.append(("conflict", intensity * 0.1))
            elif motif.category == MotifCategory.CHAOS:
                frequency_modifier += intensity * 0.05  # More events overall
                event_type_boosts.append(("disaster", intensity * 0.15))
                event_type_boosts.append(("accident", intensity * 0.1))
            elif motif.category == MotifCategory.HOPE:
                event_type_boosts.append(("celebration", intensity * 0.2))
                event_type_boosts.append(("discovery", intensity * 0.15))
            # Add more category-specific logic as needed
            
            # Create the event modifiers
            event_modifiers = {
                "frequency_modifier": frequency_modifier,
                "type_boosts": event_type_boosts,
                "source_motif": motif.name,
                "intensity": intensity
            }
            
            # Log the event changes to the result
            result["details"].append(f"Event modifiers: {event_modifiers}")
            
            # Example event dispatch for event system
            # await self._emit_event("event_generation_modifiers", event_modifiers)
            
        except Exception as e:
            result["applied"] = False
            result["error"] = str(e)
        
        return result
    
    async def _apply_to_quest_system(self, motif: Motif, effect: MotifEffect, intensity: float) -> Dict[str, Any]:
        """Apply a motif effect to the quest/arc system."""
        # This would integrate with the Quest/Arc system to influence quest generation and outcomes
        
        result = {"applied": True, "details": []}
        
        try:
            # Different motif categories affect quest generation differently
            quest_type_boosts = []
            difficulty_modifier = 0.0  # Default: no change
            reward_modifier = 0.0  # Default: no change
            
            if motif.category == MotifCategory.BETRAYAL:
                quest_type_boosts.append(("intrigue", intensity * 0.2))
                difficulty_modifier += intensity * 0.1  # Slightly harder
            elif motif.category == MotifCategory.CHAOS:
                quest_type_boosts.append(("rescue", intensity * 0.15))
                difficulty_modifier += intensity * 0.2  # Harder
            elif motif.category == MotifCategory.HOPE:
                quest_type_boosts.append(("restoration", intensity * 0.2))
                reward_modifier += intensity * 0.1  # Better rewards
            # Add more category-specific logic as needed
            
            # Create the quest modifiers
            quest_modifiers = {
                "difficulty_modifier": difficulty_modifier,
                "reward_modifier": reward_modifier,
                "type_boosts": quest_type_boosts,
                "source_motif": motif.name,
                "intensity": intensity
            }
            
            # Log the quest changes to the result
            result["details"].append(f"Quest modifiers: {quest_modifiers}")
            
            # Example event dispatch for quest system
            # await self._emit_event("quest_generation_modifiers", quest_modifiers)
            
        except Exception as e:
            result["applied"] = False
            result["error"] = str(e)
        
        return result
    
    async def _apply_to_faction_system(self, motif: Motif, effect: MotifEffect, intensity: float) -> Dict[str, Any]:
        """Apply a motif effect to the faction system."""
        # This would integrate with the Faction system to influence faction relationships
        
        result = {"applied": True, "details": []}
        
        try:
            # Different motif categories affect faction dynamics differently
            tension_modifier = 0.0  # Default: no change
            alliance_chance_modifier = 0.0  # Default: no change
            
            if motif.category == MotifCategory.BETRAYAL:
                tension_modifier += intensity * 0.15  # Increased tension
                alliance_chance_modifier -= intensity * 0.2  # Less likely to ally
            elif motif.category == MotifCategory.CHAOS:
                tension_modifier += intensity * 0.1  # Slightly increased tension
                # Random factor for unpredictability
            elif motif.category == MotifCategory.UNITY:
                tension_modifier -= intensity * 0.2  # Decreased tension
                alliance_chance_modifier += intensity * 0.15  # More likely to ally
            # Add more category-specific logic as needed
            
            # Create the faction modifiers
            faction_modifiers = {
                "tension_modifier": tension_modifier,
                "alliance_chance_modifier": alliance_chance_modifier,
                "source_motif": motif.name,
                "intensity": intensity
            }
            
            # Log the faction changes to the result
            result["details"].append(f"Faction modifiers: {faction_modifiers}")
            
            # Example event dispatch for faction system
            # await self._emit_event("faction_relationship_modifiers", faction_modifiers)
            
        except Exception as e:
            result["applied"] = False
            result["error"] = str(e)
        
        return result
    
    async def _apply_to_environment_system(self, motif: Motif, effect: MotifEffect, intensity: float) -> Dict[str, Any]:
        """Apply a motif effect to the environment/weather system."""
        # This would integrate with the Environment system to influence weather patterns
        
        result = {"applied": True, "details": []}
        
        try:
            # Different motif categories affect environment differently
            weather_type_boosts = []
            severity_modifier = 0.0  # Default: no change
            
            if motif.category == MotifCategory.CHAOS:
                weather_type_boosts.append(("storm", intensity * 0.2))
                severity_modifier += intensity * 0.15  # More severe
            elif motif.category == MotifCategory.HOPE:
                weather_type_boosts.append(("clear", intensity * 0.15))
                severity_modifier -= intensity * 0.1  # Less severe
            elif motif.category == MotifCategory.SHADOW:
                weather_type_boosts.append(("fog", intensity * 0.2))
                weather_type_boosts.append(("overcast", intensity * 0.15))
            # Add more category-specific logic as needed
            
            # Create the environment modifiers
            environment_modifiers = {
                "weather_type_boosts": weather_type_boosts,
                "severity_modifier": severity_modifier,
                "source_motif": motif.name,
                "intensity": intensity
            }
            
            # Log the environment changes to the result
            result["details"].append(f"Environment modifiers: {environment_modifiers}")
            
            # Example event dispatch for environment system
            # await self._emit_event("environment_modifiers", environment_modifiers)
            
        except Exception as e:
            result["applied"] = False
            result["error"] = str(e)
        
        return result
    
    async def _apply_to_economy_system(self, motif: Motif, effect: MotifEffect, intensity: float) -> Dict[str, Any]:
        """Apply a motif effect to the economy system."""
        # This would integrate with the Economy system to influence prices, resource availability
        
        result = {"applied": True, "details": []}
        
        try:
            # Different motif categories affect economy differently
            price_modifier = 0.0  # Default: no change
            scarcity_modifiers = []
            
            if motif.category == MotifCategory.CHAOS:
                price_modifier += intensity * 0.2  # Price increase
                scarcity_modifiers.append(("essential_goods", intensity * 0.15))
            elif motif.category == MotifCategory.PROSPERITY:
                price_modifier -= intensity * 0.1  # Price decrease
                scarcity_modifiers.append(("luxury_goods", -intensity * 0.2))  # More abundant
            elif motif.category == MotifCategory.COLLAPSE:
                price_modifier += intensity * 0.3  # Significant price increase
                scarcity_modifiers.append(("all_goods", intensity * 0.25))  # More scarce
            # Add more category-specific logic as needed
            
            # Create the economy modifiers
            economy_modifiers = {
                "price_modifier": price_modifier,
                "scarcity_modifiers": scarcity_modifiers,
                "source_motif": motif.name,
                "intensity": intensity
            }
            
            # Log the economy changes to the result
            result["details"].append(f"Economy modifiers: {economy_modifiers}")
            
            # Example event dispatch for economy system
            # await self._emit_event("economy_modifiers", economy_modifiers)
            
        except Exception as e:
            result["applied"] = False
            result["error"] = str(e)
        
        return result
    
    async def _apply_to_narrative_system(self, motif: Motif, effect: MotifEffect, intensity: float) -> Dict[str, Any]:
        """Apply a motif effect to the narrative generation system."""
        # This would integrate with the Narrative system to influence context for GPT
        
        result = {"applied": True, "details": []}
        
        try:
            # Different motif categories affect narrative differently
            narrative_themes = []
            tone_modifiers = {}
            
            # Base narrative elements from category
            if motif.category == MotifCategory.BETRAYAL:
                narrative_themes.append("betrayal")
                narrative_themes.append("suspicion")
                tone_modifiers["tension"] = intensity * 0.2
            elif motif.category == MotifCategory.CHAOS:
                narrative_themes.append("unpredictability")
                narrative_themes.append("disorder")
                tone_modifiers["urgency"] = intensity * 0.3
            elif motif.category == MotifCategory.HOPE:
                narrative_themes.append("optimism")
                narrative_themes.append("potential")
                tone_modifiers["positivity"] = intensity * 0.4
            # Add more category-specific logic as needed
            
            # Intensity affects how strongly themes are emphasized
            emphasis = "subtle" if intensity < 3 else ("notable" if intensity < 6 else "dominant")
            
            # Create the narrative context modifiers
            narrative_modifiers = {
                "themes": narrative_themes,
                "tone_modifiers": tone_modifiers,
                "emphasis": emphasis,
                "source_motif": motif.name,
                "intensity": intensity
            }
            
            # Log the narrative changes to the result
            result["details"].append(f"Narrative modifiers: {narrative_modifiers}")
            
            # Example event dispatch for narrative system
            # await self._emit_event("narrative_context_modifiers", narrative_modifiers)
            
        except Exception as e:
            result["applied"] = False
            result["error"] = str(e)
        
        return result 