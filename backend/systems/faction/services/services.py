"""
Faction System Services - Pure Business Logic

This module provides business logic services for the faction system
according to the Development Bible standards.
"""

# Standard library imports
from typing import Optional, List, Dict, Any, Tuple, Protocol
from uuid import UUID, uuid4
from datetime import datetime

# Project imports - Infrastructure utilities (if needed)
# Note: GenerationError import removed to prevent circular dependencies
# Use standard Python exceptions instead

# Project imports - Business domain models (if referencing concrete types)
from backend.systems.faction.models.faction import FactionData, CreateFactionData, UpdateFactionData

# Domain Models (business logic types) - imported from models module

# Business Logic Protocols (dependency injection)
class FactionRepository(Protocol):
    """Protocol for faction data access"""
    
    def get_faction_by_id(self, faction_id: UUID) -> Optional[FactionData]:
        """Get faction by ID"""
        ...
    
    def get_faction_by_name(self, name: str) -> Optional[FactionData]:
        """Get faction by name"""
        ...
    
    def create_faction(self, faction_data: FactionData) -> FactionData:
        """Create a new faction"""
        ...
    
    def update_faction(self, faction_data: FactionData) -> FactionData:
        """Update existing faction"""
        ...
    
    def delete_faction(self, faction_id: UUID) -> bool:
        """Delete faction"""
        ...
    
    def list_factions(self, 
                     page: int = 1, 
                     size: int = 50, 
                     status: Optional[str] = None,
                     search: Optional[str] = None) -> Tuple[List[FactionData], int]:
        """List factions with pagination"""
        ...
    
    def get_faction_statistics(self) -> Dict[str, Any]:
        """Get faction statistics"""
        ...


class FactionValidationService(Protocol):
    """Protocol for faction validation"""
    
    def validate_faction_data(self, faction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate faction creation/update data"""
        ...
    
    def validate_hidden_attributes(self, attributes: Dict[str, int]) -> Dict[str, int]:
        """Validate hidden attributes"""
        ...
    
    def generate_hidden_attributes(self) -> Dict[str, int]:
        """Generate random hidden attributes"""
        ...


class FactionBusinessService:
    """Service class for faction business logic - pure business rules"""
    
    def __init__(self, 
                 faction_repository: FactionRepository,
                 validation_service: FactionValidationService):
        self.faction_repository = faction_repository
        self.validation_service = validation_service

    def create_faction(
        self, 
        create_data: CreateFactionData,
        user_id: Optional[UUID] = None
    ) -> FactionData:
        """Create a new faction with business validation"""
        # Convert to dict for validation
        faction_data_dict = {
            'name': create_data.name,
            'description': create_data.description,
            'status': create_data.status,
            'properties': create_data.properties,
            **create_data.hidden_attributes
        }
        
        # Comprehensive validation and sanitization
        validated_data = self.validation_service.validate_faction_data(faction_data_dict)
        
        # Business rule: Check for existing faction with same name
        existing_faction = self.faction_repository.get_faction_by_name(validated_data['name'])
        if existing_faction:
            raise ValueError(f"Faction with name '{validated_data['name']}' already exists")
        
        # Business rule: Generate hidden attributes if not provided
        hidden_attrs = {}
        for attr_name in ['hidden_ambition', 'hidden_integrity', 'hidden_discipline', 
                         'hidden_impulsivity', 'hidden_pragmatism', 'hidden_resilience']:
            if attr_name in validated_data:
                hidden_attrs[attr_name] = validated_data[attr_name]
        
        if not hidden_attrs:
            # Generate random attributes if none provided
            hidden_attrs = self.validation_service.generate_hidden_attributes()
        else:
            # Validate and fill missing attributes
            hidden_attrs = self.validation_service.validate_hidden_attributes(hidden_attrs)
        
        # Create business entity with validated data
        faction_entity = FactionData(
            id=uuid4(),
            name=validated_data['name'],
            description=validated_data.get('description'),
            status=validated_data.get('status', 'active'),
            properties=validated_data.get('properties', {}),
            **hidden_attrs  # Unpack hidden attributes
        )
        
        # Business rule: Add user tracking if provided
        if user_id:
            faction_entity.properties = faction_entity.properties or {}
            faction_entity.properties['created_by'] = str(user_id)
        
        # Persist via repository
        return self.faction_repository.create_faction(faction_entity)

    def get_faction_by_id(self, faction_id: UUID) -> Optional[FactionData]:
        """Get faction by ID"""
        return self.faction_repository.get_faction_by_id(faction_id)

    def update_faction(
        self, 
        faction_id: UUID, 
        update_data: UpdateFactionData
    ) -> FactionData:
        """Update existing faction with business rules"""
        # Business rule: Faction must exist
        entity = self.faction_repository.get_faction_by_id(faction_id)
        if not entity:
            raise ValueError(f"Faction {faction_id} not found")
        
        # Apply updates with business validation
        update_fields = update_data.get_fields()
        if update_fields:
            # Business rule: Handle hidden attributes separately for validation
            hidden_attr_updates = {}
            for attr_name in ["hidden_ambition", "hidden_integrity", "hidden_discipline", 
                            "hidden_impulsivity", "hidden_pragmatism", "hidden_resilience"]:
                if attr_name in update_fields:
                    hidden_attr_updates[attr_name] = update_fields.pop(attr_name)
            
            # Business rule: Validate hidden attributes if any are being updated
            if hidden_attr_updates:
                # Get current values for attributes not being updated
                current_attrs = entity.get_hidden_attributes()
                current_attrs.update(hidden_attr_updates)
                validated_attrs = self.validation_service.validate_hidden_attributes(current_attrs)
                
                # Apply validated hidden attributes
                for attr_name, value in validated_attrs.items():
                    setattr(entity, attr_name, value)
            
            # Apply other updates
            for field, value in update_fields.items():
                setattr(entity, field, value)
        
        return self.faction_repository.update_faction(entity)

    def delete_faction(self, faction_id: UUID) -> bool:
        """Soft delete faction with business rules"""
        # Business rule: Faction must exist
        entity = self.faction_repository.get_faction_by_id(faction_id)
        if not entity:
            raise ValueError(f"Faction {faction_id} not found")
        
        return self.faction_repository.delete_faction(faction_id)

    def list_factions(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[FactionData], int]:
        """List factions with pagination and filtering"""
        return self.faction_repository.list_factions(page, size, status, search)

    def get_faction_statistics(self) -> Dict[str, Any]:
        """Get faction statistics"""
        return self.faction_repository.get_faction_statistics()

    def calculate_faction_power_score(self, faction: FactionData) -> float:
        """Business logic: Calculate overall power score for a faction"""
        # Business rule: Power is combination of hidden attributes
        attributes = faction.get_hidden_attributes()
        
        # Weighted scoring based on faction attributes
        power_score = (
            attributes['hidden_ambition'] * 0.25 +      # Drive to expand
            attributes['hidden_discipline'] * 0.2 +     # Organization effectiveness
            attributes['hidden_pragmatism'] * 0.2 +     # Strategic flexibility
            attributes['hidden_resilience'] * 0.2 +     # Ability to withstand setbacks
            attributes['hidden_integrity'] * 0.1 +      # Internal stability
            (10 - attributes['hidden_impulsivity']) * 0.05  # Strategic patience
        )
        
        return round(power_score, 2)

    def assess_faction_stability(self, faction: FactionData) -> Dict[str, Any]:
        """Business logic: Assess internal stability of a faction"""
        attributes = faction.get_hidden_attributes()
        
        # Stability factors
        organizational_stability = (attributes['hidden_discipline'] + attributes['hidden_integrity']) / 2
        leadership_stability = (attributes['hidden_integrity'] + (10 - attributes['hidden_impulsivity'])) / 2
        adaptability = (attributes['hidden_pragmatism'] + attributes['hidden_resilience']) / 2
        
        # Overall stability score
        stability_score = (organizational_stability * 0.4 + leadership_stability * 0.35 + adaptability * 0.25)
        
        # Determine stability category
        if stability_score >= 8:
            category = "highly_stable"
        elif stability_score >= 6:
            category = "stable"
        elif stability_score >= 4:
            category = "moderately_stable"
        elif stability_score >= 2:
            category = "unstable"
        else:
            category = "highly_unstable"
        
        return {
            "stability_score": round(stability_score, 2),
            "category": category,
            "organizational_stability": round(organizational_stability, 2),
            "leadership_stability": round(leadership_stability, 2),
            "adaptability": round(adaptability, 2)
        }

    def predict_faction_behavior_tendencies(self, faction: FactionData) -> Dict[str, Any]:
        """Business logic: Predict behavioral tendencies based on hidden attributes"""
        attributes = faction.get_hidden_attributes()
        
        tendencies = {}
        
        # Aggression tendency
        aggression = (attributes['hidden_ambition'] + attributes['hidden_impulsivity']) / 2
        tendencies['aggression_level'] = self._categorize_attribute(aggression)
        
        # Diplomacy tendency
        diplomacy = (attributes['hidden_integrity'] + attributes['hidden_pragmatism']) / 2
        tendencies['diplomacy_preference'] = self._categorize_attribute(diplomacy)
        
        # Expansion tendency
        expansion = (attributes['hidden_ambition'] + attributes['hidden_pragmatism']) / 2
        tendencies['expansion_drive'] = self._categorize_attribute(expansion)
        
        # Loyalty tendency
        loyalty = (attributes['hidden_integrity'] + attributes['hidden_discipline']) / 2
        tendencies['loyalty_level'] = self._categorize_attribute(loyalty)
        
        # Risk tolerance
        risk_tolerance = (attributes['hidden_impulsivity'] + (10 - attributes['hidden_discipline'])) / 2
        tendencies['risk_tolerance'] = self._categorize_attribute(risk_tolerance)
        
        return tendencies

    def _categorize_attribute(self, value: float) -> str:
        """Helper method to categorize attribute values"""
        if value >= 8:
            return "very_high"
        elif value >= 6:
            return "high"
        elif value >= 4:
            return "moderate"
        elif value >= 2:
            return "low"
        else:
            return "very_low"


def create_faction_business_service(
    faction_repository: FactionRepository,
    validation_service: FactionValidationService
) -> FactionBusinessService:
    """Factory function to create faction business service"""
    return FactionBusinessService(faction_repository, validation_service)


class FactionService:
    """Facade service for faction operations - adapts business service to API expectations"""
    
    def __init__(self, db_session):
        """Initialize with database session (for compatibility with existing tests/router)"""
        self.db_session = db_session
        # Initialize the repository and business service
        from backend.infrastructure.repositories.faction_repository import SQLAlchemyFactionRepository
        from backend.infrastructure.utils.faction.validators import DefaultFactionValidationService
        
        self.repository = SQLAlchemyFactionRepository(db_session)
        self.validation_service = DefaultFactionValidationService()
        self.business_service = FactionBusinessService(self.repository, self.validation_service)
    
    async def create_faction(self, request) -> 'FactionResponse':
        """Create a new faction"""
        try:
            # Convert API request to business data
            create_data = CreateFactionData(
                name=request.name,
                description=request.description,
                status=getattr(request, 'status', 'active'),
                properties=getattr(request, 'properties', {}),
                **{
                    attr: getattr(request, attr) 
                    for attr in ['hidden_ambition', 'hidden_integrity', 'hidden_discipline', 
                                'hidden_impulsivity', 'hidden_pragmatism', 'hidden_resilience']
                    if hasattr(request, attr) and getattr(request, attr) is not None
                }
            )
            
            # Create via business service
            faction_data = self.business_service.create_faction(create_data)
            
            # Convert back to API response
            from backend.infrastructure.models.faction.models import FactionResponse
            return FactionResponse(
                id=faction_data.id,
                name=faction_data.name,
                description=faction_data.description,
                status=faction_data.status,
                properties=faction_data.properties,
                created_at=getattr(faction_data, 'created_at', datetime.utcnow()),
                updated_at=None,
                is_active=True,
                **faction_data.get_hidden_attributes()
            )
            
        except ValueError as e:
            # Preserve specific error type for better debugging
            raise ValueError(f"Faction creation failed: {str(e)}")
        except Exception as e:
            # Only convert unexpected errors to generic exception
            raise Exception(f"Unexpected error during faction creation: {str(e)}")
    
    async def get_faction_by_id(self, faction_id: UUID) -> Optional['FactionResponse']:
        """Get faction by ID"""
        faction_data = self.business_service.get_faction_by_id(faction_id)
        if not faction_data:
            return None
            
        from backend.infrastructure.models.faction.models import FactionResponse
        return FactionResponse(
            id=faction_data.id,
            name=faction_data.name,
            description=faction_data.description,
            status=faction_data.status,
            properties=faction_data.properties,
            created_at=getattr(faction_data, 'created_at', datetime.utcnow()),
            updated_at=None,
            is_active=True,
            **faction_data.get_hidden_attributes()
        )
    
    async def update_faction(self, faction_id: UUID, request) -> 'FactionResponse':
        """Update existing faction"""
        try:
            # Convert API request to business data
            update_fields = {}
            for field in ['name', 'description', 'status', 'properties']:
                if hasattr(request, field) and getattr(request, field) is not None:
                    update_fields[field] = getattr(request, field)
            
            # Add hidden attributes if provided
            for attr in ['hidden_ambition', 'hidden_integrity', 'hidden_discipline', 
                        'hidden_impulsivity', 'hidden_pragmatism', 'hidden_resilience']:
                if hasattr(request, attr) and getattr(request, attr) is not None:
                    update_fields[attr] = getattr(request, attr)
            
            update_data = UpdateFactionData(**update_fields)
            
            # Update via business service
            faction_data = self.business_service.update_faction(faction_id, update_data)
            
            # Convert back to API response
            from backend.infrastructure.models.faction.models import FactionResponse
            return FactionResponse(
                id=faction_data.id,
                name=faction_data.name,
                description=faction_data.description,
                status=faction_data.status,
                properties=faction_data.properties,
                created_at=getattr(faction_data, 'created_at', datetime.utcnow()),
                updated_at=None,
                is_active=True,
                **faction_data.get_hidden_attributes()
            )
            
        except ValueError as e:
            # Preserve specific error type for better debugging
            raise ValueError(f"Faction update failed: {str(e)}")
        except Exception as e:
            # Only convert unexpected errors to generic exception
            raise Exception(f"Unexpected error during faction update: {str(e)}")
    
    async def delete_faction(self, faction_id: UUID) -> bool:
        """Delete faction"""
        try:
            return self.business_service.delete_faction(faction_id)
        except ValueError as e:
            # Preserve specific error type for better debugging
            raise ValueError(f"Faction deletion failed: {str(e)}")
        except Exception as e:
            # Only convert unexpected errors to generic exception
            raise Exception(f"Unexpected error during faction deletion: {str(e)}")
    
    async def list_factions(self, page: int = 1, size: int = 50, status_filter: Optional[str] = None, search: Optional[str] = None):
        """List factions with pagination"""
        factions_data, total = self.business_service.list_factions(page, size, status_filter, search)
        
        from backend.infrastructure.models.faction.models import FactionResponse, FactionListResponse
        
        faction_responses = []
        for faction_data in factions_data:
            faction_responses.append(FactionResponse(
                id=faction_data.id,
                name=faction_data.name,
                description=faction_data.description,
                status=faction_data.status,
                properties=faction_data.properties,
                created_at=getattr(faction_data, 'created_at', datetime.utcnow()),
                updated_at=None,
                is_active=True,
                **faction_data.get_hidden_attributes()
            ))
        
        return FactionListResponse(
            items=faction_responses,
            total=total,
            page=page,
            size=size,
            has_next=(page * size) < total,
            has_prev=page > 1
        )
    
    async def get_faction_diplomatic_status(self, faction_id: UUID):
        """Get diplomatic status for faction"""
        faction_data = self.business_service.get_faction_by_id(faction_id)
        if not faction_data:
            raise Exception(f"Faction {faction_id} not found")
        
        # Query alliance system through repository
        try:
            from backend.infrastructure.repositories.alliance_repository import get_alliance_repository
            alliance_repo = get_alliance_repository(self.db_session)
            active_alliances = alliance_repo.get_active_alliances_for_faction(faction_id)
        except ImportError:
            active_alliances = []
        
        # Query diplomatic relations
        try:
            from backend.infrastructure.repositories.diplomacy_repository import get_diplomacy_repository
            diplomacy_repo = get_diplomacy_repository(self.db_session)
            diplomatic_relations = diplomacy_repo.get_faction_relations(faction_id)
        except ImportError:
            diplomatic_relations = {}
        
        # Calculate trust scores based on faction attributes and history
        trust_scores = self._calculate_trust_scores(faction_data, active_alliances)
        
        # Query betrayal history
        betrayal_history = self._get_betrayal_history(faction_id)
            
        return {
            "faction_id": str(faction_id),
            "active_alliances": [
                {
                    "alliance_id": str(alliance.id),
                    "alliance_type": alliance.alliance_type,
                    "partner_faction_id": str(alliance.partner_faction_id),
                    "status": alliance.status,
                    "trust_level": alliance.trust_level,
                    "created_at": alliance.created_at.isoformat()
                } for alliance in active_alliances
            ],
            "diplomatic_relations": {
                str(faction_id): {
                    "stance": relation.stance,
                    "trust_score": relation.trust_score,
                    "last_interaction": relation.last_interaction.isoformat() if relation.last_interaction else None
                } for faction_id, relation in diplomatic_relations.items()
            },
            "trust_scores": trust_scores,
            "betrayal_history": betrayal_history
        }

    def _calculate_trust_scores(self, faction_data: FactionData, alliances: List) -> Dict[str, float]:
        """Calculate trust scores based on faction attributes and alliance history"""
        base_trustworthiness = (
            faction_data.hidden_integrity * 0.4 +
            faction_data.hidden_discipline * 0.3 +
            (10 - faction_data.hidden_impulsivity) * 0.3
        ) / 10.0
        
        trust_scores = {}
        for alliance in alliances:
            # Adjust base trustworthiness based on alliance history
            alliance_modifier = alliance.trust_level * 0.2
            trust_scores[str(alliance.partner_faction_id)] = min(1.0, base_trustworthiness + alliance_modifier)
        
        return trust_scores

    def _get_betrayal_history(self, faction_id: UUID) -> List[Dict[str, Any]]:
        """Get betrayal history for faction"""
        try:
            from backend.infrastructure.repositories.betrayal_repository import get_betrayal_repository
            betrayal_repo = get_betrayal_repository(self.db_session)
            betrayals = betrayal_repo.get_faction_betrayal_history(faction_id)
            
            return [
                {
                    "betrayal_id": str(betrayal.id),
                    "betrayed_faction_id": str(betrayal.betrayed_faction_id),
                    "betrayal_type": betrayal.betrayal_type,
                    "severity": betrayal.severity,
                    "occurred_at": betrayal.occurred_at.isoformat(),
                    "consequences": betrayal.consequences
                } for betrayal in betrayals
            ]
        except ImportError:
            return []

    async def evaluate_alliance_proposal(self, faction_id: UUID, target_faction_id: UUID, alliance_type: str):
        """Evaluate alliance proposal"""
        faction_data = self.business_service.get_faction_by_id(faction_id)
        target_faction = self.business_service.get_faction_by_id(target_faction_id)
        
        if not faction_data or not target_faction:
            raise Exception("One or both factions not found")
        
        # Use business logic to evaluate alliance
        from backend.infrastructure.utils.faction.faction_utils import calculate_faction_behavior_modifiers
        
        faction_modifiers = calculate_faction_behavior_modifiers(faction_data.get_hidden_attributes())
        target_modifiers = calculate_faction_behavior_modifiers(target_faction.get_hidden_attributes())
        
        # Calculate compatibility score
        compatibility = (
            (faction_modifiers.get('diplomatic_trustworthiness', 0.5) + 
             target_modifiers.get('diplomatic_trustworthiness', 0.5)) / 2 +
            (faction_modifiers.get('treaty_reliability', 0.5) + 
             target_modifiers.get('treaty_reliability', 0.5)) / 2
        ) / 2
        
        success_probability = max(0.1, min(0.9, compatibility))
        
        return {
            "evaluating_faction_id": str(faction_id),
            "target_faction_id": str(target_faction_id),
            "alliance_type": alliance_type,
            "compatibility_score": round(compatibility, 2),
            "success_probability": round(success_probability, 2),
            "recommendation": "accept" if success_probability > 0.6 else "reject",
            "evaluation_factors": {
                "diplomatic_trustworthiness": faction_modifiers.get('diplomatic_trustworthiness', 0.5),
                "treaty_reliability": faction_modifiers.get('treaty_reliability', 0.5),
                "target_trustworthiness": target_modifiers.get('diplomatic_trustworthiness', 0.5),
                "target_reliability": target_modifiers.get('treaty_reliability', 0.5)
            }
        }

    # Test helper methods expected by the tests
    async def _get_by_name(self, name: str):
        """Get faction by name (test helper)"""
        return self.business_service.get_faction_by_name(name)

    async def get_faction_stability_assessment(self, faction_id: UUID):
        """Get faction stability assessment"""
        faction_data = self.business_service.get_faction_by_id(faction_id)
        if not faction_data:
            raise Exception(f"Faction {faction_id} not found")
        
        stability_data = self.business_service.assess_faction_stability(faction_data)
        
        # Implement risk factor analysis
        risk_factors = self._analyze_risk_factors(faction_data)
        predicted_issues = self._predict_stability_issues(faction_data, stability_data)
        
        # Return in API contract format
        return {
            "stability_score": stability_data["stability_score"],
            "category": stability_data["category"],
            "organizational_stability": stability_data["organizational_stability"],
            "leadership_stability": stability_data["leadership_stability"],
            "adaptability": stability_data["adaptability"],
            "risk_factors": risk_factors,
            "predicted_issues": predicted_issues
        }

    def _analyze_risk_factors(self, faction_data: FactionData) -> List[Dict[str, Any]]:
        """Analyze risk factors for faction stability"""
        risk_factors = []
        attributes = faction_data.get_hidden_attributes()
        
        # High impulsivity risk
        if attributes['hidden_impulsivity'] >= 8:
            risk_factors.append({
                "factor": "high_impulsivity",
                "severity": "high",
                "description": "Leadership makes rash decisions that could destabilize the faction"
            })
        
        # Low integrity risk
        if attributes['hidden_integrity'] <= 3:
            risk_factors.append({
                "factor": "low_integrity",
                "severity": "medium",
                "description": "Poor internal trust could lead to corruption and infighting"
            })
        
        # Low discipline risk
        if attributes['hidden_discipline'] <= 3:
            risk_factors.append({
                "factor": "poor_organization",
                "severity": "medium",
                "description": "Lack of organizational structure could impede effectiveness"
            })
        
        return risk_factors

    def _predict_stability_issues(self, faction_data: FactionData, stability_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Predict potential stability issues"""
        issues = []
        
        if stability_data["stability_score"] < 4.0:
            issues.append({
                "issue": "succession_crisis_risk",
                "probability": 0.7,
                "timeframe": "short_term",
                "description": "Low stability increases risk of leadership challenges"
            })
        
        if stability_data["leadership_stability"] < 3.0:
            issues.append({
                "issue": "internal_power_struggle",
                "probability": 0.6,
                "timeframe": "medium_term", 
                "description": "Weak leadership may face internal challenges"
            })
        
        return issues

    async def calculate_betrayal_risk(self, faction_id: UUID, ally_id: UUID, scenario: Optional[str] = None):
        """Calculate betrayal risk"""
        faction_data = self.business_service.get_faction_by_id(faction_id)
        ally_data = self.business_service.get_faction_by_id(ally_id)
        
        if not faction_data or not ally_data:
            raise Exception("One or both factions not found")
        
        # Use business logic to calculate betrayal risk
        from backend.infrastructure.utils.faction.faction_utils import calculate_faction_behavior_modifiers
        
        faction_modifiers = calculate_faction_behavior_modifiers(faction_data.get_hidden_attributes())
        
        # Higher impulsivity, lower integrity, higher ambition = higher betrayal risk
        betrayal_tendency = (
            faction_modifiers.get('rash_decision_making', 0.5) * 0.3 +
            (1.0 - faction_modifiers.get('treaty_reliability', 0.5)) * 0.4 +
            faction_modifiers.get('opportunism', 0.5) * 0.3
        )
        
        risk_level = "low"
        if betrayal_tendency > 0.7:
            risk_level = "high"
        elif betrayal_tendency > 0.5:
            risk_level = "medium"
        
        return {
            "faction_id": str(faction_id),
            "ally_id": str(ally_id),
            "scenario": scenario or "general",
            "betrayal_risk_score": round(betrayal_tendency, 2),
            "risk_level": risk_level,
            "risk_factors": {
                "rash_decision_making": faction_modifiers.get('rash_decision_making', 0.5),
                "treaty_reliability": faction_modifiers.get('treaty_reliability', 0.5),
                "opportunism": faction_modifiers.get('opportunism', 0.5)
            },
            "mitigation_suggestions": [
                "Regular diplomatic communication",
                "Mutual benefit monitoring",
                "Trust-building activities"
            ] if betrayal_tendency > 0.5 else []
        }
    
    async def get_faction_behavior_modifiers(self, faction_id: UUID):
        """Get faction behavior modifiers"""
        faction_data = self.business_service.get_faction_by_id(faction_id)
        if not faction_data:
            raise Exception(f"Faction {faction_id} not found")
        
        # Use business logic to calculate behavior modifiers
        from backend.infrastructure.utils.faction.faction_utils import calculate_faction_behavior_modifiers
        modifiers = calculate_faction_behavior_modifiers(faction_data.get_hidden_attributes())
        
        # Return in API contract format
        return {
            "expansion_tendency": modifiers.get('expansion_tendency', 0.5),
            "alliance_reliability": modifiers.get('alliance_reliability', 0.5),
            "betrayal_likelihood": modifiers.get('betrayal_likelihood', 0.5),
            "diplomatic_flexibility": modifiers.get('diplomatic_flexibility', 0.5),
            "crisis_management": modifiers.get('crisis_management', 0.5),
            "military_aggression": modifiers.get('military_aggression', 0.5),
            "economic_cooperation": modifiers.get('economic_cooperation', 0.5),
            "succession_stability": modifiers.get('succession_stability', 0.5)
        }
    
    async def get_faction_power_score(self, faction_id: UUID):
        """Get faction power score"""
        faction_data = self.business_service.get_faction_by_id(faction_id)
        if not faction_data:
            raise Exception(f"Faction {faction_id} not found")
        
        power_score = self.business_service.calculate_faction_power_score(faction_data)
        
        # Determine power category
        if power_score >= 9.0:
            category = "dominant"
        elif power_score >= 7.0:
            category = "major"
        elif power_score >= 5.0:
            category = "moderate"
        elif power_score >= 3.0:
            category = "minor"
        else:
            category = "negligible"
        
        # Return in API contract format
        return {
            "power_score": power_score,
            "power_category": category,
            "breakdown": {
                "ambition_factor": faction_data.hidden_ambition * 0.25,
                "discipline_factor": faction_data.hidden_discipline * 0.2,
                "pragmatism_factor": faction_data.hidden_pragmatism * 0.2,
                "resilience_factor": faction_data.hidden_resilience * 0.2,
                "integrity_factor": faction_data.hidden_integrity * 0.1,
                "patience_factor": (10 - faction_data.hidden_impulsivity) * 0.05
            },
            "comparison_data": {
                "percentile": self._calculate_power_percentile(power_score),
                "rank": self._calculate_power_rank(faction_data.id, power_score)
            }
        }

    def _calculate_power_percentile(self, power_score: float) -> float:
        """Calculate power score percentile compared to all factions"""
        try:
            # Get all faction power scores
            all_factions, _ = self.business_service.list_factions(page=1, size=1000)
            all_scores = [self.business_service.calculate_faction_power_score(f) for f in all_factions]
            
            if not all_scores:
                return 50.0
            
            # Calculate percentile
            scores_below = sum(1 for score in all_scores if score < power_score)
            percentile = (scores_below / len(all_scores)) * 100
            return round(percentile, 1)
        except Exception:
            return 50.0  # Default fallback

    def _calculate_power_rank(self, faction_id: UUID, power_score: float) -> int:
        """Calculate faction rank by power score"""
        try:
            # Get all factions and their power scores
            all_factions, _ = self.business_service.list_factions(page=1, size=1000)
            faction_scores = [
                (f.id, self.business_service.calculate_faction_power_score(f))
                for f in all_factions
            ]
            
            # Sort by power score descending
            faction_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Find rank (1-indexed)
            for rank, (f_id, _) in enumerate(faction_scores, 1):
                if f_id == faction_id:
                    return rank
            
            return len(faction_scores)  # Default to last if not found
        except Exception:
            return 1  # Default fallback

    async def generate_hidden_attributes(self):
        """Generate random hidden attributes"""
        from backend.infrastructure.utils.faction.faction_utils import generate_faction_hidden_attributes
        return generate_faction_hidden_attributes()
    
    async def get_faction_stats(self):
        """Get faction system statistics"""
        stats = self.business_service.get_faction_statistics()
        
        # Calculate system health based on faction distribution and activity
        total_factions = stats.get("total_factions", 0)
        active_factions = stats.get("active_factions", 0)
        avg_power = stats.get("average_power_score", 0.0)
        
        # Determine system health
        if total_factions == 0:
            system_health = "empty"
        elif active_factions / total_factions < 0.3:
            system_health = "declining"
        elif active_factions / total_factions < 0.7:
            system_health = "stable"
        else:
            system_health = "thriving"
        
        return {
            "total_factions": total_factions,
            "active_factions": active_factions,
            "inactive_factions": stats.get("inactive_factions", 0),
            "disbanded_factions": stats.get("disbanded_factions", 0),
            "average_power_score": avg_power,
            "system_health": system_health
        }

    async def propose_alliance(self, faction_id: UUID, target_faction_id: UUID, alliance_type: str):
        """Propose alliance with proper alliance creation integration"""
        evaluation = await self.evaluate_alliance_proposal(faction_id, target_faction_id, alliance_type)
        
        # Create actual alliance proposal in alliance system
        try:
            from backend.infrastructure.repositories.alliance_repository import get_alliance_repository
            alliance_repo = get_alliance_repository(self.db_session)
            
            proposal = alliance_repo.create_alliance_proposal(
                proposing_faction_id=faction_id,
                target_faction_id=target_faction_id,
                alliance_type=alliance_type,
                compatibility_score=evaluation["compatibility_score"],
                success_probability=evaluation["success_probability"]
            )
            
            return {
                "proposal_id": str(proposal.id),
                "proposing_faction_id": str(faction_id),
                "target_faction_id": str(target_faction_id),
                "alliance_type": alliance_type,
                "status": proposal.status,
                "evaluation": evaluation,
                "created_at": proposal.created_at.isoformat()
            }
        except ImportError:
            # Fallback to mock implementation if alliance system not available
            return {
                "proposal_id": str(uuid4()),
                "proposing_faction_id": str(faction_id),
                "target_faction_id": str(target_faction_id),
                "alliance_type": alliance_type,
                "status": "proposed",
                "evaluation": evaluation,
                "created_at": datetime.utcnow().isoformat()
            }
