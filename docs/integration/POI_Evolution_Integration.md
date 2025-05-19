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

### 1. Add logic for additional POI types (dungeon, landmark, resource) in integration systems
- **Best Practice:** For each new POI type, define a clear data schema and event payload. Update all integration systems (NPC, Economy, War, Memory) to handle new POI types by subscribing to the `poi:evolved` event and implementing type-specific logic. Document the expected behaviors and edge cases for each POI type in the integration system's documentation.
- **Next Steps:**
  - Extend the POI data model to include new types and their attributes.
  - Update event handlers in each system to process new POI types.
  - Add unit and integration tests for each new POI type.
  - Document the integration logic and provide usage examples.

### 2. Expand event bus implementation for robust decoupling
- **Best Practice:** Use a strongly-typed, asynchronous event bus with support for event versioning, filtering, and error handling. Ensure all systems interact with the event bus via well-defined interfaces. Implement circuit breakers and retry logic for cross-system calls. Document the event bus API and provide code samples for subscribing and publishing events.
- **Next Steps:**
  - Refactor the event bus to support async event delivery and filtering.
  - Add error handling, logging, and monitoring for event propagation.
  - Provide a reference implementation and usage guide in the documentation.

### 3. Document authentication and rate limiting for all integration APIs
- **Best Practice:** Require JWT or API key authentication for all external API endpoints. Implement rate limiting using a middleware or API gateway. Document authentication requirements, rate limits, and error responses in the API reference section. Provide example requests and error handling strategies.
- **Next Steps:**
  - Add authentication and rate limiting middleware to all integration APIs.
  - Update API documentation with authentication and rate limiting details.
  - Add tests for authentication failures and rate limit exceedance.

### 4. Add more detailed sequence diagrams as systems evolve
- **Best Practice:** Maintain up-to-date sequence diagrams for all major integration flows. Use a standard diagramming tool (e.g., Mermaid, PlantUML) and store diagrams in the documentation repo. Update diagrams whenever integration logic changes. Reference diagrams in relevant documentation sections.
- **Next Steps:**
  - Create or update sequence diagrams for new or changed integration flows.
  - Review diagrams for accuracy during code reviews.
  - Link diagrams from API and integration documentation. 