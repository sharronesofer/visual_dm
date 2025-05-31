"""
Noise Generation Utilities

Provides various noise generation algorithms for procedural content generation.
"""

import math
import random
from typing import List, Tuple


class PerlinNoise:
    """Perlin noise generator for procedural content"""
    
    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(0, 1000000)
        random.seed(self.seed)
        
        # Generate permutation table
        self.permutation = list(range(256))
        random.shuffle(self.permutation)
        self.permutation *= 2  # Duplicate for easier indexing
        
        # Gradient vectors for 2D
        self.gradients_2d = [
            (1, 1), (-1, 1), (1, -1), (-1, -1),
            (1, 0), (-1, 0), (0, 1), (0, -1)
        ]
    
    def noise(self, x: float, y: float, z: float = 0.0) -> float:
        """Generate 2D or 3D Perlin noise value between -1 and 1"""
        if z == 0.0:
            return self._noise_2d(x, y)
        else:
            return self._noise_3d(x, y, z)
    
    def _noise_2d(self, x: float, y: float) -> float:
        """Generate 2D Perlin noise"""
        # Grid coordinates
        x0 = int(math.floor(x)) & 255
        y0 = int(math.floor(y)) & 255
        x1 = (x0 + 1) & 255
        y1 = (y0 + 1) & 255
        
        # Relative coordinates within grid cell
        dx = x - math.floor(x)
        dy = y - math.floor(y)
        
        # Fade curves
        u = self._fade(dx)
        v = self._fade(dy)
        
        # Hash coordinates of grid corners
        aa = self.permutation[self.permutation[x0] + y0]
        ab = self.permutation[self.permutation[x0] + y1]
        ba = self.permutation[self.permutation[x1] + y0]
        bb = self.permutation[self.permutation[x1] + y1]
        
        # Gradient dot products
        grad_aa = self._grad_2d(aa, dx, dy)
        grad_ba = self._grad_2d(ba, dx - 1, dy)
        grad_ab = self._grad_2d(ab, dx, dy - 1)
        grad_bb = self._grad_2d(bb, dx - 1, dy - 1)
        
        # Interpolate
        x1_interp = self._lerp(u, grad_aa, grad_ba)
        x2_interp = self._lerp(u, grad_ab, grad_bb)
        
        return self._lerp(v, x1_interp, x2_interp)
    
    def _noise_3d(self, x: float, y: float, z: float) -> float:
        """Generate 3D Perlin noise (simplified implementation)"""
        # For simplicity, combine multiple 2D noise calls
        noise1 = self._noise_2d(x, y)
        noise2 = self._noise_2d(y, z)
        noise3 = self._noise_2d(x, z)
        
        return (noise1 + noise2 + noise3) / 3.0
    
    def _fade(self, t: float) -> float:
        """Fade function: 6t^5 - 15t^4 + 10t^3"""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def _lerp(self, t: float, a: float, b: float) -> float:
        """Linear interpolation"""
        return a + t * (b - a)
    
    def _grad_2d(self, hash_val: int, x: float, y: float) -> float:
        """Calculate gradient dot product for 2D"""
        gradient = self.gradients_2d[hash_val & 7]
        return gradient[0] * x + gradient[1] * y
    
    def octave_noise(self, x: float, y: float, octaves: int = 4, 
                    persistence: float = 0.5, scale: float = 1.0) -> float:
        """Generate octave noise (fractal noise)"""
        value = 0.0
        amplitude = 1.0
        frequency = scale
        max_value = 0.0
        
        for _ in range(octaves):
            value += self.noise(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2.0
        
        return value / max_value
    
    def ridged_noise(self, x: float, y: float, octaves: int = 4,
                    persistence: float = 0.5, scale: float = 1.0) -> float:
        """Generate ridged noise for mountain-like features"""
        value = 0.0
        amplitude = 1.0
        frequency = scale
        max_value = 0.0
        
        for _ in range(octaves):
            noise_val = abs(self.noise(x * frequency, y * frequency))
            noise_val = 1.0 - noise_val  # Invert for ridges
            noise_val = noise_val * noise_val  # Square for sharper ridges
            
            value += noise_val * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2.0
        
        return value / max_value


class SimplexNoise:
    """Simplified Simplex noise implementation"""
    
    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(0, 1000000)
        random.seed(self.seed)
        
        # Simplex noise is more complex to implement properly
        # This is a simplified version using Perlin noise as base
        self.perlin = PerlinNoise(seed)
    
    def noise(self, x: float, y: float) -> float:
        """Generate simplex noise (using Perlin as approximation)"""
        # Skew input space
        s = (x + y) * 0.5 * (math.sqrt(3.0) - 1.0)
        i = math.floor(x + s)
        j = math.floor(y + s)
        
        # Unskew back to (x,y) space
        t = (i + j) * (3.0 - math.sqrt(3.0)) / 6.0
        x0 = x - (i - t)
        y0 = y - (j - t)
        
        # Use Perlin noise as approximation
        return self.perlin.noise(x0, y0)


class WhiteNoise:
    """White noise generator"""
    
    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(0, 1000000)
        random.seed(self.seed)
    
    def noise(self, x: float, y: float) -> float:
        """Generate white noise"""
        # Use coordinates as seed for deterministic noise
        local_seed = int((x * 12.9898 + y * 78.233) * 43758.5453) % 1000000
        random.seed(local_seed)
        return random.uniform(-1.0, 1.0)


def generate_height_map(width: int, height: int, scale: float = 0.1, 
                       octaves: int = 4, persistence: float = 0.5,
                       seed: int = None) -> List[List[float]]:
    """Generate a 2D height map using Perlin noise"""
    noise_gen = PerlinNoise(seed)
    height_map = []
    
    for y in range(height):
        row = []
        for x in range(width):
            noise_val = noise_gen.octave_noise(
                x * scale, y * scale, 
                octaves=octaves, 
                persistence=persistence
            )
            # Normalize to 0-1 range
            height_val = (noise_val + 1.0) / 2.0
            row.append(height_val)
        height_map.append(row)
    
    return height_map


def generate_temperature_map(width: int, height: int, 
                           latitude_effect: float = 0.8,
                           noise_scale: float = 0.05,
                           seed: int = None) -> List[List[float]]:
    """Generate temperature map with latitude effects"""
    noise_gen = PerlinNoise(seed)
    temp_map = []
    
    for y in range(height):
        row = []
        for x in range(width):
            # Latitude effect (colder at poles)
            lat_factor = 1.0 - abs(y - height/2) / (height/2)
            lat_temp = lat_factor * latitude_effect
            
            # Add noise variation
            noise_temp = noise_gen.noise(x * noise_scale, y * noise_scale) * (1.0 - latitude_effect)
            
            # Combine and normalize
            temperature = lat_temp + noise_temp
            temperature = max(0.0, min(1.0, temperature))
            row.append(temperature)
        temp_map.append(row)
    
    return temp_map


def generate_moisture_map(width: int, height: int,
                         coastal_effect: float = 0.6,
                         noise_scale: float = 0.08,
                         seed: int = None) -> List[List[float]]:
    """Generate moisture/humidity map"""
    noise_gen = PerlinNoise(seed)
    moisture_map = []
    
    for y in range(height):
        row = []
        for x in range(width):
            # Distance from edges (simulating coastal moisture)
            edge_dist = min(x, width - x, y, height - y)
            max_edge_dist = min(width, height) / 2
            coastal_factor = (max_edge_dist - edge_dist) / max_edge_dist
            coastal_moisture = coastal_factor * coastal_effect
            
            # Add noise variation
            noise_moisture = noise_gen.octave_noise(
                x * noise_scale, y * noise_scale,
                octaves=3, persistence=0.6
            ) * (1.0 - coastal_effect)
            
            # Combine and normalize
            moisture = coastal_moisture + noise_moisture
            moisture = max(0.0, min(1.0, (moisture + 1.0) / 2.0))
            row.append(moisture)
        moisture_map.append(row)
    
    return moisture_map 