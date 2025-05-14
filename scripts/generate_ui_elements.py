import os
from PIL import Image, ImageDraw
import math

# Constants for UI element sizes
HEX_INDICATOR_SIZE = (64, 64)
RESOURCE_MARKER_SIZE = (32, 32)
STATUS_INDICATOR_SIZE = (24, 24)
TERRITORY_MARKER_SIZE = (48, 48)
INFO_DISPLAY_SIZE = (128, 32)

# Color palette based on the asset inventory
COLORS = {
    'selection': '#3498db80',  # Semi-transparent blue
    'highlight': '#f1c40f80',  # Semi-transparent yellow
    'resource': {
        'gold': '#f1c40f',     # Yellow
        'wood': '#27ae60',     # Green
        'stone': '#7f8c8d',    # Gray
        'food': '#e67e22',     # Orange
    },
    'status': {
        'health': '#27ae60',   # Green
        'mana': '#3498db',     # Blue
        'stamina': '#f39c12',  # Orange
        'shield': '#7f8c8d',   # Gray
    },
    'territory': {
        'player': '#2ecc71',   # Green
        'ally': '#3498db',     # Blue
        'enemy': '#e74c3c',    # Red
        'neutral': '#95a5a6',  # Light gray
    },
    'info': {
        'background': '#2c3e5080',  # Semi-transparent dark blue
        'text': '#ecf0f1',     # White
        'border': '#34495e',   # Dark blue
    }
}

def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)

def create_hex_indicator(name, size, color):
    """Create a hex-shaped selection/highlight indicator"""
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
    
    # Draw the hexagon with a 2px border
    draw.polygon(points, outline=color, fill=None, width=2)
    
    return img

def create_resource_marker(resource_type, size):
    """Create a resource marker icon"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a circular background
    padding = 2
    color = COLORS['resource'][resource_type]
    draw.ellipse([padding, padding, size[0] - padding, size[1] - padding], fill=color)
    
    # Draw a center symbol based on resource type
    center_size = min(size) // 4
    center_x, center_y = size[0] // 2, size[1] // 2
    
    if resource_type == 'gold':
        # Draw a coin symbol
        draw.ellipse([
            center_x - center_size,
            center_y - center_size,
            center_x + center_size,
            center_y + center_size
        ], fill='#f39c12')
    elif resource_type == 'wood':
        # Draw a tree symbol
        points = [
            (center_x, center_y - center_size * 1.5),
            (center_x + center_size, center_y),
            (center_x - center_size, center_y)
        ]
        draw.polygon(points, fill='#196f3d')
    elif resource_type == 'stone':
        # Draw a mountain symbol
        points = [
            (center_x, center_y - center_size),
            (center_x + center_size, center_y + center_size),
            (center_x - center_size, center_y + center_size)
        ]
        draw.polygon(points, fill='#5d6d7e')
    elif resource_type == 'food':
        # Draw a wheat symbol
        draw.ellipse([
            center_x - center_size // 2,
            center_y - center_size,
            center_x + center_size // 2,
            center_y + center_size
        ], fill='#d35400')
    
    return img

def create_status_indicator(status_type, size, value_percentage=100):
    """Create a status indicator (health, mana, stamina, shield)"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw background
    padding = 1
    draw.rectangle([
        padding,
        padding,
        size[0] - padding,
        size[1] - padding
    ], fill='#2c3e50')  # Dark background
    
    # Draw the status bar based on value_percentage
    bar_width = int((size[0] - padding * 2) * (value_percentage / 100))
    draw.rectangle([
        padding,
        padding,
        bar_width,
        size[1] - padding
    ], fill=COLORS['status'][status_type])
    
    return img

def create_territory_marker(faction, size):
    """Create a territory control marker"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a semi-transparent background
    color = COLORS['territory'][faction]
    alpha_color = color[:-2] + '80'  # Add 50% transparency
    
    # Draw a banner shape
    width, height = size
    points = [
        (width // 2, height // 4),  # Top center
        (width * 3 // 4, height // 2),  # Right middle
        (width // 2, height * 3 // 4),  # Bottom center
        (width // 4, height // 2)  # Left middle
    ]
    draw.polygon(points, fill=alpha_color)
    
    # Draw border
    draw.line(points + [points[0]], fill=color, width=2)
    
    return img

def create_info_display(size):
    """Create an information display background"""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw rounded rectangle background
    radius = 5
    padding = 2
    draw.rounded_rectangle([
        padding,
        padding,
        size[0] - padding,
        size[1] - padding
    ], radius=radius, fill=COLORS['info']['background'])
    
    # Draw border
    draw.rounded_rectangle([
        padding,
        padding,
        size[0] - padding,
        size[1] - padding
    ], radius=radius, outline=COLORS['info']['border'], width=1)
    
    return img

def main():
    """Generate all UI elements and status indicators"""
    # Create base directories
    base_dir = os.path.join('assets', 'ui')
    for dir_path in [
        os.path.join(base_dir, 'indicators'),
        os.path.join(base_dir, 'resources'),
        os.path.join(base_dir, 'status'),
        os.path.join(base_dir, 'territory'),
        os.path.join(base_dir, 'info')
    ]:
        create_directory(dir_path)
    
    # Generate hex indicators
    indicators = ['selection', 'highlight']
    for indicator in indicators:
        img = create_hex_indicator(indicator, HEX_INDICATOR_SIZE, COLORS[indicator])
        img.save(os.path.join(base_dir, 'indicators', f'hex_{indicator}_01.png'))
    
    # Generate resource markers
    for resource in COLORS['resource']:
        img = create_resource_marker(resource, RESOURCE_MARKER_SIZE)
        img.save(os.path.join(base_dir, 'resources', f'resource_{resource}_01.png'))
    
    # Generate status indicators
    for status in COLORS['status']:
        # Generate different fill levels
        for percentage in [100, 75, 50, 25]:
            img = create_status_indicator(status, STATUS_INDICATOR_SIZE, percentage)
            img.save(os.path.join(base_dir, 'status', f'status_{status}_{percentage:03d}.png'))
    
    # Generate territory markers
    for faction in COLORS['territory']:
        img = create_territory_marker(faction, TERRITORY_MARKER_SIZE)
        img.save(os.path.join(base_dir, 'territory', f'territory_{faction}_01.png'))
    
    # Generate info display background
    img = create_info_display(INFO_DISPLAY_SIZE)
    img.save(os.path.join(base_dir, 'info', 'info_display_01.png'))

if __name__ == '__main__':
    main() 