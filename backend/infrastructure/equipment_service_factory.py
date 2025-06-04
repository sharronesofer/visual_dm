"""
Equipment Service Factory - Database Integration

Updated factory that wires together all equipment system components with database persistence.
Replaces in-memory repositories with SQLAlchemy database implementations.
"""

from sqlalchemy.orm import Session

from backend.systems.equipment.services import (
    EquipmentBusinessLogicService,
    CharacterEquipmentService,
    EnchantingService,
    create_equipment_business_service,
    create_character_equipment_service
)
from backend.infrastructure.database.repositories.equipment_database_repository import (
    create_equipment_database_repository
)
from backend.infrastructure.database.repositories.equipment_template_database_repository import (
    create_equipment_template_database_repository
)


class EquipmentServiceFactory:
    """Factory for creating fully wired equipment services with database persistence"""
    
    def __init__(self, db_session: Session, templates_path: str = None):
        self.db_session = db_session
        self.templates_path = templates_path
        
        # Cache for services
        self._business_logic_service = None
        self._equipment_repository = None
        self._template_repository = None
        self._character_equipment_service = None
        self._enchanting_service = None
    
    def get_business_logic_service(self) -> EquipmentBusinessLogicService:
        """Get or create equipment business logic service"""
        if self._business_logic_service is None:
            self._business_logic_service = create_equipment_business_service()
        return self._business_logic_service
    
    def get_equipment_repository(self):
        """Get or create equipment database repository"""
        if self._equipment_repository is None:
            self._equipment_repository = create_equipment_database_repository(self.db_session)
        return self._equipment_repository
    
    def get_template_repository(self):
        """Get or create equipment template database repository"""
        if self._template_repository is None:
            self._template_repository = create_equipment_template_database_repository(
                self.db_session, self.templates_path
            )
        return self._template_repository
    
    def get_character_equipment_service(self) -> CharacterEquipmentService:
        """Get or create character equipment service with database repositories"""
        if self._character_equipment_service is None:
            business_logic = self.get_business_logic_service()
            equipment_repo = self.get_equipment_repository()
            template_repo = self.get_template_repository()
            
            self._character_equipment_service = create_character_equipment_service(
                business_logic, equipment_repo, template_repo
            )
        return self._character_equipment_service
    
    def get_enchanting_service(self) -> EnchantingService:
        """Get or create enchanting service"""
        if self._enchanting_service is None:
            business_logic = self.get_business_logic_service()
            template_repo = self.get_template_repository()
            
            # Import here to avoid circular dependencies
            from backend.systems.equipment.services.enchanting_service import EnchantingService
            
            self._enchanting_service = EnchantingService(business_logic, template_repo)
        return self._enchanting_service
    
    def get_all_services(self) -> dict:
        """Get all equipment services as a dictionary"""
        return {
            'business_logic': self.get_business_logic_service(),
            'equipment_repository': self.get_equipment_repository(),
            'template_repository': self.get_template_repository(),
            'character_equipment': self.get_character_equipment_service(),
            'enchanting': self.get_enchanting_service()
        }
    
    def initialize_database_templates(self) -> int:
        """Initialize database with templates from JSON files"""
        template_repo = self.get_template_repository()
        
        if hasattr(template_repo, 'load_templates_from_json'):
            return template_repo.load_templates_from_json()
        return 0
    
    def clear_cache(self):
        """Clear all cached services (useful for testing)"""
        self._business_logic_service = None
        self._equipment_repository = None
        self._template_repository = None
        self._character_equipment_service = None
        self._enchanting_service = None


# Global factory instance (for convenience)
_global_factory = None


def get_equipment_factory(db_session: Session, templates_path: str = None) -> EquipmentServiceFactory:
    """Get a global equipment factory instance"""
    global _global_factory
    if _global_factory is None or _global_factory.db_session != db_session:
        _global_factory = EquipmentServiceFactory(db_session, templates_path)
    return _global_factory


def create_equipment_services_for_request(db_session: Session, templates_path: str = None) -> dict:
    """Create equipment services for a single request (recommended for web requests)"""
    factory = EquipmentServiceFactory(db_session, templates_path)
    return factory.get_all_services()


# Convenience functions for dependency injection
def create_equipment_business_service_with_db(db_session: Session) -> EquipmentBusinessLogicService:
    """Create business logic service (database-agnostic)"""
    return create_equipment_business_service()


def create_equipment_repository_with_db(db_session: Session):
    """Create equipment repository with database session"""
    return create_equipment_database_repository(db_session)


def create_template_repository_with_db(db_session: Session, templates_path: str = None):
    """Create template repository with database session"""
    return create_equipment_template_database_repository(db_session, templates_path)


def create_character_equipment_service_with_db(db_session: Session, templates_path: str = None) -> CharacterEquipmentService:
    """Create character equipment service with database repositories"""
    business_logic = create_equipment_business_service()
    equipment_repo = create_equipment_database_repository(db_session)
    template_repo = create_equipment_template_database_repository(db_session, templates_path)
    
    return create_character_equipment_service(business_logic, equipment_repo, template_repo) 