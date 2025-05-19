# assets/equipment/

This folder contains all equipment, item, and gear assets for the game. Store images for weapons, armor, consumables, and other equipment here.

## Subfolder Structure

- `weapons/` — Swords, bows, staves, etc.
- `armor/` — Helmets, chestplates, boots, etc.
- `consumables/` — Potions, scrolls, food, etc.

## Naming Conventions

- Weapons: `weapon_[type]_[variant].png` (e.g., `weapon_sword_001.png`)
- Armor: `armor_[type]_[variant].png` (e.g., `armor_helmet_01.png`)
- Consumables: `consumable_[type]_[variant].png` (e.g., `consumable_potion_01.png`)
- Use lowercase and underscores for all file and folder names.

# Visual DM UI Documentation

## Accessibility

Visual DM is designed to be accessible to all users, including those with disabilities. Key accessibility features include:
- Full keyboard and gamepad navigation for all UI
- Screen reader support for all visible text
- Colorblind-friendly palettes and runtime color contrast validation
- UI scaling and font resizing
- Subtitles/captions for all audio feedback
- Multi-modal feedback (visual, audio, haptic)
- Accessible error and validation messages in the backend

**How to Use:**
- Open the Accessibility Settings Panel from the main menu or with `Ctrl+Alt+A`
- Toggle colorblind mode, adjust scaling, enable/disable screen reader, and configure feedback
- All settings apply immediately and persist as needed

**More Information:**
- [Accessibility Guide](./accessibility.md)
- [Component Library](./component-library.md)
- [Design System](./design-system.md)

For questions or additional needs, contact the development team or open an issue.

## Combat System (Canonical)

- See `VDM/Assets/Scripts/Combat/` for the canonical, modular, extensible combat system implementation.
- Fully compliant with `/docs/Development_Bible.md` and `/docs/CombatSystem_API.md`.
- Backend API: `/backend/app/api/combat.py` (FastAPI, Pydantic models, `/combat/state` GET/POST).
- Unity integration: 100% runtime, no scene/prefab/tag dependencies, entry point is `GameLoader.cs` in `Bootstrap.unity`.
- For extension and usage, see the README in the combat directory.
