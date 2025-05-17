# RegionalArc System (Narrative)

## Overview
The `RegionalArc` system models region-specific narrative arcs, extending the GlobalArc architecture to support local narrative elements, region identification, progression triggers, and world state effects.

## Architecture
- **Domain Layer**: `RegionalArc`, `RegionalStoryBeat`, `OverrideRule`, `RegionalStateChange`, region-specific properties and logic.
- **Application Layer**: (Future) `IRegionalArcService`, `RegionalArcService` for business logic, progression, validation, and event hooks.
- **Infrastructure Layer**: (Future) `IRegionalArcRepository`, `InMemoryRegionalArcRepository` for persistence, `RegionalArcDTO` for data transfer, `RegionalArcMapper` for conversion.

## Class Diagram
```
+----------------------+
|    RegionalArc       |
+----------------------+
| Inherits GlobalArc   |
| RegionId             |
| RegionName           |
| RegionType           |
| RegionalStoryBeats   |
| RegionalCharacters   |
| RegionalLocations    |
| EntryConditions      |
| ProgressionEvents    |
| ExitConditions       |
| ParentGlobalArcId    |
| InfluenceLevel       |
| OverrideRules        |
| RegionalStateChanges |
| PersistentEffects    |
| TemporaryEffects     |
| CompletionConditions |
| Rewards              |
| FollowUpArcs         |
+----------------------+
```

## Usage Example
```csharp
var regionalArc = new RegionalArc(
    "Bandit Uprising in Westvale",
    "A local rebellion threatens the peace in the Westvale region.",
    "Drive regional conflict and player engagement.",
    "region-westvale",
    "Westvale",
    "Province",
    parentGlobalArcId: globalArc.Id
);
regionalArc.RegionalStoryBeats.Add(new RegionalStoryBeat { Title = "Ambush at the Crossroads", Description = "Bandits attack a merchant caravan." });
regionalArc.RegionalCharacters.Add("npc-bandit-leader");
regionalArc.RegionalLocations.Add("crossroads");
regionalArc.EntryConditions.Add(new CustomEntryCondition()); // Implement IArcCondition
regionalArc.CompletionConditions.Add(new CustomCompletionCondition()); // Implement IArcCondition
```

## Integration Points
- **Global Arc System**: Each RegionalArc references a parent GlobalArc and can influence or override global narrative elements.
- **Flexible Tick System**: RegionalArcs can use tick-based or event-based progression triggers.
- **Motifs System**: (Future) RegionalArcs may integrate with motif-driven narrative elements.
- **Event System**: Hooks for region transitions, state changes, and narrative events.
- **Persistence**: Use DTOs and mappers for serialization and data transfer.

## Best Practices
- Use validation methods to ensure region associations and data integrity.
- Use DTOs and mappers for serialization and data transfer.
- Extend interfaces for custom entry, progression, and completion logic.
- Optimize for efficient region loading/unloading and memory usage.

## For Narrative Designers
- Define regional arcs and story beats in code or via data-driven tools (future work).
- Use region identification fields for organization and filtering.
- Collaborate with developers to implement custom conditions and world state effects.

## For Developers
- Follow clean architecture: keep domain logic independent of infrastructure.
- Use the service and repository interfaces for all arc operations (future work).
- Extend for file/DB persistence as needed.

## DTO and Mapper
- **RegionalArcDTO**: Used for serialization and data transfer of RegionalArc objects.
- **RegionalArcMapper**: Converts between RegionalArc and RegionalArcDTO, handling all region-specific and inherited fields.

## Relationship to GlobalArc
- Each RegionalArc extends GlobalArc, inheriting all global narrative properties and logic.
- RegionalArc adds region-specific fields and behaviors, and references its parent GlobalArc via `ParentGlobalArcId`.
- RegionalArcs can override or influence global narrative progression through `OverrideRules` and `InfluenceLevel`.
- Use the validation methods to ensure that every RegionalArc is properly associated with an existing GlobalArc.

# Regional Arc & Region System Integration

## Overview

The Region System defines geographic regions in the game world, each with boundaries, dominant factions, cultural/resource attributes, and dynamic state. Regions are associated with Regional Arcs, enabling region-specific narrative progression and event triggers.

## Region Data Model (UML)

```
+-------------------+
|     Region        |
+-------------------+
| Id: string        |
| Name: string      |
| Type: string      |
| Boundary: Rect    |
| DominantFactions  |
| ResourceDist.     |
| CulturalAttrs     |
| State             |
| AssociatedArcIds  |
+-------------------+
```

## Region-Arc Association
- Regions can be associated with multiple RegionalArcs and vice versa.
- Use `RegionSystem.AssociateArcWithRegion(arcId, regionId)` to link.
- Query regions for an arc: `RegionSystem.GetRegionsForArc(arcId)`
- Query arcs for a region: `RegionSystem.GetArcsForRegion(regionId, allArcs)`

## Sequence Diagram: Region Transition

```
Player moves → RegionSystem.GetRegionAtPosition(pos)
    ↓
If region changes:
    → RegionalArc.TriggerRegionNarrativeEvent(regionSystem, eventKey)
    → Region.UpdateState(...)
```

## Narrative Designer Usage
- Define region-specific content by associating arcs with regions.
- Use region state to trigger narrative events or content.
- Example: When player enters a region, check `region.State` and trigger arc progression.

## Serialization
- RegionSystem supports JSON serialization for save/load.

## Extensibility
- Supports overlapping regions, multiple region types (political, climate, etc).
- Extend Region attributes as needed for new narrative or simulation features.

---
See `RegionSystem.cs` and `RegionalArc.cs` for implementation details.

## See Also
- `GlobalArc` for global narrative arcs
- `FactionArc` for faction-specific narrative arcs (see `README_FactionArc.md`) 