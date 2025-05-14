#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFilter
import os
import random
import colorsys
import math

# Constants from asset inventory
SPRITE_SIZE = 64
FEATURE_COLORS = {
    'tree': {
        'trunk': '#5D4037',  # Brown
        'leaves': '#2E7D32',  # Green
    },
    'rock': {
        'base': '#607D8B',  # Gray
        'highlight': '#90A4AE',  # Light gray
    },
    'bush': {
        'base': '#388E3C',  # Dark green
        'highlight': '#4CAF50',  # Light green
    },
    'flower': {
        'stem': '#33691E',  # Dark green
        'petals': ['#F44336', '#E91E63', '#9C27B0', '#FFEB3B']  # Various colors
    }
}

def create_tree_feature(variation_num):
    """Create a tree feature with different styles."""
    img = Image.new('RGBA', (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if variation_num == 0:
        # Pine tree
        # Trunk
        draw.rectangle([SPRITE_SIZE//2 - 3, SPRITE_SIZE//2, 
                       SPRITE_SIZE//2 + 3, SPRITE_SIZE - 10],
                      fill=FEATURE_COLORS['tree']['trunk'])
        # Triangular leaves
        draw.polygon([(SPRITE_SIZE//2, 10),
                     (SPRITE_SIZE//4, SPRITE_SIZE//2 + 10),
                     (3*SPRITE_SIZE//4, SPRITE_SIZE//2 + 10)],
                    fill=FEATURE_COLORS['tree']['leaves'])
    
    elif variation_num == 1:
        # Oak tree
        # Trunk
        draw.rectangle([SPRITE_SIZE//2 - 4, SPRITE_SIZE//3,
                       SPRITE_SIZE//2 + 4, SPRITE_SIZE - 10],
                      fill=FEATURE_COLORS['tree']['trunk'])
        # Round leaves
        for _ in range(15):
            x = SPRITE_SIZE//2 + random.randint(-15, 15)
            y = SPRITE_SIZE//3 + random.randint(-15, 15)
            size = random.randint(5, 10)
            draw.ellipse([x-size, y-size, x+size, y+size],
                        fill=FEATURE_COLORS['tree']['leaves'])
    
    elif variation_num == 2:
        # Willow tree
        # Trunk
        draw.rectangle([SPRITE_SIZE//2 - 3, 10,
                       SPRITE_SIZE//2 + 3, SPRITE_SIZE//2],
                      fill=FEATURE_COLORS['tree']['trunk'])
        # Drooping branches
        for i in range(8):
            start_x = SPRITE_SIZE//2
            start_y = random.randint(15, SPRITE_SIZE//2)
            end_x = SPRITE_SIZE//2 + random.choice([-1, 1]) * random.randint(10, 20)
            end_y = start_y + random.randint(10, 20)
            points = [(start_x, start_y)]
            
            # Create curved branch
            for t in range(1, 10):
                t = t / 10
                x = start_x + (end_x - start_x) * t
                y = start_y + (end_y - start_y) * t + 10 * math.sin(t * math.pi)
                points.append((x, y))
            
            if len(points) > 1:
                for i in range(len(points) - 1):
                    draw.line([points[i], points[i+1]],
                            fill=FEATURE_COLORS['tree']['leaves'], width=2)
    
    else:
        # Dead tree
        # Main trunk
        draw.line([SPRITE_SIZE//2, SPRITE_SIZE - 10,
                  SPRITE_SIZE//2, SPRITE_SIZE//4],
                 fill=FEATURE_COLORS['tree']['trunk'], width=4)
        # Branches
        for _ in range(5):
            start_y = random.randint(SPRITE_SIZE//4, 3*SPRITE_SIZE//4)
            length = random.randint(10, 20)
            angle = random.uniform(-math.pi/3, math.pi/3)
            end_x = SPRITE_SIZE//2 + length * math.cos(angle)
            end_y = start_y - length * math.sin(angle)
            draw.line([SPRITE_SIZE//2, start_y, end_x, end_y],
                     fill=FEATURE_COLORS['tree']['trunk'], width=2)
    
    return img

def create_rock_feature(variation_num):
    """Create a rock feature with different styles."""
    img = Image.new('RGBA', (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if variation_num == 0:
        # Single large boulder
        points = [(SPRITE_SIZE//4, SPRITE_SIZE - 10),
                 (SPRITE_SIZE//2, SPRITE_SIZE//2),
                 (3*SPRITE_SIZE//4, SPRITE_SIZE - 10)]
        draw.polygon(points, fill=FEATURE_COLORS['rock']['base'])
        # Add highlight
        draw.line([points[0], points[1]], fill=FEATURE_COLORS['rock']['highlight'], width=2)
    
    elif variation_num == 1:
        # Cluster of small rocks
        for _ in range(5):
            x = SPRITE_SIZE//2 + random.randint(-15, 15)
            y = SPRITE_SIZE - 20 + random.randint(-10, 10)
            size = random.randint(5, 10)
            draw.ellipse([x-size, y-size, x+size, y+size],
                        fill=FEATURE_COLORS['rock']['base'])
            # Add highlight
            draw.arc([x-size, y-size, x+size, y+size],
                    0, 90, fill=FEATURE_COLORS['rock']['highlight'], width=1)
    
    elif variation_num == 2:
        # Angular rock formation
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            r = random.randint(10, 20)
            x = SPRITE_SIZE//2 + r * math.cos(angle)
            y = SPRITE_SIZE - 20 + r * math.sin(angle)
            points.append((x, y))
        if points:
            draw.polygon(points, fill=FEATURE_COLORS['rock']['base'])
            # Add highlights
            for i in range(len(points)-1):
                if random.random() > 0.5:
                    draw.line([points[i], points[i+1]],
                            fill=FEATURE_COLORS['rock']['highlight'], width=1)
    
    else:
        # Cracked boulder
        # Main rock
        draw.ellipse([SPRITE_SIZE//4, SPRITE_SIZE//2,
                     3*SPRITE_SIZE//4, SPRITE_SIZE - 10],
                    fill=FEATURE_COLORS['rock']['base'])
        # Add cracks
        for _ in range(3):
            start_x = SPRITE_SIZE//2 + random.randint(-10, 10)
            points = [(start_x, SPRITE_SIZE - 20)]
            for _ in range(3):
                points.append((points[-1][0] + random.randint(-5, 5),
                             points[-1][1] - random.randint(5, 10)))
            if len(points) > 1:
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]],
                            fill=FEATURE_COLORS['rock']['highlight'], width=1)
    
    return img

def create_bush_feature(variation_num):
    """Create a bush feature with different styles."""
    img = Image.new('RGBA', (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if variation_num == 0:
        # Round bush
        draw.ellipse([SPRITE_SIZE//4, SPRITE_SIZE//2,
                     3*SPRITE_SIZE//4, SPRITE_SIZE - 10],
                    fill=FEATURE_COLORS['bush']['base'])
        # Add highlights
        for _ in range(5):
            x = SPRITE_SIZE//2 + random.randint(-10, 10)
            y = 3*SPRITE_SIZE//4 + random.randint(-10, 10)
            size = random.randint(3, 6)
            draw.ellipse([x-size, y-size, x+size, y+size],
                        fill=FEATURE_COLORS['bush']['highlight'])
    
    elif variation_num == 1:
        # Spiky bush
        center_x, center_y = SPRITE_SIZE//2, 3*SPRITE_SIZE//4
        for i in range(12):
            angle = i * math.pi / 6
            length = random.randint(10, 15)
            end_x = center_x + length * math.cos(angle)
            end_y = center_y + length * math.sin(angle)
            draw.line([center_x, center_y, end_x, end_y],
                     fill=FEATURE_COLORS['bush']['base'], width=3)
        # Add highlights
        draw.ellipse([center_x-5, center_y-5, center_x+5, center_y+5],
                    fill=FEATURE_COLORS['bush']['highlight'])
    
    elif variation_num == 2:
        # Layered bush
        for i in range(3):
            y_offset = SPRITE_SIZE - 20 - i * 10
            draw.arc([SPRITE_SIZE//4, y_offset,
                     3*SPRITE_SIZE//4, y_offset + 20],
                    0, 180, fill=FEATURE_COLORS['bush']['base'], width=5)
        # Add highlights
        draw.arc([SPRITE_SIZE//4 + 5, SPRITE_SIZE - 30,
                 3*SPRITE_SIZE//4 - 5, SPRITE_SIZE - 10],
                0, 180, fill=FEATURE_COLORS['bush']['highlight'], width=2)
    
    else:
        # Flowering bush
        # Base
        draw.ellipse([SPRITE_SIZE//4, SPRITE_SIZE//2,
                     3*SPRITE_SIZE//4, SPRITE_SIZE - 10],
                    fill=FEATURE_COLORS['bush']['base'])
        # Add flowers
        for _ in range(6):
            x = SPRITE_SIZE//2 + random.randint(-15, 15)
            y = 3*SPRITE_SIZE//4 + random.randint(-15, 15)
            size = random.randint(2, 4)
            color = random.choice(FEATURE_COLORS['flower']['petals'])
            draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
    
    return img

def create_flower_feature(variation_num):
    """Create a flower feature with different styles."""
    img = Image.new('RGBA', (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if variation_num == 0:
        # Daisy-like flower
        # Stem
        draw.line([SPRITE_SIZE//2, SPRITE_SIZE - 10,
                  SPRITE_SIZE//2, SPRITE_SIZE//2],
                 fill=FEATURE_COLORS['flower']['stem'], width=2)
        # Petals
        for i in range(8):
            angle = i * math.pi / 4
            r = 8
            x = SPRITE_SIZE//2 + r * math.cos(angle)
            y = SPRITE_SIZE//2 + r * math.sin(angle)
            draw.ellipse([x-3, y-3, x+3, y+3],
                        fill=random.choice(FEATURE_COLORS['flower']['petals']))
        # Center
        draw.ellipse([SPRITE_SIZE//2-2, SPRITE_SIZE//2-2,
                     SPRITE_SIZE//2+2, SPRITE_SIZE//2+2],
                    fill=FEATURE_COLORS['flower']['petals'][0])
    
    elif variation_num == 1:
        # Tulip-like flower
        # Stem
        draw.line([SPRITE_SIZE//2, SPRITE_SIZE - 10,
                  SPRITE_SIZE//2, SPRITE_SIZE//2],
                 fill=FEATURE_COLORS['flower']['stem'], width=2)
        # Petals
        points = [(SPRITE_SIZE//2, SPRITE_SIZE//2 - 10),
                 (SPRITE_SIZE//2 - 8, SPRITE_SIZE//2 + 5),
                 (SPRITE_SIZE//2 + 8, SPRITE_SIZE//2 + 5)]
        draw.polygon(points, fill=random.choice(FEATURE_COLORS['flower']['petals']))
    
    elif variation_num == 2:
        # Cluster of small flowers
        for _ in range(5):
            x = SPRITE_SIZE//2 + random.randint(-10, 10)
            y = SPRITE_SIZE - 20 + random.randint(-10, 10)
            # Stem
            draw.line([x, y + 10, x, y],
                     fill=FEATURE_COLORS['flower']['stem'], width=1)
            # Flower
            color = random.choice(FEATURE_COLORS['flower']['petals'])
            draw.ellipse([x-2, y-2, x+2, y+2], fill=color)
    
    else:
        # Sunflower-like
        # Stem
        draw.line([SPRITE_SIZE//2, SPRITE_SIZE - 10,
                  SPRITE_SIZE//2, SPRITE_SIZE//2],
                 fill=FEATURE_COLORS['flower']['stem'], width=3)
        # Petals
        for i in range(12):
            angle = i * math.pi / 6
            r = 12
            x = SPRITE_SIZE//2 + r * math.cos(angle)
            y = SPRITE_SIZE//2 + r * math.sin(angle)
            points = [(SPRITE_SIZE//2, SPRITE_SIZE//2),
                     (x - 3 * math.sin(angle), y + 3 * math.cos(angle)),
                     (x + 3 * math.sin(angle), y - 3 * math.cos(angle))]
            draw.polygon(points, fill=FEATURE_COLORS['flower']['petals'][3])
        # Center
        draw.ellipse([SPRITE_SIZE//2-4, SPRITE_SIZE//2-4,
                     SPRITE_SIZE//2+4, SPRITE_SIZE//2+4],
                    fill=FEATURE_COLORS['flower']['petals'][0])
    
    return img

def save_feature(img, feature_type, variation_num):
    """Save the feature sprite."""
    os.makedirs('assets/terrain/features', exist_ok=True)
    output_path = f'assets/terrain/features/feature_{feature_type}_{variation_num:02d}.png'
    img.save(output_path, 'PNG')
    print(f"Generated {output_path}")

def main():
    """Generate all terrain feature sprites."""
    print("Generating terrain feature sprites...")
    
    # Generate tree features
    for i in range(4):
        feature = create_tree_feature(i)
        save_feature(feature, 'tree', i)
    
    # Generate rock features
    for i in range(4):
        feature = create_rock_feature(i)
        save_feature(feature, 'rock', i)
    
    # Generate bush features
    for i in range(4):
        feature = create_bush_feature(i)
        save_feature(feature, 'bush', i)
    
    # Generate flower features
    for i in range(4):
        feature = create_flower_feature(i)
        save_feature(feature, 'flower', i)
    
    print("Done!")

if __name__ == '__main__':
    main() 