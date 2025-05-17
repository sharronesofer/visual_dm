# Integration Points & APIs: Interaction System ↔ Building Modification/Construction Systems

**Document ID:** API-IS-BC-001
**Last Updated:** 2025-05-16

---

## 1. Overview
This document catalogs all integration points and APIs between the Interaction System and the Building Modification/Construction Systems. Each integration point is assigned a unique identifier for traceability.

---

## 2. Construction Request Handling

### IS-BC-REQ-001: Construction Request API
- **Location:** `app/frontend/src/systems/BuildingConstructionSystem.ts`
- **Signature:**
```typescript
static emitConstructionRequest(event: {
    request: ConstructionRequest;
    structure: BuildingStructure;
    player: PlayerState;
    resourceCheck: (player: PlayerState, resources: Record<string, number>) => boolean;
    permissionCheck: (player: PlayerState, position: Position) => boolean;
}): void
```
- **Purpose:** Emits a construction request event to the EventBus for asynchronous processing.
- **Usage Example:**
```typescript
BuildingConstructionSystem.emitConstructionRequest({
  request,
  structure,
  player,
  resourceCheck,
  permissionCheck
});
```
- **Error Handling:** Errors are surfaced via `construction:result` or `construction:validationError` events.
- **Thread Safety:** EventBus is thread-safe for event emission.

### IS-BC-REQ-002: ConstructionRequestHandler Event Listener
- **Location:** `app/frontend/src/systems/ConstructionRequestSystem.ts`
- **Signature:**
```typescript
eventBus.on('construction:request', handler: (event) => void)
```
- **Purpose:** Listens for construction requests, validates, enqueues, and processes them.
- **Error Handling:** Emits `construction:result` with status `invalid` or `failed` on error.

---

## 3. Modification Application

### IS-BC-MOD-001: BuildingModificationSystem.applyModification
- **Location:** `src/systems/BuildingModificationSystem.ts`
- **Signature:**
```typescript
applyModification(modification: BuildingModification): boolean
```
- **Purpose:** Applies a modification to a building structure.
- **Usage Example:**
```typescript
buildingModificationSystem.applyModification(modification);
```
- **Error Handling:** Returns `false` on failure; errors may be logged or emitted as events.
- **Thread Safety:** Ensure thread safety for concurrent modifications.

---

## 4. Progress Tracking and Notification

### IS-BC-PROG-001: ConstructionProgressSystem Event Emission
- **Location:** `app/frontend/src/systems/ConstructionProgressSystem.ts`
- **Signature:**
```typescript
eventBus.emit('construction:progress', event: ConstructionProgressEvent)
eventBus.emit('construction:complete', event: ConstructionCompleteEvent)
```
- **Purpose:** Emits progress and completion events for ongoing construction.
- **Usage Example:**
```typescript
eventBus.emit('construction:progress', { buildingId, progress, ... });
eventBus.emit('construction:complete', { buildingId, ... });
```
- **Error Handling:** UI and feedback systems must listen for these events and display errors or notifications.
- **Thread Safety:** EventBus is thread-safe for event emission.

---

## 5. Resource Management

### IS-BC-RES-001: Material Refund and Inventory Integration
- **Location:** `app/frontend/src/systems/ConstructionProgressSystem.ts`, `src/systems/InventorySystem.ts`
- **Signature:**
```typescript
refundMaterials(buildingId: string, playerId: string): void
```
- **Purpose:** Refunds materials to a player's inventory when construction is cancelled.
- **Usage Example:**
```typescript
constructionProgressSystem.refundMaterials(buildingId, playerId);
```
- **Error Handling:** Errors are logged and surfaced to the UI if refund fails.
- **Thread Safety:** InventorySystem should be thread-safe for concurrent updates.

---

## 6. Error Handling and Recovery

### IS-BC-ERR-001: Event-Driven Error Reporting
- **Location:** `app/frontend/src/systems/ConstructionRequestSystem.ts`, `app/frontend/src/core/interfaces/types/events.ts`
- **Signature:**
```typescript
eventBus.emit('construction:validationError', event: ConstructionValidationErrorEvent)
eventBus.emit('construction:result', event: ConstructionRequestResult)
```
- **Purpose:** Reports validation and processing errors to the UI and feedback systems.
- **Usage Example:**
```typescript
eventBus.emit('construction:result', { requestId, status: 'failed', errors: [err.message] });
```
- **Error Handling:** UI and feedback systems must listen for these events and display errors.
- **Thread Safety:** EventBus is thread-safe for event emission.

---

## 7. Shared Resources and Contention Points
- **EventBus**: Central event dispatcher; thread-safe.
- **BuildingStructure Map**: Not inherently thread-safe; concurrent writes must be managed externally.
- **InventorySystem**: Should be thread-safe for concurrent inventory updates.

---

## 8. Unique Identifiers for Integration Points
- IS-BC-REQ-001: Construction Request API
- IS-BC-REQ-002: ConstructionRequestHandler Event Listener
- IS-BC-MOD-001: BuildingModificationSystem.applyModification
- IS-BC-PROG-001: ConstructionProgressSystem Event Emission
- IS-BC-RES-001: Material Refund and Inventory Integration
- IS-BC-ERR-001: Event-Driven Error Reporting

---

## 9. References
- `app/frontend/src/systems/BuildingConstructionSystem.ts`
- `app/frontend/src/systems/ConstructionRequestSystem.ts`
- `src/systems/BuildingModificationSystem.ts`
- `src/systems/BuildingSystem.ts`
- `app/frontend/src/systems/ConstructionProgressSystem.ts`
- `app/frontend/src/core/interfaces/types/events.ts`

---

*End of document.* 