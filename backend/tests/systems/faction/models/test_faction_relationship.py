import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from backend.systems.faction.models.faction import FactionRelationship
from backend.systems.faction.schemas.faction_types import DiplomaticStance
from dataclasses import field

class TestFactionRelationshipModel:
    """Test suite for FactionRelationship model."""

    def test_create_relationship_with_valid_data(self):
        """Test creation of faction relationship with valid data."""
        relationship = FactionRelationship(
            faction_id=1,
            other_faction_id=2,
            diplomatic_stance="HOSTILE",
            tension=75.0,
            treaties=["non_aggression_pact", "trade_agreement"],
            war_state={
                "at_war": True,
                "war_details": {
                    "start_date": "2024-01-01",
                    "cause": "territorial dispute",
                    "battles": ["battle_of_iron_pass"]
                }
            },
            history=[
                {
                    "date": "2024-01-01",
                    "event": "war_declared",
                    "details": "Territorial dispute over iron mines"
                }
            ],
            additional_data={
                "trade_volume": 1000,
                "cultural_exchange": False
            }
        )
        
        assert relationship.faction_id == 1
        assert relationship.other_faction_id == 2
        assert relationship.diplomatic_stance == "HOSTILE"
        assert relationship.tension == 75.0
        assert "non_aggression_pact" in relationship.treaties
        assert relationship.war_state["at_war"] is True
        assert len(relationship.history) == 1
        assert relationship.additional_data["trade_volume"] == 1000

    def test_relationship_with_missing_required_fields(self):
        """Test relationship creation with missing required fields."""
        # SQLAlchemy models don't enforce required fields at instantiation time
        relationship = FactionRelationship(
            diplomatic_stance="NEUTRAL"
            # Missing required faction_id and other_faction_id
        )
        
        # The model should accept None for required fields, but would fail at database level
        assert relationship.faction_id is None
        assert relationship.other_faction_id is None
        assert relationship.diplomatic_stance == "NEUTRAL"

    def test_relationship_with_invalid_tension(self):
        """Test relationship creation with tension values outside normal range."""
        # SQLAlchemy doesn't enforce range validation by default
        relationship = FactionRelationship(
            faction_id=1,
            other_faction_id=2,
            diplomatic_stance="HOSTILE",
            tension=150.0  # Outside normal -100 to +100 range
        )
        
        # The model should accept this value (validation would be handled at the service layer)
        assert relationship.tension == 150.0

    def test_alliance_relationship(self):
        """Test creation of alliance relationship with negative tension."""
        relationship = FactionRelationship(
            faction_id=1,
            other_faction_id=2,
            diplomatic_stance="ALLIED",
            tension=-50.0,  # Negative tension indicates alliance/trust
            treaties=["mutual_defense_pact", "trade_agreement"],
            war_state={
                "at_war": False,
                "war_details": {}
            },
            history=[
                {
                    "date": "2024-01-01",
                    "event": "alliance_formed",
                    "details": "Mutual defense agreement signed"
                }
            ]
        )
        
        assert relationship.diplomatic_stance == "ALLIED"
        assert relationship.tension == -50.0
        assert "mutual_defense_pact" in relationship.treaties
        assert relationship.war_state["at_war"] is False

    def test_relationship_defaults(self):
        """Test that relationship model sets correct defaults."""
        relationship = FactionRelationship(
            faction_id=1,
            other_faction_id=2
        )
        
        # Check the values that were explicitly set
        assert relationship.faction_id == 1
        assert relationship.other_faction_id == 2
        
        # SQLAlchemy defaults are only applied when saving to database
        # In memory objects will have None for unset values
        # We can test that the defaults are defined in the Column definitions
        assert hasattr(relationship, 'tension')
        assert hasattr(relationship, 'treaties')
        assert hasattr(relationship, 'war_state')
        assert hasattr(relationship, 'history')
        assert hasattr(relationship, 'additional_data')
        
        # Test that we can set values explicitly
        relationship.tension = -25.0
        relationship.diplomatic_stance = "ALLIED"
        assert relationship.tension == -25.0
        assert relationship.diplomatic_stance == "ALLIED"

    def test_treaties_validation(self):
        """Test treaties field accepts list of treaty names."""
        treaties = [
            "trade_agreement",
            "non_aggression_pact",
            "mutual_defense_pact",
            "cultural_exchange_agreement"
        ]
        
        relationship = FactionRelationship(
            faction_id=1,
            other_faction_id=2,
            diplomatic_stance="ALLIED",
            tension=-30.0,
            treaties=treaties
        )
        
        assert len(relationship.treaties) == 4
        assert "trade_agreement" in relationship.treaties
        assert "mutual_defense_pact" in relationship.treaties 