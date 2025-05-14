#!/usr/bin/env python3
import unittest
from PIL import Image
import os
import tempfile
import shutil

class TestTerrainOverlays(unittest.TestCase):
    """Test cases for terrain overlay functionality."""
    
    def setUp(self):
        """Create temporary directory for test outputs."""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, 'test_overlays')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Ensure asset directories exist for test
        os.makedirs(os.path.join(self.test_dir, 'base'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'variations'), exist_ok=True)
        
        # Create sample base image (green square)
        self.base_img = Image.new('RGBA', (64, 64), (0, 255, 0, 255))
        self.base_path = os.path.join(self.test_dir, 'base', 'terrain_grass_00.png')
        self.base_img.save(self.base_path)
        
        # Create sample variation (red transparent overlay)
        self.var_img = Image.new('RGBA', (64, 64), (255, 0, 0, 128))
        self.var_path = os.path.join(self.test_dir, 'variations', 'variation_autumn_00.png')
        self.var_img.save(self.var_path)
    
    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.test_dir)
    
    def test_overlay_variations(self):
        """Test overlaying autumn variations on base terrain sprites."""
        base_terrains = ['grass']
        variations = range(1)  # Just test one variation
        
        output_files = []
        
        for terrain in base_terrains:
            base_path = os.path.join(self.test_dir, 'base', f'terrain_{terrain}_00.png')
            self.assertTrue(os.path.exists(base_path), f"Base terrain file {base_path} must exist")
            
            base_img = Image.open(base_path).convert('RGBA')
            self.assertEqual(base_img.size, (64, 64), "Base image should be 64x64 pixels")
            
            for var_num in variations:
                var_path = os.path.join(self.test_dir, 'variations', f'variation_autumn_{var_num:02d}.png')
                self.assertTrue(os.path.exists(var_path), f"Variation file {var_path} must exist")
                
                var_img = Image.open(var_path).convert('RGBA')
                self.assertEqual(var_img.size, (64, 64), "Variation image should be 64x64 pixels")
                
                # Composite the images
                result = Image.alpha_composite(base_img, var_img)
                
                # Verify that the result is a valid image
                self.assertEqual(result.size, (64, 64), "Result should maintain image dimensions")
                self.assertEqual(result.mode, 'RGBA', "Result should maintain RGBA mode")
                
                # Save the result
                output_path = os.path.join(self.output_dir, f'{terrain}_autumn_{var_num:02d}.png')
                result.save(output_path)
                output_files.append(output_path)
                
                # Check if result exists and is a valid image
                self.assertTrue(os.path.exists(output_path), f"Output file {output_path} should exist")
                result_img = Image.open(output_path)
                self.assertTrue(result_img.width > 0 and result_img.height > 0, "Result should be a valid image")
                
                # Verify some pixels to ensure proper overlay
                # Center pixel should be a blend of green and red
                center_pixel = result.getpixel((32, 32))
                # With alpha blending, the result should be different from both source pixels
                base_center = base_img.getpixel((32, 32))
                var_center = var_img.getpixel((32, 32))
                self.assertNotEqual(center_pixel, base_center, "Result pixel should differ from base")
                self.assertNotEqual(center_pixel, var_center, "Result pixel should differ from variation")
                
                # Ensure red component from overlay is present
                self.assertGreater(center_pixel[0], 0, "Red component should be present from overlay")
                
        # Verify we generated the expected number of files
        self.assertEqual(len(output_files), len(base_terrains) * len(variations),
                         "Should generate one output file per terrain-variation combination")

if __name__ == '__main__':
    unittest.main() 