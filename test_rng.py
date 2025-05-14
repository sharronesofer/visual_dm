"""
Simplified test for DeterministicRNG
"""
import unittest
import sys
import os
import math
import statistics
from collections import Counter

# Get the absolute path to the directory containing this script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the project root to the Python path
sys.path.insert(0, current_dir)

# Now we can import our module
from python_converted.src.worldgen.core.simple_test import DeterministicRNG, ISeedConfig

class TestDeterministicRNG(unittest.TestCase):
    def setUp(self):
        self.seed = 12345
        self.seed_config = ISeedConfig(seed=self.seed, name="test_seed")
        self.rng = DeterministicRNG(self.seed_config)
    
    def test_uniform(self):
        """Test uniform distribution method"""
        # Test normal usage
        value = self.rng.uniform(10.0, 20.0)
        self.assertGreaterEqual(value, 10.0)
        self.assertLessEqual(value, 20.0)
        
        # Test equal bounds
        value = self.rng.uniform(15.0, 15.0)
        self.assertEqual(value, 15.0)
        
        # Test validation
        with self.assertRaises(ValueError):
            self.rng.uniform(20.0, 10.0)  # min > max
    
    def test_randint(self):
        """Test integer range method"""
        # Test normal usage
        value = self.rng.randint(10, 20)
        self.assertIsInstance(value, int)
        self.assertGreaterEqual(value, 10)
        self.assertLessEqual(value, 20)
        
        # Test equal bounds
        value = self.rng.randint(15, 15)
        self.assertEqual(value, 15)
        
        # Test validation
        with self.assertRaises(ValueError):
            self.rng.randint(20, 10)  # min > max
        
        with self.assertRaises(TypeError):
            self.rng.randint(10.5, 20)  # non-integer min
        
        with self.assertRaises(TypeError):
            self.rng.randint(10, 20.5)  # non-integer max
    
    def test_normal(self):
        """Test normal distribution method"""
        # Test normal usage with default parameters
        value = self.rng.normal()
        self.assertIsInstance(value, float)
        
        # Test with custom parameters
        mean, std_dev = 10.0, 2.0
        values = [self.rng.normal(mean, std_dev) for _ in range(1000)]
        
        # Calculate actual mean and std_dev
        actual_mean = statistics.mean(values)
        actual_std_dev = statistics.stdev(values)
        
        # Check they are close to expected values (within 10%)
        self.assertAlmostEqual(actual_mean, mean, delta=mean * 0.1)
        self.assertAlmostEqual(actual_std_dev, std_dev, delta=std_dev * 0.1)
        
        # Test with zero std_dev
        value = self.rng.normal(5.0, 0.0)
        self.assertEqual(value, 5.0)
        
        # Test validation
        with self.assertRaises(ValueError):
            self.rng.normal(0.0, -1.0)  # negative std_dev
    
    def test_boolean(self):
        """Test boolean generation method"""
        # Test default parameter (p=0.5)
        value = self.rng.boolean()
        self.assertIsInstance(value, bool)
        
        # Test with custom probability
        # For p=0.7, approximately 70% of values should be True
        values = [self.rng.boolean(0.7) for _ in range(1000)]
        true_count = sum(1 for v in values if v)
        true_ratio = true_count / len(values)
        
        # Check ratio is close to expected (within 10%)
        self.assertAlmostEqual(true_ratio, 0.7, delta=0.07)
        
        # Test edge cases
        self.assertTrue(self.rng.boolean(1.0))
        self.assertFalse(self.rng.boolean(0.0))
        
        # Test validation
        with self.assertRaises(ValueError):
            self.rng.boolean(-0.1)  # p < 0
        
        with self.assertRaises(ValueError):
            self.rng.boolean(1.1)  # p > 1
    
    def test_determinism(self):
        """Test deterministic behavior"""
        # Generate sequences with uniform
        self.rng.reset()
        values1 = [self.rng.uniform(10.0, 20.0) for _ in range(5)]
        
        self.rng.reset()
        values2 = [self.rng.uniform(10.0, 20.0) for _ in range(5)]
        
        self.assertEqual(values1, values2)
        
        # Generate sequences with randint
        self.rng.reset()
        values1 = [self.rng.randint(1, 100) for _ in range(5)]
        
        self.rng.reset()
        values2 = [self.rng.randint(1, 100) for _ in range(5)]
        
        self.assertEqual(values1, values2)
        
        # Generate sequences with normal
        self.rng.reset()
        values1 = [self.rng.normal(10.0, 2.0) for _ in range(5)]
        
        self.rng.reset()
        values2 = [self.rng.normal(10.0, 2.0) for _ in range(5)]
        
        self.assertEqual(values1, values2)
        
        # Generate sequences with boolean
        self.rng.reset()
        values1 = [self.rng.boolean(0.7) for _ in range(10)]
        
        self.rng.reset()
        values2 = [self.rng.boolean(0.7) for _ in range(10)]
        
        self.assertEqual(values1, values2)

if __name__ == '__main__':
    unittest.main() 