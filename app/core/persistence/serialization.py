"""
Serialization module for world data.

This module provides efficient serialization and deserialization functionality for world data,
supporting binary serialization, partial serialization, and schema versioning for backward compatibility.
"""

import pickle
import json
import gzip
import bz2
import lzma
import base64
import zlib
import msgpack
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union, Set, TypeVar, Generic, Callable
from datetime import datetime
import hashlib
import logging
from dataclasses import dataclass, asdict, field

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CompressionType(str, Enum):
    """Types of compression available for serialized data."""
    NONE = "none"
    GZIP = "gzip"
    BZ2 = "bz2"
    LZMA = "lzma"
    ZLIB = "zlib"

class SerializationFormat(str, Enum):
    """Available serialization formats."""
    JSON = "json"
    PICKLE = "pickle"
    MSGPACK = "msgpack"

@dataclass
class SerializedData:
    """Container for serialized data with metadata."""
    data: bytes
    format: SerializationFormat
    compression: CompressionType
    schema_version: str
    checksum: str
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = asdict(self)
        # Convert binary data to base64 for JSON compatibility
        result['data'] = base64.b64encode(self.data).decode('utf-8')
        return result

    @classmethod
    def from_dict(cls, data_dict: Dict[str, Any]) -> 'SerializedData':
        """Create from dictionary representation."""
        if 'data' in data_dict and isinstance(data_dict['data'], str):
            data_dict['data'] = base64.b64decode(data_dict['data'])
        return cls(**data_dict)

class SchemaVersion:
    """Manager for schema versioning."""
    
    CURRENT_VERSION = "1.0.0"
    
    @staticmethod
    def get_current_version() -> str:
        """Get the current schema version."""
        return SchemaVersion.CURRENT_VERSION
    
    @staticmethod
    def is_compatible(version: str) -> bool:
        """Check if a schema version is compatible with the current version."""
        # Simple semantic versioning check
        # Major version must match for compatibility
        if not version:
            return False
        
        current_parts = SchemaVersion.CURRENT_VERSION.split('.')
        version_parts = version.split('.')
        
        # Major version mismatch means incompatible
        if len(version_parts) < 1 or len(current_parts) < 1:
            return False
            
        return current_parts[0] == version_parts[0]
    
    @staticmethod
    def migrate_data(data: Dict[str, Any], from_version: str) -> Dict[str, Any]:
        """Migrate data from a previous schema version to the current version."""
        if SchemaVersion.is_compatible(from_version):
            # For compatible versions, apply incremental migrations
            # This is a placeholder for actual migration logic
            current_parts = SchemaVersion.CURRENT_VERSION.split('.')
            version_parts = from_version.split('.')
            
            # Apply migrations for minor and patch version differences
            # Example migrations would go here
            logger.info(f"Migrated data from schema {from_version} to {SchemaVersion.CURRENT_VERSION}")
            
            return data
        else:
            # For incompatible versions, we would need a more complex migration strategy
            # or potentially reject the data
            raise ValueError(f"Schema version {from_version} is not compatible with current version {SchemaVersion.CURRENT_VERSION}")

def _compress_data(data: bytes, compression: CompressionType) -> bytes:
    """Compress binary data using the specified compression method."""
    if compression == CompressionType.NONE:
        return data
    elif compression == CompressionType.GZIP:
        return gzip.compress(data)
    elif compression == CompressionType.BZ2:
        return bz2.compress(data)
    elif compression == CompressionType.LZMA:
        return lzma.compress(data)
    elif compression == CompressionType.ZLIB:
        return zlib.compress(data)
    else:
        raise ValueError(f"Unsupported compression type: {compression}")

def _decompress_data(data: bytes, compression: CompressionType) -> bytes:
    """Decompress binary data using the specified compression method."""
    if compression == CompressionType.NONE:
        return data
    elif compression == CompressionType.GZIP:
        return gzip.decompress(data)
    elif compression == CompressionType.BZ2:
        return bz2.decompress(data)
    elif compression == CompressionType.LZMA:
        return lzma.decompress(data)
    elif compression == CompressionType.ZLIB:
        return zlib.decompress(data)
    else:
        raise ValueError(f"Unsupported compression type: {compression}")

def _calculate_checksum(data: bytes) -> str:
    """Calculate SHA-256 checksum for data integrity verification."""
    return hashlib.sha256(data).hexdigest()

def _serialize_data(data: Any, format: SerializationFormat) -> bytes:
    """Serialize data to binary format."""
    if format == SerializationFormat.JSON:
        return json.dumps(data).encode('utf-8')
    elif format == SerializationFormat.PICKLE:
        return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    elif format == SerializationFormat.MSGPACK:
        return msgpack.packb(data, use_bin_type=True)
    else:
        raise ValueError(f"Unsupported serialization format: {format}")

def _deserialize_data(data: bytes, format: SerializationFormat) -> Any:
    """Deserialize data from binary format."""
    if format == SerializationFormat.JSON:
        return json.loads(data.decode('utf-8'))
    elif format == SerializationFormat.PICKLE:
        return pickle.loads(data)
    elif format == SerializationFormat.MSGPACK:
        return msgpack.unpackb(data, raw=False)
    else:
        raise ValueError(f"Unsupported serialization format: {format}")

def serialize(
    data: Any,
    format: SerializationFormat = SerializationFormat.JSON,
    compression: CompressionType = CompressionType.ZLIB,
    metadata: Optional[Dict[str, Any]] = None
) -> SerializedData:
    """
    Serialize data with optional compression and metadata.
    
    Args:
        data: Data to serialize
        format: Serialization format to use
        compression: Compression method to use
        metadata: Optional metadata to include
        
    Returns:
        SerializedData object containing the serialized data and metadata
    """
    # Serialize to the chosen format
    serialized = _serialize_data(data, format)
    
    # Compress the serialized data
    compressed = _compress_data(serialized, compression)
    
    # Calculate checksum for data integrity
    checksum = _calculate_checksum(compressed)
    
    # Create metadata if not provided
    if metadata is None:
        metadata = {}
        
    # Create serialized data container
    return SerializedData(
        data=compressed,
        format=format,
        compression=compression,
        schema_version=SchemaVersion.get_current_version(),
        checksum=checksum,
        created_at=datetime.utcnow().isoformat(),
        metadata=metadata
    )

def deserialize(serialized_data: SerializedData) -> Any:
    """
    Deserialize data from a SerializedData object.
    
    Args:
        serialized_data: SerializedData object containing the serialized data
        
    Returns:
        Deserialized data
        
    Raises:
        ValueError: If checksum verification fails or schema version is incompatible
    """
    # Verify data integrity with checksum
    calculated_checksum = _calculate_checksum(serialized_data.data)
    if calculated_checksum != serialized_data.checksum:
        raise ValueError("Data integrity check failed: checksum mismatch")
    
    # Check schema compatibility
    if not SchemaVersion.is_compatible(serialized_data.schema_version):
        raise ValueError(f"Schema version {serialized_data.schema_version} is not compatible with current version {SchemaVersion.get_current_version()}")
    
    # Decompress data
    decompressed = _decompress_data(serialized_data.data, serialized_data.compression)
    
    # Deserialize data
    return _deserialize_data(decompressed, serialized_data.format)

def partial_serialize(
    full_data: Dict[str, Any],
    changed_keys: Set[str],
    format: SerializationFormat = SerializationFormat.JSON,
    compression: CompressionType = CompressionType.ZLIB
) -> SerializedData:
    """
    Serialize only changed parts of data for incremental saves.
    
    Args:
        full_data: Complete data dictionary
        changed_keys: Set of keys that have changed
        format: Serialization format to use
        compression: Compression method to use
        
    Returns:
        SerializedData object containing only the changed data
    """
    partial_data = {
        'partial': True,
        'keys': list(changed_keys),
        'data': {k: full_data[k] for k in changed_keys if k in full_data}
    }
    
    metadata = {
        'is_partial': True,
        'included_keys': list(changed_keys)
    }
    
    return serialize(partial_data, format, compression, metadata)

def merge_partial_data(
    base_data: Dict[str, Any],
    partial_serialized: SerializedData
) -> Dict[str, Any]:
    """
    Merge partial serialized data into base data.
    
    Args:
        base_data: Base data to update
        partial_serialized: SerializedData containing partial updates
        
    Returns:
        Updated data dictionary
    """
    # Deserialize partial data
    partial = deserialize(partial_serialized)
    
    if not isinstance(partial, dict) or not partial.get('partial', False):
        raise ValueError("Invalid partial data format")
    
    # Extract changed data
    changed_data = partial.get('data', {})
    
    # Create a copy of base data
    result = base_data.copy()
    
    # Apply changes
    result.update(changed_data)
    
    return result 