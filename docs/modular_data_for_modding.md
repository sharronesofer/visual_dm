# Modular Data for Modding: Visual DM

To enable deep modding and world creation, all core game-defining data should be stored in JSON files. This allows modders to create new worlds, continents, or servers with custom content, using the same simulation and logic. Below is a recommended list of JSON files and their purposes.

| Category         | JSON File(s)                | Purpose/Notes                                 |
|------------------|----------------------------|-----------------------------------------------|
| Biomes/Regions   | land_types, adjacency      | World geography, biome rules                  |
| Items/Equipment  | weapons, armor, items      | All gear, loot, crafting                      |
| Creatures/NPCs   | races, npcs, factions      | All living entities, relationships            |
| Buildings/POIs   | building_types, poi_types  | Structures, dungeons, towns                   |
| Economy/Trade    | resources, trade_goods     | Economy, resources, prices                    |
| Magic/Abilities  | spells, abilities, effects | Magic, skills, status effects                 |
| Quests/Narrative | quest_templates, motifs    | Story, quests, world events                   |
| Visuals          | sprite_manifest, animation | Sprites, animations, visual mapping           |
| Dialogue         | dialogue_templates         | NPC/player dialogue, language                 |
| Combat/Rules     | combat_rules, effect_types | Mechanics, combat, special effects            |
| Worldgen         | worldgen_rules, spawn      | Procedural generation, spawn tables           |
| Religion/Diplom. | religion, diplomacy        | Religion, diplomacy, politics                 |
| Tech/Custom      | technology, custom_rules   | Tech trees, modder overrides                  |

## Long-term Vision
- Develop a modder-friendly UI with sliders, visual options, and fields for non-technical users to build worlds.
- Store all modder-created assets (sprites, templates, etc.) in a central repository for reuse in future worlds.
- The engine should read these JSONs at world/server creation and use them for all procedural and narrative generation.
- Use GPT/AI to power-balance new content and ensure compatibility with the base world.

## Modular Biome Adjacency Matrix (adjacency.json)

- Biome adjacency rules are defined in `backend/data/adjacency.json`.
- Each rule specifies two biomes, a rule type (`compatible`, `incompatible`, `transition_needed`), and optional transition biomes, minimum transition width, and weight.
- Modders can edit this file to:
  - Control which biomes can be directly adjacent
  - Require transition biomes (e.g., steppe between plains and desert)
  - Adjust coastline and beach placement by changing adjacency rules for water/land
  - Influence river placement by defining which biomes rivers can cross or border
- The adjacency matrix is loaded at runtime; changes take effect on world/server creation.
- See `Development_Bible.md` for a high-level overview and `backend/data/adjacency.json` for the canonical format.

## Coastline Smoothing and River Generation

- Coastline smoothing and beach placement logic now reference the modular adjacency matrix.
- Modders can affect coastline shape and beach frequency by editing adjacency rules for water, beach, and land biomes.
- River generation uses the adjacency matrix to determine valid river paths and transitions.
- All logic is modular and extensible; new biomes or transitions can be added without code changes.

## References
- See `Development_Bible.md` (Modular Biome Adjacency, Coastline, and River Generation Systems)
- See `backend/data/adjacency.json` for the canonical adjacency rules format

## World Seed Schema: The Canonical Entry Point

A canonical, extensible 'seeded world' JSON schema is now the primary entry point for world/continent/server definitions. This schema aggregates references to all modular data categories (biomes, items, races, etc.) and supports all must-have fields for world metadata, settings, factions, religions, regions, canon lists, narrative hooks, and extensibility.

- **Location:** See `backend/data/modding/worlds/world_seed.schema.json` for the schema and `backend/data/modding/worlds/example_world.json` for a rich example.
- **Extensibility:** All fields except `name` and at least one region/faction are optional. Modders can define as much or as little as they want; missing fields are procedurally generated or GPT-filled.
- **Integration:** The world seed file references or overrides modular JSONs for biomes, items, etc., and is supported by both backend and Unity loaders.
- **Modder Workflow:** Modders should start by copying the example file, editing fields as desired, and linking or overriding modular data as needed.

### Example Fields
- `name`, `background`, `creation_date`, `author`, `version`
- `magic_level`, `tech_level`, `dominant_races`, `climate`, `world_type`
- `factions`, `religions`, `deities`, `regions`
- `canon_races`, `canon_items`, `canon_monsters`
- `narrative_hooks`, `starting_quests`, `modder_notes`, `inspiration`, `license`, `overrides`, `custom_fields`

See the schema and example for full documentation and field-by-field explanations. 