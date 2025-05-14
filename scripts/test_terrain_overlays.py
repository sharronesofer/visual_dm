#!/usr/bin/env python3
from PIL import Image
import os

def test_overlay_variations():
    """Test overlaying autumn variations on base terrain sprites."""
    # Ensure output directory exists
    os.makedirs('assets/terrain/test_overlays', exist_ok=True)
    
    # Load base terrain types
    base_terrains = ['grass', 'forest']  # These will show autumn effects best
    variations = range(4)
    
    for terrain in base_terrains:
        # Load base terrain sprite
        base_path = f'assets/terrain/base/terrain_{terrain}_00.png'  # Using first variation of each
        if not os.path.exists(base_path):
            print(f"Warning: Base terrain {base_path} not found")
            continue
        
        base_img = Image.open(base_path).convert('RGBA')
        
        # Test each autumn variation
        for var_num in variations:
            # Load autumn variation
            var_path = f'assets/terrain/variations/variation_autumn_{var_num:02d}.png'
            if not os.path.exists(var_path):
                print(f"Warning: Variation {var_path} not found")
                continue
            
            var_img = Image.open(var_path).convert('RGBA')
            
            # Composite the images
            result = Image.alpha_composite(base_img, var_img)
            
            # Save the result
            output_path = f'assets/terrain/test_overlays/{terrain}_autumn_{var_num:02d}.png'
            result.save(output_path)
            print(f"Generated test overlay: {output_path}")

if __name__ == '__main__':
    print("Testing autumn variation overlays...")
    test_overlay_variations()
    print("Done!") 