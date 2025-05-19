# GlobalArc System (Narrative)

## Overview
The `GlobalArc` system models high-level narrative arcs for the game, supporting progression, conditions, relationships, and clean architecture separation.

## Architecture
- **Domain Layer**: `GlobalArc`, `ArcStage`, interfaces for conditions and completion, relationships, metadata.
- **Application Layer**: `IGlobalArcService`, `GlobalArcService` for business logic, progression, validation, and event hooks.
- **Infrastructure Layer**: `IGlobalArcRepository`, `InMemoryGlobalArcRepository` for persistence, `GlobalArcDTO` for data transfer, `GlobalArcMapper` for conversion.

## Class Diagram
```
+-------------------+
|   GlobalArc       |
+-------------------+
| Id                |
| Title             |
| Description       |
| NarrativePurpose  |
| Stages            |
| CurrentStageIndex |
| TriggerConditions |
| CompletionCriteria|
| Relationships     |
| Metadata          |
| Version           |
| DependencyArcIds  |
+-------------------+
```

## Usage Example
```csharp
var arc = new GlobalArc(
    "The Great War",
    "A world-spanning conflict that shapes the fate of nations.",
    "Drive the main plot through escalating conflict and resolution."
);
arc.Stages.Add(new ArcStage("Setup", "The world is at peace, but tensions rise."));
arc.Stages.Add(new ArcStage("Rising Action", "Nations mobilize for war."));
arc.Stages.Add(new ArcStage("Climax", "The decisive battle occurs."));
arc.Stages.Add(new ArcStage("Resolution", "Aftermath and rebuilding."));
arc.CompletionCriteria = new CustomCompletionCriteria(); // Implement IArcCompletionCriteria
arc.TriggerConditions.Add(new CustomArcCondition()); // Implement IArcCondition

var repo = new InMemoryGlobalArcRepository();
var service = new GlobalArcService(repo);
service.RegisterArc(arc);
service.ProgressArc(arc.Id);
```

## Integration Points
- **Event System**: Publishes `ArcProgressedEvent` and `ArcCompletedEvent` via `EventBus`.
- **Other Systems**: Use relationships to link arcs to characters, quests, items, etc.
- **Persistence**: Use repository for saving/loading arcs.

## Best Practices
- Use validation methods to ensure narrative consistency and prevent circular dependencies.
- Use DTOs and mappers for serialization and data transfer.
- Extend interfaces for custom conditions and completion logic.

## For Narrative Designers
- Define arcs and stages in code or via data-driven tools (future work).
- Use metadata for categorization (theme, tone, intensity).
- Collaborate with developers to implement custom conditions and completion logic.

## For Developers
- Follow clean architecture: keep domain logic independent of infrastructure.
- Use the service and repository interfaces for all arc operations.
- Extend for file/DB persistence as needed.

## See Also
- `RegionalArc` for region-specific narrative arcs
- `FactionArc` for faction-specific narrative arcs (see `README_FactionArc.md`) 