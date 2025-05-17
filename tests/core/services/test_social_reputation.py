import pytest
from datetime import datetime, timedelta
from app import app  # Import the Flask app
from app.social.models.social import Reputation, EntityType
from app.social.social_world import SocialWorld
from app.social.social_utils import get_reputation_between_entities, summarize_reputation_history, gpt_summarize_reputation
from unittest.mock import patch
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def test_multi_entity_reputation():
    with app.app_context():
        Reputation.query.delete()
        db.session.commit()
        world = SocialWorld()
        # Test all entity type combinations
        entity_types = ['individual', 'faction', 'party_group', 'region', 'poi']
        for source_type in entity_types:
            for target_type in entity_types:
                rep = world.set_reputation(10, source_type, 20, target_type, 15, context=f'{source_type}_to_{target_type}', change_source='unit_test')
                assert rep.value == 15
                assert rep.context == f'{source_type}_to_{target_type}'
                assert rep.change_source == 'unit_test'
                assert rep.strength == 1
                # Update reputation
                rep2 = world.update_reputation(10, source_type, 20, target_type, 5, context='update', change_source='unit_test')
                assert rep2.value == 20
                assert rep2.strength > 1
                # Fetch reputation
                fetched = world.get_reputation(10, source_type, 20, target_type)
                assert fetched is not None
                assert fetched.value == 20
                # Test last_updated is recent
                assert (datetime.utcnow() - fetched.last_updated) < timedelta(minutes=1)
        # Test bidirectional/asymmetric
        rep_a = world.set_reputation(1, 'individual', 2, 'faction', 30)
        rep_b = world.set_reputation(2, 'faction', 1, 'individual', 40)
        assert rep_a.value == 30
        assert rep_b.value == 40
        assert rep_a.source_entity_id == 1 and rep_a.target_entity_id == 2
        assert rep_b.source_entity_id == 2 and rep_b.target_entity_id == 1
        # Test edge case: update with negative delta
        rep_neg = world.update_reputation(1, 'individual', 2, 'faction', -10)
        assert rep_neg.value == 20
        # Summarize
        summary = summarize_reputation_history(1, 'individual', 2, 'individual')
        assert 'Reputation value' in summary or summary == 'No reputation history.'
        # Test last_updated is recent
        assert (datetime.utcnow() - fetched.last_updated) < timedelta(minutes=1)

        # Set reputation between two individuals
        rep = world.set_reputation(1, 'individual', 2, 'individual', 42, context='test', change_source='unit_test')
        assert rep.value == 42
        assert rep.context == 'test'
        assert rep.change_source == 'unit_test'
        assert rep.strength == 1
        # Update reputation
        rep2 = world.set_reputation(1, 'individual', 2, 'individual', 50, context='test2', change_source='unit_test')
        assert rep2.value == 50
        assert rep2.context == 'test2'
        assert rep2.last_updated >= rep.last_updated
        # Fetch reputation
        fetched = get_reputation_between_entities(1, 'individual', 2, 'individual')
        assert fetched.value == 50
        # Summarize history (stub)
        summary = summarize_reputation_history(1, 'individual', 2, 'individual')
        assert 'Reputation value' in summary or summary == 'No reputation history.'
        # When checking for dict summary:
        summary_dict = summarize_reputation_history(1, 'individual', 2, 'individual', as_dict=True)
        assert isinstance(summary_dict, dict)

def test_gpt_summarize_reputation_strength_axis():
    with app.app_context():
        world = SocialWorld()
        # Low strength
        rep = world.set_reputation(100, 'individual', 200, 'faction', 10, context='low strength', change_source='unit_test')
        rep.strength = 10
        rep.value = -5
        rep.rank = 'hated'
        rep.last_updated = datetime.utcnow()
        rep.change_source = 'unit_test'
        rep.context = 'low strength context'
        rep.save()
        # Medium strength
        rep2 = world.set_reputation(101, 'faction', 201, 'individual', 30, context='medium strength', change_source='unit_test')
        rep2.strength = 40
        rep2.value = 20
        rep2.rank = 'neutral'
        rep2.last_updated = datetime.utcnow()
        rep2.change_source = 'unit_test'
        rep2.context = 'medium strength context'
        rep2.save()
        # High strength
        rep3 = world.set_reputation(102, 'party_group', 202, 'region', 80, context='high strength', change_source='unit_test')
        rep3.strength = 80
        rep3.value = 50
        rep3.rank = 'exalted'
        rep3.last_updated = datetime.utcnow()
        rep3.change_source = 'unit_test'
        rep3.context = 'high strength context'
        rep3.save()
        with patch('app.social.social_utils.GPTClient.call') as mock_call:
            mock_call.side_effect = [
                'The target is rumored to be hated by many, but details are uncertain.',
                'The target is known to be neutral, with a moderate reputation.',
                'The target is renowned for their exalted deeds, reputation is well established.'
            ]
            summary_low = gpt_summarize_reputation(100, 'individual', 200, 'faction')
            summary_med = gpt_summarize_reputation(101, 'faction', 201, 'individual')
            summary_high = gpt_summarize_reputation(102, 'party_group', 202, 'region')
            assert 'rumored to be' in summary_low
            assert 'known to be' in summary_med
            assert 'renowned for' in summary_high 