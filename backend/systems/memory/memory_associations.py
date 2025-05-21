"""
This module defines memory associations and relationship types for the memory system.
It provides utilities for creating, managing, and querying memory relationships.
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Any, Tuple

class MemoryAssociationType(str, Enum):
    """Types of associations between memories."""
    CAUSE = "cause"                # Memory A caused Memory B
    EFFECT = "effect"              # Memory A is effect of Memory B
    CONTRADICTS = "contradicts"    # Memory A contradicts Memory B
    SUPPORTS = "supports"          # Memory A supports/confirms Memory B
    PRECEDES = "precedes"          # Memory A happened before Memory B
    FOLLOWS = "follows"            # Memory A happened after Memory B
    RELATED = "related"            # Memory A is generally related to Memory B
    SUPERSEDES = "supersedes"      # Memory A replaces/updates Memory B
    PART_OF = "part_of"            # Memory A is part of larger Memory B
    CONTAINS = "contains"          # Memory A contains smaller Memory B
    REFERENCES = "references"      # Memory A mentions/references Memory B


class MemoryAssociation:
    """Represents an association between two memories."""
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        association_type: MemoryAssociationType,
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a memory association.
        
        Args:
            source_id: ID of the source memory
            target_id: ID of the target memory
            association_type: Type of association
            strength: Association strength (0.0-1.0)
            metadata: Optional additional metadata
        """
        self.source_id = source_id
        self.target_id = target_id
        self.association_type = association_type
        self.strength = max(0.0, min(1.0, strength))  # Clamp to 0.0-1.0
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "association_type": self.association_type.value,
            "strength": self.strength,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryAssociation':
        """Create from dictionary representation."""
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            association_type=MemoryAssociationType(data["association_type"]),
            strength=data.get("strength", 1.0),
            metadata=data.get("metadata", {})
        )
    
    def get_inverse_association_type(self) -> MemoryAssociationType:
        """Get the inverse association type for bidirectional relationships."""
        inverse_map = {
            MemoryAssociationType.CAUSE: MemoryAssociationType.EFFECT,
            MemoryAssociationType.EFFECT: MemoryAssociationType.CAUSE,
            MemoryAssociationType.PRECEDES: MemoryAssociationType.FOLLOWS,
            MemoryAssociationType.FOLLOWS: MemoryAssociationType.PRECEDES,
            MemoryAssociationType.CONTRADICTS: MemoryAssociationType.CONTRADICTS,
            MemoryAssociationType.SUPPORTS: MemoryAssociationType.SUPPORTS,
            MemoryAssociationType.PART_OF: MemoryAssociationType.CONTAINS,
            MemoryAssociationType.CONTAINS: MemoryAssociationType.PART_OF,
            MemoryAssociationType.REFERENCES: MemoryAssociationType.REFERENCES,
            MemoryAssociationType.SUPERSEDES: MemoryAssociationType.SUPERSEDES,
            MemoryAssociationType.RELATED: MemoryAssociationType.RELATED
        }
        
        return inverse_map.get(self.association_type, MemoryAssociationType.RELATED)


class MemoryAssociationManager:
    """Manager for memory associations and relationships."""
    
    def __init__(self):
        """Initialize the memory association manager."""
        self.associations: Dict[str, List[MemoryAssociation]] = {}
        
    def add_association(
        self,
        source_id: str,
        target_id: str,
        association_type: MemoryAssociationType,
        strength: float = 1.0,
        bidirectional: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[MemoryAssociation, Optional[MemoryAssociation]]:
        """
        Add an association between two memories.
        
        Args:
            source_id: ID of the source memory
            target_id: ID of the target memory
            association_type: Type of association
            strength: Association strength (0.0-1.0)
            bidirectional: Whether to create the inverse association automatically
            metadata: Optional additional metadata
            
        Returns:
            Tuple of (primary association, inverse association or None)
        """
        # Create the primary association
        association = MemoryAssociation(
            source_id=source_id,
            target_id=target_id,
            association_type=association_type,
            strength=strength,
            metadata=metadata
        )
        
        # Add the association to the source memory's associations
        if source_id not in self.associations:
            self.associations[source_id] = []
        self.associations[source_id].append(association)
        
        # Create inverse association if bidirectional
        inverse_association = None
        if bidirectional:
            inverse_type = association.get_inverse_association_type()
            inverse_association = MemoryAssociation(
                source_id=target_id,
                target_id=source_id,
                association_type=inverse_type,
                strength=strength,
                metadata=metadata.copy() if metadata else None
            )
            
            # Add the inverse association to the target memory's associations
            if target_id not in self.associations:
                self.associations[target_id] = []
            self.associations[target_id].append(inverse_association)
        
        return association, inverse_association
    
    def remove_association(
        self,
        source_id: str,
        target_id: str,
        association_type: Optional[MemoryAssociationType] = None,
        bidirectional: bool = True
    ) -> bool:
        """
        Remove an association between two memories.
        
        Args:
            source_id: ID of the source memory
            target_id: ID of the target memory
            association_type: Optional type of association to remove (None for any)
            bidirectional: Whether to remove inverse associations automatically
            
        Returns:
            True if association was removed, False otherwise
        """
        removed = False
        
        # Remove associations from source to target
        if source_id in self.associations:
            original_count = len(self.associations[source_id])
            
            # Filter out the associations to remove
            self.associations[source_id] = [
                assoc for assoc in self.associations[source_id]
                if assoc.target_id != target_id or (
                    association_type is not None and
                    assoc.association_type != association_type
                )
            ]
            
            removed = len(self.associations[source_id]) < original_count
            
            # Clean up empty association lists
            if not self.associations[source_id]:
                del self.associations[source_id]
        
        # Remove inverse associations if bidirectional
        if bidirectional and target_id in self.associations:
            original_count = len(self.associations[target_id])
            
            # Filter out the inverse associations
            self.associations[target_id] = [
                assoc for assoc in self.associations[target_id]
                if assoc.target_id != source_id or (
                    association_type is not None and
                    assoc.association_type != association_type.get_inverse_association_type()
                    if association_type else False
                )
            ]
            
            removed = removed or len(self.associations[target_id]) < original_count
            
            # Clean up empty association lists
            if not self.associations[target_id]:
                del self.associations[target_id]
        
        return removed
    
    def get_associations(
        self,
        memory_id: str,
        association_types: Optional[List[MemoryAssociationType]] = None
    ) -> List[MemoryAssociation]:
        """
        Get all associations for a memory.
        
        Args:
            memory_id: ID of the memory
            association_types: Optional list of association types to filter by
            
        Returns:
            List of associations for the memory
        """
        if memory_id not in self.associations:
            return []
        
        # Filter by association type if specified
        if association_types:
            return [
                assoc for assoc in self.associations[memory_id]
                if assoc.association_type in association_types
            ]
        
        return self.associations[memory_id].copy()
    
    def get_related_memories(
        self,
        memory_id: str,
        association_types: Optional[List[MemoryAssociationType]] = None,
        min_strength: float = 0.0
    ) -> List[str]:
        """
        Get IDs of memories related to the given memory.
        
        Args:
            memory_id: ID of the memory
            association_types: Optional list of association types to filter by
            min_strength: Minimum association strength to include
            
        Returns:
            List of related memory IDs
        """
        associations = self.get_associations(memory_id, association_types)
        
        # Filter by strength and extract target IDs
        return [
            assoc.target_id for assoc in associations
            if assoc.strength >= min_strength
        ]
    
    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """Convert all associations to a dictionary representation."""
        result = {}
        
        for memory_id, associations in self.associations.items():
            result[memory_id] = [assoc.to_dict() for assoc in associations]
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, List[Dict[str, Any]]]) -> 'MemoryAssociationManager':
        """Create from a dictionary representation."""
        manager = cls()
        
        for memory_id, association_dicts in data.items():
            manager.associations[memory_id] = [
                MemoryAssociation.from_dict(assoc_dict)
                for assoc_dict in association_dicts
            ]
        
        return manager


def detect_memory_associations(
    memory_a_content: str,
    memory_b_content: str
) -> List[MemoryAssociationType]:
    """
    Detect likely associations between two memories based on their content.
    
    Args:
        memory_a_content: Content of the first memory
        memory_b_content: Content of the second memory
        
    Returns:
        List of detected association types
    """
    # This is a simple keyword-based detection
    # In a real implementation, this would use more sophisticated NLP
    
    associations = []
    a_lower = memory_a_content.lower()
    b_lower = memory_b_content.lower()
    
    # Causal relationship detection
    if any(phrase in b_lower for phrase in ["because of", "due to", "as a result of"]) and \
       any(keyword in b_lower for keyword in a_lower.split()):
        associations.append(MemoryAssociationType.EFFECT)
    
    # Contradictory information detection
    if any(phrase in a_lower for phrase in ["never", "impossible", "untrue"]) and \
       any(phrase in b_lower for phrase in ["always", "definitely", "true"]):
        associations.append(MemoryAssociationType.CONTRADICTS)
    
    # Referential relationship detection
    if any(keyword in b_lower for keyword in a_lower.split()):
        associations.append(MemoryAssociationType.REFERENCES)
    
    # Temporal relationship detection (very simple)
    a_time_indicators = ["before", "earlier", "previously", "first"]
    b_time_indicators = ["after", "later", "subsequently", "then"]
    
    if any(indicator in a_lower for indicator in a_time_indicators) and \
       any(indicator in b_lower for indicator in b_time_indicators):
        associations.append(MemoryAssociationType.PRECEDES)
    
    return associations 