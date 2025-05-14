import os
import math
import colorsys
from PIL import Image, ImageDraw

# Constants for asset sizes
OVERLAY_SIZE = (128, 128)
EFFECT_SIZE = (128, 128)
INDICATOR_SIZE = (64, 64)
STATUS_SIZE = (32, 32)
POI_SIZE = (32, 32)

# Color palette based on the asset inventory
COLORS = {
    'range': '#3498db80',  # Semi-transparent blue
    'attack': '#e74c3c80',  # Semi-transparent red
    'movement': '#2ecc7180',  # Semi-transparent green
    'poison': '#9b59b680',  # Semi-transparent purple
    'quest': '#f1c40f',     # Yellow
    'dialog': '#2980b9',    # Blue
    'heal': '#27ae60',      # Green
    'damage': '#c0392b',    # Dark red
}

def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)

def create_overlay(name, size, color):
    """Create a hex-shaped overlay with the specified color"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate hex points
    width, height = size
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 2 - 2
    
    # Calculate the six points of the hexagon
    points = []
    for i in range(6):
        angle = i * 60 - 30  # -30 to align flat side at top
        x = center_x + radius * math.cos(angle * math.pi / 180)
        y = center_y + radius * math.sin(angle * math.pi / 180)
        points.append((x, y))
    
    # Draw the hexagon
    draw.polygon(points, fill=color)
    
    return img

def create_effect_frame(name, size, color, frame):
    """Create an animated effect frame"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate effect parameters based on frame
    width, height = size
    center_x, center_y = width // 2, height // 2
    max_radius = min(width, height) // 3
    
    # Create a pulsing effect
    radius = max_radius * (1 + math.sin(frame * math.pi / 8)) / 2
    
    # Draw the effect
    draw.ellipse([
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius
    ], fill=color)
    
    return img

def create_indicator(name, size, color):
    """Create an indicator icon"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple arrow or marker
    width, height = size
    points = [
        (width // 2, height // 4),
        (width * 3 // 4, height * 3 // 4),
        (width // 2, height * 2 // 3),
        (width // 4, height * 3 // 4)
    ]
    draw.polygon(points, fill=color)
    
    return img

def create_status_icon(name, size, color):
    """Create a status effect icon"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple circular icon
    padding = 2
    draw.ellipse([padding, padding, size[0] - padding, size[1] - padding], fill=color)
    
    return img

def create_poi_marker(name, size, color):
    """Create a POI marker icon"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a location marker shape
    width, height = size
    points = [
        (width // 2, height // 4),
        (width * 3 // 4, height // 2),
        (width // 2, height * 3 // 4),
        (width // 4, height // 2)
    ]
    draw.polygon(points, fill=color)
    
    # Add a center dot
    center_size = min(width, height) // 6
    draw.ellipse([
        width // 2 - center_size,
        height // 2 - center_size,
        width // 2 + center_size,
        height // 2 + center_size
    ], fill=color)
    
    return img

def main():
    """Generate all combat and POI assets"""
    # Create base directories
    base_dir = os.path.join('assets')
    combat_dir = os.path.join(base_dir, 'combat')
    poi_dir = os.path.join(base_dir, 'poi')
    
    # Create all required directories
    for dir_path in [
        os.path.join(combat_dir, 'overlays'),
        os.path.join(combat_dir, 'effects'),
        os.path.join(combat_dir, 'indicators'),
        os.path.join(combat_dir, 'status'),
        os.path.join(poi_dir, 'markers'),
        os.path.join(poi_dir, 'interactions')
    ]:
        create_directory(dir_path)
    
    # Generate combat overlays
    overlay_types = ['range', 'attack', 'movement']
    for overlay_type in overlay_types:
        img = create_overlay(overlay_type, OVERLAY_SIZE, COLORS[overlay_type])
        img.save(os.path.join(combat_dir, 'overlays', f'combat_overlay_{overlay_type}_01.png'))
    
    # Generate combat effects
    effect_types = ['heal', 'damage']
    for effect_type in effect_types:
        for frame in range(1, 9):  # 8 frames of animation
            img = create_effect_frame(effect_type, EFFECT_SIZE, COLORS[effect_type], frame)
            img.save(os.path.join(combat_dir, 'effects', f'combat_effect_{effect_type}_{frame:03d}.png'))
    
    # Generate combat indicators
    indicator_types = ['movement', 'attack', 'range']
    for indicator_type in indicator_types:
        img = create_indicator(indicator_type, INDICATOR_SIZE, COLORS[indicator_type])
        img.save(os.path.join(combat_dir, 'indicators', f'combat_indicator_{indicator_type}_01.png'))
    
    # Generate status effects
    status_types = ['poison', 'heal']
    for status_type in status_types:
        img = create_status_icon(status_type, STATUS_SIZE, COLORS[status_type])
        img.save(os.path.join(combat_dir, 'status', f'status_effect_{status_type}_01.png'))
    
    # Generate POI markers
    marker_types = ['quest', 'dialog']
    for marker_type in marker_types:
        img = create_poi_marker(marker_type, POI_SIZE, COLORS[marker_type])
        img.save(os.path.join(poi_dir, 'markers', f'poi_marker_{marker_type}_01.png'))
        # Also create interaction indicators
        img = create_indicator(marker_type, POI_SIZE, COLORS[marker_type])
        img.save(os.path.join(poi_dir, 'interactions', f'poi_interaction_{marker_type}_01.png'))

if __name__ == '__main__':
    main() 