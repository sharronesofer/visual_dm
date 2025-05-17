# UI Communication for Progression-Locked Interactions

**Document ID:** UI-PROG-LOCK-001
**Last Updated:** 2025-05-16

---

## 1. Overview
This document specifies how the user interface should communicate locked or unavailable interactions to players, ensuring clarity, consistency, and accessibility.

---

## 2. Visual Indicators
- Grayed-out (desaturated) interaction options for unavailable/locked content
- Lock icon overlay on locked interactions
- Color coding: green (available), yellow (nearly available), red/gray (locked)
- Subtle animation (e.g., pulsing or fade-in) when an interaction becomes newly available

---

## 3. Tooltip Content
- On hover/focus, display a tooltip with specific requirements (e.g., "Requires Level 10 and Reputation > 50")
- If multiple requirements, list all with checkmarks (✓) for met and crosses (✗) for unmet
- For temporary locks (e.g., event ended), show reason ("Event expired")

---

## 4. Dynamic UI Elements
- UI updates in real-time as progression changes (e.g., after leveling up, completing a quest)
- Notification banner or toast when a previously locked interaction becomes available
- Optional sound cue for major unlocks

---

## 5. Accessibility Considerations
- All color indicators must have shape/icon redundancy for colorblind users
- Tooltips and lock icons must be screen-reader accessible (ARIA labels, descriptive text)
- Sufficient contrast for all UI elements

---

## 6. Wireframe/Mockup Guidelines
- **Dialogue menu:** Locked options grayed out with lock icon, tooltip on hover
- **Inventory:** Locked vendor items show lock icon and tooltip
- **World interaction:** Locked objects display lock icon and requirement tooltip on approach
- UI should be modular to support new interaction types and requirements

---

## 7. Feedback Mechanisms
- Animation and/or sound when an interaction unlocks
- Visual highlight or pulse for newly available options
- Optional notification log for recent unlocks

---

## 8. Implementation Notes
- All UI elements and behaviors should be documented in a design system for consistency and future extensibility
- UI must support dynamic updates and accessibility standards

---

## 9. References
- `docs/progression_interaction_mapping.md`
- `docs/progression_metrics_impact.md` 