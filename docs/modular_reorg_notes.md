# Modular Reorganization Notes (Task 711)

## Overview
This document logs all file moves, edge cases, and rationale for the modular reorganization of the backend (Python/FastAPI) codebase, referencing bible_qa.md for system boundaries and best practices.

## File Moves
- Moved Faction model to `backend/app/factions/faction.py`
- Moved NPC model to `backend/app/npcs/npc.py`
- Moved Quest model to `backend/app/quests/quest.py`
- Moved World model and Map model to `backend/app/world/`
- Moved Character model to `backend/app/characters/character.py`
- Moved Item model to `backend/app/items/item.py`
- Moved Location model to `backend/app/regions/location.py`
- Moved Market model to `backend/app/market/market.py`
- Moved Campaign model to `backend/app/campaigns/campaign.py`
- Moved shared base, API key, user, and cloud provider models to `backend/app/core/`

## Edge Cases
- Some models (e.g., Cleanup, CloudProvider) are infrastructure-level and remain in `core/`.
- Any ambiguous or cross-domain logic is placed in `core/` or left in its original location with a note.
- README.md files updated in each domain folder to clarify new structure.

## Rationale
- Domain logic is now grouped for maintainability, clarity, and scalability.
- Structure aligns with boundaries and future scaffolding described in `docs/bible_qa.md`.
- New folders (e.g., economy, religion, diplomacy) can be added as needed per design Q&A.

## Next Steps
- Update all import paths and references throughout the codebase.
- Run all tests to ensure nothing is broken by the reorganization.
- Continue to document any further edge cases or integration points as they arise. 