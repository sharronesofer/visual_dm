============================= test session starts ==============================
platform darwin -- Python 3.11.5, pytest-8.3.5, pluggy-1.6.0
rootdir: /Users/Sharrone/Visual_DM
plugins: anyio-4.9.0, mock-3.14.0, cov-6.1.1
collected 142 items / 73 errors / 35 skipped

WARNING: Failed to generate report: No data to report.


==================================== ERRORS ====================================
_____________ ERROR collecting archives/models/test_uuid_mixin.py ______________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/models/test_uuid_mixin.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
archives/models/base.py:3: in <module>
    from backend.app.core.base import Base, BaseModel
backend/app/core/__init__.py:7: in <module>
    from . import scene
E   ImportError: cannot import name 'scene' from partially initialized module 'backend.app.core' (most likely due to a circular import) (/Users/Sharrone/Visual_DM/backend/app/core/__init__.py)

During handling of the above exception, another exception occurred:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/models/__init__.py:4: in <module>
    from .base import BaseModel
archives/models/base.py:5: in <module>
    raise ImportError('Base and BaseModel have moved to backend.app.core.base. Please update your imports.')
E   ImportError: Base and BaseModel have moved to backend.app.core.base. Please update your imports.
___________ ERROR collecting archives/services/test_redis_service.py ___________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/services/test_redis_service.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/services/test_redis_service.py:5: in <module>
    from backend.app.services.redis_service import RedisService
backend/app/services/redis_service.py:1: in <module>
    import aioredis
E   ModuleNotFoundError: No module named 'aioredis'
____________ ERROR collecting archives/tests/test_combat_logger.py _____________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_combat_logger.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_combat_logger.py:4: in <module>
    from app.combat.combat_logger import (
E   ModuleNotFoundError: No module named 'app'
______ ERROR collecting archives/tests/test_combat_logger_and_scaling.py _______
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_combat_logger_and_scaling.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_combat_logger_and_scaling.py:2: in <module>
    from app.combat.combat_logger import CombatLogger
E   ModuleNotFoundError: No module named 'app'
__________ ERROR collecting archives/tests/test_combat_resolution.py ___________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_combat_resolution.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_combat_resolution.py:4: in <module>
    from app.combat.resolution import (
E   ModuleNotFoundError: No module named 'app'
_________ ERROR collecting archives/tests/test_combat_state_manager.py _________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_combat_state_manager.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_combat_state_manager.py:4: in <module>
    from app.combat.state_manager import CombatStateManager, CombatState
E   ModuleNotFoundError: No module named 'app'
____________ ERROR collecting archives/tests/test_combat_system.py _____________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_combat_system.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_combat_system.py:3: in <module>
    from app.core.combat import CombatSystem
E   ModuleNotFoundError: No module named 'app'
____________ ERROR collecting archives/tests/test_db_connection.py _____________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_db_connection.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_db_connection.py:2: in <module>
    from app import create_app
E   ModuleNotFoundError: No module named 'app'
__________ ERROR collecting archives/tests/test_encounter_scaling.py ___________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_encounter_scaling.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_encounter_scaling.py:2: in <module>
    from app.combat.encounter_scaling import EncounterScaler, PartyRole, EncounterDifficulty
E   ModuleNotFoundError: No module named 'app'
_______________ ERROR collecting archives/tests/test_faction.py ________________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_faction.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_faction.py:7: in <module>
    from app.core.models.world import Faction, FactionRelation, RelationshipType
E   ModuleNotFoundError: No module named 'app'
_____________ ERROR collecting archives/tests/test_git_service.py ______________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_git_service.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_git_service.py:8: in <module>
    from app.core.services.git_service import GitService
E   ModuleNotFoundError: No module named 'app'
__________ ERROR collecting archives/tests/test_hex_asset_manager.py ___________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_hex_asset_manager.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_hex_asset_manager.py:12: in <module>
    from visual_client.core.managers.hex_asset_manager import HexAssetManager
E   ModuleNotFoundError: No module named 'visual_client.core'
------------------------------- Captured stdout --------------------------------
pygame 2.6.1 (SDL 2.28.4, Python 3.11.5)
Hello from the pygame community. https://www.pygame.org/contribute.html
_________ ERROR collecting archives/tests/test_hex_asset_preview_ui.py _________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_hex_asset_preview_ui.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_hex_asset_preview_ui.py:7: in <module>
    import pygame_gui
E   ModuleNotFoundError: No module named 'pygame_gui'
__________ ERROR collecting archives/tests/test_hex_asset_renderer.py __________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_hex_asset_renderer.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_hex_asset_renderer.py:10: in <module>
    from visual_client.core.managers.hex_asset_renderer import HexAssetRenderer
E   ModuleNotFoundError: No module named 'visual_client.core'
___________ ERROR collecting archives/tests/test_hex_sprite_sheet.py ___________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_hex_sprite_sheet.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_hex_sprite_sheet.py:10: in <module>
    from visual_client.core.managers.hex_sprite_sheet import HexSpriteSheet
E   ModuleNotFoundError: No module named 'visual_client.core'
___________ ERROR collecting archives/tests/test_location_version.py ___________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_location_version.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_location_version.py:7: in <module>
    from app.core.models.location import Location
E   ModuleNotFoundError: No module named 'app'
____________ ERROR collecting archives/tests/test_loot_generator.py ____________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_loot_generator.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_loot_generator.py:6: in <module>
    from app.combat.loot_generator import (
E   ModuleNotFoundError: No module named 'app'
_____________ ERROR collecting archives/tests/test_loot_schema.py ______________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_loot_schema.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_loot_schema.py:9: in <module>
    from loot_models.base import LootBase
E   ModuleNotFoundError: No module named 'loot_models'
______________ ERROR collecting archives/tests/test_migrations.py ______________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_migrations.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_migrations.py:4: in <module>
    from alembic.config import Config
E   ModuleNotFoundError: No module named 'alembic.config'
_____________ ERROR collecting archives/tests/test_npc_version.py ______________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_npc_version.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_npc_version.py:7: in <module>
    from app.core.models.npc import NPC, NPCType, NPCDisposition
E   ModuleNotFoundError: No module named 'app'
___________ ERROR collecting archives/tests/test_redis_connection.py ___________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_redis_connection.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_redis_connection.py:2: in <module>
    from app import create_app, redis_client
E   ModuleNotFoundError: No module named 'app'
____________ ERROR collecting archives/tests/test_season_system.py _____________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_season_system.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_season_system.py:3: in <module>
    from app.core.models.time_system import TimeSystem
E   ModuleNotFoundError: No module named 'app'
_______________ ERROR collecting archives/tests/test_services.py _______________
archives/tests/test_services.py:12: in <module>
    spec.loader.exec_module(services)
<frozen importlib._bootstrap_external>:936: in exec_module
    ???
<frozen importlib._bootstrap_external>:1073: in get_code
    ???
<frozen importlib._bootstrap_external>:1130: in get_data
    ???
E   FileNotFoundError: [Errno 2] No such file or directory: '/Users/Sharrone/Visual_DM/archives/tests/../app/services/__init__.py'
____________ ERROR collecting archives/tests/test_status_effects.py ____________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_status_effects.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_status_effects.py:3: in <module>
    from app.combat.status_effects_manager import StatusEffectManager
E   ModuleNotFoundError: No module named 'app'
_____________ ERROR collecting archives/tests/test_time_system.py ______________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_time_system.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_time_system.py:3: in <module>
    from app.core.models.time_system import TimeSystem, TimeEvent, TimeScale
E   ModuleNotFoundError: No module named 'app'
___________ ERROR collecting archives/tests/test_version_control.py ____________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_version_control.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_version_control.py:7: in <module>
    from app.core.models.version_control import CodeVersion, TaskVersionLink, ReviewVersionLink
E   ModuleNotFoundError: No module named 'app'
________ ERROR collecting archives/tests/test_version_control_models.py ________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_version_control_models.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_version_control_models.py:7: in <module>
    from app.core.models.version_control import CodeVersion, TaskVersionLink, ReviewVersionLink
E   ModuleNotFoundError: No module named 'app'
_______ ERROR collecting archives/tests/test_version_control_service.py ________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_version_control_service.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_version_control_service.py:7: in <module>
    from app.core.services.version_control_service import VersionControlService
E   ModuleNotFoundError: No module named 'app'
_________ ERROR collecting archives/tests/test_weather_consistency.py __________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_weather_consistency.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_weather_consistency.py:3: in <module>
    from app.core.models.weather_system import WeatherSystem
E   ModuleNotFoundError: No module named 'app'
_______ ERROR collecting archives/tests/test_weather_gameplay_impacts.py _______
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_weather_gameplay_impacts.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_weather_gameplay_impacts.py:3: in <module>
    from app.core.models.weather_system import WeatherSystem
E   ModuleNotFoundError: No module named 'app'
______ ERROR collecting archives/tests/test_weather_intensity_scaling.py _______
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_weather_intensity_scaling.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_weather_intensity_scaling.py:2: in <module>
    from app.core.models.weather_system import WeatherSystem
E   ModuleNotFoundError: No module named 'app'
_______ ERROR collecting archives/tests/test_weather_sync_performance.py _______
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_weather_sync_performance.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_weather_sync_performance.py:4: in <module>
    from app.core.models.weather_system import WeatherSystem
E   ModuleNotFoundError: No module named 'app'
____________ ERROR collecting archives/tests/test_weather_system.py ____________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_weather_system.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_weather_system.py:4: in <module>
    from app.core.models.time_system import TimeSystem
E   ModuleNotFoundError: No module named 'app'
__________ ERROR collecting archives/tests/test_world_integration.py ___________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_world_integration.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_world_integration.py:17: in <module>
    from app.core.models.world import World
E   ModuleNotFoundError: No module named 'app'
__________ ERROR collecting archives/tests/test_world_persistence.py ___________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_world_persistence.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_world_persistence.py:18: in <module>
    from app.core.persistence.serialization import serialize, deserialize, SerializedData, SerializationFormat, CompressionType, extract_scene_dependency_graph, resolve_component_references
E   ModuleNotFoundError: No module named 'app'
___________ ERROR collecting archives/tests/test_world_validation.py ___________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/test_world_validation.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/test_world_validation.py:14: in <module>
    from app.core.models.world import World, WorldState
E   ModuleNotFoundError: No module named 'app'
____ ERROR collecting archives/tests/ui/components/test_base_components.py _____
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/ui/components/test_base_components.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/ui/components/test_base_components.py:8: in <module>
    from visual_client.ui.components.base_screen import BaseScreen, ScreenConfig
E   ModuleNotFoundError: No module named 'visual_client.ui.components'
______ ERROR collecting archives/tests/ui/components/test_integration.py _______
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/ui/components/test_integration.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/ui/components/test_integration.py:8: in <module>
    from visual_client.ui.components.base_screen import BaseScreen, ScreenConfig
E   ModuleNotFoundError: No module named 'visual_client.ui.components'
_ ERROR collecting archives/tests/ui/components/test_interactive_components.py _
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/ui/components/test_interactive_components.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/ui/components/test_interactive_components.py:8: in <module>
    from visual_client.ui.components.text_input import TextInput, TextInputConfig
E   ModuleNotFoundError: No module named 'visual_client.ui.components'
________ ERROR collecting archives/tests/ui/components/test_security.py ________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/ui/components/test_security.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/ui/components/test_security.py:8: in <module>
    from visual_client.ui.components.text_input import TextInput, TextInputConfig
E   ModuleNotFoundError: No module named 'visual_client.ui.components'
___ ERROR collecting archives/tests/unit/test_character_builder_equipment.py ___
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/unit/test_character_builder_equipment.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/unit/test_character_builder_equipment.py:4: in <module>
    from backend.systems.character.core.character_builder import CharacterBuilder
E   ModuleNotFoundError: No module named 'backend.systems.character.core.character_builder'
__ ERROR collecting archives/tests/validation/test_world_event_validation.py ___
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/validation/test_world_event_validation.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/validation/test_world_event_validation.py:5: in <module>
    from jsonschema import ValidationError
E   ModuleNotFoundError: No module named 'jsonschema'
_ ERROR collecting archives/tests/visual_client/ui/screens/game/test_npc_viewer_panel.py _
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/visual_client/ui/screens/game/test_npc_viewer_panel.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/visual_client/ui/screens/game/test_npc_viewer_panel.py:6: in <module>
    from visual_client.ui.screens.game.npc_viewer_panel import NPCViewerPanel
E   ModuleNotFoundError: No module named 'visual_client.ui.screens.game.npc_viewer_panel'
_ ERROR collecting archives/tests/visual_client/ui/screens/test_template_editor.py _
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/visual_client/ui/screens/test_template_editor.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/visual_client/ui/screens/test_template_editor.py:21: in <module>
    from visual_client.ui.screens.template_editor import TemplateEditorScreen
E   ModuleNotFoundError: No module named 'visual_client.ui.screens.template_editor'
________ ERROR collecting archives/tests/world/test_world_tick_utils.py ________
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/world/test_world_tick_utils.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/world/test_world_tick_utils.py:6: in <module>
    from app.world.tick_utils import (
E   ModuleNotFoundError: No module named 'app'
______ ERROR collecting archives/tests/worldgen/test_deterministic_rng.py ______
ImportError while importing test module '/Users/Sharrone/Visual_DM/archives/tests/worldgen/test_deterministic_rng.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
archives/tests/worldgen/test_deterministic_rng.py:13: in <module>
    from scipy import stats
E   ModuleNotFoundError: No module named 'scipy'
______ ERROR collecting backend/app/characters/test_character_builder.py _______
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/app/characters/test_character_builder.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
backend/app/models/base.py:3: in <module>
    from backend.app.core.base import Base, BaseModel
backend/app/core/__init__.py:7: in <module>
    from . import scene
E   ImportError: cannot import name 'scene' from partially initialized module 'backend.app.core' (most likely due to a circular import) (/Users/Sharrone/Visual_DM/backend/app/core/__init__.py)

During handling of the above exception, another exception occurred:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/app/characters/test_character_builder.py:2: in <module>
    from backend.systems.character.core.character_builder import CharacterBuilder
backend/app/characters/character_builder_class.py:2: in <module>
    from backend.systems.character.core.character_model import Character
backend/app/characters/character.py:4: in <module>
    from backend.app.models.base import Base
backend/app/models/__init__.py:4: in <module>
    from .base import BaseModel
backend/app/models/base.py:5: in <module>
    raise ImportError('Base and BaseModel have moved to backend.app.core.base. Please update your imports.')
E   ImportError: Base and BaseModel have moved to backend.app.core.base. Please update your imports.
____________ ERROR collecting backend/app/models/test_uuid_mixin.py ____________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/app/models/test_uuid_mixin.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
backend/app/models/base.py:3: in <module>
    from backend.app.core.base import Base, BaseModel
backend/app/core/__init__.py:7: in <module>
    from . import scene
E   ImportError: cannot import name 'scene' from partially initialized module 'backend.app.core' (most likely due to a circular import) (/Users/Sharrone/Visual_DM/backend/app/core/__init__.py)

During handling of the above exception, another exception occurred:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/app/models/__init__.py:4: in <module>
    from .base import BaseModel
backend/app/models/base.py:5: in <module>
    raise ImportError('Base and BaseModel have moved to backend.app.core.base. Please update your imports.')
E   ImportError: Base and BaseModel have moved to backend.app.core.base. Please update your imports.
_________ ERROR collecting backend/app/services/test_redis_service.py __________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/app/services/test_redis_service.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/app/services/test_redis_service.py:5: in <module>
    from backend.app.services.redis_service import RedisService
backend/app/services/redis_service.py:1: in <module>
    import aioredis
E   ModuleNotFoundError: No module named 'aioredis'
______________________ ERROR collecting backend/app/tests ______________________
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
<frozen importlib._bootstrap>:1204: in _gcd_import
    ???
<frozen importlib._bootstrap>:1176: in _find_and_load
    ???
<frozen importlib._bootstrap>:1147: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:690: in _load_unlocked
    ???
../.pyenv/versions/3.11.5/lib/python3.11/site-packages/_pytest/assertion/rewrite.py:185: in exec_module
    exec(co, module.__dict__)
backend/app/tests/conftest.py:8: in <module>
    from backend.app.main import app
backend/app/main.py:5: in <module>
    from app.api.v1 import api_router
E   ModuleNotFoundError: No module named 'app'
_______ ERROR collecting backend/combat/tests/test_damage_composition.py _______
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/combat/tests/test_damage_composition.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/combat/tests/test_damage_composition.py:3: in <module>
    from app.core.enums import DamageType
E   ModuleNotFoundError: No module named 'app'
___________________ ERROR collecting backend/config_test.py ____________________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/config_test.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/config_test.py:9: in <module>
    from app.config import Config
E   ModuleNotFoundError: No module named 'app'
_________ ERROR collecting backend/core2/models/test_combat_system.py __________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/core2/models/test_combat_system.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/core2/models/__init__.py:10: in <module>
    from app.core.models.base import BaseModel
E   ModuleNotFoundError: No module named 'app'
______ ERROR collecting backend/core2/persistence/test_version_control.py ______
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/core2/persistence/test_version_control.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/core2/persistence/__init__.py:8: in <module>
    from app.core.persistence.serialization import serialize, deserialize
E   ModuleNotFoundError: No module named 'app'
__ ERROR collecting backend/python_converted/src/worldgen/core/simple_test.py __
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/python_converted/src/worldgen/core/simple_test.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/python_converted/src/worldgen/__init__.py:32: in <module>
    from .region import *
backend/python_converted/src/worldgen/region/__init__.py:11: in <module>
    from python_converted.src.worldgen.region.BaseRegionGenerator import BaseRegionGenerator
E   ModuleNotFoundError: No module named 'python_converted'
_ ERROR collecting backend/python_converted/src/worldgen/environment/__tests__/test_biome_transitions.py _
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/python_converted/src/worldgen/environment/__tests__/test_biome_transitions.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/python_converted/src/worldgen/environment/__tests__/test_biome_transitions.py:12: in <module>
    from ..BiomeTypes import BiomeType, BIOME_PARAMETERS, TRANSITION_BIOMES
E   ImportError: attempted relative import with no known parent package
________ ERROR collecting backend/tests/api/test_websocket_endpoint.py _________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/api/test_websocket_endpoint.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/api/test_websocket_endpoint.py:5: in <module>
    from backend.app.main import app
backend/app/main.py:5: in <module>
    from app.api.v1 import api_router
backend/app/api/v1/__init__.py:6: in <module>
    from .events import router as events_router
backend/app/api/v1/events.py:7: in <module>
    from app.core.events.event_dispatcher import EventDispatcher, EventBase
backend/app/core/__init__.py:7: in <module>
    from . import scene
E   ImportError: cannot import name 'scene' from partially initialized module 'app.core' (most likely due to a circular import) (/Users/Sharrone/Visual_DM/backend/app/core/__init__.py)
________________ ERROR collecting backend/tests/test_combat.py _________________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/test_combat.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/test_combat.py:1: in <module>
    from app.core.models.combat import Combatant, Weapon, CombatSystem
backend/app/core/__init__.py:7: in <module>
    from . import scene
E   ImportError: cannot import name 'scene' from partially initialized module 'app.core' (most likely due to a circular import) (/Users/Sharrone/Visual_DM/backend/app/core/__init__.py)
_________ ERROR collecting backend/tests/test_coordinate_validation.py _________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/test_coordinate_validation.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/test_coordinate_validation.py:8: in <module>
    from visual_client.core.utils.coordinates import GlobalCoord, LocalCoord
E   ModuleNotFoundError: No module named 'visual_client.core'
_____________ ERROR collecting backend/tests/test_feature_flags.py _____________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/test_feature_flags.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/test_feature_flags.py:7: in <module>
    from backend.utils.feature_flags import (
E   ModuleNotFoundError: No module named 'backend.utils.feature_flags'
_____________ ERROR collecting backend/tests/test_id_generator.py ______________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/test_id_generator.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/test_id_generator.py:6: in <module>
    from backend.utils.id import IDGenerator, generate_unique_id, generate_uuid
E   ModuleNotFoundError: No module named 'backend.utils.id'
_______________ ERROR collecting backend/tests/test_inventory.py _______________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/test_inventory.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/test_inventory.py:2: in <module>
    from app.core.models.inventory import Inventory, Item
backend/app/core/__init__.py:7: in <module>
    from . import scene
E   ImportError: cannot import name 'scene' from partially initialized module 'app.core' (most likely due to a circular import) (/Users/Sharrone/Visual_DM/backend/app/core/__init__.py)
____________ ERROR collecting backend/tests/test_item_attributes.py ____________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/test_item_attributes.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/test_item_attributes.py:2: in <module>
    from app.core.models.item import AttributeContainer, Item
backend/app/core/__init__.py:7: in <module>
    from . import scene
E   ImportError: cannot import name 'scene' from partially initialized module 'app.core' (most likely due to a circular import) (/Users/Sharrone/Visual_DM/backend/app/core/__init__.py)
________________ ERROR collecting backend/tests/test_region.py _________________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/test_region.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/test_region.py:2: in <module>
    from backend.world.world_models import Region
backend/world/__init__.py:5: in <module>
    from visual_client.game.world import WorldState
E   ModuleNotFoundError: No module named 'visual_client.game'
_________________ ERROR collecting backend/tests/test_retry.py _________________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/test_retry.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/test_retry.py:5: in <module>
    from backend.utils.retry import retry, retry_sync, retry_async, RetryOptions
E   ModuleNotFoundError: No module named 'backend.utils.retry'
______________ ERROR collecting backend/tests/test_world_event.py ______________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/test_world_event.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/test_world_event.py:1: in <module>
    from app.core.models.world_event import WorldEvent
backend/app/core/__init__.py:7: in <module>
    from . import scene
E   ImportError: cannot import name 'scene' from partially initialized module 'app.core' (most likely due to a circular import) (/Users/Sharrone/Visual_DM/backend/app/core/__init__.py)
_ ERROR collecting backend/tests/unit/app/core/persistence/test_change_tracker.py _
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/unit/app/core/persistence/test_change_tracker.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/unit/app/core/persistence/test_change_tracker.py:10: in <module>
    from backend.app.core.persistence.change_tracker import (
backend/app/core/__init__.py:7: in <module>
    from . import scene
E   ImportError: cannot import name 'scene' from partially initialized module 'backend.app.core' (most likely due to a circular import) (/Users/Sharrone/Visual_DM/backend/app/core/__init__.py)
_ ERROR collecting backend/tests/unit/app/core/schemas/test_example_templates.py _
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/unit/app/core/schemas/test_example_templates.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/unit/app/core/schemas/test_example_templates.py:9: in <module>
    from backend.app.core.schemas.example_templates import ExampleTemplates
backend/app/core/__init__.py:7: in <module>
    from . import scene
E   ImportError: cannot import name 'scene' from partially initialized module 'backend.app.core' (most likely due to a circular import) (/Users/Sharrone/Visual_DM/backend/app/core/__init__.py)
_ ERROR collecting backend/tests/unit/app/core/schemas/test_review_template_factory.py _
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/unit/app/core/schemas/test_review_template_factory.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/unit/app/core/schemas/test_review_template_factory.py:8: in <module>
    from backend.app.core.schemas.review_template_factory import (
backend/app/core/__init__.py:7: in <module>
    from . import scene
E   ImportError: cannot import name 'scene' from partially initialized module 'backend.app.core' (most likely due to a circular import) (/Users/Sharrone/Visual_DM/backend/app/core/__init__.py)
_ ERROR collecting backend/tests/unit/app/core/schemas/test_websocket_schema.py _
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/unit/app/core/schemas/test_websocket_schema.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/unit/app/core/schemas/test_websocket_schema.py:3: in <module>
    from backend.app.schemas.websocket import WebSocketMessage
backend/app/schemas/__init__.py:1: in <module>
    from .base import (
E   ModuleNotFoundError: No module named 'backend.app.schemas.base'
_ ERROR collecting backend/tests/unit/core2/file_processing/test_concurrent_processor.py _
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/unit/core2/file_processing/test_concurrent_processor.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
backend/core2/file_processing/concurrent_processor.py:21: in <module>
    from app.core.file_processing.metrics import MetricsCollector
backend/app/core/__init__.py:7: in <module>
    from . import scene
E   ImportError: cannot import name 'scene' from partially initialized module 'app.core' (most likely due to a circular import) (/Users/Sharrone/Visual_DM/backend/app/core/__init__.py)

During handling of the above exception, another exception occurred:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/unit/core2/file_processing/test_concurrent_processor.py:12: in <module>
    from backend.core2.file_processing.concurrent_processor import (
backend/core2/file_processing/concurrent_processor.py:24: in <module>
    from backend.app.core.file_processing.metrics import MetricsCollector
backend/app/core/__init__.py:7: in <module>
    from . import scene
E   ImportError: cannot import name 'scene' from partially initialized module 'backend.app.core' (most likely due to a circular import) (/Users/Sharrone/Visual_DM/backend/app/core/__init__.py)
_________ ERROR collecting backend/tests/unit/test_bible_qa_service.py _________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/unit/test_bible_qa_service.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/unit/test_bible_qa_service.py:6: in <module>
    from backend.services.bible_qa_service import (
E   ModuleNotFoundError: No module named 'backend.services.bible_qa_service'
___________ ERROR collecting backend/tests/unit/test_motif_model.py ____________
ImportError while importing test module '/Users/Sharrone/Visual_DM/backend/tests/unit/test_motif_model.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
../.pyenv/versions/3.11.5/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
backend/tests/unit/test_motif_model.py:3: in <module>
    from backend.models.motif import Motif, MotifSchema, MotifCategory, MotifScope, MotifLifecycle
E   ModuleNotFoundError: No module named 'backend.models.motif'
=============================== warnings summary ===============================
../.pyenv/versions/3.11.5/lib/python3.11/site-packages/pydantic/_internal/_config.py:323
  /Users/Sharrone/.pyenv/versions/3.11.5/lib/python3.11/site-packages/pydantic/_internal/_config.py:323: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

backend/tests/test_async_function_patterns.py:112
  /Users/Sharrone/Visual_DM/backend/tests/test_async_function_patterns.py:112: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

backend/tests/test_async_function_patterns.py:118
  /Users/Sharrone/Visual_DM/backend/tests/test_async_function_patterns.py:118: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

backend/tests/test_async_function_patterns.py:126
  /Users/Sharrone/Visual_DM/backend/tests/test_async_function_patterns.py:126: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

backend/tests/test_async_function_patterns.py:143
  /Users/Sharrone/Visual_DM/backend/tests/test_async_function_patterns.py:143: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

backend/tests/test_async_function_patterns.py:151
  /Users/Sharrone/Visual_DM/backend/tests/test_async_function_patterns.py:151: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

backend/tests/test_async_function_patterns.py:157
  /Users/Sharrone/Visual_DM/backend/tests/test_async_function_patterns.py:157: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

backend/tests/test_async_function_patterns.py:164
  /Users/Sharrone/Visual_DM/backend/tests/test_async_function_patterns.py:164: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

backend/tests/test_async_function_patterns.py:170
  /Users/Sharrone/Visual_DM/backend/tests/test_async_function_patterns.py:170: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

backend/tests/test_async_function_patterns.py:176
  /Users/Sharrone/Visual_DM/backend/tests/test_async_function_patterns.py:176: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

backend/tests/test_async_function_patterns.py:194
  /Users/Sharrone/Visual_DM/backend/tests/test_async_function_patterns.py:194: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

backend/tests/unit/app/core/schemas/test_websocket_service.py:25
  /Users/Sharrone/Visual_DM/backend/tests/unit/app/core/schemas/test_websocket_service.py:25: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

backend/tests/unit/app/core/schemas/test_websocket_service.py:40
  /Users/Sharrone/Visual_DM/backend/tests/unit/app/core/schemas/test_websocket_service.py:40: PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.asyncio

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================================ tests coverage ================================
_______________ coverage: platform darwin, python 3.11.5-final-0 _______________

=========================== short test summary info ============================
ERROR archives/models/test_uuid_mixin.py
ERROR archives/services/test_redis_service.py
ERROR archives/tests/test_combat_logger.py
ERROR archives/tests/test_combat_logger_and_scaling.py
ERROR archives/tests/test_combat_resolution.py
ERROR archives/tests/test_combat_state_manager.py
ERROR archives/tests/test_combat_system.py
ERROR archives/tests/test_db_connection.py
ERROR archives/tests/test_encounter_scaling.py
ERROR archives/tests/test_faction.py
ERROR archives/tests/test_git_service.py
ERROR archives/tests/test_hex_asset_manager.py
ERROR archives/tests/test_hex_asset_preview_ui.py
ERROR archives/tests/test_hex_asset_renderer.py
ERROR archives/tests/test_hex_sprite_sheet.py
ERROR archives/tests/test_location_version.py
ERROR archives/tests/test_loot_generator.py
ERROR archives/tests/test_loot_schema.py
ERROR archives/tests/test_migrations.py
ERROR archives/tests/test_npc_version.py
ERROR archives/tests/test_redis_connection.py
ERROR archives/tests/test_season_system.py
ERROR archives/tests/test_services.py - FileNotFoundError: [Errno 2] No such ...
ERROR archives/tests/test_status_effects.py
ERROR archives/tests/test_time_system.py
ERROR archives/tests/test_version_control.py
ERROR archives/tests/test_version_control_models.py
ERROR archives/tests/test_version_control_service.py
ERROR archives/tests/test_weather_consistency.py
ERROR archives/tests/test_weather_gameplay_impacts.py
ERROR archives/tests/test_weather_intensity_scaling.py
ERROR archives/tests/test_weather_sync_performance.py
ERROR archives/tests/test_weather_system.py
ERROR archives/tests/test_world_integration.py
ERROR archives/tests/test_world_persistence.py
ERROR archives/tests/test_world_validation.py
ERROR archives/tests/ui/components/test_base_components.py
ERROR archives/tests/ui/components/test_integration.py
ERROR archives/tests/ui/components/test_interactive_components.py
ERROR archives/tests/ui/components/test_security.py
ERROR archives/tests/unit/test_character_builder_equipment.py
ERROR archives/tests/validation/test_world_event_validation.py
ERROR archives/tests/visual_client/ui/screens/game/test_npc_viewer_panel.py
ERROR archives/tests/visual_client/ui/screens/test_template_editor.py
ERROR archives/tests/world/test_world_tick_utils.py
ERROR archives/tests/worldgen/test_deterministic_rng.py
ERROR backend/app/characters/test_character_builder.py
ERROR backend/app/models/test_uuid_mixin.py
ERROR backend/app/services/test_redis_service.py
ERROR backend/app/tests - ModuleNotFoundError: No module named 'app'
ERROR backend/combat/tests/test_damage_composition.py
ERROR backend/config_test.py
ERROR backend/core2/models/test_combat_system.py
ERROR backend/core2/persistence/test_version_control.py
ERROR backend/python_converted/src/worldgen/core/simple_test.py
ERROR backend/python_converted/src/worldgen/environment/__tests__/test_biome_transitions.py
ERROR backend/tests/api/test_websocket_endpoint.py
ERROR backend/tests/test_combat.py
ERROR backend/tests/test_coordinate_validation.py
ERROR backend/tests/test_feature_flags.py
ERROR backend/tests/test_id_generator.py
ERROR backend/tests/test_inventory.py
ERROR backend/tests/test_item_attributes.py
ERROR backend/tests/test_region.py
ERROR backend/tests/test_retry.py
ERROR backend/tests/test_world_event.py
ERROR backend/tests/unit/app/core/persistence/test_change_tracker.py
ERROR backend/tests/unit/app/core/schemas/test_example_templates.py
ERROR backend/tests/unit/app/core/schemas/test_review_template_factory.py
ERROR backend/tests/unit/app/core/schemas/test_websocket_schema.py
ERROR backend/tests/unit/core2/file_processing/test_concurrent_processor.py
ERROR backend/tests/unit/test_bible_qa_service.py
ERROR backend/tests/unit/test_motif_model.py
!!!!!!!!!!!!!!!!!!! Interrupted: 73 errors during collection !!!!!!!!!!!!!!!!!!!
================= 35 skipped, 13 warnings, 73 errors in 22.72s =================
