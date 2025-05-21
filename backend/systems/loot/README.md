# Loot System

## Overview
This module implements the loot system for the game, including item generation, shop logic, and location-based loot distribution.

## Architecture
The loot system uses a consolidated model architecture for simplicity and ease of maintenance:

### Models (`/models`)
- **`base.py`**: SQLAlchemy declarative base for all models
- **`item.py`**: Item definitions and base model
- **`location.py`**: Location and container models
- **`shop.py`**: Shop and inventory models
- **`history.py`**: Loot history and analytics models

All models are exported via the package's `__init__.py` for easier imports.

### Utilities (`/loot_utils.py`)
The loot utilities module has been refactored into a more modular structure:

- **Item Categorization & Organization**: Functions for organizing, validating, and scoring items
- **Item Identity & Naming**: Functions for generating names, flavor text, and item identities 
- **Magical Item Effect Generation**: Functions for generating magical effects for items
- **Loot Generation**: Functions for generating complete loot bundles

This modular approach makes the code more maintainable and allows for easier testing and extension.

### API Routes (`/loot_routes.py`)
Exposes endpoints for loot generation and management. Currently includes:
- `/generate_loot`: Creates a loot bundle based on monster levels

## Usage
Import directly from the loot package:

```python
from backend.systems.loot import BaseItem, Location, Shop, LootHistory
```

Or import from specific modules:

```python
from backend.systems.loot.models import BaseItem, RarityTier
from backend.systems.loot.loot_utils import generate_loot_bundle, generate_item_identity
```

## Integration Points
- Used by combat, quest, and world systems for item drops and rewards
- Shop logic integrates with inventory and economy systems

## Design Rationale and Best Practices
- All models use the same SQLAlchemy declarative base (`LootBase`) for integration
- Use appropriate enums for categorizing items, shops, and locations
- Loot utilities are organized by functionality for better maintainability
- Type hints are used throughout to improve code clarity and IDE support
- For canonical Q&A, design rationale, and best practices, see [docs/bible_qa.md](../../../docs/bible_qa.md). 