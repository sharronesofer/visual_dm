# POI Evolution System Integration Points

## Table of Contents
1. [Overview](#overview)
2. [API References](#api-references)
3. [Sequence Diagrams](#sequence-diagrams)
4. [Authentication, Security, and Error Handling](#authentication-security-and-error-handling)
5. [Troubleshooting Guide](#troubleshooting-guide)
6. [Code Examples](#code-examples)
7. [Dependency Map](#dependency-map)
8. [Open Questions / TODOs](#open-questions--todos)

---

## Overview
This document outlines the integration points, data exchange requirements, API specifications, and event triggers between the POI Evolution System and other core systems: NPC, Economy, War, and Memory. It is based on the current codebase analysis and is intended to guide future development and ensure seamless interoperability.

---

## API References

### NPC System Integration
- **Event:** `poi:evolved`
- **Payload:** `{ poiId: string, poi: IPOI, trigger: string, changes: Partial<IPOI>, version: number }`
- **Subscription Example:** See [Code Examples](#code-examples)
- **Effect:** Update NPC routines, spawning, or behaviors based on POI state

### Economy System Integration
- **Event:** `poi:evolved`
- **Payload:** Same as above
- **Effect:** Update market data, resource generation, agent roles

### War System Integration
- **Event:** `poi:evolved`
- **Payload:** Same as above
- **Effect:** Update combat objectives, environmental effects, battle outcomes

### Memory System Integration
- **Event:** `poi:evolved`
- **Payload:** Same as above
- **Effect:** Record as MemoryEvent for historical tracking

---

## Sequence Diagrams

### POI Evolution Event Propagation
```
POIEvolutionSystem -> POIManager: emit('poi:evolved', ...)
POIManager -> EventBus: emit('poi:evolved', ...)
EventBus -> NPCSystem: notify(event)
EventBus -> EconomySystem: notify(event)
EventBus -> WarSystem: notify(event)
EventBus -> MemorySystem: notify(event)
```

### End-to-End Scenario: POI Evolution Impact
```
UserAction -> POIEvolutionSystem: processPOIEvolution()
POIEvolutionSystem -> POIManager: onPOIModified()
POIManager -> EventBus: emit('poi:evolved', ...)
EventBus -> NPCSystem: update routines
EventBus -> EconomySystem: update market
EventBus -> WarSystem: update objectives
EventBus -> MemorySystem: record event
```

---

## Authentication, Security, and Error Handling
- **Authentication:**
  - Internal event bus is trusted; external API endpoints require JWT or API key
- **Security:**
  - Only authorized systems can mutate POI state
  - Memory events are immutable once recorded
- **Error Handling:**
  - All event handlers must catch and log errors
  - Circuit breakers and retry logic are recommended for cross-system calls
  - See [Troubleshooting Guide](#troubleshooting-guide)

---

## Troubleshooting Guide
- **Issue:** NPC/Economy/War/Memory system not responding to POI events
  - **Check:** EventBus subscription is active and not filtered out
  - **Check:** Event payload matches expected schema
  - **Resolution:** Restart affected system, check logs for errors
- **Issue:** Event propagation latency
  - **Check:** System load, EventBus queue depth
  - **Resolution:** Scale up event processing, optimize handlers
- **Issue:** Data inconsistency across systems
  - **Check:** All systems are using the same POI state version
  - **Resolution:** Implement version checks and reconciliation logic

---

## Code Examples

### Subscribing to POI Evolution Events (TypeScript)
```typescript
import { EventBus as CoreEventBus } from 'src/core/interfaces/types/events';
import { POIEvents } from 'src/poi/types/POIEvents';
import { TypedEventEmitter } from 'src/utils/TypedEventEmitter';

const POIEventBus = CoreEventBus.getInstance() as TypedEventEmitter<POIEvents>;

POIEventBus.on('poi:evolved', ({ poiId, poi, trigger, changes, version }) => {
  console.log(`[Integration] POI evolved: ${poiId}, trigger: ${trigger}, changes:`, changes);
  // ...handle event...
});
```

---

## Dependency Map

- POI Evolution System <-> NPC System: Home generation, behavior updates
- POI Evolution System <-> Economy System: Market/agent initialization, resource generation
- POI Evolution System <-> War System: Combat objectives, environmental effects
- POI Evolution System <-> Memory System: Event logging, historical queries

---

## Open Questions / TODOs
- Add logic for additional POI types (dungeon, landmark, resource) in integration systems.
- Expand event bus implementation for robust decoupling.
- Document authentication and rate limiting for all integration APIs.
- Add more detailed sequence diagrams as systems evolve. 