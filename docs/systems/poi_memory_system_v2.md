# 🧠 POI Memory System — World Persistence (v2)

## 🔥 Core Concept

POIs (Points of Interest) are not static. They evolve over time through:
- Player interaction (cleared, spared, befriended)
- NPC decisions (residence, departure, death)
- World simulation (ticks, monster incursions, faction expansion)
- Random events (rumors, motifs, disasters)

This system makes the world feel *alive and responsive* without breaking deterministic design.

---

## 📂 Firebase Structure

### `/poi_state/<region>/<poi_id>/evolution_state`

```json
{
  "static_npcs": ["npc_maren", "npc_ferrick"],
  "settlement_growth": "camp",
  "control_status": "cleared",
  "motif_pool": {
    "active_motifs": ["forgotten", "cursed"],
    "entropy_tick": 2,
    "last_rotated": "ISO_DATETIME"
  },
  "state_tags": ["rumored", "cleared", "inhabited"],
  "event_log": [
    { "type": "cleared_by_player", "day": 113, "by": "velra" },
    { "type": "attacked_by_monsters", "day": 125, "result": "defended" },
    { "type": "settlement_growth", "day": 139, "new_state": "village" }
  ],
  "next_event_check": 152,
  "force_reenrich": false
}
```

---

## 🔁 Daily Tick System

### Trigger: `daily_world_tick()`
- Checks `next_event_check` for each POI
- Runs `simulate_poi_day_passage(poi_id)` if due

### Event logic:
- Revert POI to monster control if overrun
- Run combat sim (simple or detailed)
- Add/remove NPCs
- Trigger GPT *only if*:
  - Settlement tier increases
  - New permanent NPCs arrive
  - World event affects the POI
  - `force_reenrich == True`

---

## 🧠 POIs Have Memory Too

- Add `motif_pool` like NPCs:
  - "forgotten", "rebuilt", "contested", "sacred"
- Add `chaos_index` to simulate unpredictability
- Store `memory_log` from notable visits or events

---

## 💥 Combat Simulation Options

### Detailed (Full AI-driven combat)
- Use if POI has < 10 NPCs
- Trigger `resolve_combat_action()` loop

### Simplified (Monte Carlo style)
- Estimate "power score" of monsters vs NPCs
- Random roll + modifiers
- Used in cities, large groups

---

## 🧪 Sample: `simulate_poi_day_passage(poi_id)`

```python
def simulate_poi_day_passage(poi_id):
    state = db.reference(f"/poi_state/.../evolution_state").get()
    if current_day < state["next_event_check"]:
        return

    if state.get("control_status") != "cleared":
        return

    danger = db.reference(f"/poi_state/...").get().get("danger_level", 5)
    attack_roll = random.random()
    if attack_roll < danger * 0.08:
        if npc_loses_battle(poi_id):
            revert_poi_to_monster_control(poi_id)
        else:
            log_event(poi_id, "defended")
    else:
        maybe_grow_settlement(poi_id)
```

---

## ✅ Summary

This system enables your world to:
- React and evolve from player choices
- Persist narrative changes
- Let POIs become *something else* entirely
- Keep track of every important detail, with minimal storage

### GPT Use:
- On clear
- On significant evolution
- On demand (`force_reenrich`)

### Recommended:
- Delete `refresh_cleared_pois()`
- Rely on simulation + control_status tags

---

## 🧭 Future Work

- Tie rumors into POI event logs
- Allow factions to claim and defend POIs
- Expand motif interactions (POIs as thematic characters)
- Track visits, deaths, evolutions as “storylines” in the world log