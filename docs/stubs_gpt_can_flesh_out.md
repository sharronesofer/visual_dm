# Stubs: Obvious Enough That GPT Can Flesh Out

This document lists all stubs that are standard patterns or have clear names/roles, so GPT can generate a solid first implementation.

## List of Stubs GPT Can Flesh Out

- All `get_npc_*` functions (memory, relationship, dialogue, schedule, inventory, stats, skills, quests, etc.) in backend/app/core/npc/
- `AppException`, `ValidationError`, `GenerationError`, `NotFoundError` (backend/app/utils/exceptions.py, backend/app/core/utils/error_utils.py)
- `CodeQualityMetrics` (backend/app/code_quality/metrics.py)
- `ReviewTemplateFactory` (backend/app/core/schemas/review_template_factory.py)
- `LootTableEntry` (backend/app/combat/resolution.py)
- `ChangeRecord` (backend/app/core/persistence/change_tracker.py)
- `PerformanceProfiler` (backend/app/utils/profiling.py)
- `TensionUtils` (backend/app/regions/tension_utils.py)
- `update_npc_disposition` (backend/app/utils/social.py)
- `property_test_world_cli`, `validate_world_cli` (backend/app/core/validation/validation_api.py)
- `log_usage`, `get_goodwill_label` (backend/app/core/utils/gpt/utils.py)
- `commit` (backend/app/core/models/world/world_backup.py, world.py)
- `create_app`, `redis_client` (backend/app/__init__.py)
- `MockBattlefield`, `Dummy`, `save` (backend/app/combat/tests/test_damage_composition.py)
- `_noop_decorator` (backend/app/core/profiling/building_profiler.py)
- `OptimizedMeshRenderer` (backend/app/core/mesh/optimized_renderer.py)
- `WorldEvent` (backend/app/core/models/world_event.py)

**Note:** These stubs are clear in intent and can be implemented directly by GPT or a developer with minimal additional context. 