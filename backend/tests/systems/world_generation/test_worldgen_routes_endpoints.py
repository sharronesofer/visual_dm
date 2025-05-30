"""
Tests for worldgen_routes Flask endpoints.

Tests the actual Flask route functions to achieve high coverage.
"""

import json
import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime
from uuid import uuid4

# Import Flask for testing
from flask import Flask

# Mock Firebase and other dependencies
import sys
from unittest.mock import MagicMock

# Mock the problematic modules before import
sys.modules['openai'] = MagicMock()
sys.modules['firebase_admin'] = MagicMock()
sys.modules['firebase_admin.db'] = MagicMock()

# Import the module after mocking
from backend.systems.world_generation.worldgen_routes import worldgen_bp


class TestWorldgenRoutesEndpoints: pass
    """Test suite for worldgen routes Flask endpoints."""

    @pytest.fixture
    def app(self): pass
        """Create Flask app for testing."""
        app = Flask(__name__)
        app.register_blueprint(worldgen_bp)
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app): pass
        """Create test client."""
        with app.test_client() as client: pass
            with app.app_context(): pass
                yield client

    @patch('backend.systems.world_generation.worldgen_routes.db')
    @patch('backend.systems.world_generation.worldgen_routes.random')
    @patch('backend.systems.world_generation.worldgen_routes.datetime')
    def test_refresh_pois_empty_locations(self, mock_datetime, mock_random, mock_db, client): pass
        """Test refresh_pois endpoint with empty locations."""
        # Mock empty locations
        mock_db.reference.return_value.get.return_value = {}
        mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T00:00:00"
        
        response = client.post('/refresh_pois')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0

    @patch('backend.systems.world_generation.worldgen_routes.db')
    @patch('backend.systems.world_generation.worldgen_routes.random')
    @patch('backend.systems.world_generation.worldgen_routes.datetime')
    def test_refresh_pois_with_locations_no_poi(self, mock_datetime, mock_random, mock_db, client): pass
        """Test refresh_pois endpoint with locations but no POIs."""
        # Mock locations without POIs
        mock_db.reference.return_value.get.return_value = {
            "10_20": {"danger_level": 5},
            "30_40": {"danger_level": 3}
        }
        mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T00:00:00"
        
        response = client.post('/refresh_pois')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0

    @patch('backend.systems.world_generation.worldgen_routes.db')
    @patch('backend.systems.world_generation.worldgen_routes.random')
    @patch('backend.systems.world_generation.worldgen_routes.datetime')
    def test_refresh_pois_with_hostile_poi(self, mock_datetime, mock_random, mock_db, client): pass
        """Test refresh_pois endpoint with already hostile POI."""
        # Mock locations with hostile POI
        mock_db.reference.return_value.get.side_effect = [
            {"10_20": {"danger_level": 5, "POI": "temple1", "region": "region1"}},
            {"control_status": "hostile"}
        ]
        mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T00:00:00"
        
        response = client.post('/refresh_pois')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0

    @patch('backend.systems.world_generation.worldgen_routes.db')
    @patch('backend.systems.world_generation.worldgen_routes.random')
    @patch('backend.systems.world_generation.worldgen_routes.datetime')
    def test_refresh_pois_monster_attack_success(self, mock_datetime, mock_random, mock_db, client): pass
        """Test refresh_pois endpoint with successful monster attack."""
        # Mock locations with POI that gets attacked
        mock_db.reference.return_value.get.side_effect = [
            {"10_20": {"danger_level": 8, "POI": "temple1", "region": "region1"}},
            {"control_status": "neutral", "faction_influence": {}}
        ]
        mock_random.random.return_value = 0.5  # 50% roll, attack succeeds (8 * 0.1 = 0.8 > 0.5)
        mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T00:00:00"
        
        # Mock the set operations
        mock_set = MagicMock()
        mock_push = MagicMock()
        mock_db.reference.return_value.set = mock_set
        mock_db.reference.return_value.push = mock_push
        
        response = client.post('/refresh_pois')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["region"] == "region1"
        assert data[0]["poi"] == "temple1"
        assert data[0]["coord"] == "10_20"

    @patch('backend.systems.world_generation.worldgen_routes.db')
    @patch('backend.systems.world_generation.worldgen_routes.random')
    @patch('backend.systems.world_generation.worldgen_routes.datetime')
    def test_refresh_pois_defense_success(self, mock_datetime, mock_random, mock_db, client): pass
        """Test refresh_pois endpoint with successful defense."""
        # Mock locations with POI that successfully defends
        mock_db.reference.return_value.get.side_effect = [
            {"10_20": {"danger_level": 3, "POI": "temple1", "region": "region1"}},
            {"control_status": "neutral", "faction_influence": {"faction1": 50}},
            25  # Current influence for faction1
        ]
        mock_random.random.return_value = 0.5  # 50% roll, defense succeeds (3 * 0.1 - 50 * 0.01 = -0.2 < 0.5)
        mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T00:00:00"
        
        # Mock the set and push operations
        mock_set = MagicMock()
        mock_push = MagicMock()
        mock_db.reference.return_value.set = mock_set
        mock_db.reference.return_value.push = mock_push
        
        response = client.post('/refresh_pois')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0  # No POIs conquered

    @patch('backend.systems.world_generation.worldgen_routes.generate_monsters_for_tile')
    def test_monster_spawns_endpoint(self, mock_generate_monsters, client): pass
        """Test monster_spawns endpoint."""
        mock_generate_monsters.return_value = [
            {"name": "Goblin", "cr": 0.25},
            {"name": "Orc", "cr": 0.5}
        ]
        
        response = client.get('/monster_spawns/10/20')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["tile"] == "10_20"
        assert len(data["monsters"]) == 2
        assert data["monsters"][0]["name"] == "Goblin"
        mock_generate_monsters.assert_called_once_with(10, 20)

    def test_generate_encounter_missing_party_id(self, client): pass
        """Test generate_encounter endpoint with missing party_id."""
        response = client.post('/generate_encounter', 
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "party_id is required" in data["error"]

    @patch('backend.systems.world_generation.worldgen_routes.db')
    def test_generate_encounter_party_not_found(self, mock_db, client): pass
        """Test generate_encounter endpoint with non-existent party."""
        mock_db.reference.return_value.get.return_value = None
        
        response = client.post('/generate_encounter',
                             data=json.dumps({"party_id": "nonexistent"}),
                             content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "Party nonexistent not found" in data["error"]

    @patch('backend.systems.world_generation.worldgen_routes.db')
    @patch('backend.systems.world_generation.worldgen_routes.random')
    @patch('backend.systems.world_generation.worldgen_routes.CombatStateManager')
    @patch('backend.systems.world_generation.worldgen_routes.award_xp_to_party')
    @patch('backend.systems.world_generation.worldgen_routes.uuid4')
    def test_generate_encounter_no_suitable_monsters(self, mock_uuid4, mock_award_xp, 
                                                   mock_combat_manager, mock_random, mock_db, client): pass
        """Test generate_encounter endpoint with no suitable monsters."""
        # Mock party data
        mock_db.reference.return_value.get.side_effect = [
            {"members": ["player1", "player2"]},  # Party
            {"level": 5, "name": "Player 1"},     # Player 1
            {"level": 6, "name": "Player 2"},     # Player 2
            {}  # Empty monsters list
        ]
        mock_random.random.return_value = 0.1
        
        response = client.post('/generate_encounter',
                             data=json.dumps({"party_id": "party1", "location": "100_100"}),
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "No suitable monsters found" in data["error"]

    @patch('backend.systems.world_generation.worldgen_routes.db')
    @patch('backend.systems.world_generation.worldgen_routes.random')
    @patch('backend.systems.world_generation.worldgen_routes.CombatStateManager')
    @patch('backend.systems.world_generation.worldgen_routes.award_xp_to_party')
    @patch('backend.systems.world_generation.worldgen_routes.uuid4')
    def test_generate_encounter_success(self, mock_uuid4, mock_award_xp, 
                                      mock_combat_manager, mock_random, mock_db, client): pass
        """Test generate_encounter endpoint with successful encounter generation."""
        # Mock party data - using level 1 characters for simpler CR calculation
        mock_db.reference.return_value.get.side_effect = [
            {"members": ["player1", "player2"]},  # Party
            {"level": 1, "name": "Player 1"},     # Player 1
            {"level": 1, "name": "Player 2"},     # Player 2
            {  # Monsters - ensure they match the expected CR range
                "goblin": {"name": "Goblin", "challenge_rating": 0.25, "hp": 7, "ac": 15, "dex": 14, "xp": 50},
                "orc": {"name": "Orc", "challenge_rating": 0.5, "hp": 15, "ac": 13, "dex": 12, "xp": 100},
                "kobold": {"name": "Kobold", "challenge_rating": 0.125, "hp": 5, "ac": 12, "dex": 15, "xp": 25}
            }
        ]
        
        # Mock random values
        mock_random.random.return_value = 0.1
        mock_random.sample.return_value = [
            {"name": "Goblin", "challenge_rating": 0.25, "hp": 7, "ac": 15, "dex": 14, "xp": 50}
        ]
        
        # Mock UUID generation
        mock_uuid4.return_value.hex = "abcd1234abcd1234"
        
        # Mock combat state
        mock_combat_state = MagicMock()
        mock_combat_state.id = "combat123"
        mock_combat_state.round = 1
        mock_combat_state.party = [MagicMock(character_id="player1"), MagicMock(character_id="player2")]
        mock_combat_state.enemies = [MagicMock(character_id="enemy_abcd1234")]
        mock_combat_manager.initialize_combat.return_value = mock_combat_state
        
        # Mock XP award
        mock_award_xp.return_value = {"player1": 150, "player2": 200}
        
        response = client.post('/generate_encounter',
                             data=json.dumps({"party_id": "party1", "location": "0_0"}),
                             content_type='application/json')
        
        if response.status_code != 200: pass
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "RAM-based combat started"
        assert data["battle_id"] == "combat123"
        assert data["round"] == 1
        assert "player1" in data["player_party"]
        assert "player2" in data["player_party"]
        assert "enemy_abcd1234" in data["enemy_party"]
        assert data["xp_awarded"]["player1"] == 150
        assert data["distance_fraction"] == 0.0  # (0 - 50) / 50 = 0.0, but clamped to 0

    def test_generate_encounter_invalid_location_format(self, client): pass
        """Test generate_encounter endpoint with invalid location format."""
        with patch('backend.systems.world_generation.worldgen_routes.db') as mock_db: pass
            mock_db.reference.return_value.get.side_effect = [
                {"members": ["player1"]},  # Party
                {"level": 1, "name": "Player 1"},  # Player 1
                {"goblin": {"name": "Goblin", "challenge_rating": 0.25, "hp": 7, "ac": 15, "dex": 14, "xp": 50}}
            ]
            
            with patch('backend.systems.world_generation.worldgen_routes.random') as mock_random: pass
                mock_random.random.return_value = 0.1
                mock_random.sample.return_value = [
                    {"name": "Goblin", "challenge_rating": 0.25, "hp": 7, "ac": 15, "dex": 14, "xp": 50}
                ]
                
                with patch('backend.systems.world_generation.worldgen_routes.CombatStateManager') as mock_combat_manager: pass
                    mock_combat_state = MagicMock()
                    mock_combat_state.id = "combat123"
                    mock_combat_state.round = 1
                    mock_combat_state.party = [MagicMock(character_id="player1")]
                    mock_combat_state.enemies = [MagicMock(character_id="enemy_123")]
                    mock_combat_manager.initialize_combat.return_value = mock_combat_state
                    
                    with patch('backend.systems.world_generation.worldgen_routes.award_xp_to_party') as mock_award_xp: pass
                        mock_award_xp.return_value = {"player1": 50}
                        
                        response = client.post('/generate_encounter',
                                             data=json.dumps({"party_id": "party1", "location": "invalid_format"}),
                                             content_type='application/json')
                        
                        assert response.status_code == 200
                        data = json.loads(response.data)
                        assert data["distance_fraction"] == 0.0  # Invalid format defaults to 0,0

    def test_generate_location_gpt_missing_coordinates(self, client): pass
        """Test generate_location_gpt endpoint with missing coordinates."""
        response = client.post('/generate_location_gpt',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Missing x or y coordinate" in data["error"]

    def test_generate_location_gpt_missing_x(self, client): pass
        """Test generate_location_gpt endpoint with missing x coordinate."""
        response = client.post('/generate_location_gpt',
                             data=json.dumps({"y": 10}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Missing x or y coordinate" in data["error"]

    def test_generate_location_gpt_missing_y(self, client): pass
        """Test generate_location_gpt endpoint with missing y coordinate."""
        response = client.post('/generate_location_gpt',
                             data=json.dumps({"x": 10}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Missing x or y coordinate" in data["error"]

    @patch('backend.systems.world_generation.worldgen_routes.openai')
    @patch('backend.systems.world_generation.worldgen_routes.db')
    def test_generate_location_gpt_success(self, mock_db, mock_openai, client): pass
        """Test generate_location_gpt endpoint with successful generation."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "name": "Ancient Temple",
            "description": "A mysterious temple covered in vines",
            "danger_level": 5,
            "buildings": ["Temple of the Moon"],
            "npcs": ["High Priestess Elara"],
            "tags": ["ancient", "mystical"],
            "lore_hooks": ["The temple holds a powerful artifact"]
        })
        mock_response.get.return_value = {"prompt_tokens": 50, "completion_tokens": 100}
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        # Mock database operations
        mock_db.reference.return_value.set = MagicMock()
        
        response = client.post('/generate_location_gpt',
                             data=json.dumps({"x": 10, "y": 20, "prompt": "Generate a mystical temple"}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Location generated and saved."
        assert data["location"]["name"] == "Ancient Temple"
        assert data["location"]["coordinates"]["x"] == 10
        assert data["location"]["coordinates"]["y"] == 20
        
        # Verify database was called
        mock_db.reference.assert_called_with("/locations/10_20")
        mock_db.reference.return_value.set.assert_called_once()

    @patch('backend.systems.world_generation.worldgen_routes.openai')
    def test_generate_location_gpt_openai_error(self, mock_openai, client): pass
        """Test generate_location_gpt endpoint with OpenAI error."""
        mock_openai.ChatCompletion.create.side_effect = Exception("OpenAI API error")
        
        response = client.post('/generate_location_gpt',
                             data=json.dumps({"x": 10, "y": 20}),
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "GPT or Firebase error" in data["error"]

    @patch('backend.systems.world_generation.worldgen_routes.openai')
    @patch('backend.systems.world_generation.worldgen_routes.db')
    def test_generate_location_gpt_json_parse_error(self, mock_db, mock_openai, client): pass
        """Test generate_location_gpt endpoint with JSON parsing error."""
        # Mock OpenAI response with invalid JSON
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Invalid JSON response"
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        response = client.post('/generate_location_gpt',
                             data=json.dumps({"x": 10, "y": 20}),
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "GPT or Firebase error" in data["error"]

    @patch('backend.systems.world_generation.worldgen_routes.generate_region')
    def test_generate_region_success(self, mock_generate_region, client): pass
        """Test generate_region endpoint with successful generation."""
        mock_generate_region.return_value = {
            "region_id": "region_123",
            "biome": "forest",
            "size": {"width": 15, "height": 15}
        }
        
        response = client.post('/generate_region',
                             data=json.dumps({"seed_x": 10, "seed_y": 20}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Region generated successfully"
        assert data["region_id"] == "region_123"
        assert data["biome"] == "forest"
        
        mock_generate_region.assert_called_once_with(seed_x=10, seed_y=20)

    @patch('backend.systems.world_generation.worldgen_routes.generate_region')
    def test_generate_region_default_params(self, mock_generate_region, client): pass
        """Test generate_region endpoint with default parameters."""
        mock_generate_region.return_value = {
            "region_id": "region_456",
            "biome": "grassland"
        }
        
        response = client.post('/generate_region',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Region generated successfully"
        
        mock_generate_region.assert_called_once_with(seed_x=0, seed_y=0)

    @patch('backend.systems.world_generation.worldgen_routes.generate_region')
    def test_generate_region_no_json_body(self, mock_generate_region, client): pass
        """Test generate_region endpoint with no JSON body - should use defaults."""
        mock_generate_region.return_value = {
            "region_id": "region_789",
            "biome": "desert"
        }
        
        # Send request without any data or content-type to test the endpoint's robustness
        response = client.post('/generate_region')
        
        # The endpoint should handle this gracefully and use default values
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Region generated successfully"
        
        mock_generate_region.assert_called_once_with(seed_x=0, seed_y=0)

    @patch('backend.systems.world_generation.worldgen_routes.generate_region')
    def test_generate_region_error(self, mock_generate_region, client): pass
        """Test generate_region endpoint with generation error."""
        mock_generate_region.side_effect = Exception("Region generation failed")
        
        response = client.post('/generate_region',
                             data=json.dumps({"seed_x": 10, "seed_y": 20}),
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "Region generation failed" in data["error"]

    def test_blueprint_registration(self): pass
        """Test that the blueprint is properly configured."""
        assert worldgen_bp.name == "worldgen"
        
        # Check that the blueprint has the expected endpoints
        # We can't directly access url_map on blueprint, but we can check the deferred functions
        assert hasattr(worldgen_bp, 'deferred_functions')
        assert len(worldgen_bp.deferred_functions) > 0

    @patch('backend.systems.world_generation.worldgen_routes.db')
    @patch('backend.systems.world_generation.worldgen_routes.random')
    @patch('backend.systems.world_generation.worldgen_routes.datetime')
    def test_refresh_pois_multiple_factions(self, mock_datetime, mock_random, mock_db, client): pass
        """Test refresh_pois endpoint with multiple factions defending."""
        # Mock locations with POI defended by multiple factions
        mock_db.reference.return_value.get.side_effect = [
            {"10_20": {"danger_level": 6, "POI": "temple1", "region": "region1"}},
            {"control_status": "neutral", "faction_influence": {"faction1": 30, "faction2": 20}},
            25,  # Current influence for faction1
            15   # Current influence for faction2
        ]
        mock_random.random.return_value = 0.5  # 50% roll, defense succeeds (6 * 0.1 - 50 * 0.01 = 0.1 < 0.5)
        mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T00:00:00"
        
        # Mock the set and push operations
        mock_set = MagicMock()
        mock_push = MagicMock()
        mock_db.reference.return_value.set = mock_set
        mock_db.reference.return_value.push = mock_push
        
        response = client.post('/refresh_pois')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0  # No POIs conquered due to strong defense