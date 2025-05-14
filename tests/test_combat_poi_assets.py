import os
import unittest
from PIL import Image

class TestCombatPOIAssets(unittest.TestCase):
    def setUp(self):
        """Set up test paths"""
        self.base_dir = os.path.join('assets')
        self.combat_dir = os.path.join(self.base_dir, 'combat')
        self.poi_dir = os.path.join(self.base_dir, 'poi')
        
        # Expected sizes
        self.sizes = {
            'overlays': (128, 128),
            'effects': (128, 128),
            'indicators': (64, 64),
            'status': (32, 32),
            'markers': (32, 32),
            'interactions': (32, 32)
        }
        
        # Expected file counts
        self.expected_counts = {
            'overlays': 3,  # range, attack, movement
            'effects': 16,  # (heal, damage) * 8 frames
            'indicators': 3,  # movement, attack, range
            'status': 2,    # poison, heal
            'markers': 2,   # quest, dialog
            'interactions': 2  # quest, dialog
        }
    
    def test_directory_structure(self):
        """Test that all required directories exist"""
        required_dirs = [
            os.path.join(self.combat_dir, 'overlays'),
            os.path.join(self.combat_dir, 'effects'),
            os.path.join(self.combat_dir, 'indicators'),
            os.path.join(self.combat_dir, 'status'),
            os.path.join(self.poi_dir, 'markers'),
            os.path.join(self.poi_dir, 'interactions')
        ]
        
        for dir_path in required_dirs:
            self.assertTrue(os.path.exists(dir_path), f"Directory {dir_path} does not exist")
    
    def test_file_counts(self):
        """Test that the correct number of files exist in each directory"""
        # Combat assets
        self.assertEqual(
            len(os.listdir(os.path.join(self.combat_dir, 'overlays'))),
            self.expected_counts['overlays'],
            "Incorrect number of overlay files"
        )
        
        self.assertEqual(
            len(os.listdir(os.path.join(self.combat_dir, 'effects'))),
            self.expected_counts['effects'],
            "Incorrect number of effect files"
        )
        
        self.assertEqual(
            len(os.listdir(os.path.join(self.combat_dir, 'indicators'))),
            self.expected_counts['indicators'],
            "Incorrect number of indicator files"
        )
        
        self.assertEqual(
            len(os.listdir(os.path.join(self.combat_dir, 'status'))),
            self.expected_counts['status'],
            "Incorrect number of status effect files"
        )
        
        # POI assets
        self.assertEqual(
            len(os.listdir(os.path.join(self.poi_dir, 'markers'))),
            self.expected_counts['markers'],
            "Incorrect number of POI marker files"
        )
        
        self.assertEqual(
            len(os.listdir(os.path.join(self.poi_dir, 'interactions'))),
            self.expected_counts['interactions'],
            "Incorrect number of POI interaction files"
        )
    
    def test_file_naming(self):
        """Test that files follow the naming convention"""
        # Test combat overlays
        overlay_files = os.listdir(os.path.join(self.combat_dir, 'overlays'))
        for file in overlay_files:
            self.assertTrue(
                file.startswith('combat_overlay_'),
                f"Overlay file {file} does not follow naming convention"
            )
            self.assertTrue(
                file.endswith('.png'),
                f"Overlay file {file} is not a PNG file"
            )
        
        # Test combat effects
        effect_files = os.listdir(os.path.join(self.combat_dir, 'effects'))
        for file in effect_files:
            self.assertTrue(
                file.startswith('combat_effect_'),
                f"Effect file {file} does not follow naming convention"
            )
            self.assertTrue(
                file.endswith('.png'),
                f"Effect file {file} is not a PNG file"
            )
        
        # Test POI markers
        marker_files = os.listdir(os.path.join(self.poi_dir, 'markers'))
        for file in marker_files:
            self.assertTrue(
                file.startswith('poi_marker_'),
                f"Marker file {file} does not follow naming convention"
            )
            self.assertTrue(
                file.endswith('.png'),
                f"Marker file {file} is not a PNG file"
            )
    
    def test_image_properties(self):
        """Test image dimensions and format"""
        def check_image_properties(dir_path, expected_size):
            for file in os.listdir(dir_path):
                with Image.open(os.path.join(dir_path, file)) as img:
                    self.assertEqual(
                        img.size,
                        expected_size,
                        f"Incorrect size for {file}"
                    )
                    self.assertEqual(
                        img.mode,
                        'RGBA',
                        f"Incorrect mode for {file}"
                    )
        
        # Check combat assets
        check_image_properties(
            os.path.join(self.combat_dir, 'overlays'),
            self.sizes['overlays']
        )
        check_image_properties(
            os.path.join(self.combat_dir, 'effects'),
            self.sizes['effects']
        )
        check_image_properties(
            os.path.join(self.combat_dir, 'indicators'),
            self.sizes['indicators']
        )
        check_image_properties(
            os.path.join(self.combat_dir, 'status'),
            self.sizes['status']
        )
        
        # Check POI assets
        check_image_properties(
            os.path.join(self.poi_dir, 'markers'),
            self.sizes['markers']
        )
        check_image_properties(
            os.path.join(self.poi_dir, 'interactions'),
            self.sizes['interactions']
        )
    
    def test_animation_sequence(self):
        """Test that animation frames are sequential"""
        effect_files = os.listdir(os.path.join(self.combat_dir, 'effects'))
        
        # Group files by effect type
        effect_groups = {}
        for file in effect_files:
            effect_type = file.split('_')[2]  # combat_effect_TYPE_NNN.png
            if effect_type not in effect_groups:
                effect_groups[effect_type] = []
            effect_groups[effect_type].append(file)
        
        # Check each group has sequential frames
        for effect_type, files in effect_groups.items():
            files.sort()
            frame_numbers = [
                int(file.split('_')[-1].replace('.png', ''))
                for file in files
            ]
            self.assertEqual(
                frame_numbers,
                list(range(1, len(files) + 1)),
                f"Non-sequential frames for {effect_type}"
            )

if __name__ == '__main__':
    unittest.main() 