import os
import unittest
from PIL import Image

class TestUIElements(unittest.TestCase):
    def setUp(self):
        """Set up test paths"""
        self.base_dir = os.path.join('assets', 'ui')
        
        # Expected sizes
        self.sizes = {
            'indicators': (64, 64),
            'resources': (32, 32),
            'status': (24, 24),
            'territory': (48, 48),
            'info': (128, 32)
        }
        
        # Expected file counts
        self.expected_counts = {
            'indicators': 2,  # selection, highlight
            'resources': 4,   # gold, wood, stone, food
            'status': 16,     # (health, mana, stamina, shield) * 4 percentages
            'territory': 4,   # player, ally, enemy, neutral
            'info': 1        # info display background
        }
        
        # Expected file patterns
        self.file_patterns = {
            'indicators': ['hex_selection_01.png', 'hex_highlight_01.png'],
            'resources': ['resource_gold_01.png', 'resource_wood_01.png', 
                         'resource_stone_01.png', 'resource_food_01.png'],
            'status': [f'status_{status}_{percentage:03d}.png' 
                      for status in ['health', 'mana', 'stamina', 'shield']
                      for percentage in [100, 75, 50, 25]],
            'territory': ['territory_player_01.png', 'territory_ally_01.png',
                         'territory_enemy_01.png', 'territory_neutral_01.png'],
            'info': ['info_display_01.png']
        }

    def test_directory_structure(self):
        """Test that all required directories exist"""
        for dir_name in self.sizes.keys():
            dir_path = os.path.join(self.base_dir, dir_name)
            self.assertTrue(os.path.exists(dir_path),
                          f"Directory {dir_path} does not exist")

    def test_file_counts(self):
        """Test that the correct number of files are generated"""
        for dir_name, expected_count in self.expected_counts.items():
            dir_path = os.path.join(self.base_dir, dir_name)
            files = [f for f in os.listdir(dir_path) if f.endswith('.png')]
            self.assertEqual(len(files), expected_count,
                           f"Expected {expected_count} files in {dir_name}, found {len(files)}")

    def test_file_names(self):
        """Test that all expected files exist with correct names"""
        for dir_name, patterns in self.file_patterns.items():
            dir_path = os.path.join(self.base_dir, dir_name)
            for pattern in patterns:
                file_path = os.path.join(dir_path, pattern)
                self.assertTrue(os.path.exists(file_path),
                              f"File {file_path} does not exist")

    def test_image_sizes(self):
        """Test that all images have the correct dimensions"""
        for dir_name, (expected_width, expected_height) in self.sizes.items():
            dir_path = os.path.join(self.base_dir, dir_name)
            for file_name in os.listdir(dir_path):
                if file_name.endswith('.png'):
                    file_path = os.path.join(dir_path, file_name)
                    with Image.open(file_path) as img:
                        width, height = img.size
                        self.assertEqual((width, height), (expected_width, expected_height),
                                      f"Wrong size for {file_path}. Expected {(expected_width, expected_height)}, got {(width, height)}")

    def test_image_transparency(self):
        """Test that all images have an alpha channel"""
        for dir_name in self.sizes.keys():
            dir_path = os.path.join(self.base_dir, dir_name)
            for file_name in os.listdir(dir_path):
                if file_name.endswith('.png'):
                    file_path = os.path.join(dir_path, file_name)
                    with Image.open(file_path) as img:
                        self.assertEqual(img.mode, 'RGBA',
                                      f"Image {file_path} should have RGBA mode")

    def test_status_indicator_percentages(self):
        """Test that status indicators have correct percentage variations"""
        status_dir = os.path.join(self.base_dir, 'status')
        expected_percentages = [100, 75, 50, 25]
        status_types = ['health', 'mana', 'stamina', 'shield']
        
        for status in status_types:
            for percentage in expected_percentages:
                file_name = f'status_{status}_{percentage:03d}.png'
                file_path = os.path.join(status_dir, file_name)
                self.assertTrue(os.path.exists(file_path),
                              f"Status indicator {file_path} does not exist")

if __name__ == '__main__':
    unittest.main() 