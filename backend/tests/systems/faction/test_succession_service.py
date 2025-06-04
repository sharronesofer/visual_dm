"""
Comprehensive tests for Faction Succession Service

Tests all succession crisis functionality according to Task 69 requirements:
- Different succession types by faction type
- Crisis triggers and vulnerability calculation
- Candidate competition and scoring
- External interference
- Crisis resolution and faction splits
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from backend.systems.faction.services.succession_service import FactionSuccessionService
from backend.infrastructure.models.faction.models import FactionEntity
from backend.systems.faction.models.succession import (
    SuccessionCrisisEntity,
    SuccessionType,
    SuccessionCrisisStatus,
    SuccessionTrigger,
    SuccessionCandidate,
    CreateSuccessionCrisisRequest,
    UpdateSuccessionCrisisRequest,
    AddCandidateRequest
)
from backend.infrastructure.schemas.faction.faction_types import FactionType
from backend.infrastructure.shared.exceptions import FactionNotFoundError


# Module-level fixtures that can be shared across all test classes
@pytest.fixture
def succession_service():
    """Create succession service instance"""
    return FactionSuccessionService()

@pytest.fixture
def mock_db():
    """Create mock database session"""
    return Mock(spec=Session)

@pytest.fixture
def trading_company_faction():
    """Create Royal Bay Trading Company faction for testing"""
    faction = Mock(spec=FactionEntity)
    faction.id = uuid.uuid4()
    faction.name = "Royal Bay Trading Company"
    faction.properties = {"faction_type": "trading_company"}
    faction.get_hidden_attributes.return_value = {
        "hidden_ambition": 4,
        "hidden_integrity": 3,
        "hidden_discipline": 5,
        "hidden_impulsivity": 2,
        "hidden_pragmatism": 5,
        "hidden_resilience": 4
    }
    return faction

@pytest.fixture
def military_faction():
    """Create military faction for testing"""
    faction = Mock(spec=FactionEntity)
    faction.id = uuid.uuid4()
    faction.name = "Iron Legion"
    faction.properties = {"faction_type": "military"}
    faction.get_hidden_attributes.return_value = {
        "hidden_ambition": 5,
        "hidden_integrity": 2,
        "hidden_discipline": 4,
        "hidden_impulsivity": 4,
        "hidden_pragmatism": 3,
        "hidden_resilience": 3
    }
    return faction

@pytest.fixture
def religious_faction():
    """Create religious faction for testing"""
    faction = Mock(spec=FactionEntity)
    faction.id = uuid.uuid4()
    faction.name = "Temple of Light"
    faction.properties = {"faction_type": "religious"}
    faction.get_hidden_attributes.return_value = {
        "hidden_ambition": 2,
        "hidden_integrity": 5,
        "hidden_discipline": 5,
        "hidden_impulsivity": 1,
        "hidden_pragmatism": 3,
        "hidden_resilience": 4
    }
    return faction

@pytest.fixture
def guild_faction():
    """Create guild faction for testing"""
    faction = Mock(spec=FactionEntity)
    faction.id = uuid.uuid4()
    faction.name = "Artisan's Guild"
    faction.properties = {"faction_type": "guild"}
    faction.get_hidden_attributes.return_value = {
        "hidden_ambition": 3,
        "hidden_integrity": 4,
        "hidden_discipline": 5,
        "hidden_impulsivity": 2,
        "hidden_pragmatism": 4,
        "hidden_resilience": 3
    }
    return faction


class TestFactionSuccessionService:
    """Test suite for FactionSuccessionService - Base class for organization"""
    pass


class TestSuccessionTypeMapping:
    """Test succession type determination by faction type"""
    
    def test_trading_company_succession_type(self, succession_service, trading_company_faction):
        """Test that trading companies use economic competition"""
        succession_type = succession_service.determine_succession_type(trading_company_faction)
        assert succession_type == SuccessionType.ECONOMIC_COMPETITION
    
    def test_military_faction_hereditary(self, succession_service, military_faction):
        """Test military faction with low ambition uses hereditary succession"""
        # Adjust attributes for hereditary succession
        military_faction.get_hidden_attributes.return_value["hidden_ambition"] = 2
        military_faction.get_hidden_attributes.return_value["hidden_integrity"] = 4
        
        succession_type = succession_service.determine_succession_type(military_faction)
        assert succession_type == SuccessionType.HEREDITARY
    
    @patch('random.random')
    def test_military_faction_coup(self, mock_random, succession_service, military_faction):
        """Test military faction with high ambition/low integrity triggers coup"""
        # Set up for military coup (high ambition, low integrity)
        military_faction.get_hidden_attributes.return_value["hidden_ambition"] = 5
        military_faction.get_hidden_attributes.return_value["hidden_integrity"] = 1
        
        # Mock random to ensure coup triggers
        mock_random.return_value = 0.5  # Less than coup_chance
        
        succession_type = succession_service.determine_succession_type(military_faction)
        assert succession_type == SuccessionType.MILITARY_COUP
    
    def test_religious_faction_election(self, succession_service, religious_faction):
        """Test religious faction with high integrity uses election"""
        succession_type = succession_service.determine_succession_type(religious_faction)
        assert succession_type == SuccessionType.RELIGIOUS_ELECTION
    
    def test_religious_faction_divine_mandate(self, succession_service, religious_faction):
        """Test religious faction with low integrity claims divine mandate"""
        # Adjust for divine mandate
        religious_faction.get_hidden_attributes.return_value["hidden_integrity"] = 2
        
        succession_type = succession_service.determine_succession_type(religious_faction)
        assert succession_type == SuccessionType.DIVINE_MANDATE
    
    def test_guild_faction_merit_selection(self, succession_service, guild_faction):
        """Test guild faction with high discipline uses merit selection"""
        succession_type = succession_service.determine_succession_type(guild_faction)
        assert succession_type == SuccessionType.MERIT_SELECTION
    
    def test_guild_faction_democratic_election(self, succession_service, guild_faction):
        """Test guild faction with low discipline uses democratic election"""
        # Adjust for democratic election
        guild_faction.get_hidden_attributes.return_value["hidden_discipline"] = 2
        
        succession_type = succession_service.determine_succession_type(guild_faction)
        assert succession_type == SuccessionType.DEMOCRATIC_ELECTION


class TestVulnerabilityCalculation:
    """Test succession vulnerability calculation"""
    
    def test_high_ambition_increases_vulnerability(self, succession_service, trading_company_faction):
        """Test that high ambition increases succession vulnerability"""
        # High ambition faction
        trading_company_faction.get_hidden_attributes.return_value["hidden_ambition"] = 6
        
        vulnerability = succession_service.calculate_succession_vulnerability(trading_company_faction)
        assert vulnerability > 0.3  # Should be relatively high
    
    def test_high_resilience_reduces_vulnerability(self, succession_service, trading_company_faction):
        """Test that high resilience reduces succession vulnerability"""
        # High resilience faction
        trading_company_faction.get_hidden_attributes.return_value["hidden_resilience"] = 6
        trading_company_faction.get_hidden_attributes.return_value["hidden_ambition"] = 1
        trading_company_faction.get_hidden_attributes.return_value["hidden_impulsivity"] = 1
        trading_company_faction.get_hidden_attributes.return_value["hidden_discipline"] = 6
        
        vulnerability = succession_service.calculate_succession_vulnerability(trading_company_faction)
        assert vulnerability < 0.5  # Should be reduced by resilience
    
    def test_impulsivity_increases_vulnerability(self, succession_service, trading_company_faction):
        """Test that high impulsivity increases vulnerability"""
        # High impulsivity faction
        trading_company_faction.get_hidden_attributes.return_value["hidden_impulsivity"] = 6
        
        vulnerability = succession_service.calculate_succession_vulnerability(trading_company_faction)
        assert vulnerability > 0.2  # Should be increased by impulsivity
    
    def test_low_discipline_increases_vulnerability(self, succession_service, trading_company_faction):
        """Test that low discipline increases vulnerability"""
        # Low discipline faction
        trading_company_faction.get_hidden_attributes.return_value["hidden_discipline"] = 1
        
        vulnerability = succession_service.calculate_succession_vulnerability(trading_company_faction)
        assert vulnerability > 0.2  # Should be increased by low discipline


class TestCrisisTriggers:
    """Test succession crisis trigger logic"""
    
    def test_death_triggers_always_cause_crisis(self, succession_service, trading_company_faction):
        """Test that leader death always triggers succession crisis"""
        # Natural death
        should_trigger = succession_service.should_trigger_crisis(
            trading_company_faction, 
            SuccessionTrigger.LEADER_DEATH_NATURAL
        )
        assert should_trigger is True
        
        # Violent death
        should_trigger = succession_service.should_trigger_crisis(
            trading_company_faction, 
            SuccessionTrigger.LEADER_DEATH_VIOLENT
        )
        assert should_trigger is True
    
    @patch('random.random')
    def test_ambition_coup_trigger(self, mock_random, succession_service, military_faction):
        """Test that high ambition increases coup probability"""
        # High ambition should increase coup chance
        military_faction.get_hidden_attributes.return_value["hidden_ambition"] = 6
        
        # Mock random to test coup trigger
        mock_random.return_value = 0.5  # 50% chance
        
        should_trigger = succession_service.should_trigger_crisis(
            military_faction,
            SuccessionTrigger.HIDDEN_AMBITION_COUP
        )
        assert should_trigger is True
    
    @patch('random.random')
    def test_external_pressure_resilience(self, mock_random, succession_service, religious_faction):
        """Test that high resilience resists external pressure"""
        # High resilience should resist external pressure
        religious_faction.get_hidden_attributes.return_value["hidden_resilience"] = 6
        
        # Mock random to test resistance
        mock_random.return_value = 0.5  # 50% chance, but high resilience should resist
        
        should_trigger = succession_service.should_trigger_crisis(
            religious_faction,
            SuccessionTrigger.EXTERNAL_PRESSURE
        )
        assert should_trigger is False


class TestCrisisCreation:
    """Test succession crisis creation"""
    
    def test_create_succession_crisis_success(self, succession_service, mock_db, trading_company_faction):
        """Test successful succession crisis creation"""
        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = trading_company_faction
        
        # Create request
        request = CreateSuccessionCrisisRequest(
            faction_id=trading_company_faction.id,
            trigger=SuccessionTrigger.LEADER_DEATH_NATURAL,
            previous_leader_id=uuid.uuid4(),
            metadata={"test": "data"}
        )
        
        # Create crisis
        crisis = succession_service.create_succession_crisis(mock_db, request)
        
        # Verify crisis creation
        assert isinstance(crisis, SuccessionCrisisEntity)
        assert crisis.faction_id == trading_company_faction.id
        assert crisis.faction_name == trading_company_faction.name
        assert crisis.trigger == SuccessionTrigger.LEADER_DEATH_NATURAL.value
        assert crisis.succession_type == SuccessionType.ECONOMIC_COMPETITION.value
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_create_succession_crisis_faction_not_found(self, succession_service, mock_db):
        """Test succession crisis creation with non-existent faction"""
        # Mock database query to return None
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Create request
        request = CreateSuccessionCrisisRequest(
            faction_id=uuid.uuid4(),
            trigger=SuccessionTrigger.LEADER_DEATH_NATURAL
        )
        
        # Should raise FactionNotFoundError
        with pytest.raises(FactionNotFoundError):
            succession_service.create_succession_crisis(mock_db, request)


class TestCandidateManagement:
    """Test succession candidate management"""
    
    def test_add_succession_candidate(self, succession_service, mock_db):
        """Test adding a succession candidate"""
        # Mock crisis
        crisis = Mock(spec=SuccessionCrisisEntity)
        crisis.id = uuid.uuid4()
        crisis.candidates = []
        crisis.succession_type = SuccessionType.ECONOMIC_COMPETITION.value
        
        mock_db.query.return_value.filter.return_value.first.return_value = crisis
        
        # Create candidate request
        candidate_id = uuid.uuid4()
        request = AddCandidateRequest(
            character_id=candidate_id,
            character_name="Wealthy Merchant",
            net_worth=100000.0,
            qualifications={"business_experience": 15}
        )
        
        # Add candidate
        updated_crisis = succession_service.add_succession_candidate(mock_db, crisis.id, request)
        
        # Verify candidate was added
        assert len(updated_crisis.candidates) == 1
        candidate = updated_crisis.candidates[0]
        assert candidate["character_id"] == str(candidate_id)
        assert candidate["character_name"] == "Wealthy Merchant"
        assert candidate["net_worth"] == 100000.0
        
        # Verify database operations
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


class TestCrisisAdvancement:
    """Test succession crisis advancement over time"""
    
    def test_advance_succession_crisis(self, succession_service, mock_db):
        """Test advancing succession crisis by days"""
        # Mock crisis with candidates
        crisis = Mock(spec=SuccessionCrisisEntity)
        crisis.id = uuid.uuid4()
        crisis.status = SuccessionCrisisStatus.IN_PROGRESS.value
        crisis.faction_stability = 0.8
        crisis.candidates = [
            {
                "character_id": str(uuid.uuid4()),
                "character_name": "Candidate 1",
                "succession_score": 75.0,
                "faction_support": 60.0
            },
            {
                "character_id": str(uuid.uuid4()),
                "character_name": "Candidate 2", 
                "succession_score": 65.0,
                "faction_support": 40.0
            }
        ]
        
        mock_db.query.return_value.filter.return_value.first.return_value = crisis
        
        # Advance crisis
        updated_crisis = succession_service.advance_succession_crisis(mock_db, crisis.id, days=5)
        
        # Verify advancement
        assert updated_crisis is not None
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


class TestCrisisResolution:
    """Test succession crisis resolution"""
    
    def test_resolve_succession_crisis(self, succession_service, mock_db):
        """Test manual succession crisis resolution"""
        # Mock crisis
        crisis = Mock(spec=SuccessionCrisisEntity)
        crisis.id = uuid.uuid4()
        crisis.status = SuccessionCrisisStatus.IN_PROGRESS.value
        
        winner_id = uuid.uuid4()
        crisis.candidates = [
            {
                "character_id": str(winner_id),
                "character_name": "Winner",
                "succession_score": 85.0
            }
        ]
        
        mock_db.query.return_value.filter.return_value.first.return_value = crisis
        
        # Resolve crisis
        resolved_crisis = succession_service.resolve_succession_crisis(
            mock_db, 
            crisis.id, 
            winner_id, 
            "Democratic election victory"
        )
        
        # Verify resolution
        assert resolved_crisis.status == SuccessionCrisisStatus.RESOLVED.value
        assert resolved_crisis.winner_id == winner_id
        assert resolved_crisis.resolution_method == "Democratic election victory"
        assert resolved_crisis.crisis_end is not None
        
        # Verify database operations
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


class TestExternalInterference:
    """Test external faction interference in succession"""
    
    def test_add_external_interference(self, succession_service, mock_db):
        """Test adding external faction interference"""
        # Mock crisis
        crisis = Mock(spec=SuccessionCrisisEntity)
        crisis.id = uuid.uuid4()
        crisis.interfering_factions = []
        crisis.interference_details = {}
        crisis.candidates = [
            {
                "character_id": str(uuid.uuid4()),
                "character_name": "Supported Candidate",
                "faction_support": 50.0
            }
        ]
        
        mock_db.query.return_value.filter.return_value.first.return_value = crisis
        
        interfering_faction_id = uuid.uuid4()
        candidate_id = uuid.UUID(crisis.candidates[0]["character_id"])
        
        # Add interference
        updated_crisis = succession_service.add_external_interference(
            mock_db,
            crisis.id,
            interfering_faction_id,
            "financial_support",
            candidate_id,
            10000.0
        )
        
        # Verify interference was added
        assert interfering_faction_id in updated_crisis.interfering_factions
        assert str(interfering_faction_id) in updated_crisis.interference_details
        
        # Verify database operations
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


class TestSuccessionScoring:
    """Test succession candidate scoring algorithms"""
    
    def test_economic_succession_scoring(self, succession_service):
        """Test scoring for economic competition succession"""
        candidate = SuccessionCandidate(
            character_id=uuid.uuid4(),
            character_name="Rich Merchant",
            net_worth=150000.0,
            faction_support=70.0,
            qualifications={"business_experience": 20}
        )
        
        score = succession_service._calculate_succession_score(
            candidate, 
            SuccessionType.ECONOMIC_COMPETITION
        )
        
        # Economic succession should heavily weight net worth
        assert score > 50.0  # Should be a good score for wealthy candidate
    
    def test_military_succession_scoring(self, succession_service):
        """Test scoring for military succession"""
        candidate = SuccessionCandidate(
            character_id=uuid.uuid4(),
            character_name="General",
            military_rank=5,
            faction_support=80.0,
            hidden_ambition=5,
            qualifications={"military_experience": 15}
        )
        
        score = succession_service._calculate_succession_score(
            candidate,
            SuccessionType.MILITARY_COUP
        )
        
        # Military succession should weight rank and ambition
        assert score > 60.0  # Should be a good score for high-ranking military
    
    def test_religious_succession_scoring(self, succession_service):
        """Test scoring for religious succession"""
        candidate = SuccessionCandidate(
            character_id=uuid.uuid4(),
            character_name="High Priest",
            religious_authority=4,
            faction_support=75.0,
            hidden_integrity=5,
            qualifications={"religious_knowledge": 18}
        )
        
        score = succession_service._calculate_succession_score(
            candidate,
            SuccessionType.RELIGIOUS_ELECTION
        )
        
        # Religious succession should weight authority and integrity
        assert score > 55.0  # Should be a good score for religious leader


class TestStabilityEffects:
    """Test faction stability effects during succession"""
    
    def test_stability_impact_calculation(self, succession_service, trading_company_faction):
        """Test calculation of stability impact from succession trigger"""
        # Test different triggers
        natural_death_impact = succession_service._calculate_stability_impact(
            trading_company_faction, 
            SuccessionTrigger.LEADER_DEATH_NATURAL
        )
        
        violent_death_impact = succession_service._calculate_stability_impact(
            trading_company_faction,
            SuccessionTrigger.LEADER_DEATH_VIOLENT
        )
        
        coup_impact = succession_service._calculate_stability_impact(
            trading_company_faction,
            SuccessionTrigger.HIDDEN_AMBITION_COUP
        )
        
        # Violent events should have more impact than natural ones
        assert violent_death_impact < natural_death_impact
        assert coup_impact < natural_death_impact
        
        # All should reduce stability (< 1.0)
        assert natural_death_impact < 1.0
        assert violent_death_impact < 1.0
        assert coup_impact < 1.0
    
    def test_instability_effects_generation(self, succession_service, trading_company_faction):
        """Test generation of instability effects"""
        effects = succession_service._generate_instability_effects(
            trading_company_faction,
            SuccessionTrigger.LEADER_DEATH_VIOLENT
        )
        
        # Should generate meaningful effects
        assert isinstance(effects, dict)
        assert len(effects) > 0
        
        # Should include relevant effect types
        expected_effects = ["economic_disruption", "military_readiness", "diplomatic_relations"]
        assert any(effect in effects for effect in expected_effects)


class TestIntegrationScenarios:
    """Test complete succession crisis scenarios"""
    
    def test_complete_trading_company_succession(self, succession_service, mock_db, trading_company_faction):
        """Test complete succession scenario for trading company"""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = trading_company_faction
        
        # 1. Create crisis
        request = CreateSuccessionCrisisRequest(
            faction_id=trading_company_faction.id,
            trigger=SuccessionTrigger.LEADER_DEATH_NATURAL
        )
        
        crisis = succession_service.create_succession_crisis(mock_db, request)
        assert crisis.succession_type == SuccessionType.ECONOMIC_COMPETITION.value
        
        # 2. Add candidates
        mock_db.query.return_value.filter.return_value.first.return_value = crisis
        
        candidate1_request = AddCandidateRequest(
            character_id=uuid.uuid4(),
            character_name="Wealthy Merchant",
            net_worth=200000.0
        )
        
        candidate2_request = AddCandidateRequest(
            character_id=uuid.uuid4(),
            character_name="Ambitious Trader",
            net_worth=150000.0
        )
        
        crisis = succession_service.add_succession_candidate(mock_db, crisis.id, candidate1_request)
        crisis = succession_service.add_succession_candidate(mock_db, crisis.id, candidate2_request)
        
        assert len(crisis.candidates) == 2
        
        # 3. Advance crisis
        crisis = succession_service.advance_succession_crisis(mock_db, crisis.id, days=10)
        
        # 4. Resolve crisis
        winner_id = uuid.UUID(crisis.candidates[0]["character_id"])
        resolved_crisis = succession_service.resolve_succession_crisis(
            mock_db,
            crisis.id,
            winner_id,
            "Economic competition victory"
        )
        
        assert resolved_crisis.status == SuccessionCrisisStatus.RESOLVED.value
        assert resolved_crisis.winner_id == winner_id


# Performance and edge case tests
class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_crisis_with_no_candidates(self, succession_service, mock_db):
        """Test crisis advancement with no candidates"""
        crisis = Mock(spec=SuccessionCrisisEntity)
        crisis.id = uuid.uuid4()
        crisis.candidates = []
        crisis.status = SuccessionCrisisStatus.PENDING.value
        
        mock_db.query.return_value.filter.return_value.first.return_value = crisis
        
        # Should handle gracefully
        updated_crisis = succession_service.advance_succession_crisis(mock_db, crisis.id, days=1)
        assert updated_crisis is not None
    
    def test_invalid_winner_resolution(self, succession_service, mock_db):
        """Test resolving crisis with invalid winner"""
        crisis = Mock(spec=SuccessionCrisisEntity)
        crisis.id = uuid.uuid4()
        crisis.candidates = [
            {
                "character_id": str(uuid.uuid4()),
                "character_name": "Valid Candidate"
            }
        ]
        
        mock_db.query.return_value.filter.return_value.first.return_value = crisis
        
        # Try to resolve with non-existent winner
        invalid_winner_id = uuid.uuid4()
        
        # Should handle gracefully or raise appropriate error
        try:
            succession_service.resolve_succession_crisis(
                mock_db,
                crisis.id,
                invalid_winner_id,
                "Invalid resolution"
            )
        except Exception as e:
            # Should be a meaningful error
            assert "candidate" in str(e).lower() or "winner" in str(e).lower()


if __name__ == "__main__":
    pytest.main([__file__]) 