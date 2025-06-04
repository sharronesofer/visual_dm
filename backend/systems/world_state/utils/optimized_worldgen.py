"""
World_State system - Optimized World Generation.

Provides optimized algorithms for generating world content efficiently.
"""

import random
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import math

from backend.systems.world_state.world_types import WorldRegion, StateCategory, ResourceType

logger = logging.getLogger(__name__)


class OptimizedWorldGenerator:
    """Handles efficient generation of world content using optimized algorithms."""
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed or random.randint(1, 1000000)
        self.rng = random.Random(self.seed)
        logger.info(f"Initialized world generator with seed: {self.seed}")
    
    def generate_world_state(
        self,
        region_count: int = 5,
        faction_count: int = 3,
        complexity_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate a complete initial world state efficiently.
        
        Args:
            region_count: Number of regions to generate
            faction_count: Number of factions to create
            complexity_level: "simple", "medium", or "complex"
            
        Returns:
            Generated world state dictionary
        """
        logger.info(f"Generating world with {region_count} regions and {faction_count} factions")
        
        world_state = {
            "metadata": {
                "version": "1.0.0",
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "generator_seed": self.seed,
                "complexity_level": complexity_level
            },
            "regions": {},
            "factions": {},
            "variables": {},
            "active_effects": []
        }
        
        # Generate regions first
        regions = self._generate_regions(region_count, complexity_level)
        world_state["regions"] = regions
        
        # Generate factions
        factions = self._generate_factions(faction_count, regions, complexity_level)
        world_state["factions"] = factions
        
        # Generate global variables
        variables = self._generate_global_variables(complexity_level)
        world_state["variables"] = variables
        
        # Generate initial active effects
        if complexity_level in ["medium", "complex"]:
            effects = self._generate_initial_effects(regions, factions)
            world_state["active_effects"] = effects
        
        logger.info("World generation completed successfully")
        return world_state
    
    def generate_region_batch(
        self,
        base_names: List[str],
        terrain_types: List[str],
        complexity_level: str = "medium"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate multiple regions efficiently in batch.
        
        Args:
            base_names: List of base names for regions
            terrain_types: Available terrain types
            complexity_level: Generation complexity
            
        Returns:
            Dictionary of region_id -> region_data
        """
        regions = {}
        
        for i, name in enumerate(base_names):
            region_id = f"region_{i+1}"
            region = self._create_region(
                region_id,
                name,
                self.rng.choice(terrain_types),
                complexity_level
            )
            regions[region_id] = region
        
        # Add inter-region relationships for complex worlds
        if complexity_level == "complex":
            self._add_region_relationships(regions)
        
        return regions
    
    def generate_faction_network(
        self,
        faction_count: int,
        regions: Dict[str, Any],
        relationship_density: float = 0.5
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate a network of factions with relationships.
        
        Args:
            faction_count: Number of factions to create
            regions: Available regions for factions
            relationship_density: How connected factions are (0.0 to 1.0)
            
        Returns:
            Dictionary of faction_id -> faction_data
        """
        factions = {}
        faction_names = self._generate_faction_names(faction_count)
        region_ids = list(regions.keys())
        
        # Create individual factions
        for i, name in enumerate(faction_names):
            faction_id = f"faction_{i+1}"
            home_region = self.rng.choice(region_ids) if region_ids else "global"
            
            faction = {
                "id": faction_id,
                "name": name,
                "type": self.rng.choice(["political", "military", "economic", "religious"]),
                "home_region": home_region,
                "power": self.rng.randint(10, 100),
                "influence": self.rng.randint(5, 50),
                "resources": self._generate_faction_resources(),
                "relationships": {},
                "controlled_regions": [home_region] if home_region != "global" else [],
                "reputation": self.rng.randint(-50, 50),
                "activity_level": self.rng.choice(["low", "medium", "high"]),
                "goals": self._generate_faction_goals(),
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "last_activity": datetime.utcnow().isoformat()
                }
            }
            factions[faction_id] = faction
        
        # Generate relationships based on density
        faction_ids = list(factions.keys())
        total_possible_relationships = len(faction_ids) * (len(faction_ids) - 1) // 2
        target_relationships = int(total_possible_relationships * relationship_density)
        
        relationships_created = 0
        attempts = 0
        max_attempts = target_relationships * 3
        
        while relationships_created < target_relationships and attempts < max_attempts:
            faction_a = self.rng.choice(faction_ids)
            faction_b = self.rng.choice(faction_ids)
            
            if (faction_a != faction_b and 
                faction_b not in factions[faction_a]["relationships"]):
                
                relationship_type = self.rng.choice(["allied", "neutral", "hostile", "trading"])
                strength = self.rng.randint(1, 10)
                
                factions[faction_a]["relationships"][faction_b] = {
                    "type": relationship_type,
                    "strength": strength,
                    "established": datetime.utcnow().isoformat()
                }
                
                # Reciprocal relationship (may be different)
                reciprocal_type = self._get_reciprocal_relationship(relationship_type)
                factions[faction_b]["relationships"][faction_a] = {
                    "type": reciprocal_type,
                    "strength": strength + self.rng.randint(-2, 2),
                    "established": datetime.utcnow().isoformat()
                }
                
                relationships_created += 1
            
            attempts += 1
        
        logger.info(f"Generated {len(factions)} factions with {relationships_created} relationships")
        return factions
    
    def optimize_world_complexity(self, world_state: Dict[str, Any], target_complexity: str) -> Dict[str, Any]:
        """
        Optimize an existing world state for the target complexity level.
        
        Args:
            world_state: Current world state
            target_complexity: "simple", "medium", or "complex"
            
        Returns:
            Optimized world state
        """
        optimized_state = world_state.copy()
        current_complexity = world_state.get("metadata", {}).get("complexity_level", "medium")
        
        if current_complexity == target_complexity:
            return optimized_state
        
        logger.info(f"Optimizing world complexity from {current_complexity} to {target_complexity}")
        
        if target_complexity == "simple":
            optimized_state = self._simplify_world_state(optimized_state)
        elif target_complexity == "complex":
            optimized_state = self._complexify_world_state(optimized_state)
        
        optimized_state["metadata"]["complexity_level"] = target_complexity
        optimized_state["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        
        return optimized_state
    
    def _generate_regions(self, count: int, complexity_level: str) -> Dict[str, Dict[str, Any]]:
        """Generate regions based on count and complexity."""
        regions = {}
        terrain_types = ["forest", "grassland", "mountain", "desert", "coastal", "swamp"]
        climates = ["temperate", "tropical", "arctic", "arid", "mediterranean"]
        
        region_names = self._generate_region_names(count)
        
        for i in range(count):
            region_id = f"region_{i+1}"
            name = region_names[i] if i < len(region_names) else f"Region {i+1}"
            
            region = self._create_region(
                region_id,
                name,
                self.rng.choice(terrain_types),
                complexity_level,
                self.rng.choice(climates)
            )
            regions[region_id] = region
        
        return regions
    
    def _create_region(
        self,
        region_id: str,
        name: str,
        terrain_type: str,
        complexity_level: str,
        climate: str = "temperate"
    ) -> Dict[str, Any]:
        """Create a single region with appropriate complexity."""
        region = {
            "id": region_id,
            "name": name,
            "terrain_type": terrain_type,
            "climate": climate,
            "population": self.rng.randint(1000, 100000),
            "prosperity": self.rng.randint(1, 10),
            "stability": self.rng.randint(1, 10),
            "resources": self._generate_region_resources(terrain_type),
            "settlements": self._generate_settlements(complexity_level),
            "controlled_by": None,
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "terrain_features": self._generate_terrain_features(terrain_type),
                "economic_focus": self._determine_economic_focus(terrain_type)
            }
        }
        
        if complexity_level in ["medium", "complex"]:
            region["trade_routes"] = []
            region["natural_resources"] = self._generate_natural_resources(terrain_type)
            region["cultural_traits"] = self._generate_cultural_traits()
        
        if complexity_level == "complex":
            region["political_structure"] = self._generate_political_structure()
            region["military_presence"] = self.rng.randint(0, 100)
            region["unrest_level"] = self.rng.randint(0, 10)
        
        return region
    
    def _generate_factions(
        self,
        count: int,
        regions: Dict[str, Any],
        complexity_level: str
    ) -> Dict[str, Dict[str, Any]]:
        """Generate factions based on regions and complexity."""
        return self.generate_faction_network(count, regions, 
                                           0.3 if complexity_level == "simple" else
                                           0.5 if complexity_level == "medium" else 0.7)
    
    def _generate_global_variables(self, complexity_level: str) -> Dict[str, Any]:
        """Generate global world variables."""
        variables = {
            "world_tension": self.rng.randint(0, 100),
            "global_prosperity": self.rng.randint(0, 100),
            "magic_level": self.rng.randint(0, 100),
            "technology_level": self.rng.randint(1, 10),
            "year": 1,
            "season": self.rng.choice(["spring", "summer", "autumn", "winter"])
        }
        
        if complexity_level in ["medium", "complex"]:
            variables.update({
                "plague_risk": self.rng.randint(0, 50),
                "natural_disaster_chance": self.rng.randint(0, 30),
                "trade_prosperity": self.rng.randint(0, 100),
                "religious_influence": self.rng.randint(0, 100)
            })
        
        if complexity_level == "complex":
            variables.update({
                "political_stability": self.rng.randint(0, 100),
                "cultural_exchange": self.rng.randint(0, 100),
                "exploration_progress": self.rng.randint(0, 100),
                "arcane_events_frequency": self.rng.randint(0, 50)
            })
        
        return variables
    
    def _generate_initial_effects(
        self,
        regions: Dict[str, Any],
        factions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate initial active effects for the world."""
        effects = []
        effect_count = self.rng.randint(0, 3)
        
        for _ in range(effect_count):
            effect_type = self.rng.choice([
                "economic_boom", "trade_disruption", "good_harvest",
                "natural_disaster", "political_unrest", "magical_phenomenon"
            ])
            
            target_region = self.rng.choice(list(regions.keys())) if regions else "global"
            
            effect = {
                "id": f"effect_{len(effects) + 1}",
                "name": effect_type.replace("_", " ").title(),
                "description": f"A {effect_type.replace('_', ' ')} affecting the world.",
                "effect_type": effect_type,
                "target": target_region,
                "magnitude": self.rng.uniform(0.5, 2.0),
                "duration": self.rng.randint(30, 365),  # days
                "started_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "generated": True,
                    "intensity": self.rng.choice(["minor", "moderate", "major"])
                }
            }
            effects.append(effect)
        
        return effects
    
    # Helper methods for generating names and content
    def _generate_region_names(self, count: int) -> List[str]:
        """Generate region names."""
        prefixes = ["North", "South", "East", "West", "Upper", "Lower", "Great", "Old", "New"]
        suffixes = ["lands", "march", "shire", "vale", "moor", "reach", "ford", "burg", "haven"]
        base_names = ["Alder", "Birch", "Cedar", "Drake", "Ember", "Frost", "Grove", "Haven"]
        
        names = []
        for i in range(count):
            if i < len(base_names):
                names.append(base_names[i] + self.rng.choice(suffixes))
            else:
                names.append(self.rng.choice(prefixes) + " " + self.rng.choice(base_names))
        
        return names
    
    def _generate_faction_names(self, count: int) -> List[str]:
        """Generate faction names."""
        descriptors = ["Iron", "Golden", "Silver", "Crimson", "Azure", "Shadow", "Dawn", "Storm"]
        nouns = ["Brotherhood", "Order", "Guild", "Alliance", "Empire", "Republic", "Confederacy", "Dynasty"]
        
        names = []
        for i in range(count):
            if self.rng.random() < 0.7:  # 70% chance for descriptor + noun
                names.append(f"The {self.rng.choice(descriptors)} {self.rng.choice(nouns)}")
            else:  # 30% chance for just noun
                names.append(f"The {self.rng.choice(nouns)} of {self.rng.choice(descriptors)}")
        
        return names
    
    def _generate_region_resources(self, terrain_type: str) -> Dict[str, int]:
        """Generate resources based on terrain type."""
        base_resources = {resource.value: 0 for resource in ResourceType}
        
        terrain_bonuses = {
            "forest": {"wood": 50, "food": 30},
            "grassland": {"food": 60, "population": 40},
            "mountain": {"stone": 70, "iron": 50, "gold": 20},
            "desert": {"magic": 30, "stone": 20},
            "coastal": {"food": 40, "gold": 30},
            "swamp": {"magic": 40, "wood": 20}
        }
        
        bonuses = terrain_bonuses.get(terrain_type, {})
        for resource, bonus in bonuses.items():
            if resource in base_resources:
                base_resources[resource] = self.rng.randint(bonus//2, bonus + 20)
        
        # Add some randomness to other resources
        for resource in base_resources:
            if base_resources[resource] == 0:
                base_resources[resource] = self.rng.randint(0, 20)
        
        return base_resources
    
    def _generate_faction_resources(self) -> Dict[str, int]:
        """Generate faction resources."""
        return {
            "gold": self.rng.randint(1000, 50000),
            "military_units": self.rng.randint(50, 500),
            "influence_points": self.rng.randint(10, 100),
            "territory_size": self.rng.randint(1, 10)
        }
    
    def _generate_settlements(self, complexity_level: str) -> List[Dict[str, Any]]:
        """Generate settlements for a region."""
        if complexity_level == "simple":
            settlement_count = self.rng.randint(1, 2)
        elif complexity_level == "medium":
            settlement_count = self.rng.randint(2, 4)
        else:
            settlement_count = self.rng.randint(3, 6)
        
        settlements = []
        settlement_types = ["village", "town", "city", "fortress", "trading_post"]
        
        for i in range(settlement_count):
            settlement = {
                "name": f"Settlement {i+1}",
                "type": self.rng.choice(settlement_types),
                "population": self.rng.randint(100, 10000),
                "prosperity": self.rng.randint(1, 10)
            }
            settlements.append(settlement)
        
        return settlements
    
    def _generate_terrain_features(self, terrain_type: str) -> List[str]:
        """Generate terrain-specific features."""
        features_by_terrain = {
            "forest": ["ancient_grove", "hidden_clearing", "ranger_outpost"],
            "grassland": ["rolling_hills", "river_crossing", "windmill"],
            "mountain": ["high_peak", "deep_cave", "mountain_pass"],
            "desert": ["oasis", "sand_dunes", "ancient_ruins"],
            "coastal": ["natural_harbor", "lighthouse", "fishing_village"],
            "swamp": ["murky_bog", "abandoned_tower", "crocodile_lair"]
        }
        
        available_features = features_by_terrain.get(terrain_type, ["generic_landmark"])
        feature_count = self.rng.randint(1, 3)
        return self.rng.sample(available_features, min(feature_count, len(available_features)))
    
    def _determine_economic_focus(self, terrain_type: str) -> str:
        """Determine economic focus based on terrain."""
        economic_focuses = {
            "forest": "logging",
            "grassland": "agriculture",
            "mountain": "mining",
            "desert": "trade",
            "coastal": "fishing",
            "swamp": "herbalism"
        }
        return economic_focuses.get(terrain_type, "mixed")
    
    def _generate_natural_resources(self, terrain_type: str) -> List[str]:
        """Generate natural resources for terrain."""
        resources_by_terrain = {
            "forest": ["timber", "herbs", "game"],
            "grassland": ["grain", "livestock", "clay"],
            "mountain": ["ore", "gemstones", "stone"],
            "desert": ["salt", "rare_minerals", "exotic_spices"],
            "coastal": ["fish", "pearls", "seaweed"],
            "swamp": ["peat", "rare_herbs", "alchemical_components"]
        }
        
        return resources_by_terrain.get(terrain_type, ["common_resources"])
    
    def _generate_cultural_traits(self) -> List[str]:
        """Generate cultural traits for a region."""
        traits = [
            "hospitable", "warlike", "scholarly", "mercantile", "religious",
            "artistic", "nomadic", "industrious", "superstitious", "cosmopolitan"
        ]
        trait_count = self.rng.randint(1, 3)
        return self.rng.sample(traits, trait_count)
    
    def _generate_political_structure(self) -> str:
        """Generate political structure for a region."""
        structures = [
            "feudal", "democratic", "autocratic", "theocratic",
            "tribal", "merchant_republic", "military_junta", "anarchic"
        ]
        return self.rng.choice(structures)
    
    def _generate_faction_goals(self) -> List[str]:
        """Generate goals for a faction."""
        goals = [
            "expand_territory", "increase_wealth", "gain_influence",
            "maintain_peace", "promote_trade", "advance_technology",
            "spread_religion", "preserve_tradition", "explore_unknown"
        ]
        goal_count = self.rng.randint(1, 3)
        return self.rng.sample(goals, goal_count)
    
    def _get_reciprocal_relationship(self, relationship_type: str) -> str:
        """Get reciprocal relationship type."""
        reciprocals = {
            "allied": "allied",
            "hostile": "hostile",
            "neutral": "neutral",
            "trading": "trading"
        }
        return reciprocals.get(relationship_type, "neutral")
    
    def _add_region_relationships(self, regions: Dict[str, Any]) -> None:
        """Add relationships between regions for complex worlds."""
        region_ids = list(regions.keys())
        
        for region_id in region_ids:
            # Add neighbor relationships
            neighbors = self.rng.sample(
                [r for r in region_ids if r != region_id],
                min(2, len(region_ids) - 1)
            )
            regions[region_id]["neighboring_regions"] = neighbors
            
            # Add trade relationships
            trade_partners = self.rng.sample(
                [r for r in region_ids if r != region_id],
                min(self.rng.randint(0, 2), len(region_ids) - 1)
            )
            regions[region_id]["trade_partners"] = trade_partners
    
    def _simplify_world_state(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify world state by removing complex elements."""
        simplified = world_state.copy()
        
        # Simplify regions
        for region in simplified.get("regions", {}).values():
            # Remove complex fields
            region.pop("trade_routes", None)
            region.pop("political_structure", None)
            region.pop("military_presence", None)
            region.pop("unrest_level", None)
            region.pop("cultural_traits", None)
            
            # Simplify settlements
            if "settlements" in region and len(region["settlements"]) > 2:
                region["settlements"] = region["settlements"][:2]
        
        # Simplify factions
        for faction in simplified.get("factions", {}).values():
            # Reduce relationships
            if "relationships" in faction and len(faction["relationships"]) > 2:
                items = list(faction["relationships"].items())
                faction["relationships"] = dict(items[:2])
        
        return simplified
    
    def _complexify_world_state(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """Add complexity to world state."""
        complexified = world_state.copy()
        
        # Add complex variables if missing
        variables = complexified.get("variables", {})
        complex_vars = {
            "political_stability": self.rng.randint(0, 100),
            "cultural_exchange": self.rng.randint(0, 100),
            "exploration_progress": self.rng.randint(0, 100)
        }
        variables.update(complex_vars)
        complexified["variables"] = variables
        
        # Add complexity to regions
        for region in complexified.get("regions", {}).values():
            if "political_structure" not in region:
                region["political_structure"] = self._generate_political_structure()
            if "military_presence" not in region:
                region["military_presence"] = self.rng.randint(0, 100)
            if "cultural_traits" not in region:
                region["cultural_traits"] = self._generate_cultural_traits()
        
        return complexified


# Global instance for easy access
world_generator = OptimizedWorldGenerator()
