import pytest
import os
import json
from app.characters.character_builder_class import CharacterBuilder
from app.core.utils.json_utils import load_json

# Mock data for tests
MOCK_STARTER_KITS = {
    "starter_kits": [
        {
            "name": "Adventurer's Kit",
            "description": "Basic equipment for starting adventurers",
            "equipment": [
                {
                    "name": "Backpack",
                    "type": "tool",
                    "properties": ["container"],
                    "description": "A sturdy leather backpack"
                },
                {
                    "name": "Dagger",
                    "type": "weapon",
                    "damage": "1d4",
                    "properties": ["light", "finesse"],
                    "description": "A simple but effective blade"
                }
            ],
            "gold": 50
        },
        {
            "name": "Scholar's Kit",
            "description": "Equipment focused on knowledge and study",
            "equipment": [
                {
                    "name": "Spellbook",
                    "type": "tool",
                    "properties": ["magical"],
                    "description": "A book for recording spells"
                }
            ],
            "gold": 25
        }
    ]
}

@pytest.fixture
def character_builder():
    # Create a basic CharacterBuilder instance for testing
    return CharacterBuilder(
        race_data={},  # Empty race data as it's not needed for equipment tests
        feat_data={},  # Empty feat data as it's not needed for equipment tests
        skill_list=[]  # Empty skill list as it's not needed for equipment tests
    )

@pytest.fixture
def mock_starter_kits(monkeypatch, tmp_path):
    # Create a temporary starter_kits.json file
    starter_kits_path = tmp_path / "starter_kits.json"
    starter_kits_path.write_text(json.dumps(MOCK_STARTER_KITS))
    
    # Mock the DATA_DIR path to use our temporary directory
    monkeypatch.setattr("app.characters.character_builder_class.DATA_DIR", str(tmp_path))
    
    return MOCK_STARTER_KITS

def test_get_available_starter_kits(character_builder, mock_starter_kits):
    """Test retrieving available starter kits"""
    kits = character_builder.get_available_starter_kits()
    assert len(kits) == 2
    assert kits[0]["name"] == "Adventurer's Kit"
    assert kits[1]["name"] == "Scholar's Kit"

def test_apply_starter_kit_valid(character_builder, mock_starter_kits):
    """Test applying a valid starter kit"""
    character_builder.apply_starter_kit("Adventurer's Kit")
    
    assert len(character_builder.starter_kit["equipment"]) == 2
    assert character_builder.gold == 50
    assert character_builder.starter_kit["equipment"][0]["name"] == "Backpack"
    assert character_builder.starter_kit["equipment"][1]["name"] == "Dagger"

def test_apply_starter_kit_invalid(character_builder, mock_starter_kits):
    """Test applying an invalid starter kit"""
    with pytest.raises(ValueError, match="Unknown starter kit: Invalid Kit"):
        character_builder.apply_starter_kit("Invalid Kit")

def test_finalize_with_starter_kit(character_builder, mock_starter_kits):
    """Test character finalization with starter kit equipment"""
    character_builder.character_name = "Test Character"
    character_builder.apply_starter_kit("Adventurer's Kit")
    
    result = character_builder.finalize()
    
    assert len(result["equipment"]) == 2
    assert result["gold"] == 50
    assert any(item["name"] == "Backpack" for item in result["equipment"])
    assert any(item["name"] == "Dagger" for item in result["equipment"])

def test_empty_starter_kits_file(character_builder, monkeypatch, tmp_path):
    """Test handling of empty starter kits file"""
    # Create an empty starter_kits.json file
    starter_kits_path = tmp_path / "starter_kits.json"
    starter_kits_path.write_text(json.dumps({"starter_kits": []}))
    
    # Mock the DATA_DIR path
    monkeypatch.setattr("app.characters.character_builder_class.DATA_DIR", str(tmp_path))
    
    kits = character_builder.get_available_starter_kits()
    assert len(kits) == 0

def test_missing_starter_kits_file(character_builder, monkeypatch, tmp_path):
    """Test handling of missing starter kits file"""
    # Mock the DATA_DIR path to a directory without starter_kits.json
    monkeypatch.setattr("app.characters.character_builder_class.DATA_DIR", str(tmp_path))
    
    kits = character_builder.get_available_starter_kits()
    assert len(kits) == 0 