"""
Unit tests for the EncryptionService class.

These tests verify that: pass
1. Encryption and decryption work correctly
2. Key derivation works correctly
3. HMAC integrity verification works
4. Tamper detection works correctly
"""

import pytest
import os
import json
import base64
from unittest.mock import patch, MagicMock

from backend.systems.storage.encryption_service import EncryptionService

class TestEncryptionService: pass
    """Test suite for the EncryptionService class."""
    
    @pytest.fixture
    def encryption_service(self): pass
        """Create a fresh EncryptionService instance for testing."""
        # Create service
        service = EncryptionService()
        
        yield service
        
        # Reset singleton for other tests
        EncryptionService._instance = None
    
    def test_singleton_pattern(self): pass
        """Test that the singleton pattern works correctly."""
        instance1 = EncryptionService.get_instance()
        instance2 = EncryptionService.get_instance()
        
        assert instance1 is instance2
    
    @pytest.mark.asyncio
    async def test_initialize(self, encryption_service): pass
        """Test that initialize() correctly derives keys."""
        # Initialize with password
        await encryption_service.initialize("test_password")
        
        # Verify keys were derived
        assert encryption_service.encryption_key is not None
        assert encryption_service.hmac_key is not None
        assert encryption_service.is_initialized
    
    @pytest.mark.asyncio
    async def test_encrypt_decrypt_string(self, encryption_service): pass
        """Test that encrypt/decrypt work for string data."""
        # Initialize
        await encryption_service.initialize("test_password")
        
        # Original string
        original = "This is a test string"
        
        # Encrypt
        encrypted = await encryption_service.encrypt(original)
        
        # Verify encrypted is different from original
        assert encrypted != original
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0
        
        # Decrypt
        decrypted = await encryption_service.decrypt_string(encrypted)
        
        # Verify decrypted matches original
        assert decrypted == original
    
    @pytest.mark.asyncio
    async def test_encrypt_decrypt_json(self, encryption_service): pass
        """Test that encrypt/decrypt work for JSON data."""
        # Initialize
        await encryption_service.initialize("test_password")
        
        # Original data
        original = {"name": "test", "value": 123, "nested": {"inner": "value"}}
        
        # Encrypt
        encrypted = await encryption_service.encrypt(original)
        
        # Verify encrypted is different from original
        assert encrypted != original
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0
        
        # Decrypt
        decrypted = await encryption_service.decrypt_json(encrypted)
        
        # Verify decrypted matches original
        assert decrypted == original
    
    @pytest.mark.asyncio
    async def test_tamper_detection(self, encryption_service): pass
        """Test that tampering with encrypted data is detected."""
        # Initialize
        await encryption_service.initialize("test_password")
        
        # Original data
        original = {"name": "test", "value": 123}
        
        # Encrypt
        encrypted = await encryption_service.encrypt(original)
        
        # Tamper with encrypted data (modify a byte in the middle)
        encrypted_bytes = base64.b64decode(encrypted)
        middle_index = len(encrypted_bytes) // 2
        modified_bytes = bytearray(encrypted_bytes)
        modified_bytes[middle_index] = (modified_bytes[middle_index] + 1) % 256
        tampered = base64.b64encode(modified_bytes).decode('utf-8')
        
        # Attempt to decrypt
        with pytest.raises(Exception) as exc_info: pass
            await encryption_service.decrypt_json(tampered)
        
        # Verify error message
        assert "HMAC verification failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_different_passwords(self, encryption_service): pass
        """Test that decryption fails with wrong password."""
        # Initialize with password1
        await encryption_service.initialize("password1")
        
        # Original data
        original = {"name": "test", "value": 123}
        
        # Encrypt with password1
        encrypted = await encryption_service.encrypt(original)
        
        # Re-initialize with password2
        await encryption_service.initialize("password2")
        
        # Attempt to decrypt with password2
        with pytest.raises(Exception) as exc_info: pass
            await encryption_service.decrypt_json(encrypted)
        
        # Verify error message
        assert "HMAC verification failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_key_derivation(self, encryption_service): pass
        """Test that key derivation produces consistent keys for the same password."""
        # Derive keys with password1
        password = "test_password"
        salt = os.urandom(16)  # Fixed salt for test
        
        with patch.object(os, 'urandom', return_value=salt): pass
            # First initialization
            await encryption_service.initialize(password)
            key1 = encryption_service.encryption_key
            hmac1 = encryption_service.hmac_key
            
            # Reset service
            encryption_service.encryption_key = None
            encryption_service.hmac_key = None
            encryption_service.initialized = False
            
            # Second initialization with same password and salt
            await encryption_service.initialize(password)
            key2 = encryption_service.encryption_key
            hmac2 = encryption_service.hmac_key
        
        # Verify keys are the same
        assert key1 == key2
        assert hmac1 == hmac2
    
    @pytest.mark.asyncio
    async def test_encrypt_large_data(self, encryption_service): pass
        """Test encryption/decryption with large data."""
        # Initialize
        await encryption_service.initialize("test_password")
        
        # Generate large data (1MB)
        large_data = {
            "array": ["item" + str(i) for i in range(10000)],
            "nested": {
                "deep": {
                    "deeper": {
                        "deepest": "x" * 100000
                    }
                }
            }
        }
        
        # Encrypt
        encrypted = await encryption_service.encrypt(large_data)
        
        # Decrypt
        decrypted = await encryption_service.decrypt_json(encrypted)
        
        # Verify
        assert decrypted == large_data
    
    @pytest.mark.asyncio
    async def test_empty_data(self, encryption_service): pass
        """Test encryption/decryption with empty data."""
        # Initialize
        await encryption_service.initialize("test_password")
        
        # Empty data
        empty_dict = {}
        
        # Encrypt
        encrypted = await encryption_service.encrypt(empty_dict)
        
        # Decrypt
        decrypted = await encryption_service.decrypt_json(encrypted)
        
        # Verify
        assert decrypted == empty_dict
    
    @pytest.mark.asyncio
    async def test_non_initialized(self, encryption_service): pass
        """Test that using encryption without initialization raises exception."""
        # Attempt to encrypt without initialization
        with pytest.raises(Exception) as exc_info: pass
            await encryption_service.encrypt({"test": "data"})
        
        # Verify error message
        assert "not initialized" in str(exc_info.value).lower()
        
        # Create fake encrypted data (base64 string)
        encrypted = base64.b64encode(b"fake_encrypted_data").decode('utf-8')
        
        # Attempt to decrypt without initialization
        with pytest.raises(Exception) as exc_info: pass
            await encryption_service.decrypt_json(encrypted)
        
        # Verify error message
        assert "not initialized" in str(exc_info.value).lower() 