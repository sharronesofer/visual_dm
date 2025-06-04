"""
Consolidated Rumor Business Service - Pure Business Logic

This service provides consolidated business logic for rumor operations
without technical dependencies like databases, events, or external services.
"""

from typing import Optional, List, Dict, Any, Union, Protocol, Tuple
from datetime import datetime
from uuid import UUID, uuid4
import random

# Import business services
from .services import (
    RumorData, CreateRumorData, UpdateRumorData,
    RumorBusinessService, RumorRepository, RumorValidationService
)

# Import centralized rules configuration
try:
    from backend.systems.rumor.utils.rumor_rules import (
        get_rumor_decay_rate,
        get_rumor_mutation_chance,
        get_rumor_spread_radius,
        get_rumor_believability_threshold,
        get_npc_rumor_behavior,
        get_rumor_config
    )
    _USE_CENTRALIZED_CONFIG = True
except ImportError:
    _USE_CENTRALIZED_CONFIG = False


class ConsolidatedRumorBusinessService:
    """
    Unified business logic service for rumor operations.
    Provides high-level business operations using pure business logic.
    """
    
    def __init__(self, 
                 rumor_business_service: RumorBusinessService):
        """
        Initialize the consolidated business service.
        
        Args:
            rumor_business_service: The core business service for rumor operations
        """
        self.rumor_service = rumor_business_service
    
    def create_rumor_with_defaults(self,
                                  originator_id: str,
                                  content: str,
                                  categories: List[str] = None,
                                  severity: str = None,
                                  truth_value: float = 0.5,
                                  user_id: Optional[UUID] = None) -> RumorData:
        """
        Create a new rumor with business rule defaults.
        
        Args:
            originator_id: ID of entity creating the rumor
            content: The content of the rumor
            categories: List of rumor categories (defaults to ['other'])
            severity: Severity level (defaults based on content length or 'minor')
            truth_value: How true the rumor is (0.0-1.0)
            user_id: Optional user ID for tracking
            
        Returns:
            Created rumor data
        """
        # Business rule: Apply intelligent defaults
        if categories is None:
            categories = ['other']
        
        if severity is None:
            # Business rule: Determine severity from content length
            severity = self._determine_severity_from_content(content)
        
        # Business rule: Generate unique name from content
        name = self._generate_rumor_name(content, originator_id)
        
        # Create rumor data
        create_data = CreateRumorData(
            name=name,
            content=content,
            originator_id=originator_id,
            categories=categories,
            severity=severity,
            truth_value=truth_value
        )
        
        return self.rumor_service.create_rumor(create_data, user_id)
    
    def spread_rumor_with_environment(self,
                                    rumor_id: UUID,
                                    from_entity_id: str,
                                    to_entity_id: str,
                                    location_type: Optional[str] = None,
                                    relationship_strength: float = 0.0) -> Tuple[bool, Optional[str]]:
        """
        Spread a rumor between entities considering environmental factors.
        
        Args:
            rumor_id: ID of the rumor to spread
            from_entity_id: ID of the entity spreading the rumor
            to_entity_id: ID of the entity receiving the rumor
            location_type: Type of location for environmental modifiers
            relationship_strength: Strength of relationship (-1.0 to 1.0)
            
        Returns:
            (success, error_message) tuple
        """
        # Business rule: Get location modifiers
        location_modifiers = self._get_location_modifiers(location_type)
        
        # Business rule: Adjust relationship strength based on location
        adjusted_relationship = relationship_strength * location_modifiers.get("relationship_modifier", 1.0)
        
        # Business rule: Check if mutation should be allowed based on location
        allow_mutation = location_modifiers.get("allow_mutation", True)
        
        return self.rumor_service.spread_rumor(
            rumor_id, from_entity_id, to_entity_id, 
            adjusted_relationship, allow_mutation
        )
    
    def bulk_decay_rumors(self, days_since_active: int = 1) -> Dict[str, Any]:
        """
        Apply decay to multiple rumors based on their properties.
        
        Args:
            days_since_active: Number of days since rumors were last active
            
        Returns:
            Summary of decay operations
        """
        # Get all active rumors
        rumors, total = self.rumor_service.list_rumors(page=1, size=1000, status='active')
        
        decayed_count = 0
        expired_count = 0
        decay_summary = []
        
        for rumor in rumors:
            original_believability = rumor.believability
            
            # Apply decay
            updated_rumor = self.rumor_service.decay_rumor_believability(
                rumor.id, days_since_active
            )
            
            if updated_rumor.believability != original_believability:
                decayed_count += 1
                decay_amount = original_believability - updated_rumor.believability
                
                decay_summary.append({
                    'rumor_id': str(rumor.id),
                    'original_believability': original_believability,
                    'new_believability': updated_rumor.believability,
                    'decay_amount': decay_amount
                })
                
                # Business rule: Mark as expired if believability drops too low
                if updated_rumor.believability <= 0.1:
                    self.rumor_service.update_rumor(
                        rumor.id, 
                        UpdateRumorData(status='expired')
                    )
                    expired_count += 1
        
        return {
            'total_rumors_processed': len(rumors),
            'decayed_count': decayed_count,
            'expired_count': expired_count,
            'days_since_active': days_since_active,
            'decay_details': decay_summary
        }
    
    def get_rumor_network_analysis(self, rumor_id: UUID) -> Dict[str, Any]:
        """
        Analyze rumor spread network and patterns.
        
        Args:
            rumor_id: ID of the rumor to analyze
            
        Returns:
            Network analysis data
        """
        rumor = self.rumor_service.get_rumor_by_id(rumor_id)
        if not rumor:
            return {}
        
        # Business rule: Calculate network metrics
        return {
            'rumor_id': str(rumor_id),
            'spread_count': rumor.spread_count,
            'believability': rumor.believability,
            'truth_value': rumor.truth_value,
            'accuracy_score': self._calculate_accuracy_score(rumor),
            'virality_score': self._calculate_virality_score(rumor),
            'decay_rate': rumor.calculate_decay(1),
            'mutation_probability': rumor.calculate_mutation_probability(),
            'severity': rumor.severity,
            'categories': rumor.categories,
            'age_days': (datetime.utcnow() - rumor.created_at).days,
            'status': rumor.status
        }
    
    def find_similar_rumors(self, rumor_id: UUID, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Find rumors similar to the given rumor based on content.
        
        Args:
            rumor_id: ID of the reference rumor
            similarity_threshold: Minimum similarity score (0.0-1.0)
            
        Returns:
            List of similar rumors with similarity scores
        """
        reference_rumor = self.rumor_service.get_rumor_by_id(rumor_id)
        if not reference_rumor:
            return []
        
        # Get all rumors for comparison
        all_rumors, _ = self.rumor_service.list_rumors(page=1, size=1000)
        
        similar_rumors = []
        for rumor in all_rumors:
            if rumor.id == rumor_id:
                continue
            
            # Business rule: Calculate content similarity
            similarity_score = reference_rumor.calculate_truth_similarity(rumor.content)
            
            if similarity_score >= similarity_threshold:
                similar_rumors.append({
                    'rumor_id': str(rumor.id),
                    'content': rumor.content,
                    'similarity_score': similarity_score,
                    'believability': rumor.believability,
                    'spread_count': rumor.spread_count,
                    'severity': rumor.severity
                })
        
        # Sort by similarity score descending
        similar_rumors.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar_rumors
    
    def _determine_severity_from_content(self, content: str) -> str:
        """Business rule: Determine rumor severity from content characteristics"""
        content_lower = content.lower()
        
        # Business rules for severity classification
        if any(word in content_lower for word in ['death', 'war', 'attack', 'murder', 'disaster']):
            return 'critical'
        elif any(word in content_lower for word in ['important', 'urgent', 'secret', 'danger']):
            return 'major'
        elif any(word in content_lower for word in ['interesting', 'strange', 'unusual']):
            return 'moderate'
        elif len(content) > 200:
            return 'moderate'
        elif len(content) > 50:
            return 'minor'
        else:
            return 'trivial'
    
    def _generate_rumor_name(self, content: str, originator_id: str) -> str:
        """Business rule: Generate unique rumor name from content and originator"""
        # Extract key words from content
        words = content.split()[:3]  # First 3 words
        key_phrase = ' '.join(words).replace('.', '').replace(',', '')
        
        # Add originator prefix and timestamp for uniqueness
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")
        return f"{originator_id}_{key_phrase}_{timestamp}"
    
    def _get_location_modifiers(self, location_type: Optional[str]) -> Dict[str, Any]:
        """Business rule: Get location-specific modifiers for rumor spreading"""
        if _USE_CENTRALIZED_CONFIG and location_type:
            config = get_rumor_config("environment")
            return config.get("location_modifiers", {}).get(location_type.lower(), {})
        else:
            # Business rule fallbacks for common locations
            default_modifiers = {
                'tavern': {
                    'spread_multiplier': 1.5,
                    'relationship_modifier': 1.2,
                    'allow_mutation': True
                },
                'marketplace': {
                    'spread_multiplier': 1.3,
                    'relationship_modifier': 1.0,
                    'allow_mutation': True
                },
                'court': {
                    'spread_multiplier': 1.2,
                    'relationship_modifier': 0.9,
                    'allow_mutation': False
                },
                'temple': {
                    'spread_multiplier': 0.8,
                    'relationship_modifier': 1.1,
                    'allow_mutation': False
                },
                'wilderness': {
                    'spread_multiplier': 0.3,
                    'relationship_modifier': 1.0,
                    'allow_mutation': True
                }
            }
            return default_modifiers.get(location_type.lower() if location_type else '', {
                'spread_multiplier': 1.0,
                'relationship_modifier': 1.0,
                'allow_mutation': True
            })
    
    def _calculate_accuracy_score(self, rumor: RumorData) -> float:
        """Business rule: Calculate how accurate a rumor is relative to truth"""
        # Business rule: Base accuracy on truth value and spread degradation
        base_accuracy = rumor.truth_value
        spread_degradation = min(0.5, rumor.spread_count * 0.01)  # Accuracy decreases with spread
        return max(0.0, base_accuracy - spread_degradation)
    
    def _calculate_virality_score(self, rumor: RumorData) -> float:
        """Business rule: Calculate how viral/spreadable a rumor is"""
        # Business rule: Virality based on believability, severity, and content characteristics
        severity_scores = {
            'trivial': 0.2,
            'minor': 0.4,
            'moderate': 0.6,
            'major': 0.8,
            'critical': 1.0
        }
        
        severity_factor = severity_scores.get(rumor.severity, 0.5)
        believability_factor = rumor.believability
        content_factor = min(1.0, len(rumor.content) / 100.0)  # Longer content may be less viral
        
        virality = (severity_factor * 0.4 + believability_factor * 0.4 + content_factor * 0.2)
        return round(virality, 2)


def create_consolidated_rumor_business_service(
    rumor_business_service: RumorBusinessService
) -> ConsolidatedRumorBusinessService:
    """Factory function to create consolidated rumor business service"""
    return ConsolidatedRumorBusinessService(rumor_business_service) 