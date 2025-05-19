# Feat Achievement History System - Data Model

## Overview
This module tracks feat acquisition events for characters, including timing, character stats at acquisition, and context. It is designed for extensibility and efficient querying.

## Entity Relationship Diagram (ERD)

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

## Field Descriptions

### FeatAchievementEvent
- `Id`: Unique identifier for the event
- `CharacterId`: Reference to the character acquiring the feat
- `FeatId`: Reference to the acquired feat
- `Timestamp`: When the feat was acquired
- `CharacterLevel`: Level of the character at acquisition
- `StatsSnapshot`: Snapshot of character stats (see below)
- `Context`: Additional context (JSON or string)

### CharacterSnapshot
- `Level`, `Health`, `Mana`, `Strength`, `Dexterity`, `Intelligence`: Common RPG stats
- `CustomStats`: Dictionary for extensible stats

### Feat
- `Id`: Unique feat identifier
- `Name`: Feat name
- `Description`: Feat description
- `Metadata`: Dictionary for extensible feat properties

## Storage
- Data is stored in a JSON file for prototyping, with in-memory caching and indexing for performance.
- Retention policy is configurable (default: 365 days).

## Extensibility
- The schema is designed to allow new stats, context fields, and feat metadata without breaking changes.

---

# Region Definition and Association System for Regional Arcs

## Overview
This module defines the structure and management of geographic regions within the game world and their association with Regional Arcs. It supports narrative-driven gameplay by enabling dynamic region-arc relationships, region-specific properties, and integration with other world systems.

## Entity Relationship Diagram (ERD)

```
+-----------+        +-----------------+        +-----------------+
|  Region   |<------>|  RegionalArc    |<------>|  GlobalArc      |
+-----------+        +-----------------+        +-----------------+
| Id        |        | Id              |        | Id              |
| Name      |        | RegionId        |        | Title           |
| Type      |        | RegionName      |        | ...             |
| Boundary  |        | RegionType      |        +-----------------+
| Factions  |        | ...             |
| Resources |        +-----------------+
| Culture   |
| State     |
| ArcIds    |
+-----------+
```

- **Region**: Represents a geographic area with boundaries, dominant factions, resources, cultural attributes, and dynamic state. Each region can be associated with multiple Regional Arcs.
- **RegionalArc**: Narrative arc tied to a specific region, with region-specific story beats, characters, and locations. Linked to a parent GlobalArc.
- **GlobalArc**: High-level narrative arc that can have multiple RegionalArcs as children.

## Field Descriptions

### Region
- `Id`: Unique identifier (GUID)
- `Name`: Human-readable region name
- `Type`: Category (e.g., city, province, biome)
- `Boundary`: 2D boundary (Rect) for region
- `DominantFactions`: List of faction IDs
- `ResourceDistribution`: Dictionary of resource types and quantities
- `CulturalAttributes`: Dictionary of cultural properties
- `State`: Dynamic state dictionary
- `AssociatedArcIds`: List of RegionalArc IDs associated with this region

### RegionalArc
- `RegionId`: Associated region's ID
- `RegionName`: Name of the region
- `RegionType`: Type/category of the region
- `RegionalStoryBeats`: List of region-specific story beats
- `RegionalCharacters`: List of character IDs unique to the region
- `RegionalLocations`: List of location IDs unique to the region
- `ParentGlobalArcId`: ID of the parent GlobalArc
- `InfluenceLevel`: Degree of influence from the global arc
- `OverrideRules`: Rules for overriding global arc behavior
- `RegionalStateChanges`: List of state changes triggered by the arc
- `CompletionConditions`: List of conditions for arc completion
- `Rewards`: List of rewards for arc completion
- `FollowUpArcs`: List of subsequent arcs

## Association Logic
- Regions and RegionalArcs are associated bidirectionally using the `RegionSystem`.
- `RegionSystem` maintains mappings from arc IDs to region IDs and vice versa.
- Regions can be queried for all associated arcs, and arcs can retrieve their associated region.
- Supports overlapping regions and multiple arcs per region.

## Integration Points
- **WorldManager**: Instantiates and manages the `RegionSystem`.
- **Narrative System**: Uses `RegionalArc` and region associations for narrative progression.
- **WorldStateManager**: Integrates region state for persistence and gameplay logic.
- **Event System**: Can trigger events based on region or arc state changes.

## Extensibility
- The system is designed to allow new region types, properties, and association rules without breaking changes.
- Regions and arcs can be extended with additional metadata as needed for gameplay or narrative features.

--- 