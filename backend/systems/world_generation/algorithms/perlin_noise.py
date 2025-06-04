"""
Perlin Noise Generator

Provides terrain generation algorithms for creating realistic elevation maps
and other geographic features using Perlin noise.
"""

import math
import random
from typing import Dict, List
from backend.systems.region.models import HexCoordinate


class PerlinNoiseGenerator:
    """Generates Perlin noise for terrain elevation and other geographic features."""
    
    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(0, 1000000)
        random.seed(self.seed)
        
        # Initialize permutation table for Perlin noise
        self.permutation = list(range(256))
        random.shuffle(self.permutation)
        self.permutation = self.permutation * 2  # Duplicate for easy wrapping
    
    def generate_elevation_map(self, hex_grid: List[HexCoordinate]) -> Dict[HexCoordinate, float]:
        """Generate elevation values for each hex coordinate using Perlin noise."""
        elevation_map = {}
        
        # Parameters for terrain generation
        scale = 0.05  # Controls feature size (smaller = larger features)
        octaves = 4   # Number of noise layers
        persistence = 0.5  # How much each octave contributes
        lacunarity = 2.0   # Frequency multiplier between octaves
        
        for coord in hex_grid:
            # Convert hex coordinates to cartesian for noise sampling
            x, y = self._hex_to_cartesian(coord)
            
            # Generate multi-octave Perlin noise
            elevation = 0.0
            frequency = scale
            amplitude = 1.0
            max_value = 0.0
            
            for _ in range(octaves):
                elevation += self._perlin_noise(x * frequency, y * frequency) * amplitude
                max_value += amplitude
                amplitude *= persistence
                frequency *= lacunarity
            
            # Normalize to 0-1 range
            normalized_elevation = (elevation / max_value + 1) / 2
            elevation_map[coord] = max(0.0, min(1.0, normalized_elevation))
        
        return elevation_map
    
    def _hex_to_cartesian(self, coord: HexCoordinate) -> tuple:
        """Convert hex coordinates to cartesian coordinates for noise sampling."""
        x = coord.q * 1.5
        y = coord.r * math.sqrt(3) + coord.q * math.sqrt(3) / 2
        return x, y
    
    def _perlin_noise(self, x: float, y: float) -> float:
        """Generate 2D Perlin noise at given coordinates."""
        # Floor coordinates to get integer grid
        xi = int(math.floor(x)) & 255
        yi = int(math.floor(y)) & 255
        
        # Fractional parts
        xf = x - math.floor(x)
        yf = y - math.floor(y)
        
        # Ease curves for smooth interpolation
        u = self._fade(xf)
        v = self._fade(yf)
        
        # Hash coordinates of the 4 cube corners
        aa = self.permutation[self.permutation[xi] + yi]
        ab = self.permutation[self.permutation[xi] + yi + 1]
        ba = self.permutation[self.permutation[xi + 1] + yi]
        bb = self.permutation[self.permutation[xi + 1] + yi + 1]
        
        # Calculate gradient contributions
        x1 = self._lerp(self._grad(aa, xf, yf), self._grad(ba, xf - 1, yf), u)
        x2 = self._lerp(self._grad(ab, xf, yf - 1), self._grad(bb, xf - 1, yf - 1), u)
        
        # Interpolate between the two results
        return self._lerp(x1, x2, v)
    
    def _fade(self, t: float) -> float:
        """Fade function for smooth interpolation."""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def _lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation between a and b by factor t."""
        return a + t * (b - a)
    
    def _grad(self, hash_val: int, x: float, y: float) -> float:
        """Calculate gradient vector dot product."""
        h = hash_val & 3
        u = x if h < 2 else y
        v = y if h < 2 else x
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)
    
    def generate_temperature_noise(self, hex_grid: List[HexCoordinate]) -> Dict[HexCoordinate, float]:
        """Generate temperature variation using a different noise pattern."""
        temp_map = {}
        scale = 0.02  # Larger scale features for climate
        
        for coord in hex_grid:
            x, y = self._hex_to_cartesian(coord)
            
            # Base temperature from latitude (distance from center)
            center_distance = math.sqrt(x*x + y*y)
            latitude_temp = 1.0 - (center_distance * 0.1)  # Cooler toward edges
            
            # Add noise variation
            noise = self._perlin_noise(x * scale, y * scale)
            temp_variation = noise * 0.3  # 30% variation from noise
            
            final_temp = latitude_temp + temp_variation
            temp_map[coord] = max(0.0, min(1.0, final_temp))
        
        return temp_map
    
    def generate_humidity_noise(self, hex_grid: List[HexCoordinate], elevation_map: Dict[HexCoordinate, float]) -> Dict[HexCoordinate, float]:
        """Generate humidity patterns influenced by elevation and distance from edges."""
        humidity_map = {}
        scale = 0.03
        
        for coord in hex_grid:
            x, y = self._hex_to_cartesian(coord)
            elevation = elevation_map.get(coord, 0.5)
            
            # Base humidity - higher at edges (coastal), lower inland
            center_distance = math.sqrt(x*x + y*y)
            base_humidity = 0.8 - (center_distance * 0.05)
            
            # Elevation effect - lower elevation = more humid
            elevation_effect = (1.0 - elevation) * 0.3
            
            # Noise variation
            noise = self._perlin_noise(x * scale, y * scale)
            humidity_variation = noise * 0.2
            
            final_humidity = base_humidity + elevation_effect + humidity_variation
            humidity_map[coord] = max(0.0, min(1.0, final_humidity))
        
        return humidity_map 