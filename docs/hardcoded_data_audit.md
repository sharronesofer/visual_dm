# Hardcoded Data Audit: Visual DM

This document inventories all hardcoded game data that should be modularized into JSON files for modding, as per Task 753. Each entry includes the data type, current file location(s), line numbers (if applicable), and a brief description. Categories are based on `modular_data_for_modding.md` and canonical lists in `Development_Bible.md`.

---

## Audit Table

| Category         | Data Type         | File(s) / Location(s)                        | Line(s) / Example | Description / Notes |
|------------------|-------------------|----------------------------------------------|-------------------|---------------------|
| Biomes/Regions   | land_types        | backend/app/models/region_tile.py            | terrain_type      | Biome tags for regions/tiles |
| Biomes/Regions   | adjacency         | data/system/runtime/adjacency.json                  | -                 | Modular adjacency matrix (already modular) |
| Items/Equipment  | weapons           | backend/app/models/weapon.py                 | class Weapon      | Weapon definitions (dataclass, hardcoded) |
| Items/Equipment  | armor             | backend/app/models/equipment.py              | class Equipment   | Armor/equipment types, hardcoded fields |
| Items/Equipment  | items             | backend/app/models/item.py                   | class Item, enums | Item types, rarities, properties |
| Creatures/NPCs   | races             | data/system/runtime/models/races.py                 | -                 | Race definitions (Python, not modular JSON) |
| Creatures/NPCs   | npcs              | backend/app/models/npc.py                    | class NPC         | NPC archetypes, traits, etc. |
| Creatures/NPCs   | factions          | backend/app/models/faction.py                | class Faction     | Faction types, minimal stub |
| Buildings/POIs   | building_types    | backend/app/models/location.py               | LocationType enum | Building/POI types |
| Buildings/POIs   | poi_types         | backend/app/models/location.py               | LocationType enum | POI types (city, dungeon, etc.) |
| Economy/Trade    | resources         | backend/app/models/market_item.py            | -                 | Resource types, trade goods |
| Economy/Trade    | trade_goods       | backend/app/models/market_item.py            | -                 | Trade goods, item types |
| Magic/Abilities  | spells            | backend/app/models/character_skills.py       | -                 | Spell/ability definitions |
| Magic/Abilities  | abilities         | backend/app/models/character_skills.py       | -                 | Ability definitions |
| Magic/Abilities  | effects           | backend/app/models/item.py                   | usage_effects      | Item/magic effects |
| Quests/Narrative | quest_templates   | backend/app/models/quest.py                  | stages/objectives | Quest structure, templates |
| Quests/Narrative | motifs            | backend/app/models/motifs.py                 | class Motif       | Motif types, data |
| Visuals          | sprite_manifest   | (TBD: likely in Unity/VDM/Assets/Scripts)    | -                 | Sprite mapping, not yet modular |
| Visuals          | animation         | (TBD: likely in Unity/VDM/Assets/Scripts)    | -                 | Animation data |
| Dialogue         | dialogue_templates| backend/app/models/dialogue.py               | -                 | Dialogue templates, not modular |
| Combat/Rules     | combat_rules      | backend/app/models/weapon.py, item.py        | -                 | Combat mechanics, damage types |
| Combat/Rules     | effect_types      | backend/app/models/item.py                   | usage_effects      | Effect types, not modular |
| Worldgen         | worldgen_rules    | backend/app/models/world.py                  | settings          | Worldgen config, not modular |
| Worldgen         | spawn             | backend/app/models/npc.py                    | -                 | NPC spawn logic |
| Religion/Diplom. | religion          | backend/app/models/faction.py                | -                 | Religion types, not modular |
| Religion/Diplom. | diplomacy         | backend/app/models/faction.py                | -                 | Diplomacy types, not modular |
| Tech/Custom      | technology        | (TBD: check for tech trees, custom rules)    | -                 | Technology, custom rules |

---

## Notes
- Some data (e.g., adjacency.json) is already modular.
- Many enums and dataclasses in models/ are hardcoded and must be migrated.
- Unity-side visuals (sprites, animation) will require a separate audit in VDM/Assets/Scripts/.
- This audit will be updated as new data types are discovered or as migration progresses.

## Next Steps
- Design canonical JSON schemas for each category.
- Migrate all hardcoded data to data/builders/ as JSON files.
- Refactor code to load from modular data files.
- Validate all data against schemas.
- Update documentation and tests. 