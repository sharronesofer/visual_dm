# Progression-to-Interaction Mapping Tables and Rules

**Document ID:** PROG-INT-001
**Last Updated:** 2025-05-16

---

## 1. Overview
This document defines the mapping between character progression metrics and interaction availability in the Interaction System. It provides structured tables and rules to guide both design and implementation.

---

## 2. Mapping Tables

### 2.1 Dialogue Options
| Interaction           | Required Metric(s) | Threshold/Condition         | Unlock/Restriction Rule                | Special Cases                | Example Character Profiles         |
|----------------------|--------------------|----------------------------|----------------------------------------|------------------------------|------------------------------------|
| Advanced Dialogue    | Level, Reputation  | Level >= 10, Reputation > 50| Unlocks advanced dialogue options      | Temporary level boost, reputation loss| High-level hero, disgraced noble    |
| Secret Dialogue      | Reputation         | Reputation > 50            | Unlocks secret dialogue                | Story event may override     | High-rep Rogue, Low-rep Outcast       |
| Skill-based Persuade | Skills (Persuasion)| Persuasion >= 5            | Unlocks persuade option                | Temporary debuff may block   | Persuasion 6 Bard, Persuasion 3 NPC    |

### 2.2 Quest Access
| Interaction      | Required Metric(s) | Threshold/Condition         | Unlock/Restriction Rule                | Special Cases                | Example Character Profiles         |
|-----------------|--------------------|----------------------------|----------------------------------------|------------------------------|------------------------------------|
| Main Quest      | Story Milestone    | Milestone: Prologue Complete| Unlocks main quest                     | None                         | All characters post-prologue         |
| Faction Quest   | Faction Standing   | Standing >= 30              | Unlocks faction quest                  | Temporary alliance may unlock  | Faction Member, Neutral Player       |
| Repeatable Quest| Quest Completion   | Quest not completed         | Available until completed              | Daily reset may re-enable       | New Player, Veteran                 |

### 2.3 Vendor Inventory
| Interaction      | Required Metric(s) | Threshold/Condition         | Unlock/Restriction Rule                | Special Cases                | Example Character Profiles         |
|-----------------|--------------------|----------------------------|----------------------------------------|------------------------------|------------------------------------|
| Rare Items      | Level, Reputation  | Level >= 15, Reputation > 60| Unlocks rare vendor items              | Event unlocks all items        | High-level Hero, Low-rep Thief        |
| Discounted Goods| Achievements       | Achievement: Bargainer      | Unlocks discount                       | Temporary sale event           | Bargainer, Non-achiever              |

### 2.4 Skill Checks
| Interaction      | Required Metric(s) | Threshold/Condition         | Unlock/Restriction Rule                | Special Cases                | Example Character Profiles         |
|-----------------|--------------------|----------------------------|----------------------------------------|------------------------------|------------------------------------|
| Lockpicking     | Skills (Lockpick)  | Lockpick >= 7               | Unlocks lockpicking interaction        | Tool bonus may override        | Lockpick 8 Rogue, Lockpick 5 Mage      |
| Strength Test   | Attributes (STR)   | STR >= 12                   | Unlocks strength-based interaction     | Temporary buff/debuff          | STR 14 Warrior, STR 10 Cleric          |

### 2.5 World Events
| Interaction      | Required Metric(s) | Threshold/Condition         | Unlock/Restriction Rule                | Special Cases                | Example Character Profiles         |
|-----------------|--------------------|----------------------------|----------------------------------------|------------------------------|------------------------------------|
| Festival Event  | Save State/Flags   | Flag: FestivalActive        | Unlocks festival interactions          | Manual override by admin       | All players during event             |
| Disaster Relief | Quest Completion   | Quest: Disaster Started     | Unlocks relief interactions            | Early access for VIPs            | Quest Starter, VIP                   |

### 2.6 Secret Interaction
| Interaction      | Required Metric(s) | Threshold/Condition         | Unlock/Restriction Rule                | Special Cases                | Example Character Profiles         |
|-----------------|--------------------|----------------------------|----------------------------------------|------------------------------|------------------------------------|
| Secret Interaction | Equipment, Achievement | Possess "Ancient Key", "Master Thief" | Unlocks secret door or hidden NPC      | Equipment loss, achievement revocation | Treasure hunter, unrecognized rogue |

### 2.7 Cosmetic Option
| Interaction      | Required Metric(s) | Threshold/Condition         | Unlock/Restriction Rule                | Special Cases                | Example Character Profiles         |
|-----------------|--------------------|----------------------------|----------------------------------------|------------------------------|------------------------------------|
| Cosmetic Option | Achievements, Perks | "Fashionista" achievement, "Silver Tongue" perk | Unlocks cosmetic dialogue or appearance options | Perk removal, hidden achievement | Socialite, plain adventurer         |

### 2.8 Temporary Event
| Interaction      | Required Metric(s) | Threshold/Condition         | Unlock/Restriction Rule                | Special Cases                | Example Character Profiles         |
|-----------------|--------------------|----------------------------|----------------------------------------|------------------------------|------------------------------------|
| Temporary Event | Temporary Effect, Story | "Blessing of Speed", during festival | Temporarily unlocks time-limited interaction | Effect expiration, event end | Festival participant, unblessed villager |

---

## 3. Temporary Overrides and Special Cases
- **Buffs/Debuffs:** Temporary effects can override progression requirements (e.g., potion grants temporary skill boost).
- **Story Events:** Major story milestones may unlock or lock interactions regardless of progression.
- **Admin Overrides:** Manual intervention can unlock/lock interactions for testing or live events.
- **Daily/Weekly Resets:** Some interactions may become available again after a reset period.

---

## 4. Implementation Notes
- All rules should be implemented as modular, data-driven checks.
- Edge cases (e.g., regression, temporary effects) must be handled gracefully.
- Fallback logic should be provided for ambiguous or missing progression data.
- Mapping tables should be reviewed and updated as new progression mechanics are introduced.

---

## 5. References
- `docs/progression_metrics_impact.md` (from subtask 474.1)
- `docs/interaction-building-event-catalog.md`
- `docs/interaction-building-integration-points.md` 