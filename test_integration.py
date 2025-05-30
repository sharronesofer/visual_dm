#!/usr/bin/env python3
"""
Character Management Integration Test
-----------------------------------
Test script to verify the character management system integration
between Unity and FastAPI backend.
"""

import json
import requests
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_CHARACTER_ID = "test-integration-char-001"

def test_character_creation():
    """Test character creation via API."""
    print("🧪 Testing Character Creation...")
    
    character_data = {
        "character_name": "Integration Test Character",
        "character_id": TEST_CHARACTER_ID,
        "race": "Human",
        "attributes": {
            "strength": 2,
            "dexterity": 1,
            "constitution": 3,
            "intelligence": 2,
            "wisdom": 1,
            "charisma": 3
        },
        "background": "A test character for integration testing.",
        "personality": {
            "traits": ["Brave", "Curious"],
            "ideals": [],
            "bonds": [],
            "flaws": []
        },
        "alignment": "Neutral",
        "languages": ["Common"]
    }
    
    response = requests.post(f"{BASE_URL}/characters", json=character_data)
    
    if response.status_code == 201:
        character = response.json()
        print(f"✅ Character created successfully: {character['character_name']} (ID: {character['id']})")
        print(f"   Level: {character['level']}, Race: {character['race']}")
        print(f"   HP: {character['derived_stats']['max_hit_points']}, MP: {character['derived_stats']['max_mana_points']}")
        return character
    else:
        print(f"❌ Character creation failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_character_listing():
    """Test character listing API."""
    print("\n🧪 Testing Character Listing...")
    
    response = requests.get(f"{BASE_URL}/characters")
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and 'characters' in data:
            characters = data['characters']
            print(f"✅ Retrieved {len(characters)} characters")
            for char in characters:
                print(f"   - {char['character_name']} (Level {char['level']} {char['race']})")
        elif isinstance(data, list):
            print(f"✅ Retrieved {len(data)} characters")
            for char in data:
                print(f"   - {char['character_name']} (Level {char['level']} {char['race']})")
        return True
    else:
        print(f"❌ Character listing failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_character_retrieval(character_id: str):
    """Test character retrieval by game ID."""
    print(f"\n🧪 Testing Character Retrieval (ID: {character_id})...")
    
    response = requests.get(f"{BASE_URL}/characters/by-game-id/{character_id}")
    
    if response.status_code == 200:
        character = response.json()
        print(f"✅ Character retrieved: {character['character_name']}")
        print(f"   Attributes: STR {character['attributes']['strength']}, "
              f"DEX {character['attributes']['dexterity']}, CON {character['attributes']['constitution']}")
        print(f"   Skills: {character.get('skills', {})}")
        print(f"   Abilities: {character.get('abilities', [])}")
        return character
    else:
        print(f"❌ Character retrieval failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_experience_grant(character_id: str):
    """Test granting experience to a character."""
    print(f"\n🧪 Testing Experience Grant (ID: {character_id})...")
    
    # Get character UUID first
    char_response = requests.get(f"{BASE_URL}/characters/by-game-id/{character_id}")
    if char_response.status_code != 200:
        print("❌ Could not retrieve character for XP grant")
        return False
    
    character = char_response.json()
    uuid = character['id']
    original_xp = character['experience']
    original_level = character['level']
    
    xp_data = {
        "amount": 150,
        "source": "Integration Test",
        "notes": "Testing experience grant functionality"
    }
    
    response = requests.post(f"{BASE_URL}/characters/{uuid}/experience", json=xp_data)
    
    if response.status_code == 200:
        updated_character = response.json()
        new_xp = updated_character['experience']
        new_level = updated_character['level']
        
        print(f"✅ Experience granted successfully")
        print(f"   XP: {original_xp} -> {new_xp} (+{new_xp - original_xp})")
        print(f"   Level: {original_level} -> {new_level}")
        
        if new_level > original_level:
            print(f"🎉 Character leveled up from {original_level} to {new_level}!")
        
        return True
    else:
        print(f"❌ Experience grant failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_skill_increase(character_id: str):
    """Test increasing a character's skill."""
    print(f"\n🧪 Testing Skill Increase (ID: {character_id})...")
    
    # Get character UUID first
    char_response = requests.get(f"{BASE_URL}/characters/by-game-id/{character_id}")
    if char_response.status_code != 200:
        print("❌ Could not retrieve character for skill increase")
        return False
    
    character = char_response.json()
    uuid = character['id']
    original_skills = character.get('skills', {})
    
    skill_data = {
        "skill_name": "Combat",
        "increase_amount": 1
    }
    
    response = requests.post(f"{BASE_URL}/characters/{uuid}/skills", json=skill_data)
    
    if response.status_code == 200:
        updated_character = response.json()
        new_skills = updated_character.get('skills', {})
        
        print(f"✅ Skill increased successfully")
        print(f"   Original skills: {original_skills}")
        print(f"   Updated skills: {new_skills}")
        print(f"   Combat skill: {original_skills.get('Combat', 0)} -> {new_skills.get('Combat', 0)}")
        
        return True
    else:
        print(f"❌ Skill increase failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_ability_selection(character_id: str):
    """Test adding an ability to a character."""
    print(f"\n🧪 Testing Ability Selection (ID: {character_id})...")
    
    # Get character UUID first
    char_response = requests.get(f"{BASE_URL}/characters/by-game-id/{character_id}")
    if char_response.status_code != 200:
        print("❌ Could not retrieve character for ability selection")
        return False
    
    character = char_response.json()
    uuid = character['id']
    original_abilities = character.get('abilities', [])
    
    ability_data = {
        "ability_name": "Arcane Focus",
        "prerequisites_met": True
    }
    
    response = requests.post(f"{BASE_URL}/characters/{uuid}/abilities", json=ability_data)
    
    if response.status_code == 200:
        updated_character = response.json()
        new_abilities = updated_character.get('abilities', [])
        
        print(f"✅ Ability added successfully")
        print(f"   Original abilities: {original_abilities}")
        print(f"   Updated abilities: {new_abilities}")
        
        return True
    else:
        print(f"❌ Ability selection failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_progression_history(character_id: str):
    """Test retrieving character progression history."""
    print(f"\n🧪 Testing Progression History (ID: {character_id})...")
    
    # Get character UUID first
    char_response = requests.get(f"{BASE_URL}/characters/by-game-id/{character_id}")
    if char_response.status_code != 200:
        print("❌ Could not retrieve character for progression history")
        return False
    
    character = char_response.json()
    uuid = character['id']
    
    response = requests.get(f"{BASE_URL}/characters/{uuid}/progression")
    
    if response.status_code == 200:
        progression_history = response.json()
        
        print(f"✅ Progression history retrieved")
        print(f"   Total entries: {len(progression_history)}")
        
        for entry in progression_history[:3]:  # Show first 3 entries
            print(f"   - {entry['event_type']}: {entry.get('notes', 'No notes')}")
            if entry.get('experience'):
                print(f"     XP: {entry['experience'].get('before', 0)} -> {entry['experience'].get('after', 0)}")
        
        return True
    else:
        print(f"❌ Progression history retrieval failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_character_deletion(character_id: str):
    """Test character deletion."""
    print(f"\n🧪 Testing Character Deletion (ID: {character_id})...")
    
    # Get character UUID first
    char_response = requests.get(f"{BASE_URL}/characters/by-game-id/{character_id}")
    if char_response.status_code != 200:
        print("❌ Could not retrieve character for deletion")
        return False
    
    character = char_response.json()
    uuid = character['id']
    
    response = requests.delete(f"{BASE_URL}/characters/{uuid}")
    
    if response.status_code == 200:
        print(f"✅ Character deleted successfully")
        
        # Verify deletion
        verify_response = requests.get(f"{BASE_URL}/characters/by-game-id/{character_id}")
        if verify_response.status_code == 404:
            print(f"✅ Deletion verified - character no longer exists")
            return True
        else:
            print(f"⚠️  Character still exists after deletion")
            return False
    else:
        print(f"❌ Character deletion failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_server_connection():
    """Test basic server connection."""
    print("🧪 Testing Server Connection...")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to server: {e}")
        return False

def run_integration_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("CHARACTER MANAGEMENT INTEGRATION TESTS")
    print("=" * 60)
    
    # Test server connection
    if not test_server_connection():
        print("\n❌ Server connection failed. Make sure the backend is running.")
        return False
    
    print("\n" + "=" * 40)
    print("RUNNING CHARACTER MANAGEMENT TESTS")
    print("=" * 40)
    
    results = []
    
    # Test character creation
    character = test_character_creation()
    if character:
        results.append(("Character Creation", True))
        character_id = character['character_id']
        
        # Test character listing
        results.append(("Character Listing", test_character_listing()))
        
        # Test character retrieval
        results.append(("Character Retrieval", test_character_retrieval(character_id)))
        
        # Test experience grant
        results.append(("Experience Grant", test_experience_grant(character_id)))
        
        # Test skill increase
        results.append(("Skill Increase", test_skill_increase(character_id)))
        
        # Test ability selection
        results.append(("Ability Selection", test_ability_selection(character_id)))
        
        # Test progression history
        results.append(("Progression History", test_progression_history(character_id)))
        
        # Test character deletion (cleanup)
        results.append(("Character Deletion", test_character_deletion(character_id)))
    else:
        results.append(("Character Creation", False))
    
    # Print summary
    print("\n" + "=" * 40)
    print("TEST RESULTS SUMMARY")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if passed_test:
            passed += 1
    
    print("-" * 40)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1) 