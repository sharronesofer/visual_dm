"""
Unified Diplomacy Service

This module provides a consolidated diplomacy service that combines:
- Comprehensive diplomatic operations (treaties, negotiations, events, etc.)
- Simple CRUD operations for basic diplomacy entities
- Backward compatibility with existing service interfaces

This service acts as the single point of entry for all diplomatic functionality.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Import consolidated models (using core_models as authoritative)
from backend.systems.diplomacy.models.core_models import (
    DiplomaticEvent, 
    DiplomaticEventType, 
    DiplomaticStatus, 
    Negotiation, 
    NegotiationOffer,
    NegotiationStatus, 
    Treaty, 
    TreatyType,
    TreatyStatus,
    TreatyViolation,
    TreatyViolationType,
    DiplomaticIncident,
    DiplomaticIncidentType,
    DiplomaticIncidentSeverity,
    Ultimatum,
    UltimatumStatus,
    Sanction,
    SanctionType,
    SanctionStatus
)

# Import legacy models for compatibility
from backend.systems.diplomacy.models.models import (
    DiplomacyModel as LegacyDiplomacyModel,
    CreateDiplomacyRequest,
    UpdateDiplomacyRequest,
    DiplomacyResponse
)

# Import proper database models for modern functionality
from backend.infrastructure.databases.diplomacy import (
    DiplomaticRelationship,
    Treaty,
    Negotiation,
    NegotiationOffer,
    DiplomaticEvent,
    TreatyViolation,
    DiplomaticIncident,
    Ultimatum,
    Sanction
)

# Import repository
try:
    from backend.infrastructure.repositories.diplomacy_repository import DiplomacyRepository
except ImportError:
    # Fallback for development
    DiplomacyRepository = None

# Import existing services to delegate to
from backend.systems.diplomacy.services.core_services import DiplomacyService as CoreDiplomacyService, TensionService

logger = logging.getLogger(__name__)


class UnifiedDiplomacyService:
    """
    Unified diplomacy service that consolidates all diplomatic functionality.
    
    This service provides:
    1. Full diplomatic operations (treaties, negotiations, incidents, etc.)
    2. Simple CRUD operations for basic entities
    3. Backward compatibility with existing interfaces
    4. Integrated tension and relationship management
    """
    
    def __init__(self, repository: Optional[DiplomacyRepository] = None, db_session: Optional[Session] = None):
        """
        Initialize the unified diplomacy service.
        
        Args:
            repository: Optional diplomacy repository for data operations
            db_session: Optional SQLAlchemy session for direct database operations
        """
        self.repository = repository
        self.db_session = db_session
        
        # Initialize core services as components
        self.core_service = CoreDiplomacyService(repository)
        self.tension_service = TensionService(repository)
        
        logger.info("Initialized UnifiedDiplomacyService")
    
    # ===========================
    # Comprehensive Diplomatic Operations (Core Functionality)
    # ===========================
    
    # Treaty Management
    def create_treaty(
        self,
        name: str,
        treaty_type: TreatyType,
        parties: List[UUID],
        terms: Dict = None,
        end_date: Optional[datetime] = None,
        is_public: bool = True,
        negotiation_id: Optional[UUID] = None,
        created_by: Optional[UUID] = None
    ) -> Treaty:
        """Create a new treaty."""
        return self.core_service.create_treaty(
            name=name,
            treaty_type=treaty_type,
            parties=parties,
            terms=terms,
            end_date=end_date,
            is_public=is_public,
            negotiation_id=negotiation_id,
            created_by=created_by
        )
    
    def get_treaty(self, treaty_id: UUID) -> Optional[Treaty]:
        """Get a treaty by ID."""
        return self.core_service.get_treaty(treaty_id)
    
    def list_treaties(
        self, 
        faction_id: Optional[UUID] = None,
        active_only: bool = False,
        treaty_type: Optional[TreatyType] = None
    ) -> List[Treaty]:
        """List treaties with optional filtering."""
        return self.core_service.list_treaties(faction_id, active_only, treaty_type)
    
    def expire_treaty(self, treaty_id: UUID) -> Optional[Treaty]:
        """Expire a treaty."""
        return self.core_service.expire_treaty(treaty_id)
    
    # Negotiation Management
    def start_negotiation(
        self,
        parties: List[UUID],
        initiator_id: UUID,
        treaty_type: Optional[TreatyType] = None,
        initial_offer: Optional[Dict] = None,
        metadata: Dict = None
    ) -> Negotiation:
        """Start a new negotiation."""
        return self.core_service.start_negotiation(
            parties=parties,
            initiator_id=initiator_id,
            treaty_type=treaty_type,
            initial_offer=initial_offer,
            metadata=metadata
        )
    
    def make_offer(
        self,
        negotiation_id: UUID,
        faction_id: UUID,
        terms: Dict,
        counter_to: Optional[UUID] = None
    ) -> Optional[Tuple[Negotiation, NegotiationOffer]]:
        """Make an offer in a negotiation."""
        return self.core_service.make_offer(negotiation_id, faction_id, terms, counter_to)
    
    def accept_offer(
        self,
        negotiation_id: UUID,
        faction_id: UUID
    ) -> Optional[Tuple[Negotiation, Treaty]]:
        """Accept an offer and conclude negotiation."""
        return self.core_service.accept_offer(negotiation_id, faction_id)
    
    def reject_offer(
        self,
        negotiation_id: UUID,
        faction_id: UUID,
        final: bool = False
    ) -> Optional[Negotiation]:
        """Reject an offer."""
        return self.core_service.reject_offer(negotiation_id, faction_id, final)
    
    # Relationship and Tension Management
    def get_faction_relationship(self, faction_a_id: UUID, faction_b_id: UUID) -> Dict:
        """Get relationship between two factions."""
        return self.tension_service.get_faction_relationship(faction_a_id, faction_b_id)
    
    def get_faction_relationships(self, faction_id: UUID) -> List[Dict]:
        """Get all relationships for a faction."""
        return self.tension_service.get_faction_relationships(faction_id)
    
    def update_faction_tension(
        self,
        faction_a_id: UUID,
        faction_b_id: UUID,
        tension_change: int,
        reason: Optional[str] = None
    ) -> Dict:
        """Update tension between factions."""
        return self.tension_service.update_faction_tension(
            faction_a_id, faction_b_id, tension_change, reason
        )
    
    def set_diplomatic_status(
        self,
        faction_a_id: UUID,
        faction_b_id: UUID,
        status: DiplomaticStatus
    ) -> Dict:
        """Set diplomatic status between factions."""
        return self.tension_service.set_diplomatic_status(faction_a_id, faction_b_id, status)
    
    def are_at_war(self, faction_a_id: UUID, faction_b_id: UUID) -> bool:
        """Check if factions are at war."""
        return self.tension_service.are_at_war(faction_a_id, faction_b_id)
    
    def are_allied(self, faction_a_id: UUID, faction_b_id: UUID) -> bool:
        """Check if factions are allied."""
        return self.tension_service.are_allied(faction_a_id, faction_b_id)
    
    # Treaty Violation Management
    def report_treaty_violation(
        self,
        treaty_id: UUID,
        violator_id: UUID,
        violation_type: TreatyViolationType,
        description: str,
        evidence: Dict,
        reported_by: UUID,
        severity: int = 50
    ) -> TreatyViolation:
        """Report a treaty violation."""
        return self.core_service.report_treaty_violation(
            treaty_id, violator_id, violation_type, description, evidence, reported_by, severity
        )
    
    def enforce_treaties_automatically(self) -> List[TreatyViolation]:
        """Automatically detect and report treaty violations."""
        return self.core_service.enforce_treaties_automatically()
    
    # Incident Management
    def create_diplomatic_incident(
        self,
        incident_type: DiplomaticIncidentType,
        perpetrator_id: UUID,
        victim_id: UUID,
        description: str,
        evidence: Dict[str, Union[str, int, bool, Dict, List]] = {},
        severity: DiplomaticIncidentSeverity = DiplomaticIncidentSeverity.MODERATE,
        tension_impact: int = 20,
        public: bool = True,
        witnessed_by: List[UUID] = [],
        related_event_id: Optional[UUID] = None,
        related_treaty_id: Optional[UUID] = None
    ) -> DiplomaticIncident:
        """Create a diplomatic incident."""
        return self.core_service.create_diplomatic_incident(
            incident_type, perpetrator_id, victim_id, description, evidence,
            severity, tension_impact, public, witnessed_by, related_event_id, related_treaty_id
        )
    
    # Ultimatum Management
    def create_ultimatum(
        self,
        issuer_id: UUID,
        recipient_id: UUID,
        demands: Dict[str, Union[str, int, bool, Dict, List]],
        consequences: Dict[str, Union[str, int, bool, Dict, List]],
        deadline: datetime,
        justification: str,
        public: bool = True,
        witnessed_by: List[UUID] = [],
        related_incident_id: Optional[UUID] = None,
        related_treaty_id: Optional[UUID] = None,
        related_event_id: Optional[UUID] = None,
        tension_change_on_issue: int = 20,
        tension_change_on_accept: int = -10,
        tension_change_on_reject: int = 40
    ) -> Ultimatum:
        """Create an ultimatum."""
        return self.core_service.create_ultimatum(
            issuer_id, recipient_id, demands, consequences, deadline, justification,
            public, witnessed_by, related_incident_id, related_treaty_id, related_event_id,
            tension_change_on_issue, tension_change_on_accept, tension_change_on_reject
        )
    
    # Sanction Management
    def create_sanction(
        self,
        imposer_id: UUID,
        target_id: UUID,
        sanction_type: SanctionType,
        description: str,
        justification: str,
        end_date: Optional[datetime] = None,
        conditions_for_lifting: Dict[str, Union[str, int, bool, Dict, List]] = None,
        severity: int = 50,
        economic_impact: int = 50,
        diplomatic_impact: int = 50,
        enforcement_measures: Dict[str, Union[str, int, bool, Dict, List]] = None,
        supporting_factions: List[UUID] = None,
        opposing_factions: List[UUID] = None,
        is_public: bool = True
    ) -> Sanction:
        """Create a sanction."""
        return self.core_service.create_sanction(
            imposer_id, target_id, sanction_type, description, justification,
            end_date, conditions_for_lifting, severity, economic_impact, diplomatic_impact,
            enforcement_measures, supporting_factions, opposing_factions, is_public
        )
    
    # ===========================
    # Simple CRUD Operations (Legacy Compatibility)
    # ===========================
    
    def get_diplomacy(self, diplomacy_id: Union[int, UUID]) -> Optional[LegacyDiplomacyModel]:
        """Get basic diplomacy entity (legacy compatibility - uses mock data)."""
        try:
            # Mock implementation for legacy compatibility
            # Real diplomatic functionality uses treaties, negotiations, etc.
            if isinstance(diplomacy_id, UUID):
                return LegacyDiplomacyModel(
                    id=int(str(diplomacy_id).replace('-', '')[:8], 16),
                    name=f"Mock Diplomacy {diplomacy_id}",
                    description="Legacy compatibility mock entity"
                )
            else:
                return LegacyDiplomacyModel(
                    id=diplomacy_id,
                    name=f"Mock Diplomacy {diplomacy_id}",
                    description="Legacy compatibility mock entity"
                )
            
        except Exception as e:
            logger.error(f"Error getting diplomacy {diplomacy_id}: {str(e)}")
            return None
    
    def get_all_diplomacys(self) -> List[LegacyDiplomacyModel]:
        """Get all basic diplomacy entities (legacy compatibility - uses mock data)."""
        try:
            # Mock implementation for legacy compatibility
            return [
                LegacyDiplomacyModel(id=1, name="Mock Diplomacy 1", description="Legacy compatibility"),
                LegacyDiplomacyModel(id=2, name="Mock Diplomacy 2", description="Legacy compatibility"),
                LegacyDiplomacyModel(id=3, name="Mock Diplomacy 3", description="Legacy compatibility")
            ]
            
        except Exception as e:
            logger.error(f"Error getting all diplomacies: {str(e)}")
            return []
    
    def create_diplomacy(self, diplomacy_data: Dict[str, Any]) -> LegacyDiplomacyModel:
        """Create new basic diplomacy entity (legacy compatibility - returns mock)."""
        try:
            # Mock implementation for legacy compatibility
            mock_id = hash(diplomacy_data.get('name', 'default')) % 10000
            return LegacyDiplomacyModel(
                id=mock_id,
                name=diplomacy_data.get('name', 'Mock Diplomacy'),
                description=diplomacy_data.get('description', 'Legacy compatibility mock entity')
            )
            
        except Exception as e:
            logger.error(f"Error creating diplomacy: {str(e)}")
            raise
    
    def update_diplomacy(self, diplomacy_id: int, updates: Dict[str, Any]) -> Optional[LegacyDiplomacyModel]:
        """Update basic diplomacy entity (legacy compatibility - returns mock)."""
        try:
            # Mock implementation for legacy compatibility
            return LegacyDiplomacyModel(
                id=diplomacy_id,
                name=updates.get('name', f'Updated Mock Diplomacy {diplomacy_id}'),
                description=updates.get('description', 'Legacy compatibility updated mock entity')
            )
            
        except Exception as e:
            logger.error(f"Error updating diplomacy {diplomacy_id}: {str(e)}")
            return None
    
    def delete_diplomacy(self, diplomacy_id: int) -> bool:
        """Delete basic diplomacy entity (legacy compatibility - always returns True)."""
        try:
            # Mock implementation for legacy compatibility
            logger.info(f"Mock deletion of diplomacy {diplomacy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting diplomacy {diplomacy_id}: {str(e)}")
            return False
    
    # ===========================
    # Modern Entity Management (New Pattern)
    # ===========================
    
    async def create_diplomacy_async(
        self, 
        request: CreateDiplomacyRequest,
        user_id: Optional[UUID] = None
    ) -> DiplomacyResponse:
        """Create a new diplomacy entity (modern async interface - mock implementation)."""
        try:
            logger.info(f"Creating diplomacy: {request.name}")
            
            # Mock implementation for modern interface
            mock_id = uuid4()
            now = datetime.utcnow()
            
            response_data = {
                "id": mock_id,
                "name": request.name,
                "description": request.description or "Mock diplomacy entity",
                "status": "active",
                "properties": request.properties or {},
                "created_at": now,
                "updated_at": now,
                "is_active": True
            }
            
            logger.info(f"Created mock diplomacy {mock_id} successfully")
            return DiplomacyResponse(**response_data)
            
        except Exception as e:
            logger.error(f"Error creating diplomacy: {str(e)}")
            raise
    
    async def get_diplomacy_by_id_async(self, diplomacy_id: UUID) -> Optional[DiplomacyResponse]:
        """Get diplomacy entity by ID (modern async interface - mock implementation)."""
        try:
            # Mock implementation
            now = datetime.utcnow()
            return DiplomacyResponse(
                id=diplomacy_id,
                name=f"Mock Diplomacy {diplomacy_id}",
                description="Mock diplomacy entity for legacy compatibility",
                status="active",
                properties={},
                created_at=now,
                updated_at=now,
                is_active=True
            )
            
        except Exception as e:
            logger.error(f"Error getting diplomacy {diplomacy_id}: {str(e)}")
            return None
    
    # ===========================
    # Service Health and Status
    # ===========================
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of the unified diplomacy service."""
        return {
            "service": "UnifiedDiplomacyService",
            "version": "1.0.0",
            "components": {
                "core_service": self.core_service is not None,
                "tension_service": self.tension_service is not None,
                "repository": self.repository is not None,
                "db_session": self.db_session is not None
            },
            "capabilities": {
                "treaty_management": True,
                "negotiation_management": True,
                "relationship_management": True,
                "incident_management": True,
                "ultimatum_management": True,
                "sanction_management": True,
                "legacy_crud": True,
                "modern_async": True
            },
            "status": "active",
            "timestamp": datetime.utcnow().isoformat()
        }


# ===========================
# Factory Functions
# ===========================

def create_unified_diplomacy_service(
    repository: Optional[DiplomacyRepository] = None,
    db_session: Optional[Session] = None
) -> UnifiedDiplomacyService:
    """
    Factory function to create a unified diplomacy service.
    
    Args:
        repository: Optional diplomacy repository
        db_session: Optional SQLAlchemy session
        
    Returns:
        Configured UnifiedDiplomacyService instance
    """
    return UnifiedDiplomacyService(repository=repository, db_session=db_session)


# Legacy alias for backward compatibility
DiplomacyService = UnifiedDiplomacyService 