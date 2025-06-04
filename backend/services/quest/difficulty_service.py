"""
Dynamic Quest Difficulty Service

Implements distance-based difficulty scaling where quest difficulty increases
as the player moves farther from their canonical "home POI" (Point of Interest).
This creates a natural progression system tied to exploration.
"""

import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from .models import QuestDifficulty, QuestTheme, LocationData, PlayerHomeData


class DifficultyZone(Enum):
    """Difficulty zones based on distance from home"""
    SAFE_ZONE = "safe_zone"           # 0-500 units from home
    EXPLORATION_ZONE = "exploration"   # 501-1500 units
    DANGER_ZONE = "danger"            # 1501-3000 units  
    FRONTIER_ZONE = "frontier"        # 3001-5000 units
    FORBIDDEN_ZONE = "forbidden"      # 5000+ units


class DynamicDifficultyService:
    """Service for calculating dynamic quest difficulty based on spatial distance"""
    
    def __init__(self):
        # Distance thresholds for difficulty zones (in game units)
        self.zone_thresholds = {
            DifficultyZone.SAFE_ZONE: (0, 500),
            DifficultyZone.EXPLORATION_ZONE: (501, 1500),
            DifficultyZone.DANGER_ZONE: (1501, 3000),
            DifficultyZone.FRONTIER_ZONE: (3001, 5000),
            DifficultyZone.FORBIDDEN_ZONE: (5001, float('inf'))
        }
        
        # Base difficulty mapping by zone
        self.zone_base_difficulties = {
            DifficultyZone.SAFE_ZONE: QuestDifficulty.EASY,
            DifficultyZone.EXPLORATION_ZONE: QuestDifficulty.MEDIUM,
            DifficultyZone.DANGER_ZONE: QuestDifficulty.HARD,
            DifficultyZone.FRONTIER_ZONE: QuestDifficulty.EPIC,
            DifficultyZone.FORBIDDEN_ZONE: QuestDifficulty.EPIC
        }
        
        # Difficulty progression factors
        self.difficulty_factors = {
            "base_distance_factor": 0.1,      # How much distance alone affects difficulty
            "danger_level_factor": 0.3,       # How much location danger affects difficulty
            "player_level_factor": 0.05,      # How player level affects scaling
            "theme_modifiers": {               # Theme-specific difficulty adjustments
                QuestTheme.COMBAT: 1.2,
                QuestTheme.EXPLORATION: 1.0,
                QuestTheme.SOCIAL: 0.8,
                QuestTheme.MYSTERY: 1.1,
                QuestTheme.CRAFTING: 0.9,
                QuestTheme.TRADE: 0.7,
                QuestTheme.AID: 0.8,
                QuestTheme.KNOWLEDGE: 1.0,
                QuestTheme.GENERAL: 1.0
            }
        }
    
    def calculate_quest_difficulty(self, quest_location: LocationData, 
                                 player_home: PlayerHomeData,
                                 quest_theme: QuestTheme = QuestTheme.GENERAL,
                                 base_level_override: Optional[int] = None) -> Tuple[QuestDifficulty, Dict[str, Any]]:
        """
        Calculate the appropriate difficulty for a quest based on distance from player's home
        
        Args:
            quest_location: Location where the quest takes place
            player_home: Player's home location data
            quest_theme: Theme of the quest (affects difficulty modifiers)
            base_level_override: Override the quest's base level requirement
            
        Returns:
            Tuple of (calculated_difficulty, calculation_details)
        """
        # Calculate distance from home
        distance = self.calculate_distance(
            (player_home.home_x, player_home.home_y, player_home.home_z),
            (quest_location.x, quest_location.y, quest_location.z)
        )
        
        # Determine difficulty zone
        zone = self.get_difficulty_zone(distance)
        
        # Get base difficulty for the zone
        base_difficulty = self.zone_base_difficulties[zone]
        
        # Calculate difficulty score (0.0 to 10.0)
        difficulty_score = self._calculate_difficulty_score(
            distance, quest_location, player_home, quest_theme
        )
        
        # Apply theme modifiers
        theme_modifier = self.difficulty_factors["theme_modifiers"].get(quest_theme, 1.0)
        adjusted_score = difficulty_score * theme_modifier
        
        # Convert score to difficulty enum
        final_difficulty = self._score_to_difficulty(adjusted_score)
        
        # Prepare calculation details
        calculation_details = {
            "distance_from_home": distance,
            "difficulty_zone": zone.value,
            "base_zone_difficulty": base_difficulty.value,
            "raw_difficulty_score": difficulty_score,
            "theme_modifier": theme_modifier,
            "adjusted_score": adjusted_score,
            "final_difficulty": final_difficulty.value,
            "location_danger_level": quest_location.base_danger_level,
            "player_level": player_home.player_level,
            "calculation_factors": {
                "distance_factor": self.difficulty_factors["base_distance_factor"],
                "danger_factor": self.difficulty_factors["danger_level_factor"],
                "player_factor": self.difficulty_factors["player_level_factor"]
            }
        }
        
        return final_difficulty, calculation_details
    
    def get_recommended_level_for_location(self, quest_location: LocationData,
                                         player_home: PlayerHomeData,
                                         base_level: int = 1) -> int:
        """
        Get recommended player level for a quest at a specific location
        
        Args:
            quest_location: Location of the quest
            player_home: Player's home location
            base_level: Base level requirement for the quest type
            
        Returns:
            Recommended player level
        """
        distance = self.calculate_distance(
            (player_home.home_x, player_home.home_y, player_home.home_z),
            (quest_location.x, quest_location.y, quest_location.z)
        )
        
        zone = self.get_difficulty_zone(distance)
        
        # Base level recommendations by zone
        zone_level_recommendations = {
            DifficultyZone.SAFE_ZONE: base_level,
            DifficultyZone.EXPLORATION_ZONE: base_level + 5,
            DifficultyZone.DANGER_ZONE: base_level + 15,
            DifficultyZone.FRONTIER_ZONE: base_level + 30,
            DifficultyZone.FORBIDDEN_ZONE: base_level + 50
        }
        
        recommended_level = zone_level_recommendations.get(zone, base_level)
        
        # Apply location danger modifier
        danger_modifier = quest_location.base_danger_level / 5.0  # Normalize to 0-2 range
        recommended_level = int(recommended_level * (1 + danger_modifier * 0.2))
        
        return max(1, recommended_level)  # Ensure minimum level of 1
    
    def get_difficulty_zone(self, distance_from_home: float) -> DifficultyZone:
        """
        Determine which difficulty zone a distance falls into
        
        Args:
            distance_from_home: Distance in game units from player's home
            
        Returns:
            Difficulty zone enum
        """
        for zone, (min_dist, max_dist) in self.zone_thresholds.items():
            if min_dist <= distance_from_home <= max_dist:
                return zone
        
        # Default to forbidden zone for extreme distances
        return DifficultyZone.FORBIDDEN_ZONE
    
    def calculate_distance(self, home_coords: Tuple[float, float, float],
                          quest_coords: Tuple[float, float, float]) -> float:
        """
        Calculate 3D Euclidean distance between two points
        
        Args:
            home_coords: (x, y, z) coordinates of home location
            quest_coords: (x, y, z) coordinates of quest location
            
        Returns:
            Distance in game units
        """
        dx = quest_coords[0] - home_coords[0]
        dy = quest_coords[1] - home_coords[1] 
        dz = quest_coords[2] - home_coords[2]
        
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def get_zone_boundaries(self, player_home: PlayerHomeData) -> Dict[str, Dict[str, float]]:
        """
        Get the coordinate boundaries for each difficulty zone around player's home
        
        Args:
            player_home: Player's home location data
            
        Returns:
            Dictionary mapping zone names to boundary coordinates
        """
        boundaries = {}
        
        for zone, (min_dist, max_dist) in self.zone_thresholds.items():
            # Calculate rough circular boundaries (simplified)
            boundaries[zone.value] = {
                "center_x": player_home.home_x,
                "center_y": player_home.home_y,
                "center_z": player_home.home_z,
                "inner_radius": min_dist,
                "outer_radius": max_dist if max_dist != float('inf') else 10000,
                "recommended_min_level": self.get_recommended_level_for_location(
                    LocationData("temp", "temp", 
                               player_home.home_x + min_dist, 
                               player_home.home_y, 
                               player_home.home_z),
                    player_home
                )
            }
        
        return boundaries
    
    def find_appropriate_quest_locations(self, player_home: PlayerHomeData,
                                       target_difficulty: QuestDifficulty,
                                       available_locations: List[LocationData],
                                       tolerance: int = 1) -> List[LocationData]:
        """
        Find locations that would generate quests of the target difficulty
        
        Args:
            player_home: Player's home location data
            target_difficulty: Desired quest difficulty
            available_locations: List of possible quest locations
            tolerance: How many difficulty levels to accept (0 = exact match)
            
        Returns:
            List of suitable locations
        """
        suitable_locations = []
        target_score = self._difficulty_to_score(target_difficulty)
        
        for location in available_locations:
            difficulty, details = self.calculate_quest_difficulty(
                location, player_home, QuestTheme.GENERAL
            )
            
            location_score = self._difficulty_to_score(difficulty)
            
            # Check if within tolerance
            if abs(location_score - target_score) <= tolerance:
                suitable_locations.append(location)
        
        return suitable_locations
    
    def _calculate_difficulty_score(self, distance: float, 
                                  quest_location: LocationData,
                                  player_home: PlayerHomeData,
                                  quest_theme: QuestTheme) -> float:
        """
        Calculate raw difficulty score (0.0 to 10.0) based on all factors
        
        Returns:
            Difficulty score where:
            0-2: Easy, 2-4: Medium, 4-7: Hard, 7-10: Epic
        """
        # Base score from distance
        distance_factor = self.difficulty_factors["base_distance_factor"]
        distance_score = min(distance * distance_factor / 1000, 6.0)  # Cap at 6.0
        
        # Location danger contribution
        danger_factor = self.difficulty_factors["danger_level_factor"]
        danger_score = quest_location.base_danger_level * danger_factor
        
        # Player level adjustment (higher level players face relatively easier content)
        player_factor = self.difficulty_factors["player_level_factor"]
        player_adjustment = max(0, (player_home.player_level - 1) * player_factor)
        
        # Exploration bonus (experienced explorers handle distance better)
        exploration_adjustment = (player_home.exploration_bonus - 1.0) * 0.5
        
        # Combine all factors
        total_score = distance_score + danger_score - player_adjustment - exploration_adjustment
        
        # Apply zone-specific modifiers
        zone = self.get_difficulty_zone(distance)
        zone_modifiers = quest_location.zone_modifiers or {}
        zone_modifier = zone_modifiers.get(zone.value, 1.0)
        
        final_score = max(0.0, min(10.0, total_score * zone_modifier))
        
        return final_score
    
    def _score_to_difficulty(self, score: float) -> QuestDifficulty:
        """Convert difficulty score to difficulty enum"""
        if score < 2.0:
            return QuestDifficulty.EASY
        elif score < 4.0:
            return QuestDifficulty.MEDIUM
        elif score < 7.0:
            return QuestDifficulty.HARD
        else:
            return QuestDifficulty.EPIC
    
    def _difficulty_to_score(self, difficulty: QuestDifficulty) -> float:
        """Convert difficulty enum to approximate score for comparison"""
        score_map = {
            QuestDifficulty.EASY: 1.0,
            QuestDifficulty.MEDIUM: 3.0,
            QuestDifficulty.HARD: 5.5,
            QuestDifficulty.EPIC: 8.5
        }
        return score_map.get(difficulty, 3.0)
    
    def get_progression_recommendations(self, player_home: PlayerHomeData,
                                     current_player_level: int) -> Dict[str, Any]:
        """
        Get recommendations for quest progression based on player's current level and location
        
        Args:
            player_home: Player's home location data
            current_player_level: Player's current level
            
        Returns:
            Dictionary with progression recommendations
        """
        recommendations = {
            "current_level": current_player_level,
            "safe_exploration_radius": 0,
            "recommended_exploration_radius": 0,
            "challenge_exploration_radius": 0,
            "zone_recommendations": {},
            "next_progression_targets": []
        }
        
        # Calculate recommended exploration distances based on level
        level_factor = current_player_level / 10.0  # Scale by 10-level chunks
        
        recommendations["safe_exploration_radius"] = min(300 + (level_factor * 200), 500)
        recommendations["recommended_exploration_radius"] = min(800 + (level_factor * 700), 1500)
        recommendations["challenge_exploration_radius"] = min(2000 + (level_factor * 1000), 3000)
        
        # Zone-specific recommendations
        for zone in DifficultyZone:
            zone_info = {
                "zone_name": zone.value,
                "distance_range": self.zone_thresholds[zone],
                "recommended_level": self.get_recommended_level_for_location(
                    LocationData("temp", "temp", 
                               player_home.home_x + self.zone_thresholds[zone][0], 
                               player_home.home_y, 
                               player_home.home_z),
                    player_home
                ),
                "suitable_for_player": False
            }
            
            # Check if zone is suitable for player's current level
            zone_rec_level = zone_info["recommended_level"]
            if zone_rec_level <= current_player_level + 5:  # Allow 5 level buffer
                zone_info["suitable_for_player"] = True
            
            recommendations["zone_recommendations"][zone.value] = zone_info
        
        # Generate progression targets
        progression_targets = []
        for target_level in [current_player_level + 5, current_player_level + 10, current_player_level + 20]:
            target_distance = min(500 + (target_level * 100), 5000)
            progression_targets.append({
                "target_level": target_level,
                "exploration_distance": target_distance,
                "recommended_zone": self.get_difficulty_zone(target_distance).value
            })
        
        recommendations["next_progression_targets"] = progression_targets
        
        return recommendations 