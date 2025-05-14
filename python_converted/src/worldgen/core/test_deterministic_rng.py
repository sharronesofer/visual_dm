"""
Unit tests for the DeterministicRNG class
"""
import unittest
import statistics
from collections import Counter
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from python_converted.src.worldgen.core.simple_test import DeterministicRNG, ISeedConfig

class TestDeterministicRNG(unittest.TestCase):
    """Test cases for DeterministicRNG class"""
    
    def setUp(self):
        """Set up test cases"""
        self.seed = 12345
        self.seed_config = ISeedConfig(seed=self.seed, name="test_seed")
        self.rng = DeterministicRNG(self.seed_config)
    
    def test_determinism(self):
        """Test that the RNG produces the same sequence with the same seed"""
        # Generate a sequence of random numbers
        numbers1 = [self.rng.random() for _ in range(100)]
        
        # Reset the RNG
        self.rng.reset()
        
        # Generate another sequence
        numbers2 = [self.rng.random() for _ in range(100)]
        
        # Check they are identical
        self.assertEqual(numbers1, numbers2)
        
        # Create a new RNG with the same seed
        rng2 = DeterministicRNG(ISeedConfig(seed=self.seed))
        
        # Generate a sequence
        numbers3 = [rng2.random() for _ in range(100)]
        
        # Check it's identical to the first one
        self.assertEqual(numbers1, numbers3)
    
    def test_different_seeds(self):
        """Test that different seeds produce different sequences"""
        # Create a second RNG with a different seed
        rng2 = DeterministicRNG(ISeedConfig(seed=54321))
        
        # Generate sequences
        numbers1 = [self.rng.random() for _ in range(100)]
        numbers2 = [rng2.random() for _ in range(100)]
        
        # They should be different
        self.assertNotEqual(numbers1, numbers2)
    
    def test_random_range(self):
        """Test that random() generates values in [0,1)"""
        # Generate many random values
        values = [self.rng.random() for _ in range(1000)]
        
        # Check all values are in range [0,1)
        for value in values:
            self.assertGreaterEqual(value, 0.0)
            self.assertLess(value, 1.0)
    
    def test_uniform_values(self):
        """Test uniform() generates values in specified range"""
        min_val, max_val = 10.0, 20.0
        
        # Generate many values
        values = [self.rng.uniform(min_val, max_val) for _ in range(1000)]
        
        # Check all values are in range [min_val, max_val]
        for value in values:
            self.assertGreaterEqual(value, min_val)
            self.assertLessEqual(value, max_val)
        
        # Check distribution (not perfect but should be roughly uniform)
        # Split range into 10 bins and count values in each bin
        bin_size = (max_val - min_val) / 10
        bins = [0] * 10
        
        for value in values:
            bin_idx = min(9, int((value - min_val) / bin_size))
            bins[bin_idx] += 1
        
        # Each bin should have roughly the same number of values (within a reasonable margin)
        expected_count = 1000 / 10
        for count in bins:
            # Allow for some variation (within 30% of expected)
            self.assertGreaterEqual(count, expected_count * 0.7)
            self.assertLessEqual(count, expected_count * 1.3)
    
    def test_uniform_equal_bounds(self):
        """Test uniform() with min=max returns the value"""
        value = self.rng.uniform(15.0, 15.0)
        self.assertEqual(value, 15.0)
    
    def test_uniform_validation(self):
        """Test uniform() validates inputs correctly"""
        with self.assertRaises(ValueError):
            self.rng.uniform(20.0, 10.0)  # min > max
    
    def test_randint_values(self):
        """Test randint() generates integers in specified range"""
        min_val, max_val = 10, 20
        
        # Generate many values
        values = [self.rng.randint(min_val, max_val) for _ in range(1000)]
        
        # Check all values are integers in range [min_val, max_val]
        for value in values:
            self.assertIsInstance(value, int)
            self.assertGreaterEqual(value, min_val)
            self.assertLessEqual(value, max_val)
        
        # Check we get all possible values in the range
        unique_values = set(values)
        expected_values = set(range(min_val, max_val + 1))
        self.assertEqual(unique_values, expected_values)
        
        # Check distribution (should be roughly uniform)
        counter = Counter(values)
        expected_count = 1000 / (max_val - min_val + 1)
        
        for value in range(min_val, max_val + 1):
            count = counter[value]
            # Allow for some variation (within 30% of expected)
            self.assertGreaterEqual(count, expected_count * 0.7)
            self.assertLessEqual(count, expected_count * 1.3)
    
    def test_randint_equal_bounds(self):
        """Test randint() with min=max returns the value"""
        value = self.rng.randint(15, 15)
        self.assertEqual(value, 15)
    
    def test_randint_validation(self):
        """Test randint() validates inputs correctly"""
        with self.assertRaises(ValueError):
            self.rng.randint(20, 10)  # min > max
        
        with self.assertRaises(TypeError):
            self.rng.randint(10.5, 20)  # non-integer min
        
        with self.assertRaises(TypeError):
            self.rng.randint(10, 20.5)  # non-integer max
    
    def test_uniform_determinism(self):
        """Test that uniform() is deterministic"""
        # Generate a sequence
        self.rng.reset()
        values1 = [self.rng.uniform(10.0, 20.0) for _ in range(100)]
        
        # Reset and generate again
        self.rng.reset()
        values2 = [self.rng.uniform(10.0, 20.0) for _ in range(100)]
        
        # Check they match
        self.assertEqual(values1, values2)
    
    def test_randint_determinism(self):
        """Test that randint() is deterministic"""
        # Generate a sequence
        self.rng.reset()
        values1 = [self.rng.randint(1, 1000) for _ in range(100)]
        
        # Reset and generate again
        self.rng.reset()
        values2 = [self.rng.randint(1, 1000) for _ in range(100)]
        
        # Check they match
        self.assertEqual(values1, values2)

if __name__ == '__main__':
    unittest.main() 