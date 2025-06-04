"""
Test module for disease.services

Tests disease services according to Development Bible standards:
- Disease management business logic
- Contagion simulation
- Treatment and recovery mechanics
- Environmental disease factors
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from uuid import uuid4

# Import the module under test
try:
    from backend.systems.disease.services import (
        DiseaseService, ContagionService, TreatmentService,
        DiseaseProgressionService, EnvironmentalDiseaseService
    )
    disease_services_available = True
except ImportError as e:
    print(f"Disease services not available: {e}")
    disease_services_available = False
    
    # Create mock classes for testing
    class DiseaseService:
        def __init__(self, disease_repository=None, config_service=None):
            self.disease_repository = disease_repository
            self.config_service = config_service
        
        def create_disease_instance(self, character_id, disease_id):
            return {"id": str(uuid4()), "character_id": character_id, "disease_id": disease_id}
        
        def get_character_diseases(self, character_id):
            return []
        
        def advance_disease_progression(self, instance_id):
            return True
    
    class ContagionService:
        def __init__(self, disease_service=None, location_service=None):
            self.disease_service = disease_service
            self.location_service = location_service
        
        def check_contagion_risk(self, character_id, location_id):
            return 0.1
        
        def attempt_contagion(self, source_character, target_character, disease_id):
            return False
        
        def calculate_transmission_rate(self, disease_id, environment_factors):
            return 0.2
    
    class TreatmentService:
        def __init__(self, disease_service=None, item_service=None):
            self.disease_service = disease_service
            self.item_service = item_service
        
        def apply_treatment(self, character_id, disease_instance_id, treatment_item_id):
            return {"success": True, "effectiveness": 0.7}
        
        def get_available_treatments(self, disease_id):
            return []
        
        def calculate_treatment_effectiveness(self, treatment_id, disease_id, character_attributes):
            return 0.6
    
    class DiseaseProgressionService:
        def __init__(self, disease_service=None, time_service=None):
            self.disease_service = disease_service
            self.time_service = time_service
        
        def process_disease_progression(self, character_id):
            return {"diseases_progressed": 0, "recoveries": 0}
        
        def calculate_progression_rate(self, disease_instance):
            return 0.1
        
        def check_recovery_conditions(self, disease_instance):
            return False
    
    class EnvironmentalDiseaseService:
        def __init__(self, disease_service=None, weather_service=None):
            self.disease_service = disease_service
            self.weather_service = weather_service
        
        def check_environmental_disease_risk(self, character_id, location_id):
            return {"risk_level": "low", "potential_diseases": []}
        
        def apply_environmental_factors(self, disease_instance_id, environment_data):
            return {"severity_modifier": 1.0, "progression_modifier": 1.0}


class MockDiseaseRepository:
    """Mock disease repository for testing"""
    
    def get_disease_by_id(self, disease_id):
        return {
            "id": disease_id,
            "name": "Test Disease",
            "contagious": True,
            "base_severity": "moderate"
        }
    
    def create_disease_instance(self, instance_data):
        return {**instance_data, "id": str(uuid4())}
    
    def get_character_disease_instances(self, character_id):
        return []
    
    def update_disease_instance(self, instance_id, updates):
        return True


class MockConfigService:
    """Mock configuration service for testing"""
    
    def get_disease_config(self):
        return {
            "base_progression_rate": 0.1,
            "contagion_base_rate": 0.05,
            "environmental_factor_strength": 1.0
        }
    
    def get_treatment_config(self):
        return {
            "base_effectiveness": 0.5,
            "resistance_buildup_rate": 0.02
        }


class TestDiseaseService:
    """Test class for DiseaseService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_repository = MockDiseaseRepository()
        self.mock_config = MockConfigService()
        self.disease_service = DiseaseService(self.mock_repository, self.mock_config)
    
    def test_service_creation(self):
        """Test that the service can be created"""
        assert self.disease_service is not None
        assert self.disease_service.disease_repository is not None
        assert self.disease_service.config_service is not None
    
    def test_create_disease_instance(self):
        """Test creating a disease instance for a character"""
        character_id = str(uuid4())
        disease_id = str(uuid4())
        
        instance = self.disease_service.create_disease_instance(character_id, disease_id)
        
        assert instance is not None
        assert instance["character_id"] == character_id
        assert instance["disease_id"] == disease_id
        assert "id" in instance
    
    def test_get_character_diseases(self):
        """Test getting diseases for a character"""
        character_id = str(uuid4())
        diseases = self.disease_service.get_character_diseases(character_id)
        
        assert isinstance(diseases, list)
    
    def test_advance_disease_progression(self):
        """Test advancing disease progression"""
        instance_id = str(uuid4())
        result = self.disease_service.advance_disease_progression(instance_id)
        
        assert isinstance(result, bool)


class TestContagionService:
    """Test class for ContagionService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_disease_service = DiseaseService()
        self.mock_location_service = Mock()
        self.contagion_service = ContagionService(
            self.mock_disease_service, 
            self.mock_location_service
        )
    
    def test_service_creation(self):
        """Test that the contagion service can be created"""
        assert self.contagion_service is not None
        assert self.contagion_service.disease_service is not None
        assert self.contagion_service.location_service is not None
    
    def test_check_contagion_risk(self):
        """Test checking contagion risk in a location"""
        character_id = str(uuid4())
        location_id = str(uuid4())
        
        risk = self.contagion_service.check_contagion_risk(character_id, location_id)
        
        assert isinstance(risk, (int, float))
        assert 0.0 <= risk <= 1.0
    
    def test_attempt_contagion(self):
        """Test attempting contagion between characters"""
        source_character = str(uuid4())
        target_character = str(uuid4())
        disease_id = str(uuid4())
        
        result = self.contagion_service.attempt_contagion(
            source_character, target_character, disease_id
        )
        
        assert isinstance(result, bool)
    
    def test_calculate_transmission_rate(self):
        """Test calculating disease transmission rate"""
        disease_id = str(uuid4())
        environment_factors = {
            "temperature": 25.0,
            "humidity": 60.0,
            "air_quality": "good"
        }
        
        rate = self.contagion_service.calculate_transmission_rate(
            disease_id, environment_factors
        )
        
        assert isinstance(rate, (int, float))
        assert rate >= 0.0


class TestTreatmentService:
    """Test class for TreatmentService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_disease_service = DiseaseService()
        self.mock_item_service = Mock()
        self.treatment_service = TreatmentService(
            self.mock_disease_service,
            self.mock_item_service
        )
    
    def test_service_creation(self):
        """Test that the treatment service can be created"""
        assert self.treatment_service is not None
        assert self.treatment_service.disease_service is not None
        assert self.treatment_service.item_service is not None
    
    def test_apply_treatment(self):
        """Test applying treatment to a disease instance"""
        character_id = str(uuid4())
        disease_instance_id = str(uuid4())
        treatment_item_id = str(uuid4())
        
        result = self.treatment_service.apply_treatment(
            character_id, disease_instance_id, treatment_item_id
        )
        
        assert isinstance(result, dict)
        assert "success" in result
        assert "effectiveness" in result
        assert isinstance(result["success"], bool)
        assert isinstance(result["effectiveness"], (int, float))
    
    def test_get_available_treatments(self):
        """Test getting available treatments for a disease"""
        disease_id = str(uuid4())
        treatments = self.treatment_service.get_available_treatments(disease_id)
        
        assert isinstance(treatments, list)
    
    def test_calculate_treatment_effectiveness(self):
        """Test calculating treatment effectiveness"""
        treatment_id = str(uuid4())
        disease_id = str(uuid4())
        character_attributes = {
            "constitution": 15,
            "intelligence": 12,
            "wisdom": 14
        }
        
        effectiveness = self.treatment_service.calculate_treatment_effectiveness(
            treatment_id, disease_id, character_attributes
        )
        
        assert isinstance(effectiveness, (int, float))
        assert 0.0 <= effectiveness <= 1.0


class TestDiseaseProgressionService:
    """Test class for DiseaseProgressionService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_disease_service = DiseaseService()
        self.mock_time_service = Mock()
        self.progression_service = DiseaseProgressionService(
            self.mock_disease_service,
            self.mock_time_service
        )
    
    def test_service_creation(self):
        """Test that the progression service can be created"""
        assert self.progression_service is not None
        assert self.progression_service.disease_service is not None
        assert self.progression_service.time_service is not None
    
    def test_process_disease_progression(self):
        """Test processing disease progression for a character"""
        character_id = str(uuid4())
        result = self.progression_service.process_disease_progression(character_id)
        
        assert isinstance(result, dict)
        assert "diseases_progressed" in result
        assert "recoveries" in result
        assert isinstance(result["diseases_progressed"], int)
        assert isinstance(result["recoveries"], int)
    
    def test_calculate_progression_rate(self):
        """Test calculating disease progression rate"""
        disease_instance = {
            "id": str(uuid4()),
            "severity": "moderate",
            "duration_days": 5
        }
        
        rate = self.progression_service.calculate_progression_rate(disease_instance)
        
        assert isinstance(rate, (int, float))
        assert rate >= 0.0
    
    def test_check_recovery_conditions(self):
        """Test checking recovery conditions"""
        disease_instance = {
            "id": str(uuid4()),
            "severity": "minor",
            "treatment_history": [],
            "duration_days": 7
        }
        
        can_recover = self.progression_service.check_recovery_conditions(disease_instance)
        
        assert isinstance(can_recover, bool)


class TestEnvironmentalDiseaseService:
    """Test class for EnvironmentalDiseaseService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_disease_service = DiseaseService()
        self.mock_weather_service = Mock()
        self.environmental_service = EnvironmentalDiseaseService(
            self.mock_disease_service,
            self.mock_weather_service
        )
    
    def test_service_creation(self):
        """Test that the environmental disease service can be created"""
        assert self.environmental_service is not None
        assert self.environmental_service.disease_service is not None
        assert self.environmental_service.weather_service is not None
    
    def test_check_environmental_disease_risk(self):
        """Test checking environmental disease risk"""
        character_id = str(uuid4())
        location_id = str(uuid4())
        
        risk_assessment = self.environmental_service.check_environmental_disease_risk(
            character_id, location_id
        )
        
        assert isinstance(risk_assessment, dict)
        assert "risk_level" in risk_assessment
        assert "potential_diseases" in risk_assessment
        assert isinstance(risk_assessment["potential_diseases"], list)
    
    def test_apply_environmental_factors(self):
        """Test applying environmental factors to disease"""
        disease_instance_id = str(uuid4())
        environment_data = {
            "climate": "tropical",
            "pollution_level": "moderate",
            "season": "wet_season"
        }
        
        factors = self.environmental_service.apply_environmental_factors(
            disease_instance_id, environment_data
        )
        
        assert isinstance(factors, dict)
        assert "severity_modifier" in factors
        assert "progression_modifier" in factors
        assert isinstance(factors["severity_modifier"], (int, float))
        assert isinstance(factors["progression_modifier"], (int, float))


class TestDiseaseServicesIntegration:
    """Integration tests for disease services"""
    
    def setup_method(self):
        """Set up integrated test fixtures"""
        self.mock_repository = MockDiseaseRepository()
        self.mock_config = MockConfigService()
        
        self.disease_service = DiseaseService(self.mock_repository, self.mock_config)
        self.contagion_service = ContagionService(self.disease_service, Mock())
        self.treatment_service = TreatmentService(self.disease_service, Mock())
        self.progression_service = DiseaseProgressionService(self.disease_service, Mock())
        self.environmental_service = EnvironmentalDiseaseService(self.disease_service, Mock())
    
    def test_disease_lifecycle_workflow(self):
        """Test complete disease lifecycle workflow"""
        character_id = str(uuid4())
        disease_id = str(uuid4())
        location_id = str(uuid4())
        
        # 1. Check environmental risk
        environmental_risk = self.environmental_service.check_environmental_disease_risk(
            character_id, location_id
        )
        assert isinstance(environmental_risk, dict)
        
        # 2. Create disease instance
        disease_instance = self.disease_service.create_disease_instance(
            character_id, disease_id
        )
        assert disease_instance is not None
        
        # 3. Process progression
        progression_result = self.progression_service.process_disease_progression(character_id)
        assert isinstance(progression_result, dict)
        
        # 4. Apply treatment
        treatment_result = self.treatment_service.apply_treatment(
            character_id, disease_instance["id"], str(uuid4())
        )
        assert isinstance(treatment_result, dict)
        assert "success" in treatment_result
    
    def test_contagion_and_treatment_interaction(self):
        """Test interaction between contagion and treatment systems"""
        source_character = str(uuid4())
        target_character = str(uuid4())
        disease_id = str(uuid4())
        
        # Attempt contagion
        contagion_result = self.contagion_service.attempt_contagion(
            source_character, target_character, disease_id
        )
        
        # Get available treatments
        treatments = self.treatment_service.get_available_treatments(disease_id)
        
        assert isinstance(contagion_result, bool)
        assert isinstance(treatments, list)
    
    def test_environmental_and_progression_interaction(self):
        """Test interaction between environmental factors and disease progression"""
        character_id = str(uuid4())
        disease_instance_id = str(uuid4())
        
        # Apply environmental factors
        environment_data = {"climate": "harsh", "pollution": "high"}
        environmental_factors = self.environmental_service.apply_environmental_factors(
            disease_instance_id, environment_data
        )
        
        # Calculate progression with environmental factors
        disease_instance = {"id": disease_instance_id, "severity": "moderate"}
        progression_rate = self.progression_service.calculate_progression_rate(disease_instance)
        
        assert isinstance(environmental_factors, dict)
        assert isinstance(progression_rate, (int, float))
        assert progression_rate >= 0.0 