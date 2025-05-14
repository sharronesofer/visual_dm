import requests
import os
import json
import re
from visual_client.core.utils.rules_loader import RulesLoader

# Get the workspace root directory
CURRENT_FILE = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_FILE)
WORKSPACE_ROOT = "/Users/Sharrone/Visual_DM"  # Set the workspace root directly

# Initialize RulesLoader with the correct base path
rules_loader = RulesLoader()
rules_loader.base_path = os.path.join(WORKSPACE_ROOT, "app/data/rules")

def ensure_home_region():
    try:
        res = requests.get("http://localhost:5050/global_state/settings", timeout=10)
        
        if res.status_code == 404:
            print("⚠️ /global_state/settings not found, assuming no home region exists.")
            data = {}
        else:
            data = res.json() or {}

        home_region = data.get("home_region")

        if not home_region:
            print("🌍 No home region found — generating new starting region...")
            res = requests.post("http://localhost:5050/regions/create_starting_region", timeout=15)
            if res.status_code == 200:
                region_data = res.json().get("region", {})
                region_id = region_data.get("region_id")
                if region_id:
                    requests.post("http://localhost:5050/global_state/update", json={"settings": {"home_region": region_id}})
                    return region_id
                else:
                    raise Exception("Failed to get region ID from response")
            else:
                raise Exception(f"Failed to generate starting region: {res.text}")
        else:
            print("✅ Existing home region:", home_region)
            return home_region

    except Exception as e:
        print("❌ Error ensuring home region:", str(e))
        return "capital_hub"

def feat_prereqs_met(name, known_feats, skills, attributes):
    """
    Checks whether a feat is available given current skills, attributes, and known feats.
    Prereqs come from feats.json (parsed as strings).
    """
    feat_data = rules_loader.get_feat_data(name)
    prereqs = feat_data.get("prerequisites", [])
    print(f"🧠 Checking prereqs for: {name}")

    for line in prereqs:
        # Handle numeric conditions like "Skill >= N" or "Attribute >= N"
        match = re.match(r"(\w+)\s*>=\s*(\d+)", line)
        if match:
            key = match.group(1)
            required_val = int(match.group(2))

            # Pull value from skills or attributes
            if key in skills:
                actual_val = skills[key]
            elif key in attributes:
                actual_val = attributes[key]
            else:
                actual_val = 0  # default fallback

            if actual_val < required_val:
                print(f"   ✖ {name}: {key} = {actual_val} < {required_val}")
                return False
            continue

        # Handle feat prerequisites like "Feat: Sneak Attack"
        elif line.startswith("Feat:"):
            required_feats = [f.strip() for f in line[5:].split(",")]
            for feat in required_feats:
                if feat and feat not in known_feats:
                    print(f"   ✖ {name}: missing required feat '{feat}'")
                    return False
            continue

        # Unknown prereq format (safety fallback)
        else:
            print(f"   ⚠️ Unhandled prereq format: '{line}'")
            continue

    print(f"   ✅ {name}: prerequisites met.")
    return True

def save_character(data):
    """Save character data to the backend"""
    try:
        res = requests.post("http://localhost:5050/character/create", json=data)
        if res.status_code == 200:
            return res.json().get("character_id")
        else:
            print(f"❌ Failed to save character: {res.text}")
            return None
    except Exception as e:
        print(f"❌ Error saving character: {str(e)}")
        return None

def begin_game(character_id):
    """Start the game with the given character"""
    try:
        res = requests.post("http://localhost:5050/start_game", json={"character_id": character_id})
        return res.status_code == 200
    except Exception as e:
        print(f"❌ Error starting game: {str(e)}")
        return False 