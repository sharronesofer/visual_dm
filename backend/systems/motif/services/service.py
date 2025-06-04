"""
Business service layer for the motif system.

This module handles business logic and orchestrates interactions between
the repository layer and external services.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import json
import random
from pathlib import Path

from backend.infrastructure.systems.motif.models import (
    Motif, MotifCreate, MotifUpdate, MotifFilter, MotifScope, 
    MotifLifecycle, MotifCategory, MotifEvolutionTrigger
)
from backend.infrastructure.systems.motif.repositories import MotifRepository
from backend.systems.motif.utils.motif_utils import (
    generate_descriptors_from_theme,
    determine_tone_from_theme, 
    determine_narrative_direction,
    synthesize_motifs,
    are_motifs_conflicting
)

logger = logging.getLogger(__name__)


class MotifService:
    """Core service for motif operations using rich configuration"""
    
    def __init__(self, repository: MotifRepository):
        self.repository = repository
        
        # Load configuration for enhanced functionality
        config_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "systems" / "motif" / "motif_config.json"
        self.config = self._load_config(config_path)
        
    def _load_config(self, path: Path) -> Dict[str, Any]:
        """Load motif configuration"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Could not load motif config from {path}: {e}")
            return {}

    async def create_motif_from_action(self, action_type: str, context: Dict[str, Any]) -> Optional[Motif]:
        """
        Create a motif based on an action using configuration mapping
        
        Args:
            action_type: Type of action that occurred (e.g., 'heroic_deed', 'betrayal')
            context: Context information for the motif
            
        Returns:
            Created motif or None if action type not recognized
        """
        try:
            # Map action to motif category using config
            action_mapping = self.config.get('action_to_motif_mapping', {})
            if action_type not in action_mapping:
                logger.warning(f"Unknown action type: {action_type}")
                return None
            
            category_str = action_mapping[action_type]
            category = MotifCategory(category_str.lower())
            
            # Generate name using config
            name = self._generate_motif_name(category, context.get('scope', MotifScope.LOCAL))
            
            # Create motif data
            motif_data = MotifCreate(
                name=name,
                description=self._generate_description_from_action(action_type, context),
                category=category,
                scope=context.get('scope', MotifScope.LOCAL),
                intensity=context.get('intensity', 5),
                location=context.get('location'),
                metadata={'source_action': action_type, 'created_from': 'action_mapping'}
            )
            
            return await self.create_motif(motif_data)
            
        except Exception as e:
            logger.error(f"Error creating motif from action {action_type}: {e}")
            return None
    
    def _generate_motif_name(self, category: MotifCategory, scope: MotifScope) -> str:
        """Generate a thematic name for a motif using configuration"""
        name_config = self.config.get('name_generation', {}).get(category.value.upper(), {})
        
        if not name_config:
            # Fallback to simple naming
            return f"{category.value.title()} of the {scope.value.title()}"
        
        base_names = name_config.get('base_names', [category.value.title()])
        modifiers = name_config.get('modifiers', ['of the Unknown'])
        
        # Select appropriate modifier based on scope
        if scope == MotifScope.GLOBAL:
            scope_modifiers = [m for m in modifiers if any(word in m.lower() for word in ['world', 'universal', 'cosmic', 'eternal', 'infinite'])]
        elif scope == MotifScope.REGIONAL:
            scope_modifiers = [m for m in modifiers if any(word in m.lower() for word in ['land', 'regional', 'territorial', 'local', 'provincial'])]
        elif scope == MotifScope.PLAYER_CHARACTER:
            scope_modifiers = [m for m in modifiers if any(word in m.lower() for word in ['hero', 'personal', 'individual', 'chosen', 'destined'])]
        else:  # LOCAL
            scope_modifiers = [m for m in modifiers if any(word in m.lower() for word in ['place', 'intimate', 'immediate', 'close'])]
        
        if not scope_modifiers:
            scope_modifiers = modifiers
        
        import random
        base = random.choice(base_names)
        modifier = random.choice(scope_modifiers)
        
        return f"{base} {modifier}"
    
    def _generate_description_from_action(self, action_type: str, context: Dict[str, Any]) -> str:
        """Generate a description based on the action type and context"""
        action_descriptions = {
            'heroic_deed': 'A moment of heroism that inspires hope and courage in those who witness it.',
            'betrayal': 'An act of treachery that shatters trust and breeds suspicion.',
            'sacrifice': 'A selfless act that demonstrates the power of putting others before oneself.',
            'revenge': 'A quest for retribution that consumes and drives those affected.',
            'discovery': 'A revelation that changes understanding and opens new possibilities.',
            'destruction': 'An act of devastation that leaves lasting scars on the land and people.',
            'protection': 'A demonstration of care and defense that creates safety and security.',
            'leadership': 'An ascension to power that changes the dynamics of authority.',
            'deception': 'A web of lies that obscures truth and creates false realities.',
            'redemption': 'A journey of atonement that offers hope for transformation.'
        }
        
        base_description = action_descriptions.get(action_type, f'An event related to {action_type}.')
        
        # Enhance with context
        location = context.get('location_name', 'this place')
        if 'character_name' in context:
            base_description += f" The actions of {context['character_name']} in {location} have created ripples that influence the narrative atmosphere."
        else:
            base_description += f" This event in {location} has created a lasting thematic influence."
        
        return base_description
    
    async def detect_motif_conflicts_with_config(self) -> List[Dict[str, Any]]:
        """Detect motif conflicts using configuration relationship data"""
        try:
            all_motifs = await self.list_motifs()
            conflicts = []
            
            opposing_pairs = self.config.get('theme_relationships', {}).get('opposing_pairs', [])
            
            for pair in opposing_pairs:
                theme_a, theme_b = pair
                
                # Find motifs of each opposing category
                motifs_a = [m for m in all_motifs if m.category.value == theme_a]
                motifs_b = [m for m in all_motifs if m.category.value == theme_b]
                
                # Check for conflicts based on proximity and intensity
                for motif_a in motifs_a:
                    for motif_b in motifs_b:
                        if self._motifs_are_proximate(motif_a, motif_b):
                            conflict_intensity = (motif_a.get_effective_intensity() + motif_b.get_effective_intensity()) / 2
                            
                            conflicts.append({
                                'motif_a': {
                                    'id': motif_a.id,
                                    'name': motif_a.name,
                                    'category': motif_a.category.value,
                                    'intensity': motif_a.get_effective_intensity()
                                },
                                'motif_b': {
                                    'id': motif_b.id,
                                    'name': motif_b.name,
                                    'category': motif_b.category.value,
                                    'intensity': motif_b.get_effective_intensity()
                                },
                                'conflict_type': 'opposing_themes',
                                'conflict_intensity': conflict_intensity,
                                'resolution_suggestion': self._suggest_conflict_resolution(motif_a, motif_b)
                            })
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error detecting motif conflicts: {e}")
            return []
    
    def _motifs_are_proximate(self, motif_a: Motif, motif_b: Motif) -> bool:
        """Check if two motifs are close enough to conflict"""
        # Global motifs always interact
        if motif_a.scope == MotifScope.GLOBAL or motif_b.scope == MotifScope.GLOBAL:
            return True
        
        # Same region motifs interact
        if (motif_a.scope == MotifScope.REGIONAL and motif_b.scope == MotifScope.REGIONAL and
            motif_a.location and motif_b.location and 
            motif_a.location.region_id == motif_b.location.region_id):
            return True
        
        # Local motifs within range
        if (motif_a.location and motif_b.location and
            motif_a.location.x is not None and motif_a.location.y is not None and
            motif_b.location.x is not None and motif_b.location.y is not None):
            
            distance = ((motif_a.location.x - motif_b.location.x) ** 2 + 
                       (motif_a.location.y - motif_b.location.y) ** 2) ** 0.5
            
            max_range = max(motif_a.location.radius, motif_b.location.radius, 100.0)
            return distance <= max_range
        
        return False
    
    def _suggest_conflict_resolution(self, motif_a: Motif, motif_b: Motif) -> str:
        """Suggest how to resolve conflicts between opposing motifs"""
        intensity_diff = abs(motif_a.get_effective_intensity() - motif_b.get_effective_intensity())
        
        if intensity_diff >= 3:
            return "dominance"  # Stronger motif should dominate
        elif intensity_diff >= 1:
            return "tension"    # Create dramatic tension
        else:
            return "synthesis"  # Try to blend into complex theme
    
    async def create_chaos_event_motif(self, event_category: str, event_description: str, context: Dict[str, Any]) -> Optional[Motif]:
        """Create a motif based on a chaos event from configuration"""
        try:
            chaos_events = self.config.get('chaos_events', {})
            if event_category not in chaos_events:
                logger.warning(f"Unknown chaos event category: {event_category}")
                return None
            
            # Map event category to appropriate motif category
            category_mapping = {
                'political': MotifCategory.BETRAYAL,
                'supernatural': MotifCategory.REVELATION,
                'social': MotifCategory.PARANOIA,
                'criminal': MotifCategory.DECEPTION,
                'temporal': MotifCategory.DESTINY,
                'relational': MotifCategory.LOYALTY
            }
            
            category = category_mapping.get(event_category, MotifCategory.CHAOS)
            
            motif_data = MotifCreate(
                name=f"Chaos of {event_category.title()}",
                description=f"A chaotic event has occurred: {event_description}. This disruption creates lasting narrative ripples.",
                category=category,
                scope=context.get('scope', MotifScope.LOCAL),
                intensity=context.get('intensity', 6),  # Chaos events tend to be more intense
                location=context.get('location'),
                metadata={
                    'source': 'chaos_event',
                    'event_category': event_category,
                    'event_description': event_description
                }
            )
            
            return await self.create_motif(motif_data)
            
        except Exception as e:
            logger.error(f"Error creating chaos event motif: {e}")
            return None
    
    async def find_complementary_motifs(self, motif: Motif) -> List[Motif]:
        """Find motifs that complement the given motif using configuration"""
        try:
            all_motifs = await self.list_motifs()
            complementary_pairs = self.config.get('theme_relationships', {}).get('complementary_pairs', [])
            
            complementary_motifs = []
            
            for pair in complementary_pairs:
                theme_a, theme_b = pair
                
                if motif.category.value == theme_a:
                    # Look for motifs of theme_b
                    complements = [m for m in all_motifs if m.category.value == theme_b and m.id != motif.id]
                    complementary_motifs.extend(complements)
                elif motif.category.value == theme_b:
                    # Look for motifs of theme_a
                    complements = [m for m in all_motifs if m.category.value == theme_a and m.id != motif.id]
                    complementary_motifs.extend(complements)
            
            return complementary_motifs
            
        except Exception as e:
            logger.error(f"Error finding complementary motifs: {e}")
            return []

    async def create_motif(self, motif_data: MotifCreate) -> Motif:
        """Create a new motif with business logic applied."""
        motif = Motif(**motif_data.dict())
        
        # Add descriptors based on the theme if not provided
        if not motif.descriptors:
            motif.descriptors = generate_descriptors_from_theme(motif.theme)
        
        # Determine tone and narrative direction if not provided
        if not motif.tone:
            motif.tone = determine_tone_from_theme(motif.theme)
        
        if not motif.narrative_direction:
            motif.narrative_direction = determine_narrative_direction(motif.theme)
        
        return await self.repository.create_motif(motif)

    async def get_motif(self, motif_id: str) -> Optional[Motif]:
        """Get a motif by ID."""
        return await self.repository.get_motif(motif_id)

    async def update_motif(self, motif_id: str, motif_update: MotifUpdate) -> Optional[Motif]:
        """Update an existing motif."""
        # Convert to dict and remove None values
        update_data = {k: v for k, v in motif_update.dict().items() if v is not None}
        return await self.repository.update_motif(motif_id, update_data)

    async def delete_motif(self, motif_id: str) -> bool:
        """Delete a motif."""
        try:
            # Check if motif exists first
            motif = await self.get_motif(motif_id)
            if not motif:
                return False
            
            # In a real implementation, this would call repository.delete_motif
            # For now, we'll simulate it
            logger.info(f"Deleting motif: {motif_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting motif {motif_id}: {e}")
            return False

    async def list_motifs(self, filter_params: MotifFilter = None, limit: int = 50, offset: int = 0) -> List[Motif]:
        """
        List motifs based on filter criteria.
        
        Args:
            filter_params: Filter criteria to apply
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of motifs matching the criteria
        """
        if filter_params is None:
            return self.repository.get_all_motifs()
        return self.repository.filter_motifs(filter_params)

    async def count_motifs(self, filter_params: MotifFilter = None) -> int:
        """
        Count motifs matching the filter criteria.
        
        Args:
            filter_params: Filter criteria to apply
            
        Returns:
            Count of matching motifs
        """
        try:
            # For now, use list_motifs and count the results
            # In a real implementation, this would be a dedicated count query
            motifs = await self.list_motifs(filter_params)
            return len(motifs)
        except Exception as e:
            logger.error(f"Error counting motifs: {e}")
            return 0

    async def get_global_motifs(self) -> List[Motif]:
        """Get all active global motifs."""
        return self.repository.get_global_motifs()

    async def get_regional_motifs(self, region_id: str) -> List[Motif]:
        """Get all active motifs for a specific region."""
        return self.repository.get_regional_motifs(region_id)

    async def get_motifs_at_position(self, x: float, y: float, radius: float = 50.0) -> List[Motif]:
        """Get all motifs that affect a specific position."""
        # For now, return empty list - implement based on repository capabilities
        logger.info(f"Getting motifs at position ({x}, {y}) with radius {radius}")
        return []

    async def get_motif_context(self, x: Optional[float] = None, y: Optional[float] = None) -> Dict[str, Any]:
        """
        Get narrative context for AI systems.
        
        Args:
            x: X coordinate (optional)
            y: Y coordinate (optional)
            
        Returns:
            Context dictionary for narrative generation
        """
        motifs = []
        
        # If position is provided, get motifs at that position
        if x is not None and y is not None:
            motifs = await self.get_motifs_at_position(x, y)
        else:
            # Get global motifs as fallback
            motifs = await self.get_global_motifs()
        
        # Extract narrative themes
        narrative_themes = self._extract_narrative_themes(motifs)
        
        # Determine dominant motif
        dominant_motif = motifs[0].name if motifs else None
        
        # Build active motifs list
        active_motifs = [
            {
                "name": motif.name,
                "description": motif.description,
                "category": motif.category.value,
                "intensity": motif.intensity,
                "scope": motif.scope.value,
            }
            for motif in motifs
        ]
        
        return {
            "active_motifs": active_motifs,
            "dominant_motif": dominant_motif,
            "narrative_themes": narrative_themes,
            "motif_count": len(motifs),
            "narrative_guidance": "No active motifs affecting this location." if not motifs else f"{len(motifs)} motifs influencing this area"
        }

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

    async def get_enhanced_narrative_context(self, context_size: str = "medium") -> Dict[str, Any]:
        """
        Get enhanced narrative context for AI systems.
        
        Args:
            context_size: Size of context ('small', 'medium', 'large')
            
        Returns:
            Enhanced context for narrative generation
        """
        all_motifs = await self.list_motifs()
        
        if not all_motifs:
            return {
                "has_motifs": False,
                "prompt_text": "No active motifs are influencing the narrative.",
                "context_size": context_size
            }
        
        # Use synthesize_motifs to create enhanced context
        synthesis = synthesize_motifs(all_motifs)
        
        if context_size == "small":
            prompt_text = f"Theme: {synthesis['theme']} (intensity: {synthesis['intensity']})"
        elif context_size == "large":
            descriptors = ", ".join(synthesis.get('descriptors', []))
            prompt_text = (
                f"Dominant theme: {synthesis['theme']} with intensity {synthesis['intensity']}. "
                f"Tone: {synthesis['tone']}. Direction: {synthesis['narrative_direction']}. "
                f"Descriptors: {descriptors}."
            )
        else:  # medium
            prompt_text = (
                f"Theme: {synthesis['theme']} (intensity: {synthesis['intensity']}) "
                f"creates a {synthesis['tone']} atmosphere."
            )
        
        return {
            "has_motifs": True,
            "prompt_text": prompt_text,
            "synthesis": synthesis,
            "context_size": context_size
        }

    async def update_motif_lifecycle(self, motif_id: str, new_lifecycle: MotifLifecycle) -> Optional[Motif]:
        """
        Update a motif's lifecycle state.
        
        Args:
            motif_id: ID of the motif to update
            new_lifecycle: New lifecycle state
            
        Returns:
            Updated motif or None if not found
        """
        try:
            motif = await self.get_motif(motif_id)
            if not motif:
                return None
            
            # Update lifecycle
            motif.lifecycle = new_lifecycle
            
            # In a real implementation, save to repository
            logger.info(f"Updated lifecycle for motif {motif_id} to {new_lifecycle}")
            return motif
        except Exception as e:
            logger.error(f"Error updating lifecycle for motif {motif_id}: {e}")
            return None

    async def advance_motif_lifecycles(self) -> int:
        """
        Advance all eligible motif lifecycles.
        
        Returns:
            Number of motifs advanced
        """
        try:
            # For now, simulate advancement
            logger.info("Advancing motif lifecycles")
            return 0
        except Exception as e:
            logger.error(f"Error advancing lifecycles: {e}")
            return 0

    async def trigger_motif_evolution(
        self, 
        motif_id: str, 
        trigger_type: MotifEvolutionTrigger,
        trigger_description: str
    ) -> Optional[Dict[str, Any]]:
        """
        Manually trigger motif evolution.
        
        Args:
            motif_id: ID of the motif to evolve
            trigger_type: Type of trigger causing evolution
            trigger_description: Description of the trigger event
            
        Returns:
            Evolution result or None if failed
        """
        try:
            motif = await self.get_motif(motif_id)
            if not motif:
                return None
            
            logger.info(f"Triggered evolution for motif {motif_id} with trigger {trigger_type}")
            return {
                "motif_id": motif_id,
                "evolved": True,
                "trigger_type": trigger_type.value,
                "trigger_description": trigger_description,
                "changes": {
                    "intensity": {"old": motif.intensity, "new": motif.intensity + 1}
                }
            }
            
        except Exception as e:
            logger.error(f"Error triggering evolution for motif {motif_id}: {e}")
            return None

    async def get_motif_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive motif system statistics.
        
        Returns:
            Dictionary containing various statistics
        """
        try:
            # Get all motifs for statistics
            all_motifs = await self.list_motifs()
            
            # Basic counts
            total_motifs = len(all_motifs)
            
            # Count by scope
            scope_counts = {}
            for scope in MotifScope:
                scope_counts[scope.value] = len([m for m in all_motifs if m.scope == scope])
            
            # Count by lifecycle
            lifecycle_counts = {}
            for lifecycle in MotifLifecycle:
                lifecycle_counts[lifecycle.value] = len([m for m in all_motifs if m.lifecycle == lifecycle])
            
            # Count by category (top 10)
            category_counts = {}
            for motif in all_motifs:
                cat = motif.category.value
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            top_categories = dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            
            # Intensity distribution
            intensity_avg = sum(m.intensity for m in all_motifs) / len(all_motifs) if all_motifs else 0
            intensity_distribution = {}
            for i in range(1, 11):
                intensity_distribution[str(i)] = len([m for m in all_motifs if m.intensity == i])
            
            # Active conflicts
            conflicts = await self.get_active_conflicts()
            
            return {
                "timestamp": datetime.utcnow(),
                "total_motifs": total_motifs,
                "scope_distribution": scope_counts,
                "lifecycle_distribution": lifecycle_counts,
                "top_categories": top_categories,
                "intensity_statistics": {
                    "average": round(intensity_avg, 2),
                    "distribution": intensity_distribution
                },
                "active_conflicts": len(conflicts),
                "system_health": "healthy" if total_motifs > 0 else "no_motifs"
            }
            
        except Exception as e:
            logger.error(f"Error getting motif statistics: {e}")
            return {
                "timestamp": datetime.utcnow(),
                "error": str(e),
                "system_health": "error"
            }

    async def get_active_conflicts(self) -> List[Dict[str, Any]]:
        """
        Get all active motif conflicts.
        
        Returns:
            List of conflict information
        """
        try:
            all_motifs = await self.list_motifs()
            conflicts = []
            
            # Check for conflicts between all pairs of motifs
            for i, motif1 in enumerate(all_motifs):
                for motif2 in all_motifs[i+1:]:
                    # Use the conflict detection from motif_utils
                    if are_motifs_conflicting(motif1, motif2):
                        conflict = {
                            "motif_a": {
                                "id": motif1.id,
                                "name": motif1.name,
                                "category": motif1.category.value,
                                "theme": getattr(motif1, 'theme', motif1.category.value)
                            },
                            "motif_b": {
                                "id": motif2.id,
                                "name": motif2.name,
                                "category": motif2.category.value,
                                "theme": getattr(motif2, 'theme', motif2.category.value)
                            },
                            "conflict_type": "opposing_themes",
                            "severity": "medium",
                            "detected_at": datetime.utcnow()
                        }
                        conflicts.append(conflict)
            
            logger.info(f"Found {len(conflicts)} active motif conflicts")
            return conflicts
            
        except Exception as e:
            logger.error(f"Error getting active conflicts: {e}")
            return []

    async def resolve_conflicts(self, auto_resolve: bool = True) -> int:
        """
        Resolve active motif conflicts.
        
        Args:
            auto_resolve: Whether to automatically resolve conflicts
            
        Returns:
            Number of conflicts resolved
        """
        try:
            conflicts = await self.get_active_conflicts()
            resolved_count = 0
            
            if not auto_resolve:
                logger.info("Manual conflict resolution not implemented - requires specific conflict handling")
                return 0
            
            # Auto-resolution: reduce intensity of weaker conflicting motifs
            for conflict in conflicts:
                motif_a_id = conflict["motif_a"]["id"]
                motif_b_id = conflict["motif_b"]["id"]
                
                motif_a = await self.get_motif(motif_a_id)
                motif_b = await self.get_motif(motif_b_id)
                
                if motif_a and motif_b:
                    # Reduce intensity of the weaker motif
                    if motif_a.intensity > motif_b.intensity:
                        motif_b.intensity = max(1, motif_b.intensity - 1)
                        logger.info(f"Reduced intensity of motif {motif_b.id} due to conflict with {motif_a.id}")
                    elif motif_b.intensity > motif_a.intensity:
                        motif_a.intensity = max(1, motif_a.intensity - 1)
                        logger.info(f"Reduced intensity of motif {motif_a.id} due to conflict with {motif_b.id}")
                    else:
                        # Equal intensity - reduce both slightly
                        motif_a.intensity = max(1, motif_a.intensity - 1)
                        motif_b.intensity = max(1, motif_b.intensity - 1)
                        logger.info(f"Reduced intensity of both conflicting motifs {motif_a.id} and {motif_b.id}")
                    
                    resolved_count += 1
            
            logger.info(f"Auto-resolved {resolved_count} motif conflicts")
            return resolved_count
            
        except Exception as e:
            logger.error(f"Error resolving conflicts: {e}")
            return 0

    async def process_evolution_triggers(self) -> Dict[str, Any]:
        """
        Process all pending motif evolution triggers.
        
        Returns:
            Summary of evolution processing results
        """
        try:
            all_motifs = await self.list_motifs()
            
            evolution_results = {
                "processed": 0,
                "evolved": 0,
                "failed": 0,
                "details": []
            }
            
            for motif in all_motifs:
                try:
                    # Check if motif is ready for evolution based on various factors
                    if self._should_evolve_motif(motif):
                        # Trigger automatic evolution
                        result = await self.trigger_motif_evolution(
                            motif_id=motif.id,
                            trigger_type=MotifEvolutionTrigger.TIME_PROGRESSION,
                            trigger_description="Automatic evolution based on system analysis"
                        )
                        
                        if result:
                            evolution_results["evolved"] += 1
                            evolution_results["details"].append({
                                "motif_id": motif.id,
                                "name": motif.name,
                                "action": "evolved",
                                "result": result
                            })
                        else:
                            evolution_results["failed"] += 1
                    
                    evolution_results["processed"] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing evolution for motif {motif.id}: {e}")
                    evolution_results["failed"] += 1
            
            logger.info(f"Evolution processing complete: {evolution_results['evolved']} evolved out of {evolution_results['processed']} processed")
            return evolution_results
            
        except Exception as e:
            logger.error(f"Error in evolution processing: {e}")
            return {"error": str(e), "processed": 0, "evolved": 0, "failed": 0}

    def _should_evolve_motif(self, motif: Motif) -> bool:
        """
        Determine if a motif should evolve based on business rules.
        
        Args:
            motif: Motif to evaluate
            
        Returns:
            True if motif should evolve
        """
        # High intensity motifs are more likely to evolve
        if motif.intensity >= 8:
            return True
        
        # Motifs in EMERGING state that have been around for a while
        if motif.lifecycle == MotifLifecycle.EMERGING and motif.created_at:
            time_since_creation = datetime.utcnow() - motif.created_at
            if time_since_creation.days >= 7:  # 7 days
                return True
        
        # STABLE motifs with very high intensity
        if motif.lifecycle == MotifLifecycle.STABLE and motif.intensity >= 9:
            return True
        
        return False

    async def generate_canonical_motifs(self, force_regenerate: bool = False) -> Dict[str, Any]:
        """
        Generate the 50 canonical motifs as specified in the Bible.
        
        Args:
            force_regenerate: Whether to regenerate existing canonical motifs
            
        Returns:
            Generation results summary
        """
        try:
            # Check if canonical motifs already exist
            existing_canonical = await self.list_motifs(
                MotifFilter(scope=MotifScope.GLOBAL, active_only=False)
            )
            
            canonical_count = len([m for m in existing_canonical if getattr(m, 'is_canonical', False)])
            
            if canonical_count >= 50 and not force_regenerate:
                return {
                    "status": "exists",
                    "message": f"Found {canonical_count} existing canonical motifs",
                    "generated": 0,
                    "existing": canonical_count
                }
            
            # Load name generation templates
            from backend.systems.motif.utils.config_validator import load_motif_config
            config = load_motif_config()
            name_generation = config.get("name_generation", {})
            
            generated_count = 0
            results = []
            
            # Generate canonical motifs for each category
            for category_name, templates in name_generation.items():
                try:
                    category = MotifCategory(category_name)
                    base_names = templates.get("base_names", [])
                    modifiers = templates.get("modifiers", [])
                    
                    if base_names and modifiers:
                        # Generate one canonical motif for this category
                        canonical_name = f"{base_names[0]} {modifiers[0]}"
                        
                        canonical_motif_data = MotifCreate(
                            name=canonical_name,
                            description=f"Canonical {category_name.lower()} motif representing core narrative themes",
                            category=category,
                            scope=MotifScope.GLOBAL,
                            intensity=5,  # Moderate baseline intensity
                            theme=category_name.lower(),
                            descriptors=[category_name.lower(), "canonical", "permanent"],
                            is_canonical=True
                        )
                        
                        canonical_motif = await self.create_motif(canonical_motif_data)
                        generated_count += 1
                        
                        results.append({
                            "category": category_name,
                            "name": canonical_name,
                            "id": canonical_motif.id
                        })
                        
                except Exception as e:
                    logger.error(f"Error generating canonical motif for {category_name}: {e}")
            
            logger.info(f"Generated {generated_count} canonical motifs")
            return {
                "status": "generated",
                "message": f"Generated {generated_count} canonical motifs",
                "generated": generated_count,
                "existing": canonical_count,
                "details": results
            }
            
        except Exception as e:
            logger.error(f"Error generating canonical motifs: {e}")
            return {"status": "error", "message": str(e), "generated": 0}

    async def cleanup_expired_motifs(self) -> int:
        """
        Clean up motifs that have reached CONCLUDED lifecycle.
        
        Returns:
            Number of motifs cleaned up
        """
        try:
            # Get all concluded motifs
            concluded_filter = MotifFilter(
                lifecycle=MotifLifecycle.CONCLUDED,
                active_only=False
            )
            concluded_motifs = await self.list_motifs(concluded_filter)
            
            cleanup_count = 0
            
            for motif in concluded_motifs:
                # Only cleanup non-canonical motifs that have been concluded for a while
                if not getattr(motif, 'is_canonical', False):
                    # Check if motif has been concluded for long enough
                    if motif.updated_at:
                        time_since_conclusion = datetime.utcnow() - motif.updated_at
                        if time_since_conclusion.days >= 30:  # 30 days
                            success = await self.delete_motif(motif.id)
                            if success:
                                cleanup_count += 1
                                logger.info(f"Cleaned up expired motif: {motif.id}")
            
            logger.info(f"Cleaned up {cleanup_count} expired motifs")
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired motifs: {e}")
            return 0

    async def analyze_motif_interactions(self, region_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze interactions between motifs in a region or globally.
        
        Args:
            region_id: Optional region to analyze (None for global analysis)
            
        Returns:
            Analysis results including synergies and conflicts
        """
        try:
            # Get motifs to analyze
            if region_id:
                motifs = await self.get_regional_motifs(region_id)
            else:
                motifs = await self.list_motifs(MotifFilter(active_only=True))
            
            if len(motifs) < 2:
                return {
                    "region_id": region_id,
                    "motif_count": len(motifs),
                    "interactions": [],
                    "synergies": [],
                    "conflicts": [],
                    "summary": "Insufficient motifs for interaction analysis"
                }
            
            interactions = []
            synergies = []
            conflicts = []
            
            # Analyze all pairs of motifs
            for i, motif1 in enumerate(motifs):
                for motif2 in motifs[i+1:]:
                    # Check for conflicts using utility function
                    if are_motifs_conflicting(motif1, motif2):
                        conflict = {
                            "motif_a": {"id": motif1.id, "name": motif1.name, "category": motif1.category.value},
                            "motif_b": {"id": motif2.id, "name": motif2.name, "category": motif2.category.value},
                            "type": "opposing_themes",
                            "severity": self._calculate_conflict_severity(motif1, motif2)
                        }
                        conflicts.append(conflict)
                    else:
                        # Check for potential synergies
                        synergy_strength = self._calculate_synergy_strength(motif1, motif2)
                        if synergy_strength > 0.5:
                            synergy = {
                                "motif_a": {"id": motif1.id, "name": motif1.name, "category": motif1.category.value},
                                "motif_b": {"id": motif2.id, "name": motif2.name, "category": motif2.category.value},
                                "strength": synergy_strength,
                                "type": "complementary_themes"
                            }
                            synergies.append(synergy)
                    
                    # Record the interaction
                    interactions.append({
                        "motif_a": motif1.id,
                        "motif_b": motif2.id,
                        "type": "conflict" if are_motifs_conflicting(motif1, motif2) else "neutral"
                    })
            
            return {
                "region_id": region_id,
                "motif_count": len(motifs),
                "interactions": interactions,
                "synergies": synergies,
                "conflicts": conflicts,
                "summary": f"Analyzed {len(interactions)} interactions: {len(conflicts)} conflicts, {len(synergies)} synergies"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing motif interactions: {e}")
            return {"error": str(e), "region_id": region_id}

    def _calculate_conflict_severity(self, motif1: Motif, motif2: Motif) -> str:
        """Calculate the severity of a conflict between two motifs."""
        # Base severity on intensity difference and absolute intensities
        intensity_sum = motif1.intensity + motif2.intensity
        
        if intensity_sum >= 16:  # Both very high intensity
            return "high"
        elif intensity_sum >= 12:  # Moderate to high intensity
            return "medium"
        else:
            return "low"

    def _calculate_synergy_strength(self, motif1: Motif, motif2: Motif) -> float:
        """Calculate synergy strength between two motifs."""
        # Simple synergy calculation based on complementary themes
        # This would be enhanced with more sophisticated logic
        
        # Motifs in same scope have higher synergy potential
        scope_bonus = 0.3 if motif1.scope == motif2.scope else 0.0
        
        # Similar intensity levels create better synergy
        intensity_diff = abs(motif1.intensity - motif2.intensity)
        intensity_bonus = max(0, 0.4 - (intensity_diff * 0.05))
        
        # Base synergy calculation
        base_synergy = 0.3
        
        return min(1.0, base_synergy + scope_bonus + intensity_bonus)

    async def optimize_motif_distribution(self) -> Dict[str, Any]:
        """
        Optimize the distribution of motifs across regions and scopes.
        
        Returns:
            Optimization results and recommendations
        """
        try:
            all_motifs = await self.list_motifs()
            
            # Analyze current distribution
            scope_counts = {}
            for scope in MotifScope:
                scope_counts[scope.value] = len([m for m in all_motifs if m.scope == scope])
            
            # Calculate recommendations
            recommendations = []
            total_motifs = len(all_motifs)
            
            # Check if distribution follows recommended patterns
            global_ratio = scope_counts.get(MotifScope.GLOBAL.value, 0) / max(total_motifs, 1)
            regional_ratio = scope_counts.get(MotifScope.REGIONAL.value, 0) / max(total_motifs, 1)
            local_ratio = scope_counts.get(MotifScope.LOCAL.value, 0) / max(total_motifs, 1)
            
            # Recommended ratios: 20% global, 40% regional, 40% local
            if global_ratio < 0.15:
                recommendations.append({
                    "type": "increase_global",
                    "message": "Consider adding more global motifs for world-spanning themes",
                    "current": f"{global_ratio:.1%}",
                    "recommended": "20%"
                })
            
            if regional_ratio < 0.30:
                recommendations.append({
                    "type": "increase_regional", 
                    "message": "Consider adding more regional motifs for location-specific themes",
                    "current": f"{regional_ratio:.1%}",
                    "recommended": "40%"
                })
            
            return {
                "total_motifs": total_motifs,
                "distribution": scope_counts,
                "ratios": {
                    "global": f"{global_ratio:.1%}",
                    "regional": f"{regional_ratio:.1%}",
                    "local": f"{local_ratio:.1%}"
                },
                "recommendations": recommendations,
                "optimized": len(recommendations) == 0
            }
            
        except Exception as e:
            logger.error(f"Error optimizing motif distribution: {e}")
            return {"error": str(e), "optimized": False}


class MotifEvolutionEngine:
    """Background service for automatic motif evolution"""
    
    def __init__(self, motif_manager: 'MotifManager'):
        self.motif_manager = motif_manager
        self.is_running = False
        self.evolution_task = None
        
        # Load evolution rules from configuration
        config_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "systems" / "motif" / "motif_config.json"
        self.config = self._load_config(config_path)
        
    def _load_config(self, path: Path) -> Dict[str, Any]:
        """Load motif configuration"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load motif config from {path}: {e}")
            return {}
    
    async def start_evolution_service(self):
        """Start the background evolution service"""
        if self.is_running:
            return
            
        self.is_running = True
        self.evolution_task = asyncio.create_task(self._evolution_loop())
        
    async def stop_evolution_service(self):
        """Stop the background evolution service"""
        self.is_running = False
        if self.evolution_task:
            self.evolution_task.cancel()
            try:
                await self.evolution_task
            except asyncio.CancelledError:
                pass
    
    async def _evolution_loop(self):
        """Main evolution loop - runs every hour"""
        while self.is_running:
            try:
                await self._process_time_based_evolution()
                await asyncio.sleep(3600)  # Check every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in motif evolution loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _process_time_based_evolution(self):
        """Process automatic time-based motif evolution"""
        try:
            # Get all active motifs
            all_motifs = await self.motif_manager.get_motifs()
            current_time = datetime.utcnow()
            
            for motif in all_motifs:
                # Skip concluded motifs
                if motif.lifecycle == MotifLifecycle.CONCLUDED:
                    continue
                
                # Check for time-based evolution rules
                eligible_rules = motif.can_evolve(MotifEvolutionTrigger.TIME_PASSAGE)
                
                for rule in eligible_rules:
                    # Check if enough time has passed since last evolution
                    if motif.last_evolution:
                        hours_since_evolution = (current_time - motif.last_evolution).total_seconds() / 3600
                        if hours_since_evolution < rule.cooldown_hours:
                            continue
                    
                    # Check probability
                    if random.random() > rule.probability:
                        continue
                    
                    # Check intensity threshold
                    if rule.requires_intensity_threshold and motif.get_effective_intensity() < rule.requires_intensity_threshold:
                        continue
                    
                    # Apply evolution
                    await self._apply_evolution_rule(motif, rule, MotifEvolutionTrigger.TIME_PASSAGE)
                
                # Check for natural lifecycle progression
                await self._check_natural_progression(motif, current_time)
                
        except Exception as e:
            print(f"Error processing time-based motif evolution: {e}")
    
    async def _apply_evolution_rule(self, motif, rule: MotifEvolutionRule, trigger: MotifEvolutionTrigger):
        """Apply an evolution rule to a motif"""
        changes = {}
        
        # Apply intensity change
        if rule.intensity_change != 0:
            new_intensity = max(1, min(10, motif.intensity + rule.intensity_change))
            motif.intensity = new_intensity
            changes['intensity'] = {'old': motif.intensity - rule.intensity_change, 'new': new_intensity}
        
        # Apply lifecycle change
        if rule.lifecycle_change:
            old_lifecycle = motif.lifecycle
            motif.lifecycle = rule.lifecycle_change
            changes['lifecycle'] = {'old': old_lifecycle, 'new': rule.lifecycle_change}
        
        # Apply category change (transformation)
        if rule.category_change:
            old_category = motif.category
            motif.category = rule.category_change
            changes['category'] = {'old': old_category, 'new': rule.category_change}
        
        # Update motif
        motif.last_evolution = datetime.utcnow()
        motif.updated_at = datetime.utcnow()
        
        # Record evolution in history
        evolution_event = {
            'timestamp': datetime.utcnow().isoformat(),
            'trigger': trigger.value,
            'rule_applied': rule.trigger_condition,
            'changes': changes
        }
        motif.evolution_history.append(evolution_event)
        
        # Save motif
        await self.motif_manager.update_motif(motif.id, motif)
        
        print(f"Motif '{motif.name}' evolved: {rule.trigger_condition}")
    
    async def _check_natural_progression(self, motif, current_time: datetime):
        """Check for natural lifecycle progression based on age and intensity"""
        if not motif.start_time:
            return
        
        age_hours = (current_time - motif.start_time).total_seconds() / 3600
        age_days = age_hours / 24
        
        # Natural progression based on configured thresholds
        evolution_config = self.config.get('evolution', {})
        
        # Emerging -> Stable
        if motif.lifecycle == MotifLifecycle.EMERGING and age_days >= evolution_config.get('emerging_to_stable_days', 2):
            motif.lifecycle = MotifLifecycle.STABLE
            await self._record_natural_evolution(motif, 'natural_maturation', 'Motif matured to stable phase')
        
        # Stable -> Waning (based on duration)
        elif motif.lifecycle == MotifLifecycle.STABLE and age_days >= motif.duration_days * 0.7:
            motif.lifecycle = MotifLifecycle.WANING
            await self._record_natural_evolution(motif, 'natural_aging', 'Motif entered waning phase due to age')
        
        # Waning -> Dormant or Concluded
        elif motif.lifecycle == MotifLifecycle.WANING:
            if age_days >= motif.duration_days:
                # Check if motif should go dormant or conclude
                dormancy_chance = evolution_config.get('dormancy_chance', 0.3)
                if random.random() < dormancy_chance and motif.intensity >= 3:
                    motif.lifecycle = MotifLifecycle.DORMANT
                    motif.intensity = max(1, motif.intensity - 2)  # Reduce intensity when going dormant
                    await self._record_natural_evolution(motif, 'natural_dormancy', 'Motif went dormant')
                else:
                    motif.lifecycle = MotifLifecycle.CONCLUDED
                    await self._record_natural_evolution(motif, 'natural_conclusion', 'Motif concluded naturally')
    
    async def _record_natural_evolution(self, motif, event_type: str, description: str):
        """Record a natural evolution event"""
        motif.last_evolution = datetime.utcnow()
        motif.updated_at = datetime.utcnow()
        
        evolution_event = {
            'timestamp': datetime.utcnow().isoformat(),
            'trigger': 'natural_progression',
            'event_type': event_type,
            'description': description,
            'lifecycle': motif.lifecycle.value
        }
        motif.evolution_history.append(evolution_event)
        
        await self.motif_manager.update_motif(motif.id, motif)
        
    async def trigger_event_evolution(self, event_type: str, event_data: Dict[str, Any]):
        """Trigger motif evolution based on external events"""
        try:
            all_motifs = await self.motif_manager.get_motifs()
            
            for motif in all_motifs:
                if motif.lifecycle == MotifLifecycle.CONCLUDED:
                    continue
                
                # Check for event-triggered evolution rules
                eligible_rules = motif.can_evolve(MotifEvolutionTrigger.WORLD_EVENT)
                
                for rule in eligible_rules:
                    # Check if rule matches this event type
                    if event_type in rule.trigger_condition:
                        # Check probability and other conditions
                        if random.random() <= rule.probability:
                            await self._apply_evolution_rule(motif, rule, MotifEvolutionTrigger.WORLD_EVENT)
                            
        except Exception as e:
            print(f"Error processing event-triggered motif evolution: {e}")


class MotifManager(MotifService):
    """Enhanced manager for motif operations with evolution and conflict resolution"""
    
    def __init__(self, repository: MotifRepository):
        super().__init__(repository)
        self.evolution_engine = MotifEvolutionEngine(self)
        self._service_started = False
        
    async def start_service(self):
        """Start the motif management service including background evolution"""
        if not self._service_started:
            await self.evolution_engine.start_evolution_service()
            self._service_started = True
            logger.info("Motif management service started")
    
    async def stop_service(self):
        """Stop the motif management service"""
        if self._service_started:
            await self.evolution_engine.stop_evolution_service()
            self._service_started = False
            logger.info("Motif management service stopped")
    
    async def trigger_external_event(self, event_type: str, event_data: Dict[str, Any]):
        """Trigger motif evolution based on external system events"""
        await self.evolution_engine.trigger_event_evolution(event_type, event_data)

    # ... existing methods ... 