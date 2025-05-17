# Legendary Drop Formula Documentation

## Overview
This document explains the mathematical formula, implementation, configuration, and design intent for the legendary item drop system in Visual_DM.

---

## 1. Mathematical Basis

The legendary drop probability is calculated as:

```
P = PBase
    + (PLevel * (Level / 20))
    + (PArc * ArcCompletion)
    + (PGlobal * GlobalEventParticipation)
    + (PDifficulty * EncounterDifficulty)
    - (PClassXP * (ClassXPModifier - 1.0))
```

- **PBase**: Base drop probability per eligible event (e.g., 1%)
- **PLevel**: Additional probability scaling with player level
- **PArc**: Bonus for Arc Completion
- **PGlobal**: Bonus for Global Event participation
- **PDifficulty**: Bonus for encounter difficulty
- **PClassXP**: Modifier for class XP rate (faster leveling = lower chance)

**Pity/Bad Luck Protection:**
- If a player goes more than `MinEventsBetweenLegendaries` events without a legendary, probability is increased by `PityBonus` per event.
- Hard cap: no more than one legendary every `MinEventsBetweenLegendaries` events.

---

## 2. Implementation

- **Core Logic:** `LegendaryDropCalculator.RollForLegendaryDrop(PlayerProgressionData, EncounterData, LegendaryDropConfig, LegendaryDropLogger)`
- **Config:** All parameters are set in `LegendaryDropConfig.cs` and can be tuned at runtime.
- **Logging:** All events and drops are logged via `LegendaryDropLogger.cs` for analytics.
- **Integration:** Called from `LootSystem.GenerateLoot` during loot generation.

---

## 3. Configuration Guidelines

- **PBase**: Start with 0.01 (1%). Increase for more frequent drops.
- **PLevel**: 0.02 is typical for linear scaling. Adjust for desired curve.
- **PArc/PGlobal/PDifficulty**: Use 0.2–0.5 for meaningful bonuses.
- **PClassXP**: 0.1–0.3 discourages power-leveling exploits.
- **PityBonus**: 0.05–0.1 per event is standard for bad luck protection.
- **MinEventsBetweenLegendaries**: 5–10 to prevent streaks.

**Tuning:**
- Use simulation results (see `LegendaryDropTest.cs`) to validate and adjust config.
- Target: Median player should receive ~2 legendaries by level 20.
- Adjust for class fairness and event participation.

---

## 4. Game Design Notes

- **Player Experience:**
  - Legendary drops should feel rare but achievable.
  - Pity system ensures no player is left behind.
  - Event and arc bonuses reward engagement.
- **Analytics:**
  - All drops and eligible events are logged for balancing.
  - Use logs to monitor outliers and dry spells.

---

## 5. Developer Notes

- All code is runtime-only, no scene or prefab dependencies.
- All configuration is hot-reloadable for live tuning.
- Extend `LegendaryDropConfig` and `LegendaryDropLogger` for future needs.

---

## 6. Example Config (C#)

```csharp
public class LegendaryDropConfig
{
    public float PBase = 0.01f;
    public float PLevel = 0.02f;
    public float PArc = 0.5f;
    public float PGlobal = 0.3f;
    public float PDifficulty = 0.2f;
    public float PClassXP = 0.2f;
    public float PityBonus = 0.05f;
    public int MinEventsBetweenLegendaries = 5;
}
```

---

## 7. References
- Industry loot system best practices (Blizzard, Bungie, GGG)
- [LegendaryDropCalculator.cs](LegendaryDropCalculator.cs)
- [LegendaryDropConfig.cs](LegendaryDropConfig.cs)
- [LegendaryDropLogger.cs](LegendaryDropLogger.cs)
- [LegendaryDropTest.cs](LegendaryDropTest.cs) 