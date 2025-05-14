#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import os
import random
import colorsys
import math

# Constants from asset inventory
SPRITE_SIZE = 64
BASE_COLORS = {
    'grass': '#2E7D32',  # Green
    'water': '#1976D2',  # Blue
    'forest': '#33691E',  # Dark Green
    'desert': '#FDD835',  # Yellow
    'snow': '#FAFAFA',   # White
    'mountain': '#795548' # Brown
}

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_noise_texture(base_color, variation=0.1, pattern_scale=1.0):
    """Create a noise texture with the given base color and pattern scale."""
    img = Image.new('RGB', (SPRITE_SIZE, SPRITE_SIZE))
    pixels = []
    base_rgb = hex_to_rgb(base_color)
    
    # Convert RGB to HSV for better color variation
    base_hsv = colorsys.rgb_to_hsv(base_rgb[0]/255, base_rgb[1]/255, base_rgb[2]/255)
    
    for y in range(SPRITE_SIZE):
        for x in range(SPRITE_SIZE):
            # Create a more complex noise pattern
            noise = math.sin(x * pattern_scale) * math.cos(y * pattern_scale)
            noise = (noise + 1) / 2  # Normalize to 0-1
            
            # Add random variation
            value_variation = random.uniform(-variation, variation) + noise * variation
            new_value = max(0, min(1, base_hsv[2] + value_variation))
            
            # Convert back to RGB
            new_rgb = colorsys.hsv_to_rgb(base_hsv[0], base_hsv[1], new_value)
            pixels.extend([int(c * 255) for c in new_rgb])
    
    img.frombytes(bytes(pixels))
    return img

def add_terrain_details(img, terrain_type, variation_num):
    """Add terrain-specific details based on the terrain type and variation number."""
    draw = ImageDraw.Draw(img)
    
    if terrain_type == 'water':
        # Different wave patterns for each variation
        wave_height = 4 + variation_num * 2
        wave_spacing = 8 + variation_num * 4
        for y in range(0, SPRITE_SIZE, wave_spacing):
            for x in range(0, SPRITE_SIZE, 16):
                offset = (y // wave_spacing) % 2 * wave_height
                draw.line([(x + offset, y), (x + offset + wave_height, y)],
                         fill=hex_to_rgb(BASE_COLORS['water']), width=2)
    
    elif terrain_type == 'mountain':
        # Different mountain shapes for each variation
        peak_offset = variation_num * 5
        points = [
            (SPRITE_SIZE//2 + peak_offset, 10 + variation_num * 2),
            (10, SPRITE_SIZE-10),
            (SPRITE_SIZE-10, SPRITE_SIZE-10)
        ]
        draw.polygon(points, fill=hex_to_rgb(BASE_COLORS['mountain']))
    
    elif terrain_type == 'forest':
        # Add tree-like patterns
        num_trees = 3 + variation_num
        for _ in range(num_trees):
            x = random.randint(10, SPRITE_SIZE-10)
            y = random.randint(10, SPRITE_SIZE-10)
            size = random.randint(8, 12)
            draw.ellipse([x-size, y-size, x+size, y+size],
                        fill=hex_to_rgb(BASE_COLORS['forest']))
    
    return img

def create_terrain_sprite(terrain_type, variation_num):
    """Create a terrain sprite of the specified type and variation."""
    base_color = BASE_COLORS[terrain_type]
    
    # Vary the pattern scale and noise variation for different variations
    pattern_scale = 0.1 + variation_num * 0.05
    variation = 0.1 + variation_num * 0.02
    
    # Create base texture with noise
    img = create_noise_texture(base_color, variation, pattern_scale)
    
    # Add terrain-specific details
    img = add_terrain_details(img, terrain_type, variation_num)
    
    # Apply some post-processing
    if variation_num > 0:
        # Vary brightness and contrast slightly
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.9 + variation_num * 0.1)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(0.9 + variation_num * 0.1)
    
    # Add subtle blur for some variations
    if variation_num % 2 == 1:
        img = img.filter(ImageFilter.GaussianBlur(0.5))
    
    # Save the sprite
    os.makedirs('assets/terrain/base', exist_ok=True)
    output_path = f'assets/terrain/base/terrain_{terrain_type}_{variation_num:02d}.png'
    img.save(output_path)
    print(f"Generated {output_path}")

def main():
    """Generate all terrain sprites with variations."""
    print("Generating terrain sprites with variations...")
    for terrain_type in BASE_COLORS.keys():
        # Generate 4 variations of each terrain type
        for variation in range(4):
            create_terrain_sprite(terrain_type, variation)
    print("Done!")

if __name__ == '__main__':
    main() 