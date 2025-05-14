#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFilter
import os
import random
import colorsys
import math

# Constants from asset inventory
SPRITE_SIZE = 64
OVERLAY_COLORS = {
    'elevation': {
        'base': '#000000',  # Black with 20% opacity
        'alpha': 51,  # 20% of 255
    },
    'highlight': {
        'base': '#FFFFFF',  # White with 40% opacity
        'alpha': 102,  # 40% of 255
    },
    'path': {
        'base': '#FFD700',  # Yellow with 60% opacity
        'alpha': 153,  # 60% of 255
    }
}

def hex_to_rgba(hex_color, alpha):
    """Convert hex color to RGBA tuple."""
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return rgb + (alpha,)

def create_elevation_overlay(variation_num):
    """Create an elevation overlay with varying height indicators."""
    img = Image.new('RGBA', (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create contour-like patterns
    color = hex_to_rgba(OVERLAY_COLORS['elevation']['base'], OVERLAY_COLORS['elevation']['alpha'])
    
    # Generate different contour patterns based on variation
    num_lines = 3 + variation_num
    for i in range(num_lines):
        y_offset = SPRITE_SIZE * (i + 1) / (num_lines + 1)
        points = []
        for x in range(0, SPRITE_SIZE + 1, 4):
            y = y_offset + math.sin(x * 0.1 + variation_num) * 5
            points.append((x, y))
        
        if points:
            draw.line(points, fill=color, width=2)
    
    return img

def create_highlight_overlay(variation_num):
    """Create a highlight overlay with different patterns."""
    img = Image.new('RGBA', (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    color = hex_to_rgba(OVERLAY_COLORS['highlight']['base'], OVERLAY_COLORS['highlight']['alpha'])
    
    if variation_num == 0:
        # Simple border highlight
        draw.rectangle([2, 2, SPRITE_SIZE-3, SPRITE_SIZE-3], outline=color, width=2)
    elif variation_num == 1:
        # Corner highlights
        for corner in [(0, 0), (0, SPRITE_SIZE), (SPRITE_SIZE, 0), (SPRITE_SIZE, SPRITE_SIZE)]:
            draw.arc([corner[0]-20, corner[1]-20, corner[0]+20, corner[1]+20], 0, 90, fill=color, width=2)
    elif variation_num == 2:
        # Center glow
        for radius in range(5, 30, 5):
            alpha = int(OVERLAY_COLORS['highlight']['alpha'] * (30 - radius) / 30)
            draw.ellipse([SPRITE_SIZE//2 - radius, SPRITE_SIZE//2 - radius,
                         SPRITE_SIZE//2 + radius, SPRITE_SIZE//2 + radius],
                        outline=color[:3] + (alpha,), width=2)
    else:
        # Diagonal stripes
        for i in range(-SPRITE_SIZE, SPRITE_SIZE, 10):
            draw.line([i, 0, i + SPRITE_SIZE, SPRITE_SIZE], fill=color, width=2)
    
    return img

def create_path_overlay(variation_num):
    """Create a path overlay with different patterns."""
    img = Image.new('RGBA', (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    color = hex_to_rgba(OVERLAY_COLORS['path']['base'], OVERLAY_COLORS['path']['alpha'])
    
    if variation_num == 0:
        # Straight path
        draw.rectangle([SPRITE_SIZE//4, 0, 3*SPRITE_SIZE//4, SPRITE_SIZE], fill=color)
    elif variation_num == 1:
        # Curved path
        points = []
        for y in range(0, SPRITE_SIZE + 1, 4):
            x = SPRITE_SIZE//2 + math.sin(y * 0.1) * 15
            points.append((x, y))
        if points:
            for i in range(len(points) - 1):
                draw.line([points[i], points[i+1]], fill=color, width=SPRITE_SIZE//4)
    elif variation_num == 2:
        # Dotted path
        for y in range(0, SPRITE_SIZE, 10):
            draw.ellipse([SPRITE_SIZE//2 - 5, y - 5, SPRITE_SIZE//2 + 5, y + 5], fill=color)
    else:
        # Diagonal path
        draw.rectangle([0, 0, SPRITE_SIZE, SPRITE_SIZE], fill=color)
        img = img.rotate(45, expand=True)
        img = img.resize((SPRITE_SIZE, SPRITE_SIZE))
    
    return img

def save_overlay(img, overlay_type, variation_num):
    """Save the overlay sprite."""
    os.makedirs('assets/terrain/overlay', exist_ok=True)
    output_path = f'assets/terrain/overlay/overlay_{overlay_type}_{variation_num:02d}.png'
    img.save(output_path, 'PNG')
    print(f"Generated {output_path}")

def main():
    """Generate all terrain overlay sprites."""
    print("Generating terrain overlay sprites...")
    
    # Generate elevation overlays
    for i in range(4):
        overlay = create_elevation_overlay(i)
        save_overlay(overlay, 'elevation', i)
    
    # Generate highlight overlays
    for i in range(4):
        overlay = create_highlight_overlay(i)
        save_overlay(overlay, 'highlight', i)
    
    # Generate path overlays
    for i in range(4):
        overlay = create_path_overlay(i)
        save_overlay(overlay, 'path', i)
    
    print("Done!")

if __name__ == '__main__':
    main() 