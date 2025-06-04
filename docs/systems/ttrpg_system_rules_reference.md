# Custom TTRPG System Rules Reference

## 🎯 Core Mechanics

### Attributes
- STR, DEX, CON, INT, WIS, CHA
- Ranges typically –2 to +5

### Derived Stats
- **HP**: `Level × (1d12 + CON)`
- **MP**: `Level × 1d8 + INT × Level`
- **DR**: Sum of equipped armor DR + any feat bonuses
- **AC**: `10 + DEX + Feat Bonuses`

### Action Economy
Each turn, a character may use:
- 1 **Action**
- 1 **Bonus Action**
- 1 **Movement**
- 2 **Free Actions**
- 1 **Trigger per action type**:
  - Action Trigger
  - Bonus Trigger
  - Free Trigger

## ⚔️ Combat Resolution

### To Hit
- Formula: `1d20 + relevant attribute + (skill / 3)`

### Damage
- Based on weapon or feat
- Apply relevant attribute bonus
- Reduce final value by target's **DR**

### Crits
- Natural 20 = **Critical Hit** (double damage)

### Saving Throws
- **DC (Attribute-based)**: `10 + attribute`
- **DC (Skill-based)**: `10 + skill`
- Resolve: `1d20 + saving modifier vs DC`

## 🔁 Movement
- Can move through **ally squares** at half speed
- Cannot move through **enemy squares** unless passing **Acrobatics vs. Athletics** check

## 🛡 Resistance & Advantage
- **Resistance** = take half damage
- **Vulnerability** = take double damage
- **Advantage/Disadvantage**:
  - Cancel 1:1
  - 2x advantage vs 1x disadvantage = still advantage

## 🧬 Wild Shape
- Available beasts = CR ≤ (Nature score ÷ 4), rounded down to nearest 0.25
- Choose from loaded monster list (tagged as type: Beast)

## 📚 Leveling Rules
- XP: See leveling table
- **Abilities**: 7 at level 1, +3 per level after
- **Skills**: Max rank = `Level + 3`
- Skill points per level = `4 + INT`

## 📖 Feat Data Format
Each feat should include:
- `mp_cost`
- `action_type`
- `trigger_type` (if applicable)
- `damage`, `damage_dice`, `damage_bonus_attribute`
- `save_required`, `save_type`, `save_dc`, `save_vs`
- `status_condition`, `effect_duration`, `targets`, `area`
- `requires_hit`, `requires_weapon`
- `mobility_effect`, `visibility_effect`
- `tags`, `scaling_attribute`, `combo_tags`

Optional flags:
- `spellcasting_granted`, `spellcasting_type`
- `repeatable`, `usable_once_per_turn`
- `combat_irrelevant` (for abilities like Beast Speech, Eldritch Sight)

