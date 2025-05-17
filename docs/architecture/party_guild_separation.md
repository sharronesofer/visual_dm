# Party vs. Guild Organization: Codebase Separation

## Overview
This document explains the architectural separation between party and guild systems in the codebase, as part of the audit for Task 493 (Party Disbanding Trigger Audit and Documentation).

---

## Party System
- **Location:** `backend/core/systems/party/PartyManager.ts`, `backend/core/systems/party/types.ts`
- **Key Class:** `PartyManager`
- **Responsibilities:**
  - Manages party lifecycle: creation, joining, leaving, kicking, disbanding, and state transitions.
  - Handles party membership, invitations, roles, and party-specific events.
  - Implements distributed locking for concurrency control.
  - All party logic (including disbanding) is encapsulated in the `PartyManager` class and related types.
- **Persistence:**
  - Parties are managed in-memory and via Redis for distributed locking.
  - No overlap with guild persistence or logic.

## Guild System
- **Location:** `src/poi/models/SocialPOI.ts`, `utils/buildingFactory.ts`, `types/buildings/social.ts`
- **Key Concepts:**
  - Guilds are modeled as a subtype of social points of interest (POIs), specifically as `SocialSubtype.GUILD`.
  - Guild buildings are created via `createGuildHall` in `utils/buildingFactory.ts`.
  - Guilds have their own NPCs, quests, and faction logic, managed within the `SocialPOI` class.
- **Responsibilities:**
  - Guilds are persistent world organizations, not tied to transient player parties.
  - Guild logic includes NPC roles (e.g., guildmaster, trainer), quest availability, and faction reputation.
  - No direct overlap with party membership, party events, or party disbanding logic.

## Architectural Separation
- **No Shared Classes or Data Structures:**
  - Parties and guilds are implemented in entirely separate modules and files.
  - No shared state, event systems, or persistence layers.
- **Distinct Use Cases:**
  - Parties: Temporary player groups for adventuring, with dynamic membership and lifecycle.
  - Guilds: Persistent organizations in the world, with their own buildings, NPCs, and quests.
- **No Cross-Triggering:**
  - Disbanding a party does not affect guild membership or state.
  - Guild operations (joining, leaving, managing) are handled independently of party logic.

## References
- `backend/core/systems/party/PartyManager.ts` (Party logic)
- `src/poi/models/SocialPOI.ts` (Guild logic)
- `utils/buildingFactory.ts` (Guild building creation)
- `types/buildings/social.ts` (GuildHall type)

---

This separation ensures maintainability, clarity, and prevents unintended side effects between party and guild systems. 