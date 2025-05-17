# Visual DM Test Suite

## Overview
This directory contains automated tests for the Visual DM project, covering:
- Unit tests
- Integration tests
- End-to-end (PlayMode/UI) tests
- Performance and security tests

## Structure
- `CoreTests.cs` — Core systems (StateManager, EventBus, IdGenerator)
- `WorldTests.cs` — World systems (WorldTimeSystem, SeasonSystem, etc.)
- `StorageTests.cs` — Storage systems (FileSystemStorageProvider, etc.)
- `QuestTests.cs` — Quest systems (Quest, QuestStage, RewardGenerator)
- `UITests.cs` — UI logic (FileUploadService, FileValidationService, ItemManagementPanel)
- `NPCPersonalityTests.cs`, `DialogueServiceTests.cs` — Existing tests for NPC and Dialogue

## Running Unity Tests
1. Open the project in Unity.
2. Open the Test Runner window (`Window > General > Test Runner`).
3. Run EditMode and PlayMode tests.
4. Review results and coverage.

## Python Backend Tests
- Python backend tests are located in `server/tests/`.
- Use `pytest` and `pytest-asyncio` for unit/integration tests.
- Use `locust` for load testing, `bandit` for security.

## Coverage Goals
- All major systems and features should have unit and integration tests.
- UI logic should be tested for correctness, not rendering.
- End-to-end flows should be covered by PlayMode tests.
- Performance and security tests should be automated in CI/CD.

## Best Practices
- Use setup/teardown to isolate test state.
- Mock dependencies where possible.
- Add new tests for all new features and bug fixes.
- Keep tests fast and reliable.

---
For questions or contributions, see the project documentation or contact the maintainers. 