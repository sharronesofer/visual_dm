"""
Integration tests for Alliance System with existing Faction systems
Tests complete workflow from faction attributes to alliance formation and betrayal
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from typing import Dict, List, Optional, Any

from backend.systems.faction.services.alliance_service import AllianceService
from backend.infrastructure.repositories.faction.alliance_repository import AllianceRepository
from backend.infrastructure.repositories.faction.faction_repository import FactionRepository, FactionRelationshipRepository
from backend.systems.faction.models.alliance import (
    AllianceEntity, BetrayalEntity, CreateAllianceRequest,
    AllianceType, AllianceStatus, BetrayalReason
)


class TestAllianceSystemIntegration:
    """Integration tests for the complete alliance system"""

    @pytest.fixture
    def mock_repositories(self):
        """Create mock repositories for integration testing"""
        return {
            'alliance_repo': Mock(spec=AllianceRepository),
            'faction_repo': Mock(spec=FactionRepository),
            'relationship_repo': Mock(spec=FactionRelationshipRepository)
        }

    @pytest.fixture
    def alliance_service(self, mock_repositories):
        """Create AllianceService with all dependencies"""
        service = AllianceService()
        service.alliance_repository = mock_repositories['alliance_repo']
        service.faction_repository = mock_repositories['faction_repo']
        service.relationship_repository = mock_repositories['relationship_repo']
        return service

    @pytest.fixture
    def sample_factions(self):
        """Sample factions with different characteristics for testing"""
        return {
            'honorable_militarists': {
                'id': uuid4(),
                'name': 'Steel Legion',
                'faction_type': 'military',
                'hidden_attributes': {
                    'hidden_pragmatism': 7,
                    'hidden_integrity': 9,
                    'hidden_ambition': 6,
                    'hidden_impulsivity': 3
                },
                'visible_attributes': {
                    'military_strength': 8,
                    'economic_power': 5,
                    'diplomatic_influence': 6
                },
                'resources': {
                    'military_units': 1000,
                    'credits': 50000,
                    'technology_level': 7
                }
            },
            'ambitious_traders': {
                'id': uuid4(),
                'name': 'Merchant Consortium',
                'faction_type': 'economic',
                'hidden_attributes': {
                    'hidden_pragmatism': 8,
                    'hidden_integrity': 4,
                    'hidden_ambition': 9,
                    'hidden_impulsivity': 5
                },
                'visible_attributes': {
                    'military_strength': 4,
                    'economic_power': 9,
                    'diplomatic_influence': 7
                },
                'resources': {
                    'military_units': 300,
                    'credits': 200000,
                    'technology_level': 8
                }
            },
            'unpredictable_raiders': {
                'id': uuid4(),
                'name': 'Crimson Reapers',
                'faction_type': 'aggressive',
                'hidden_attributes': {
                    'hidden_pragmatism': 3,
                    'hidden_integrity': 2,
                    'hidden_ambition': 8,
                    'hidden_impulsivity': 9
                },
                'visible_attributes': {
                    'military_strength': 7,
                    'economic_power': 3,
                    'diplomatic_influence': 2
                },
                'resources': {
                    'military_units': 800,
                    'credits': 20000,
                    'technology_level': 5
                }
            },
            'powerful_empire': {
                'id': uuid4(),
                'name': 'Galactic Imperium',
                'faction_type': 'empire',
                'hidden_attributes': {
                    'hidden_pragmatism': 6,
                    'hidden_integrity': 5,
                    'hidden_ambition': 9,
                    'hidden_impulsivity': 4
                },
                'visible_attributes': {
                    'military_strength': 10,
                    'economic_power': 9,
                    'diplomatic_influence': 8
                },
                'resources': {
                    'military_units': 5000,
                    'credits': 1000000,
                    'technology_level': 10
                }
            }
        }

    @pytest.fixture
    def sample_relationships(self, sample_factions):
        """Sample faction relationships for testing"""
        factions = sample_factions
        return [
            {
                'faction_a_id': factions['honorable_militarists']['id'],
                'faction_b_id': factions['ambitious_traders']['id'],
                'relationship_type': 'neutral',
                'tension_level': 0.3,
                'trust_level': 0.5,
                'interaction_history': []
            },
            {
                'faction_a_id': factions['honorable_militarists']['id'],
                'faction_b_id': factions['powerful_empire']['id'],
                'relationship_type': 'hostile',
                'tension_level': 0.9,
                'trust_level': 0.1,
                'interaction_history': [
                    {'type': 'conflict', 'intensity': 'high', 'date': datetime.utcnow() - timedelta(days=30)}
                ]
            },
            {
                'faction_a_id': factions['ambitious_traders']['id'],
                'faction_b_id': factions['powerful_empire']['id'],
                'relationship_type': 'hostile',
                'tension_level': 0.8,
                'trust_level': 0.2,
                'interaction_history': [
                    {'type': 'trade_dispute', 'intensity': 'medium', 'date': datetime.utcnow() - timedelta(days=15)}
                ]
            }
        ]

    # Complete Alliance Formation Workflow Tests

    def test_alliance_formation_against_common_threat(
        self, alliance_service, mock_repositories, sample_factions, sample_relationships
    ):
        """Test complete alliance formation workflow against common threat"""
        # Setup faction data
        militarists = sample_factions['honorable_militarists']
        traders = sample_factions['ambitious_traders']
        empire = sample_factions['powerful_empire']  # Common threat

        # Mock faction repository responses
        def mock_get_faction(faction_id):
            for faction in sample_factions.values():
                if faction['id'] == faction_id:
                    return Mock(
                        id=faction['id'],
                        name=faction['name'],
                        faction_type=faction['faction_type'],
                        hidden_attributes=faction['hidden_attributes'],
                        visible_attributes=faction['visible_attributes'],
                        resources=faction['resources']
                    )
            return None

        mock_repositories['faction_repo'].get_faction_by_id.side_effect = mock_get_faction

        # Mock relationship tensions (high tension with empire)
        def mock_get_tension(faction_a_id, faction_b_id):
            if faction_b_id == empire['id']:
                return 0.9  # High tension with empire
            return 0.3  # Lower tension otherwise

        mock_repositories['relationship_repo'].get_relationship_tension.side_effect = mock_get_tension

        # Test alliance evaluation
        result = alliance_service.evaluate_alliance_opportunity(
            faction_a_id=militarists['id'],
            faction_b_id=traders['id'],
            common_threat_ids=[empire['id']],
            alliance_type=AllianceType.MILITARY
        )

        # Verify alliance opportunity evaluation
        assert result['compatible'] is True  # Should be compatible against common threat
        assert result['threat_level'] > 0.8  # High threat from empire
        assert result['willingness_score'] > 0.6  # High willingness due to threat
        assert AllianceType.MILITARY in result['recommended_alliance_types']

    def test_alliance_formation_with_attribute_conflicts(
        self, alliance_service, mock_repositories, sample_factions
    ):
        """Test alliance formation between factions with conflicting attributes"""
        # Setup faction data - high integrity vs low integrity
        militarists = sample_factions['honorable_militarists']  # High integrity
        raiders = sample_factions['unpredictable_raiders']      # Low integrity, high impulsivity

        def mock_get_faction(faction_id):
            for faction in sample_factions.values():
                if faction['id'] == faction_id:
                    return Mock(
                        hidden_attributes=faction['hidden_attributes']
                    )
            return None

        mock_repositories['faction_repo'].get_faction_by_id.side_effect = mock_get_faction

        # Test alliance evaluation
        result = alliance_service.evaluate_alliance_opportunity(
            faction_a_id=militarists['id'],
            faction_b_id=raiders['id'],
            common_threat_ids=[]
        )

        # Verify incompatibility detection
        assert result['compatible'] is False
        assert result['compatibility_score'] < 0.4
        assert len(result['risks']) > 0
        assert any('integrity' in risk.lower() or 'impulsiv' in risk.lower() for risk in result['risks'])

    def test_economic_alliance_formation(
        self, alliance_service, mock_repositories, sample_factions
    ):
        """Test economic alliance formation between compatible economic factions"""
        # Setup faction data
        militarists = sample_factions['honorable_militarists']
        traders = sample_factions['ambitious_traders']

        def mock_get_faction(faction_id):
            for faction in sample_factions.values():
                if faction['id'] == faction_id:
                    return Mock(
                        hidden_attributes=faction['hidden_attributes']
                    )
            return None

        mock_repositories['faction_repo'].get_faction_by_id.side_effect = mock_get_faction

        # Test economic alliance evaluation (low threat level)
        result = alliance_service.evaluate_alliance_opportunity(
            faction_a_id=militarists['id'],
            faction_b_id=traders['id'],
            common_threat_ids=[],
            alliance_type=AllianceType.ECONOMIC
        )

        # Should recommend economic alliance in low-threat scenarios
        assert AllianceType.ECONOMIC in result['recommended_alliance_types'] or \
               AllianceType.TEMPORARY_TRUCE in result['recommended_alliance_types']

    # Alliance Creation and Management Tests

    def test_alliance_creation_with_initialization(
        self, alliance_service, mock_repositories, sample_factions
    ):
        """Test alliance creation with proper initialization"""
        militarists = sample_factions['honorable_militarists']
        traders = sample_factions['ambitious_traders']

        # Create alliance request
        request = CreateAllianceRequest(
            name="Defense Coalition",
            alliance_type=AllianceType.MILITARY,
            description="Joint defense against common threats",
            leader_faction_id=militarists['id'],
            member_faction_ids=[traders['id']],
            terms={'mutual_defense': True, 'resource_sharing': False},
            mutual_obligations=['Provide military support when attacked'],
            shared_enemies=[sample_factions['powerful_empire']['id']],
            shared_goals=['Defeat the Galactic Imperium']
        )

        # Mock alliance creation
        created_alliance = AllianceEntity(
            id=uuid4(),
            name=request.name,
            alliance_type=request.alliance_type.value,
            leader_faction_id=request.leader_faction_id,
            member_faction_ids=request.member_faction_ids,
            terms=request.terms,
            mutual_obligations=request.mutual_obligations,
            shared_enemies=request.shared_enemies,
            shared_goals=request.shared_goals,
            status=AllianceStatus.ACTIVE.value
        )
        mock_repositories['alliance_repo'].create_alliance.return_value = created_alliance

        # Test alliance creation
        result = alliance_service.create_alliance(request)

        # Verify alliance was created properly
        assert result.name == request.name
        assert result.alliance_type == request.alliance_type.value
        assert result.leader_faction_id == request.leader_faction_id
        assert result.member_faction_ids == request.member_faction_ids
        mock_repositories['alliance_repo'].create_alliance.assert_called_once()

    # Betrayal System Integration Tests

    def test_betrayal_probability_with_faction_attributes(
        self, alliance_service, mock_repositories, sample_factions
    ):
        """Test betrayal probability calculation using faction hidden attributes"""
        alliance_id = uuid4()
        traders = sample_factions['ambitious_traders']  # High ambition, low integrity

        # Mock alliance
        mock_alliance = Mock(
            id=alliance_id,
            member_faction_ids=[traders['id']],
            trust_levels={str(traders['id']): 0.6},
            status='active'
        )
        mock_repositories['alliance_repo'].get_alliance_by_id.return_value = mock_alliance

        # Mock faction with betrayal-prone attributes
        mock_repositories['faction_repo'].get_faction_by_id.return_value = Mock(
            hidden_attributes=traders['hidden_attributes']
        )

        # Test betrayal evaluation with external pressure
        external_factors = {
            'opportunity_present': True,
            'external_pressure': 0.7,
            'resource_scarcity': True,
            'ally_power_growing': False
        }

        result = alliance_service.evaluate_betrayal_probability(
            alliance_id=alliance_id,
            faction_id=traders['id'],
            external_factors=external_factors
        )

        # High ambition + low integrity + external factors = high betrayal risk
        assert result['betrayal_probability'] > 0.5
        assert result['primary_motivation'] in [
            BetrayalReason.AMBITION, BetrayalReason.OPPORTUNITY, BetrayalReason.PRESSURE
        ]
        assert len(result['risk_factors']) > 0

    def test_betrayal_execution_impact_on_relationships(
        self, alliance_service, mock_repositories, sample_factions
    ):
        """Test betrayal execution and its impact on faction relationships"""
        alliance_id = uuid4()
        traders = sample_factions['ambitious_traders']
        militarists = sample_factions['honorable_militarists']

        # Mock alliance with multiple members
        mock_alliance = Mock(
            id=alliance_id,
            member_faction_ids=[traders['id'], militarists['id']],
            status='active'
        )
        mock_repositories['alliance_repo'].get_alliance_by_id.return_value = mock_alliance

        # Mock faction attributes for betrayer
        mock_repositories['faction_repo'].get_faction_by_id.return_value = Mock(
            hidden_attributes=traders['hidden_attributes']
        )

        # Mock betrayal creation
        betrayal_entity = BetrayalEntity(
            id=uuid4(),
            alliance_id=alliance_id,
            betrayer_faction_id=traders['id'],
            victim_faction_ids=[militarists['id']],
            betrayal_reason=BetrayalReason.AMBITION.value,
            betrayal_type='economic_sabotage',
            description='Sabotaged ally supply lines for personal gain'
        )
        mock_repositories['alliance_repo'].create_betrayal.return_value = betrayal_entity

        # Test betrayal execution
        result = alliance_service.execute_betrayal(
            alliance_id=alliance_id,
            betrayer_faction_id=traders['id'],
            betrayal_type='economic_sabotage',
            description='Sabotaged ally supply lines for personal gain',
            reason=BetrayalReason.AMBITION
        )

        # Verify betrayal execution and relationship impacts
        assert result.betrayer_faction_id == traders['id']
        assert result.alliance_id == alliance_id
        
        # Verify alliance status was updated to betrayed
        mock_repositories['alliance_repo'].update_alliance_status.assert_called_with(
            alliance_id, AllianceStatus.BETRAYED
        )

    def test_reliable_faction_betrayal_resistance(
        self, alliance_service, mock_repositories, sample_factions
    ):
        """Test that reliable factions are resistant to betrayal"""
        alliance_id = uuid4()
        militarists = sample_factions['honorable_militarists']  # High integrity, low impulsivity

        # Mock alliance
        mock_alliance = Mock(
            id=alliance_id,
            member_faction_ids=[militarists['id']],
            trust_levels={str(militarists['id']): 0.8},
            status='active'
        )
        mock_repositories['alliance_repo'].get_alliance_by_id.return_value = mock_alliance

        # Mock reliable faction
        mock_repositories['faction_repo'].get_faction_by_id.return_value = Mock(
            hidden_attributes=militarists['hidden_attributes']
        )

        # Test betrayal evaluation even with external pressure
        external_factors = {
            'opportunity_present': True,
            'external_pressure': 0.8,
            'resource_scarcity': True
        }

        result = alliance_service.evaluate_betrayal_probability(
            alliance_id=alliance_id,
            faction_id=militarists['id'],
            external_factors=external_factors
        )

        # High integrity should resist betrayal despite external factors
        assert result['betrayal_probability'] < 0.4
        assert len(result['protective_factors']) > 0
        assert any('integrity' in factor.lower() for factor in result['protective_factors'])

    # Complex Scenario Integration Tests

    def test_multi_faction_alliance_with_varied_betrayal_risks(
        self, alliance_service, mock_repositories, sample_factions
    ):
        """Test complex scenario with multiple factions having different betrayal risks"""
        alliance_id = uuid4()
        militarists = sample_factions['honorable_militarists']    # Low betrayal risk
        traders = sample_factions['ambitious_traders']           # High betrayal risk
        raiders = sample_factions['unpredictable_raiders']       # Very high betrayal risk

        # Mock alliance with multiple members
        mock_alliance = Mock(
            id=alliance_id,
            member_faction_ids=[militarists['id'], traders['id'], raiders['id']],
            trust_levels={
                str(militarists['id']): 0.8,
                str(traders['id']): 0.6,
                str(raiders['id']): 0.4
            },
            status='active'
        )
        mock_repositories['alliance_repo'].get_alliance_by_id.return_value = mock_alliance

        # Test betrayal probability for each faction
        faction_risks = {}
        for faction_name, faction_data in [
            ('militarists', militarists),
            ('traders', traders),
            ('raiders', raiders)
        ]:
            mock_repositories['faction_repo'].get_faction_by_id.return_value = Mock(
                hidden_attributes=faction_data['hidden_attributes']
            )

            result = alliance_service.evaluate_betrayal_probability(
                alliance_id=alliance_id,
                faction_id=faction_data['id']
            )
            faction_risks[faction_name] = result['betrayal_probability']

        # Verify risk hierarchy
        assert faction_risks['raiders'] > faction_risks['traders'] > faction_risks['militarists']
        assert faction_risks['militarists'] < 0.3  # Very low risk
        assert faction_risks['raiders'] > 0.7      # Very high risk

    def test_alliance_dissolution_cascade_effects(
        self, alliance_service, mock_repositories, sample_factions
    ):
        """Test cascade effects when alliance dissolves due to betrayal"""
        alliance_id = uuid4()
        traders = sample_factions['ambitious_traders']
        militarists = sample_factions['honorable_militarists']

        # Mock alliance
        mock_alliance = Mock(
            id=alliance_id,
            member_faction_ids=[traders['id'], militarists['id']],
            status='active'
        )
        mock_repositories['alliance_repo'].get_alliance_by_id.return_value = mock_alliance

        # Mock faction attributes
        mock_repositories['faction_repo'].get_faction_by_id.return_value = Mock(
            hidden_attributes=traders['hidden_attributes']
        )

        # Mock betrayal creation
        betrayal_entity = BetrayalEntity(
            id=uuid4(),
            alliance_id=alliance_id,
            betrayer_faction_id=traders['id'],
            victim_faction_ids=[militarists['id']],
            betrayal_reason=BetrayalReason.AMBITION.value,
            betrayal_type='military_attack',
            description='Surprise attack on ally forces'
        )
        mock_repositories['alliance_repo'].create_betrayal.return_value = betrayal_entity

        # Execute betrayal
        result = alliance_service.execute_betrayal(
            alliance_id=alliance_id,
            betrayer_faction_id=traders['id'],
            betrayal_type='military_attack',
            description='Surprise attack on ally forces',
            reason=BetrayalReason.AMBITION
        )

        # Verify cascade effects
        # 1. Alliance status changed to betrayed
        mock_repositories['alliance_repo'].update_alliance_status.assert_called_with(
            alliance_id, AllianceStatus.BETRAYED
        )
        
        # 2. Betrayal record created
        assert result.betrayer_faction_id == traders['id']
        assert BetrayalReason.AMBITION.value in result.betrayal_reason

    def test_temporary_truce_formation_under_extreme_threat(
        self, alliance_service, mock_repositories, sample_factions
    ):
        """Test temporary truce formation between normally hostile factions under extreme threat"""
        # Setup normally incompatible factions
        militarists = sample_factions['honorable_militarists']
        raiders = sample_factions['unpredictable_raiders']
        empire = sample_factions['powerful_empire']  # Overwhelming threat

        def mock_get_faction(faction_id):
            for faction in sample_factions.values():
                if faction['id'] == faction_id:
                    return Mock(
                        hidden_attributes=faction['hidden_attributes']
                    )
            return None

        mock_repositories['faction_repo'].get_faction_by_id.side_effect = mock_get_faction

        # Mock extremely high threat level from empire
        def mock_get_tension(faction_a_id, faction_b_id):
            if faction_b_id == empire['id']:
                return 0.95  # Extreme threat
            return 0.6  # Moderate tension between militarists and raiders

        mock_repositories['relationship_repo'].get_relationship_tension.side_effect = mock_get_tension

        # Test alliance evaluation under extreme threat
        result = alliance_service.evaluate_alliance_opportunity(
            faction_a_id=militarists['id'],
            faction_b_id=raiders['id'],
            common_threat_ids=[empire['id']]
        )

        # Extreme threat should overcome normal incompatibility
        assert result['threat_level'] > 0.9
        assert result['compatible'] is True  # Threat overrides normal incompatibility
        assert AllianceType.TEMPORARY_TRUCE in result['recommended_alliance_types']

    # Performance and Stress Tests

    def test_large_scale_alliance_evaluation(
        self, alliance_service, mock_repositories, sample_factions
    ):
        """Test performance with large number of alliance evaluations"""
        # Simulate evaluating alliances for all faction pairs
        faction_ids = [faction['id'] for faction in sample_factions.values()]
        faction_pairs = [(a, b) for a in faction_ids for b in faction_ids if a != b]

        # Mock faction repository
        def mock_get_faction(faction_id):
            for faction in sample_factions.values():
                if faction['id'] == faction_id:
                    return Mock(
                        hidden_attributes=faction['hidden_attributes']
                    )
            return None

        mock_repositories['faction_repo'].get_faction_by_id.side_effect = mock_get_faction

        # Test performance with multiple evaluations
        results = []
        for faction_a_id, faction_b_id in faction_pairs[:6]:  # Limit to reasonable number for testing
            result = alliance_service.evaluate_alliance_opportunity(
                faction_a_id, faction_b_id
            )
            results.append(result)

        # Verify all evaluations completed
        assert len(results) == 6
        assert all('compatibility_score' in result for result in results)

    def test_concurrent_betrayal_evaluations(
        self, alliance_service, mock_repositories, sample_factions
    ):
        """Test concurrent betrayal evaluations for multiple factions"""
        alliance_id = uuid4()
        faction_ids = [faction['id'] for faction in sample_factions.values()]

        # Mock alliance with all factions
        mock_alliance = Mock(
            id=alliance_id,
            member_faction_ids=faction_ids,
            trust_levels={str(fid): 0.5 for fid in faction_ids},
            status='active'
        )
        mock_repositories['alliance_repo'].get_alliance_by_id.return_value = mock_alliance

        # Test betrayal evaluation for all members
        betrayal_results = []
        for faction_data in sample_factions.values():
            mock_repositories['faction_repo'].get_faction_by_id.return_value = Mock(
                hidden_attributes=faction_data['hidden_attributes']
            )

            result = alliance_service.evaluate_betrayal_probability(
                alliance_id=alliance_id,
                faction_id=faction_data['id']
            )
            betrayal_results.append(result)

        # Verify all evaluations completed
        assert len(betrayal_results) == len(sample_factions)
        assert all('betrayal_probability' in result for result in betrayal_results)

    # Edge Cases and Error Handling

    def test_alliance_evaluation_with_missing_faction_data(
        self, alliance_service, mock_repositories
    ):
        """Test graceful handling of missing faction data"""
        faction_a_id = uuid4()
        faction_b_id = uuid4()

        # Mock missing faction
        mock_repositories['faction_repo'].get_faction_by_id.return_value = None

        # Should raise appropriate error
        with pytest.raises(ValueError, match="not found"):
            alliance_service.evaluate_alliance_opportunity(faction_a_id, faction_b_id)

    def test_betrayal_evaluation_with_invalid_alliance(
        self, alliance_service, mock_repositories
    ):
        """Test betrayal evaluation with non-existent alliance"""
        alliance_id = uuid4()
        faction_id = uuid4()

        # Mock missing alliance
        mock_repositories['alliance_repo'].get_alliance_by_id.return_value = None

        # Should raise appropriate error
        with pytest.raises(ValueError, match="Alliance .* not found"):
            alliance_service.evaluate_betrayal_probability(alliance_id, faction_id)

    def test_alliance_with_incomplete_hidden_attributes(
        self, alliance_service, mock_repositories
    ):
        """Test alliance evaluation with incomplete hidden attributes"""
        faction_a_id = uuid4()
        faction_b_id = uuid4()

        # Mock faction with incomplete attributes
        incomplete_attrs = {
            'hidden_pragmatism': 5,
            'hidden_integrity': 6
            # Missing hidden_ambition and hidden_impulsivity
        }

        mock_repositories['faction_repo'].get_faction_by_id.return_value = Mock(
            hidden_attributes=incomplete_attrs
        )

        # Should handle gracefully with defaults
        result = alliance_service.evaluate_alliance_opportunity(faction_a_id, faction_b_id)
        
        # Should still return valid result with default values
        assert 'compatibility_score' in result
        assert 'willingness_score' in result 