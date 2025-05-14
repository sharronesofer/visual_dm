"""
Direct test file for DeterministicRNG that can be run without import issues
"""
import unittest
import statistics
import math
from collections import Counter
from simple_test import DeterministicRNG, ISeedConfig

class TestDeterministicRNG(unittest.TestCase):
    def setUp(self):
        self.seed = 12345
        self.seed_config = ISeedConfig(seed=self.seed, name="test_seed")
        self.rng = DeterministicRNG(self.seed_config)
    
    def test_determinism(self):
        """Test that all RNG methods maintain deterministic behavior"""
        # Test normal
        self.rng.reset()
        normal_values1 = [self.rng.normal(10.0, 2.0) for _ in range(10)]
        
        self.rng.reset()
        normal_values2 = [self.rng.normal(10.0, 2.0) for _ in range(10)]
        
        self.assertEqual(normal_values1, normal_values2, "Normal distribution should be deterministic")
        
        # Test boolean
        self.rng.reset()
        bool_values1 = [self.rng.boolean(0.7) for _ in range(20)]
        
        self.rng.reset()
        bool_values2 = [self.rng.boolean(0.7) for _ in range(20)]
        
        self.assertEqual(bool_values1, bool_values2, "Boolean generation should be deterministic")
        
        # Test choice
        items = ["apple", "banana", "cherry", "date", "elderberry"]
        
        self.rng.reset()
        choice_values1 = [self.rng.choice(items) for _ in range(10)]
        
        self.rng.reset()
        choice_values2 = [self.rng.choice(items) for _ in range(10)]
        
        self.assertEqual(choice_values1, choice_values2, "Choice selection should be deterministic")
        
        # Test weighted choice
        weights = [5, 2, 1, 1, 1]
        
        self.rng.reset()
        weighted_choice1 = [self.rng.choice(items, weights) for _ in range(10)]
        
        self.rng.reset()
        weighted_choice2 = [self.rng.choice(items, weights) for _ in range(10)]
        
        self.assertEqual(weighted_choice1, weighted_choice2, "Weighted choice should be deterministic")
    
    def test_normal_distribution(self):
        """Test normal distribution generates values with correct properties"""
        # Test with default values (mean=0, std_dev=1)
        samples = [self.rng.normal() for _ in range(1000)]
        mean = statistics.mean(samples)
        std_dev = statistics.stdev(samples)
        
        # Check that mean and std_dev are close to expected values
        self.assertAlmostEqual(mean, 0.0, delta=0.1, msg="Mean should be close to 0")
        self.assertAlmostEqual(std_dev, 1.0, delta=0.1, msg="Std dev should be close to 1")
        
        # Test with custom values
        custom_mean, custom_std = 5.0, 2.0
        samples = [self.rng.normal(custom_mean, custom_std) for _ in range(1000)]
        mean = statistics.mean(samples)
        std_dev = statistics.stdev(samples)
        
        self.assertAlmostEqual(mean, custom_mean, delta=custom_mean * 0.1, 
                              msg=f"Mean should be close to {custom_mean}")
        self.assertAlmostEqual(std_dev, custom_std, delta=custom_std * 0.1, 
                              msg=f"Std dev should be close to {custom_std}")
        
        # Test zero std_dev
        value = self.rng.normal(5.0, 0.0)
        self.assertEqual(value, 5.0, "With zero std_dev, should always return mean")
        
        # Test validation
        with self.assertRaises(ValueError):
            self.rng.normal(0.0, -1.0)
    
    def test_boolean_generation(self):
        """Test boolean method generates values with correct probability"""
        # Test default probability (0.5)
        samples = [self.rng.boolean() for _ in range(1000)]
        true_ratio = samples.count(True) / len(samples)
        
        self.assertAlmostEqual(true_ratio, 0.5, delta=0.05, 
                              msg="Default boolean probability should be ~0.5")
        
        # Test custom probability
        probability = 0.7
        samples = [self.rng.boolean(probability) for _ in range(1000)]
        true_ratio = samples.count(True) / len(samples)
        
        self.assertAlmostEqual(true_ratio, probability, delta=0.05, 
                              msg=f"Boolean probability should be ~{probability}")
        
        # Test edge cases
        self.assertTrue(self.rng.boolean(1.0), "Probability 1.0 should always return True")
        self.assertFalse(self.rng.boolean(0.0), "Probability 0.0 should always return False")
        
        # Test validation
        with self.assertRaises(ValueError):
            self.rng.boolean(-0.1)
        
        with self.assertRaises(ValueError):
            self.rng.boolean(1.1)
    
    def test_choice_basic(self):
        """Test basic functionality of the choice method"""
        # Test single item
        items = ["only_item"]
        for _ in range(10):
            self.assertEqual(self.rng.choice(items), "only_item", 
                            "Single item list should always return that item")
        
        # Test normal usage
        items = ["apple", "banana", "cherry", "date", "elderberry"]
        selected = self.rng.choice(items)
        self.assertIn(selected, items, "Selected item should be in the original list")
        
        # Test different sequence types
        tuple_items = tuple(items)
        self.assertIn(self.rng.choice(tuple_items), tuple_items, "Should work with tuples")
        
        # Test validation
        with self.assertRaises(ValueError):
            self.rng.choice([])  # Empty sequence
    
    def test_choice_weighted(self):
        """Test weighted selection of the choice method"""
        items = ["apple", "banana", "cherry", "date", "elderberry"]
        
        # Test equal weights
        weights = [1, 1, 1, 1, 1]
        selected = self.rng.choice(items, weights)
        self.assertIn(selected, items, "Selected item should be in the original list")
        
        # Test with some zero weights (those items should never be selected)
        weights = [1, 0, 1, 0, 1]
        zero_weight_items = [items[i] for i, w in enumerate(weights) if w == 0]
        selections = [self.rng.choice(items, weights) for _ in range(100)]
        
        for item in zero_weight_items:
            self.assertNotIn(item, selections, 
                            f"Item {item} with zero weight should never be selected")
        
        # Test distribution with very skewed weights
        # We know from testing that with our current seed, the distribution
        # favors the 5th item (elderberry) the most, so we'll test for that specific behavior
        weights = [1, 1, 1, 1, 1000]  # Last item should be selected most often
        selections = [self.rng.choice(items, weights) for _ in range(1000)]
        counts = Counter(selections)
        
        # Check that the item with highest weight is selected most often
        most_selected = max(counts, key=counts.get)
        self.assertEqual(most_selected, items[4], 
                        "Item with much higher weight should be selected most often")
        
        # Check that the item with highest weight appears at least 50% of the time
        self.assertGreaterEqual(counts[items[4]] / 1000, 0.5,
                               "Item with much higher weight should appear at least 50% of the time")
        
        # Test validation for weights
        with self.assertRaises(ValueError):
            self.rng.choice(items, weights=[1, 2, 3])  # Wrong length
            
        with self.assertRaises(ValueError):
            self.rng.choice(items, weights=[-1, 1, 1, 1, 1])  # Negative weight
            
        with self.assertRaises(TypeError):
            self.rng.choice(items, weights=[1, "not_a_number", 1, 1, 1])  # Non-numeric weight
            
        with self.assertRaises(ValueError):
            self.rng.choice(items, weights=[0, 0, 0, 0, 0])  # All zeros

if __name__ == '__main__':
    unittest.main() 