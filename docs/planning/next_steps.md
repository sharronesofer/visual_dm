# VDM Restructuring: Next Steps for Manual Review

This document provides specific guidance for the next phase of the VDM restructuring process, which requires manual review and decision-making.

## Step 1: Run the Duplicate Cleanup Script

```bash
./cleanup_duplicates.sh
```

This will:
- Group duplicate files together in the `vdm/Assets/Scripts/Modules_Duplicates_Backup` directory
- Organize them by filename for easy comparison
- Log the process in `cleanup_log.txt`

## Step 2: Review Duplicate Files, Starting with Core Systems

Start with the most critical systems, as these are likely referenced by many other files:

1. **Events System Duplicates**
   - Review duplicates in `Modules_Duplicates_Backup/EventManager.cs/` etc.
   - Compare implementation details, checking for differences in:
     - Method signatures
     - Properties
     - Event handling
   - Keep the most complete implementation in the Events module
   - Document decisions in a file like `events_resolution.md`

2. **Core Module Duplicates**
   - Many files were found in both legacy locations and the Core module
   - Keep base system implementations in Core
   - Move specialized implementations to their respective modules
   - Ensure proper dependencies between modules

3. **Faction/Factions Module Resolution**
   - Consolidate the `Faction` and `Factions` modules (both exist with duplicate files)
   - Standardize on `Factions` (plural) for consistency with other module names
   - Update all references accordingly

## Step 3: Apply Namespace Updates

After resolving the most critical duplicates:

```bash
./update_namespaces.sh
```

This will:
- Update namespaces to match the new module structure
- Create backups of all modified files
- Log changes to `namespace_updates_log.txt`

## Step 4: Test Building the Project by Module

Build the project incrementally, focusing on one module at a time:

1. Start with Core module
2. Fix any reference errors
3. Move to Events module
4. Continue with remaining modules in dependency order

## Step 5: Detailed Review by Module Category

### Core Game Systems
- Review Events, Analytics, Memory, Rumor, WorldState, and Time modules
- Ensure each module contains only relevant functionality
- Move any misplaced files to the correct module
- Update the cleanup log with your decisions

### Game World Systems
- Review Factions, NPCs, Quests, POI, and World modules
- Focus on clarifying responsibilities between:
  - NPCs vs Characters
  - Quests vs Quest modules
  - World vs WorldState

### Technical Infrastructure
- Review Storage, Networking, UI, and Dialogue modules
- Pay special attention to:
  - Network-related files that might be in different modules
  - UI components that should be consolidated
  - Dialogue system integration with other modules

### Supporting Systems
- Review Combat, Economy, Testing modules
- Ensure test files are properly associated with the modules they test

## Step 6: Updating References and Import Statements

After relocating files to their final locations:

1. Update `using` statements in C# files to reference the new namespaces
2. Pay special attention to:
   - Files that reference relocated utilities
   - Cross-module dependencies
   - Event handler registrations

## Step 7: Final Cleanup

1. Remove backup files (`.bak`) after confirming everything works
2. Remove empty directories
3. Update compiler settings if needed
4. Consider creating a dependency graph between modules

## Common Issues to Watch For

- **Circular Dependencies**: Two modules that reference each other
- **Hidden Dependencies**: Implicit dependencies through static references
- **Namespace Conflicts**: Multiple classes with the same name in different namespaces
- **Split Functionality**: Related functionality split across multiple modules
- **Interface/Implementation Mismatches**: Interfaces and their implementations in different modules

## Documentation to Maintain

For each module you review:
1. Document key responsibilities
2. List main classes/components
3. Note dependencies on other modules
4. Record any technical debt or future improvements

## Timeline Recommendation

- **Week 1**: Review and resolve duplicates in Core and Events modules
- **Week 2**: Review and resolve duplicates in remaining Core Game Systems
- **Week 3**: Review and resolve duplicates in Game World systems
- **Week 4**: Review and resolve duplicates in Technical Infrastructure and Supporting Systems
- **Week 5**: Final cleanup, testing, and documentation 