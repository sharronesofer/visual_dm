"""
Memory Association Network System
--------------------------------

Implements sophisticated association detection, network optimization, and storage
for creating rich connections between memories in the memory system.
"""

from typing import Dict, List, Optional, Any, Tuple, Set, TYPE_CHECKING
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import math
import asyncio
from collections import defaultdict, deque

if TYPE_CHECKING:
    from backend.systems.memory.services.memory import Memory
    from backend.systems.memory.memory_categories import MemoryCategory

logger = logging.getLogger(__name__)


class AssociationType(Enum):
    """Types of memory associations."""
    
    # Temporal associations
    TEMPORAL_SEQUENCE = "temporal_sequence"      # Memories that occurred close in time
    TEMPORAL_CAUSAL = "temporal_causal"          # One memory caused another
    
    # Semantic associations
    SEMANTIC_SIMILAR = "semantic_similar"        # Similar content/topics
    SEMANTIC_OPPOSITE = "semantic_opposite"      # Contrasting content
    SEMANTIC_ELABORATION = "semantic_elaboration" # One elaborates on another
    
    # Entity-based associations
    ENTITY_SAME_PERSON = "entity_same_person"    # Same person involved
    ENTITY_SAME_LOCATION = "entity_same_location" # Same location
    ENTITY_SAME_FACTION = "entity_same_faction"   # Same faction
    
    # Emotional associations
    EMOTIONAL_SIMILAR = "emotional_similar"      # Similar emotional valence
    EMOTIONAL_TRIGGER = "emotional_trigger"      # One triggers emotion in another
    
    # Behavioral associations
    BEHAVIORAL_PATTERN = "behavioral_pattern"    # Part of recurring behavior
    BEHAVIORAL_CONSEQUENCE = "behavioral_consequence" # Behavior and its result


@dataclass
class MemoryAssociation:
    """Represents an association between two memories."""
    
    memory_a_id: str
    memory_b_id: str
    association_type: AssociationType
    strength: float  # 0.0 to 1.0
    confidence: float  # How confident we are in this association
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_reinforced: datetime = field(default_factory=datetime.utcnow)
    reinforcement_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AssociationCluster:
    """Represents a cluster of related memories."""
    
    cluster_id: str
    memory_ids: Set[str]
    cluster_theme: str
    cluster_importance: float
    association_types: Set[AssociationType]
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_memory(self, memory_id: str):
        """Add memory to cluster."""
        self.memory_ids.add(memory_id)
    
    def remove_memory(self, memory_id: str):
        """Remove memory from cluster."""
        self.memory_ids.discard(memory_id)


@dataclass
class NetworkAnalysisResult:
    """Result of network analysis operation."""
    
    entity_id: str
    total_memories: int
    total_associations: int
    clusters_found: int
    average_connectivity: float
    highly_connected_memories: List[str]  # Memory IDs with many connections
    isolated_memories: List[str]  # Memory IDs with few/no connections
    strongest_associations: List[MemoryAssociation]
    analysis_timestamp: datetime


class MemoryAssociationNetwork:
    """Manages memory associations and network analysis."""
    
    def __init__(self, memory_manager=None):
        self.memory_manager = memory_manager
        self.associations: Dict[str, List[MemoryAssociation]] = defaultdict(list)
        self.clusters: Dict[str, AssociationCluster] = {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.min_association_strength = 0.3
        self.max_associations_per_memory = 20
        self.cluster_size_threshold = 3
        self.temporal_window_hours = 24  # Hours for temporal associations
    
    async def detect_associations(self, entity_id: str, memory_ids: Optional[List[str]] = None) -> List[MemoryAssociation]:
        """Detect associations between memories for an entity."""
        if not self.memory_manager:
            return []
        
        # Get memories to analyze
        if memory_ids:
            memories = []
            for memory_id in memory_ids:
                memory = await self.memory_manager.get_memory(memory_id)
                if memory:
                    memories.append(memory)
        else:
            memories = await self.memory_manager.get_memories_by_entity(entity_id, limit=500)
        
        if len(memories) < 2:
            return []
        
        detected_associations = []
        
        # Analyze all pairs of memories
        for i, memory_a in enumerate(memories):
            for memory_b in memories[i+1:]:
                associations = await self._analyze_memory_pair(memory_a, memory_b)
                detected_associations.extend(associations)
        
        # Filter and optimize associations
        optimized_associations = self._optimize_associations(detected_associations)
        
        # Store associations
        await self._store_associations(optimized_associations)
        
        return optimized_associations
    
    async def _analyze_memory_pair(self, memory_a: "Memory", memory_b: "Memory") -> List[MemoryAssociation]:
        """Analyze a pair of memories for associations."""
        associations = []
        
        # Temporal associations
        temporal_assocs = self._detect_temporal_associations(memory_a, memory_b)
        associations.extend(temporal_assocs)
        
        # Semantic associations
        semantic_assocs = self._detect_semantic_associations(memory_a, memory_b)
        associations.extend(semantic_assocs)
        
        # Entity-based associations
        entity_assocs = self._detect_entity_associations(memory_a, memory_b)
        associations.extend(entity_assocs)
        
        # Emotional associations
        emotional_assocs = self._detect_emotional_associations(memory_a, memory_b)
        associations.extend(emotional_assocs)
        
        # Behavioral associations
        behavioral_assocs = self._detect_behavioral_associations(memory_a, memory_b)
        associations.extend(behavioral_assocs)
        
        return associations
    
    def _detect_temporal_associations(self, memory_a: "Memory", memory_b: "Memory") -> List[MemoryAssociation]:
        """Detect temporal associations between memories."""
        associations = []
        
        time_diff = abs((memory_a.created_at - memory_b.created_at).total_seconds() / 3600)  # Hours
        
        if time_diff <= self.temporal_window_hours:
            # Temporal sequence - memories close in time
            strength = max(0.1, 1.0 - (time_diff / self.temporal_window_hours))
            
            associations.append(MemoryAssociation(
                memory_a_id=memory_a.memory_id,
                memory_b_id=memory_b.memory_id,
                association_type=AssociationType.TEMPORAL_SEQUENCE,
                strength=strength,
                confidence=0.8,
                metadata={"time_diff_hours": time_diff}
            ))
            
            # Check for causal relationship
            causal_strength = self._detect_causal_relationship(memory_a, memory_b)
            if causal_strength > 0.3:
                associations.append(MemoryAssociation(
                    memory_a_id=memory_a.memory_id,
                    memory_b_id=memory_b.memory_id,
                    association_type=AssociationType.TEMPORAL_CAUSAL,
                    strength=causal_strength,
                    confidence=0.6,
                    metadata={"causal_indicators": self._get_causal_indicators(memory_a, memory_b)}
                ))
        
        return associations
    
    def _detect_semantic_associations(self, memory_a: "Memory", memory_b: "Memory") -> List[MemoryAssociation]:
        """Detect semantic associations between memories."""
        associations = []
        
        # Extract keywords from memory content
        keywords_a = self._extract_keywords(memory_a.content)
        keywords_b = self._extract_keywords(memory_b.content)
        
        # Calculate semantic similarity
        similarity = self._calculate_semantic_similarity(keywords_a, keywords_b)
        
        if similarity > 0.4:
            associations.append(MemoryAssociation(
                memory_a_id=memory_a.memory_id,
                memory_b_id=memory_b.memory_id,
                association_type=AssociationType.SEMANTIC_SIMILAR,
                strength=similarity,
                confidence=0.7,
                metadata={
                    "shared_keywords": list(keywords_a.intersection(keywords_b)),
                    "similarity_score": similarity
                }
            ))
        
        # Check for opposing concepts
        opposition = self._calculate_semantic_opposition(keywords_a, keywords_b)
        if opposition > 0.5:
            associations.append(MemoryAssociation(
                memory_a_id=memory_a.memory_id,
                memory_b_id=memory_b.memory_id,
                association_type=AssociationType.SEMANTIC_OPPOSITE,
                strength=opposition,
                confidence=0.6,
                metadata={"opposition_indicators": self._get_opposition_indicators(memory_a, memory_b)}
            ))
        
        return associations
    
    def _detect_entity_associations(self, memory_a: "Memory", memory_b: "Memory") -> List[MemoryAssociation]:
        """Detect entity-based associations between memories."""
        associations = []
        
        # Extract entities from memory content
        entities_a = self._extract_entities(memory_a.content)
        entities_b = self._extract_entities(memory_b.content)
        
        # Check for shared entities
        shared_entities = entities_a.intersection(entities_b)
        
        if shared_entities:
            strength = len(shared_entities) / max(len(entities_a), len(entities_b), 1)
            
            # Determine specific association type based on entity types
            if any(self._is_person_entity(entity) for entity in shared_entities):
                assoc_type = AssociationType.ENTITY_SAME_PERSON
            elif any(self._is_location_entity(entity) for entity in shared_entities):
                assoc_type = AssociationType.ENTITY_SAME_LOCATION
            elif any(self._is_faction_entity(entity) for entity in shared_entities):
                assoc_type = AssociationType.ENTITY_SAME_FACTION
            else:
                assoc_type = AssociationType.ENTITY_SAME_PERSON  # Default
            
            associations.append(MemoryAssociation(
                memory_a_id=memory_a.memory_id,
                memory_b_id=memory_b.memory_id,
                association_type=assoc_type,
                strength=strength,
                confidence=0.8,
                metadata={"shared_entities": list(shared_entities)}
            ))
        
        return associations
    
    def _detect_emotional_associations(self, memory_a: "Memory", memory_b: "Memory") -> List[MemoryAssociation]:
        """Detect emotional associations between memories."""
        associations = []
        
        # Analyze emotional content
        emotion_a = self._extract_emotional_valence(memory_a.content)
        emotion_b = self._extract_emotional_valence(memory_b.content)
        
        # Similar emotional valence
        emotional_similarity = 1.0 - abs(emotion_a - emotion_b)
        if emotional_similarity > 0.7:
            associations.append(MemoryAssociation(
                memory_a_id=memory_a.memory_id,
                memory_b_id=memory_b.memory_id,
                association_type=AssociationType.EMOTIONAL_SIMILAR,
                strength=emotional_similarity,
                confidence=0.6,
                metadata={
                    "emotion_a": emotion_a,
                    "emotion_b": emotion_b,
                    "similarity": emotional_similarity
                }
            ))
        
        # Emotional triggers
        trigger_strength = self._detect_emotional_trigger(memory_a, memory_b)
        if trigger_strength > 0.4:
            associations.append(MemoryAssociation(
                memory_a_id=memory_a.memory_id,
                memory_b_id=memory_b.memory_id,
                association_type=AssociationType.EMOTIONAL_TRIGGER,
                strength=trigger_strength,
                confidence=0.5,
                metadata={"trigger_strength": trigger_strength}
            ))
        
        return associations
    
    def _detect_behavioral_associations(self, memory_a: "Memory", memory_b: "Memory") -> List[MemoryAssociation]:
        """Detect behavioral pattern associations between memories."""
        associations = []
        
        # Extract behavioral patterns
        patterns_a = self._extract_behavioral_patterns(memory_a.content)
        patterns_b = self._extract_behavioral_patterns(memory_b.content)
        
        # Check for shared patterns
        shared_patterns = patterns_a.intersection(patterns_b)
        if shared_patterns:
            strength = len(shared_patterns) / max(len(patterns_a), len(patterns_b), 1)
            
            associations.append(MemoryAssociation(
                memory_a_id=memory_a.memory_id,
                memory_b_id=memory_b.memory_id,
                association_type=AssociationType.BEHAVIORAL_PATTERN,
                strength=strength,
                confidence=0.7,
                metadata={"shared_patterns": list(shared_patterns)}
            ))
        
        # Check for consequence relationships
        consequence_strength = self._detect_behavioral_consequence(memory_a, memory_b)
        if consequence_strength > 0.4:
            associations.append(MemoryAssociation(
                memory_a_id=memory_a.memory_id,
                memory_b_id=memory_b.memory_id,
                association_type=AssociationType.BEHAVIORAL_CONSEQUENCE,
                strength=consequence_strength,
                confidence=0.6,
                metadata={"consequence_strength": consequence_strength}
            ))
        
        return associations
    
    def _optimize_associations(self, associations: List[MemoryAssociation]) -> List[MemoryAssociation]:
        """Optimize associations by removing weak ones and strengthening strong ones."""
        # Filter by minimum strength
        filtered = [a for a in associations if a.strength >= self.min_association_strength]
        
        # Group by memory pairs to avoid duplicates
        pair_associations = defaultdict(list)
        for assoc in filtered:
            key = tuple(sorted([assoc.memory_a_id, assoc.memory_b_id]))
            pair_associations[key].append(assoc)
        
        # Keep strongest association per pair, or merge compatible ones
        optimized = []
        for pair_assocs in pair_associations.values():
            if len(pair_assocs) == 1:
                optimized.extend(pair_assocs)
            else:
                # Keep strongest or merge compatible associations
                pair_assocs.sort(key=lambda a: a.strength, reverse=True)
                optimized.append(pair_assocs[0])
                
                # Add compatible secondary associations
                for assoc in pair_assocs[1:]:
                    if assoc.strength > 0.6:  # Only keep very strong secondary associations
                        optimized.append(assoc)
        
        return optimized
    
    async def _store_associations(self, associations: List[MemoryAssociation]):
        """Store associations in memory manager."""
        for assoc in associations:
            # Store in local cache
            self.associations[assoc.memory_a_id].append(assoc)
            self.associations[assoc.memory_b_id].append(assoc)
            
            # Store in database if memory manager supports it
            if hasattr(self.memory_manager, 'create_association'):
                await self.memory_manager.create_association(
                    memory_a_id=assoc.memory_a_id,
                    memory_b_id=assoc.memory_b_id,
                    association_type=assoc.association_type.value,
                    strength=assoc.strength,
                    metadata=assoc.metadata
                )
    
    async def build_clusters(self, entity_id: str) -> List[AssociationCluster]:
        """Build memory clusters based on associations."""
        if not self.memory_manager:
            return []
        
        # Get all associations for entity
        memories = await self.memory_manager.get_memories_by_entity(entity_id)
        memory_ids = {m.memory_id for m in memories}
        
        # Build adjacency graph
        graph = defaultdict(set)
        for memory_id in memory_ids:
            for assoc in self.associations.get(memory_id, []):
                other_id = assoc.memory_b_id if assoc.memory_a_id == memory_id else assoc.memory_a_id
                if other_id in memory_ids and assoc.strength > 0.5:  # Strong associations only
                    graph[memory_id].add(other_id)
                    graph[other_id].add(memory_id)
        
        # Find clusters using connected components
        clusters = []
        visited = set()
        
        for memory_id in memory_ids:
            if memory_id not in visited:
                cluster_memories = self._find_connected_component(graph, memory_id, visited)
                
                if len(cluster_memories) >= self.cluster_size_threshold:
                    cluster = AssociationCluster(
                        cluster_id=f"cluster_{entity_id}_{len(clusters)}",
                        memory_ids=cluster_memories,
                        cluster_theme=await self._determine_cluster_theme(cluster_memories),
                        cluster_importance=await self._calculate_cluster_importance(cluster_memories),
                        association_types=self._get_cluster_association_types(cluster_memories)
                    )
                    clusters.append(cluster)
                    self.clusters[cluster.cluster_id] = cluster
        
        return clusters
    
    def _find_connected_component(self, graph: Dict[str, Set[str]], start: str, visited: Set[str]) -> Set[str]:
        """Find connected component using BFS."""
        component = set()
        queue = deque([start])
        
        while queue:
            node = queue.popleft()
            if node not in visited:
                visited.add(node)
                component.add(node)
                
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        queue.append(neighbor)
        
        return component
    
    async def _determine_cluster_theme(self, memory_ids: Set[str]) -> str:
        """Determine the theme of a memory cluster."""
        if not self.memory_manager:
            return "unknown"
        
        # Get memory contents
        contents = []
        for memory_id in memory_ids:
            memory = await self.memory_manager.get_memory(memory_id)
            if memory:
                contents.append(memory.content)
        
        # Extract common themes (simple keyword analysis)
        all_keywords = set()
        for content in contents:
            keywords = self._extract_keywords(content)
            all_keywords.update(keywords)
        
        # Find most common keywords
        keyword_counts = {}
        for keyword in all_keywords:
            count = sum(1 for content in contents if keyword.lower() in content.lower())
            keyword_counts[keyword] = count
        
        # Return top keywords as theme
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        return ", ".join([kw for kw, _ in top_keywords])
    
    async def _calculate_cluster_importance(self, memory_ids: Set[str]) -> float:
        """Calculate importance of a memory cluster."""
        if not self.memory_manager:
            return 0.5
        
        importances = []
        for memory_id in memory_ids:
            memory = await self.memory_manager.get_memory(memory_id)
            if memory:
                importances.append(memory.importance)
        
        return sum(importances) / len(importances) if importances else 0.5
    
    def _get_cluster_association_types(self, memory_ids: Set[str]) -> Set[AssociationType]:
        """Get association types present in cluster."""
        association_types = set()
        
        for memory_id in memory_ids:
            for assoc in self.associations.get(memory_id, []):
                if (assoc.memory_a_id in memory_ids and assoc.memory_b_id in memory_ids):
                    association_types.add(assoc.association_type)
        
        return association_types
    
    async def analyze_network(self, entity_id: str) -> NetworkAnalysisResult:
        """Analyze the memory association network for an entity."""
        if not self.memory_manager:
            return self._empty_network_result(entity_id)
        
        memories = await self.memory_manager.get_memories_by_entity(entity_id)
        total_memories = len(memories)
        
        # Count associations
        total_associations = 0
        memory_connectivity = {}
        
        for memory in memories:
            associations = self.associations.get(memory.memory_id, [])
            memory_connectivity[memory.memory_id] = len(associations)
            total_associations += len(associations)
        
        total_associations //= 2  # Each association counted twice
        
        # Calculate metrics
        avg_connectivity = sum(memory_connectivity.values()) / total_memories if total_memories > 0 else 0
        
        # Find highly connected and isolated memories
        connectivities = list(memory_connectivity.values())
        if connectivities:
            high_threshold = max(connectivities) * 0.7
            low_threshold = max(connectivities) * 0.1
        else:
            high_threshold = 0
            low_threshold = 0
        
        highly_connected = [mid for mid, conn in memory_connectivity.items() if conn >= high_threshold]
        isolated = [mid for mid, conn in memory_connectivity.items() if conn <= low_threshold]
        
        # Find strongest associations
        all_associations = []
        for assoc_list in self.associations.values():
            all_associations.extend(assoc_list)
        
        strongest = sorted(all_associations, key=lambda a: a.strength, reverse=True)[:10]
        
        # Build clusters
        clusters = await self.build_clusters(entity_id)
        
        return NetworkAnalysisResult(
            entity_id=entity_id,
            total_memories=total_memories,
            total_associations=total_associations,
            clusters_found=len(clusters),
            average_connectivity=avg_connectivity,
            highly_connected_memories=highly_connected,
            isolated_memories=isolated,
            strongest_associations=strongest,
            analysis_timestamp=datetime.utcnow()
        )
    
    # Utility methods for semantic analysis
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text."""
        # Simple keyword extraction
        words = text.lower().split()
        # Filter out common words and short words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "her", "its", "our", "their", "this", "that", "these", "those", "is", "was", "are", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "can", "may", "might"}
        return {word for word in words if len(word) > 3 and word not in stop_words}
    
    def _extract_entities(self, text: str) -> Set[str]:
        """Extract entity names from text."""
        # Simple entity extraction - look for capitalized words
        import re
        entities = set()
        words = text.split()
        
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                # Check if it's a proper noun (not start of sentence)
                if i > 0 and not words[i-1].endswith('.'):
                    entities.add(word.strip('.,!?'))
        
        return entities
    
    def _is_person_entity(self, entity: str) -> bool:
        """Check if entity is likely a person."""
        # Simple heuristic - could be improved with NER
        return len(entity) > 2 and entity.istitle()
    
    def _is_location_entity(self, entity: str) -> bool:
        """Check if entity is likely a location."""
        location_indicators = ["city", "town", "village", "castle", "kingdom", "empire", "forest", "mountain", "river"]
        return any(indicator in entity.lower() for indicator in location_indicators)
    
    def _is_faction_entity(self, entity: str) -> bool:
        """Check if entity is likely a faction."""
        faction_indicators = ["guild", "order", "clan", "house", "brotherhood", "sisterhood", "cult", "army", "legion"]
        return any(indicator in entity.lower() for indicator in faction_indicators)
    
    def _calculate_semantic_similarity(self, keywords_a: Set[str], keywords_b: Set[str]) -> float:
        """Calculate semantic similarity between keyword sets."""
        if not keywords_a or not keywords_b:
            return 0.0
        
        intersection = keywords_a.intersection(keywords_b)
        union = keywords_a.union(keywords_b)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_semantic_opposition(self, keywords_a: Set[str], keywords_b: Set[str]) -> float:
        """Calculate semantic opposition between keyword sets."""
        # Look for opposing concepts
        opposition_pairs = [
            ("love", "hate"), ("friend", "enemy"), ("good", "evil"), ("happy", "sad"),
            ("trust", "distrust"), ("ally", "enemy"), ("help", "harm"), ("success", "failure"),
            ("victory", "defeat"), ("peace", "war"), ("light", "dark"), ("hope", "despair")
        ]
        
        opposition_score = 0.0
        for word_a in keywords_a:
            for word_b in keywords_b:
                for pair in opposition_pairs:
                    if (word_a in pair[0] and word_b in pair[1]) or (word_a in pair[1] and word_b in pair[0]):
                        opposition_score += 1.0
        
        max_possible = len(keywords_a) * len(keywords_b)
        return opposition_score / max_possible if max_possible > 0 else 0.0
    
    def _extract_emotional_valence(self, text: str) -> float:
        """Extract emotional valence from text (0.0 = negative, 1.0 = positive)."""
        positive_words = ["happy", "joy", "love", "good", "great", "excellent", "wonderful", "amazing", "success", "victory", "trust", "hope", "friend", "ally"]
        negative_words = ["sad", "hate", "bad", "terrible", "awful", "horrible", "failure", "defeat", "betrayal", "enemy", "fear", "despair", "anger", "rage"]
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if any(pos in word for pos in positive_words))
        negative_count = sum(1 for word in words if any(neg in word for neg in negative_words))
        
        if positive_count + negative_count == 0:
            return 0.5  # Neutral
        
        return positive_count / (positive_count + negative_count)
    
    def _extract_behavioral_patterns(self, text: str) -> Set[str]:
        """Extract behavioral patterns from text."""
        behavior_patterns = {
            "aggression", "violence", "fighting", "attack", "defend", "flee", "hide",
            "negotiate", "diplomacy", "trade", "bargain", "deceive", "lie", "truth",
            "help", "assist", "support", "betray", "abandon", "loyalty", "trust"
        }
        
        words = text.lower().split()
        found_patterns = set()
        
        for word in words:
            for pattern in behavior_patterns:
                if pattern in word:
                    found_patterns.add(pattern)
        
        return found_patterns
    
    def _detect_causal_relationship(self, memory_a: "Memory", memory_b: "Memory") -> float:
        """Detect if one memory caused another."""
        causal_indicators = ["because", "caused", "resulted", "led to", "due to", "therefore", "consequently", "as a result"]
        
        # Check if memories are temporally ordered
        if memory_a.created_at > memory_b.created_at:
            memory_a, memory_b = memory_b, memory_a  # Ensure A comes before B
        
        # Look for causal language in the later memory
        later_content = memory_b.content.lower()
        causal_score = sum(1 for indicator in causal_indicators if indicator in later_content)
        
        return min(causal_score / 3.0, 1.0)  # Normalize to 0-1
    
    def _get_causal_indicators(self, memory_a: "Memory", memory_b: "Memory") -> List[str]:
        """Get causal indicators found between memories."""
        causal_indicators = ["because", "caused", "resulted", "led to", "due to", "therefore", "consequently", "as a result"]
        
        later_content = memory_b.content.lower()
        return [indicator for indicator in causal_indicators if indicator in later_content]
    
    def _get_opposition_indicators(self, memory_a: "Memory", memory_b: "Memory") -> List[str]:
        """Get opposition indicators between memories."""
        # Implementation for finding opposition indicators
        return ["contrasting_emotions", "opposite_outcomes"]
    
    def _detect_emotional_trigger(self, memory_a: "Memory", memory_b: "Memory") -> float:
        """Detect if one memory triggers emotion in another."""
        # Look for emotional escalation patterns
        emotion_a = self._extract_emotional_valence(memory_a.content)
        emotion_b = self._extract_emotional_valence(memory_b.content)
        
        # Strong emotional difference might indicate triggering
        emotional_diff = abs(emotion_a - emotion_b)
        
        # Look for trigger language
        trigger_words = ["reminded", "triggered", "brought back", "recalled", "flashback"]
        later_memory = memory_b if memory_b.created_at > memory_a.created_at else memory_a
        
        trigger_score = sum(1 for word in trigger_words if word in later_memory.content.lower())
        
        return min((emotional_diff + trigger_score / 3.0) / 2.0, 1.0)
    
    def _detect_behavioral_consequence(self, memory_a: "Memory", memory_b: "Memory") -> float:
        """Detect behavioral consequence relationships."""
        # Look for action-consequence patterns
        action_words = ["did", "acted", "decided", "chose", "performed"]
        consequence_words = ["resulted", "outcome", "consequence", "effect", "impact"]
        
        earlier_memory = memory_a if memory_a.created_at < memory_b.created_at else memory_b
        later_memory = memory_b if memory_b.created_at > memory_a.created_at else memory_a
        
        action_score = sum(1 for word in action_words if word in earlier_memory.content.lower())
        consequence_score = sum(1 for word in consequence_words if word in later_memory.content.lower())
        
        return min((action_score + consequence_score) / 4.0, 1.0)
    
    def _empty_network_result(self, entity_id: str) -> NetworkAnalysisResult:
        """Return empty network analysis result."""
        return NetworkAnalysisResult(
            entity_id=entity_id,
            total_memories=0,
            total_associations=0,
            clusters_found=0,
            average_connectivity=0.0,
            highly_connected_memories=[],
            isolated_memories=[],
            strongest_associations=[],
            analysis_timestamp=datetime.utcnow()
        )


def create_association_network(memory_manager=None) -> MemoryAssociationNetwork:
    """Factory function for creating association network."""
    return MemoryAssociationNetwork(memory_manager) 