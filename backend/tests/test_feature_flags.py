import unittest
import tempfile
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from backend.utils.feature_flags import (
    FeatureFlagSystem, 
    is_feature_enabled, 
    set_feature_flag, 
    get_all_feature_flags,
    load_feature_flags_from_file,
    register_context_evaluator
)

class TestFeatureFlags(unittest.TestCase):
    def setUp(self):
        # Create a fresh feature flag system for each test
        self.feature_flags = FeatureFlagSystem()
        
        # Set some test environment variables
        os.environ["FEATURE_FLAG_TEST_ENV_FLAG"] = "true"
        os.environ["FEATURE_FLAG_TEST_ENV_FLAG_FALSE"] = "false"
        
        # Reload to pick up the environment variables
        self.feature_flags._load_from_environment()
    
    def tearDown(self):
        # Clean up environment variables
        if "FEATURE_FLAG_TEST_ENV_FLAG" in os.environ:
            del os.environ["FEATURE_FLAG_TEST_ENV_FLAG"]
        if "FEATURE_FLAG_TEST_ENV_FLAG_FALSE" in os.environ:
            del os.environ["FEATURE_FLAG_TEST_ENV_FLAG_FALSE"]
    
    def test_env_variables_loading(self):
        """Test loading feature flags from environment variables."""
        self.assertTrue(
            self.feature_flags.is_feature_enabled("TEST_ENV_FLAG"),
            "Environment variable flag should be enabled"
        )
        self.assertFalse(
            self.feature_flags.is_feature_enabled("TEST_ENV_FLAG_FALSE"),
            "Environment variable flag should be disabled"
        )
    
    def test_set_get_feature_flag(self):
        """Test setting and getting feature flags."""
        # Set a flag
        self.feature_flags.set_feature_flag("TEST_FLAG", True)
        
        # Check it was set correctly
        self.assertTrue(
            self.feature_flags.is_feature_enabled("TEST_FLAG"),
            "Flag should be enabled after setting"
        )
        
        # Change the flag
        self.feature_flags.set_feature_flag("TEST_FLAG", False)
        
        # Check it was updated correctly
        self.assertFalse(
            self.feature_flags.is_feature_enabled("TEST_FLAG"),
            "Flag should be disabled after updating"
        )
    
    def test_get_all_feature_flags(self):
        """Test getting all feature flags."""
        # Set some flags
        self.feature_flags.set_feature_flag("TEST_FLAG_1", True)
        self.feature_flags.set_feature_flag("TEST_FLAG_2", False)
        
        # Get all flags
        all_flags = self.feature_flags.get_all_feature_flags()
        
        # Check the flags we set are included
        self.assertIn("TEST_FLAG_1", all_flags)
        self.assertIn("TEST_FLAG_2", all_flags)
        self.assertTrue(all_flags["TEST_FLAG_1"])
        self.assertFalse(all_flags["TEST_FLAG_2"])
    
    def test_load_from_file(self):
        """Test loading feature flags from a config file."""
        # Create a temporary file with feature flags
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            config = {
                "featureFlags": {
                    "TEST_FILE_FLAG_1": True,
                    "TEST_FILE_FLAG_2": False
                }
            }
            json.dump(config, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Load flags from the file
            result = self.feature_flags.load_from_file(temp_file_path)
            self.assertTrue(result, "Loading from file should succeed")
            
            # Check the flags were loaded correctly
            self.assertTrue(
                self.feature_flags.is_feature_enabled("TEST_FILE_FLAG_1"),
                "File flag 1 should be enabled"
            )
            self.assertFalse(
                self.feature_flags.is_feature_enabled("TEST_FILE_FLAG_2"),
                "File flag 2 should be disabled"
            )
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)
    
    def test_load_from_invalid_file(self):
        """Test loading from an invalid file."""
        # Test with non-existent file
        result = self.feature_flags.load_from_file("nonexistent_file.json")
        self.assertFalse(result, "Loading from non-existent file should fail")
        
        # Test with file that doesn't contain featureFlags key
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            config = {"someOtherKey": {}}
            json.dump(config, temp_file)
            temp_file_path = temp_file.name
        
        try:
            result = self.feature_flags.load_from_file(temp_file_path)
            self.assertFalse(result, "Loading from file without featureFlags key should fail")
        finally:
            os.unlink(temp_file_path)
    
    def test_context_evaluator(self):
        """Test context-based flag evaluation."""
        # Create a context evaluator that checks if user is admin
        def admin_evaluator(flag, context):
            return context.get("role") == "admin"
        
        # Register the evaluator
        self.feature_flags.register_evaluator("ADMIN_ONLY_FEATURE", admin_evaluator)
        
        # Test with admin context
        admin_context = {"role": "admin"}
        self.assertTrue(
            self.feature_flags.is_feature_enabled("ADMIN_ONLY_FEATURE", admin_context),
            "Feature should be enabled for admin"
        )
        
        # Test with non-admin context
        user_context = {"role": "user"}
        self.assertFalse(
            self.feature_flags.is_feature_enabled("ADMIN_ONLY_FEATURE", user_context),
            "Feature should be disabled for non-admin"
        )
    
    def test_thread_safety(self):
        """Test thread safety with concurrent access."""
        num_threads = 10
        operations_per_thread = 100
        
        def worker():
            # Do a mix of operations
            for i in range(operations_per_thread):
                flag_name = f"THREAD_TEST_{i % 10}"
                
                # Alternate setting and checking flags
                if i % 2 == 0:
                    self.feature_flags.set_feature_flag(flag_name, i % 3 == 0)
                else:
                    # Just read the flag (result doesn't matter for this test)
                    self.feature_flags.is_feature_enabled(flag_name)
            
            # End with getting all flags
            return self.feature_flags.get_all_feature_flags()
        
        # Run concurrent operations
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            results = list(executor.map(lambda _: worker(), range(num_threads)))
        
        # Just verify we didn't get any exceptions during concurrent access
        self.assertEqual(len(results), num_threads)
    
    def test_module_level_functions(self):
        """Test module-level functions for backward compatibility."""
        # Set a flag using module function
        set_feature_flag("MODULE_TEST_FLAG", True)
        
        # Check it using module function
        self.assertTrue(
            is_feature_enabled("MODULE_TEST_FLAG"),
            "Module-level functions should work correctly"
        )
        
        # Get all flags
        all_flags = get_all_feature_flags()
        self.assertIn("MODULE_TEST_FLAG", all_flags)

if __name__ == "__main__":
    unittest.main() 