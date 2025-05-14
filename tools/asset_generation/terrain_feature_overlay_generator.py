import os
import argparse
import numpy as np
from PIL import Image, ImageDraw

# Feature and overlay definitions
FEATURE_TYPES = {
    'tree_oak': [(34, 139, 34), (139, 69, 19)],  # foliage, trunk
    'tree_pine': [(0, 100, 0), (139, 69, 19)],
    'bush': [(60, 179, 113), (46, 139, 87)],
    'rock_small': [(169, 169, 169), (112, 128, 144)],
    'rock_large': [(105, 105, 105), (169, 169, 169)],
    'flower': [(255, 192, 203), (255, 255, 0)],  # petal, center
}

OVERLAY_TYPES = ['elevation', 'shadow']
DIRECTIONS = ['north', 'south', 'east', 'west']
ASSET_SIZE = (64, 64)
VARIATIONS_PER_FEATURE = 5
VARIATIONS_PER_OVERLAY = 3
FEATURE_OUTPUT_DIR = os.path.join('assets', 'terrain', 'features')
OVERLAY_OUTPUT_DIR = os.path.join('assets', 'terrain', 'overlays')


def generate_feature(feature_type, variation_num, size=ASSET_SIZE):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    center = (size[0] // 2, size[1] // 2)
    np.random.seed(variation_num * hash(feature_type) % 2**32)
    if feature_type.startswith('tree'):
        # Draw trunk
        trunk_color = FEATURE_TYPES[feature_type][1]
        draw.rectangle([center[0]-3, center[1]+10, center[0]+3, size[1]-8], fill=trunk_color)
        # Draw foliage (ellipse or triangle for pine)
        foliage_color = FEATURE_TYPES[feature_type][0]
        if 'oak' in feature_type:
            draw.ellipse([center[0]-16, center[1]-16, center[0]+16, center[1]+16], fill=foliage_color)
        elif 'pine' in feature_type:
            points = [
                (center[0], center[1]-20),
                (center[0]-16, center[1]+10),
                (center[0]+16, center[1]+10)
            ]
            draw.polygon(points, fill=foliage_color)
    elif feature_type == 'bush':
        for i in range(3):
            offset = np.random.randint(-8, 8, 2)
            draw.ellipse([
                center[0]-12+offset[0], center[1]-8+offset[1],
                center[0]+12+offset[0], center[1]+8+offset[1]
            ], fill=FEATURE_TYPES[feature_type][i%2])
    elif feature_type.startswith('rock'):
        for i in range(2 if 'small' in feature_type else 4):
            offset = np.random.randint(-10, 10, 2)
            size_mod = np.random.randint(8, 16)
            draw.ellipse([
                center[0]-size_mod+offset[0], center[1]-size_mod//2+offset[1],
                center[0]+size_mod+offset[0], center[1]+size_mod//2+offset[1]
            ], fill=FEATURE_TYPES[feature_type][i%2])
    elif feature_type == 'flower':
        # Draw petals
        for angle in range(0, 360, 72):
            rad = np.deg2rad(angle)
            px = int(center[0] + 16 * np.cos(rad))
            py = int(center[1] + 16 * np.sin(rad))
            draw.ellipse([px-6, py-6, px+6, py+6], fill=FEATURE_TYPES[feature_type][0])
        # Draw center
        draw.ellipse([center[0]-8, center[1]-8, center[0]+8, center[1]+8], fill=FEATURE_TYPES[feature_type][1])
    return img


def generate_overlay(overlay_type, direction, variation_num, size=ASSET_SIZE):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    arr = np.zeros((size[1], size[0], 4), dtype=np.uint8)
    if overlay_type == 'elevation':
        # Alpha gradient in direction
        grad = np.linspace(0, 180, size[1] if direction in ['north', 'south'] else size[0])
        grad = grad.astype(np.uint8)
        if direction == 'north':
            arr[:,:,-1] = grad[::-1][:,None] if grad.ndim == 1 else grad[::-1]
        elif direction == 'south':
            arr[:,:,-1] = grad[:,None] if grad.ndim == 1 else grad
        elif direction == 'east':
            arr[:,-1] = grad
        elif direction == 'west':
            arr[:,0] = grad[::-1]
        arr[...,:3] = 255  # white
    elif overlay_type == 'shadow':
        # Soft shadow in direction
        shadow_color = (0, 0, 0)
        alpha = np.zeros(size)
        if direction == 'north':
            alpha[:size[1]//2,:] = np.linspace(80, 0, size[1]//2)[:,None]
        elif direction == 'south':
            alpha[size[1]//2:,:] = np.linspace(0, 80, size[1]//2)[:,None]
        elif direction == 'east':
            alpha[:,size[0]//2:] = np.linspace(0, 80, size[0]//2)[None,:]
        elif direction == 'west':
            alpha[:,:size[0]//2] = np.linspace(80, 0, size[0]//2)[None,:]
        for c in range(3):
            arr[...,c] = shadow_color[c]
        arr[...,-1] = alpha.astype(np.uint8)
    img = Image.fromarray(arr, 'RGBA')
    return img


def generate_all_features_and_overlays(feature_dir=FEATURE_OUTPUT_DIR, overlay_dir=OVERLAY_OUTPUT_DIR, dry_run=False):
    os.makedirs(feature_dir, exist_ok=True)
    os.makedirs(overlay_dir, exist_ok=True)
    # Features
    for feature_type in FEATURE_TYPES:
        for variation in range(1, VARIATIONS_PER_FEATURE+1):
            img = generate_feature(feature_type, variation)
            filename = f"{feature_type}_{variation:02d}.png"
            path = os.path.join(feature_dir, filename)
            if not dry_run:
                img.save(path)
            print(f"Generated feature: {path}")
    # Overlays
    for overlay_type in OVERLAY_TYPES:
        for direction in DIRECTIONS:
            for variation in range(1, VARIATIONS_PER_OVERLAY+1):
                img = generate_overlay(overlay_type, direction, variation)
                filename = f"{overlay_type}_{direction}_{variation:02d}.png"
                path = os.path.join(overlay_dir, filename)
                if not dry_run:
                    img.save(path)
                print(f"Generated overlay: {path}")


def main():
    parser = argparse.ArgumentParser(description="Generate terrain features and overlays for hex-based system.")
    parser.add_argument('--dry-run', action='store_true', help='Do not save files, just print actions.')
    parser.add_argument('--feature-dir', type=str, default=FEATURE_OUTPUT_DIR, help='Output directory for features.')
    parser.add_argument('--overlay-dir', type=str, default=OVERLAY_OUTPUT_DIR, help='Output directory for overlays.')
    args = parser.parse_args()
    generate_all_features_and_overlays(feature_dir=args.feature_dir, overlay_dir=args.overlay_dir, dry_run=args.dry_run)

if __name__ == "__main__":
    main() 