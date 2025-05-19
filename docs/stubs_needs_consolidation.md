# Stubs: Has Existing Modules That Need Consolidation

This document lists all stubs that have partial or legacy implementations elsewhere, or multiple versions that need to be unified.

## List of Stubs Needing Consolidation

- `Region` (various files, e.g., backend/world/world_models.py, backend/app/core/models/region.py)
- `Faction` (various files, e.g., backend/app/models/faction.py, backend/app/core/models/faction.py)
- `LoggerStub` (backend/app/core/logging.py)
- `db` (backend/app/extensions.py)
- `ReviewTemplateFactory` (backend/app/core/schemas/review_template_factory.py)
- `ExampleTemplates` (backend/app/core/schemas/example_templates.py)
- `UUIDMixin` (backend/app/models/base.py)
- `ChangeRecord` (backend/app/core/persistence/change_tracker.py)
- `WorldVersionControl`, `VersionMetadata` (backend/app/core/persistence/version_control.py)
- `CombatSystem` (backend/app/core/models/combat_system.py)
- `Entity` (backend/app/core/models/entity.py)
- `SceneManager` (backend/app/core/models/scene_manager.py)
- `NetworkManager` (backend/app/core/models/network_manager.py)
- `GameState` (backend/app/core/models/game_state.py)
- `PerformanceProfiler`, `_BuildingProfilerStub` (backend/app/utils/profiling.py, backend/app/core/profiling/building_profiler.py)
- `OptimizedMeshRenderer` (backend/app/core/mesh/optimized_renderer.py)
- `LootTableEntry` (backend/app/combat/resolution.py)
- `TensionUtils` (backend/app/regions/tension_utils.py)
- `RedisService` (backend/app/services/redis_service.py)
- `CharacterBuilder` (backend/app/characters/character_builder_class.py)
- `SocialConsequences`, `SocialSkills` (backend/app/social/social_consequences.py, backend/app/social/social_skills.py)
- `DialogueGPTClient`, `IntentAnalyzer`, `GPTClient` (backend/app/core/utils/gpt/dialogue.py, intents.py, client.py)
- `update_npc_disposition` (backend/app/utils/social.py)
- `create_app`, `redis_client` (backend/app/__init__.py)
- `MockBattlefield`, `Dummy`, `save` (backend/app/combat/tests/test_damage_composition.py)

**Note:** These stubs have related code or patterns elsewhere and should be unified or refactored for consistency. 