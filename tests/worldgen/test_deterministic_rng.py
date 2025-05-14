"""
Tests for the DeterministicRNG class in the WorldGen system.

This module contains comprehensive tests for the DeterministicRNG class, verifying its
functionality, deterministic behavior, statistical properties, and integration with
the broader WorldGen system.
"""
import os
import sys
import math
import pytest
import numpy as np
from scipy import stats
from collections import Counter

# Add the project root to the Python path if needed
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the DeterministicRNG class
from python_converted.src.worldgen.core.simple_test import DeterministicRNG, ISeedConfig


# Fixtures for common test setup
@pytest.fixture
def seed_value():
    """Provides a consistent seed value for tests."""
    return 12345


@pytest.fixture
def seed_config(seed_value):
    """Creates a seed configuration with the test seed."""
    return ISeedConfig(seed=seed_value, name="test_seed")


@pytest.fixture
def rng(seed_config):
    """Creates a DeterministicRNG instance with the test seed configuration."""
    return DeterministicRNG(seed_config)


class TestDeterministicRNG:
    """Test suite for the DeterministicRNG class."""

    def test_initialization(self, seed_value, seed_config, rng):
        """Test initialization and seed configuration."""
        assert rng.seed_config == seed_config
        assert rng.seed_config.seed == seed_value
        assert rng.seed_config.name == "test_seed"
        
        # Test with different seed values
        rng1 = DeterministicRNG(ISeedConfig(seed=1))
        rng2 = DeterministicRNG(ISeedConfig(seed=2))
        
        # Different seeds should produce different sequences
        assert rng1.random() != rng2.random()
        
        # Test initialization with zero seed (should be handled)
        rng0 = DeterministicRNG(ISeedConfig(seed=0))
        assert rng0.random() >= 0.0  # Just ensure it doesn't crash


    def test_reset(self, rng):
        """Test the reset method returns the RNG to its initial state."""
        # Generate a sequence of random numbers
        original_values = [rng.random() for _ in range(10)]
        
        # Reset the RNG
        rng.reset()
        
        # Generate another sequence of random numbers
        reset_values = [rng.random() for _ in range(10)]
        
        # The two sequences should be identical
        assert original_values == reset_values


    def test_random(self, rng):
        """Test the random method generates values in the range [0, 1)."""
        # Generate a large sample
        samples = [rng.random() for _ in range(1000)]
        
        # All values should be in range [0, 1)
        assert all(0 <= value < 1 for value in samples)
        
        # Test determinism
        rng.reset()
        samples2 = [rng.random() for _ in range(1000)]
        assert samples == samples2
        
        # Test distribution (should be roughly uniform)
        # Divide [0,1) into 10 bins and count values in each bin
        bins = [0] * 10
        for value in samples:
            bin_index = min(int(value * 10), 9)  # Handles edge case of value=1.0
            bins[bin_index] += 1
        
        # Chi-square test for uniform distribution
        # Expected count for a uniform distribution in each bin
        expected_count = len(samples) / 10
        chi2, p_value = stats.chisquare(bins, [expected_count] * 10)
        
        # For a uniform distribution, p_value should be high (> 0.05)
        assert p_value > 0.05, f"Chi-square test failed for random() with p-value {p_value}"


    def test_uniform(self, rng):
        """Test the uniform method generates values in the specified range."""
        # Test with positive range
        min_val, max_val = 10.0, 20.0
        samples = [rng.uniform(min_val, max_val) for _ in range(1000)]
        
        # All values should be in range [min_val, max_val]
        assert all(min_val <= value <= max_val for value in samples)
        
        # Test with negative range
        min_val, max_val = -20.0, -10.0
        samples = [rng.uniform(min_val, max_val) for _ in range(1000)]
        assert all(min_val <= value <= max_val for value in samples)
        
        # Test with range spanning zero
        min_val, max_val = -10.0, 10.0
        samples = [rng.uniform(min_val, max_val) for _ in range(1000)]
        assert all(min_val <= value <= max_val for value in samples)
        
        # Test equal bounds
        value = rng.uniform(15.0, 15.0)
        assert value == 15.0
        
        # Test edge cases
        with pytest.raises(ValueError):
            rng.uniform(20.0, 10.0)  # min > max
            
        # Test distribution (should be approximately uniform)
        min_val, max_val = 0.0, 10.0
        samples = [rng.uniform(min_val, max_val) for _ in range(1000)]
        
        # Divide [min_val, max_val) into 10 bins and count values in each bin
        bins = [0] * 10
        bin_width = (max_val - min_val) / 10
        for value in samples:
            bin_index = min(int((value - min_val) / bin_width), 9)
            bins[bin_index] += 1
        
        # Chi-square test for uniform distribution
        expected_count = len(samples) / 10
        chi2, p_value = stats.chisquare(bins, [expected_count] * 10)
        
        # For a uniform distribution, p_value should be high (> 0.05)
        assert p_value > 0.05, f"Chi-square test failed for uniform() with p-value {p_value}"
        
        # Kolmogorov-Smirnov test
        # Create a uniform distribution with the same range
        uniform_dist = stats.uniform(min_val, max_val - min_val)
        
        # Run KS test
        ks_stat, ks_p_value = stats.kstest(samples, uniform_dist.cdf)
        
        # For a good match, p_value should be high (> 0.05)
        assert ks_p_value > 0.05, f"KS test failed for uniform() with p-value {ks_p_value}"
        
        # Test determinism
        rng.reset()
        original_values = [rng.uniform(min_val, max_val) for _ in range(10)]
        rng.reset()
        reset_values = [rng.uniform(min_val, max_val) for _ in range(10)]
        assert original_values == reset_values


    def test_randint(self, rng):
        """Test the randint method generates integers in the specified range."""
        # Test with positive range
        min_val, max_val = 10, 20
        samples = [rng.randint(min_val, max_val) for _ in range(1000)]
        
        # All values should be in range [min_val, max_val] and be integers
        assert all(min_val <= value <= max_val for value in samples)
        assert all(isinstance(value, int) for value in samples)
        
        # Test with negative range
        min_val, max_val = -20, -10
        samples = [rng.randint(min_val, max_val) for _ in range(1000)]
        assert all(min_val <= value <= max_val for value in samples)
        
        # Test with range spanning zero
        min_val, max_val = -10, 10
        samples = [rng.randint(min_val, max_val) for _ in range(1000)]
        assert all(min_val <= value <= max_val for value in samples)
        
        # Test equal bounds
        value = rng.randint(15, 15)
        assert value == 15
        
        # Test edge cases
        with pytest.raises(ValueError):
            rng.randint(20, 10)  # min > max
            
        with pytest.raises(TypeError):
            rng.randint(10.5, 20)  # non-integer min
            
        with pytest.raises(TypeError):
            rng.randint(10, 20.5)  # non-integer max
            
        # Test distribution (should be approximately uniform)
        min_val, max_val = 1, 10
        samples = [rng.randint(min_val, max_val) for _ in range(1000)]
        
        # Count occurrences of each value
        counter = Counter(samples)
        
        # Each value should occur approximately equally
        expected_count = len(samples) / (max_val - min_val + 1)
        
        # Chi-square test
        observed = [counter[i] for i in range(min_val, max_val + 1)]
        expected = [expected_count] * (max_val - min_val + 1)
        chi2, p_value = stats.chisquare(observed, expected)
        
        # For a uniform distribution, p_value should be high (> 0.05)
        assert p_value > 0.05, f"Chi-square test failed for randint() with p-value {p_value}"
        
        # Test determinism
        rng.reset()
        original_values = [rng.randint(min_val, max_val) for _ in range(10)]
        rng.reset()
        reset_values = [rng.randint(min_val, max_val) for _ in range(10)]
        assert original_values == reset_values


    def test_normal(self, rng):
        """Test the normal method generates values from a normal distribution."""
        # Test with default parameters (mean=0, std_dev=1)
        samples = [rng.normal() for _ in range(1000)]
        
        # Calculate sample statistics
        sample_mean = np.mean(samples)
        sample_std = np.std(samples, ddof=1)  # Using sample standard deviation
        
        # For a large enough sample, statistics should be close to the expected values
        assert abs(sample_mean) < 0.1, f"Expected mean close to 0, got {sample_mean}"
        assert abs(sample_std - 1.0) < 0.1, f"Expected std_dev close to 1, got {sample_std}"
        
        # Test with custom parameters
        mean, std_dev = 10.0, 2.0
        samples = [rng.normal(mean, std_dev) for _ in range(1000)]
        
        # Calculate sample statistics
        sample_mean = np.mean(samples)
        sample_std = np.std(samples, ddof=1)
        
        # For a large enough sample, statistics should be close to the expected values
        assert abs(sample_mean - mean) < mean * 0.1, f"Expected mean close to {mean}, got {sample_mean}"
        assert abs(sample_std - std_dev) < std_dev * 0.1, f"Expected std_dev close to {std_dev}, got {sample_std}"
        
        # Test zero std_dev
        value = rng.normal(5.0, 0.0)
        assert value == 5.0
        
        # Test negative std_dev
        with pytest.raises(ValueError):
            rng.normal(0.0, -1.0)
            
        # Test the distribution shape using Kolmogorov-Smirnov test
        mean, std_dev = 0.0, 1.0
        samples = [rng.normal(mean, std_dev) for _ in range(1000)]
        
        # Create a normal distribution with the same parameters
        normal_dist = stats.norm(mean, std_dev)
        
        # Run KS test
        ks_stat, p_value = stats.kstest(samples, normal_dist.cdf)
        
        # For a good match, p_value should be high (> 0.05)
        assert p_value > 0.05, f"KS test failed for normal() with p-value {p_value}"
        
        # Test determinism
        rng.reset()
        original_values = [rng.normal(mean, std_dev) for _ in range(10)]
        rng.reset()
        reset_values = [rng.normal(mean, std_dev) for _ in range(10)]
        assert original_values == reset_values


    def test_boolean(self, rng):
        """Test the boolean method generates values according to the specified probability."""
        # Test with default probability (0.5)
        samples = [rng.boolean() for _ in range(1000)]
        true_count = sum(samples)
        true_ratio = true_count / len(samples)
        
        # Should be approximately 0.5
        assert abs(true_ratio - 0.5) < 0.05, f"Expected ratio close to 0.5, got {true_ratio}"
        
        # Test with custom probability
        probability = 0.7
        samples = [rng.boolean(probability) for _ in range(1000)]
        true_count = sum(samples)
        true_ratio = true_count / len(samples)
        
        # Should be approximately equal to the specified probability
        assert abs(true_ratio - probability) < 0.05, f"Expected ratio close to {probability}, got {true_ratio}"
        
        # Test edge cases
        assert rng.boolean(1.0) is True
        assert rng.boolean(0.0) is False
        
        # Test invalid probabilities
        with pytest.raises(ValueError):
            rng.boolean(-0.1)  # p < 0
            
        with pytest.raises(ValueError):
            rng.boolean(1.1)  # p > 1
            
        # Test distribution using binomial test
        probability = 0.3
        samples = [rng.boolean(probability) for _ in range(1000)]
        true_count = sum(samples)
        
        # Binomial test against expected probability
        p_value = stats.binom_test(true_count, n=len(samples), p=probability)
        
        # For a good match, p_value should be high (> 0.05)
        assert p_value > 0.05, f"Binomial test failed for boolean() with p-value {p_value}"
        
        # Test determinism
        rng.reset()
        original_values = [rng.boolean(probability) for _ in range(10)]
        rng.reset()
        reset_values = [rng.boolean(probability) for _ in range(10)]
        assert original_values == reset_values


    def test_choice(self, rng):
        """Test the choice method selects items from a sequence according to specified weights."""
        # Test with uniform selection (no weights)
        items = ["apple", "banana", "cherry", "date", "elderberry"]
        samples = [rng.choice(items) for _ in range(1000)]
        
        # Count occurrences of each item
        counter = Counter(samples)
        
        # Each item should occur approximately equally
        expected_count = len(samples) / len(items)
        for item in items:
            count = counter[item]
            assert abs(count - expected_count) < expected_count * 0.2, f"Expected {item} count close to {expected_count}, got {count}"
        
        # Test with weighted selection
        weights = [5, 2, 1, 1, 1]  # 5:2:1:1:1 ratio
        samples = [rng.choice(items, weights) for _ in range(1000)]
        counter = Counter(samples)
        
        # Calculate expected counts based on weights
        total_weight = sum(weights)
        expected_counts = {item: (weight / total_weight) * len(samples) for item, weight in zip(items, weights)}
        
        # Check counts are approximately equal to expected
        for item in items:
            count = counter[item]
            expected = expected_counts[item]
            assert abs(count - expected) < expected * 0.2, f"Expected {item} count close to {expected}, got {count}"
        
        # Test with single-item sequence
        single_item = ["only_option"]
        assert rng.choice(single_item) == "only_option"
        
        # Test with empty sequence
        with pytest.raises(ValueError):
            rng.choice([])
            
        # Test with invalid weights
        with pytest.raises(ValueError):
            rng.choice(items, weights=[-1, 1, 1, 1, 1])  # Negative weight
            
        with pytest.raises(ValueError):
            rng.choice(items, weights=[0, 0, 0, 0, 0])  # All zeros
            
        with pytest.raises(ValueError):
            rng.choice(items, weights=[1, 1, 1])  # Wrong length
            
        with pytest.raises(TypeError):
            rng.choice(items, weights=[1, 1, "a", 1, 1])  # Non-numeric weight
            
        # Test different sequence types
        assert isinstance(rng.choice(("tuple", "example")), str)
        
        # Test determinism
        rng.reset()
        original_values = [rng.choice(items, weights) for _ in range(10)]
        rng.reset()
        reset_values = [rng.choice(items, weights) for _ in range(10)]
        assert original_values == reset_values


    def test_different_seeds(self):
        """Test that different seeds produce different sequences."""
        rng1 = DeterministicRNG(ISeedConfig(seed=1))
        rng2 = DeterministicRNG(ISeedConfig(seed=2))
        
        # Generate sequences
        seq1 = [rng1.random() for _ in range(10)]
        seq2 = [rng2.random() for _ in range(10)]
        
        # Sequences should be different
        assert seq1 != seq2
        
        # But each sequence should be deterministic with its own seed
        rng1.reset()
        seq1_reset = [rng1.random() for _ in range(10)]
        assert seq1 == seq1_reset
        
        rng2.reset()
        seq2_reset = [rng2.random() for _ in range(10)]
        assert seq2 == seq2_reset


    def test_seed_hierarchy(self):
        """Test seed hierarchy functionality."""
        parent_seed = ISeedConfig(seed=12345, name="parent")
        child_seed = ISeedConfig(seed=67890, name="child", parent=parent_seed)
        
        assert child_seed.parent == parent_seed
        
        # Create RNGs using the hierarchical seeds
        parent_rng = DeterministicRNG(parent_seed)
        child_rng = DeterministicRNG(child_seed)
        
        # Each should generate its own deterministic sequence
        parent_seq = [parent_rng.random() for _ in range(5)]
        child_seq = [child_rng.random() for _ in range(5)]
        
        # Sequences should be different
        assert parent_seq != child_seq
        
        # But each should be deterministic with its own seed
        parent_rng.reset()
        parent_seq_reset = [parent_rng.random() for _ in range(5)]
        assert parent_seq == parent_seq_reset
        
        child_rng.reset()
        child_seq_reset = [child_rng.random() for _ in range(5)]
        assert child_seq == child_seq_reset


    def test_edge_cases(self, rng):
        """Test various edge cases and error conditions."""
        # Already tested many edge cases in individual method tests
        # This test focuses on additional edge cases
        
        # Test with very large range in randint
        large_min = 2**30
        large_max = 2**30 + 100
        values = [rng.randint(large_min, large_max) for _ in range(100)]
        assert all(large_min <= v <= large_max for v in values)
        
        # Test with very small probabilities in boolean
        small_p = 0.001
        # With such a small probability, most values should be False
        values = [rng.boolean(small_p) for _ in range(1000)]
        true_count = sum(values)
        assert true_count < 10  # Should be around 1, but allow some variance
        
        # Test with very large standard deviations in normal
        large_std = 1000.0
        values = [rng.normal(0, large_std) for _ in range(100)]
        # Hard to make specific assertions here, but at least ensure it runs
        assert len(values) == 100
        
        # Test with equal weights in choice
        items = ["a", "b", "c"]
        weights = [1, 1, 1]
        counter = Counter([rng.choice(items, weights) for _ in range(300)])
        # Each should appear approximately equally
        for item in items:
            assert 70 <= counter[item] <= 130  # Allow for some variance


    def test_reproducibility_across_instances(self, seed_value):
        """Test that different instances with the same seed produce the same sequences."""
        rng1 = DeterministicRNG(ISeedConfig(seed=seed_value))
        rng2 = DeterministicRNG(ISeedConfig(seed=seed_value))
        
        # Generate sequences from different methods
        seq1_random = [rng1.random() for _ in range(5)]
        seq1_uniform = [rng1.uniform(0, 10) for _ in range(5)]
        seq1_randint = [rng1.randint(1, 100) for _ in range(5)]
        seq1_normal = [rng1.normal(10, 2) for _ in range(5)]
        seq1_boolean = [rng1.boolean(0.7) for _ in range(5)]
        seq1_choice = [rng1.choice(["a", "b", "c"]) for _ in range(5)]
        
        seq2_random = [rng2.random() for _ in range(5)]
        seq2_uniform = [rng2.uniform(0, 10) for _ in range(5)]
        seq2_randint = [rng2.randint(1, 100) for _ in range(5)]
        seq2_normal = [rng2.normal(10, 2) for _ in range(5)]
        seq2_boolean = [rng2.boolean(0.7) for _ in range(5)]
        seq2_choice = [rng2.choice(["a", "b", "c"]) for _ in range(5)]
        
        # All sequences should match
        assert seq1_random == seq2_random
        assert seq1_uniform == seq2_uniform
        assert seq1_randint == seq2_randint
        assert seq1_normal == seq2_normal
        assert seq1_boolean == seq2_boolean
        assert seq1_choice == seq2_choice


    def test_known_values(self, seed_value):
        """Test against known good values for regression testing."""
        rng = DeterministicRNG(ISeedConfig(seed=seed_value))
        
        # Generate a random value and save it as a known good value
        known_random = rng.random()
        rng.reset()
        
        # Now test against the known value
        assert rng.random() == known_random
        
        # Can repeat this pattern for other methods as needed during development
        # For now, we'll just verify that reset works correctly


    def test_integration(self, seed_value):
        """Test integration with the WorldGen system components."""
        # For this test, we need to identify key WorldGen components that use the RNG
        # and verify they continue to function correctly with the enhanced implementation.
        # Since we don't have direct access to those components in this test context,
        # we'll simulate integration by creating a simple world generation function
        
        def generate_simple_terrain(rng, width, height):
            """Simulate terrain generation using the RNG."""
            terrain = []
            for y in range(height):
                row = []
                for x in range(width):
                    # Use various RNG methods to generate terrain features
                    elevation = rng.uniform(0, 100)
                    terrain_type = rng.choice(["grass", "water", "forest", "mountain"], 
                                            weights=[10, 3, 5, 2])
                    has_resource = rng.boolean(0.2)
                    num_entities = rng.randint(0, 5)
                    
                    # Create a cell with these features
                    cell = {
                        "elevation": elevation,
                        "type": terrain_type,
                        "has_resource": has_resource,
                        "num_entities": num_entities
                    }
                    row.append(cell)
                terrain.append(row)
            return terrain
        
        # Generate terrain with the same seed multiple times
        rng1 = DeterministicRNG(ISeedConfig(seed=seed_value))
        terrain1 = generate_simple_terrain(rng1, 10, 10)
        
        rng2 = DeterministicRNG(ISeedConfig(seed=seed_value))
        terrain2 = generate_simple_terrain(rng2, 10, 10)
        
        # Terrains should be identical due to deterministic RNG
        assert terrain1 == terrain2
        
        # Reset first RNG and regenerate
        rng1.reset()
        terrain1_reset = generate_simple_terrain(rng1, 10, 10)
        
        # Should match the original terrain
        assert terrain1 == terrain1_reset
        
        # Try with a different seed
        rng_diff = DeterministicRNG(ISeedConfig(seed=seed_value + 1))
        terrain_diff = generate_simple_terrain(rng_diff, 10, 10)
        
        # Should be different from the original
        assert terrain1 != terrain_diff


# Main block to allow running the tests directly
if __name__ == "__main__":
    pytest.main(["-v", __file__]) 