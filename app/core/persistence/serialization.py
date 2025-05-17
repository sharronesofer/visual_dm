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
import time
from collections import defaultdict, deque

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

try:
    import msgpack
    HAS_MSGPACK = True
except ImportError:
    HAS_MSGPACK = False

def _serialize_data(data: Any, format: SerializationFormat) -> bytes:
    """
    Serialize data to bytes using the specified format. Uses msgpack for performance if available.
    """
    if format == SerializationFormat.MSGPACK or (format == SerializationFormat.JSON and HAS_MSGPACK):
        # Use msgpack for binary serialization if available
        return msgpack.packb(data, use_bin_type=True) if HAS_MSGPACK else json.dumps(data).encode('utf-8')
    elif format == SerializationFormat.JSON:
        return json.dumps(data).encode('utf-8')
    elif format == SerializationFormat.PICKLE:
        import pickle
        return pickle.dumps(data)
    else:
        raise ValueError(f"Unsupported serialization format: {format}")

def _deserialize_data(data: bytes, format: SerializationFormat) -> Any:
    """
    Deserialize bytes to data using the specified format. Uses msgpack for performance if available.
    """
    if format == SerializationFormat.MSGPACK or (format == SerializationFormat.JSON and HAS_MSGPACK):
        return msgpack.unpackb(data, raw=False) if HAS_MSGPACK else json.loads(data.decode('utf-8'))
    elif format == SerializationFormat.JSON:
        return json.loads(data.decode('utf-8'))
    elif format == SerializationFormat.PICKLE:
        import pickle
        return pickle.loads(data)
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

def benchmark_compression_algorithms(data: bytes, repeat: int = 3) -> Dict[str, Dict[str, Any]]:
    """
    Benchmark available compression algorithms for a given data payload.
    Returns a dict with size and speed metrics for each algorithm.
    """
    results = {}
    for comp in [CompressionType.ZLIB, CompressionType.LZMA, CompressionType.BZ2, CompressionType.GZIP, CompressionType.NONE]:
        # Compression
        comp_times = []
        comp_sizes = []
        for _ in range(repeat):
            start = time.perf_counter()
            compressed = _compress_data(data, comp)
            comp_times.append(time.perf_counter() - start)
            comp_sizes.append(len(compressed))
        # Decompression
        decomp_times = []
        for _ in range(repeat):
            compressed = _compress_data(data, comp)
            start = time.perf_counter()
            _ = _decompress_data(compressed, comp)
            decomp_times.append(time.perf_counter() - start)
        results[comp.value] = {
            'avg_compress_time': sum(comp_times) / repeat,
            'avg_decompress_time': sum(decomp_times) / repeat,
            'avg_size': sum(comp_sizes) / repeat
        }
    return results

def select_compression_preset(preset: str = 'balanced') -> CompressionType:
    """
    Select a compression algorithm based on preset: 'fast', 'balanced', 'small'.
    """
    if preset == 'fast':
        return CompressionType.ZLIB
    elif preset == 'small':
        return CompressionType.LZMA
    elif preset == 'balanced':
        return CompressionType.GZIP
    else:
        return CompressionType.ZLIB

class SceneDependencyGraph:
    """
    Tracks dependencies between scene components for partial scene restoration.
    Nodes are component IDs; edges represent dependencies (A -> B means A depends on B).
    """
    def __init__(self):
        self.graph = defaultdict(set)  # node -> set of dependencies
        self.reverse_graph = defaultdict(set)  # node -> set of dependents

    def add_node(self, node_id: str):
        self.graph[node_id]  # Ensure node exists

    def add_dependency(self, node_id: str, depends_on_id: str):
        self.graph[node_id].add(depends_on_id)
        self.reverse_graph[depends_on_id].add(node_id)

    def get_dependencies(self, node_id: str) -> set:
        return self.graph.get(node_id, set())

    def get_dependents(self, node_id: str) -> set:
        return self.reverse_graph.get(node_id, set())

    def topological_sort(self, subset: set = None) -> list:
        """
        Return a topological sort of the graph (or a subset of nodes).
        Raises ValueError if a cycle is detected.
        """
        in_degree = {node: 0 for node in (subset or self.graph.keys())}
        for node in in_degree:
            for dep in self.graph[node]:
                if subset is None or dep in in_degree:
                    in_degree[dep] += 1
        queue = deque([n for n, d in in_degree.items() if d == 0])
        result = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for dep in self.reverse_graph[node]:
                if subset is None or dep in in_degree:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        queue.append(dep)
        if len(result) != len(in_degree):
            raise ValueError("Cycle detected in dependency graph")
        return result

    def has_cycle(self) -> bool:
        try:
            self.topological_sort()
            return False
        except ValueError:
            return True

def extract_scene_dependency_graph(world_data: dict, extra_dicts: dict = None) -> SceneDependencyGraph:
    """
    Extracts a dependency graph from world_data and related dicts.
    Looks for fields like 'references', 'dependencies', 'parent_id', etc. in each component.
    Returns a SceneDependencyGraph representing all dependencies for partial restoration.
    Args:
        world_data: The main world data dict (from WorldState)
        extra_dicts: Optional dict of additional component dicts (e.g., npcs, factions)
    Returns:
        SceneDependencyGraph
    """
    graph = SceneDependencyGraph()
    # Helper to process a component dict
    def process_component(cid, comp):
        graph.add_node(cid)
        # Common dependency fields
        for key in ('references', 'dependencies', 'parents', 'parent_id', 'children', 'child_ids'):
            val = comp.get(key)
            if isinstance(val, list):
                for dep in val:
                    if isinstance(dep, str):
                        graph.add_dependency(cid, dep)
            elif isinstance(val, str):
                graph.add_dependency(cid, val)
            elif isinstance(val, dict):
                for dep in val.values():
                    if isinstance(dep, str):
                        graph.add_dependency(cid, dep)
    # Process world_data components
    for cid, comp in world_data.items():
        if isinstance(comp, dict):
            process_component(cid, comp)
    # Process extra dicts (e.g., npcs, factions)
    if extra_dicts:
        for d in extra_dicts.values():
            for cid, comp in d.items():
                if isinstance(comp, dict):
                    process_component(cid, comp)
    return graph 

def resolve_component_references(loaded_components: dict, log_missing: bool = True) -> None:
    """
    Ensures all references in loaded components point to other loaded components.
    For each component, scans fields like 'references', 'dependencies', 'parent_id', etc.
    If a referenced ID is missing, sets it to None or logs a warning.
    Args:
        loaded_components: Dict of component_id -> component dict
        log_missing: If True, logs a warning for missing references
    Modifies loaded_components in place.
    """
    valid_ids = set(loaded_components.keys())
    for cid, comp in loaded_components.items():
        for key in ('references', 'dependencies', 'parents', 'parent_id', 'children', 'child_ids'):
            if key in comp:
                val = comp[key]
                if isinstance(val, list):
                    new_val = []
                    for ref in val:
                        if ref in valid_ids:
                            new_val.append(ref)
                        else:
                            if log_missing:
                                logger.warning(f"Component {cid}: reference '{ref}' in '{key}' not loaded.")
                    comp[key] = new_val
                elif isinstance(val, str):
                    if val not in valid_ids:
                        if log_missing:
                            logger.warning(f"Component {cid}: reference '{val}' in '{key}' not loaded.")
                        comp[key] = None
                elif isinstance(val, dict):
                    new_val = {}
                    for k, ref in val.items():
                        if ref in valid_ids:
                            new_val[k] = ref
                        else:
                            if log_missing:
                                logger.warning(f"Component {cid}: reference '{ref}' in '{key}[{k}]' not loaded.")
                    comp[key] = new_val 