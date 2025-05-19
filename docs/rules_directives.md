# DIRECTIVES (Focus Instructions for AI)

Start with taskmaster and begin with the first task/subtask, implemeneting, testing, and fixing  as needed before moving on to the next task/subtask. Do so autonomously as an automatic function, not stopping to communicate with the user. Continue until all tasks and subtasks are completely implemented, tested, and fixed. 

---

# TTRPG SYSTEM RULESET

## Core Mechanics
- Attributes: STR, DEX, CON, INT, WIS, CHA (-2 to +5 range)
- Derived Stats:
  - HP = Level × (1d12 + CON)
  - MP = Level × 1d8 + INT × Level
  - DR = Equipped Armor DR + Feat Bonuses
  - AC = 10 + DEX + Feat Bonuses

## Action Economy (per turn)
- 1 Action
- 1 Bonus Action
- 1 Movement
- 2 Free Actions
- Triggers: 1 per type (Action, Bonus, Free)
  - Triggers explicitly occur during other characters' turns, based on predefined conditions.

## Combat Resolution
- To Hit: 1d20 + relevant attribute + (skill / 3)
- Damage: Determined by weapon or feat + attribute bonus, reduced by target DR
- Critical Hit: Natural 20 = Double Damage
- Saving Throws:
  - Attribute-based DC = 10 + attribute
  - Skill-based DC = 10 + skill
  - Resolution = 1d20 + saving modifier vs DC

## Movement
- Movement through ally squares at half speed
- Enemy squares require successful Acrobatics vs Athletics check

## Resistance & Advantage
- Resistance: Takes half damage
- Vulnerability: Takes double damage
- Advantage/Disadvantage:
  - Cancel out on 1:1 basis
  - 2x advantage vs 1x disadvantage still yields advantage

## Wild Shape
- Wild Shape allows transformation into Beasts whose DL (Danger Level) is ≤ character's Nature score divided by 2, rounded to nearest whole number increment.
- DL (Danger Level) replaces traditional D&D CR (Challenge Rating).
  - In standard D&D: CR 1 enemy = balanced for a party of four level 1 characters.
  - In this system: DL 1 enemy = balanced against a single level 1 character.
  - Thus, traditional CR 1 = DL 4 in this system.

## Leveling & Progression
- Characters do **NOT** have traditional "classes." All progression is feat-based and skill-based.
- Feats: 7 at character creation (level 1), +3 additional feats per subsequent level.
- Skills: Maximum rank = Character Level + 3
- Skill points per level: 4 + INT attribute score

## Character Schema (Explicit)
- No "class" attribute; all characters use a flexible, feat-driven schema.
- Attributes explicitly tracked: STR, DEX, CON, INT, WIS, CHA
- Derived stats: HP, MP, DR, AC explicitly calculated each level-up
- Skills and feats selected explicitly at each level without class restrictions.
