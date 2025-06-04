"""
Refactored Memory Core Service
-----------------------------

This module provides a refactored implementation of memory management that:
1. Eliminates code duplication from the original services
2. Uses JSON configuration instead of hardcoded values
3. Resolves contradictions between decay and reinforcement mechanisms
4. Provides a clean, maintainable interface
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# Import infrastructure dependencies
from backend.infrastructure.memory_config import get_memory_config
from backend.infrastructure.memory_utils.cognitive_frame_detection import detect_cognitive_frames, apply_cognitive_frames
from backend.infrastructure.memory_utils.memory_categorization import categorize_memory_content
from backend.infrastructure.memory_utils.saliency_scoring import calculate_memory_saliency, calculate_initial_importance

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Centralized memory management with configuration-driven behavior.
    
    This class replaces the scattered memory creation and management logic
    with a single, configurable implementation.
    """
    
    def __init__(self):
        self.config = get_memory_config()
        self.logger = logging.getLogger(__name__)
    
    def create_memory(
        self, 
        npc_id: str, 
        content: str, 
        memory_type: str = None, 
        importance: float = None,
        categories: List[str] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new memory with proper categorization, importance scoring, and cognitive frame analysis.
        
        This replaces the scattered memory creation logic across multiple services.
        
        Args:
            npc_id: ID of the NPC this memory belongs to
            content: Memory content
            memory_type: Optional specific memory type
            importance: Optional manual importance override
            categories: Optional manual categories
            context: Optional additional context
            
        Returns:
            Complete memory dictionary
        """
        timestamp = datetime.utcnow()
        
        # 1. Detect cognitive frames
        cognitive_frames = detect_cognitive_frames(content, context.get('additional_context') if context else None)
        
        # 2. Automatic categorization (if not provided)
        if categories is None:
            auto_category = categorize_memory_content(content)
            categories = [auto_category.value] if hasattr(auto_category, 'value') else [str(auto_category)]
            
            # Add suggested categories from cognitive frames
            frame_suggestions = self._extract_frame_categories(cognitive_frames)
            categories.extend(frame_suggestions)
            categories = list(set(categories))  # Remove duplicates
        
        # 3. Calculate importance (if not provided)
        if importance is None:
            importance = self._calculate_memory_importance(content, categories, cognitive_frames, context)
        
        # 4. Create base memory structure
        memory = {
            'id': self._generate_memory_id(npc_id, timestamp),
            'npc_id': npc_id,
            'content': content,
            'importance': importance,
            'categories': categories,
            'timestamp': timestamp.isoformat(),
            'created_at': timestamp.isoformat(),
            'last_accessed': timestamp.isoformat(),
            'access_count': 1,
            'metadata': {
                'memory_type': memory_type,
                'creation_context': context or {},
                'cognitive_analysis_version': '1.0'
            }
        }
        
        # 5. Apply cognitive frames
        memory = apply_cognitive_frames(memory, cognitive_frames)
        
        # 6. Apply category-specific configurations
        memory = self._apply_category_configurations(memory)
        
        # 7. Initialize decay and reinforcement tracking
        memory = self._initialize_memory_lifecycle(memory)
        
        self.logger.info(f"Created memory {memory['id']} for NPC {npc_id} with importance {importance:.2f}")
        
        return memory
    
    def calculate_trust_level(
        self, 
        npc_id: str, 
        target_entity: str, 
        memories: List[Dict[str, Any]],
        baseline: float = None
    ) -> Dict[str, Any]:
        """
        Calculate trust level based on memories, using configuration-driven weights.
        
        This consolidates trust calculation logic that was duplicated across services.
        
        Args:
            npc_id: ID of the NPC
            target_entity: Entity being evaluated for trust
            memories: Relevant memories involving the target entity
            baseline: Optional baseline trust level
            
        Returns:
            Trust analysis with detailed breakdown
        """
        trust_config = self.config.get_trust_factors()
        interaction_weights = trust_config.get('interaction_weights', {})
        temporal_factors = trust_config.get('temporal_factors', {})
        emotional_modifiers = trust_config.get('emotional_modifiers', {})
        
        if baseline is None:
            baseline = trust_config.get('relationship_baselines', {}).get('stranger_baseline', 0.5)
        
        trust_score = baseline
        confidence = 0.0
        detailed_factors = []
        
        # Filter memories involving the target entity
        relevant_memories = [m for m in memories if self._memory_involves_entity(m, target_entity)]
        
        if not relevant_memories:
            return {
                'trust_level': baseline,
                'confidence': 0.0,
                'factors': [],
                'memory_count': 0,
                'last_interaction': None
            }
        
        # Sort by importance and recency
        relevant_memories.sort(
            key=lambda m: (m.get('importance', 0.5), self._parse_timestamp(m.get('timestamp'))),
            reverse=True
        )
        
        total_weight = 0.0
        weighted_trust_sum = 0.0
        
        for memory in relevant_memories[:trust_config.get('calculation_settings', {}).get('max_memories_considered', 50)]:
            memory_impact = self._calculate_memory_trust_impact(
                memory, target_entity, interaction_weights, temporal_factors, emotional_modifiers
            )
            
            if memory_impact['weight'] > 0:
                weighted_trust_sum += memory_impact['trust_delta'] * memory_impact['weight']
                total_weight += memory_impact['weight']
                detailed_factors.append(memory_impact)
                confidence += memory_impact['weight'] * 0.1
        
        # Calculate final trust score
        if total_weight > 0:
            trust_adjustment = weighted_trust_sum / total_weight
            trust_score = max(0.0, min(1.0, baseline + trust_adjustment))
        
        confidence = min(1.0, confidence)
        
        return {
            'trust_level': trust_score,
            'confidence': confidence,
            'factors': detailed_factors,
            'memory_count': len(relevant_memories),
            'last_interaction': relevant_memories[0]['timestamp'] if relevant_memories else None,
            'baseline': baseline
        }
    
    def process_memory_decay(self, memories: List[Dict[str, Any]], days_passed: float = 1.0) -> List[Dict[str, Any]]:
        """
        Process memory decay using configuration-driven decay rules.
        
        This resolves the contradiction between decay and reinforcement by implementing
        a clear hierarchy of memory protection mechanisms.
        
        Args:
            memories: List of memories to process
            days_passed: Number of days that have passed
            
        Returns:
            Updated memories with decay applied
        """
        memory_integration_config = self.config.get_memory_integration_config()
        decay_protection = memory_integration_config.get('decay_protection', {})
        
        updated_memories = []
        
        for memory in memories:
            updated_memory = memory.copy()
            
            # Check for decay protection
            protection_level = self._calculate_decay_protection(memory, decay_protection)
            
            if protection_level >= 1.0:
                # Memory is fully protected from decay
                updated_memory['metadata']['decay_protected'] = True
                updated_memories.append(updated_memory)
                continue
            
            # Get category-specific decay configuration
            primary_category = memory.get('categories', ['interaction'])[0]
            category_config = self.config.get_memory_category_config(primary_category)
            
            if category_config.get('is_permanent', False):
                # Permanent memory types don't decay
                updated_memory['metadata']['permanent'] = True
                updated_memories.append(updated_memory)
                continue
            
            # Calculate decay
            decay_modifier = category_config.get('decay_modifier', 1.0)
            base_decay_rate = 0.02  # 2% per day base rate
            effective_decay_rate = base_decay_rate * decay_modifier * (1.0 - protection_level)
            
            # Apply temporal decay
            current_importance = memory.get('importance', 0.5)
            decay_amount = effective_decay_rate * days_passed
            
            # Importance-based decay resistance (more important memories decay slower)
            importance_resistance = current_importance * 0.5
            actual_decay = decay_amount * (1.0 - importance_resistance)
            
            new_importance = max(0.1, current_importance - actual_decay)
            updated_memory['importance'] = new_importance
            
            # Track decay history
            if 'decay_history' not in updated_memory['metadata']:
                updated_memory['metadata']['decay_history'] = []
            
            updated_memory['metadata']['decay_history'].append({
                'date': datetime.utcnow().isoformat(),
                'decay_amount': actual_decay,
                'protection_level': protection_level,
                'category_modifier': decay_modifier
            })
            
            updated_memories.append(updated_memory)
        
        return updated_memories
    
    def reinforce_memory(self, memory: Dict[str, Any], reinforcement_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reinforce a memory based on access or related experiences.
        
        This provides a controlled reinforcement mechanism that doesn't conflict with decay.
        
        Args:
            memory: Memory to reinforce
            reinforcement_context: Context for the reinforcement
            
        Returns:
            Reinforced memory
        """
        updated_memory = memory.copy()
        memory_integration_config = self.config.get_memory_integration_config()
        reinforcement_triggers = memory_integration_config.get('reinforcement_triggers', {})
        
        # Determine reinforcement type and strength
        reinforcement_type = reinforcement_context.get('type', 'access')
        strength = reinforcement_context.get('strength', 0.1)
        
        # Apply reinforcement based on type
        if reinforcement_type == 'similar_event':
            strength *= reinforcement_triggers.get('similar_event_bonus', 0.3)
        elif reinforcement_type == 'confirmation':
            strength *= reinforcement_triggers.get('confirmation_bonus', 0.2)
        elif reinforcement_type == 'contradiction':
            strength *= reinforcement_triggers.get('contradiction_penalty', -0.4)
        elif reinforcement_type == 'relevance_access':
            strength *= reinforcement_triggers.get('relevance_access_bonus', 0.1)
        
        # Calculate reinforcement boost
        current_importance = memory.get('importance', 0.5)
        max_importance = 1.0
        
        # Diminishing returns for already high-importance memories
        reinforcement_efficiency = 1.0 - (current_importance * 0.5)
        actual_boost = strength * reinforcement_efficiency
        
        new_importance = min(max_importance, current_importance + actual_boost)
        updated_memory['importance'] = new_importance
        
        # Update access tracking
        updated_memory['last_accessed'] = datetime.utcnow().isoformat()
        updated_memory['access_count'] = memory.get('access_count', 1) + 1
        
        # Track reinforcement history
        if 'reinforcement_history' not in updated_memory['metadata']:
            updated_memory['metadata']['reinforcement_history'] = []
        
        updated_memory['metadata']['reinforcement_history'].append({
            'date': datetime.utcnow().isoformat(),
            'type': reinforcement_type,
            'strength': strength,
            'actual_boost': actual_boost,
            'context': reinforcement_context
        })
        
        return updated_memory
    
    # Private helper methods
    def _calculate_memory_importance(
        self, 
        content: str, 
        categories: List[str], 
        cognitive_frames: List[Dict[str, Any]], 
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate memory importance using saliency scoring and configuration."""
        # Use calculate_initial_importance for content-based scoring
        base_importance = calculate_initial_importance(
            memory_content=content,
            memory_type="regular",
            categories=categories
        )
        
        # Category-based importance
        category_importance = 0.5
        for category in categories:
            cat_config = self.config.get_memory_category_config(category)
            cat_importance = cat_config.get('default_importance', 0.5)
            category_importance = max(category_importance, cat_importance)
        
        # Cognitive frame importance
        frame_importance = 1.0
        if cognitive_frames:
            total_emotional_impact = sum(f.get('emotional_impact', 0.5) for f in cognitive_frames)
            avg_emotional_impact = total_emotional_impact / len(cognitive_frames)
            frame_importance = 1.0 + (avg_emotional_impact - 0.5)
        
        # Context-based importance
        context_importance = 1.0
        if context:
            if context.get('involves_player', False):
                context_importance *= 1.3
            if context.get('public_event', False):
                context_importance *= 1.2
            if context.get('faction_significant', False):
                context_importance *= 1.1
        
        # Combine factors
        final_importance = base_importance * category_importance * frame_importance * context_importance
        return min(1.0, max(0.1, final_importance))
    
    def _extract_frame_categories(self, cognitive_frames: List[Dict[str, Any]]) -> List[str]:
        """Extract suggested categories from cognitive frames."""
        categories = []
        for frame in cognitive_frames:
            if frame.get('confidence', 0.0) > 0.5:
                frame_name = frame.get('frame', '')
                if frame_name in ['betrayal', 'fear', 'threat']:
                    categories.append('trauma')
                elif frame_name in ['success', 'achievement']:
                    categories.append('achievement')
                elif frame_name in ['trust', 'cooperation']:
                    categories.append('relationship')
                elif frame_name in ['learning', 'discovery']:
                    categories.append('knowledge')
        return categories
    
    def _apply_category_configurations(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """Apply category-specific configurations to memory."""
        for category in memory.get('categories', []):
            cat_config = self.config.get_memory_category_config(category)
            if cat_config:
                memory['metadata'][f'{category}_config'] = cat_config
        return memory
    
    def _initialize_memory_lifecycle(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize memory lifecycle tracking."""
        memory['metadata']['lifecycle'] = {
            'decay_immunity_until': None,
            'reinforcement_count': 0,
            'last_decay_processed': datetime.utcnow().isoformat(),
            'creation_importance': memory['importance']
        }
        return memory
    
    def _generate_memory_id(self, npc_id: str, timestamp: datetime) -> str:
        """Generate unique memory ID."""
        import hashlib
        unique_string = f"{npc_id}_{timestamp.isoformat()}_{hash(timestamp)}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def _memory_involves_entity(self, memory: Dict[str, Any], entity: str) -> bool:
        """Check if memory involves a specific entity."""
        content = memory.get('content', '').lower()
        entity_lower = entity.lower()
        
        # Simple check - could be enhanced with more sophisticated NLP
        return entity_lower in content
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime."""
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            return datetime.utcnow()
    
    def _calculate_memory_trust_impact(
        self, 
        memory: Dict[str, Any], 
        target_entity: str, 
        interaction_weights: Dict[str, float],
        temporal_factors: Dict[str, float],
        emotional_modifiers: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate how a specific memory impacts trust."""
        content = memory.get('content', '').lower()
        importance = memory.get('importance', 0.5)
        
        # Analyze memory content for trust-relevant keywords
        trust_delta = 0.0
        matched_keywords = []
        
        # Check for positive trust indicators
        positive_keywords = ['help', 'assist', 'loyal', 'honest', 'fair', 'kept promise', 'reliable']
        for keyword in positive_keywords:
            if keyword in content:
                trust_delta += interaction_weights.get('help_weight', 0.6)
                matched_keywords.append(f"+{keyword}")
        
        # Check for negative trust indicators
        negative_keywords = ['betray', 'lie', 'cheat', 'abandon', 'broke promise', 'unfair']
        for keyword in negative_keywords:
            if keyword in content:
                trust_delta += interaction_weights.get('betrayal_weight', -0.8)
                matched_keywords.append(f"-{keyword}")
        
        # Apply temporal decay
        memory_age_days = (datetime.utcnow() - self._parse_timestamp(memory.get('timestamp'))).days
        recency_factor = temporal_factors.get('time_decay_factor', 0.95) ** memory_age_days
        
        # Apply importance weighting
        weight = importance * recency_factor
        
        return {
            'memory_id': memory.get('id'),
            'trust_delta': trust_delta,
            'weight': weight,
            'keywords': matched_keywords,
            'age_days': memory_age_days,
            'recency_factor': recency_factor
        }
    
    def _calculate_decay_protection(self, memory: Dict[str, Any], decay_protection_config: Dict[str, float]) -> float:
        """Calculate how much protection a memory has from decay."""
        protection = 0.0
        
        importance = memory.get('importance', 0.5)
        categories = memory.get('categories', [])
        
        # High importance memories get protection
        if importance > 0.8:
            protection += decay_protection_config.get('high_impact_memories', 0.8)
        
        # Category-based protection
        if any(cat in ['core', 'identity', 'belief'] for cat in categories):
            protection += decay_protection_config.get('identity_core_memories', 1.0)
        elif 'relationship' in categories:
            protection += decay_protection_config.get('relationship_defining_memories', 0.7)
        
        # Check if memory is marked as behavioral anchor
        if memory.get('metadata', {}).get('behavioral_anchor', False):
            protection += decay_protection_config.get('behavioral_anchor_memories', 0.9)
        
        return min(1.0, protection) 