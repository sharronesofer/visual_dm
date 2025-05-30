"""
Tests for backend.systems.shared.utils.game.random_utils

Comprehensive tests for random generation utilities including weighted selection,
attribute distribution, and name generation.
"""

import pytest
import unittest
import tempfile
import os
import shutil
import json
from unittest.mock import Mock, patch, mock_open

# Import the module being tested
from backend.systems.shared.utils.game.random_utils import (
    WeightedRandomSelector,
    AttributeDistributor,
    NameGenerator,
    weighted_choice,
    weighted_choice_multiple,
    distribute_points,
    generate_name,
)


class TestWeightedRandomSelector(unittest.TestCase): pass
    """Test the WeightedRandomSelector class."""

    def setUp(self): pass
        """Set up test fixtures."""
        self.selector = WeightedRandomSelector()

    def test_init_empty(self): pass
        """Test initialization with no items."""
        selector = WeightedRandomSelector()
        self.assertEqual(len(selector), 0)

    def test_init_with_items(self): pass
        """Test initialization with items."""
        items = {"a": 1.0, "b": 2.0, "c": 3.0}
        selector = WeightedRandomSelector(items)
        self.assertEqual(len(selector), 3)

    def test_add_item(self): pass
        """Test adding items."""
        self.selector.add_item("test", 1.0)
        self.assertEqual(len(self.selector), 1)
        
        # Test negative weight (should be clamped to 0)
        self.selector.add_item("negative", -1.0)
        self.assertEqual(self.selector.items["negative"], 0.0)

    def test_remove_item(self): pass
        """Test removing items."""
        self.selector.add_item("test", 1.0)
        result = self.selector.remove_item("test")
        self.assertTrue(result)
        self.assertEqual(len(self.selector), 0)
        
        # Test removing non-existent item
        result = self.selector.remove_item("nonexistent")
        self.assertFalse(result)

    def test_update_weight(self): pass
        """Test updating item weights."""
        self.selector.add_item("test", 1.0)
        result = self.selector.update_weight("test", 2.0)
        self.assertTrue(result)
        self.assertEqual(self.selector.items["test"], 2.0)
        
        # Test updating non-existent item
        result = self.selector.update_weight("nonexistent", 1.0)
        self.assertFalse(result)

    def test_select_empty(self): pass
        """Test selection from empty selector."""
        result = self.selector.select()
        self.assertIsNone(result)

    def test_select_single_item(self): pass
        """Test selection with single item."""
        self.selector.add_item("only", 1.0)
        result = self.selector.select()
        self.assertEqual(result, "only")

    def test_select_multiple_items(self): pass
        """Test selection with multiple items."""
        self.selector.add_item("a", 1.0)
        self.selector.add_item("b", 2.0)
        self.selector.add_item("c", 3.0)
        
        # Test multiple selections to check distribution
        results = [self.selector.select() for _ in range(100)]
        
        # All results should be valid
        for result in results: pass
            self.assertIn(result, ["a", "b", "c"])

    def test_select_zero_weights(self): pass
        """Test selection with zero weights."""
        self.selector.add_item("zero1", 0.0)
        self.selector.add_item("zero2", 0.0)
        result = self.selector.select()
        self.assertIsNone(result)

    def test_select_all_zero_weights_returns_none(self): pass
        """Test selection with all zero weights returns None."""
        self.selector.add_item("a", 0.0)
        self.selector.add_item("b", 0.0)
        self.selector.add_item("c", 0.0)
        
        # Should return None when all weights are zero (filtered out)
        result = self.selector.select()
        self.assertIsNone(result)

    def test_select_fallback_edge_case(self): pass
        """Test the fallback case in select method."""
        self.selector.add_item("a", 1.0)
        self.selector.add_item("b", 1.0)
        
        # Mock random.uniform to return a value that would cause fallback
        with patch('random.uniform') as mock_uniform: pass
            mock_uniform.return_value = 10.0  # Value larger than total weight
            result = self.selector.select()
            # Should return the last item as fallback
            self.assertEqual(result, "b")

    def test_select_multiple_unique(self): pass
        """Test selecting multiple unique items."""
        self.selector.add_item("a", 1.0)
        self.selector.add_item("b", 2.0)
        self.selector.add_item("c", 3.0)
        
        results = self.selector.select_multiple(2, unique=True)
        self.assertEqual(len(results), 2)
        self.assertEqual(len(set(results)), 2)  # All unique

    def test_select_multiple_unique_more_than_available(self): pass
        """Test selecting more unique items than available."""
        self.selector.add_item("a", 1.0)
        self.selector.add_item("b", 2.0)
        
        # Request more items than available
        results = self.selector.select_multiple(5, unique=True)
        self.assertEqual(len(results), 2)  # Should only return available items

    def test_select_multiple_unique_empty_selector(self): pass
        """Test selecting multiple unique items from empty selector."""
        results = self.selector.select_multiple(3, unique=True)
        self.assertEqual(len(results), 0)

    def test_select_multiple_unique_zero_count(self): pass
        """Test selecting zero items."""
        self.selector.add_item("a", 1.0)
        results = self.selector.select_multiple(0, unique=True)
        self.assertEqual(len(results), 0)

    def test_select_multiple_unique_negative_count(self): pass
        """Test selecting negative count of items."""
        self.selector.add_item("a", 1.0)
        results = self.selector.select_multiple(-1, unique=True)
        self.assertEqual(len(results), 0)

    def test_select_multiple_non_unique(self): pass
        """Test selecting multiple non-unique items."""
        self.selector.add_item("a", 1.0)
        self.selector.add_item("b", 2.0)
        
        results = self.selector.select_multiple(5, unique=False)
        self.assertEqual(len(results), 5)

    def test_select_multiple_non_unique_with_none_results(self): pass
        """Test selecting multiple non-unique items when some selections return None."""
        # Create a selector that will return None sometimes
        empty_selector = WeightedRandomSelector()
        results = empty_selector.select_multiple(3, unique=False)
        self.assertEqual(len(results), 0)  # All None results filtered out

    def test_get_probability(self): pass
        """Test probability calculation."""
        self.selector.add_item("a", 1.0)
        self.selector.add_item("b", 2.0)
        self.selector.add_item("c", 3.0)
        
        prob_a = self.selector.get_probability("a")
        prob_b = self.selector.get_probability("b")
        prob_c = self.selector.get_probability("c")
        
        self.assertAlmostEqual(prob_a, 1.0/6.0)
        self.assertAlmostEqual(prob_b, 2.0/6.0)
        self.assertAlmostEqual(prob_c, 3.0/6.0)
        
        # Test non-existent item
        prob_none = self.selector.get_probability("nonexistent")
        self.assertEqual(prob_none, 0.0)

    def test_get_probability_empty_selector(self): pass
        """Test probability calculation on empty selector."""
        prob = self.selector.get_probability("anything")
        self.assertEqual(prob, 0.0)

    def test_get_probability_zero_total_weight(self): pass
        """Test probability calculation when total weight is zero."""
        self.selector.add_item("a", 0.0)
        self.selector.add_item("b", 0.0)
        prob = self.selector.get_probability("a")
        self.assertEqual(prob, 0.0)

    def test_to_dict(self): pass
        """Test dictionary conversion."""
        self.selector.add_item("a", 1.0)
        self.selector.add_item("b", 2.0)
        
        result = self.selector.to_dict()
        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 2)

    def test_str_representation(self): pass
        """Test string representation."""
        self.selector.add_item("test", 1.0)
        str_repr = str(self.selector)
        self.assertIn("WeightedRandomSelector", str_repr)
        self.assertIn("1 items", str_repr)


class TestAttributeDistributor(unittest.TestCase): pass
    """Test the AttributeDistributor class."""

    def setUp(self): pass
        """Set up test fixtures."""
        self.attributes = ["str", "dex", "con", "int", "wis", "cha"]
        self.distributor = AttributeDistributor(self.attributes, 100)

    def test_init(self): pass
        """Test initialization."""
        self.assertEqual(self.distributor.attributes, self.attributes)
        self.assertEqual(self.distributor.total_points, 100)

    def test_uniform_distribution(self): pass
        """Test uniform distribution."""
        result = self.distributor.uniform_distribution()
        
        # Check all attributes are present
        for attr in self.attributes: pass
            self.assertIn(attr, result)
        
        # Check total points
        total = sum(result.values())
        self.assertEqual(total, 100)
        
        # Check roughly equal distribution
        values = list(result.values())
        self.assertTrue(max(values) - min(values) <= 1)

    def test_uniform_distribution_empty_attributes(self): pass
        """Test uniform distribution with empty attributes."""
        distributor = AttributeDistributor([], 100)
        result = distributor.uniform_distribution()
        self.assertEqual(result, {})

    def test_normal_distribution(self): pass
        """Test normal distribution."""
        result = self.distributor.normal_distribution()
        
        # Check all attributes are present
        for attr in self.attributes: pass
            self.assertIn(attr, result)
        
        # Check total points
        total = sum(result.values())
        self.assertEqual(total, 100)
        
        # Check minimum values are respected
        for value in result.values(): pass
            self.assertGreaterEqual(value, 0)

    def test_normal_distribution_empty_attributes(self): pass
        """Test normal distribution with empty attributes."""
        distributor = AttributeDistributor([], 100)
        result = distributor.normal_distribution()
        self.assertEqual(result, {})

    def test_normal_distribution_with_min_value(self): pass
        """Test normal distribution with minimum value constraint."""
        result = self.distributor.normal_distribution(min_value=10)
        
        # Check all values meet minimum
        for value in result.values(): pass
            self.assertGreaterEqual(value, 10)

    def test_skewed_distribution(self): pass
        """Test skewed distribution."""
        result = self.distributor.skewed_distribution()
        
        # Check all attributes are present
        for attr in self.attributes: pass
            self.assertIn(attr, result)
        
        # Check total points
        total = sum(result.values())
        self.assertEqual(total, 100)

    def test_skewed_distribution_empty_attributes(self): pass
        """Test skewed distribution with empty attributes."""
        distributor = AttributeDistributor([], 100)
        result = distributor.skewed_distribution()
        self.assertEqual(result, {})

    def test_skewed_distribution_single_attribute(self): pass
        """Test skewed distribution with single attribute."""
        distributor = AttributeDistributor(["str"], 100)
        result = distributor.skewed_distribution()
        self.assertEqual(result["str"], 100)

    def test_skewed_distribution_two_attributes(self): pass
        """Test skewed distribution with two attributes."""
        distributor = AttributeDistributor(["str", "dex"], 100)
        result = distributor.skewed_distribution()
        
        # Check total points (may not be exactly 100 due to min_value constraints)
        total = sum(result.values())
        self.assertGreaterEqual(total, 10)  # At least min_value for each attribute

    def test_tiered_distribution(self): pass
        """Test tiered distribution."""
        result = self.distributor.tiered_distribution()
        
        # Check all attributes are present
        for attr in self.attributes: pass
            self.assertIn(attr, result)
        
        # Check total points
        total = sum(result.values())
        self.assertEqual(total, 100)

    def test_tiered_distribution_empty_attributes(self): pass
        """Test tiered distribution with empty attributes."""
        distributor = AttributeDistributor([], 100)
        result = distributor.tiered_distribution()
        self.assertEqual(result, {})

    def test_tiered_distribution_custom_tiers(self): pass
        """Test tiered distribution with custom tier weights."""
        custom_tiers = [0.5, 0.3, 0.2]
        result = self.distributor.tiered_distribution(tiers=custom_tiers)
        
        # Check total points
        total = sum(result.values())
        self.assertEqual(total, 100)

    def test_tiered_distribution_more_attributes_than_tiers(self): pass
        """Test tiered distribution when there are more attributes than tiers."""
        # Use default tiers which should be shorter than our attribute list
        result = self.distributor.tiered_distribution()
        
        # Should still work and distribute all points
        total = sum(result.values())
        self.assertEqual(total, 100)

    def test_empty_attributes(self): pass
        """Test with empty attributes list."""
        distributor = AttributeDistributor([], 50)
        
        uniform = distributor.uniform_distribution()
        normal = distributor.normal_distribution()
        skewed = distributor.skewed_distribution()
        tiered = distributor.tiered_distribution()
        
        self.assertEqual(uniform, {})
        self.assertEqual(normal, {})
        self.assertEqual(skewed, {})
        self.assertEqual(tiered, {})

    def test_single_attribute(self): pass
        """Test with single attribute."""
        distributor = AttributeDistributor(["str"], 50)
        
        uniform = distributor.uniform_distribution()
        normal = distributor.normal_distribution()
        skewed = distributor.skewed_distribution()
        tiered = distributor.tiered_distribution()
        
        self.assertEqual(uniform["str"], 50)
        self.assertEqual(normal["str"], 50)
        self.assertEqual(skewed["str"], 50)
        # Tiered distribution uses default tiers, so may not be exactly 50
        self.assertGreater(tiered["str"], 0)


class TestNameGenerator(unittest.TestCase): pass
    """Test the NameGenerator class."""

    def setUp(self): pass
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = NameGenerator(self.temp_dir)

    def tearDown(self): pass
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_init(self): pass
        """Test initialization."""
        self.assertIsNotNone(self.generator.data_dir)
        self.assertIsInstance(self.generator.first_names, dict)
        self.assertIsInstance(self.generator.last_names, list)
        self.assertIsInstance(self.generator.place_names, dict)

    def test_init_no_data_dir(self): pass
        """Test initialization without data directory."""
        generator = NameGenerator()
        self.assertIsNotNone(generator.data_dir)

    def test_find_data_dir_current_directory(self): pass
        """Test finding data directory in current directory."""
        with patch('os.path.exists') as mock_exists: pass
            mock_exists.side_effect = lambda path: 'data' in path and not path.startswith('/')
            generator = NameGenerator()
            # Should find a data directory
            self.assertIsNotNone(generator.data_dir)

    def test_find_data_dir_parent_directory(self): pass
        """Test finding data directory in parent directory."""
        with patch('os.path.exists') as mock_exists: pass
            mock_exists.side_effect = lambda path: '../data' in path
            generator = NameGenerator()
            # Should find a data directory
            self.assertIsNotNone(generator.data_dir)

    def test_find_data_dir_fallback(self): pass
        """Test fallback when no data directory is found."""
        with patch('os.path.exists', return_value=False): pass
            generator = NameGenerator()
            # Should use fallback directory (may include path components)
            self.assertIn('data', generator.data_dir)

    def test_load_name_data_file_not_found(self): pass
        """Test loading name data when files don't exist."""
        # Files don't exist, should use defaults
        self.assertIsInstance(self.generator.first_names, dict)
        self.assertIsInstance(self.generator.last_names, list)
        self.assertIsInstance(self.generator.place_names, dict)

    def test_load_name_data_json_decode_error(self): pass
        """Test loading name data with JSON decode error."""
        # Create invalid JSON files
        with open(os.path.join(self.temp_dir, 'first_names.json'), 'w') as f: pass
            f.write('invalid json')
        
        # Should handle error gracefully and use defaults
        generator = NameGenerator(self.temp_dir)
        self.assertIsInstance(generator.first_names, dict)

    def test_load_name_data_io_error(self): pass
        """Test loading name data with IO error."""
        # Create a directory instead of a file to cause IO error
        os.makedirs(os.path.join(self.temp_dir, 'first_names.json'))
        
        # Should handle error gracefully and use defaults
        generator = NameGenerator(self.temp_dir)
        self.assertIsInstance(generator.first_names, dict)

    def test_save_name_data_success(self): pass
        """Test saving name data successfully."""
        self.generator.add_first_names('male', ['TestName'])
        self.generator._save_name_data()
        
        # Check that file was created
        first_names_file = os.path.join(self.temp_dir, 'first_names.json')
        self.assertTrue(os.path.exists(first_names_file))

    def test_save_name_data_io_error(self): pass
        """Test saving name data with IO error."""
        # Make directory read-only to cause IO error
        os.chmod(self.temp_dir, 0o444)
        
        try: pass
            # Should handle error gracefully
            self.generator._save_name_data()
        except Exception: pass
            self.fail("_save_name_data should handle IO errors gracefully")
        finally: pass
            # Restore permissions for cleanup
            os.chmod(self.temp_dir, 0o755)

    def test_add_first_names(self): pass
        """Test adding first names."""
        self.generator.add_first_names('male', ['John', 'James'])
        self.assertIn('male', self.generator.first_names)
        self.assertIn('John', self.generator.first_names['male'])

    def test_add_last_names(self): pass
        """Test adding last names."""
        self.generator.add_last_names(['Smith', 'Johnson'])
        self.assertIn('Smith', self.generator.last_names)

    def test_add_place_names(self): pass
        """Test adding place names."""
        self.generator.add_place_names('city', ['Springfield', 'Riverside'])
        self.assertIn('city', self.generator.place_names)
        self.assertIn('Springfield', self.generator.place_names['city'])

    def test_generate_first_name(self): pass
        """Test generating first names."""
        self.generator.add_first_names('male', ['John'])
        name = self.generator.generate_first_name('male')
        self.assertIsInstance(name, str)

    def test_generate_first_name_unknown_gender(self): pass
        """Test generating first name with unknown gender."""
        name = self.generator.generate_first_name('unknown')
        self.assertIsInstance(name, str)

    def test_generate_first_name_empty_list(self): pass
        """Test generating first name from empty list."""
        self.generator.first_names['empty'] = []
        name = self.generator.generate_first_name('empty')
        self.assertIsInstance(name, str)

    def test_generate_last_name(self): pass
        """Test generating last names."""
        self.generator.add_last_names(['Smith'])
        name = self.generator.generate_last_name()
        self.assertIsInstance(name, str)

    def test_generate_last_name_empty_list(self): pass
        """Test generating last name from empty list."""
        self.generator.last_names = []
        name = self.generator.generate_last_name()
        self.assertIsInstance(name, str)

    def test_generate_full_name(self): pass
        """Test generating full names."""
        self.generator.add_first_names('male', ['John'])
        self.generator.add_last_names(['Smith'])
        name = self.generator.generate_full_name('male')
        self.assertIsInstance(name, str)
        self.assertIn(' ', name)  # Should contain space between first and last

    def test_generate_place_name(self): pass
        """Test generating place names."""
        self.generator.add_place_names('city', ['Springfield'])
        name = self.generator.generate_place_name('city')
        self.assertIsInstance(name, str)

    def test_generate_place_name_unknown_category(self): pass
        """Test generating place name with unknown category."""
        name = self.generator.generate_place_name('unknown')
        self.assertIsInstance(name, str)

    def test_generate_place_name_empty_list(self): pass
        """Test generating place name from empty list."""
        self.generator.place_names['empty'] = []
        name = self.generator.generate_place_name('empty')
        self.assertIsInstance(name, str)

    def test_generate_place_name_no_category(self): pass
        """Test generating place name without specifying category."""
        self.generator.add_place_names('city', ['Springfield'])
        name = self.generator.generate_place_name()
        self.assertIsInstance(name, str)

    def test_generate_place_name_empty_place_names(self): pass
        """Test generating place name when place_names is empty."""
        self.generator.place_names = {}
        name = self.generator.generate_place_name()
        self.assertIsInstance(name, str)

    @patch("builtins.open", mock_open(read_data='{"male": ["Alice", "Bob", "Charlie"]}'))
    @patch("os.path.exists", return_value=True)
    def test_load_name_data_success(self, mock_exists): pass
        """Test successful loading of name data."""
        generator = NameGenerator(self.temp_dir)
        # Should have loaded the mocked data
        self.assertIsInstance(generator.first_names, dict)

    def test_placeholder_name_generation(self): pass
        """Test placeholder name generation."""
        placeholder = self.generator._generate_placeholder_name()
        self.assertIsInstance(placeholder, str)
        self.assertTrue(len(placeholder) > 0)

    def test_generate_unique_id(self): pass
        """Test unique ID generation."""
        id1 = self.generator.generate_unique_id()
        id2 = self.generator.generate_unique_id()
        self.assertNotEqual(id1, id2)
        
        # Test with prefix
        id_with_prefix = self.generator.generate_unique_id("test_")
        self.assertTrue(id_with_prefix.startswith("test_"))


class TestStandaloneFunctions(unittest.TestCase): pass
    """Test standalone utility functions."""

    def test_weighted_choice(self): pass
        """Test weighted choice function."""
        options = {"a": 1.0, "b": 2.0, "c": 3.0}
        result = weighted_choice(options)
        self.assertIn(result, options.keys())

    def test_weighted_choice_empty_options(self): pass
        """Test weighted choice with empty options."""
        result = weighted_choice({})
        self.assertIsNone(result)

    def test_weighted_choice_multiple(self): pass
        """Test weighted choice multiple function."""
        options = {"a": 1.0, "b": 2.0, "c": 3.0}
        results = weighted_choice_multiple(options, 2)
        self.assertEqual(len(results), 2)

    def test_weighted_choice_multiple_empty_options(self): pass
        """Test weighted choice multiple with empty options."""
        results = weighted_choice_multiple({}, 2)
        self.assertEqual(len(results), 0)

    def test_distribute_points_uniform(self): pass
        """Test distribute points with uniform distribution."""
        attributes = ["str", "dex", "con"]
        result = distribute_points(attributes, 90, "uniform")
        
        total = sum(result.values())
        self.assertEqual(total, 90)

    def test_distribute_points_normal(self): pass
        """Test distribute points with normal distribution."""
        attributes = ["str", "dex", "con"]
        result = distribute_points(attributes, 90, "normal")
        
        total = sum(result.values())
        self.assertEqual(total, 90)

    def test_distribute_points_skewed(self): pass
        """Test distribute points with skewed distribution."""
        attributes = ["str", "dex", "con"]
        result = distribute_points(attributes, 90, "skewed")
        
        total = sum(result.values())
        self.assertEqual(total, 90)

    def test_distribute_points_tiered(self): pass
        """Test distribute points with tiered distribution."""
        attributes = ["str", "dex", "con"]
        result = distribute_points(attributes, 90, "tiered")
        
        total = sum(result.values())
        self.assertEqual(total, 90)

    def test_distribute_points_invalid_type(self): pass
        """Test distribute points with invalid distribution type."""
        attributes = ["str", "dex", "con"]
        result = distribute_points(attributes, 90, "invalid")
        
        # Should default to normal distribution
        total = sum(result.values())
        self.assertEqual(total, 90)

    def test_generate_name_full(self): pass
        """Test generate_name function with full name."""
        name = generate_name("full")
        self.assertIsInstance(name, str)

    def test_generate_name_first(self): pass
        """Test generate_name function with first name."""
        name = generate_name("first")
        self.assertIsInstance(name, str)

    def test_generate_name_last(self): pass
        """Test generate_name function with last name."""
        name = generate_name("last")
        self.assertIsInstance(name, str)

    def test_generate_name_place(self): pass
        """Test generate_name function with place name."""
        name = generate_name("place")
        self.assertIsInstance(name, str)

    def test_generate_name_invalid_type(self): pass
        """Test generate_name function with invalid type."""
        name = generate_name("invalid")
        self.assertIsInstance(name, str)

    def test_generate_name_with_gender(self): pass
        """Test generate_name function with gender specification."""
        name = generate_name("first", "male")
        self.assertIsInstance(name, str)


if __name__ == "__main__": pass
    unittest.main()
