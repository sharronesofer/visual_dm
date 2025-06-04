"""
Tests for Economic Espionage System Models

Comprehensive tests for all espionage models following the Development Bible standards.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session

# Business models from systems
from backend.systems.espionage.models import (
    EspionageOperation,
    EspionageAgent,
    EconomicIntelligence,
    SpyNetwork,
    EspionageOperationType,
    EspionageOperationStatus,
    IntelligenceType,
    AgentRole,
    NetworkStatus,
    CreateEspionageRequest,
    UpdateEspionageRequest,
    CreateEspionageOperationRequest,
    UpdateEspionageOperationRequest,
    CreateEspionageAgentRequest,
    UpdateEspionageAgentRequest,
    CreateEconomicIntelligenceRequest,
    UpdateEconomicIntelligenceRequest,
    CreateSpyNetworkRequest,
    UpdateSpyNetworkRequest
)

# Database entities from infrastructure
from backend.infrastructure.models.espionage_models import (
    EspionageEntity,
    EspionageOperationEntity,
    EspionageAgentEntity,
    EconomicIntelligenceEntity,
    SpyNetworkEntity
)


class TestEspionageModels:
    """Test espionage model creation and validation"""

    def test_espionage_entity_creation(self):
        """Test creating an espionage entity"""
        entity = EspionageEntity(
            name="Test Espionage Entity",
            description="A test espionage entity",
            status="active"
        )
        
        assert entity.name == "Test Espionage Entity"
        assert entity.description == "A test espionage entity"
        assert entity.status == "active"
        assert entity.is_active is True
        assert entity.properties == {}

    def test_espionage_entity_to_dict(self):
        """Test converting espionage entity to dictionary"""
        entity = EspionageEntity(
            name="Test Entity",
            description="Test description",
            status="active",
            properties={"test": "value"}
        )
        
        result = entity.to_dict()
        
        assert result["name"] == "Test Entity"
        assert result["description"] == "Test description"
        assert result["status"] == "active"
        assert result["properties"] == {"test": "value"}
        assert result["is_active"] is True

    def test_espionage_operation_entity_creation(self):
        """Test creating an espionage operation entity"""
        operation = EspionageOperationEntity(
            operation_type=EspionageOperationType.TRADE_SECRET_THEFT,
            status=EspionageOperationStatus.PLANNED,
            initiator_id=uuid4(),
            initiator_type="faction",
            target_id=uuid4(),
            target_type="business",
            planned_start=datetime.utcnow(),
            planned_duration=24,
            difficulty=7,
            success_chance=0.6,
            risk_level=5
        )
        
        assert operation.operation_type == EspionageOperationType.TRADE_SECRET_THEFT
        assert operation.status == EspionageOperationStatus.PLANNED
        assert operation.difficulty == 7
        assert operation.success_chance == 0.6
        assert operation.risk_level == 5
        assert operation.planned_duration == 24

    def test_espionage_agent_entity_creation(self):
        """Test creating an espionage agent entity"""
        agent = EspionageAgentEntity(
            npc_id=uuid4(),
            role=AgentRole.INFILTRATOR,
            skill_level=5,
            loyalty=7.5,
            trust_level=6.0,
            cover_identity="Merchant",
            legitimate_occupation="Trader",
            access_level=3
        )
        
        assert agent.role == AgentRole.INFILTRATOR
        assert agent.skill_level == 5
        assert agent.loyalty == 7.5
        assert agent.trust_level == 6.0
        assert agent.cover_identity == "Merchant"
        assert agent.legitimate_occupation == "Trader"
        assert agent.access_level == 3
        assert agent.status == "active"

    def test_economic_intelligence_entity_creation(self):
        """Test creating an economic intelligence entity"""
        intelligence = EconomicIntelligenceEntity(
            intelligence_type=IntelligenceType.PRICING_DATA,
            target_entity=uuid4(),
            target_type="business",
            data={"prices": {"wheat": 10, "iron": 25}},
            gathered_by=uuid4(),
            reliability=0.8,
            freshness=1.0,
            strategic_value=7,
            economic_value=1000.0
        )
        
        assert intelligence.intelligence_type == IntelligenceType.PRICING_DATA
        assert intelligence.data == {"prices": {"wheat": 10, "iron": 25}}
        assert intelligence.reliability == 0.8
        assert intelligence.freshness == 1.0
        assert intelligence.strategic_value == 7
        assert intelligence.economic_value == 1000.0

    def test_spy_network_entity_creation(self):
        """Test creating a spy network entity"""
        network = SpyNetworkEntity(
            name="Shadow Merchants",
            faction_id=uuid4(),
            status=NetworkStatus.ACTIVE,
            coverage_area=["Region1", "Region2"],
            specialization=["trade_intelligence", "sabotage"],
            agent_count=12,
            cell_structure=True,
            depth_levels=3,
            intelligence_capacity=8,
            sabotage_capacity=6,
            infiltration_capacity=7,
            security_level=7,
            funding_level=8
        )
        
        assert network.name == "Shadow Merchants"
        assert network.status == NetworkStatus.ACTIVE
        assert network.coverage_area == ["Region1", "Region2"]
        assert network.specialization == ["trade_intelligence", "sabotage"]
        assert network.agent_count == 12
        assert network.cell_structure is True
        assert network.depth_levels == 3
        assert network.intelligence_capacity == 8
        assert network.sabotage_capacity == 6
        assert network.infiltration_capacity == 7


class TestEspionagePydanticModels:
    """Test Pydantic model validation"""

    def test_espionage_operation_model_validation(self):
        """Test espionage operation Pydantic model validation"""
        operation_data = {
            "operation_type": EspionageOperationType.PRICE_INTELLIGENCE,
            "initiator_id": uuid4(),
            "initiator_type": "faction",
            "target_id": uuid4(),
            "target_type": "business",
            "planned_start": datetime.utcnow(),
            "planned_duration": 12,
            "difficulty": 5,
            "success_chance": 0.7,
            "risk_level": 4
        }
        
        operation = EspionageOperation(**operation_data)
        
        assert operation.operation_type == EspionageOperationType.PRICE_INTELLIGENCE
        assert operation.status == EspionageOperationStatus.PLANNED  # default
        assert operation.difficulty == 5
        assert operation.success_chance == 0.7
        assert operation.risk_level == 4

    def test_espionage_agent_model_validation(self):
        """Test espionage agent Pydantic model validation"""
        agent_data = {
            "npc_id": uuid4(),
            "role": AgentRole.SPYMASTER,
            "skill_level": 8,
            "loyalty": 9.0,
            "trust_level": 8.5,
            "specializations": ["intelligence_gathering", "network_management"],
            "languages_known": ["Common", "Elvish", "Dwarvish"]
        }
        
        agent = EspionageAgent(**agent_data)
        
        assert agent.role == AgentRole.SPYMASTER
        assert agent.skill_level == 8
        assert agent.loyalty == 9.0
        assert agent.trust_level == 8.5
        assert agent.specializations == ["intelligence_gathering", "network_management"]
        assert agent.languages_known == ["Common", "Elvish", "Dwarvish"]

    def test_economic_intelligence_model_validation(self):
        """Test economic intelligence Pydantic model validation"""
        intelligence_data = {
            "intelligence_type": IntelligenceType.SUPPLIER_LIST,
            "target_entity": uuid4(),
            "target_type": "faction",
            "data": {
                "suppliers": [
                    {"name": "Iron Works Ltd", "location": "Region1", "capacity": 1000},
                    {"name": "Steel Forge Co", "location": "Region2", "capacity": 800}
                ]
            },
            "gathered_by": uuid4(),
            "reliability": 0.9,
            "strategic_value": 8
        }
        
        intelligence = EconomicIntelligence(**intelligence_data)
        
        assert intelligence.intelligence_type == IntelligenceType.SUPPLIER_LIST
        assert intelligence.reliability == 0.9
        assert intelligence.strategic_value == 8
        assert len(intelligence.data["suppliers"]) == 2

    def test_spy_network_model_validation(self):
        """Test spy network Pydantic model validation"""
        network_data = {
            "name": "Iron Fist Network",
            "faction_id": uuid4(),
            "spymaster_id": uuid4(),
            "status": NetworkStatus.ACTIVE,
            "coverage_area": ["Capital", "Trade_Hub", "Border_Region"],
            "specialization": ["economic_espionage", "counter_intelligence"],
            "agent_count": 25,
            "intelligence_capacity": 9,
            "sabotage_capacity": 7,
            "infiltration_capacity": 8,
            "security_level": 8,
            "funding_level": 9
        }
        
        network = SpyNetwork(**network_data)
        
        assert network.name == "Iron Fist Network"
        assert network.status == NetworkStatus.ACTIVE
        assert network.coverage_area == ["Capital", "Trade_Hub", "Border_Region"]
        assert network.specialization == ["economic_espionage", "counter_intelligence"]
        assert network.agent_count == 25
        assert network.intelligence_capacity == 9


class TestEspionageRequestModels:
    """Test request model validation"""

    def test_create_espionage_request_validation(self):
        """Test create espionage request validation"""
        request_data = {
            "name": "Test Espionage Entity",
            "description": "A test entity for espionage operations",
            "properties": {"region": "test_region", "priority": "high"}
        }
        
        request = CreateEspionageRequest(**request_data)
        
        assert request.name == "Test Espionage Entity"
        assert request.description == "A test entity for espionage operations"
        assert request.properties == {"region": "test_region", "priority": "high"}

    def test_create_espionage_operation_request_validation(self):
        """Test create espionage operation request validation"""
        request_data = {
            "operation_type": EspionageOperationType.FACILITY_SABOTAGE,
            "initiator_id": uuid4(),
            "initiator_type": "faction",
            "target_id": uuid4(),
            "target_type": "business",
            "planned_start": datetime.utcnow() + timedelta(hours=2),
            "planned_duration": 8,
            "difficulty": 6,
            "agents_assigned": [uuid4(), uuid4()],
            "cover_story": "Routine maintenance inspection"
        }
        
        request = CreateEspionageOperationRequest(**request_data)
        
        assert request.operation_type == EspionageOperationType.FACILITY_SABOTAGE
        assert request.difficulty == 6
        assert len(request.agents_assigned) == 2
        assert request.cover_story == "Routine maintenance inspection"

    def test_create_espionage_agent_request_validation(self):
        """Test create espionage agent request validation"""
        request_data = {
            "npc_id": uuid4(),
            "role": AgentRole.SABOTEUR,
            "faction_id": uuid4(),
            "skill_level": 6,
            "cover_identity": "Blacksmith",
            "specializations": ["sabotage", "demolitions"]
        }
        
        request = CreateEspionageAgentRequest(**request_data)
        
        assert request.role == AgentRole.SABOTEUR
        assert request.skill_level == 6
        assert request.cover_identity == "Blacksmith"
        assert request.specializations == ["sabotage", "demolitions"]

    def test_create_economic_intelligence_request_validation(self):
        """Test create economic intelligence request validation"""
        request_data = {
            "intelligence_type": IntelligenceType.TRADE_ROUTE,
            "target_entity": uuid4(),
            "target_type": "faction",
            "data": {
                "routes": [
                    {"from": "City_A", "to": "City_B", "goods": ["grain", "textiles"]},
                    {"from": "City_B", "to": "City_C", "goods": ["metals", "gems"]}
                ]
            },
            "gathered_by": uuid4(),
            "reliability": 0.85,
            "strategic_value": 7
        }
        
        request = CreateEconomicIntelligenceRequest(**request_data)
        
        assert request.intelligence_type == IntelligenceType.TRADE_ROUTE
        assert request.reliability == 0.85
        assert request.strategic_value == 7
        assert len(request.data["routes"]) == 2

    def test_create_spy_network_request_validation(self):
        """Test create spy network request validation"""
        request_data = {
            "name": "Merchant's Eye Network",
            "faction_id": uuid4(),
            "spymaster_id": uuid4(),
            "coverage_area": ["Trade_District", "Harbor", "Market_Square"],
            "specialization": ["price_intelligence", "trade_route_monitoring"]
        }
        
        request = CreateSpyNetworkRequest(**request_data)
        
        assert request.name == "Merchant's Eye Network"
        assert request.coverage_area == ["Trade_District", "Harbor", "Market_Square"]
        assert request.specialization == ["price_intelligence", "trade_route_monitoring"]


class TestEspionageUpdateModels:
    """Test update model validation"""

    def test_update_espionage_request_validation(self):
        """Test update espionage request validation"""
        request_data = {
            "name": "Updated Espionage Entity",
            "status": "inactive",
            "properties": {"updated": True}
        }
        
        request = UpdateEspionageRequest(**request_data)
        
        assert request.name == "Updated Espionage Entity"
        assert request.status == "inactive"
        assert request.properties == {"updated": True}

    def test_update_espionage_operation_request_validation(self):
        """Test update espionage operation request validation"""
        request_data = {
            "status": EspionageOperationStatus.COMPLETED,
            "success_level": 0.8,
            "detection_level": 0.2,
            "intelligence_gained": ["intel_001", "intel_002"],
            "damage_dealt": {"economic_loss": 5000, "reputation_damage": 0.3}
        }
        
        request = UpdateEspionageOperationRequest(**request_data)
        
        assert request.status == EspionageOperationStatus.COMPLETED
        assert request.success_level == 0.8
        assert request.detection_level == 0.2
        assert request.intelligence_gained == ["intel_001", "intel_002"]
        assert request.damage_dealt == {"economic_loss": 5000, "reputation_damage": 0.3}

    def test_update_espionage_agent_request_validation(self):
        """Test update espionage agent request validation"""
        request_data = {
            "status": "active",
            "skill_level": 7,
            "loyalty": 8.5,
            "burn_risk": 0.3,
            "heat_level": 4
        }
        
        request = UpdateEspionageAgentRequest(**request_data)
        
        assert request.status == "active"
        assert request.skill_level == 7
        assert request.loyalty == 8.5
        assert request.burn_risk == 0.3
        assert request.heat_level == 4


class TestEspionageEnums:
    """Test espionage enum values"""

    def test_espionage_operation_type_enum(self):
        """Test espionage operation type enum values"""
        assert EspionageOperationType.TRADE_SECRET_THEFT == "trade_secret_theft"
        assert EspionageOperationType.PRICE_INTELLIGENCE == "price_intelligence"
        assert EspionageOperationType.SUPPLIER_INTELLIGENCE == "supplier_intelligence"
        assert EspionageOperationType.ROUTE_SURVEILLANCE == "route_surveillance"
        assert EspionageOperationType.FACILITY_SABOTAGE == "facility_sabotage"
        assert EspionageOperationType.SHIPMENT_SABOTAGE == "shipment_sabotage"
        assert EspionageOperationType.REPUTATION_SABOTAGE == "reputation_sabotage"
        assert EspionageOperationType.MARKET_MANIPULATION == "market_manipulation"
        assert EspionageOperationType.COUNTER_ESPIONAGE == "counter_espionage"
        assert EspionageOperationType.AGENT_RECRUITMENT == "agent_recruitment"
        assert EspionageOperationType.NETWORK_INFILTRATION == "network_infiltration"

    def test_espionage_operation_status_enum(self):
        """Test espionage operation status enum values"""
        assert EspionageOperationStatus.PLANNED == "planned"
        assert EspionageOperationStatus.IN_PROGRESS == "in_progress"
        assert EspionageOperationStatus.COMPLETED == "completed"
        assert EspionageOperationStatus.FAILED == "failed"
        assert EspionageOperationStatus.COMPROMISED == "compromised"
        assert EspionageOperationStatus.ABANDONED == "abandoned"

    def test_intelligence_type_enum(self):
        """Test intelligence type enum values"""
        assert IntelligenceType.PRICING_DATA == "pricing_data"
        assert IntelligenceType.SUPPLIER_LIST == "supplier_list"
        assert IntelligenceType.TRADE_ROUTE == "trade_route"
        assert IntelligenceType.INVENTORY_LEVEL == "inventory_level"
        assert IntelligenceType.FINANCIAL_DATA == "financial_data"
        assert IntelligenceType.STRATEGIC_PLAN == "strategic_plan"
        assert IntelligenceType.WEAKNESS_ANALYSIS == "weakness_analysis"
        assert IntelligenceType.MARKET_SHARE == "market_share"

    def test_agent_role_enum(self):
        """Test agent role enum values"""
        assert AgentRole.SPYMASTER == "spymaster"
        assert AgentRole.INFILTRATOR == "infiltrator"
        assert AgentRole.INFORMANT == "informant"
        assert AgentRole.SABOTEUR == "saboteur"
        assert AgentRole.COURIER == "courier"
        assert AgentRole.ANALYST == "analyst"
        assert AgentRole.HANDLER == "handler"
        assert AgentRole.SLEEPER == "sleeper"

    def test_network_status_enum(self):
        """Test network status enum values"""
        assert NetworkStatus.ACTIVE == "active"
        assert NetworkStatus.COMPROMISED == "compromised"
        assert NetworkStatus.DORMANT == "dormant"
        assert NetworkStatus.DISBANDED == "disbanded"
        assert NetworkStatus.REBUILDING == "rebuilding" 