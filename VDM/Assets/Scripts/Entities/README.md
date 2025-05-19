# Entities Directory

## Purpose
The `Entities` directory contains all scripts related to in-game entities, including:
- NPCs (Non-Player Characters)
- Player characters
- Entity logic and behavior (e.g., AI controllers, trait generators, state machines)
- Factions, relationships, and profiles
- Factories and spawners for entity instantiation

All scripts in this directory are focused on representing, managing, and controlling the various entities that populate the game world.

## Subsystems

### Feat Achievement History System

This module tracks feat acquisition events for characters, including timing, character stats at acquisition, and context. It is designed for extensibility and efficient querying.

#### Entity Relationship Diagram (ERD)

```
+---------------------+        +-----------------+        +-----------------+
|  FeatAchievementEvent|------->|   Character     |        |      Feat       |
+---------------------+        +-----------------+        +-----------------+
| Id (string)         |        | Id (string)     |        | Id (string)     |
| CharacterId (string)|        | ...             |        | Name (string)   |
| FeatId (string)     |        |                 |        | Description     |
| Timestamp (DateTime)|        +-----------------+        | Metadata (dict) |
| CharacterLevel (int)|                                   +-----------------+
| StatsSnapshot       |
| Context (string)    |
+---------------------+
```

- **FeatAchievementEvent**: Records each feat acquisition, linking to a character and a feat, with timestamp and context.
- **CharacterSnapshot**: Embedded in FeatAchievementEvent, captures stats at the time of acquisition.
- **Feat**: Describes the feat, with metadata for extensibility.

#### Field Descriptions

##### FeatAchievementEvent
- `Id`: Unique identifier for the event
- `CharacterId`: Reference to the character acquiring the feat
- `FeatId`: Reference to the acquired feat
- `Timestamp`: When the feat was acquired
- `CharacterLevel`: Level of the character at acquisition
- `StatsSnapshot`: Snapshot of character stats (see below)
- `Context`: Additional context (JSON or string)

##### CharacterSnapshot
- `Level`, `Health`, `Mana`, `Strength`, `Dexterity`, `Intelligence`: Common RPG stats
- `CustomStats`: Dictionary for extensible stats

##### Feat
- `Id`: Unique feat identifier
- `Name`: Feat name
- `Description`: Feat description
- `Metadata`: Dictionary for extensible feat properties

#### Storage
- Data is stored in a JSON file for prototyping, with in-memory caching and indexing for performance.
- Retention policy is configurable (default: 365 days).

#### Extensibility
- The schema is designed to allow new stats, context fields, and feat metadata without breaking changes.

--- 