## Region System (Consolidated)

The Region system models the narrative and mechanical structure of a world region, supporting dynamic control, memory, motifs, and arcs. This system is designed per the requirements in `docs/stubs_needs_consolidation_qna.md` and is implemented in `backend/world/world_models.py` and region generation utilities.

### Data Model Fields
- **id**: Unique region identifier.
- **name, description**: Human-readable fields.
- **level_range**: Tuple of (min, max) level for encounters/content.
- **terrain_types**: List of terrain types present.
- **points_of_interest**: List of POI IDs in the region.
- **factions**: List of controlling/influential faction IDs.
- **climate**: Climate descriptor.
- **primary_capitol_id**: ID of the original (birth) capitol city. Never changes; used for historical reference.
- **secondary_capitol_id**: ID of the current controlling capitol city. Changes with conquest or revolt.
- **metropolis_type**: One of Arcane, Industrial, Sacred, Ruined, Natural. Assigned at creation if a metropolis exists; never changes.
- **motif_pool**: List of 3 unique active motif IDs. Motifs are narrative drivers, hidden from the player, and rotate out as their duration expires.
- **motif_history**: List of previously assigned motifs for narrative tracking.
- **memory**: List of memory/core memory objects for major events. Summarized at daily, weekly, monthly, and annual intervals. Core memories are never summarized further.
- **arc**: ID of the current active arc (meta-quest). Only one arc per region at a time; must resolve/fail before a new one starts.
- **arc_history**: List of resolved/failed arcs for the region.
- **history**: List of major region events (capitol changes, arc failures, tension spikes, etc.).
- **population**: Total region population, used for city/POI generation.
- **tension_level**: Current tension (0-100) between factions in the region.

### Motif System
- Each region has 3 unique active motifs, drawn from a canonical set. Motifs have entropy/decay and rotate out when their duration expires. Motif history is tracked for narrative purposes. See `motif_utils.py` and `motif_engine_class.py` for implementation details.

### Memory System
- Region memory logs all major events (capitol changes, arc failures, etc.). Memories are summarized at daily, weekly, monthly, and annual intervals. Core memories are created for major events and are not summarized further. See `memory_utils.py` for summarization and core memory logic.

### Arc System
- Only one arc (meta-quest) per region at a time. Arcs must resolve or fail before a new one starts. Arc failures and completions are logged as core memories. See `arcs_class.py` and `player_arc_utils.py` for arc management.

### Metropolis and Capitol Rules
- A region can have more than one metropolis, but the largest is always the capitol. Metropolis type is assigned at creation and never changes. The original (primary) capitol is a historical note; the current (secondary) capitol changes with conquest or revolt.

### Event Hooks
- All major system changes (capitol change, arc failure, tension spike) are logged in region memory and a central world history for analytics or narrative purposes.

### References
- See `docs/stubs_needs_consolidation_qna.md` for Q&A clarifications and rationale.
- See `backend/world/world_models.py` for the canonical data model.
- See `archives/unzips/Backend/regions/region_generation_utils.py` for procedural region generation logic.

## Motif System (Consolidated)

The Motif system provides narrative drivers for regions and NPCs, supporting dynamic worldbuilding and emergent storytelling. Motifs are hidden from the player and used for narrative generation only.

### Canonical Motif Pool
- There is a canonical set of 50 motifs (see `CANONICAL_MOTIFS` in `motif_utils.py`).

### Motif Assignment
- Each region and NPC has a motif pool of 3 unique active motifs at a time.
- Motifs are assigned randomly from the canonical pool, ensuring uniqueness within the pool.
- Motifs are not locked and rotate out when their duration expires.

### Motif Lifecycle
- Each motif has:
  - **theme**: The motif's narrative theme (e.g., "Betrayal").
  - **intensity**: 1-6, determines narrative pressure and duration.
  - **duration**: 7 - intensity (e.g., intensity 6 = 1 week duration).
  - **entropy_tick**: Increments each tick; when it reaches duration, the motif rotates out.
  - **weight**: Same as intensity; used for narrative escalation.
- Motif history is tracked for each region/NPC for narrative reference.

### Motif Rotation
- Expired motifs are added to motif history and replaced with new unique motifs.
- Motif pools are always kept at 3 unique active motifs.
- Motif rotation and tick logic are implemented in `motif_utils.py` and `motif_engine_class.py`.

### Integration
- Motif pools and history are attached to region and NPC data models.
- Motif changes are triggered by world ticks, chaos events, or narrative hooks.

### References
- See `backend/motifs/motif_utils.py` for canonical motif pool and lifecycle logic.
- See `backend/motifs/motif_engine_class.py` for motif engine and tick/rotation logic.
- See `docs/stubs_needs_consolidation_qna.md` for Q&A clarifications and rationale.

## Memory System (Consolidated)

The Memory system tracks and summarizes major events for regions, factions, NPCs, and the world, providing a historical record for narrative and gameplay systems.

### Core Memory Determination
- Core memories are logged for major events (e.g., party/faction join/leave, arc completion, war, capitol change).
- Core memories are never summarized further and serve as permanent historical records.
- Core memory logging is handled by utility functions (see `log_permanent_memory`, `update_faction_memory`, `update_region_memory` in `memory_utils.py`).

### Memory Summarization
- Memories are summarized at regular intervals:
  - **Daily**: Short-term events are logged.
  - **Weekly (7 days)**: Daily logs are summarized and purged for factions.
  - **Monthly (4 weeks/28 days)**: Daily logs are summarized and purged for regions.
  - **Annual (12 months)**: Annual summaries are the final, non-summarized record.
- Summarization logic is implemented in `memory_utils.py` and can be triggered by event hooks or scheduled jobs.

### Event Hooks and Integration
- Memory logs and summaries are attached to region, faction, NPC, and world data models.
- All major system changes (capitol change, arc failure, tension spike, war, membership changes) are logged in memory and a central world history for analytics or narrative purposes.
- Event hooks ensure that memory is updated whenever a significant event occurs.

### GPT-Based Summarization and Belief Generation
- Some summarization and belief generation is handled by GPT (see `generate_beliefs_from_meta_summary` in `memory_utils.py`).
- GPT is used to generate natural language summaries and extract beliefs from memory logs for richer narrative context.

### References
- See `archives/Unzips/Backend/memory/memory_utils.py` for core memory, summarization, and event logging logic.
- See `docs/stubs_needs_consolidation_qna.md` for Q&A clarifications and rationale.

## Arc System (Consolidated)

The Arc system manages major narrative arcs (meta-quests) for regions and player characters, providing structure for world events and story progression.

### Arc Management
- Each region has only one active arc (meta-quest) at a time.
- Arcs must resolve or fail before a new one can start; no pausing or overlapping arcs.
- Arc failures and completions are logged as core memories in the region's memory log.
- Arc and arc history fields are included in the region data model:
  - **arc**: ID or data for the current active arc.
  - **arc_history**: List of resolved/failed arcs for the region.

### Player and Sub-Arcs
- Player-specific arcs are managed by the `PlayerArc` class and related utilities.
- Sub-arcs and subquests can be generated as needed, but only one main arc per region is active at a time.

### Event Hooks and Integration
- Arc changes (resolution, failure) trigger event hooks that log core memories and may update motif pools or trigger new narrative events.
- Arc system integrates with the memory and motif systems for narrative consistency.

### References
- See `archives/Unzips/Backend/quests/arcs_class.py` for the PlayerArc class and arc management logic.
- See `archives/Unzips/Backend/quests/player_arc_utils.py` for arc utilities and event handling.
- See `docs/stubs_needs_consolidation_qna.md` for Q&A clarifications and rationale.

## Population and City System (Consolidated)

The Population and City system governs the creation and expansion of cities and metropolises within regions, driven by population and narrative logic.

### City and Metropolis Creation
- Cities are created as Social POIs if population and POI type requirements are met.
- New cities are founded one at a time until the region's population is "used up."
- The number of cities per region is open-ended and determined by available population.
- Metropolises are assigned a type at creation (Arcane, Industrial, Sacred, Ruined, Natural) and this type never changes.
- The largest metropolis is always the capitol; a region can have more than one metropolis, but this is rare.

### Population-Driven Expansion
- Population is updated by world tick utilities (birth, death, migration).
- Social POI (city) expansion is driven by population pressure; as population grows, new cities may be founded.
- City/POI creation logic is implemented in `poi_building_utils.py`.

### Integration
- Population, city list, and metropolis type are fields in the region data model.
- City and metropolis creation is triggered by population changes and narrative events.

### References
- See `backend/pois/poi_building_utils.py` for city and metropolis creation logic.
- See `docs/stubs_needs_consolidation_qna.md` for Q&A clarifications and rationale.

## Faction System (Consolidated)

The Faction system models the narrative and mechanical structure of organizations, groups, and power blocs in the world. This system is designed per the requirements in `docs/stubs_needs_consolidation_qna.md` and is implemented in `backend/models/faction.py` and faction utility modules.

### Data Model Fields
- **name, description**: Faction name and lore.
- **alignment**: Alignment (see FactionAlignment enum).
- **type**: Faction type (guild, kingdom, tribe, etc.).
- **leader_id, leadership_structure**: Current leader and leadership roles/members.
- **parent_faction_id**: Parent/superior faction.
- **headquarters_id**: HQ location.
- **territories**: List of controlled territory IDs.
- **resources**: Dict of resources and states.
- **members**: List of member NPC IDs.
- **required_reputation_join**: Minimum reputation to join.
- **reputation_levels**: Dict of reputation thresholds/labels.
- **wealth, income, expenses, tax_rate**: Economic data.
- **relationships**: Dict of relationships with other factions.
- **goals**: List of goals/objectives.
- **culture**: Dict of values, traditions, etc.
- **is_active**: Whether the faction is active.
- **influence**: World influence (0-100).
- **founding_date**: Date of founding.
- **major_events**: List of significant events.
- **tension**: Dict of tension scores with other factions (0-100).
- **war_state**: Dict of current war/conflict state.
- **affinity**: Dict of affinity scores for NPCs/members.
- **rumors**: List of rumors known to the faction.
- **truth_scores**: Dict of rumor truth scores.
- **membership_logic**: Dict of logic for joining/leaving.
- **memory**: List of memory/core memory objects.
- **active_wars**: List of active war/conflict IDs.
- **rumor_decay_rate**: How quickly rumors decay.
- **tension_decay_rate**: How quickly tension decays.
- **created_at, updated_at**: Timestamps.

### Tension and War System
- Tension is tracked as a numeric score (0-100) between factions and decays over time if no hostile actions occur. War is triggered when tension exceeds a threshold and is always initiated by an attack. War state, duration, and outcomes are managed by `war_utils.py` and related modules. See Q&A for details on war triggers, duration, and resolution.

### Affinity and Membership
- Affinity is calculated based on NPC and faction traits, determining the likelihood of joining or switching factions. Membership logic supports multi-faction membership (e.g., spies, diplomats) and is managed by `faction_utils.py` and related modules. See Q&A for affinity rules and switching logic.

### Rumor and Truth System
- Factions track rumors separately from memories. Rumors decay over time and cannot be proven or converted to core memories. Truth scores are calculated by direct comparison with fuzzy logic. See `npc_rumor_utils.py` for rumor propagation, decay, and truth scoring logic.

### Memory and Event Logging
- Faction memory logs all war events, control changes, and major events. Memories are summarized and can be referenced for narrative or gameplay purposes. See `memory_utils.py` for summarization and core memory logic.

### Influence and Propagation
- Faction influence propagates through POIs and can spread to NPCs based on proximity and other factors. Influence propagation and membership drift are managed by `faction_tick_utils.py` and related modules.

### Event Hooks
- All major system changes (war, territory loss, membership changes, rumor spikes) are logged in faction memory and a central world history for analytics or narrative purposes.

### References
- See `docs/stubs_needs_consolidation_qna.md` for Q&A clarifications and rationale.
- See `backend/models/faction.py` for the canonical data model.
- See `archives/unzips/Backend/factions/` for utility modules (tension, war, membership, rumor, influence).

## Logging System

The codebase now uses a real logger based on the standard Python `logging` module, replacing the previous `LoggerStub`. The logger is configured in `backend/core2/logging.py` and can be imported as `logger` throughout the codebase. This enables proper logging of events, errors, and debug information for all systems, supporting both console and file output as needed.

## Database System

The codebase now uses a real SQLAlchemy database object, replacing the previous db stub. The database object is configured in `backend/extensions.py` and can be imported as `db` throughout the codebase. Use `db` for model definitions, sessions, and migrations, following standard SQLAlchemy and Flask best practices.

## Template Utilities

The codebase provides two utilities for standardizing reviews and examples:

- **ReviewTemplateFactory** (`backend/core2/schemas/review_template_factory.py`):
  Generates review templates for different entity types (NPC, Quest, Region, Faction, etc.) with sensible default fields. Use `ReviewTemplateFactory.get_template(entity_type)` to obtain a template for reviews or feedback.

- **ExampleTemplates** (`backend/core2/schemas/example_templates.py`):
  Provides example data for different entity types, useful for tests, documentation, and onboarding. Use `ExampleTemplates.get_example(entity_type)` to obtain a sample data dictionary.

These utilities help ensure consistency in documentation, testing, and user feedback across the codebase.

## Versioning and Change Tracking Utilities

The codebase provides several utilities for unique identification, change tracking, and version control:

- **UUIDMixin** (`backend/models/base.py`):
  SQLAlchemy mixin that adds a UUID primary key column named `id`. Use as a base class for models requiring a UUID primary key.

- **ChangeRecord** (`backend/core2/persistence/change_tracker.py`):
  Dataclass representing a single change to the world state, including metadata for auditing and versioning. Used by the `ChangeTracker` system.

- **WorldVersionControl** and **VersionMetadata** (`backend/core2/persistence/version_control.py`):
  `WorldVersionControl` manages version history, current version, and rollback for the world state. `VersionMetadata` stores version info, timestamp, author, and description for each version.

These utilities enable robust tracking of changes, support for undo/redo, and comprehensive audit trails for all major systems. 