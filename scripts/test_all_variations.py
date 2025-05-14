#!/usr/bin/env python3
from PIL import Image
import os

def test_all_variations():
    """Test all variations overlaid on all base terrains."""
    # Ensure output directory exists
    os.makedirs('assets/terrain/test_all', exist_ok=True)
    
    # Base terrains
    base_terrains = ['grass', 'water', 'forest', 'desert', 'snow', 'mountain']
    
    # Variations
    variations = {
        'snow': range(4),
        'autumn': range(4),
        'rain': range(4),
        'fog': range(4)
    }
    
    for terrain in base_terrains:
        # Load base terrain sprite (using first variation)
        base_path = f'assets/terrain/base/terrain_{terrain}_00.png'
        if not os.path.exists(base_path):
            print(f"Warning: Base terrain {base_path} not found")
            continue
        
        base_img = Image.open(base_path).convert('RGBA')
        
        # Test each variation type
        for var_type, var_range in variations.items():
            for var_num in var_range:
                # Load variation
                var_path = f'assets/terrain/variations/variation_{var_type}_{var_num:02d}.png'
                if not os.path.exists(var_path):
                    print(f"Warning: Variation {var_path} not found")
                    continue
                
                var_img = Image.open(var_path).convert('RGBA')
                
                # Composite the images
                result = Image.alpha_composite(base_img, var_img)
                
                # Save the result
                output_path = f'assets/terrain/test_all/{terrain}_{var_type}_{var_num:02d}.png'
                result.save(output_path)
                print(f"Generated test overlay: {output_path}")

if __name__ == '__main__':
    print("Testing all variations...")
    test_all_variations()
    print("Done!") 