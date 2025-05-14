# Manual Test Plan: Building Type Template Editor UI

## 1. Launch and Initial State
- **Step:** Launch the Template Editor screen from the main menu.
- **Expected:** Title "Building Type Template Editor" is visible. 'Add Room' and 'Remove Room' buttons are present. Grid is empty.

## 2. Add Room
- **Step:** Click 'Add Room' repeatedly.
- **Expected:** Each click adds a room to the grid, with names incrementing ("Room 1", "Room 2", ...). No more rooms can be added than grid allows (5x5 = 25).

## 3. Remove Room
- **Step:** Select a room cell, then click 'Remove Room'.
- **Expected:** Selected room is removed from the grid. If no room is selected, clicking 'Remove Room' does nothing and does not crash.

## 4. Select and Edit Room
- **Step:** Click on a room cell in the grid.
- **Expected:** Room cell is highlighted. Property editor appears (if implemented). Room name is shown and can be edited (if implemented).

## 5. Deselect Room
- **Step:** Click on an empty cell or outside the grid.
- **Expected:** No room is selected. Property editor disappears.

## 6. Add Beyond Grid Limit
- **Step:** Add rooms until the grid is full, then try to add more.
- **Expected:** No error or crash. Room count does not exceed grid capacity.

## 7. Remove When None Selected
- **Step:** Ensure no room is selected, then click 'Remove Room'.
- **Expected:** No error or crash. No rooms are removed.

## 8. Usability
- **Step:** Use keyboard and mouse to interact with all UI elements.
- **Expected:** All buttons and grid cells respond to input. No lag or unresponsive elements.

## 9. Error Handling
- **Step:** Attempt invalid actions (e.g., remove room when none selected, add room when grid is full).
- **Expected:** UI remains stable. No crashes or unhandled exceptions.

## 10. Preview/Visual Feedback
- **Step:** Select and deselect rooms, observe highlighting and property editor.
- **Expected:** Visual feedback is clear and immediate. Selected room is highlighted. Property editor visibility matches selection state.

## 11. Export/Import/Validation (if implemented)
- **Step:** Use export/import features to save and load templates. Validate template with backend if possible.
- **Expected:** Exported data matches backend schema. Imported templates populate UI correctly. Validation errors are shown to user if present.

---

**Reference:** See `test_template_editor.py` for automated test skeletons covering core logic and state changes. 