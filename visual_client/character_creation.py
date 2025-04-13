import os
import sys
import pygame
import random
import requests
from textwrap import wrap
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)

feat_view_mode = "categories"  # Modes: "categories" or "feats"
current_category = None
feat_group_keys = []  # Initialize as empty list
selected_feat_tab = 0

# How many attribute points the player can spend in total
points_pool = 16

# Determine the directory where this script is located
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

STAT_DESCRIPTIONS = {
    "STR": "Measures physical strength.",
    "DEX": "Measures agility and reflexes.",
    "CON": "Measures endurance and stamina.",
    "INT": "Measures intellect and reasoning.",
    "WIS": "Measures perception and insight.",
    "CHA": "Measures charisma and influence."
}

# --- Global UI Variables ---
ATTRIBUTES = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
LEVEL = 1
MAX_FEATS = 7
MAX_BG_LENGTH = 10000
MAX_VISIBLE = 18

# Helper function to load JSON data from a URL, with a fallback.
def safe_get_json(url, fallback={}):
    try:
        response = requests.get(url, timeout=3)
        return response.json()
    except Exception as e:
        logging.error(f"Error loading {url}: {e}")
        return fallback

# --- Load local JSON files ---
def load_local_json(filename):
    path = os.path.join(CURRENT_DIR, filename)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load {filename}: {e}")
        return {}

equipment_data = load_local_json("equipment.json")
intrinsic_feats = load_local_json("intrinsic_feats.json")

# Normalize intrinsic_feats to a list of names
intrinsic_feats_raw = load_local_json("intrinsic_feats.json")
if isinstance(intrinsic_feats_raw, list):
    intrinsic_feats = []
    for item in intrinsic_feats_raw:
        if isinstance(item, dict):
            if "name" in item:
                intrinsic_feats.append(item["name"])
            else:
                logging.warning(f"Intrinsic feat dictionary without 'name': {item}")
        elif isinstance(item, str):
            intrinsic_feats.append(item)
        else:
            logging.warning(f"Unexpected intrinsic feat format: {item}")
else:
    intrinsic_feats = []

# --- Load rule endpoints via URLs ---
RACES_URL = "http://localhost:5050/rules/races"
SKILLS_URL = "http://localhost:5050/rules/skills"
FEATS_URL = "http://localhost:5050/rules/feats"
STARTING_KITS_URL = "http://localhost:5050/rules/starting_kits"

race_data = safe_get_json(RACES_URL, {"Human": {"description": "Fallback race."}})
skill_data = safe_get_json(SKILLS_URL, {"Stealth": {"description": "Fallback skill."}})
feats_data = safe_get_json(FEATS_URL, [])
if isinstance(feats_data, list):
    feat_index = { feat["name"]: feat for feat in feats_data }
else:
    feat_index = feats_data

starter_kits = safe_get_json(STARTING_KITS_URL, {})
if isinstance(starter_kits, list):
    starter_kits = { kit["name"]: kit for kit in starter_kits }

# Group feats by category
def group_feats_by_category(feat_dict):
    groups = {}
    for name, feat in feat_dict.items():
        category = feat.get("category", "Misc")
        groups.setdefault(category, []).append(name)
    return groups

# Simple check for whether feat is valid (from your code)
def is_feat_valid(feat_name, character):
    feat = feat_index.get(feat_name, {})
    prereqs = feat.get("prerequisites", {})
    if not isinstance(prereqs, dict):
        for req in prereqs:
            if ">=" in req:
                key, val = req.split(">= ")
                try:
                    required = int(val.strip())
                except Exception:
                    required = 0
                if character["stats"].get(key.strip(), 0) < required:
                    return False
        return True

    skill_reqs = prereqs.get("skills", [])
    for req in skill_reqs:
        required_skill = req.get("name")
        required_rank = req.get("rank", 0)
        if character["skills"].get(required_skill, 0) < required_rank:
            return False

    feat_req = prereqs.get("feat")
    if feat_req:
        if feat_req not in character["feats"]:
            return False

    other_req = prereqs.get("other")
    if other_req:
        if character.get("other") != other_req:
            return False

    return True

# Character state
character = {
    "name": "",
    "race": None,
    "level": LEVEL,
    "base_stats": {},
    "stats": {},
    "racial_modifiers": {},
    "racial_traits": {},
    "racial_description": "",
    "skills": {},
    "feats": [],
    "starting_kit": None,
    "background": "",
    "remaining_skill_points": 0,
    "skill_points_total": 0,
    "max_skill_rank": LEVEL + 3,
    "dr": 0,
    "step": 0,
    "player": "PlayerPlaceholder"
}

steps = ["Race", "Stats", "Skills", "Feats", "Name", "Background", "Kit", "Summary"]

# Local UI Vars
selected_index = 0
scroll_offset = 0
name_input = ""
background_input = ""

# Stats-specific
stats_phase = "pointbuy"  # We only do point-buy
assigned_stats = {attr: -2 for attr in ATTRIBUTES}  # e.g. start each stat at 8
selected_attribute_index = 0

feat_groups = group_feats_by_category(feat_index)
feat_group_keys = sorted(feat_groups.keys())

result = None

def launch_character_creation():
    global feat_view_mode, current_category, feat_group_keys, selected_feat_tab
    global selected_index, scroll_offset, name_input, background_input
    global stats_phase, assigned_stats, selected_attribute_index
    global points_pool, result

    # Re-init local variables
    selected_index = 0
    scroll_offset = 0
    name_input = ""
    background_input = ""
    stats_phase = "pointbuy"
    assigned_stats.update({attr: -2 for attr in ATTRIBUTES})  # start each at 8
    selected_attribute_index = 0

    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Character Creation")
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    running = True
    result = None

    while running:
        current_step = steps[character["step"] % len(steps)]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                result = {}

            elif event.type == pygame.KEYDOWN:
                current_step = steps[character["step"] % len(steps)]

                if current_step == "Stats":
                    # ========== STATS STEP (POINT BUY OR WHATEVER) ==========
                    if event.key == pygame.K_UP:
                        # Move highlight up among attributes
                        selected_attribute_index = (selected_attribute_index - 1) % len(ATTRIBUTES)
                    elif event.key == pygame.K_DOWN:
                        # Move highlight down among attributes
                        selected_attribute_index = (selected_attribute_index + 1) % len(ATTRIBUTES)
                    elif event.key == pygame.K_LEFT:
                        # Decrement the chosen stat if above min
                        attr = ATTRIBUTES[selected_attribute_index]
                        if assigned_stats[attr] > -2 and points_pool < 99:
                            assigned_stats[attr] -= 1
                            points_pool += 1
                    elif event.key == pygame.K_RIGHT:
                        # Increment the chosen stat if below max and have points
                        attr = ATTRIBUTES[selected_attribute_index]
                        if assigned_stats[attr] < 5 and points_pool > 0:
                            assigned_stats[attr] += 1
                            points_pool -= 1
                    elif event.key == pygame.K_RETURN:
                        character["base_stats"] = assigned_stats.copy()
                        character["stats"] = assigned_stats.copy()
                        
                        # Example formula: skill points = 14 + INT
                        INT_val = assigned_stats.get("INT", 0)
                        skill_pts = 14 + INT_val
                        
                        character["skill_points_total"] = skill_pts
                        character["remaining_skill_points"] = skill_pts

                        # Then move to next step
                        character["step"] += 1
                        selected_index = 0
                    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                        # go back or exit
                        character["step"] = max(0, character["step"] - 1)
                        selected_index = 0

                elif current_step == "Race":
                    # ========== RACE STEP ==========
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        race_list = list(race_data.keys())
                        if event.key == pygame.K_UP:
                            selected_index = max(selected_index - 1, 0)
                        else: # K_DOWN
                            selected_index = min(selected_index + 1, len(race_list) - 1)
                    elif event.key == pygame.K_RETURN:
                        # Set race to the selected one & move on
                        race_list = list(race_data.keys())
                        if race_list:
                            character["race"] = race_list[selected_index]
                        character["step"] += 1
                        selected_index = 0
                    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                        character["step"] = max(0, character["step"] - 1)
                        selected_index = 0

                elif current_step == "Skills":
                    skill_list = list(skill_data.keys())

                    if event.key == pygame.K_UP:
                        # move highlight up
                        selected_index = max(selected_index - 1, 0)

                    elif event.key == pygame.K_DOWN:
                        # move highlight down
                        selected_index = min(selected_index + 1, len(skill_list) - 1)

                    elif event.key == pygame.K_LEFT:
                        # Decrement rank if it's above 0
                        if skill_list and selected_index < len(skill_list):
                            sel_skill = skill_list[selected_index]
                            rank = character["skills"].get(sel_skill, 0)
                            if rank > 0:
                                character["skills"][sel_skill] = rank - 1
                                character["remaining_skill_points"] += 1

                    elif event.key == pygame.K_RIGHT:
                        # Increment rank if it's below 4 and you still have skill points
                        if skill_list and selected_index < len(skill_list):
                            sel_skill = skill_list[selected_index]
                            rank = character["skills"].get(sel_skill, 0)
                            if rank < 4 and character["remaining_skill_points"] > 0:
                                character["skills"][sel_skill] = rank + 1
                                character["remaining_skill_points"] -= 1

                    elif event.key == pygame.K_RETURN:
                        # Confirm and go next
                        character["step"] += 1
                        selected_index = 0

                    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                        # Go back one step
                        character["step"] = max(0, character["step"] - 1)
                        selected_index = 0


                elif current_step == "Feats":
                    # ========== FEATS STEP ==========
                    if feat_view_mode == "categories":
                        if event.key == pygame.K_LEFT:
                            selected_index = (selected_index - 1) % len(feat_group_keys)
                        elif event.key == pygame.K_RIGHT:
                            selected_index = (selected_index + 1) % len(feat_group_keys)
                        elif event.key == pygame.K_RETURN:
                            # Enter feats view for selected category
                            current_category = feat_group_keys[selected_index]
                            feat_view_mode = "feats"
                            selected_index = 0
                            scroll_offset = 0
                        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                            character["step"] = max(0, character["step"] - 1)
                            selected_index = 0
                    else:
                        # feat_view_mode == "feats"
                        current_feats = feat_groups.get(current_category, [])
                        if event.key == pygame.K_LEFT:
                            # Left => go back to categories
                            feat_view_mode = "categories"
                            selected_index = feat_group_keys.index(current_category)
                        elif event.key == pygame.K_UP:
                            selected_index = max(selected_index - 1, 0)
                        elif event.key == pygame.K_DOWN:
                            selected_index = min(selected_index + 1, len(current_feats) - 1)
                        elif event.key == pygame.K_SPACE:
                            # Toggle this feat
                            if current_feats:
                                featname = current_feats[selected_index]
                                if featname in character["feats"]:
                                    character["feats"].remove(featname)
                                else:
                                    if len(character["feats"]) < MAX_FEATS:
                                        character["feats"].append(featname)
                        elif event.key == pygame.K_RETURN:
                            # Confirm feats & next step
                            character["step"] += 1
                            feat_view_mode = "categories"
                            selected_index = 0
                        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                            # Also go back to categories or step
                            feat_view_mode = "categories"
                            selected_index = feat_group_keys.index(current_category)

                elif current_step == "Name":
                    # ========== NAME STEP ==========
                    if event.key == pygame.K_RETURN:
                        # Confirm name & go next
                        character["step"] += 1
                        selected_index = 0
                    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                        if len(name_input) > 0:
                            name_input = name_input[:-1]
                        else:
                            # If empty, go back a step
                            character["step"] = max(0, character["step"] - 1)
                    else:
                        # Handle typed characters
                        if event.unicode.isprintable():
                            name_input += event.unicode

                elif current_step == "Background":
                    # ========== BACKGROUND STEP ==========
                    if event.key == pygame.K_RETURN:
                        # Confirm background
                        character["background"] = background_input
                        character["step"] += 1
                        selected_index = 0
                    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                        if len(background_input) > 0:
                            background_input = background_input[:-1]
                        else:
                            # If empty, go back
                            character["step"] = max(0, character["step"] - 1)
                    else:
                        if event.unicode.isprintable():
                            background_input += event.unicode

                elif current_step == "Kit":
                    # ========== KIT STEP ==========
                    kit_list = sorted(list(starter_kits.keys()))
                    if event.key == pygame.K_UP:
                        selected_index = max(selected_index - 1, 0)
                    elif event.key == pygame.K_DOWN:
                        selected_index = min(selected_index + 1, len(kit_list) - 1)
                    elif event.key == pygame.K_RETURN:
                        if kit_list and selected_index < len(kit_list):
                            character["starting_kit"] = kit_list[selected_index]
                        character["step"] += 1
                        selected_index = 0
                    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                        character["step"] = max(0, character["step"] - 1)
                        selected_index = 0

                elif current_step == "Summary":
                    # ========== SUMMARY STEP ==========
                    if event.key == pygame.K_RETURN:
                        # Possibly do final save, or set result => next: "start_game"
                        # e.g.:
                        result = {"next": "start_game", "character": character}
                        running = False
                    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                        character["step"] = max(0, character["step"] - 1)
                        selected_index = 0

        # End of event processing
        screen.fill((30, 30, 60))
        prompt_str = (f"Step: {current_step}   (UP/DOWN = select, LEFT/RIGHT = +/- stat or feats, ENTER to confirm, "
                      f"BACKSPACE to go back, Points={points_pool})")
        screen.blit(font.render(prompt_str, True, (255,255,255)), (50, 30))

        if current_step == "Stats":
            if stats_phase == "pointbuy":
                # Pull the chosen race's modifiers, if any
                chosen_race = character.get("race")
                if chosen_race and chosen_race in race_data:
                    race_mods = race_data[chosen_race].get("ability_modifiers", {})
                else:
                    race_mods = {}

                y = 100
                screen.blit(font.render("POINT BUY MODE", True, (255,255,255)), (100, y - 30))

                # For each attribute, show base_val, race bonus, and total
                for i, attr in enumerate(ATTRIBUTES):
                    color = (255, 255, 0) if i == selected_attribute_index else (200, 200, 200)
                    base_val = assigned_stats.get(attr, 8)  # or whatever your default is
                    bonus = race_mods.get(attr, 0)
                    total = base_val + bonus
                    line_text = f"{attr}: {base_val}  {'+' if bonus >= 0 else ''}{bonus}  => {total}"
                    screen.blit(font.render(line_text, True, color), (100, y + i*40))

                # Show how many points remain
                text_pts = f"Points remaining: {points_pool}"
                screen.blit(font.render(text_pts, True, (255,255,0)), (100, y + len(ATTRIBUTES)*40))

                help_msg = "Use LEFT/RIGHT to adjust stats, ENTER to confirm, BACKSPACE to go back"
                screen.blit(font.render(help_msg, True, (200,255,200)), (100, y + len(ATTRIBUTES)*40 + 40))

        elif current_step == "Race":
            race_list = list(race_data.keys())
            y = 100
            # Display each race in a vertical list
            for i, race in enumerate(race_list):
                col = (255,255,0) if i == selected_index else (200,200,200)
                screen.blit(font.render(race, True, col), (100, y + i * 30))

            # If we have a valid selected race, show its description + ability modifiers
            if race_list and selected_index < len(race_list):
                sel_race = race_list[selected_index]
                desc = race_data[sel_race].get("description", "No description available.")
                racial_mods = race_data[sel_race].get("ability_modifiers", {})

                # Build lines that only show the modifiers, e.g. "STR: +2"
                mod_lines = []
                for attr in ATTRIBUTES:
                    bonus = racial_mods.get(attr, 0)
                    sign = "+" if bonus >= 0 else ""
                    mod_lines.append(f"{attr}: {sign}{bonus}")

                # Display the race's description on the right side
                dy = 100
                screen.blit(font.render("Race Description:", True, (255, 255, 255)), (600, dy))
                dy += 30
                for line in wrap(desc, 60):
                    screen.blit(font.render(line, True, (180, 180, 255)), (600, dy))
                    dy += 25

                # Now display the race's special traits (if any)
                screen.blit(font.render("Special Traits:", True, (255, 255, 255)), (600, dy))
                dy += 30
                special_traits = race_data[sel_race].get("special_traits", [])
                if special_traits and isinstance(special_traits, list):
                    for trait in special_traits:
                        trait_type = trait.get("type", "Unknown")
                        effect = trait.get("effect") or trait.get("detail", "")
                        # Combine extras if needed
                        extras = []
                        for key, val in trait.items():
                            if key not in ("type", "effect", "detail"):
                                extras.append(f"{key}: {val}")
                        extra_str = f" ({', '.join(extras)})" if extras else ""
                        trait_line = f"{trait_type.capitalize()}: {effect}{extra_str}"
                        screen.blit(font.render(trait_line, True, (180, 180, 255)), (600, dy))
                        dy += 25
                else:
                    screen.blit(font.render("None", True, (180, 180, 255)), (600, dy))
                    dy += 25

                # Leave a little spacing, then display the ability modifiers
                dy += 10
                screen.blit(font.render("Ability Modifiers:", True, (255, 255, 255)), (600, dy))
                dy += 30
                for line in mod_lines:
                    screen.blit(font.render(line, True, (180, 180, 255)), (600, dy))
                    dy += 25

        elif current_step == "Skills":
            skill_list = list(skill_data.keys())
            sp_total = character.get("skill_points_total", 14 + character["stats"].get("INT", 0))
            sp_remaining = character.get("remaining_skill_points", sp_total)
            screen.blit(font.render(f"Total Skill Points: {sp_total}   Remaining: {sp_remaining}", True, (255,255,0)), (100, 60))
            y = 100
            visible_skills = skill_list[scroll_offset:scroll_offset+MAX_VISIBLE]
            for i, skill in enumerate(visible_skills):
                idx = i + scroll_offset
                col = (255,255,0) if idx == selected_index else (200,200,200)
                rank = character["skills"].get(skill, 0)
                ability_key = skill_data[skill].get("ability", "STR")
                base_stat = character["stats"].get(ability_key, 0)
                total_val = rank + base_stat
                line_text = f"{skill}: {rank} + {base_stat} => {total_val}"
                screen.blit(font.render(line_text, True, col), (100, y + i * 30))

        elif current_step == "Feats":
            if feat_view_mode == "categories":
                y = 100
                screen.blit(font.render("Select a Feat Category:", True, (200,255,200)), (100, 60))
                for i, cat in enumerate(feat_group_keys):
                    col = (255,255,0) if i == selected_index else (200,200,200)
                    screen.blit(font.render(cat, True, col), (100, y + i*30))
                help_text = "Press RIGHT or ENTER to view feats, BACKSPACE to go back."
                screen.blit(font.render(help_text, True, (200,255,200)), (100, y + len(feat_group_keys)*30 + 20))
            else:  # feat_view_mode == "feats"
                y = 100
                cat_header = f"Category: {current_category} (Press BACKSPACE to return)"
                screen.blit(font.render(cat_header, True, (200,255,200)), (100, 60))
                current_feats = feat_groups.get(current_category, [])
                if current_feats:
                    visible_feats = current_feats[scroll_offset:scroll_offset+MAX_VISIBLE]
                    for i, featname in enumerate(visible_feats):
                        idx = i + scroll_offset
                        col = (255,255,0) if idx == selected_index else (200,200,200)
                        prefix = "[✓]" if featname in character["feats"] else "[ ]"
                        msg = prefix + " " + featname
                        screen.blit(font.render(msg, True, col), (100, y + i*30))
                    # Show details
                    if current_feats:
                        sel_feat = current_feats[selected_index]
                        fdata = feat_index[sel_feat]
                        desc = fdata.get("description", "No description.")
                        mech = fdata.get("mechanical_description", "")
                        combined = desc + "\n" + mech
                        dy = 100
                        for line in combined.split("\n"):
                            screen.blit(font.render(line, True, (180,180,255)), (600, dy))
                            dy += 25

        elif current_step == "Name":
            screen.blit(font.render("Enter character name:", True, (255,255,255)), (100, 100))
            screen.blit(font.render(name_input, True, (255,255,0)), (100, 150))

        elif current_step == "Background":
            dy = 100
            screen.blit(font.render("Enter character background:", True, (255,255,255)), (100, dy))
            dy += 40
            for line in wrap(background_input, 80):
                screen.blit(font.render(line, True, (255,255,0)), (100, dy))
                dy += 25

        elif current_step == "Kit":
            kit_list = sorted(list(starter_kits.keys()))
            y = 100
            for i, kit in enumerate(kit_list):
                col = (255,255,0) if i == selected_index else (200,200,200)
                screen.blit(font.render(kit, True, col), (100, y + i*30))
            if kit_list and selected_index < len(kit_list):
                sel_kit = kit_list[selected_index]
                kit_data = starter_kits[sel_kit]
                contents = "\n".join(kit_data.get("items", []))
                dy = 100
                screen.blit(font.render("Kit Contents:", True, (255,255,255)), (600, dy))
                dy += 30
                for line in contents.split("\n"):
                    screen.blit(font.render(line, True, (180,180,255)), (600, dy))
                    dy += 25

        elif current_step == "Summary":
            y = 100
            combined_feats = list(set(character["feats"] + intrinsic_feats))
            character["feats"] = combined_feats
            summary_lines = [
                f"Name: {name_input}",
                f"Race: {character['race']}",
            ]
            # If we have base_stats
            if "base_stats" in character and "racial_modifiers" in character:
                base_line = "Base Stats: " + ", ".join(
                    f"{attr}: {character['base_stats'].get(attr, '---')}" for attr in ATTRIBUTES
                )
                bonus_line = "Racial Bonuses: " + ", ".join(
                    f"{attr}: {character['racial_modifiers'].get(attr, 0)}"
                    for attr in ATTRIBUTES
                )
                final_line = "Final Stats: " + ", ".join(
                    f"{attr}: {character['stats'].get(attr, '---')}" for attr in ATTRIBUTES
                )
                summary_lines.extend([base_line, bonus_line, final_line])
            else:
                stats_str = ", ".join(f"{k}: {v}" for k, v in character["stats"].items())
                summary_lines.append("Stats: " + stats_str)
            if character.get("racial_traits"):
                traits_line = "Racial Traits: " + "; ".join(
                    f"{k}: {v}" for k, v in character["racial_traits"].items()
                )
                summary_lines.append(traits_line)
            summary_lines.extend([
                f"Skills: {json.dumps(character['skills'])}",
                f"Feats: {', '.join(character['feats'])}",
                f"Starting Kit: {character.get('starting_kit') or 'None'}",
                f"Background: {(character.get('background') or '')[:100]}...",
                f"DR (from armor): {character['dr']}"
            ])
            for line in summary_lines:
                screen.blit(font.render(line, True, (255,255,255)), (100, y))
                y += 30
            screen.blit(font.render("Press ENTER to save. BACKSPACE to edit.", True, (0,255,0)), (100, y+20))

            # Check for ENTER on summary
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                try:
                    # Post to your backend
                    requests.post("http://localhost:5050/character_creator/save", json={
                        "character_name": name_input,
                        "race": character["race"],
                        "location": "0_0",
                        "known_tiles": ["0_0"],
                        "level": LEVEL,
                        "base_stats": character.get("base_stats", {}),
                        "racial_modifiers": character.get("racial_modifiers", {}),
                        "stats": character["stats"],
                        "racial_traits": character.get("racial_traits", {}),
                        "racial_description": character.get("racial_description", ""),
                        "skills": character["skills"],
                        "feats": character["feats"],
                        "starting_kit": character.get("starting_kit"),
                        "background": character.get("background") or "",
                        "dr": character["dr"]
                    }, timeout=3)
                except Exception as e:
                    logging.error(f"Error saving character: {e}")
                else:
                    # Return to main menu with next="start_game"
                    result = {"next": "start_game", "character": character}
                    running = False

        # Flip & Tick
        pygame.display.flip()
        clock.tick(30)

    print("Character creation complete.")
    if not result:
        result = {"next": "main_menu", "character": character}
    return result

if __name__ == "__main__":
    res = launch_character_creation()
    print("launch_character_creation returned:", res)
