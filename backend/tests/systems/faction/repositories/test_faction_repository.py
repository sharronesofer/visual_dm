import pytest
import tempfile
import shutil
import json
from pathlib import Path
from backend.systems.faction.repositories.faction_repository import FactionRepository

class TestFactionRepository: pass
    """Test suite for FactionRepository."""
    
    @pytest.fixture
    def temp_data_dir(self): pass
        """Create a temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
        
    @pytest.fixture
    def repository(self, temp_data_dir): pass
        """Create a FactionRepository instance with a temporary data directory."""
        return FactionRepository(data_dir=temp_data_dir)
    
    @pytest.fixture
    def sample_faction_data(self): pass
        """Create sample faction data for testing."""
        return {
            "id": "faction-123",
            "name": "Iron Legion",
            "type": "MILITARY",
            "description": "A militaristic faction focused on conquest",
            "influence": 75.0,
            "reputation": 50.0,
            "resources": {
                "gold": 1000,
                "materials": {"iron": 500},
                "special_resources": {},
                "income_sources": ["mining", "taxation"],
                "expenses": ["military", "maintenance"]
            },
            "territory": {"regions": ["region-1", "region-2"]},
            "relationships": {
                "allies": [],
                "enemies": ["faction-456"],
                "neutral": [],
                "trade_partners": []
            },
            "history": "Founded as a military organization",
            "is_active": True,
            "power": 85.0,
            "wealth": 5000.0,
            "goals": {
                "current": ["conquer northern territories"],
                "completed": [],
                "failed": []
            },
            "policies": {
                "diplomatic": {"aggression": 80, "trade_focus": 20, "expansion": 90},
                "economic": {"tax_rate": 15, "trade_tariffs": 10, "investment_focus": ["military"]},
                "military": {
                    "stance": "aggressive",
                    "recruitment_rate": "high",
                    "training_focus": ["combat", "tactics"]
                }
            },
            "state": {
                "active_wars": ["war-123"],
                "current_projects": ["fortress construction"],
                "recent_events": ["conquered eastern plains"],
                "statistics": {
                    "members_count": 150,
                    "territory_count": 2,
                    "quest_success_rate": 85
                }
            }
        }
    
    def test_get_all_factions(self, repository, sample_faction_data): pass
        """Test retrieving all factions."""
        # Create a faction first
        repository.create_faction(sample_faction_data)
        
        result = repository.get_all_factions()
        
        assert len(result) == 1
        assert result[0]["id"] == "faction-123"
        assert result[0]["name"] == "Iron Legion"
        assert result[0]["type"] == "MILITARY"
    
    def test_get_faction_by_id(self, repository, sample_faction_data): pass
        """Test retrieving a faction by ID."""
        # Create a faction first
        repository.create_faction(sample_faction_data)
        
        result = repository.get_faction_by_id("faction-123")
        
        assert result is not None
        assert result["id"] == "faction-123"
        assert result["name"] == "Iron Legion"
        assert result["type"] == "MILITARY"
    
    def test_get_faction_by_id_not_found(self, repository): pass
        """Test retrieving a non-existent faction by ID."""
        result = repository.get_faction_by_id("non-existent-id")
        
        assert result is None
    
    def test_create_faction(self, repository, sample_faction_data): pass
        """Test creating a new faction."""
        result = repository.create_faction(sample_faction_data)
        
        assert result["id"] == "faction-123"
        assert result["name"] == "Iron Legion"
        assert "created_at" in result
        assert "updated_at" in result
        
        # Verify it was actually saved
        saved_faction = repository.get_faction_by_id("faction-123")
        assert saved_faction is not None
        assert saved_faction["name"] == "Iron Legion"
    
    def test_update_faction(self, repository, sample_faction_data): pass
        """Test updating an existing faction."""
        # Create a faction first
        repository.create_faction(sample_faction_data)
        
        # Update the faction
        update_data = {
            "name": "New Legion Name",
            "influence": 80.0,
            "description": "Updated description"
        }
        
        result = repository.update_faction("faction-123", update_data)
        
        assert result is not None
        assert result["name"] == "New Legion Name"
        assert result["influence"] == 80.0
        assert result["description"] == "Updated description"
        assert "updated_at" in result
    
    def test_delete_faction(self, repository, sample_faction_data): pass
        """Test deleting a faction."""
        # Create a faction first
        repository.create_faction(sample_faction_data)
        
        # Verify it exists
        assert repository.get_faction_by_id("faction-123") is not None
        
        # Delete it
        result = repository.delete_faction("faction-123")
        
        assert result is True
        
        # Verify it's gone
        assert repository.get_faction_by_id("faction-123") is None
    
    def test_get_factions_by_type(self, repository, sample_faction_data): pass
        """Test retrieving factions by type."""
        # Create a faction first
        repository.create_faction(sample_faction_data)
        
        # Create another faction with different type
        other_faction = sample_faction_data.copy()
        other_faction["id"] = "faction-456"
        other_faction["name"] = "Arcane Circle"
        other_faction["type"] = "ARCANE"
        repository.create_faction(other_faction)
        
        result = repository.get_factions_by_type("MILITARY")
        
        assert len(result) == 1
        assert result[0]["type"] == "MILITARY"
        assert result[0]["name"] == "Iron Legion"
    
    def test_get_factions_by_territory(self, repository, sample_faction_data): pass
        """Test retrieving factions by territory."""
        # Create a faction first
        repository.create_faction(sample_faction_data)
        
        result = repository.get_factions_by_territory("region-1")
        
        assert len(result) == 1
        assert "region-1" in result[0]["territory"]["regions"]
    
    def test_get_at_war_factions(self, repository, sample_faction_data): pass
        """Test retrieving factions that are at war."""
        # Modify faction to be at war
        sample_faction_data["state"]["active_wars"] = ["war-123", "war-456"]
        
        # Create the faction
        repository.create_faction(sample_faction_data)
        
        result = repository.get_at_war_factions()
        
        assert len(result) == 1
        assert len(result[0]["state"]["active_wars"]) > 0 