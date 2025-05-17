import unittest
import threading
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from backend.utils.id import IDGenerator, generate_unique_id, generate_uuid

class TestIDGenerator(unittest.TestCase):
    def setUp(self):
        # Create a fresh ID generator for each test
        self.id_generator = IDGenerator()
    
    def test_unique_id_format(self):
        """Test that generated IDs follow the expected format with sortability."""
        id_str = self.id_generator.generate_unique_id()
        
        # Format should be: timestamp_sequence_randomstring
        # Where timestamp is 15 digits, sequence is 4 digits, randomstring is 8 alphanumeric chars
        pattern = r"^\d{15}_\d{4}_[a-z0-9]{8}$"
        self.assertTrue(re.match(pattern, id_str), f"ID format invalid: {id_str}")
    
    def test_id_with_prefix(self):
        """Test that IDs can be generated with prefixes."""
        prefix = "test-"
        id_str = self.id_generator.generate_unique_id(prefix)
        self.assertTrue(id_str.startswith(prefix))
    
    def test_uniqueness(self):
        """Test that generated IDs are unique."""
        num_ids = 1000
        ids = [self.id_generator.generate_unique_id() for _ in range(num_ids)]
        unique_ids = set(ids)
        self.assertEqual(len(unique_ids), num_ids, "Generated IDs are not unique")
    
    def test_id_sortability(self):
        """Test that IDs are sortable by creation time."""
        ids = []
        for _ in range(5):
            ids.append(self.id_generator.generate_unique_id())
        
        # IDs should be sortable naturally due to timestamp prefix
        sorted_ids = sorted(ids)
        self.assertEqual(sorted_ids, ids, "IDs are not naturally sortable by time")
    
    def test_concurrent_generation(self):
        """Test concurrent ID generation with multiple threads."""
        num_threads = 10
        ids_per_thread = 100
        all_ids = []
        
        def generate_ids():
            return [self.id_generator.generate_unique_id() for _ in range(ids_per_thread)]
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            results = list(executor.map(lambda _: generate_ids(), range(num_threads)))
            
        for result in results:
            all_ids.extend(result)
        
        # Check all IDs are unique even with concurrent generation
        unique_ids = set(all_ids)
        self.assertEqual(len(unique_ids), num_threads * ids_per_thread, 
                         "Concurrent ID generation produced duplicates")
    
    def test_uuid_generation(self):
        """Test UUID generation."""
        # Test UUID v4 (random)
        uuid_str = self.id_generator.generate_uuid()
        try:
            uuid_obj = uuid.UUID(uuid_str)
            self.assertEqual(uuid_obj.version, 4, "UUID is not version 4")
        except ValueError:
            self.fail(f"Generated UUID is not valid: {uuid_str}")
    
    def test_deterministic_uuid_generation(self):
        """Test deterministic UUID v5 generation."""
        namespace = uuid.NAMESPACE_DNS
        name = "example.com"
        
        # Generate two UUIDs with the same parameters
        uuid1 = self.id_generator.generate_uuid(namespace, name)
        uuid2 = self.id_generator.generate_uuid(namespace, name)
        
        # They should be identical
        self.assertEqual(uuid1, uuid2, "Deterministic UUIDs are not consistent")
        
        # Test with different name
        uuid3 = self.id_generator.generate_uuid(namespace, "different.com")
        self.assertNotEqual(uuid1, uuid3, "UUIDs with different names should differ")
    
    def test_clear_id_cache(self):
        """Test clearing the ID cache."""
        # Generate some IDs
        for _ in range(10):
            self.id_generator.generate_unique_id()
        
        # Clear the cache
        self.id_generator.clear_id_cache()
        
        # Verify internal state was reset
        self.assertEqual(len(self.id_generator._generated_ids), 0)
        self.assertEqual(self.id_generator._collision_count, 0)
    
    def test_module_level_functions(self):
        """Test the module-level functions for backward compatibility."""
        # Test the module-level generate_unique_id function
        id_str = generate_unique_id()
        pattern = r"^\d{15}_\d{4}_[a-z0-9]{8}$"
        self.assertTrue(re.match(pattern, id_str), f"Module-level ID format invalid: {id_str}")
        
        # Test the module-level generate_uuid function
        uuid_str = generate_uuid()
        try:
            uuid_obj = uuid.UUID(uuid_str)
            self.assertEqual(uuid_obj.version, 4, "Module-level UUID is not version 4")
        except ValueError:
            self.fail(f"Generated module-level UUID is not valid: {uuid_str}")

if __name__ == "__main__":
    unittest.main() 