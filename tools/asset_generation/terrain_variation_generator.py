import os
import argparse
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

SEASONS = ['summer', 'autumn', 'winter', 'spring']
WEATHERS = ['rain', 'snow', 'fog']
VARIATION_INPUT_DIRS = [
    os.path.join('assets', 'terrain', 'base'),
    os.path.join('assets', 'terrain', 'features')
]
VARIATION_OUTPUT_DIR = os.path.join('assets', 'terrain', 'variations')

SEASON_TRANSFORMS = {
    'summer': lambda img: img,
    'autumn': lambda img: ImageOps.colorize(ImageOps.grayscale(img), (120, 70, 20), (255, 200, 80)).convert('RGBA'),
    'winter': lambda img: ImageEnhance.Color(img).enhance(0.3),
    'spring': lambda img: ImageEnhance.Color(img).enhance(1.2),
}


def apply_seasonal_variation(img, season):
    if season == 'autumn':
        # Orange/yellow tint
        return SEASON_TRANSFORMS['autumn'](img)
    elif season == 'winter':
        # Desaturate and brighten, add snow overlay
        img = SEASON_TRANSFORMS['winter'](img)
        snow = Image.new('RGBA', img.size, (255, 255, 255, 0))
        arr = np.array(snow)
        snow_mask = np.random.rand(*img.size) > 0.92
        arr[snow_mask] = [255, 255, 255, 120]
        snow = Image.fromarray(arr, 'RGBA')
        return Image.alpha_composite(img.convert('RGBA'), snow)
    elif season == 'spring':
        # Slightly more saturated
        return SEASON_TRANSFORMS['spring'](img)
    else:
        return img


def apply_weather_variation(img, weather):
    if weather == 'rain':
        # Blue/gray tint, add puddle highlights
        overlay = Image.new('RGBA', img.size, (80, 120, 180, 60))
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        # Add puddle speckles
        arr = np.array(img)
        mask = np.random.rand(*img.size) > 0.97
        arr[mask] = [180, 200, 255, 180]
        return Image.fromarray(arr, 'RGBA')
    elif weather == 'snow':
        # Overlay white speckles, increase brightness
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.2)
        snow = Image.new('RGBA', img.size, (255, 255, 255, 0))
        arr = np.array(snow)
        snow_mask = np.random.rand(*img.size) > 0.94
        arr[snow_mask] = [255, 255, 255, 140]
        snow = Image.fromarray(arr, 'RGBA')
        return Image.alpha_composite(img.convert('RGBA'), snow)
    elif weather == 'fog':
        # Overlay semi-transparent white/gray layer
        overlay = Image.new('RGBA', img.size, (220, 220, 220, 80))
        return Image.alpha_composite(img.convert('RGBA'), overlay)
    else:
        return img


def generate_all_variations(input_dirs=VARIATION_INPUT_DIRS, output_dir=VARIATION_OUTPUT_DIR, dry_run=False):
    os.makedirs(output_dir, exist_ok=True)
    for input_dir in input_dirs:
        for fname in os.listdir(input_dir):
            if not fname.endswith('.png'):
                continue
            path = os.path.join(input_dir, fname)
            img = Image.open(path).convert('RGBA')
            # Seasonal variations
            for season in SEASONS:
                out_img = apply_seasonal_variation(img, season)
                out_name = f"{season}_{fname}"
                out_path = os.path.join(output_dir, out_name)
                if not dry_run:
                    out_img.save(out_path)
                print(f"Generated: {out_path}")
            # Weather variations
            for weather in WEATHERS:
                out_img = apply_weather_variation(img, weather)
                out_name = f"{weather}_{fname}"
                out_path = os.path.join(output_dir, out_name)
                if not dry_run:
                    out_img.save(out_path)
                print(f"Generated: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate seasonal and weather variations for terrain assets.")
    parser.add_argument('--dry-run', action='store_true', help='Do not save files, just print actions.')
    parser.add_argument('--input-dirs', nargs='+', default=VARIATION_INPUT_DIRS, help='Input directories for base assets.')
    parser.add_argument('--output-dir', type=str, default=VARIATION_OUTPUT_DIR, help='Output directory for variations.')
    args = parser.parse_args()
    generate_all_variations(input_dirs=args.input_dirs, output_dir=args.output_dir, dry_run=args.dry_run)

if __name__ == "__main__":
    main() 