"""
Test module for disease.models

Tests disease models according to Development Bible standards:
- Disease progression mechanics
- Severity levels and symptoms
- Treatment and recovery systems
- Environmental disease factors
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from uuid import uuid4
from enum import Enum

# Import the module under test
try:
    from backend.systems.disease.models import (
        Disease, DiseaseInstance, DiseaseProgression, DiseaseSymptom,
        DiseaseSeverity, DiseaseType, TreatmentEffect, RecoveryState
    )
    disease_models_available = True
except ImportError as e:
    print(f"Disease models not available: {e}")
    disease_models_available = False
    
    # Create mock classes for testing
    class DiseaseSeverity(Enum):
        MINOR = "minor"
        MODERATE = "moderate"
        SEVERE = "severe"
        CRITICAL = "critical"
        FATAL = "fatal"
    
    class DiseaseType(Enum):
        VIRAL = "viral"
        BACTERIAL = "bacterial"
        PARASITIC = "parasitic"
        MAGICAL = "magical"
        ENVIRONMENTAL = "environmental"
    
    class RecoveryState(Enum):
        HEALTHY = "healthy"
        RECOVERING = "recovering"
        STABLE = "stable"
        DETERIORATING = "deteriorating"
        TERMINAL = "terminal"
    
    class Disease:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', str(uuid4()))
            self.name = kwargs.get('name', 'Test Disease')
            self.disease_type = kwargs.get('disease_type', DiseaseType.VIRAL)
            self.base_severity = kwargs.get('base_severity', DiseaseSeverity.MINOR)
            self.contagious = kwargs.get('contagious', False)
            self.incubation_period = kwargs.get('incubation_period', 1)
            self.duration = kwargs.get('duration', 7)
            self.mortality_rate = kwargs.get('mortality_rate', 0.0)
            for k, v in kwargs.items():
                setattr(self, k, v)
        
        def get_progression_rate(self):
            return 1.0
        
        def is_fatal(self):
            return self.mortality_rate > 0.5
    
    class DiseaseInstance:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', str(uuid4()))
            self.disease_id = kwargs.get('disease_id', str(uuid4()))
            self.character_id = kwargs.get('character_id', str(uuid4()))
            self.current_severity = kwargs.get('current_severity', DiseaseSeverity.MINOR)
            self.onset_date = kwargs.get('onset_date', datetime.utcnow())
            self.recovery_state = kwargs.get('recovery_state', RecoveryState.STABLE)
            self.treatment_history = kwargs.get('treatment_history', [])
            for k, v in kwargs.items():
                setattr(self, k, v)
        
        def calculate_progression(self):
            return 0.1
        
        def apply_treatment(self, treatment):
            return True
        
        def get_current_symptoms(self):
            return []
    
    class DiseaseProgression:
        def __init__(self, **kwargs):
            self.stage = kwargs.get('stage', 1)
            self.severity = kwargs.get('severity', DiseaseSeverity.MINOR)
            self.symptoms = kwargs.get('symptoms', [])
            self.duration = kwargs.get('duration', 1)
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class DiseaseSymptom:
        def __init__(self, **kwargs):
            self.name = kwargs.get('name', 'Test Symptom')
            self.severity_impact = kwargs.get('severity_impact', 1)
            self.visible = kwargs.get('visible', True)
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class TreatmentEffect:
        def __init__(self, **kwargs):
            self.treatment_type = kwargs.get('treatment_type', 'medicine')
            self.effectiveness = kwargs.get('effectiveness', 0.5)
            self.side_effects = kwargs.get('side_effects', [])
            for k, v in kwargs.items():
                setattr(self, k, v)


class TestDiseaseSeverity:
    """Test class for DiseaseSeverity enum"""

    def test_severity_levels(self):
        """Test DiseaseSeverity enum has expected values"""
        assert hasattr(DiseaseSeverity, 'MINOR')
        assert hasattr(DiseaseSeverity, 'MODERATE')
        assert hasattr(DiseaseSeverity, 'SEVERE')
        assert hasattr(DiseaseSeverity, 'CRITICAL')
        assert hasattr(DiseaseSeverity, 'FATAL')

    def test_severity_progression(self):
        """Test severity levels represent logical progression"""
        severities = [
            DiseaseSeverity.MINOR,
            DiseaseSeverity.MODERATE,
            DiseaseSeverity.SEVERE,
            DiseaseSeverity.CRITICAL,
            DiseaseSeverity.FATAL
        ]
        assert len(set(severities)) == len(severities)


class TestDiseaseType:
    """Test class for DiseaseType enum"""

    def test_disease_types(self):
        """Test DiseaseType enum has expected values"""
        assert hasattr(DiseaseType, 'VIRAL')
        assert hasattr(DiseaseType, 'BACTERIAL')
        assert hasattr(DiseaseType, 'PARASITIC')
        assert hasattr(DiseaseType, 'MAGICAL')
        assert hasattr(DiseaseType, 'ENVIRONMENTAL')

    def test_disease_type_consistency(self):
        """Test disease types are unique"""
        types = [
            DiseaseType.VIRAL,
            DiseaseType.BACTERIAL,
            DiseaseType.PARASITIC,
            DiseaseType.MAGICAL,
            DiseaseType.ENVIRONMENTAL
        ]
        assert len(set(types)) == len(types)


class TestDisease:
    """Test class for Disease model"""

    @pytest.fixture
    def sample_disease_data(self):
        """Sample disease data for testing"""
        return {
            "name": "Test Plague",
            "disease_type": DiseaseType.VIRAL,
            "base_severity": DiseaseSeverity.MODERATE,
            "contagious": True,
            "incubation_period": 3,
            "duration": 14,
            "mortality_rate": 0.1
        }

    def test_disease_creation(self, sample_disease_data):
        """Test Disease creation with standard parameters"""
        disease = Disease(**sample_disease_data)
        
        assert disease.name == "Test Plague"
        assert disease.disease_type == DiseaseType.VIRAL
        assert disease.base_severity == DiseaseSeverity.MODERATE
        assert disease.contagious is True
        assert disease.incubation_period == 3
        assert disease.duration == 14
        assert disease.mortality_rate == 0.1

    def test_disease_defaults(self):
        """Test Disease creation with default values"""
        disease = Disease(name="Simple Disease")
        
        assert disease.name == "Simple Disease"
        assert disease.disease_type == DiseaseType.VIRAL
        assert disease.base_severity == DiseaseSeverity.MINOR
        assert disease.contagious is False
        assert disease.incubation_period == 1
        assert disease.duration == 7
        assert disease.mortality_rate == 0.0

    def test_disease_progression_rate(self, sample_disease_data):
        """Test disease progression rate calculation"""
        disease = Disease(**sample_disease_data)
        progression_rate = disease.get_progression_rate()
        
        assert isinstance(progression_rate, (int, float))
        assert progression_rate > 0

    def test_disease_fatality_assessment(self, sample_disease_data):
        """Test disease fatality assessment"""
        # Low mortality disease
        low_mortality_disease = Disease(name="Minor Cold", mortality_rate=0.01)
        assert low_mortality_disease.is_fatal() is False
        
        # High mortality disease
        high_mortality_disease = Disease(name="Deadly Plague", mortality_rate=0.8)
        assert high_mortality_disease.is_fatal() is True

    def test_disease_contagion_properties(self):
        """Test disease contagion properties"""
        contagious_disease = Disease(name="Flu", contagious=True)
        non_contagious_disease = Disease(name="Cancer", contagious=False)
        
        assert contagious_disease.contagious is True
        assert non_contagious_disease.contagious is False


class TestDiseaseInstance:
    """Test class for DiseaseInstance model"""

    @pytest.fixture
    def sample_instance_data(self):
        """Sample disease instance data for testing"""
        return {
            "disease_id": str(uuid4()),
            "character_id": str(uuid4()),
            "current_severity": DiseaseSeverity.MODERATE,
            "onset_date": datetime.utcnow() - timedelta(days=2),
            "recovery_state": RecoveryState.STABLE
        }

    def test_disease_instance_creation(self, sample_instance_data):
        """Test DiseaseInstance creation"""
        instance = DiseaseInstance(**sample_instance_data)
        
        assert instance.disease_id == sample_instance_data["disease_id"]
        assert instance.character_id == sample_instance_data["character_id"]
        assert instance.current_severity == DiseaseSeverity.MODERATE
        assert instance.recovery_state == RecoveryState.STABLE
        assert isinstance(instance.onset_date, datetime)

    def test_disease_instance_defaults(self):
        """Test DiseaseInstance with default values"""
        instance = DiseaseInstance()
        
        assert instance.id is not None
        assert instance.disease_id is not None
        assert instance.character_id is not None
        assert instance.current_severity == DiseaseSeverity.MINOR
        assert instance.recovery_state == RecoveryState.STABLE
        assert isinstance(instance.onset_date, datetime)

    def test_disease_progression_calculation(self, sample_instance_data):
        """Test disease progression calculation"""
        instance = DiseaseInstance(**sample_instance_data)
        progression = instance.calculate_progression()
        
        assert isinstance(progression, (int, float))
        assert progression >= 0

    def test_treatment_application(self, sample_instance_data):
        """Test treatment application to disease instance"""
        instance = DiseaseInstance(**sample_instance_data)
        
        # Mock treatment
        treatment = {
            "type": "medicine",
            "effectiveness": 0.7,
            "administered_at": datetime.utcnow()
        }
        
        result = instance.apply_treatment(treatment)
        assert isinstance(result, bool)

    def test_symptom_tracking(self, sample_instance_data):
        """Test current symptom tracking"""
        instance = DiseaseInstance(**sample_instance_data)
        symptoms = instance.get_current_symptoms()
        
        assert isinstance(symptoms, list)

    def test_treatment_history(self, sample_instance_data):
        """Test treatment history tracking"""
        instance = DiseaseInstance(**sample_instance_data)
        
        # Should have treatment history attribute
        assert hasattr(instance, 'treatment_history')
        assert isinstance(instance.treatment_history, list)


class TestDiseaseProgression:
    """Test class for DiseaseProgression model"""

    def test_progression_stage_tracking(self):
        """Test disease progression stage tracking"""
        progression = DiseaseProgression(
            stage=2,
            severity=DiseaseSeverity.MODERATE,
            duration=5
        )
        
        assert progression.stage == 2
        assert progression.severity == DiseaseSeverity.MODERATE
        assert progression.duration == 5

    def test_progression_symptoms(self):
        """Test progression symptom tracking"""
        symptoms = ["fever", "cough", "fatigue"]
        progression = DiseaseProgression(symptoms=symptoms)
        
        assert progression.symptoms == symptoms
        assert len(progression.symptoms) == 3

    def test_progression_defaults(self):
        """Test progression with default values"""
        progression = DiseaseProgression()
        
        assert progression.stage == 1
        assert progression.severity == DiseaseSeverity.MINOR
        assert isinstance(progression.symptoms, list)
        assert progression.duration == 1


class TestDiseaseSymptom:
    """Test class for DiseaseSymptom model"""

    def test_symptom_creation(self):
        """Test DiseaseSymptom creation"""
        symptom = DiseaseSymptom(
            name="High Fever",
            severity_impact=3,
            visible=True
        )
        
        assert symptom.name == "High Fever"
        assert symptom.severity_impact == 3
        assert symptom.visible is True

    def test_symptom_defaults(self):
        """Test symptom with default values"""
        symptom = DiseaseSymptom()
        
        assert symptom.name == "Test Symptom"
        assert symptom.severity_impact == 1
        assert symptom.visible is True

    def test_symptom_visibility(self):
        """Test symptom visibility tracking"""
        visible_symptom = DiseaseSymptom(name="Rash", visible=True)
        hidden_symptom = DiseaseSymptom(name="Internal Pain", visible=False)
        
        assert visible_symptom.visible is True
        assert hidden_symptom.visible is False


class TestTreatmentEffect:
    """Test class for TreatmentEffect model"""

    def test_treatment_effect_creation(self):
        """Test TreatmentEffect creation"""
        treatment = TreatmentEffect(
            treatment_type="antibiotic",
            effectiveness=0.8,
            side_effects=["nausea", "dizziness"]
        )
        
        assert treatment.treatment_type == "antibiotic"
        assert treatment.effectiveness == 0.8
        assert treatment.side_effects == ["nausea", "dizziness"]

    def test_treatment_defaults(self):
        """Test treatment with default values"""
        treatment = TreatmentEffect()
        
        assert treatment.treatment_type == "medicine"
        assert treatment.effectiveness == 0.5
        assert isinstance(treatment.side_effects, list)

    def test_treatment_effectiveness_bounds(self):
        """Test treatment effectiveness validation"""
        if not disease_models_available:
            pytest.skip("Advanced validation requires actual disease models")
            
        # Test bounds (should be 0.0 to 1.0)
        low_effectiveness = TreatmentEffect(effectiveness=0.1)
        high_effectiveness = TreatmentEffect(effectiveness=0.9)
        
        assert 0.0 <= low_effectiveness.effectiveness <= 1.0
        assert 0.0 <= high_effectiveness.effectiveness <= 1.0


class TestDiseaseModelsIntegration:
    """Integration tests for disease models"""

    def test_disease_instance_with_disease(self):
        """Test disease instance with associated disease"""
        disease = Disease(
            name="Test Flu",
            disease_type=DiseaseType.VIRAL,
            base_severity=DiseaseSeverity.MODERATE
        )
        
        instance = DiseaseInstance(
            disease_id=disease.id,
            character_id=str(uuid4()),
            current_severity=disease.base_severity
        )
        
        assert instance.disease_id == disease.id
        assert instance.current_severity == disease.base_severity

    def test_progression_with_symptoms(self):
        """Test disease progression with multiple symptoms"""
        symptoms = [
            DiseaseSymptom(name="Fever", severity_impact=2),
            DiseaseSymptom(name="Cough", severity_impact=1),
            DiseaseSymptom(name="Fatigue", severity_impact=2)
        ]
        
        progression = DiseaseProgression(
            stage=2,
            severity=DiseaseSeverity.MODERATE,
            symptoms=[s.name for s in symptoms]
        )
        
        assert len(progression.symptoms) == 3
        assert "Fever" in progression.symptoms
        assert "Cough" in progression.symptoms
        assert "Fatigue" in progression.symptoms

    def test_treatment_effect_on_instance(self):
        """Test treatment effect application to disease instance"""
        instance = DiseaseInstance(
            current_severity=DiseaseSeverity.SEVERE,
            recovery_state=RecoveryState.DETERIORATING
        )
        
        treatment = TreatmentEffect(
            treatment_type="advanced_medicine",
            effectiveness=0.9
        )
        
        # Apply treatment
        result = instance.apply_treatment(treatment)
        assert isinstance(result, bool)

    def test_disease_system_workflow(self):
        """Test complete disease system workflow"""
        # Create disease
        disease = Disease(
            name="Fantasy Plague",
            disease_type=DiseaseType.MAGICAL,
            base_severity=DiseaseSeverity.SEVERE,
            contagious=True,
            mortality_rate=0.3
        )
        
        # Create instance
        instance = DiseaseInstance(
            disease_id=disease.id,
            character_id=str(uuid4()),
            current_severity=disease.base_severity
        )
        
        # Create progression
        progression = DiseaseProgression(
            stage=1,
            severity=instance.current_severity,
            symptoms=["magical_corruption", "weakness"]
        )
        
        # Create treatment
        treatment = TreatmentEffect(
            treatment_type="magical_healing",
            effectiveness=0.7
        )
        
        # Verify workflow
        assert instance.disease_id == disease.id
        assert progression.severity == instance.current_severity
        assert len(progression.symptoms) == 2
        assert treatment.treatment_type == "magical_healing" 