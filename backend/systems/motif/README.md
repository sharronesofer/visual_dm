# Motif System

The Motif system manages narrative motifs or themes that dynamically influence the game world. Motifs are recurring patterns that can affect NPC behavior, event frequency, and other aspects of gameplay to create cohesive narrative experiences.

## Refactored Structure

The system has been refactored to consolidate functionality into a more maintainable structure:

```
backend/systems/motif/
├── __init__.py        # Exports key components
├── manager.py         # Main MotifManager class (primary interface)
├── models.py          # Data models and schemas
├── repository.py      # Data storage and retrieval
├── router.py          # FastAPI endpoints
├── service.py         # Business logic
├── utils.py           # Utility functions
└── README.md          # This file
```

## Usage

The MotifManager is designed as a singleton and should be the primary interface for interacting with motifs:

```python
from backend.systems.motif import get_motif_manager

# Get the MotifManager instance
motif_manager = get_motif_manager()

# Create a new motif
new_motif = await motif_manager.create_motif({
    "name": "The Gathering Storm",
    "category": "CHAOS",
    "scope": "REGIONAL",
    "intensity": 6.5,
    "description": "A growing sense of disorder and unpredictability."
})

# Get all active motifs
active_motifs = await motif_manager.get_motifs()

# Get motifs affecting a specific location
location_motifs = await motif_manager.get_motifs_by_location(x=150.0, y=275.0)

# Generate a random motif
random_motif = await motif_manager.generate_random_motif()

# Get narrative context for a location
narrative_context = await motif_manager.get_narrative_context(x=150.0, y=275.0)
```

## Event Integration

The MotifManager emits events that other systems can listen for:

```python
# Register an event listener
def motif_event_handler(event):
    print(f"Received motif event: {event['type']}")
    print(f"Event data: {event['data']}")

motif_manager.register_event_listener(motif_event_handler)
```

## API Endpoints

The system includes FastAPI endpoints for HTTP access:

```
GET /motifs               # List all motifs
GET /motifs/{motif_id}    # Get a specific motif
POST /motifs              # Create a new motif
PUT /motifs/{motif_id}    # Update a motif
DELETE /motifs/{motif_id} # Delete a motif
```

## Previous Structure

Note: The previous structure contained multiple subdirectories, many of which only had `__init__.py` files. This refactoring consolidates functionality into a more maintainable set of files.
