import os
import argparse
import numpy as np
from PIL import Image, ImageDraw

# Terrain type definitions and color palettes
TERRAIN_TYPES = {
    'grass': [(34, 139, 34), (50, 205, 50), (107, 142, 35)],
    'water': [(28, 107, 160), (0, 191, 255), (70, 130, 180)],
    'sand': [(237, 201, 175), (244, 164, 96), (210, 180, 140)],
    'rock': [(112, 128, 144), (169, 169, 169), (105, 105, 105)],
    'dirt': [(139, 69, 19), (160, 82, 45), (205, 133, 63)],
    'snow': [(255, 250, 250), (240, 248, 255), (220, 220, 220)],
    'lava': [(207, 16, 32), (255, 69, 0), (255, 140, 0)],
}

ASSET_SIZE = (64, 64)
VARIATIONS_PER_TYPE = 6
OUTPUT_DIR = os.path.join('assets', 'terrain', 'base')


def perlin_noise(size, scale=8):
    # Simple Perlin-like noise using numpy
    lin = np.linspace(0, scale, size[0], endpoint=False)
    x, y = np.meshgrid(lin, lin)
    noise = np.sin(x) * np.cos(y)
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    return noise


def generate_terrain_base(terrain_type, variation_num, size=ASSET_SIZE):
    base_colors = TERRAIN_TYPES[terrain_type]
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Generate noise for texture
    noise = perlin_noise(size, scale=8 + variation_num)
    for y in range(size[1]):
        for x in range(size[0]):
            # Pick a base color and modulate with noise
            color_idx = (x + y + variation_num) % len(base_colors)
            base = np.array(base_colors[color_idx])
            n = noise[y, x]
            # Blend with white/black for subtle variation
            blend = np.clip(base * (0.8 + 0.2 * n), 0, 255).astype(np.uint8)
            draw.point((x, y), tuple(blend) + (255,))

    # Optionally add pattern overlays for uniqueness
    if terrain_type == 'grass':
        for _ in range(20):
            rx, ry = np.random.randint(0, size[0]), np.random.randint(0, size[1])
            draw.ellipse((rx, ry, rx+2, ry+2), fill=(60, 179, 113, 120))
    elif terrain_type == 'rock':
        for _ in range(10):
            rx, ry = np.random.randint(0, size[0]), np.random.randint(0, size[1])
            draw.rectangle((rx, ry, rx+3, ry+3), fill=(169, 169, 169, 100))
    # Add more patterns for other types as needed

    return img


def generate_all_terrain_bases(output_dir=OUTPUT_DIR, dry_run=False):
    os.makedirs(output_dir, exist_ok=True)
    for terrain_type in TERRAIN_TYPES:
        for variation in range(1, VARIATIONS_PER_TYPE + 1):
            img = generate_terrain_base(terrain_type, variation)
            filename = f"{terrain_type}_{variation:02d}.png"
            path = os.path.join(output_dir, filename)
            if not dry_run:
                img.save(path)
            print(f"Generated: {path}")


def main():
    parser = argparse.ArgumentParser(description="Generate base terrain assets for hex-based system.")
    parser.add_argument('--dry-run', action='store_true', help='Do not save files, just print actions.')
    parser.add_argument('--output', type=str, default=OUTPUT_DIR, help='Output directory for assets.')
    args = parser.parse_args()
    generate_all_terrain_bases(output_dir=args.output, dry_run=args.dry_run)

if __name__ == "__main__":
    main() 