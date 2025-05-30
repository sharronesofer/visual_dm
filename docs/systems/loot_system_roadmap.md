
# 🛠️ Visual DM: Loot & Item System Roadmap

This roadmap outlines the full loot generation, identification, and item evolution system for Visual DM, centered around a hybrid AI + rule-driven engine.

---

## 🎯 GOALS

- Every item is magical and evolves with the player
- Loot drops regularly and is meaningful at all levels
- Epics and Legendaries are rare, flavorful, and lore-rich
- Players can identify hidden powers through gameplay or high-cost encounters
- GPT enhances flavor, not mechanics — ensuring consistent rule compliance

---

## 🔢 DROP SYSTEM OVERVIEW

| Rarity    | Drop Rate (from battles) | Effects | Naming       | Notes |
|-----------|--------------------------|---------|--------------|-------|
| Normal    | 50%                      | 3–5     | Generic      | Frequent, low impact |
| Epic      | 0.25% of drops (1/400)   | 8–12    | Template/GPT | Story-worthy |
| Legendary | 0.0025% of drops (1/40K) | 20      | GPT-named    | Ultra-rare, quest-tied |

---

## 🧩 ITEM STRUCTURE

```json
{
  "item_id": "armor_0572",
  "base_item": "Chainmail",
  "rarity": "legendary",
  "display_name": "The Voidwoven Shell",
  "flavor_text": "This chainmail once anchored a dying god to the mortal plane.",
  "effects": [
    { "level": 1, "effect": { "damage_resistance": "necrotic" } },
    { "level": 3, "effect": { "skill_bonus": 2, "modified_skill": "Arcane" } }
  ],
  "identified_levels": [1, 2],
  "max_effects": 20
}
```

---

## 🧠 SYSTEM COMPONENTS

### 1. `item_effects.json`
- Contains all valid effect types
- Effects are tagged by item type
- Supports:
  - `feat`: pulls from feats list (excludes spellcasting feats)
  - `skill_bonus`: pulls from valid skills
  - `countable_effects`: stackable (e.g. DR, stat bonuses)
  - Monster-only feats (for legendary items)

### 2. Loot Generator
- Takes in `player_level` and `battle_context`
- Rolls:
  - Drop chance (50%)
  - Rarity tier
  - Base item (from item type pool)
  - Effects (level-gated)
- GPT used for epic/legendary naming and lore

### 3. Validator
- Ensures items:
  - Only use allowed fields
  - Pull valid skills/effects
  - Are safe and rule-compliant

### 4. Identification System
- Standard vendors reveal next effect
- Legendary NPC reveals all (for a price)
- Shopkeepers identify and mark-up legendary items sold to them

---

## 🧪 DESIGN INSIGHTS

- Unlocking effects per level provides a "gear evolution" arc
- Players won't know how good an item is until it's identified
- Names hint at rarity but don't guarantee it
- Regret-driven systems (e.g. selling legendaries) build deeper engagement

---

## 🚧 NEXT STEPS

- [ ] Finalize `item_effects.json` with effect schema
- [ ] Build `generate_loot()` logic
- [ ] Create `validate_item()` function
- [ ] Create ID system with NPC interaction
- [ ] Integrate loot drops into battle resolution flow
