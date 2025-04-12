import pygame
import requests
import json
import random
import re
from textwrap import wrap

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Character Creation")
font = pygame.font.SysFont(None, 30)

# Load all rules
race_data = requests.get("http://localhost:5050/rules/races").json()
class_data = requests.get("http://localhost:5050/rules/classes").json()
skill_data = requests.get("http://localhost:5050/rules/skills").json()
feat_data = requests.get("http://localhost:5050/rules/feats").json()
equipment_data = requests.get("http://localhost:5050/rules/equipment").json()
spells0 = requests.get("http://localhost:5050/rules/spells/0").json()
spells1 = requests.get("http://localhost:5050/rules/spells/1").json()
ability_rolls = requests.get("http://localhost:5050/rules/ability_scores/4d6").json()
preview_index = 0  # Highlighted row in preview
preview_returning = False  # Flag for post-edit return

# Setup globals
steps = [
    "select_race", "select_class", "allocate_stats", "confirm_stats", "choose_skills", "choose_feats",
    "choose_spells", "select_equipment", "enter_name", "write_background", 
    "preview_summary", "confirm_and_save"
]
current_step_index = 0

# Character data
base_stats = {k: 0 for k in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]}
stats = base_stats.copy()  # Final stats, includes racial modifiers after allocation
rolled_scores = sorted([r["score"] for r in ability_rolls["results"]], reverse=True)
character_data = {}

# Selection trackers
selected_race = 0
selected_class = 0
selected_stat = 0
selected_skill_index = 0
scroll_offset = 0
MAX_VISIBLE_SKILLS = 15
selected_feat_index = 0
feat_scroll_offset = 0
MAX_VISIBLE_FEATS = 15
selected_spell_index = 0
spell_scroll_offset = 0
selected_spells = []
MAX_VISIBLE_SPELLS = 15
selected_equipment_index = 0
equipment_scroll_offset = 0
MAX_VISIBLE_EQUIPMENT = 15
selected_equipment = []

# Choice storage
selected_skills = []
selected_feats = []
selected_spells = []
selected_equipment = []
name_text = ""
background_text = ""
skill_points_allocated = {}

# Class skill tracking
max_skill_points = 0
remaining_skill_points = 0
class_skills = []

# Equipment setup
armor = list(equipment_data.get("armor", {}).keys())
weapons = list(equipment_data.get("weapons", {}).keys())
gear = list(equipment_data.get("gear", {}).keys())
equipment_list = ["[ARMOR]"] + armor + ["[WEAPONS]"] + weapons + ["[GEAR]"] + gear
equipment_scroll = 0

# Gold logic
starting_gold = 0
remaining_gold = 0

# Load spell data from backend
spells0 = requests.get("http://localhost:5050/rules/spells/0").json()
spells1 = requests.get("http://localhost:5050/rules/spells/1").json()

# Flatten spell list for unified rendering
all_spells_flat = [("0", name) for name in spells0.keys()] + [("1", name) for name in spells1.keys()]

# Loaded equipment data
equipment_data = requests.get("http://localhost:5050/rules/equipment").json()

# Flatten into a master list with categories for display
equipment_store = []

for category, items in equipment_data.items():
    equipment_store.append(f"[{category.upper()}]")
    for name, details in items.items():
        cost = details.get("cost_gp", 0)
        equipment_store.append({
            "name": name,
            "category": category,
            "cost": cost,
            "description": details.get("description", "")
        })

def roll_gold(dice_expr):
    match = re.match(r"(\\d+)d(\\d+) \\* (\\d+)", dice_expr)
    if match:
        count, sides, multiplier = map(int, match.groups())
        return sum(random.randint(1, sides) for _ in range(count)) * multiplier
    return 100  # fallback default

def is_feat_available(feat_name, stats, class_data, level=1):
    prereqs = feat_data[feat_name].get("prerequisites", [])
    class_name = list(class_data.keys())[selected_class]
    class_info = class_data[class_name]

    # Extract base attack bonus
    bab_progression = class_info.get("base_attack_bonus", "medium")
    bab = 0
    if bab_progression == "full":
        bab = level
    elif bab_progression == "medium":
        bab = level * 0.75
    elif bab_progression == "low":
        bab = level * 0.5

    spellcaster = class_info.get("is_spellcaster", False)

    for prereq in prereqs:
        if prereq.startswith("Str "):
            if stats["STR"] < int(prereq.split()[1]):
                return False
        elif prereq.startswith("Dex "):
            if stats["DEX"] < int(prereq.split()[1]):
                return False
        elif prereq.startswith("Con "):
            if stats["CON"] < int(prereq.split()[1]):
                return False
        elif prereq.startswith("Int "):
            if stats["INT"] < int(prereq.split()[1]):
                return False
        elif prereq.startswith("Wis "):
            if stats["WIS"] < int(prereq.split()[1]):
                return False
        elif prereq.startswith("Cha "):
            if stats["CHA"] < int(prereq.split()[1]):
                return False
        elif prereq.startswith("Base attack bonus"):
            if bab < int(prereq.split("+")[1]):
                return False
        elif prereq.startswith("Spellcaster level"):
            required_level = int(prereq.split()[2][:-2])  # e.g., "9th" → 9
            if not spellcaster or level < required_level:
                return False
        else:
            # For now, skip unknown prereqs like "Proficiency with weapon"
            continue
    return True

# UI Flags
MAX_BACKGROUND_LENGTH = 10000
WRAP_WIDTH = 70
running = True
while running:
    screen.fill((25, 25, 60))
    if current_step_index >= len(steps):
        break

    step = steps[current_step_index]
    screen.blit(font.render(f"Step: {step}", True, (255, 255, 255)), (50, 30))

    if step == "select_race":
        races = list(race_data.keys())

        # Draw race list
        for i, race in enumerate(races):
            color = (255, 255, 0) if i == selected_race else (200, 200, 200)
            screen.blit(font.render(race, True, color), (100, 100 + i * 30))

        # Extract race details
        selected_name = races[selected_race]
        race_info = race_data[selected_name]

        # Wrap and show description
        y_offset = 100
        for i, line in enumerate(wrap(race_info["description"], 40)):
            screen.blit(font.render(line, True, (180, 180, 255)), (400, y_offset + i * 20))
        y_offset += (len(wrap(race_info["description"], 40)) + 1) * 20

        # Show ability modifiers
        mods = race_info.get("ability_modifiers", {})
        if mods:
            mod_text = ", ".join([f"{stat} {'+' if val >= 0 else ''}{val}" for stat, val in mods.items()])
            screen.blit(font.render(f"Ability Modifiers: {mod_text}", True, (200, 255, 200)), (400, y_offset))
            y_offset += 25

        # Show skill bonuses
        skills = race_info.get("skill_bonuses", {})
        if skills:
            skill_text = ", ".join([f"{skill} +{val}" for skill, val in skills.items()])
            screen.blit(font.render(f"Skill Bonuses: {skill_text}", True, (255, 200, 200)), (400, y_offset))
            y_offset += 25

        # Show traits
        traits = race_info.get("traits", [])
        if traits:
            screen.blit(font.render("Traits:", True, (255, 255, 200)), (400, y_offset))
            y_offset += 20
            for trait in traits:
                for line in wrap(trait, 40):
                    screen.blit(font.render(f"- {line}", True, (255, 255, 200)), (420, y_offset))
                    y_offset += 20

    elif step == "select_class":
        classes = list(class_data.keys())

        # Render class names
        for i, cls in enumerate(classes):
            color = (255, 255, 0) if i == selected_class else (200, 200, 200)
            screen.blit(font.render(cls, True, color), (100, 100 + i * 30))

        # Show class description
        class_name = classes[selected_class]
        desc = class_data[class_name].get("description", "")
        for j, line in enumerate(wrap(desc, 40)):
            screen.blit(font.render(line, True, (180, 255, 180)), (400, 100 + j * 20))

        # Show level 1 features (optional)
        features = class_data[class_name].get("features", {}).get("1", [])
        if features:
            screen.blit(font.render("Level 1 Features:", True, (255, 255, 200)), (400, 220))
            for i, line in enumerate(wrap(" | ".join(features), 40)):
                screen.blit(font.render(line, True, (200, 200, 255)), (400, 250 + i * 20))

    elif step == "allocate_stats":
        screen.blit(font.render("Use ← → to assign scores", True, (180, 180, 180)), (100, 80))
        for i, stat in enumerate(base_stats.keys()):
            val = base_stats[stat]
            color = (255, 255, 0) if i == selected_stat else (200, 200, 200)
            screen.blit(font.render(f"{stat}: {val if val else '-'}", True, color), (100, 120 + i * 30))
        screen.blit(font.render(f"Available Scores: {rolled_scores}", True, (180, 255, 255)), (100, 320))

    elif step == "confirm_stats":
        screen.blit(font.render("Final Stats (after racial bonus):", True, (255, 255, 255)), (100, 80))
        y_offset = 120
        for stat in stats:
            screen.blit(font.render(f"{stat}: {stats[stat]}", True, (255, 255, 0)), (100, y_offset))
            y_offset += 30

        screen.blit(font.render("Press Enter to continue, or Backspace to go back.", True, (200, 200, 200)), (100, y_offset + 20))

    elif step == "choose_skills":
        skill_list = list(skill_data.keys())
        class_skill_names = class_skills
        visible_skills = skill_list[scroll_offset:scroll_offset + MAX_VISIBLE_SKILLS]

        screen.blit(font.render(f"Remaining Skill Points: {remaining_skill_points}", True, (255, 255, 0)), (100, 80))

        for i, skill in enumerate(visible_skills):
            is_class = skill in class_skill_names
            cost = 1 if is_class else 2
            points = skill_points_allocated.get(skill, 0)
            color = (255, 255, 0) if i == (selected_skill_index - scroll_offset) else (200, 200, 200)
            line = f"{skill} - {points} pts ({'Class' if is_class else 'Cross'}) [{cost}pt/level]"
            screen.blit(font.render(line, True, color), (100, 120 + i * 25))

    elif step == "choose_feats":
        all_feats = list(feat_data.keys())
        visible_feats = all_feats[feat_scroll_offset:feat_scroll_offset + MAX_VISIBLE_FEATS]

        screen.blit(font.render("Select a feat (→ to pick, Enter to confirm)", True, (255, 255, 0)), (100, 80))

        for i, feat in enumerate(visible_feats):
            color = (255, 255, 0) if i == (selected_feat_index - feat_scroll_offset) else (200, 200, 200)
            prefix = "[✓] " if feat in selected_feats else "[ ] "
            screen.blit(font.render(prefix + feat, True, color), (100, 120 + i * 25))

        if visible_feats:
            desc = feat_data[visible_feats[selected_feat_index - feat_scroll_offset]].get("benefit", "")
            for j, line in enumerate(wrap(desc, 40)):
                screen.blit(font.render(line, True, (180, 180, 255)), (500, 120 + j * 20))

    elif step == "choose_spells":
        spell_list_0 = list(spells0.keys())
        spell_list_1 = list(spells1.keys())
        all_spells_flat = [("0", name) for name in spell_list_0] + [("1", name) for name in spell_list_1]

        visible_spells = all_spells_flat[spell_scroll_offset:spell_scroll_offset + MAX_VISIBLE_SPELLS]

        # Show header
        screen.blit(font.render("Select spells (→ to pick, Enter to continue)", True, (255, 255, 0)), (100, 60))

        # Load max spells based on class
        class_name = list(class_data.keys())[selected_class]
        spell_limits = class_data[class_name].get("spells_known_at_level_1", {})
        max_0 = spell_limits.get("0", 0)
        max_1 = spell_limits.get("1", 0)
        screen.blit(font.render(f"0th: {max_0} | 1st: {max_1}", True, (180, 255, 255)), (100, 85))

        for i, (lvl, spell) in enumerate(visible_spells):
            is_selected = spell in selected_spells
            color = (255, 255, 0) if i == (selected_spell_index - spell_scroll_offset) else (200, 200, 200)
            prefix = "[✓] " if is_selected else "[ ] "
            label = f"{prefix}({lvl}) {spell}"
            screen.blit(font.render(label, True, color), (100, 120 + i * 25))

        # Show spell description
        if visible_spells:
            selected_level, selected_name = visible_spells[selected_spell_index - spell_scroll_offset]
            spell_data = (spells0 if selected_level == "0" else spells1).get(selected_name, {})
            description = spell_data.get("description", "No description available.")
            for j, line in enumerate(wrap(description, 50)):
                screen.blit(font.render(line, True, (180, 180, 255)), (600, 120 + j * 20))

    elif step == "select_equipment":
        visible_items = equipment_store[equipment_scroll_offset:equipment_scroll_offset + MAX_VISIBLE_EQUIPMENT]

        screen.blit(font.render("Buy Equipment (→ to buy/sell, Enter to finish)", True, (255, 255, 0)), (100, 60))
        screen.blit(font.render(f"Gold Remaining: {remaining_gold:.2f} gp", True, (180, 255, 255)), (100, 90))

        for i, item in enumerate(visible_items):
            y = 120 + i * 25
            if isinstance(item, str):  # section header
                screen.blit(font.render(item, True, (150, 150, 150)), (100, y))
            else:
                is_selected = item["name"] in selected_equipment
                color = (255, 255, 0) if i == (selected_equipment_index - equipment_scroll_offset) else (200, 200, 200)
                prefix = "[✓] " if is_selected else "[ ] "
                label = f"{prefix}{item['name']} - {item['cost']} gp"
                screen.blit(font.render(label, True, color), (100, y))

        # Show item description
        try:
            hovered = visible_items[selected_equipment_index - equipment_scroll_offset]
            if isinstance(hovered, dict):
                desc = hovered.get("description", "")
                for j, line in enumerate(wrap(desc, 50)):
                    screen.blit(font.render(line, True, (180, 180, 255)), (600, 120 + j * 20))
        except:
            pass

    elif step == "enter_name":
        screen.blit(font.render("Enter character name:", True, (255, 255, 255)), (100, 100))
        screen.blit(font.render(name_text, True, (255, 255, 0)), (100, 150))

    elif step == "write_background":
        screen.blit(font.render("Background (Enter to finish):", True, (255, 255, 255)), (100, 80))
        wrapped = wrap(background_text, WRAP_WIDTH)
        for i, line in enumerate(wrapped[-10:]):
            screen.blit(font.render(line, True, (255, 255, 0)), (100, 120 + i * 25))

    elif step == "preview_summary":
        screen.fill((15, 15, 40))
        screen.blit(font.render("Character Summary (↑/↓ to highlight, Enter to edit, S to Save)", True, (255, 255, 255)), (50, 30))

        preview_lines = [
            f"Name: {name_text}",
            f"Race: {list(race_data.keys())[selected_race]}",
            f"Class: {list(class_data.keys())[selected_class]}",
            "Stats: " + ", ".join([f"{k}: {v}" for k, v in stats.items()]),
            f"Skills: {', '.join(selected_skills)}",
            f"Feats: {', '.join(selected_feats)}",
            f"Spells: {', '.join(selected_spells)}",
            f"Equipment: {', '.join(selected_equipment)}",
            f"Background: {background_text[:60]}..." if len(background_text) > 60 else f"Background: {background_text}"
    ]

        for i, line in enumerate(preview_lines):
            color = (255, 255, 0) if i == preview_index else (200, 200, 200)
            screen.blit(font.render(f"{i+1}. {line}", True, color), (80, 80 + i * 30))

    footer = f"Unspent: {remaining_gold} gp | {remaining_skill_points} skill pts | {1 if not selected_feats else 0} feats"
    screen.blit(font.render(footer, True, (180, 255, 255)), (80, 600))
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if step == "select_race":
                if event.key == pygame.K_DOWN:
                    selected_race = (selected_race + 1) % len(race_data)
                elif event.key == pygame.K_UP:
                    selected_race = (selected_race - 1) % len(race_data)
                elif event.key == pygame.K_RETURN:
                    # Apply racial modifiers
                    race = list(race_data.keys())[selected_race]
                    for stat, mod in race_data[race].get("ability_modifiers", {}).items():
                        stats[stat] += mod
                    current_step_index += 1
                    if preview_returning:
                        current_step_index = steps.index("preview_summary")
                        preview_returning = False

            elif step == "select_class":
                class_names = list(class_data.keys())

                if event.key == pygame.K_DOWN:
                    selected_class = (selected_class + 1) % len(class_names)

                elif event.key == pygame.K_UP:
                    selected_class = (selected_class - 1) % len(class_names)

                elif event.key == pygame.K_RETURN:
                    # Setup class-based state
                    chosen_class = class_names[selected_class]
                    class_info = class_data[chosen_class]

                    # Calculate skill points
                    int_mod = max((stats["INT"] - 10) // 2, 0)
                    max_skill_points = class_info.get("skill_points_per_level", 4) + int_mod
                    remaining_skill_points = max_skill_points

                    class_skills = class_info.get("class_skills", [])

                    # Roll starting gold
                    starting_gold_expr = class_info.get("starting_gold_dice", "4d4 * 10")
                    remaining_gold = roll_gold(starting_gold_expr)

                    current_step_index += 1
                    if preview_returning:
                        current_step_index = steps.index("preview_summary")
                        preview_returning = False

                elif event.key == pygame.K_n:
                    current_step_index += 1  # Manual skip (dev/debug shortcut)


            elif step == "allocate_stats":
                if event.key == pygame.K_DOWN:
                    selected_stat = (selected_stat + 1) % len(base_stats)
                elif event.key == pygame.K_UP:
                    selected_stat = (selected_stat - 1) % len(base_stats)
                elif event.key == pygame.K_RIGHT and rolled_scores:
                    stat_key = list(base_stats.keys())[selected_stat]
                    if base_stats[stat_key] == 0:
                        base_stats[stat_key] = rolled_scores.pop(0)
                elif event.key == pygame.K_LEFT:
                    stat_key = list(base_stats.keys())[selected_stat]
                    if base_stats[stat_key] > 0:
                        rolled_scores.append(base_stats[stat_key])
                        base_stats[stat_key] = 0
                        rolled_scores.sort(reverse=True)
                elif event.key == pygame.K_RETURN:
                    if all(base_stats[k] > 0 for k in base_stats):
                        # Apply racial modifiers now
                        stats = base_stats.copy()
                        race = list(race_data.keys())[selected_race]
                        for stat, mod in race_data[race].get("ability_modifiers", {}).items():
                            stats[stat] += mod
                        current_step_index = steps.index("confirm_stats")
                        if preview_returning:
                            current_step_index = steps.index("preview_summary")
                            preview_returning = False

            elif step == "confirm_stats":
                if event.key == pygame.K_RETURN:
                    current_step_index += 1
                    if preview_returning:
                        current_step_index = steps.index("preview_summary")
                        preview_returning = False
                elif event.key == pygame.K_BACKSPACE:
                    current_step_index = steps.index("allocate_stats")

            elif step == "choose_feats":
                feat_list = list(feat_data.keys())

                if event.key == pygame.K_DOWN:
                    if selected_feat_index < len(feat_list) - 1:
                        selected_feat_index += 1
                        if selected_feat_index >= feat_scroll_offset + MAX_VISIBLE_FEATS:
                            feat_scroll_offset += 1

                elif event.key == pygame.K_UP:
                    if selected_feat_index > 0:
                        selected_feat_index -= 1
                        if selected_feat_index < feat_scroll_offset:
                            feat_scroll_offset -= 1

                elif event.key == pygame.K_RIGHT:
                    selected = feat_list[selected_feat_index]
                    if not selected_feats:
                        selected_feats.append(selected)
                    elif selected in selected_feats:
                        selected_feats.remove(selected)

                elif event.key == pygame.K_RETURN:
                    if selected_feats:
                        current_step_index += 1
                        if preview_returning:
                            current_step_index = steps.index("preview_summary")
                            preview_returning = False


            elif step == "choose_skills":
                skill_list = list(skill_data.keys())
                current_skill = skill_list[selected_skill_index]
                is_class = current_skill in class_skills
                cost = 1 if is_class else 2

                if event.key == pygame.K_DOWN:
                    if selected_skill_index < len(skill_list) - 1:
                        selected_skill_index += 1
                        if selected_skill_index >= scroll_offset + MAX_VISIBLE_SKILLS:
                            scroll_offset += 1

                elif event.key == pygame.K_UP:
                    if selected_skill_index > 0:
                        selected_skill_index -= 1
                        if selected_skill_index < scroll_offset:
                            scroll_offset -= 1

                elif event.key == pygame.K_RIGHT:
                    points = skill_points_allocated.get(current_skill, 0)
                    if remaining_skill_points >= cost:
                        skill_points_allocated[current_skill] = points + 1
                        remaining_skill_points -= cost

                elif event.key == pygame.K_LEFT:
                    points = skill_points_allocated.get(current_skill, 0)
                    if points > 0:
                        skill_points_allocated[current_skill] = points - 1
                        remaining_skill_points += cost
                        if skill_points_allocated[current_skill] == 0:
                            del skill_points_allocated[current_skill]

                elif event.key == pygame.K_RETURN:
                    selected_skills.clear()
                    for skill, pts in skill_points_allocated.items():
                        selected_skills.extend([skill] * pts)
                    current_step_index += 1
                    if preview_returning:
                        current_step_index = steps.index("preview_summary")
                        preview_returning = False

            elif step == "choose_spells":
                spell_list_0 = list(spells0.keys())
                spell_list_1 = list(spells1.keys())
                all_spells_flat = [("0", name) for name in spell_list_0] + [("1", name) for name in spell_list_1]

                if event.key == pygame.K_DOWN:
                    if selected_spell_index < len(all_spells_flat) - 1:
                        selected_spell_index += 1
                        if selected_spell_index >= spell_scroll_offset + MAX_VISIBLE_SPELLS:
                            spell_scroll_offset += 1

                elif event.key == pygame.K_UP:
                    if selected_spell_index > 0:
                        selected_spell_index -= 1
                        if selected_spell_index < spell_scroll_offset:
                            spell_scroll_offset -= 1

                elif event.key == pygame.K_RIGHT:
                    lvl, spell = all_spells_flat[selected_spell_index]
                    level_selected = [s for s in selected_spells if (s in spells0 if lvl == "0" else s in spells1)]

                    # Get cap from class data
                    class_name = list(class_data.keys())[selected_class]
                    spell_limits = class_data[class_name].get("spells_known_at_level_1", {})
                    max_per_level = spell_limits.get(lvl, 0)

                    if spell in selected_spells:
                        selected_spells.remove(spell)
                    elif len(level_selected) < max_per_level:
                        selected_spells.append(spell)

                elif event.key == pygame.K_RETURN:
                    # Done selecting spells
                    current_step_index += 1
                    if preview_returning:
                        current_step_index = steps.index("preview_summary")
                        preview_returning = False


            elif step == "select_equipment":
                if event.key == pygame.K_DOWN:
                    if selected_equipment_index < len(equipment_list) - 1:
                        selected_equipment_index += 1
                        if selected_equipment_index >= equipment_scroll_offset + MAX_VISIBLE_EQUIPMENT:
                            equipment_scroll_offset += 1

                elif event.key == pygame.K_UP:
                    if selected_equipment_index > 0:
                        selected_equipment_index -= 1
                        if selected_equipment_index < equipment_scroll_offset:
                            equipment_scroll_offset -= 1

                elif event.key == pygame.K_RIGHT:
                    item = equipment_list[selected_equipment_index]
                    if not item.startswith("["):
                        if item in selected_equipment:
                            selected_equipment.remove(item)
                        elif len(selected_equipment) < 6:
                            selected_equipment.append(item)

                elif event.key == pygame.K_RETURN:
                    current_step_index += 1
                    if preview_returning:
                        current_step_index = steps.index("preview_summary")
                        preview_returning = False


            elif step == "enter_name":
                if event.key == pygame.K_RETURN:
                    current_step_index += 1
                elif event.key == pygame.K_BACKSPACE:
                    name_text = name_text[:-1]
                elif len(name_text) < 25 and event.unicode.isprintable():
                    name_text += event.unicode
                if preview_returning:
                    current_step_index = steps.index("preview_summary")
                    preview_returning = False
    
            elif step == "preview_summary":
                if event.key == pygame.K_DOWN:
                    preview_index = (preview_index + 1) % 9
                elif event.key == pygame.K_UP:
                    preview_index = (preview_index - 1) % 9
                elif event.key == pygame.K_RETURN:
                    preview_returning = True
                    step_map = [
                        "enter_name", "select_race", "select_class", "allocate_stats",
                        "choose_skills", "choose_feats", "choose_spells", "select_equipment",
                        "write_background"
                    ]
                    current_step_index = steps.index(step_map[preview_index])
                elif event.key == pygame.K_s:
                    current_step_index = steps.index("confirm_and_save")

            elif step == "write_background":
                if event.key == pygame.K_RETURN:
                    current_step_index += 1
                elif event.key == pygame.K_BACKSPACE:
                    background_text = background_text[:-1]
                elif len(background_text) < MAX_BACKGROUND_LENGTH and len(event.unicode) == 1 and event.unicode.isprintable():
                    background_text += event.unicode
                if preview_returning:
                    current_step_index = steps.index("preview_summary")
                    preview_returning = False

            elif step == "choose_feats":
                visible_feats = list(feat_data.keys())[selected_feat:selected_feat + 15]
                for i, feat in enumerate(visible_feats):
                    color = (255, 255, 0) if i == 0 else (200, 200, 200)
                    prefix = "[✓] " if feat in selected_feats else "[ ] "
                    screen.blit(font.render(prefix + feat, True, color), (100, 120 + i * 25))

            elif step == "choose_spells":
                visible_spells = list(spells0.keys()) + list(spells1.keys())
                visible = visible_spells[selected_spell:selected_spell + 15]
                for i, spell in enumerate(visible):
                    prefix = "[✓] " if spell in selected_spells else "[ ] "
                    screen.blit(font.render(prefix + spell, True, (255, 255, 0) if i == 0 else (200, 200, 200)), (100, 120 + i * 25))

            elif step == "select_equipment":
                screen.blit(font.render(f"Gold Remaining: {remaining_gold} gp", True, (255, 255, 255)), (100, 60))
                visible = equipment_list[selected_equipment_index:selected_equipment_index + 15]
                for i, item in enumerate(visible):
                    if item.startswith("["):
                        screen.blit(font.render(item, True, (150, 150, 150)), (100, 120 + i * 25))
                    else:
                        tag = "[✓]" if item in selected_equipment else "[ ]"
                        screen.blit(font.render(f"{tag} {item}", True, (255, 255, 0) if i == 0 else (200, 200, 200)), (100, 120 + i * 25))

            elif step == "confirm_and_save":
                screen.blit(font.render("Saving character...", True, (0, 255, 0)), (100, 100))
                character_data.update({
                    "name": name_text,
                    "race": list(race_data.keys())[selected_race],
                    "class": list(class_data.keys())[selected_class],
                    "stats": stats,
                    "skills": selected_skills,
                    "feats": selected_feats,
                    "spells": selected_spells,
                    "equipment": selected_equipment,
                    "background": background_text,
                    "unspent_gold": remaining_gold,
                    "unspent_skill_points": remaining_skill_points,
                    "unassigned_feats": 1 if not selected_feats else 0
                })
                requests.post("http://localhost:5050/character_creator/save", json=character_data)

pygame.quit()
print("Character creation complete.")