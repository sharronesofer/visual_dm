# Narrative System Overview

The Narrative system supports GlobalArc, RegionalArc, and FactionArc for multi-scale narrative management.

- **GlobalArc**: World-spanning narrative arcs
- **RegionalArc**: Region-specific narrative arcs
- **FactionArc**: Faction-specific narrative arcs (see `README_FactionArc.md`)

## FactionArc System

See `FactionArc.cs`, `FactionArcDTO.cs`, `FactionArcMapper.cs`, and `README_FactionArc.md` for the comprehensive data structure and integration of faction-specific narrative arcs. FactionArc extends the Arc system to support:
- Faction identity, goals, and motivations
- Progression stages and state transitions
- Triggering conditions and completion criteria
- Inter-faction relationship matrix
- Integration with Tick System and Region System
- Serialization via DTO/Mapper pattern
- Validation and error handling

Refer to `README_FactionArc.md` for class diagrams, usage, and validation rules. 