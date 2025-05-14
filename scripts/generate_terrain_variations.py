#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import os
import random
import colorsys
import math

# Constants from asset inventory
SPRITE_SIZE = 64
VARIATION_COLORS = {
    'snow': {
        'overlay': '#FFFFFF',  # White with 70% opacity
        'alpha': 178  # 70% of 255
    },
    'autumn': {
        'tint': '#FFA500',  # Orange with 40% opacity
        'alpha': 153  # 60% of 255 (increased from 102 to allow proper ranges)
    },
    'rain': {
        'droplet': '#1E88E5',  # Blue
        'puddle': '#1565C0'  # Dark blue
    },
    'fog': {
        'color': '#B0BEC5',  # Gray with varying opacity
        'alpha_range': (51, 153)  # 20-60% opacity
    }
}

def create_snow_variation(variation_num):
    """Create a snow overlay with different patterns."""
    img = Image.new('RGBA', (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if variation_num == 0:
        # Even snow cover
        for y in range(0, SPRITE_SIZE, 4):
            for x in range(0, SPRITE_SIZE, 4):
                if random.random() > 0.3:
                    size = random.randint(2, 4)
                    alpha = random.randint(128, VARIATION_COLORS['snow']['alpha'])
                    color = VARIATION_COLORS['snow']['overlay'] + hex(alpha)[2:].zfill(2)
                    draw.ellipse([x, y, x+size, y+size], fill=color)
    
    elif variation_num == 1:
        # Drifting snow
        for _ in range(30):
            x = random.randint(0, SPRITE_SIZE)
            y = random.randint(0, SPRITE_SIZE)
            size = random.randint(4, 8)
            alpha = random.randint(128, VARIATION_COLORS['snow']['alpha'])
            color = VARIATION_COLORS['snow']['overlay'] + hex(alpha)[2:].zfill(2)
            points = []
            for i in range(6):
                angle = i * math.pi / 3 + random.uniform(-0.2, 0.2)
                r = size + random.randint(-2, 2)
                px = x + r * math.cos(angle)
                py = y + r * math.sin(angle)
                points.append((px, py))
            if points:
                draw.polygon(points, fill=color)
    
    elif variation_num == 2:
        # Heavy snow
        for y in range(0, SPRITE_SIZE, 2):
            for x in range(0, SPRITE_SIZE, 2):
                if random.random() > 0.2:
                    size = random.randint(1, 3)
                    alpha = random.randint(153, VARIATION_COLORS['snow']['alpha'])
                    color = VARIATION_COLORS['snow']['overlay'] + hex(alpha)[2:].zfill(2)
                    draw.ellipse([x, y, x+size, y+size], fill=color)
    
    else:
        # Light snow
        for _ in range(40):
            x = random.randint(0, SPRITE_SIZE)
            y = random.randint(0, SPRITE_SIZE)
            size = random.randint(1, 2)
            alpha = random.randint(102, VARIATION_COLORS['snow']['alpha'])
            color = VARIATION_COLORS['snow']['overlay'] + hex(alpha)[2:].zfill(2)
            draw.ellipse([x, y, x+size, y+size], fill=color)
    
    return img

def create_autumn_variation(variation_num):
    """Create autumn color variations."""
    img = Image.new('RGBA', (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if variation_num == 0:
        # Scattered leaves
        for _ in range(20):
            x = random.randint(0, SPRITE_SIZE)
            y = random.randint(0, SPRITE_SIZE)
            size = random.randint(2, 4)
            alpha = random.randint(128, VARIATION_COLORS['autumn']['alpha'])
            color = VARIATION_COLORS['autumn']['tint'] + hex(alpha)[2:].zfill(2)
            angle = random.uniform(0, math.pi * 2)
            points = []
            for i in range(5):
                a = angle + (i * 2 * math.pi / 5)
                r = size if i % 2 == 0 else size * 0.5
                px = x + r * math.cos(a)
                py = y + r * math.sin(a)
                points.append((px, py))
            if points:
                draw.polygon(points, fill=color)
    
    elif variation_num == 1:
        # Color gradient
        for y in range(SPRITE_SIZE):
            for x in range(SPRITE_SIZE):
                if random.random() > 0.7:
                    alpha = int(VARIATION_COLORS['autumn']['alpha'] * (1 - y/SPRITE_SIZE))
                    if alpha > 0:
                        color = VARIATION_COLORS['autumn']['tint'] + hex(alpha)[2:].zfill(2)
                        draw.point([x, y], fill=color)
    
    elif variation_num == 2:
        # Dense leaves
        for _ in range(40):
            x = random.randint(0, SPRITE_SIZE)
            y = random.randint(0, SPRITE_SIZE)
            size = random.randint(3, 5)
            alpha = random.randint(102, VARIATION_COLORS['autumn']['alpha'])
            color = VARIATION_COLORS['autumn']['tint'] + hex(alpha)[2:].zfill(2)
            draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
    
    else:
        # Swirling leaves
        center_x, center_y = SPRITE_SIZE//2, SPRITE_SIZE//2
        for i in range(30):
            angle = (i / 30) * math.pi * 4
            r = (SPRITE_SIZE//4) * (1 + math.sin(angle * 2))
            x = center_x + r * math.cos(angle)
            y = center_y + r * math.sin(angle)
            size = random.randint(2, 3)
            alpha = random.randint(102, VARIATION_COLORS['autumn']['alpha'])
            color = VARIATION_COLORS['autumn']['tint'] + hex(alpha)[2:].zfill(2)
            draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
    
    return img

def create_rain_variation(variation_num):
    """Create rain effect variations."""
    img = Image.new('RGBA', (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if variation_num == 0:
        # Light rain
        for _ in range(20):
            x = random.randint(0, SPRITE_SIZE)
            y = random.randint(0, SPRITE_SIZE)
            length = random.randint(3, 5)
            alpha = random.randint(51, 102)
            color = VARIATION_COLORS['rain']['droplet'] + hex(alpha)[2:].zfill(2)
            end_x = x - length//2
            end_y = y + length
            draw.line([x, y, end_x, end_y], fill=color, width=1)
    
    elif variation_num == 1:
        # Heavy rain
        for _ in range(40):
            x = random.randint(0, SPRITE_SIZE)
            y = random.randint(0, SPRITE_SIZE)
            length = random.randint(4, 7)
            alpha = random.randint(102, 153)
            color = VARIATION_COLORS['rain']['droplet'] + hex(alpha)[2:].zfill(2)
            end_x = x - length//2
            end_y = y + length
            draw.line([x, y, end_x, end_y], fill=color, width=1)
            # Add puddles
            if random.random() > 0.8:
                puddle_x = random.randint(0, SPRITE_SIZE)
                puddle_y = SPRITE_SIZE - random.randint(5, 15)
                size = random.randint(2, 4)
                puddle_alpha = random.randint(51, 102)
                puddle_color = VARIATION_COLORS['rain']['puddle'] + hex(puddle_alpha)[2:].zfill(2)
                draw.ellipse([puddle_x-size, puddle_y-size//2,
                            puddle_x+size, puddle_y+size//2],
                           fill=puddle_color)
    
    elif variation_num == 2:
        # Storm
        for _ in range(60):
            x = random.randint(0, SPRITE_SIZE)
            y = random.randint(0, SPRITE_SIZE)
            length = random.randint(5, 8)
            alpha = random.randint(153, 204)
            color = VARIATION_COLORS['rain']['droplet'] + hex(alpha)[2:].zfill(2)
            end_x = x - length
            end_y = y + length
            draw.line([x, y, end_x, end_y], fill=color, width=2)
        # Add large puddles
        for _ in range(5):
            puddle_x = random.randint(0, SPRITE_SIZE)
            puddle_y = SPRITE_SIZE - random.randint(5, 15)
            size = random.randint(4, 7)
            puddle_alpha = random.randint(102, 153)
            puddle_color = VARIATION_COLORS['rain']['puddle'] + hex(puddle_alpha)[2:].zfill(2)
            draw.ellipse([puddle_x-size, puddle_y-size//2,
                         puddle_x+size, puddle_y+size//2],
                        fill=puddle_color)
    
    else:
        # Drizzle
        for _ in range(15):
            x = random.randint(0, SPRITE_SIZE)
            y = random.randint(0, SPRITE_SIZE)
            length = random.randint(2, 4)
            alpha = random.randint(51, 76)
            color = VARIATION_COLORS['rain']['droplet'] + hex(alpha)[2:].zfill(2)
            end_x = x - length//3
            end_y = y + length
            draw.line([x, y, end_x, end_y], fill=color, width=1)
    
    return img

def create_fog_variation(variation_num):
    """Create fog effect variations."""
    img = Image.new('RGBA', (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if variation_num == 0:
        # Light fog
        for y in range(0, SPRITE_SIZE, 4):
            alpha = random.randint(*VARIATION_COLORS['fog']['alpha_range'])
            color = VARIATION_COLORS['fog']['color'] + hex(alpha)[2:].zfill(2)
            draw.rectangle([0, y, SPRITE_SIZE, y+4], fill=color)
    
    elif variation_num == 1:
        # Swirling fog
        for i in range(8):
            points = []
            start_y = i * SPRITE_SIZE//8
            for x in range(0, SPRITE_SIZE, 4):
                y = start_y + math.sin(x/10) * 5
                points.append((x, y))
            if points:
                alpha = random.randint(*VARIATION_COLORS['fog']['alpha_range'])
                color = VARIATION_COLORS['fog']['color'] + hex(alpha)[2:].zfill(2)
                for j in range(len(points)-1):
                    draw.line([points[j], points[j+1]], fill=color, width=8)
    
    elif variation_num == 2:
        # Dense fog
        for y in range(0, SPRITE_SIZE, 2):
            alpha = random.randint(102, 178)  # 40-70% opacity
            color = VARIATION_COLORS['fog']['color'] + hex(alpha)[2:].zfill(2)
            draw.rectangle([0, y, SPRITE_SIZE, y+2], fill=color)
    
    else:
        # Patchy fog
        for _ in range(15):
            x = random.randint(0, SPRITE_SIZE)
            y = random.randint(0, SPRITE_SIZE)
            size = random.randint(10, 20)
            alpha = random.randint(*VARIATION_COLORS['fog']['alpha_range'])
            color = VARIATION_COLORS['fog']['color'] + hex(alpha)[2:].zfill(2)
            for i in range(5):
                offset = i * 4
                draw.ellipse([x-size+offset, y-size//2,
                            x+size+offset, y+size//2],
                           fill=color)
    
    return img

def save_variation(img, variation_type, variation_num):
    """Save the variation sprite."""
    os.makedirs('assets/terrain/variations', exist_ok=True)
    output_path = f'assets/terrain/variations/variation_{variation_type}_{variation_num:02d}.png'
    img.save(output_path, 'PNG')
    print(f"Generated {output_path}")

def main():
    """Generate all terrain variation sprites."""
    print("Generating terrain variation sprites...")
    
    # Generate snow variations
    for i in range(4):
        variation = create_snow_variation(i)
        save_variation(variation, 'snow', i)
    
    # Generate autumn variations
    for i in range(4):
        variation = create_autumn_variation(i)
        save_variation(variation, 'autumn', i)
    
    # Generate rain variations
    for i in range(4):
        variation = create_rain_variation(i)
        save_variation(variation, 'rain', i)
    
    # Generate fog variations
    for i in range(4):
        variation = create_fog_variation(i)
        save_variation(variation, 'fog', i)
    
    print("Done!")

if __name__ == '__main__':
    main() 