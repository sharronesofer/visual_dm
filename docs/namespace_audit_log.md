# Namespace Audit and Repair Log

## Issues Identified
- `VisualDM.NPC` (non-existent namespace, NPC classes are in `VisualDM.Entities`)
- `VisualDM.CombatSystem` (non-existent namespace)
- `VisualDM.Inventory` (should be `VisualDM.Systems.Inventory`)
- `VisualDM.Narrative` (non-existent namespace)
- `VisualDM.Utilities` (should be `VisualDM.Systems.Utilities`)
- `VisualDM.Core.Network` (non-existent namespace)
- `VisualDM.Systems.Metrics` (non-existent namespace)
- `VisualDM.MotifSystem` (should be `VisualDM.Systems.MotifSystem`)

## Changes Made

### Entities Folder Fixes

1. `VDM/Assets/Scripts/Entities/BountyHunterNPC.cs`:
   - Replaced `using VisualDM.NPC;` with `using VisualDM.Entities;`
   - Removed `using VisualDM.CombatSystem;` (non-existent namespace)
   - Replaced `using VisualDM.Inventory;` with `using VisualDM.Systems.Inventory;`
   - Added `using VisualDM.Systems.Bounty;` for BountyHunterManager

2. `VDM/Assets/Scripts/Entities/BountyHunterNPCFactory.cs`:
   - Replaced `using VisualDM.NPC;` with `using VisualDM.Entities;`
   - Replaced `using VisualDM.Inventory;` with `using VisualDM.Systems.Inventory;`

3. `VDM/Assets/Scripts/Entities/RelationshipStateMachine.cs`:
   - Replaced `using VisualDM.Utilities;` with `using VisualDM.Systems.Utilities;`

4. `VDM/Assets/Scripts/Entities/NPCController.cs`:
   - Added `namespace VisualDM.Entities` to properly scope the class

### Systems Folder Fixes

1. `VDM/Assets/Scripts/Systems/Inventory/InventoryGiveTakeSystem.cs`:
   - Replaced `using VisualDM.Inventory;` with `using VisualDM.Systems.Inventory;`
   - Changed `using Systems.Integration;` to `using VisualDM.Systems.Integration;`

2. `VDM/Assets/Scripts/Systems/Inventory/InventorySystem.cs`:
   - Added `using VisualDM.Systems.Integration;` for IntegrationLogger and IntegrationTransaction
   - Changed `Systems.Integration.IntegrationTransaction` to `IntegrationTransaction`

3. `VDM/Assets/Scripts/Systems/ArcToQuestMapper.cs`:
   - Changed `using VisualDM.Narrative;` to `using VisualDM.Systems.Narrative;`
   - Changed `using VisualDM.MotifSystem;` to `using VisualDM.Systems.MotifSystem;`

4. `VDM/Assets/Scripts/Systems/ArcToQuestDebugTools.cs`:
   - Changed `using VisualDM.Narrative;` to `using VisualDM.Systems.Narrative;`

5. `VDM/Assets/Scripts/Systems/TickSystem/TickManager.cs`:
   - Changed `using VisualDM.Narrative;` to `using VisualDM.Systems.Narrative;`

6. `VDM/Assets/Scripts/Systems/Bounty/BountyHunterManager.cs`:
   - Created new file in proper namespace `VisualDM.Systems.Bounty`
   - Implemented missing manager class referenced by BountyHunterNPC

### UI Folder Fixes

1. `VDM/Assets/Scripts/UI/InventoryUI.cs`:
   - Changed `using VisualDM.Inventory;` to `using VisualDM.Systems.Inventory;`

2. `VDM/Assets/Scripts/UI/PowerAnalysisDashboard.cs`:
   - Changed `using VisualDM.Utilities;` to `using VisualDM.Systems.Utilities;`

### World Folder Fixes

1. `VDM/Assets/Scripts/World/RegionSystem.cs`:
   - Changed `using VisualDM.Narrative;` to `using VisualDM.Systems.Narrative;`

### Core Folder Fixes

1. `VDM/Assets/Scripts/Core/IsExternalInit.cs`:
   - Moved from root Scripts folder to Core folder for better organization

2. `VDM/Assets/Scripts/Core/MonitoringManager.cs`:
   - Removed non-existent namespace `using VisualDM.Core.Network;`

3. `VDM/Assets/Scripts/Core/InteractionMetricsCollector.cs`:
   - Removed non-existent namespace `using VisualDM.Core.Network;`
   - Removed non-existent namespace `using VisualDM.Systems.Metrics;`

## Remaining Issues

Some outstanding issues to consider:

1. MetricsCollector class is used in InteractionMetricsCollector.cs but it's not clear where this class is defined or what namespace it should be in. Tests for it exist in CoreTests.cs, but the actual implementation can't be found.

2. There are references to Integration classes (IntegrationLogger, IntegrationTransaction) but we've fixed them to use VisualDM.Systems.Integration namespace. This seems to be the expected namespace, but it's important to verify that this namespace exists and the classes are implemented correctly there.

3. `VDM/Assets/Scripts/Entities/NPCController.cs`:
   - May need to add additional using statements

4. `VDM/Assets/Scripts/Entities/BountyHunterNPC.cs`:
   - References `BountyHunterManager.Instance` but missing the corresponding using statement
   - May need to add `using VisualDM.Systems.Bounty;` or similar

5. Namespace consistency issues:
   - Several files may still reference non-existent or improperly named namespaces
   - Need standardization between folder structure and namespace names
   - Need to audit additional files not yet covered 