"""
Rumor System Services - Pure Business Logic

This module provides business logic services for the rumor system
according to the Development Bible standards.
"""

# Standard library imports
from typing import Optional, List, Dict, Any, Tuple, Protocol
from uuid import UUID, uuid4
from datetime import datetime
import random
import difflib

# Project imports - Configuration
from backend.systems.rumor.utils.rumor_rules import get_rumor_config


# Domain Models (business logic types) - Updated to match infrastructure
class RumorVariantData:
    """Business domain rumor variant data structure"""
    def __init__(self, 
                 id: str,
                 content: str,
                 created_at: datetime,
                 parent_variant_id: Optional[str] = None,
                 entity_id: str = "",
                 mutation_metadata: Optional[Dict[str, Any]] = None):
        self.id = id
        self.content = content
        self.created_at = created_at
        self.parent_variant_id = parent_variant_id
        self.entity_id = entity_id
        self.mutation_metadata = mutation_metadata or {}


class RumorSpreadData:
    """Business domain rumor spread data structure"""
    def __init__(self,
                 entity_id: str,
                 variant_id: str,
                 heard_from_entity_id: Optional[str] = None,
                 believability: float = 0.5,
                 heard_at: Optional[datetime] = None):
        self.entity_id = entity_id
        self.variant_id = variant_id
        self.heard_from_entity_id = heard_from_entity_id
        self.believability = believability
        self.heard_at = heard_at or datetime.utcnow()


class RumorData:
    """Business domain rumor data structure - Updated to match infrastructure"""
    def __init__(self, 
                 id: UUID,
                 originator_id: str,
                 original_content: str,
                 categories: List[str] = None,
                 severity: str = 'minor',
                 truth_value: float = 0.5,
                 variants: Optional[List[RumorVariantData]] = None,
                 spread: Optional[List[RumorSpreadData]] = None,
                 properties: Optional[Dict[str, Any]] = None,
                 created_at: Optional[datetime] = None):
        self.id = id
        self.originator_id = originator_id
        self.original_content = original_content
        self.categories = categories or []
        self.severity = severity
        self.truth_value = truth_value
        self.variants = variants or []
        self.spread = spread or []
        self.properties = properties or {}
        self.created_at = created_at or datetime.utcnow()

    def calculate_decay(self, days_inactive: int, base_decay: float = 0.05) -> float:
        """Calculate rumor believability decay"""
        severity_factors = {
            'trivial': 1.5,    # Decays faster
            'minor': 1.2,
            'moderate': 1.0,
            'major': 0.8,
            'critical': 0.6    # Decays slower
        }
        
        factor = severity_factors.get(self.severity, 1.0)
        import math
        decay = base_decay * factor * math.log10(days_inactive + 1)
        return min(1.0, max(0.0, decay))

    def calculate_mutation_probability(self, base_chance: float = 0.2) -> float:
        """Calculate probability of mutation during spread"""
        severity_factors = {
            'trivial': 1.5,    # More likely to mutate
            'minor': 1.2,
            'moderate': 1.0,
            'major': 0.8,
            'critical': 0.6    # Less likely to mutate
        }
        
        factor = severity_factors.get(self.severity, 1.0)
        spread_factor = min(2.0, 1.0 + (len(self.spread) / 50.0))
        probability = base_chance * factor * spread_factor
        return min(1.0, max(0.0, probability))

    def calculate_truth_similarity(self, other_content: str) -> float:
        """Calculate truth similarity between contents using fuzzy matching"""
        seq = difflib.SequenceMatcher(None, self.original_content, other_content)
        return round(seq.ratio() * 100, 2)

    def get_latest_variant_id_for_entity(self, entity_id: str) -> Optional[str]:
        """Get the most recent variant ID heard by an entity"""
        entity_spread = [s for s in self.spread if s.entity_id == entity_id]
        if not entity_spread:
            return None
        latest_spread = max(entity_spread, key=lambda s: s.heard_at)
        return latest_spread.variant_id

    def get_variant_by_id(self, variant_id: str) -> Optional[RumorVariantData]:
        """Get a specific variant by ID"""
        for variant in self.variants:
            if variant.id == variant_id:
                return variant
        return None

    def get_current_content_for_entity(self, entity_id: str) -> Optional[str]:
        """Get the content of the rumor as known to a specific entity"""
        variant_id = self.get_latest_variant_id_for_entity(entity_id)
        if not variant_id:
            return None
        variant = self.get_variant_by_id(variant_id)
        if not variant:
            return None
        return variant.content

    def get_believability_for_entity(self, entity_id: str) -> Optional[float]:
        """Get how strongly an entity believes this rumor"""
        entity_spread = [s for s in self.spread if s.entity_id == entity_id]
        if not entity_spread:
            return None
        latest_spread = max(entity_spread, key=lambda s: s.heard_at)
        return latest_spread.believability

    def entity_knows_rumor(self, entity_id: str) -> bool:
        """Check if an entity has heard this rumor"""
        return any(s.entity_id == entity_id for s in self.spread)

    @property
    def spread_count(self) -> int:
        """Get the number of entities that know this rumor"""
        return len(self.spread)


class CreateRumorData:
    """Business domain data for rumor creation"""
    def __init__(self, 
                 originator_id: str,
                 content: str,
                 categories: Optional[List[str]] = None,
                 severity: str = 'minor',
                 truth_value: float = 0.5,
                 properties: Optional[Dict[str, Any]] = None):
        self.originator_id = originator_id
        self.content = content
        self.categories = categories or []
        self.severity = severity
        self.truth_value = truth_value
        self.properties = properties or {}


class UpdateRumorData:
    """Business domain data for rumor updates"""
    def __init__(self, **update_fields):
        self.update_fields = update_fields

    def get_fields(self) -> Dict[str, Any]:
        return self.update_fields


# Business Logic Protocols (dependency injection)
class RumorRepository(Protocol):
    """Protocol for rumor data access"""
    
    def get_rumor_by_id(self, rumor_id: UUID) -> Optional[RumorData]:
        """Get rumor by ID"""
        ...
    
    def create_rumor(self, rumor_data: RumorData) -> RumorData:
        """Create a new rumor"""
        ...
    
    def update_rumor(self, rumor_data: RumorData) -> RumorData:
        """Update existing rumor"""
        ...
    
    def delete_rumor(self, rumor_id: UUID) -> bool:
        """Delete rumor"""
        ...
    
    def list_rumors(self, 
                   page: int = 1, 
                   size: int = 50, 
                   status: Optional[str] = None,
                   search: Optional[str] = None) -> Tuple[List[RumorData], int]:
        """List rumors with pagination"""
        ...
    
    def get_rumor_statistics(self) -> Dict[str, Any]:
        """Get rumor statistics"""
        ...


class RumorValidationService(Protocol):
    """Protocol for rumor validation"""
    
    def validate_rumor_data(self, rumor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate rumor creation/update data"""
        ...
    
    def validate_severity(self, severity: str) -> str:
        """Validate rumor severity"""
        ...
    
    def validate_categories(self, categories: List[str]) -> List[str]:
        """Validate rumor categories"""
        ...


class RumorBusinessService:
    """Service class for rumor business logic - pure business rules"""
    
    def __init__(self, 
                 rumor_repository: RumorRepository,
                 validation_service: RumorValidationService):
        self.rumor_repository = rumor_repository
        self.validation_service = validation_service

    def create_rumor(
        self, 
        create_data: CreateRumorData,
        user_id: Optional[UUID] = None
    ) -> RumorData:
        """Create a new rumor with business validation"""
        # Convert to dict for validation
        rumor_data_dict = {
            'content': create_data.content,
            'originator_id': create_data.originator_id,
            'categories': create_data.categories,
            'severity': create_data.severity,
            'truth_value': create_data.truth_value,
            'properties': create_data.properties
        }
        
        # Business validation
        validated_data = self.validation_service.validate_rumor_data(rumor_data_dict)
        
        # Business rule: Validate severity and categories
        validated_severity = self.validation_service.validate_severity(validated_data['severity'])
        validated_categories = self.validation_service.validate_categories(validated_data['categories'])
        
        # Create initial variant for the original content
        initial_variant = RumorVariantData(
            id=str(uuid4()),
            content=validated_data['content'],
            created_at=datetime.utcnow(),
            parent_variant_id=None,
            entity_id=validated_data['originator_id']
        )
        
        # Create initial spread record for originator
        initial_spread = RumorSpreadData(
            entity_id=validated_data['originator_id'],
            variant_id=initial_variant.id,
            believability=1.0  # Originator believes fully
        )
        
        # Create business entity with validated data
        rumor_entity = RumorData(
            id=uuid4(),
            originator_id=validated_data['originator_id'],
            original_content=validated_data['content'],
            categories=validated_categories,
            severity=validated_severity,
            truth_value=validated_data['truth_value'],
            variants=[initial_variant],
            spread=[initial_spread],
            properties=validated_data.get('properties', {})
        )
        
        # Business rule: Add user tracking if provided
        if user_id:
            rumor_entity.properties = rumor_entity.properties or {}
            rumor_entity.properties['created_by'] = str(user_id)
        
        # Persist via repository
        return self.rumor_repository.create_rumor(rumor_entity)

    def get_rumor_by_id(self, rumor_id: UUID) -> Optional[RumorData]:
        """Get rumor by ID"""
        return self.rumor_repository.get_rumor_by_id(rumor_id)

    def update_rumor(
        self, 
        rumor_id: UUID, 
        update_data: UpdateRumorData
    ) -> RumorData:
        """Update existing rumor with business rules"""
        # Business rule: Rumor must exist
        entity = self.rumor_repository.get_rumor_by_id(rumor_id)
        if not entity:
            raise ValueError(f"Rumor {rumor_id} not found")
        
        # Apply updates with business validation
        update_fields = update_data.get_fields()
        if update_fields:
            # Apply other updates
            for field, value in update_fields.items():
                if hasattr(entity, field):
                    setattr(entity, field, value)
        
        return self.rumor_repository.update_rumor(entity)

    def delete_rumor(self, rumor_id: UUID) -> bool:
        """Delete rumor with business rules"""
        # Business rule: Rumor must exist
        entity = self.rumor_repository.get_rumor_by_id(rumor_id)
        if not entity:
            raise ValueError(f"Rumor {rumor_id} not found")
        
        return self.rumor_repository.delete_rumor(rumor_id)

    def list_rumors(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[RumorData], int]:
        """List rumors with pagination and filtering"""
        return self.rumor_repository.list_rumors(page, size, status, search)

    def get_rumor_statistics(self) -> Dict[str, Any]:
        """Get rumor statistics"""
        return self.rumor_repository.get_rumor_statistics()

    def spread_rumor(
        self,
        rumor_id: UUID,
        from_entity_id: str,
        to_entity_id: str,
        relationship_strength: float = 0.0,
        allow_mutation: bool = True,
        variant_id: Optional[str] = None,
        believability_modifier: float = 0.0,
        social_context: Optional[Dict[str, Any]] = None,
        receiver_personality: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], Optional[RumorData]]:
        """Spread rumor with sophisticated variant and believability handling"""
        social_context = social_context or {}
        receiver_personality = receiver_personality or {}
        
        # Get the rumor
        rumor = self.rumor_repository.get_rumor_by_id(rumor_id)
        if not rumor:
            return False, f"Rumor {rumor_id} not found", None
        
        # Check if the source entity knows the rumor
        if not rumor.entity_knows_rumor(from_entity_id):
            return False, f"Entity {from_entity_id} doesn't know rumor {rumor_id}", None
        
        # Get the variant to spread
        spread_variant_id = variant_id or rumor.get_latest_variant_id_for_entity(from_entity_id)
        if not spread_variant_id:
            return False, f"No variant found for entity {from_entity_id}", None
        
        spread_variant = rumor.get_variant_by_id(spread_variant_id)
        if not spread_variant:
            return False, f"Variant {spread_variant_id} not found", None
        
        # Calculate mutation probability
        mutation_probability = rumor.calculate_mutation_probability()
        should_mutate = allow_mutation and random.random() < mutation_probability
        
        final_variant = spread_variant
        final_variant_id = spread_variant_id
        
        # Handle mutation if it should occur
        if should_mutate:
            # Create a mutation
            mutated_content = self._generate_mutation(
                spread_variant.content, 
                rumor.severity, 
                receiver_personality
            )
            
            # Create new variant
            new_variant = RumorVariantData(
                id=str(uuid4()),
                content=mutated_content,
                created_at=datetime.utcnow(),
                parent_variant_id=spread_variant_id,
                entity_id=to_entity_id,
                mutation_metadata={
                    'mutation_type': 'spread_mutation',
                    'personality_factors': list(receiver_personality.keys()),
                    'original_content': spread_variant.content
                }
            )
            
            rumor.variants.append(new_variant)
            final_variant = new_variant
            final_variant_id = new_variant.id
        
        # Calculate final believability
        base_believability = rumor.get_believability_for_entity(from_entity_id) or 0.5
        receiver_skepticism = receiver_personality.get('skepticism', 0.3)
        source_credibility = social_context.get('source_credibility', 0.7)
        
        new_believability = max(0.0, min(1.0, 
            base_believability + believability_modifier - (receiver_skepticism * 0.2) + (source_credibility * 0.1)
        ))
        
        # Add spread record
        new_spread = RumorSpreadData(
            entity_id=to_entity_id,
            variant_id=final_variant_id,
            heard_from_entity_id=from_entity_id,
            believability=new_believability
        )
        
        rumor.spread.append(new_spread)
        
        # Update and save
        updated_rumor = self.rumor_repository.update_rumor(rumor)
        
        return True, None, updated_rumor

    def _generate_mutation(self, original_content: str, severity: str, personality: Dict[str, Any]) -> str:
        """Generate a mutation of rumor content"""
        config = get_rumor_config()
        mutation_templates = config.get('mutation', {}).get('templates', {})
        
        mutated_content = original_content
        
        # Add uncertainty phrases
        if random.random() < 0.4:
            uncertainty_phrases = mutation_templates.get('uncertainty_phrases', [
                "supposedly", "allegedly", "I heard that", "word is that"
            ])
            if uncertainty_phrases:
                mutated_content = f"{random.choice(uncertainty_phrases)} {mutated_content}"
        
        # Add location vagueness
        if random.random() < 0.3:
            location_vagueness = mutation_templates.get('location_vagueness', [
                "somewhere near", "around", "in the vicinity of"
            ])
            if location_vagueness:
                mutated_content = mutated_content.replace(
                    " at ", f" {random.choice(location_vagueness)} "
                )
        
        # Apply personality-based modifications
        if personality.get('dramatic', False) and random.random() < 0.5:
            intensity_modifiers = mutation_templates.get('intensity_modifiers', {}).get('amplify', [
                "definitely", "absolutely", "certainly"
            ])
            if intensity_modifiers:
                mutated_content = f"{random.choice(intensity_modifiers)} {mutated_content}"
        
        if personality.get('careful', False) and random.random() < 0.5:
            intensity_modifiers = mutation_templates.get('intensity_modifiers', {}).get('diminish', [
                "might have", "possibly", "perhaps"
            ])
            if intensity_modifiers:
                mutated_content = f"{random.choice(intensity_modifiers)} {mutated_content}"
        
        return mutated_content

    def apply_time_decay(
        self,
        rumor_id: UUID,
        days_elapsed: int,
        environmental_factors: Optional[Dict[str, Any]] = None
    ) -> RumorData:
        """Apply time-based decay to rumor believability"""
        environmental_factors = environmental_factors or {}
        
        rumor = self.rumor_repository.get_rumor_by_id(rumor_id)
        if not rumor:
            raise ValueError(f"Rumor {rumor_id} not found")
        
        # Calculate base decay
        base_decay = rumor.calculate_decay(days_elapsed)
        
        # Apply environmental modifiers
        config = get_rumor_config()
        env_modifiers = config.get('decay', {}).get('environmental_modifiers', {})
        
        total_modifier = 1.0
        for factor, value in environmental_factors.items():
            if factor in env_modifiers:
                total_modifier *= env_modifiers[factor]
        
        final_decay = base_decay * total_modifier
        
        # Apply decay to all spread records
        for spread_record in rumor.spread:
            spread_record.believability = max(0.0, spread_record.believability - final_decay)
        
        return self.rumor_repository.update_rumor(rumor)

    def contradict_rumor(
        self,
        rumor_id: UUID,
        contradiction_strength: float,
        source_credibility: float
    ) -> RumorData:
        """Apply contradiction effects to rumor believability"""
        rumor = self.rumor_repository.get_rumor_by_id(rumor_id)
        if not rumor:
            raise ValueError(f"Rumor {rumor_id} not found")
        
        config = get_rumor_config()
        base_decay = config.get('contradiction', {}).get('base_decay', 0.4)
        randomness_range = config.get('contradiction', {}).get('randomness_range', [0.7, 1.3])
        
        # Calculate contradiction effect
        randomness = random.uniform(*randomness_range)
        contradiction_effect = base_decay * contradiction_strength * source_credibility * randomness
        
        # Apply to all spread records
        for spread_record in rumor.spread:
            spread_record.believability = max(0.0, spread_record.believability - contradiction_effect)
        
        return self.rumor_repository.update_rumor(rumor)

    def reinforce_rumor(
        self,
        rumor_id: UUID,
        reinforcement_strength: float,
        source_credibility: float
    ) -> RumorData:
        """Apply reinforcement effects to rumor believability"""
        rumor = self.rumor_repository.get_rumor_by_id(rumor_id)
        if not rumor:
            raise ValueError(f"Rumor {rumor_id} not found")
        
        config = get_rumor_config()
        base_boost = config.get('reinforcement', {}).get('base_boost', 0.3)
        diminishing_returns = config.get('reinforcement', {}).get('diminishing_returns_factor', 0.5)
        
        # Calculate reinforcement effect with diminishing returns
        reinforcement_effect = base_boost * reinforcement_strength * source_credibility
        
        # Apply to all spread records with diminishing returns
        for spread_record in rumor.spread:
            current_believability = spread_record.believability
            # Diminishing returns: harder to reinforce already high believability
            diminished_effect = reinforcement_effect * (1.0 - current_believability * diminishing_returns)
            spread_record.believability = min(1.0, current_believability + diminished_effect)
        
        return self.rumor_repository.update_rumor(rumor)

    def get_rumor_variants(self, original_rumor_id: UUID) -> List[RumorVariantData]:
        """Get all variants of a rumor"""
        rumor = self.rumor_repository.get_rumor_by_id(original_rumor_id)
        if not rumor:
            return []
        
        return rumor.variants

    def calculate_rumor_impact_score(self, rumor_id: UUID) -> float:
        """Calculate overall impact score for a rumor"""
        rumor = self.rumor_repository.get_rumor_by_id(rumor_id)
        if not rumor:
            return 0.0
        
        config = get_rumor_config()
        severity_scores = config.get('impact_calculation', {}).get('severity_scores', {})
        spread_weight = config.get('impact_calculation', {}).get('spread_weight', 0.5)
        spread_cap = config.get('impact_calculation', {}).get('spread_normalization_cap', 100)
        
        # Base impact from severity
        severity_impact = severity_scores.get(rumor.severity, 0.5)
        
        # Spread impact (normalized)
        spread_impact = min(1.0, rumor.spread_count / spread_cap)
        
        # Average believability impact
        if rumor.spread:
            avg_believability = sum(s.believability for s in rumor.spread) / len(rumor.spread)
        else:
            avg_believability = 0.0
        
        # Combined impact score
        impact_score = (
            severity_impact * 0.4 +
            spread_impact * spread_weight +
            avg_believability * (1.0 - spread_weight - 0.4)
        )
        
        return round(impact_score, 3)


def create_rumor_business_service(
    rumor_repository: RumorRepository,
    validation_service: RumorValidationService
) -> RumorBusinessService:
    """Factory function to create rumor business service"""
    return RumorBusinessService(rumor_repository, validation_service)


class RumorService:
    """Facade service for rumor operations - adapts business service to API expectations"""
    
    def __init__(self, db_session):
        """Initialize with database session (for compatibility with existing tests/router)"""
        self.db_session = db_session
        # Initialize the repository and business service
        from backend.infrastructure.repositories.rumor_repository import SQLAlchemyRumorRepository
        from backend.infrastructure.systems.rumor.services.validation_service import DefaultRumorValidationService
        
        self.repository = SQLAlchemyRumorRepository(db_session)
        self.validation_service = DefaultRumorValidationService()
        self.business_service = RumorBusinessService(self.repository, self.validation_service)
    
    async def create_rumor(self, request) -> 'RumorResponse':
        """Create a new rumor"""
        try:
            # Convert API request to business data
            create_data = CreateRumorData(
                originator_id=request.originator_id,
                content=request.content,
                categories=getattr(request, 'categories', []),
                severity=getattr(request, 'severity', 'minor'),
                truth_value=getattr(request, 'truth_value', 0.5),
                properties=getattr(request, 'properties', {})
            )
            
            # Create via business service
            rumor_data = self.business_service.create_rumor(create_data)
            
            # Convert back to API response
            from backend.infrastructure.systems.rumor.models.models import RumorResponse
            return RumorResponse(
                id=str(rumor_data.id),
                original_content=rumor_data.original_content,
                originator_id=rumor_data.originator_id,
                categories=rumor_data.categories,
                severity=rumor_data.severity,
                truth_value=rumor_data.truth_value,
                properties=rumor_data.properties,
                created_at=rumor_data.created_at,
                updated_at=None,
                spread_count=rumor_data.spread_count,
                variants=[],  # Populated by from_orm if needed
                spread_records=[]  # Populated by from_orm if needed
            )
            
        except ValueError as e:
            # Preserve specific error type for better debugging
            raise ValueError(f"Rumor creation failed: {str(e)}")
        except Exception as e:
            # Only convert unexpected errors to generic exception
            raise Exception(f"Unexpected error during rumor creation: {str(e)}")
    
    async def get_rumor_by_id(self, rumor_id: UUID) -> Optional['RumorResponse']:
        """Get rumor by ID"""
        rumor_data = self.business_service.get_rumor_by_id(rumor_id)
        if not rumor_data:
            return None
            
        from backend.infrastructure.systems.rumor.models.models import RumorResponse, RumorVariantResponse, RumorSpreadResponse
        return RumorResponse(
            id=str(rumor_data.id),
            original_content=rumor_data.original_content,
            originator_id=rumor_data.originator_id,
            categories=rumor_data.categories,
            severity=rumor_data.severity,
            truth_value=rumor_data.truth_value,
            properties=rumor_data.properties,
            created_at=rumor_data.created_at,
            updated_at=None,
            spread_count=rumor_data.spread_count,
            variants=[
                RumorVariantResponse(
                    id=v.id,
                    content=v.content,
                    parent_variant_id=v.parent_variant_id,
                    entity_id=v.entity_id,
                    mutation_metadata=v.mutation_metadata,
                    created_at=v.created_at
                ) for v in rumor_data.variants
            ],
            spread_records=[
                RumorSpreadResponse(
                    entity_id=s.entity_id,
                    variant_id=s.variant_id,
                    heard_from_entity_id=s.heard_from_entity_id,
                    believability=s.believability,
                    heard_at=s.heard_at
                ) for s in rumor_data.spread
            ]
        )
    
    async def update_rumor(self, rumor_id: UUID, request) -> 'RumorResponse':
        """Update existing rumor"""
        try:
            # Convert API request to business data
            update_fields = {}
            for field in ['original_content', 'categories', 'severity', 'truth_value', 'properties']:
                if hasattr(request, field) and getattr(request, field) is not None:
                    update_fields[field] = getattr(request, field)
            
            update_data = UpdateRumorData(**update_fields)
            
            # Update via business service
            rumor_data = self.business_service.update_rumor(rumor_id, update_data)
            
            # Convert back to API response
            from backend.infrastructure.systems.rumor.models.models import RumorResponse, RumorVariantResponse, RumorSpreadResponse
            return RumorResponse(
                id=str(rumor_data.id),
                original_content=rumor_data.original_content,
                originator_id=rumor_data.originator_id,
                categories=rumor_data.categories,
                severity=rumor_data.severity,
                truth_value=rumor_data.truth_value,
                properties=rumor_data.properties,
                created_at=rumor_data.created_at,
                updated_at=datetime.utcnow(),
                spread_count=rumor_data.spread_count,
                variants=[
                    RumorVariantResponse(
                        id=v.id,
                        content=v.content,
                        parent_variant_id=v.parent_variant_id,
                        entity_id=v.entity_id,
                        mutation_metadata=v.mutation_metadata,
                        created_at=v.created_at
                    ) for v in rumor_data.variants
                ],
                spread_records=[
                    RumorSpreadResponse(
                        entity_id=s.entity_id,
                        variant_id=s.variant_id,
                        heard_from_entity_id=s.heard_from_entity_id,
                        believability=s.believability,
                        heard_at=s.heard_at
                    ) for s in rumor_data.spread
                ]
            )
            
        except ValueError as e:
            # Preserve specific error type for better debugging
            raise ValueError(f"Rumor update failed: {str(e)}")
        except Exception as e:
            # Only convert unexpected errors to generic exception
            raise Exception(f"Unexpected error during rumor update: {str(e)}")
    
    async def delete_rumor(self, rumor_id: UUID) -> bool:
        """Delete rumor"""
        try:
            return self.business_service.delete_rumor(rumor_id)
        except ValueError as e:
            # Preserve specific error type for better debugging
            raise ValueError(f"Rumor deletion failed: {str(e)}")
        except Exception as e:
            # Only convert unexpected errors to generic exception
            raise Exception(f"Unexpected error during rumor deletion: {str(e)}")
    
    async def list_rumors(self, page: int = 1, size: int = 50, status_filter: Optional[str] = None, search: Optional[str] = None):
        """List rumors with pagination"""
        rumors_data, total = self.business_service.list_rumors(page, size, status_filter, search)
        
        from backend.infrastructure.systems.rumor.models.models import RumorResponse, RumorListResponse, RumorVariantResponse, RumorSpreadResponse
        
        rumor_responses = []
        for rumor_data in rumors_data:
            rumor_responses.append(RumorResponse(
                id=str(rumor_data.id),
                original_content=rumor_data.original_content,
                originator_id=rumor_data.originator_id,
                categories=rumor_data.categories,
                severity=rumor_data.severity,
                truth_value=rumor_data.truth_value,
                properties=rumor_data.properties,
                created_at=rumor_data.created_at,
                updated_at=None,
                spread_count=rumor_data.spread_count,
                variants=[
                    RumorVariantResponse(
                        id=v.id,
                        content=v.content,
                        parent_variant_id=v.parent_variant_id,
                        entity_id=v.entity_id,
                        mutation_metadata=v.mutation_metadata,
                        created_at=v.created_at
                    ) for v in rumor_data.variants
                ],
                spread_records=[
                    RumorSpreadResponse(
                        entity_id=s.entity_id,
                        variant_id=s.variant_id,
                        heard_from_entity_id=s.heard_from_entity_id,
                        believability=s.believability,
                        heard_at=s.heard_at
                    ) for s in rumor_data.spread
                ]
            ))
        
        return RumorListResponse(
            items=rumor_responses,
            total=total,
            page=page,
            size=size,
            has_next=(page * size) < total,
            has_prev=page > 1
        )
    
    async def spread_rumor(
        self,
        rumor_id: UUID,
        from_entity_id: str,
        to_entity_id: str,
        relationship_strength: float = 0.0,
        allow_mutation: bool = True,
        variant_id: Optional[str] = None,
        believability_modifier: float = 0.0,
        social_context: Optional[Dict[str, Any]] = None,
        receiver_personality: Optional[Dict[str, Any]] = None
    ):
        """Spread rumor between entities"""
        success, error_msg, updated_rumor = self.business_service.spread_rumor(
            rumor_id=rumor_id,
            from_entity_id=from_entity_id,
            to_entity_id=to_entity_id,
            relationship_strength=relationship_strength,
            allow_mutation=allow_mutation,
            variant_id=variant_id,
            believability_modifier=believability_modifier,
            social_context=social_context or {},
            receiver_personality=receiver_personality or {}
        )
        
        if not success:
            raise Exception(error_msg)
        
        return {
            "success": True,
            "rumor_id": str(rumor_id),
            "from_entity": from_entity_id,
            "to_entity": to_entity_id,
            "new_spread_count": updated_rumor.spread_count if updated_rumor else 0,
            "was_mutated": len(updated_rumor.variants) > 1 if updated_rumor else False
        }
    
    async def apply_time_decay(self, rumor_id: UUID, days_elapsed: int, environmental_factors: Optional[Dict[str, Any]] = None):
        """Apply time-based decay to rumor"""
        updated_rumor = self.business_service.apply_time_decay(rumor_id, days_elapsed, environmental_factors)
        
        return {
            "rumor_id": str(rumor_id),
            "days_elapsed": days_elapsed,
            "spread_count": updated_rumor.spread_count,
            "average_believability": sum(s.believability for s in updated_rumor.spread) / len(updated_rumor.spread) if updated_rumor.spread else 0.0
        }
    
    async def contradict_rumor(self, rumor_id: UUID, contradiction_strength: float, source_credibility: float):
        """Apply contradiction to rumor"""
        updated_rumor = self.business_service.contradict_rumor(rumor_id, contradiction_strength, source_credibility)
        
        return {
            "rumor_id": str(rumor_id),
            "contradiction_applied": True,
            "average_believability": sum(s.believability for s in updated_rumor.spread) / len(updated_rumor.spread) if updated_rumor.spread else 0.0
        }
    
    async def reinforce_rumor(self, rumor_id: UUID, reinforcement_strength: float, source_credibility: float):
        """Apply reinforcement to rumor"""
        updated_rumor = self.business_service.reinforce_rumor(rumor_id, reinforcement_strength, source_credibility)
        
        return {
            "rumor_id": str(rumor_id),
            "reinforcement_applied": True,
            "average_believability": sum(s.believability for s in updated_rumor.spread) / len(updated_rumor.spread) if updated_rumor.spread else 0.0
        }
    
    async def get_rumor_variants(self, rumor_id: UUID):
        """Get all variants of a rumor"""
        variants = self.business_service.get_rumor_variants(rumor_id)
        
        from backend.infrastructure.systems.rumor.models.models import RumorVariantResponse
        return [
            RumorVariantResponse(
                id=v.id,
                content=v.content,
                parent_variant_id=v.parent_variant_id,
                entity_id=v.entity_id,
                mutation_metadata=v.mutation_metadata,
                created_at=v.created_at
            ) for v in variants
        ]
    
    async def calculate_rumor_impact_score(self, rumor_id: UUID):
        """Calculate rumor impact score"""
        impact_score = self.business_service.calculate_rumor_impact_score(rumor_id)
        
        return {
            "rumor_id": str(rumor_id),
            "impact_score": impact_score,
            "impact_category": self._categorize_impact(impact_score)
        }
    
    def _categorize_impact(self, score: float) -> str:
        """Categorize impact score"""
        if score >= 0.8:
            return "very_high"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "moderate"
        elif score >= 0.2:
            return "low"
        else:
            return "minimal"
    
    async def get_rumor_stats(self):
        """Get rumor system statistics"""
        stats = self.business_service.get_rumor_statistics()
        return {
            "total_rumors": stats.get("total_rumors", 0),
            "active_rumors": stats.get("active_rumors", 0),
            "inactive_rumors": stats.get("inactive_rumors", 0),
            "average_spread_count": stats.get("average_spread_count", 0.0),
            "severity_distribution": {
                "trivial": stats.get("trivial_rumors", 0),
                "minor": stats.get("minor_rumors", 0),
                "moderate": stats.get("moderate_rumors", 0),
                "major": stats.get("major_rumors", 0),
                "critical": stats.get("critical_rumors", 0)
            },
            "system_health": "healthy"  # TODO: Implement health checks
        }
    
    # Test helper methods expected by the tests
    async def _get_by_originator(self, originator_id: str):
        """Get rumors by originator (test helper)"""
        # TODO: Implement proper originator-based lookup via repository
        return None
        
    async def _get_entity_by_id(self, rumor_id: UUID):
        """Get rumor entity by ID (test helper)"""
        return self.business_service.get_rumor_by_id(rumor_id)
