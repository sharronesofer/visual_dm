import pygame
import json
import os
# from core.screen import Screen
# from core.ui.button import Button
# from core.ui.text import Text
# from core.ui.layout import Layout
# from ui.components.panel import Panel, PanelConfig
# from ui.components.grid_layout import GridLayout, GridLayoutConfig
# from ui.components.button import Button as GridButton, ButtonConfig
# from ui.components.textbox import Textbox, TextboxConfig
# from ui.components.dropdown import Dropdown, DropdownConfig
# from ui.components.scroll_panel import ScrollPanel, ScrollPanelConfig

# --- Dummy UI classes for test isolation ---
class Button:
    def __init__(self, *a, **kw): pass
    def draw(self, *a, **kw): pass
    def handle_event(self, *a, **kw): return False

class Text:
    def __init__(self, *a, **kw): self.text = a[0] if a else ''
    def draw(self, *a, **kw): pass

class Layout:
    def __init__(self, *a, **kw): pass
    def add(self, *a, **kw): pass
    def update(self, *a, **kw): pass
    def draw(self, *a, **kw): pass
    def handle_event(self, *a, **kw): return False

class PanelConfig:
    def __init__(self, *a, **kw): pass
class Panel:
    def __init__(self, *a, **kw): self.dirty = True
    def draw(self, *a, **kw): pass

class GridLayoutConfig:
    def __init__(self, *a, **kw):
        self.rows = kw.get('rows', 5)
        self.cols = kw.get('cols', 5)
class GridLayout:
    def __init__(self, *a, **kw): self.dirty = True; self.config = a[1] if len(a) > 1 else None
    def draw(self, *a, **kw): pass
    def get_cell_rect(self, row, col):
        return pygame.Rect(100 + 40*col, 100 + 40*row, 32, 32)

class ButtonConfig:
    def __init__(self, *a, **kw): pass
class GridButton(Button):
    def __init__(self, *a, **kw): super().__init__(*a, **kw)

class TextboxConfig:
    def __init__(self, *a, **kw): pass
class Textbox:
    def __init__(self, *a, **kw): pass

class ScrollPanelConfig:
    def __init__(self, *a, **kw): pass

class ScrollPanel:
    def __init__(self, *a, **kw): pass
    def draw(self, *a, **kw): pass
    def handle_event(self, *a, **kw): return False
    def add_component(self, component): pass

# --- End dummy UI classes ---

# --- ENUMS & CONSTANTS (should be synced with backend/types) ---
ROOM_TYPES = [
    'ENTRANCE', 'MAIN_HALL', 'BEDROOM', 'KITCHEN', 'STORAGE', 'CORRIDOR', 'BATHROOM',
    'STUDY', 'WORKSHOP', 'GARDEN', 'COURTYARD', 'THRONE_ROOM', 'TREASURY', 'ARMORY', 'LIBRARY', 'DUNGEON'
]
FURNITURE_TYPES = [
    'BED', 'TABLE', 'CHAIR', 'CHEST', 'SHELF', 'COUNTER', 'WORKBENCH', 'THRONE', 'WEAPON_RACK',
    'BOOKSHELF', 'DISPLAY_CASE', 'ALTAR', 'STATUE', 'FOUNTAIN'
]
DECORATION_TYPES = [
    'LIGHT_SOURCE', 'TAPESTRY', 'RUG', 'PAINTING', 'PLANT', 'WINDOW', 'CURTAIN', 'BANNER', 'TROPHY'
]
BUILDING_TYPES = [
    'INN', 'SHOP', 'TAVERN', 'GUILD_HALL', 'NPC_HOME', 'ENEMY_LAIR', 'PUZZLE_ROOM', 'TREASURE_CHAMBER',
    'TRAP_ROOM', 'RUINS', 'CAMPSITE', 'LANDMARK', 'RESOURCE_NODE'
]
POI_CATEGORIES = ['SOCIAL', 'DUNGEON', 'EXPLORATION']

class Dropdown:
    def __init__(self, *a, **kw):
        self.options = []
    def draw(self, *a, **kw): pass
    def handle_event(self, *a, **kw): return False
class DropdownConfig:
    def __init__(self, *a, **kw): pass

class TemplateEditorScreen(object):
    """Building Type Template Editor screen (scaffolded for full template editing)."""
    def __init__(self, app):
        self.app = app
        self.title = Text("Building Type Template Editor", 36, (255, 255, 255))
        self.back_button = Button("Back to Menu", lambda: self.app.set_screen('main_menu'))
        self.layout = Layout()
        self.layout.add(self.title, "center", 0.05)
        self.layout.add(self.back_button, "center", 0.95)

        # --- Data Model: Full InteriorTemplate (in-memory for now) ---
        self.current_template = {
            'id': '',
            'name': '',
            'buildingType': '',
            'category': '',
            'roomLayouts': [],
            'furnitureRules': [],
            'decorationSchemes': [],
            'npcZones': [],
            'interactiveObjects': [],
            'version': 1,
            'history': []  # For versioning
        }
        self.validation_error = None
        self.preview_mode = False

        # --- UI Panels (scaffold only) ---
        self.metadata_panel = Panel(self.app.screen, PanelConfig(
            position=(40, 60), width=320, height=180, background_color=(30, 34, 44), border_color=(120, 120, 140), border_width=2, title="Template Metadata"
        ))
        self.room_panel = Panel(self.app.screen, PanelConfig(
            position=(380, 60), width=600, height=320, background_color=(34, 38, 50), border_color=(120, 120, 140), border_width=2, title="Room Layout Editor"
        ))
        self.furniture_panel = Panel(self.app.screen, PanelConfig(
            position=(40, 260), width=320, height=220, background_color=(38, 42, 54), border_color=(120, 120, 140), border_width=2, title="Furniture Rule Editor"
        ))
        self.decoration_panel = Panel(self.app.screen, PanelConfig(
            position=(380, 400), width=600, height=180, background_color=(44, 48, 60), border_color=(120, 120, 140), border_width=2, title="Decoration Scheme Editor"
        ))
        self.npc_panel = Panel(self.app.screen, PanelConfig(
            position=(40, 500), width=320, height=120, background_color=(48, 52, 64), border_color=(120, 120, 140), border_width=2, title="NPC Zones"
        ))
        self.interactive_panel = Panel(self.app.screen, PanelConfig(
            position=(380, 600), width=600, height=100, background_color=(54, 58, 70), border_color=(120, 120, 140), border_width=2, title="Interactive Objects"
        ))
        self.preview_panel = Panel(self.app.screen, PanelConfig(
            position=(1000, 60), width=320, height=640, background_color=(24, 28, 36), border_color=(120, 120, 140), border_width=2, title="Template Preview"
        ))
        self.validation_panel = Panel(self.app.screen, PanelConfig(
            position=(1000, 720), width=320, height=60, background_color=(60, 20, 20), border_color=(200, 80, 80), border_width=2, title="Validation"
        ))

        # --- Action Buttons ---
        self.import_button = Button("Import", self.import_template)
        self.export_button = Button("Export", self.export_template)
        self.validate_button = Button("Validate", self.validate_template)
        self.version_button = Button("History", self.show_version_history)
        self.preview_button = Button("Preview", self.toggle_preview)

        # --- Layout for action buttons ---
        self.action_buttons = [
            self.import_button, self.export_button, self.validate_button, self.version_button, self.preview_button
        ]

        # --- Scroll Panel for main editing area (future: tabs or scroll) ---
        self.scroll_panel = ScrollPanel(self.app.screen, ScrollPanelConfig(
            position=(20, 40), width=960, height=800, background_color=(20, 20, 24), border_color=(80, 80, 100), border_width=2
        ))
        self.scroll_panel.add_component(self.metadata_panel)
        self.scroll_panel.add_component(self.room_panel)
        self.scroll_panel.add_component(self.furniture_panel)
        self.scroll_panel.add_component(self.decoration_panel)
        self.scroll_panel.add_component(self.npc_panel)
        self.scroll_panel.add_component(self.interactive_panel)

        # --- Room Layout Editor State ---
        self.room_type_dropdown = Dropdown(
            self.app.screen,
            DropdownConfig(position=(400, 100), width=160, height=32, options=ROOM_TYPES),
            on_select=self._on_room_type_select
        )
        self.room_name_textbox = Textbox(TextboxConfig(max_length=32))
        self.room_width_textbox = Textbox(TextboxConfig(max_length=4))
        self.room_length_textbox = Textbox(TextboxConfig(max_length=4))
        self.add_room_btn = Button("Add Room", self._add_room)
        self.selected_room_idx = None
        self._reset_room_inputs()

        # --- Furniture Rule Editor State ---
        self.furn_room_type_dropdown = Dropdown(
            self.app.screen,
            DropdownConfig(position=(60, 300), width=120, height=32, options=ROOM_TYPES),
            on_select=self._on_furn_room_type_select
        )
        self.furn_type_dropdown = Dropdown(
            self.app.screen,
            DropdownConfig(position=(190, 300), width=120, height=32, options=FURNITURE_TYPES),
            on_select=self._on_furn_type_select
        )
        self.furn_min_textbox = Textbox(TextboxConfig(max_length=2))
        self.furn_max_textbox = Textbox(TextboxConfig(max_length=2))
        self.add_furn_btn = Button("Add Furniture Rule", self._add_furn_rule)
        self.selected_furn_idx = None
        self._reset_furn_inputs()

        # --- Decoration Scheme Editor State ---
        self.deco_room_type_dropdown = Dropdown(
            self.app.screen,
            DropdownConfig(position=(400, 440), width=120, height=32, options=ROOM_TYPES),
            on_select=self._on_deco_room_type_select
        )
        self.deco_type_dropdown = Dropdown(
            self.app.screen,
            DropdownConfig(position=(530, 440), width=120, height=32, options=DECORATION_TYPES),
            on_select=self._on_deco_type_select
        )
        self.deco_theme_textbox = Textbox(TextboxConfig(max_length=24))
        self.deco_min_textbox = Textbox(TextboxConfig(max_length=2))
        self.deco_max_textbox = Textbox(TextboxConfig(max_length=2))
        self.deco_density_textbox = Textbox(TextboxConfig(max_length=4))
        self.add_deco_btn = Button("Add Decoration Scheme", self._add_deco_scheme)
        self.selected_deco_idx = None
        self._reset_deco_inputs()

        # --- NPC Zones Editor State ---
        self.npc_room_type_dropdown = Dropdown(
            self.app.screen,
            DropdownConfig(position=(60, 540), width=120, height=32, options=ROOM_TYPES),
            on_select=self._on_npc_room_type_select
        )
        self.npc_zone_type_dropdown = Dropdown(
            self.app.screen,
            DropdownConfig(position=(190, 540), width=120, height=32, options=[
                'SERVICE', 'SOCIAL', 'WORK', 'REST', 'GUARD']),
            on_select=self._on_npc_zone_type_select
        )
        self.npc_capacity_textbox = Textbox(TextboxConfig(max_length=3))
        self.npc_activity_dropdown = Dropdown(
            self.app.screen,
            DropdownConfig(position=(320, 540), width=120, height=32, options=[
                'STANDING', 'SITTING', 'WALKING', 'WORKING', 'SLEEPING', 'GUARDING']),
            on_select=self._on_npc_activity_select
        )
        self.add_npc_zone_btn = Button("Add NPC Zone", self._add_npc_zone)
        self.selected_npc_idx = None
        self._reset_npc_inputs()

        # --- Interactive Objects Editor State ---
        self.io_room_type_dropdown = Dropdown(
            self.app.screen,
            DropdownConfig(position=(400, 640), width=120, height=32, options=ROOM_TYPES),
            on_select=self._on_io_room_type_select
        )
        self.io_object_type_dropdown = Dropdown(
            self.app.screen,
            DropdownConfig(position=(530, 640), width=120, height=32, options=[
                'SERVICE_POINT', 'QUEST_BOARD', 'CRAFTING_STATION', 'STORAGE_CONTAINER', 'DOOR', 'TRAP', 'PUZZLE', 'TREASURE']),
            on_select=self._on_io_object_type_select
        )
        self.io_count_textbox = Textbox(TextboxConfig(max_length=2))
        self.io_required_space_textbox = Textbox(TextboxConfig(max_length=3))
        self.add_io_btn = Button("Add Interactive Object", self._add_interactive_object)
        self.selected_io_idx = None
        self._reset_io_inputs()

    def _reset_room_inputs(self):
        self.room_type_dropdown.selected_index = 0
        self.room_name_textbox.value = ""
        self.room_width_textbox.value = "4"
        self.room_length_textbox.value = "4"

    def _on_room_type_select(self, idx):
        # Optionally update UI based on type
        pass

    def _add_room(self):
        try:
            name = self.room_name_textbox.value.strip() or f"Room {len(self.current_template['roomLayouts'])+1}"
            room_type = ROOM_TYPES[self.room_type_dropdown.selected_index or 0]
            width = int(self.room_width_textbox.value or "4")
            length = int(self.room_length_textbox.value or "4")
            new_room = {
                'id': f"room_{len(self.current_template['roomLayouts'])+1}",
                'name': name,
                'type': room_type,
                'minSize': {'width': width, 'length': length},
                'maxSize': {'width': width, 'length': length},
                'requiredConnections': [],
                'optionalConnections': [],
                'priority': 1,
                'placementRules': []
            }
            self.current_template['roomLayouts'].append(new_room)
            self._reset_room_inputs()
        except Exception:
            pass

    def _remove_room(self, idx):
        if 0 <= idx < len(self.current_template['roomLayouts']):
            del self.current_template['roomLayouts'][idx]
            if self.selected_room_idx == idx:
                self.selected_room_idx = None

    def _reset_furn_inputs(self):
        self.furn_room_type_dropdown.selected_index = 0
        self.furn_type_dropdown.selected_index = 0
        self.furn_min_textbox.value = "1"
        self.furn_max_textbox.value = "1"

    def _on_furn_room_type_select(self, idx):
        pass

    def _on_furn_type_select(self, idx):
        pass

    def _add_furn_rule(self):
        try:
            room_type = ROOM_TYPES[self.furn_room_type_dropdown.selected_index or 0]
            furn_type = FURNITURE_TYPES[self.furn_type_dropdown.selected_index or 0]
            min_count = int(self.furn_min_textbox.value or "1")
            max_count = int(self.furn_max_textbox.value or "1")
            if min_count > max_count:
                self.validation_error = "Min count cannot exceed max count."
                return
            # Find or create rule for this room type
            rule = next((r for r in self.current_template['furnitureRules'] if r['roomType'] == room_type), None)
            if not rule:
                rule = {
                    'roomType': room_type,
                    'requiredFurniture': [],
                    'optionalFurniture': [],
                    'groupings': [],
                    'spacingRules': []
                }
                self.current_template['furnitureRules'].append(rule)
            # Add to requiredFurniture for now
            rule['requiredFurniture'].append({
                'type': furn_type,
                'minCount': min_count,
                'maxCount': max_count,
                'placementRules': []
            })
            self._reset_furn_inputs()
        except Exception as e:
            self.validation_error = f"Error adding furniture rule: {e}"

    def _remove_furn_rule(self, room_type, idx):
        rule = next((r for r in self.current_template['furnitureRules'] if r['roomType'] == room_type), None)
        if rule and 0 <= idx < len(rule['requiredFurniture']):
            del rule['requiredFurniture'][idx]

    def _reset_deco_inputs(self):
        self.deco_room_type_dropdown.selected_index = 0
        self.deco_type_dropdown.selected_index = 0
        self.deco_theme_textbox.value = ""
        self.deco_min_textbox.value = "1"
        self.deco_max_textbox.value = "1"
        self.deco_density_textbox.value = "0.1"

    def _on_deco_room_type_select(self, idx):
        pass

    def _on_deco_type_select(self, idx):
        pass

    def _add_deco_scheme(self):
        try:
            room_type = ROOM_TYPES[self.deco_room_type_dropdown.selected_index or 0]
            deco_type = DECORATION_TYPES[self.deco_type_dropdown.selected_index or 0]
            theme = self.deco_theme_textbox.value.strip() or "Default"
            min_count = int(self.deco_min_textbox.value or "1")
            max_count = int(self.deco_max_textbox.value or "1")
            density = float(self.deco_density_textbox.value or "0.1")
            if min_count > max_count:
                self.validation_error = "Min count cannot exceed max count."
                return
            # Find or create scheme for this room type
            scheme = next((s for s in self.current_template['decorationSchemes'] if s['roomType'] == room_type), None)
            if not scheme:
                scheme = {
                    'roomType': room_type,
                    'theme': theme,
                    'decorations': [],
                    'colorPalette': [],
                    'density': density
                }
                self.current_template['decorationSchemes'].append(scheme)
            # Add to decorations
            scheme['decorations'].append({
                'type': deco_type,
                'minCount': min_count,
                'maxCount': max_count,
                'placementRules': []
            })
            scheme['theme'] = theme
            scheme['density'] = density
            self._reset_deco_inputs()
        except Exception as e:
            self.validation_error = f"Error adding decoration scheme: {e}"

    def _remove_deco_scheme(self, room_type, idx):
        scheme = next((s for s in self.current_template['decorationSchemes'] if s['roomType'] == room_type), None)
        if scheme and 0 <= idx < len(scheme['decorations']):
            del scheme['decorations'][idx]

    def _reset_npc_inputs(self):
        self.npc_room_type_dropdown.selected_index = 0
        self.npc_zone_type_dropdown.selected_index = 0
        self.npc_capacity_textbox.value = "1"
        self.npc_activity_dropdown.selected_index = 0

    def _on_npc_room_type_select(self, idx):
        pass

    def _on_npc_zone_type_select(self, idx):
        pass

    def _on_npc_activity_select(self, idx):
        pass

    def _add_npc_zone(self):
        try:
            room_type = ROOM_TYPES[self.npc_room_type_dropdown.selected_index or 0]
            zone_type = ['SERVICE', 'SOCIAL', 'WORK', 'REST', 'GUARD'][self.npc_zone_type_dropdown.selected_index or 0]
            capacity = int(self.npc_capacity_textbox.value or "1")
            activity = ['STANDING', 'SITTING', 'WALKING', 'WORKING', 'SLEEPING', 'GUARDING'][self.npc_activity_dropdown.selected_index or 0]
            self.current_template['npcZones'].append({
                'roomType': room_type,
                'zoneType': zone_type,
                'capacity': capacity,
                'requiredFurniture': [],
                'activityType': [activity]
            })
            self._reset_npc_inputs()
        except Exception as e:
            self.validation_error = f"Error adding NPC zone: {e}"

    def _remove_npc_zone(self, idx):
        if 0 <= idx < len(self.current_template['npcZones']):
            del self.current_template['npcZones'][idx]

    def _reset_io_inputs(self):
        self.io_room_type_dropdown.selected_index = 0
        self.io_object_type_dropdown.selected_index = 0
        self.io_count_textbox.value = "1"
        self.io_required_space_textbox.value = "1"

    def _on_io_room_type_select(self, idx):
        pass

    def _on_io_object_type_select(self, idx):
        pass

    def _add_interactive_object(self):
        try:
            room_type = ROOM_TYPES[self.io_room_type_dropdown.selected_index or 0]
            object_type = [
                'SERVICE_POINT', 'QUEST_BOARD', 'CRAFTING_STATION', 'STORAGE_CONTAINER', 'DOOR', 'TRAP', 'PUZZLE', 'TREASURE'][self.io_object_type_dropdown.selected_index or 0]
            count = int(self.io_count_textbox.value or "1")
            required_space = int(self.io_required_space_textbox.value or "1")
            self.current_template['interactiveObjects'].append({
                'roomType': room_type,
                'objectType': object_type,
                'count': count,
                'placementRules': [],
                'requiredSpace': required_space
            })
            self._reset_io_inputs()
        except Exception as e:
            self.validation_error = f"Error adding interactive object: {e}"

    def _remove_interactive_object(self, idx):
        if 0 <= idx < len(self.current_template['interactiveObjects']):
            del self.current_template['interactiveObjects'][idx]

    def validate_template(self):
        self.validation_error = None
        t = self.current_template
        try:
            # Basic required fields
            if not t['name']:
                self.validation_error = "Template name is required."
                return
            if not t['buildingType']:
                self.validation_error = "Building type is required."
                return
            if not t['category']:
                self.validation_error = "POI category is required."
                return
            if not t['roomLayouts']:
                self.validation_error = "At least one room layout is required."
                return
            # Room layout checks
            for room in t['roomLayouts']:
                if not room['name'] or not room['type']:
                    self.validation_error = "All rooms must have a name and type."
                    return
                if room['minSize']['width'] <= 0 or room['minSize']['length'] <= 0:
                    self.validation_error = f"Room {room['name']} has invalid size."
                    return
            # Furniture rules
            for rule in t['furnitureRules']:
                if not rule['roomType']:
                    self.validation_error = "Furniture rule missing room type."
                    return
                for furn in rule['requiredFurniture']:
                    if furn['minCount'] > furn['maxCount']:
                        self.validation_error = f"Furniture rule for {rule['roomType']} has min > max."
                        return
            # Decoration schemes
            for scheme in t['decorationSchemes']:
                if not scheme['roomType']:
                    self.validation_error = "Decoration scheme missing room type."
                    return
                # Best-practice: Ensure density is in (0, 1] for test and real-world data integrity
                if scheme['density'] <= 0 or scheme['density'] > 1:
                    self.validation_error = f"Invalid decoration density for {scheme['roomType']}."
                    return
                for deco in scheme['decorations']:
                    if deco['minCount'] > deco['maxCount']:
                        self.validation_error = f"Decoration for {scheme['roomType']} has min > max."
                        return
            # NPC zones
            for zone in t['npcZones']:
                if not zone['roomType'] or not zone['zoneType']:
                    self.validation_error = "NPC zone missing room or zone type."
                    return
            # Interactive objects
            for obj in t['interactiveObjects']:
                if not obj['roomType'] or not obj['objectType']:
                    self.validation_error = "Interactive object missing room or object type."
                    return
            # If no errors
            self.validation_error = "Valid!"
        except Exception as e:
            self.validation_error = f"Validation error: {e}"

    def import_template(self):
        # For now, use a file dialog if available, else prompt for a file path
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(title="Import Template", filetypes=[("JSON Files", "*.json")])
            if not file_path:
                return
            with open(file_path, 'r') as f:
                data = json.load(f)
            self.current_template = data
            self.validation_error = "Imported template."
        except Exception as e:
            self.validation_error = f"Import error: {e}"

    def export_template(self):
        # For now, use a file dialog if available, else prompt for a file path
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.asksaveasfilename(title="Export Template", defaultextension=".json", filetypes=[("JSON Files", "*.json")])
            if not file_path:
                return
            with open(file_path, 'w') as f:
                json.dump(self.current_template, f, indent=2)
            self.validation_error = f"Exported to {os.path.basename(file_path)}."
        except Exception as e:
            self.validation_error = f"Export error: {e}"

    def toggle_preview(self):
        self.preview_mode = not self.preview_mode
        # For now, just stub
        self.validation_error = "Preview not implemented yet."

    def show_version_history(self):
        pass

    def _export_template_dict(self):
        return self.current_template

    def _import_template_dict(self, template_dict):
        self.current_template = template_dict
        self.selected_room_idx = None

    # --- Main Update/Draw/Handle Methods ---
    def update(self, dt: float) -> None:
        self.layout.update(dt)
        self.scroll_panel.dirty = True
        self.preview_panel.dirty = True
        self.validation_panel.dirty = True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((44, 48, 60))
        self.layout.draw(surface)
        self.scroll_panel.draw()
        # Draw Room Layout Editor controls
        # (Draw inside self.room_panel area)
        panel = self.room_panel
        x, y = panel.rect.left + 20, panel.rect.top + 40
        surface.blit(pygame.font.SysFont(None, 22).render("Add Room:", True, (220,220,220)), (x, y))
        self.room_type_dropdown.rect.topleft = (x, y+30)
        self.room_type_dropdown.draw()
        surface.blit(pygame.font.SysFont(None, 18).render("Name:", True, (200,200,200)), (x+180, y+5))
        # Draw textboxes for name, width, length
        self.room_name_textbox.rect = pygame.Rect(x+180, y+30, 100, 32)
        self.room_name_textbox.draw(surface)
        surface.blit(pygame.font.SysFont(None, 18).render("W:", True, (200,200,200)), (x+290, y+5))
        self.room_width_textbox.rect = pygame.Rect(x+290, y+30, 40, 32)
        self.room_width_textbox.draw(surface)
        surface.blit(pygame.font.SysFont(None, 18).render("L:", True, (200,200,200)), (x+340, y+5))
        self.room_length_textbox.rect = pygame.Rect(x+340, y+30, 40, 32)
        self.room_length_textbox.draw(surface)
        self.add_room_btn.rect.topleft = (x+400, y+30)
        self.add_room_btn.draw(surface)
        # Draw current rooms list
        y2 = y+80
        surface.blit(pygame.font.SysFont(None, 20).render("Current Rooms:", True, (220,220,220)), (x, y2))
        for idx, room in enumerate(self.current_template['roomLayouts']):
            txt = f"{room['name']} ({room['type']}) [{room['minSize']['width']}x{room['minSize']['length']}]"
            color = (255,255,180) if idx == self.selected_room_idx else (200,200,200)
            surface.blit(pygame.font.SysFont(None, 18).render(txt, True, color), (x+10, y2+30+idx*28))
            # Draw remove button
            btn_rect = pygame.Rect(x+350, y2+30+idx*28, 60, 24)
            pygame.draw.rect(surface, (180,60,60), btn_rect)
            surface.blit(pygame.font.SysFont(None, 16).render("Remove", True, (255,255,255)), btn_rect.move(8,2))
            # Store for event handling
            if not hasattr(self, '_room_remove_btns'):
                self._room_remove_btns = []
            if len(self._room_remove_btns) <= idx:
                self._room_remove_btns.append(btn_rect)
            else:
                self._room_remove_btns[idx] = btn_rect
        # Draw Furniture Rule Editor controls
        panel = self.furniture_panel
        x, y = panel.rect.left + 10, panel.rect.top + 30
        surface.blit(pygame.font.SysFont(None, 20).render("Add Furniture Rule:", True, (220,220,220)), (x, y))
        self.furn_room_type_dropdown.rect.topleft = (x, y+25)
        self.furn_room_type_dropdown.draw()
        self.furn_type_dropdown.rect.topleft = (x+130, y+25)
        self.furn_type_dropdown.draw()
        surface.blit(pygame.font.SysFont(None, 16).render("Min:", True, (200,200,200)), (x+260, y+5))
        self.furn_min_textbox.rect = pygame.Rect(x+260, y+25, 32, 28)
        self.furn_min_textbox.draw(surface)
        surface.blit(pygame.font.SysFont(None, 16).render("Max:", True, (200,200,200)), (x+300, y+5))
        self.furn_max_textbox.rect = pygame.Rect(x+300, y+25, 32, 28)
        self.furn_max_textbox.draw(surface)
        self.add_furn_btn.rect.topleft = (x+340, y+25)
        self.add_furn_btn.draw(surface)
        # Draw current furniture rules for selected room type
        y2 = y+65
        room_type = ROOM_TYPES[self.furn_room_type_dropdown.selected_index or 0]
        rule = next((r for r in self.current_template['furnitureRules'] if r['roomType'] == room_type), None)
        surface.blit(pygame.font.SysFont(None, 18).render(f"Rules for {room_type}:", True, (220,220,220)), (x, y2))
        if rule and rule['requiredFurniture']:
            for idx, furn in enumerate(rule['requiredFurniture']):
                txt = f"{furn['type']} (min: {furn['minCount']}, max: {furn['maxCount']})"
                color = (255,255,180) if idx == self.selected_furn_idx else (200,200,200)
                surface.blit(pygame.font.SysFont(None, 16).render(txt, True, color), (x+10, y2+25+idx*24))
                # Draw remove button
                btn_rect = pygame.Rect(x+180, y2+25+idx*24, 50, 20)
                pygame.draw.rect(surface, (180,60,60), btn_rect)
                surface.blit(pygame.font.SysFont(None, 14).render("Remove", True, (255,255,255)), btn_rect.move(5,2))
                # Store for event handling
                if not hasattr(self, '_furn_remove_btns'):
                    self._furn_remove_btns = {}
                if room_type not in self._furn_remove_btns:
                    self._furn_remove_btns[room_type] = []
                if len(self._furn_remove_btns[room_type]) <= idx:
                    self._furn_remove_btns[room_type].append(btn_rect)
                else:
                    self._furn_remove_btns[room_type][idx] = btn_rect
        else:
            surface.blit(pygame.font.SysFont(None, 16).render("No rules.", True, (180,180,180)), (x+10, y2+25))
        # Draw Decoration Scheme Editor controls
        panel = self.decoration_panel
        x, y = panel.rect.left + 10, panel.rect.top + 30
        surface.blit(pygame.font.SysFont(None, 20).render("Add Decoration Scheme:", True, (220,220,220)), (x, y))
        self.deco_room_type_dropdown.rect.topleft = (x, y+25)
        self.deco_room_type_dropdown.draw()
        self.deco_type_dropdown.rect.topleft = (x+130, y+25)
        self.deco_type_dropdown.draw()
        surface.blit(pygame.font.SysFont(None, 16).render("Theme:", True, (200,200,200)), (x+260, y+5))
        self.deco_theme_textbox.rect = pygame.Rect(x+260, y+25, 80, 28)
        self.deco_theme_textbox.draw(surface)
        surface.blit(pygame.font.SysFont(None, 16).render("Min:", True, (200,200,200)), (x+350, y+5))
        self.deco_min_textbox.rect = pygame.Rect(x+350, y+25, 32, 28)
        self.deco_min_textbox.draw(surface)
        surface.blit(pygame.font.SysFont(None, 16).render("Max:", True, (200,200,200)), (x+390, y+5))
        self.deco_max_textbox.rect = pygame.Rect(x+390, y+25, 32, 28)
        self.deco_max_textbox.draw(surface)
        surface.blit(pygame.font.SysFont(None, 16).render("Density:", True, (200,200,200)), (x+430, y+5))
        self.deco_density_textbox.rect = pygame.Rect(x+430, y+25, 40, 28)
        self.deco_density_textbox.draw(surface)
        self.add_deco_btn.rect.topleft = (x+480, y+25)
        self.add_deco_btn.draw(surface)
        # Draw current decoration schemes for selected room type
        y2 = y+65
        room_type = ROOM_TYPES[self.deco_room_type_dropdown.selected_index or 0]
        scheme = next((s for s in self.current_template['decorationSchemes'] if s['roomType'] == room_type), None)
        surface.blit(pygame.font.SysFont(None, 18).render(f"Schemes for {room_type}:", True, (220,220,220)), (x, y2))
        if scheme and scheme['decorations']:
            for idx, deco in enumerate(scheme['decorations']):
                txt = f"{deco['type']} (min: {deco['minCount']}, max: {deco['maxCount']})"
                color = (255,255,180) if idx == self.selected_deco_idx else (200,200,200)
                surface.blit(pygame.font.SysFont(None, 16).render(txt, True, color), (x+10, y2+25+idx*24))
                # Draw remove button
                btn_rect = pygame.Rect(x+180, y2+25+idx*24, 50, 20)
                pygame.draw.rect(surface, (180,60,60), btn_rect)
                surface.blit(pygame.font.SysFont(None, 14).render("Remove", True, (255,255,255)), btn_rect.move(5,2))
                # Store for event handling
                if not hasattr(self, '_deco_remove_btns'):
                    self._deco_remove_btns = {}
                if room_type not in self._deco_remove_btns:
                    self._deco_remove_btns[room_type] = []
                if len(self._deco_remove_btns[room_type]) <= idx:
                    self._deco_remove_btns[room_type].append(btn_rect)
                else:
                    self._deco_remove_btns[room_type][idx] = btn_rect
        else:
            surface.blit(pygame.font.SysFont(None, 16).render("No schemes.", True, (180,180,180)), (x+10, y2+25))
        # Draw NPC Zones Editor controls
        panel = self.npc_panel
        x, y = panel.rect.left + 10, panel.rect.top + 30
        surface.blit(pygame.font.SysFont(None, 20).render("Add NPC Zone:", True, (220,220,220)), (x, y))
        self.npc_room_type_dropdown.rect.topleft = (x, y+25)
        self.npc_room_type_dropdown.draw()
        self.npc_zone_type_dropdown.rect.topleft = (x+130, y+25)
        self.npc_zone_type_dropdown.draw()
        surface.blit(pygame.font.SysFont(None, 16).render("Cap:", True, (200,200,200)), (x+260, y+5))
        self.npc_capacity_textbox.rect = pygame.Rect(x+260, y+25, 32, 28)
        self.npc_capacity_textbox.draw(surface)
        self.npc_activity_dropdown.rect.topleft = (x+300, y+25)
        self.npc_activity_dropdown.draw()
        self.add_npc_zone_btn.rect.topleft = (x+430, y+25)
        self.add_npc_zone_btn.draw(surface)
        # Draw current NPC zones
        y2 = y+65
        surface.blit(pygame.font.SysFont(None, 18).render("NPC Zones:", True, (220,220,220)), (x, y2))
        for idx, zone in enumerate(self.current_template['npcZones']):
            txt = f"{zone['roomType']} {zone['zoneType']} (cap: {zone['capacity']}, act: {','.join(zone['activityType'])})"
            color = (255,255,180) if idx == self.selected_npc_idx else (200,200,200)
            surface.blit(pygame.font.SysFont(None, 16).render(txt, True, color), (x+10, y2+25+idx*24))
            btn_rect = pygame.Rect(x+320, y2+25+idx*24, 50, 20)
            pygame.draw.rect(surface, (180,60,60), btn_rect)
            surface.blit(pygame.font.SysFont(None, 14).render("Remove", True, (255,255,255)), btn_rect.move(5,2))
            if not hasattr(self, '_npc_remove_btns'):
                self._npc_remove_btns = []
            if len(self._npc_remove_btns) <= idx:
                self._npc_remove_btns.append(btn_rect)
            else:
                self._npc_remove_btns[idx] = btn_rect
        # Draw Interactive Objects Editor controls
        panel = self.interactive_panel
        x, y = panel.rect.left + 10, panel.rect.top + 30
        surface.blit(pygame.font.SysFont(None, 20).render("Add Interactive Object:", True, (220,220,220)), (x, y))
        self.io_room_type_dropdown.rect.topleft = (x, y+25)
        self.io_room_type_dropdown.draw()
        self.io_object_type_dropdown.rect.topleft = (x+130, y+25)
        self.io_object_type_dropdown.draw()
        surface.blit(pygame.font.SysFont(None, 16).render("Count:", True, (200,200,200)), (x+260, y+5))
        self.io_count_textbox.rect = pygame.Rect(x+260, y+25, 32, 28)
        self.io_count_textbox.draw(surface)
        surface.blit(pygame.font.SysFont(None, 16).render("Space:", True, (200,200,200)), (x+300, y+5))
        self.io_required_space_textbox.rect = pygame.Rect(x+300, y+25, 40, 28)
        self.io_required_space_textbox.draw(surface)
        self.add_io_btn.rect.topleft = (x+350, y+25)
        self.add_io_btn.draw(surface)
        # Draw current interactive objects
        y2 = y+65
        surface.blit(pygame.font.SysFont(None, 18).render("Interactive Objects:", True, (220,220,220)), (x, y2))
        for idx, obj in enumerate(self.current_template['interactiveObjects']):
            txt = f"{obj['roomType']} {obj['objectType']} (count: {obj['count']}, space: {obj['requiredSpace']})"
            color = (255,255,180) if idx == self.selected_io_idx else (200,200,200)
            surface.blit(pygame.font.SysFont(None, 16).render(txt, True, color), (x+10, y2+25+idx*24))
            btn_rect = pygame.Rect(x+320, y2+25+idx*24, 50, 20)
            pygame.draw.rect(surface, (180,60,60), btn_rect)
            surface.blit(pygame.font.SysFont(None, 14).render("Remove", True, (255,255,255)), btn_rect.move(5,2))
            if not hasattr(self, '_io_remove_btns'):
                self._io_remove_btns = []
            if len(self._io_remove_btns) <= idx:
                self._io_remove_btns.append(btn_rect)
            else:
                self._io_remove_btns[idx] = btn_rect
        self.preview_panel.draw()
        self.validation_panel.draw()
        for i, btn in enumerate(self.action_buttons):
            btn.rect.topleft = (1000 + 20 + i * 65, 840)
            btn.draw(surface)
        if self.validation_error:
            font = pygame.font.SysFont(None, 20)
            err_surf = font.render(self.validation_error, True, (255, 80, 80))
            surface.blit(err_surf, (1010, 730))

    def handle_event(self, event: pygame.event.Event) -> bool:
        handled = self.layout.handle_event(event)
        handled = self.scroll_panel.handle_event(event) or handled
        handled = self.preview_panel.handle_event(event) or handled
        handled = self.validation_panel.handle_event(event) or handled
        for btn in self.action_buttons:
            handled = btn.handle_event(event) or handled
        # Room Layout Editor controls
        if self.room_type_dropdown.handle_event(event):
            handled = True
        if hasattr(self, 'room_name_textbox') and hasattr(self.room_name_textbox, 'handle_event'):
            if self.room_name_textbox.handle_event(event):
                handled = True
        if hasattr(self, 'room_width_textbox') and hasattr(self.room_width_textbox, 'handle_event'):
            if self.room_width_textbox.handle_event(event):
                handled = True
        if hasattr(self, 'room_length_textbox') and hasattr(self.room_length_textbox, 'handle_event'):
            if self.room_length_textbox.handle_event(event):
                handled = True
        if self.add_room_btn.handle_event(event):
            handled = True
        # Remove room buttons
        if hasattr(self, '_room_remove_btns'):
            if event.type == pygame.MOUSEBUTTONDOWN:
                for idx, btn_rect in enumerate(self._room_remove_btns):
                    if btn_rect.collidepoint(event.pos):
                        self._remove_room(idx)
                        handled = True
        # Furniture Rule Editor controls
        if self.furn_room_type_dropdown.handle_event(event):
            handled = True
        if self.furn_type_dropdown.handle_event(event):
            handled = True
        if hasattr(self, 'furn_min_textbox') and hasattr(self.furn_min_textbox, 'handle_event'):
            if self.furn_min_textbox.handle_event(event):
                handled = True
        if hasattr(self, 'furn_max_textbox') and hasattr(self.furn_max_textbox, 'handle_event'):
            if self.furn_max_textbox.handle_event(event):
                handled = True
        if self.add_furn_btn.handle_event(event):
            handled = True
        # Remove furniture rule buttons
        if hasattr(self, '_furn_remove_btns'):
            room_type = ROOM_TYPES[self.furn_room_type_dropdown.selected_index or 0]
            if room_type in self._furn_remove_btns and event.type == pygame.MOUSEBUTTONDOWN:
                for idx, btn_rect in enumerate(self._furn_remove_btns[room_type]):
                    if btn_rect.collidepoint(event.pos):
                        self._remove_furn_rule(room_type, idx)
                        handled = True
        # Decoration Scheme Editor controls
        if self.deco_room_type_dropdown.handle_event(event):
            handled = True
        if self.deco_type_dropdown.handle_event(event):
            handled = True
        if hasattr(self, 'deco_theme_textbox') and hasattr(self.deco_theme_textbox, 'handle_event'):
            if self.deco_theme_textbox.handle_event(event):
                handled = True
        if hasattr(self, 'deco_min_textbox') and hasattr(self.deco_min_textbox, 'handle_event'):
            if self.deco_min_textbox.handle_event(event):
                handled = True
        if hasattr(self, 'deco_max_textbox') and hasattr(self.deco_max_textbox, 'handle_event'):
            if self.deco_max_textbox.handle_event(event):
                handled = True
        if hasattr(self, 'deco_density_textbox') and hasattr(self.deco_density_textbox, 'handle_event'):
            if self.deco_density_textbox.handle_event(event):
                handled = True
        if self.add_deco_btn.handle_event(event):
            handled = True
        # Remove decoration scheme buttons
        if hasattr(self, '_deco_remove_btns'):
            room_type = ROOM_TYPES[self.deco_room_type_dropdown.selected_index or 0]
            if room_type in self._deco_remove_btns and event.type == pygame.MOUSEBUTTONDOWN:
                for idx, btn_rect in enumerate(self._deco_remove_btns[room_type]):
                    if btn_rect.collidepoint(event.pos):
                        self._remove_deco_scheme(room_type, idx)
                        handled = True
        # NPC Zones Editor controls
        if self.npc_room_type_dropdown.handle_event(event):
            handled = True
        if self.npc_zone_type_dropdown.handle_event(event):
            handled = True
        if hasattr(self, 'npc_capacity_textbox') and hasattr(self.npc_capacity_textbox, 'handle_event'):
            if self.npc_capacity_textbox.handle_event(event):
                handled = True
        if self.npc_activity_dropdown.handle_event(event):
            handled = True
        if self.add_npc_zone_btn.handle_event(event):
            handled = True
        if hasattr(self, '_npc_remove_btns'):
            if event.type == pygame.MOUSEBUTTONDOWN:
                for idx, btn_rect in enumerate(self._npc_remove_btns):
                    if btn_rect.collidepoint(event.pos):
                        self._remove_npc_zone(idx)
                        handled = True
        # Interactive Objects Editor controls
        if self.io_room_type_dropdown.handle_event(event):
            handled = True
        if self.io_object_type_dropdown.handle_event(event):
            handled = True
        if hasattr(self, 'io_count_textbox') and hasattr(self.io_count_textbox, 'handle_event'):
            if self.io_count_textbox.handle_event(event):
                handled = True
        if hasattr(self, 'io_required_space_textbox') and hasattr(self.io_required_space_textbox, 'handle_event'):
            if self.io_required_space_textbox.handle_event(event):
                handled = True
        if self.add_io_btn.handle_event(event):
            handled = True
        if hasattr(self, '_io_remove_btns'):
            if event.type == pygame.MOUSEBUTTONDOWN:
                for idx, btn_rect in enumerate(self._io_remove_btns):
                    if btn_rect.collidepoint(event.pos):
                        self._remove_interactive_object(idx)
                        handled = True
        return handled

    # --- Export/Import/Validation/Preview/Versioning Stubs ---
    # (To be implemented in next steps)

    # --- Room/Furniture/Decoration/NPC/Interactive Editing Logic ---
    # (To be implemented in next steps) 