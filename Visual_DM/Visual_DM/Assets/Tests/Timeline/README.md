# Timeline Visualization PlayMode Tests

This directory contains PlayMode tests for the Timeline visualization and UI controls in Visual_DM.

## Test Coverage
- Node and edge rendering for FeatTimelineVisualizer
- Tooltip display on node hover
- Path highlighting for prerequisite chains on node click
- Gap and cluster marker rendering for feat distribution
- UI control interactions (planned):
  - Category filter toggles
  - Search input and autocomplete
  - Statistics panel updates
  - Pan/zoom camera controls

## Test Data
- Uses mock FeatDataSet with diverse categories, prerequisites, and edge cases
- Includes tests for circular dependencies, missing prerequisites, and feats with no dependencies

## Manual QA Checklist
- All feat nodes are visible and color-coded by category
- Tooltips show correct feat info and follow the mouse
- Clicking a node highlights the full prerequisite path recursively
- Gap/cluster markers appear at correct levels
- UI remains responsive with large feat sets (100+ nodes)
- Statistics panel accurately reflects feat distribution

## Known Limitations
- Some UI controls (filters, search, statistics) are not yet fully covered by automated tests
- Visual regression testing is not automated; manual review recommended for major UI changes
- Camera bounds and responsive layout require further test coverage

## UI Control Interaction Notes
- Filter toggles should update node visibility in real time
- Search input should support partial matches and highlight results
- Statistics panel should update as filters/search are applied
- Pan/zoom should be smooth and not break node/edge alignment

---
For questions or to extend test coverage, contact the Timeline module maintainers. 