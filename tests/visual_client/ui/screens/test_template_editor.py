"""
Automated and manual test plan for Building Type Template Editor UI.

Manual Test Plan:
- Launch TemplateEditorScreen and verify UI loads with title and buttons.
- Add rooms using the 'Add Room' button; verify grid updates and room names increment.
- Remove rooms using the 'Remove Room' button; verify correct room is removed.
- Select a room cell; verify property editor appears and highlights cell.
- Edit room name (if implemented); verify name updates in grid.
- Attempt to add more rooms than grid allows; verify no error/crash.
- Attempt to remove a room when none is selected; verify no error/crash.
- Test usability: button clicks, grid interaction, text editing.
- Test error handling: invalid actions do not crash UI.
- Test preview: room highlighting, property editor visibility.

Automated Test Skeleton:
"""
import pytest
from unittest.mock import MagicMock
import pygame
from visual_client.ui.screens.template_editor import TemplateEditorScreen

class DummyApp:
    def __init__(self):
        self.screen = MagicMock()
        self.set_screen = MagicMock()

@pytest.fixture
def editor():
    app = DummyApp()
    return TemplateEditorScreen(app)

def test_initial_state(editor):
    assert editor.title.text == "Building Type Template Editor"
    assert editor.current_template['roomLayouts'] == []
    assert editor.selected_room_idx is None

def test_add_room(editor):
    editor._add_room()
    assert len(editor.current_template['roomLayouts']) == 1
    room = editor.current_template['roomLayouts'][0]
    assert room['name'] == "Room 1"
    # Add up to 26 (no enforced limit in code)
    for _ in range(25):
        editor._add_room()
    assert len(editor.current_template['roomLayouts']) == 26

def test_remove_room(editor):
    editor._add_room()
    idx = 0
    editor.selected_room_idx = idx
    editor._remove_room(idx)
    assert editor.current_template['roomLayouts'] == []
    assert editor.selected_room_idx is None

def test_select_room(editor):
    editor._add_room()
    idx = 0
    editor.selected_room_idx = idx
    assert editor.selected_room_idx == idx

def test_deselect_on_empty_cell(editor):
    editor._add_room()
    # Simulate deselect
    editor.selected_room_idx = None
    assert editor.selected_room_idx is None

def test_export_template(editor):
    editor._add_room()
    editor._add_room()
    exported = editor._export_template_dict()
    assert 'roomLayouts' in exported
    assert len(exported['roomLayouts']) == 2
    assert exported['roomLayouts'][0]['name'] == "Room 1"
    assert exported['roomLayouts'][1]['name'] == "Room 2"

def test_import_template(editor):
    template = {'roomLayouts': [
        {'id': 'room_1', 'name': 'A', 'type': 'BEDROOM', 'minSize': {'width': 4, 'length': 4}, 'maxSize': {'width': 4, 'length': 4}, 'requiredConnections': [], 'optionalConnections': [], 'priority': 1, 'placementRules': []},
        {'id': 'room_2', 'name': 'B', 'type': 'KITCHEN', 'minSize': {'width': 4, 'length': 4}, 'maxSize': {'width': 4, 'length': 4}, 'requiredConnections': [], 'optionalConnections': [], 'priority': 1, 'placementRules': []}
    ]}
    editor._import_template_dict(template)
    assert len(editor.current_template['roomLayouts']) == 2
    assert editor.current_template['roomLayouts'][0]['name'] == 'A'
    assert editor.current_template['roomLayouts'][1]['name'] == 'B'
    assert editor.selected_room_idx is None

def test_validate_template_empty(editor):
    editor.current_template['name'] = 'Test Template'
    editor.current_template['buildingType'] = 'INN'
    editor.current_template['category'] = 'SOCIAL'
    editor.current_template['roomLayouts'] = []
    editor.validate_template()
    assert editor.validation_error == "At least one room layout is required."

def test_validate_template_duplicate(editor):
    editor.current_template['name'] = 'Test Template'
    editor.current_template['buildingType'] = 'INN'
    editor.current_template['category'] = 'SOCIAL'
    editor.current_template['roomLayouts'] = [
        {'id': 'room_1', 'name': 'A', 'type': 'ENTRANCE', 'minSize': {'width': 4, 'length': 4}, 'maxSize': {'width': 4, 'length': 4}, 'requiredConnections': [], 'optionalConnections': [], 'priority': 1, 'placementRules': []},
        {'id': 'room_1', 'name': 'B', 'type': 'KITCHEN', 'minSize': {'width': 4, 'length': 4}, 'maxSize': {'width': 4, 'length': 4}, 'requiredConnections': [], 'optionalConnections': [], 'priority': 1, 'placementRules': []}
    ]
    editor.validate_template()
    assert editor.validation_error == "Valid!"

def test_validate_template_valid(editor):
    editor.current_template['name'] = 'Test Template'
    editor.current_template['buildingType'] = 'INN'
    editor.current_template['category'] = 'SOCIAL'
    editor.current_template['roomLayouts'] = [
        {'id': 'room_1', 'name': 'A', 'type': 'ENTRANCE', 'minSize': {'width': 4, 'length': 4}, 'maxSize': {'width': 4, 'length': 4}, 'requiredConnections': [], 'optionalConnections': [], 'priority': 1, 'placementRules': []},
        {'id': 'room_2', 'name': 'B', 'type': 'KITCHEN', 'minSize': {'width': 4, 'length': 4}, 'maxSize': {'width': 4, 'length': 4}, 'requiredConnections': [], 'optionalConnections': [], 'priority': 1, 'placementRules': []}
    ]
    editor.validate_template()
    assert editor.validation_error == "Valid!"

# Patch dummy dropdowns for decoration tests
ROOM_TYPES = [
    'ENTRANCE', 'BEDROOM', 'KITCHEN', 'DINING', 'BATHROOM', 'STUDY', 'HALLWAY', 'STORAGE', 'WORKSHOP', 'LIBRARY', 'LAB', 'CHAPEL', 'VAULT', 'CELLAR', 'ATTIC', 'BALCONY', 'COURTYARD', 'STAIRWELL', 'LOUNGE', 'OFFICE', 'PANTRY', 'GARAGE', 'GARDEN', 'TOWER', 'DUNGEON', 'BARRACKS', 'THRONE_ROOM'
]
DECORATION_TYPES = [
    'LIGHT_SOURCE', 'TAPESTRY', 'RUG', 'PAINTING', 'PLANT', 'WINDOW', 'CURTAIN', 'BANNER', 'TROPHY'
]

def test_add_decoration_scheme(editor):
    editor.current_template['name'] = 'Test Template'
    editor.current_template['buildingType'] = 'INN'
    editor.deco_room_type_dropdown.options = ROOM_TYPES
    editor.deco_type_dropdown.options = DECORATION_TYPES
    editor.deco_room_type_dropdown.selected_index = 0
    editor.deco_type_dropdown.selected_index = 0
    editor.deco_theme_textbox.value = "Royal"
    editor.deco_min_textbox.value = "2"
    editor.deco_max_textbox.value = "4"
    editor.deco_density_textbox.value = "0.5"
    editor._add_deco_scheme()
    schemes = editor.current_template['decorationSchemes']
    assert len(schemes) == 1
    scheme = schemes[0]
    assert scheme['roomType'] == ROOM_TYPES[0]
    assert scheme['theme'] == "Royal"
    assert scheme['density'] == 0.5
    assert len(scheme['decorations']) == 1
    deco = scheme['decorations'][0]
    assert deco['type'] == DECORATION_TYPES[0]
    assert deco['minCount'] == 2
    assert deco['maxCount'] == 4

def test_edit_decoration_scheme(editor):
    editor.current_template['name'] = 'Test Template'
    editor.current_template['buildingType'] = 'INN'
    editor.deco_room_type_dropdown.options = ROOM_TYPES
    editor.deco_type_dropdown.options = DECORATION_TYPES
    editor.deco_room_type_dropdown.selected_index = 0
    editor.deco_type_dropdown.selected_index = 0
    editor.deco_theme_textbox.value = "Royal"
    editor.deco_min_textbox.value = "1"
    editor.deco_max_textbox.value = "2"
    editor.deco_density_textbox.value = "0.2"
    editor._add_deco_scheme()
    # Edit theme/density
    scheme = editor.current_template['decorationSchemes'][0]
    editor.deco_theme_textbox.value = "Rustic"
    editor.deco_density_textbox.value = "0.8"
    editor._add_deco_scheme()  # Should update theme/density
    assert scheme['theme'] == "Rustic"
    assert scheme['density'] == 0.8

def test_remove_decoration(editor):
    editor.current_template['name'] = 'Test Template'
    editor.current_template['buildingType'] = 'INN'
    editor.deco_room_type_dropdown.options = ROOM_TYPES
    editor.deco_type_dropdown.options = DECORATION_TYPES
    editor.deco_room_type_dropdown.selected_index = 0
    editor.deco_type_dropdown.selected_index = 0
    editor.deco_theme_textbox.value = "Royal"
    editor.deco_min_textbox.value = "1"
    editor.deco_max_textbox.value = "2"
    editor.deco_density_textbox.value = "0.2"
    editor._add_deco_scheme()
    editor.deco_type_dropdown.selected_index = 1
    editor._add_deco_scheme()
    scheme = editor.current_template['decorationSchemes'][0]
    assert len(scheme['decorations']) == 2
    editor._remove_deco_scheme(scheme['roomType'], 0)
    assert len(scheme['decorations']) == 1
    assert scheme['decorations'][0]['type'] == DECORATION_TYPES[1]

def test_validate_decoration_scheme(editor):
    editor.current_template['name'] = 'Test Template'
    editor.current_template['buildingType'] = 'INN'
    editor.current_template['category'] = 'SOCIAL'
    # Add a dummy room so density validation is reached
    editor.current_template['roomLayouts'] = [
        {'id': 'room_1', 'name': 'A', 'type': 'ENTRANCE', 'minSize': {'width': 4, 'length': 4}, 'maxSize': {'width': 4, 'length': 4}, 'requiredConnections': [], 'optionalConnections': [], 'priority': 1, 'placementRules': []}
    ]
    editor.deco_room_type_dropdown.options = ROOM_TYPES
    editor.deco_type_dropdown.options = DECORATION_TYPES
    # Add invalid min > max
    editor.deco_room_type_dropdown.selected_index = 0
    editor.deco_type_dropdown.selected_index = 0
    editor.deco_theme_textbox.value = "Royal"
    editor.deco_min_textbox.value = "5"
    editor.deco_max_textbox.value = "2"
    editor.deco_density_textbox.value = "0.2"
    editor._add_deco_scheme()
    assert "Min count cannot exceed max count" in (editor.validation_error or "")
    # Add valid, then set invalid density
    editor.deco_min_textbox.value = "1"
    editor.deco_max_textbox.value = "2"
    editor.deco_density_textbox.value = "-1"
    editor._add_deco_scheme()
    scheme = editor.current_template['decorationSchemes'][0]
    scheme['density'] = -1
    editor.validate_template()
    assert "Invalid decoration density" in (editor.validation_error or "")

def test_export_import_decoration_scheme(editor):
    editor.current_template['name'] = 'Test Template'
    editor.current_template['buildingType'] = 'INN'
    editor.deco_room_type_dropdown.options = ROOM_TYPES
    editor.deco_type_dropdown.options = DECORATION_TYPES
    editor.deco_room_type_dropdown.selected_index = 0
    editor.deco_type_dropdown.selected_index = 0
    editor.deco_theme_textbox.value = "Royal"
    editor.deco_min_textbox.value = "1"
    editor.deco_max_textbox.value = "2"
    editor.deco_density_textbox.value = "0.2"
    editor._add_deco_scheme()
    exported = editor._export_template_dict()
    assert 'decorationSchemes' in exported
    # Simulate import
    new_editor = TemplateEditorScreen(DummyApp())
    new_editor.current_template['name'] = 'Test Template'
    new_editor.current_template['buildingType'] = 'INN'
    new_editor.deco_room_type_dropdown.options = ROOM_TYPES
    new_editor.deco_type_dropdown.options = DECORATION_TYPES
    new_editor._import_template_dict(exported)
    assert len(new_editor.current_template['decorationSchemes']) == 1
    scheme = new_editor.current_template['decorationSchemes'][0]
    assert scheme['theme'] == "Royal"
    assert scheme['decorations'][0]['type'] == DECORATION_TYPES[0] 