"""
Memory Associations System.

This module manages relationships and associations between memories,
enabling complex memory networks and retrieval patterns.
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple
from pydantic import BaseModel
from datetime import datetime
import uuid


class AssociationType(Enum):
    """Types of associations between memories."""
    
    # Temporal associations
    FOLLOWS = "follows"                 # Memory B follows Memory A in time
    PRECEDES = "precedes"              # Memory A precedes Memory B
    SIMULTANEOUS = "simultaneous"      # Memories occurred at the same time
    
    # Causal associations
    CAUSES = "causes"                  # Memory A caused Memory B
    CAUSED_BY = "caused_by"            # Memory A was caused by Memory B
    ENABLES = "enables"                # Memory A enabled Memory B
    PREVENTS = "prevents"              # Memory A prevented Memory B
    
    # Similarity associations
    SIMILAR_TO = "similar_to"          # Memories are similar in content
    OPPOSITE_TO = "opposite_to"        # Memories are opposite in nature
    RELATED_TO = "related_to"          # General relationship
    
    # Contextual associations
    SAME_LOCATION = "same_location"    # Occurred in the same place
    SAME_PEOPLE = "same_people"        # Involved the same people
    SAME_ACTIVITY = "same_activity"    # Same type of activity
    
    # Emotional associations
    SAME_EMOTION = "same_emotion"      # Evoked similar emotions
    CONTRASTING_EMOTION = "contrasting_emotion"  # Evoked opposite emotions
    
    # Hierarchical associations
    PART_OF = "part_of"                # Memory A is part of larger Memory B
    CONTAINS = "contains"              # Memory A contains Memory B
    GENERALIZES = "generalizes"        # Memory A is a generalization of B
    SPECIALIZES = "specializes"        # Memory A is a specialization of B


class MemoryAssociation(BaseModel):
    """Represents an association between two memories."""
    
    id: str
    source_memory_id: str
    target_memory_id: str
    association_type: AssociationType
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    created_at: str
    metadata: Dict[str, Any] = {}
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        if 'created_at' not in data:
            data['created_at'] = datetime.now().isoformat()
        super().__init__(**data)


class AssociationNetwork:
    """Manages a network of memory associations."""
    
    def __init__(self):
        self.associations: Dict[str, MemoryAssociation] = {}
        self.memory_associations: Dict[str, List[str]] = {}  # memory_id -> association_ids
    
    def add_association(self, association: MemoryAssociation) -> None:
        """Add an association to the network."""
        self.associations[association.id] = association
        
        # Update memory association mappings
        if association.source_memory_id not in self.memory_associations:
            self.memory_associations[association.source_memory_id] = []
        if association.target_memory_id not in self.memory_associations:
            self.memory_associations[association.target_memory_id] = []
        
        self.memory_associations[association.source_memory_id].append(association.id)
        self.memory_associations[association.target_memory_id].append(association.id)
    
    def get_associations_for_memory(self, memory_id: str) -> List[MemoryAssociation]:
        """Get all associations involving a specific memory."""
        if memory_id not in self.memory_associations:
            return []
        
        return [self.associations[assoc_id] 
                for assoc_id in self.memory_associations[memory_id]
                if assoc_id in self.associations]
    
    def get_related_memories(self, memory_id: str, 
                           association_types: Optional[List[AssociationType]] = None,
                           min_strength: float = 0.0) -> List[Tuple[str, MemoryAssociation]]:
        """Get memories related to a given memory."""
        related = []
        associations = self.get_associations_for_memory(memory_id)
        
        for assoc in associations:
            if association_types and assoc.association_type not in association_types:
                continue
            if assoc.strength < min_strength:
                continue
            
            # Determine the related memory ID
            if assoc.source_memory_id == memory_id:
                related_memory_id = assoc.target_memory_id
            else:
                related_memory_id = assoc.source_memory_id
            
            related.append((related_memory_id, assoc))
        
        return related
    
    def remove_association(self, association_id: str) -> bool:
        """Remove an association from the network."""
        if association_id not in self.associations:
            return False
        
        association = self.associations[association_id]
        
        # Remove from memory association mappings
        if association.source_memory_id in self.memory_associations:
            if association_id in self.memory_associations[association.source_memory_id]:
                self.memory_associations[association.source_memory_id].remove(association_id)
        
        if association.target_memory_id in self.memory_associations:
            if association_id in self.memory_associations[association.target_memory_id]:
                self.memory_associations[association.target_memory_id].remove(association_id)
        
        # Remove the association itself
        del self.associations[association_id]
        return True


def detect_temporal_associations(memory_a: Dict[str, Any], memory_b: Dict[str, Any]) -> Optional[MemoryAssociation]:
    """Detect temporal associations between two memories."""
    created_a = memory_a.get('created_at')
    created_b = memory_b.get('created_at')
    
    if not created_a or not created_b:
        return None
    
    try:
        time_a = datetime.fromisoformat(created_a.replace('Z', '+00:00'))
        time_b = datetime.fromisoformat(created_b.replace('Z', '+00:00'))
        
        time_diff = abs((time_a - time_b).total_seconds())
        
        # If very close in time (within 5 minutes), consider simultaneous
        if time_diff < 300:
            return MemoryAssociation(
                source_memory_id=memory_a['id'],
                target_memory_id=memory_b['id'],
                association_type=AssociationType.SIMULTANEOUS,
                strength=1.0 - (time_diff / 300),  # Closer = stronger
                confidence=0.9
            )
        
        # If within reasonable sequence (within 1 hour), consider follows/precedes
        elif time_diff < 3600:
            if time_a < time_b:
                return MemoryAssociation(
                    source_memory_id=memory_a['id'],
                    target_memory_id=memory_b['id'],
                    association_type=AssociationType.FOLLOWS,
                    strength=1.0 - (time_diff / 3600),
                    confidence=0.7
                )
            else:
                return MemoryAssociation(
                    source_memory_id=memory_b['id'],
                    target_memory_id=memory_a['id'],
                    association_type=AssociationType.FOLLOWS,
                    strength=1.0 - (time_diff / 3600),
                    confidence=0.7
                )
    
    except (ValueError, TypeError):
        pass
    
    return None


def detect_content_associations(memory_a: Dict[str, Any], memory_b: Dict[str, Any]) -> Optional[MemoryAssociation]:
    """Detect content-based associations between two memories."""
    content_a = memory_a.get('content', '').lower()
    content_b = memory_b.get('content', '').lower()
    
    if not content_a or not content_b:
        return None
    
    # Calculate word overlap
    words_a = set(content_a.split())
    words_b = set(content_b.split())
    
    common_words = words_a.intersection(words_b)
    total_words = words_a.union(words_b)
    
    if len(total_words) == 0:
        return None
    
    similarity = len(common_words) / len(total_words)
    
    # If high similarity, create association
    if similarity > 0.3:
        return MemoryAssociation(
            source_memory_id=memory_a['id'],
            target_memory_id=memory_b['id'],
            association_type=AssociationType.SIMILAR_TO,
            strength=similarity,
            confidence=0.6,
            metadata={'common_words': list(common_words)}
        )
    
    return None


def detect_category_associations(memory_a: Dict[str, Any], memory_b: Dict[str, Any]) -> Optional[MemoryAssociation]:
    """Detect category-based associations between two memories."""
    categories_a = set(memory_a.get('categories', []))
    categories_b = set(memory_b.get('categories', []))
    
    if not categories_a or not categories_b:
        return None
    
    common_categories = categories_a.intersection(categories_b)
    
    if common_categories:
        # Calculate category overlap strength
        total_categories = categories_a.union(categories_b)
        strength = len(common_categories) / len(total_categories)
        
        return MemoryAssociation(
            source_memory_id=memory_a['id'],
            target_memory_id=memory_b['id'],
            association_type=AssociationType.RELATED_TO,
            strength=strength,
            confidence=0.8,
            metadata={'common_categories': list(common_categories)}
        )
    
    return None


def detect_emotional_associations(memory_a: Dict[str, Any], memory_b: Dict[str, Any]) -> Optional[MemoryAssociation]:
    """Detect emotional associations between memories."""
    # Check for emotional keywords in content
    emotional_keywords = {
        'positive': ['happy', 'joy', 'love', 'excited', 'pleased', 'satisfied', 'proud'],
        'negative': ['sad', 'angry', 'fear', 'hate', 'disappointed', 'frustrated', 'hurt'],
        'neutral': ['calm', 'peaceful', 'content', 'relaxed']
    }
    
    def get_emotional_tone(content: str) -> Optional[str]:
        content_lower = content.lower()
        for tone, keywords in emotional_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return tone
        return None
    
    content_a = memory_a.get('content', '')
    content_b = memory_b.get('content', '')
    
    tone_a = get_emotional_tone(content_a)
    tone_b = get_emotional_tone(content_b)
    
    if tone_a and tone_b:
        if tone_a == tone_b:
            return MemoryAssociation(
                source_memory_id=memory_a['id'],
                target_memory_id=memory_b['id'],
                association_type=AssociationType.SAME_EMOTION,
                strength=0.7,
                confidence=0.6,
                metadata={'emotional_tone': tone_a}
            )
        elif (tone_a == 'positive' and tone_b == 'negative') or (tone_a == 'negative' and tone_b == 'positive'):
            return MemoryAssociation(
                source_memory_id=memory_a['id'],
                target_memory_id=memory_b['id'],
                association_type=AssociationType.CONTRASTING_EMOTION,
                strength=0.6,
                confidence=0.5,
                metadata={'emotional_tones': [tone_a, tone_b]}
            )
    
    return None


def auto_detect_associations(memory_a: Dict[str, Any], memory_b: Dict[str, Any]) -> List[MemoryAssociation]:
    """Automatically detect all possible associations between two memories."""
    associations = []
    
    # Try different detection methods
    detection_methods = [
        detect_temporal_associations,
        detect_content_associations,
        detect_category_associations,
        detect_emotional_associations
    ]
    
    for method in detection_methods:
        try:
            association = method(memory_a, memory_b)
            if association:
                associations.append(association)
        except Exception:
            # Skip failed detection methods
            continue
    
    return associations


def build_association_network(memories: List[Dict[str, Any]]) -> AssociationNetwork:
    """Build a complete association network from a list of memories."""
    network = AssociationNetwork()
    
    # Compare each memory with every other memory
    for i, memory_a in enumerate(memories):
        for j, memory_b in enumerate(memories):
            if i >= j:  # Avoid duplicate comparisons and self-comparison
                continue
            
            associations = auto_detect_associations(memory_a, memory_b)
            for association in associations:
                network.add_association(association)
    
    return network


def get_memory_cluster(network: AssociationNetwork, memory_id: str, 
                      max_depth: int = 2, min_strength: float = 0.3) -> Set[str]:
    """Get a cluster of related memories using network traversal."""
    cluster = {memory_id}
    to_explore = [(memory_id, 0)]  # (memory_id, depth)
    
    while to_explore:
        current_memory, depth = to_explore.pop(0)
        
        if depth >= max_depth:
            continue
        
        related = network.get_related_memories(current_memory, min_strength=min_strength)
        
        for related_memory_id, association in related:
            if related_memory_id not in cluster:
                cluster.add(related_memory_id)
                to_explore.append((related_memory_id, depth + 1))
    
    return cluster


def get_association_summary(network: AssociationNetwork, memory_id: str) -> Dict[str, Any]:
    """Get a summary of associations for a memory."""
    associations = network.get_associations_for_memory(memory_id)
    
    if not associations:
        return {"memory_id": memory_id, "association_count": 0, "associations": []}
    
    # Group by association type
    by_type = {}
    for assoc in associations:
        assoc_type = assoc.association_type.value
        if assoc_type not in by_type:
            by_type[assoc_type] = []
        by_type[assoc_type].append({
            "target_memory": assoc.target_memory_id if assoc.source_memory_id == memory_id else assoc.source_memory_id,
            "strength": assoc.strength,
            "confidence": assoc.confidence
        })
    
    return {
        "memory_id": memory_id,
        "association_count": len(associations),
        "associations_by_type": by_type,
        "average_strength": sum(a.strength for a in associations) / len(associations),
        "average_confidence": sum(a.confidence for a in associations) / len(associations)
    }
