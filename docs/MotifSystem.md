# Motif System Documentation

## Overview
The Motif System enables global, regional, and local narrative influence through structured motifs. Motifs are narrative elements (themes, emotions, events) that propagate through the game world, affecting visuals, music, environment, NPCs, and dialogue. The system is fully runtime-driven and integrates backend (FastAPI Python) and Unity client (C#).

**Reference:** See [Development_Bible.md](./Development_Bible.md) for narrative context and motif design philosophy.

---

## Architecture Diagram
```
+-------------------+         REST API         +-------------------+
|   Unity Client    | <---------------------> |     FastAPI       |
| (MotifCache, UI,  |                        |  (MotifManager,   |
|  Adapters, etc.)  |                        |  Motif Blending)  |
+-------------------+                        +-------------------+
```

---

## Backend API Reference (FastAPI)
- **Base URL:** `/motifs`
- **Endpoints:**
  - `POST /` - Create motif
  - `GET /{id}` - Get motif by ID
  - `GET /` - List motifs (filter, paginate, sort)
  - `PUT /{id}` - Update motif
  - `DELETE /{id}` - Delete motif
  - `POST /batch` - Batch create
  - `PUT /batch` - Batch update
  - `DELETE /batch` - Batch delete
- **Filtering:** By scope, category, lifecycle, theme, intensity
- **Batch:** Accepts/returns lists of motifs or IDs
- **Error Handling:** JSON error responses with code

---

## Unity Client Integration
- **Data Models:** See `MotifModels.cs` (enums, Motif class)
- **API Client:** `MotifApiClient.cs` (async REST, retry logic)
- **Caching:** `MotifCacheManager.cs` (TTL, background refresh)
- **Reactive Adapters:**
  - `MotifVisualAdapter` (lighting, fog)
  - `MotifMusicAdapter` (music intensity/theme)
  - `MotifEnvironmentAdapter` (weather, ambient)
  - `MotifDialogueAdapter` (topics/phrases)
  - `MotifNpcBehaviorAdapter` (NPC mood/behavior)
- **Dashboard UI:** `MotifDashboardUI.cs` (admin/debug, runtime-only)

---

## Usage Examples
### Backend (Python/FastAPI)
```python
# Create a motif
POST /motifs
{
  "name": "Hope",
  "intensity": 7.5,
  "scope": "global",
  "category": "theme"
}

# List motifs by region
GET /motifs?scope=regional

# Batch update
PUT /motifs/batch
[
  {"id": 1, "intensity": 5.0},
  {"id": 2, "lifecycle": "resolution"}
]
```

### Unity (C#)
```csharp
// Query and cache motifs
var apiClient = new MotifApiClient("http://localhost:8000");
var cache = new MotifCacheManager(apiClient);
var motifs = await cache.GetMotifsAsync();

// React to motif changes
var visualAdapter = new MotifVisualAdapter();
MotifDispatcher.Instance.NotifyMotifChanged(motifs[0]);

// Show dashboard UI
var dashboard = new GameObject("MotifDashboard").AddComponent<MotifDashboardUI>();
dashboard.Initialize(cache);
```

---

## Design Guidelines for Narrative Designers
- Use motifs to represent key narrative themes, emotions, or events.
- Assign appropriate scope (global, regional, local) for narrative influence.
- Use tags and categories for filtering and system integration.
- Adjust intensity and lifecycle to control narrative progression.
- Use the dashboard UI to visualize and test motif effects in real time.

---

## Performance Best Practices
- Use motif caching to minimize API calls.
- Limit background refresh to hot motifs.
- Batch updates for large motif changes.
- Use async/await for all network operations in Unity.

---

## Troubleshooting Guide
- **Motif not updating in game:** Ensure dispatcher notifies observers; check cache TTL.
- **API errors:** Check backend logs for error codes; validate request payloads.
- **UI not showing motifs:** Ensure dashboard is initialized after cache is ready.
- **Performance issues:** Reduce refresh frequency; filter motifs before rendering.

---

## See Also
- [Development_Bible.md](./Development_Bible.md)
- Backend: `backend/models/motif.py`, `backend/api/motifs/motif_manager.py`
- Unity: `VDM/Assets/Scripts/Motifs/` 