# Nemesis/Rival System Testing Framework

This directory contains the runtime testing framework for the Nemesis/Rival system in Visual_DM. All tests are written in C# and run at runtime (no UnityEditor code, no scene references, no prefabs).

## Structure
- **TestRunner.cs**: Discovers and runs all tests implementing `IRuntimeTest` at runtime. Attach this script to a GameObject in the Bootstrap scene or instantiate at runtime.
- **IRuntimeTest**: Interface for all runtime test classes.
- **[TestName]Test.cs**: Place new test classes here, each implementing `IRuntimeTest`.

## Adding New Tests
1. Create a new C# class in this directory implementing `IRuntimeTest`.
2. Implement the `TestName`, `RunTest()`, and `GetResultMessage()` members.
3. The test will be automatically discovered and run by `TestRunner` at runtime.

## Running Tests
- Ensure `TestRunner` is attached to a GameObject in the Bootstrap scene or instantiated at runtime.
- On game start, all tests will run and results will be logged to the Unity console.
- Results include pass/fail status, test name, and result message.

## Best Practices
- Use dependency injection and interfaces for testability.
- Avoid any Editor-only APIs or scene references.
- Keep tests deterministic and repeatable.
- Maintain clear, concise result messages for each test.
- Target 80%+ code coverage for critical systems.
- Document each test with comments explaining its purpose.

## Extending the Framework
- Add integration, simulation, performance, and stress tests as needed.
- For reporting/visualization, extend the framework with runtime UI (Canvas) or export results to CSV/JSON.
- See `TestRunner.cs` and `ExampleRelationshipStateMachineTest.cs` for templates.

## Test Results Reporting & Export
- The framework includes a `TestResultsReporter` utility for collecting and exporting test results.
- After running tests, results are automatically exported to CSV and JSON files in the Unity persistent data path.
- Example output files:
  - `NemesisRivalTestResults.csv`
  - `NemesisRivalTestResults.json`
- You can retrieve results at runtime for use in dashboards:
  ```csharp
  var results = TestResultsReporter.GetResults();
  foreach (var r in results) {
      Debug.Log($"{r.testName}: {(r.passed ? "PASS" : "FAIL")} - {r.message}");
  }
  ```

### CI/CD Integration
- Use the exported CSV/JSON files for automated test result collection in CI/CD pipelines.
- Files are written to `Application.persistentDataPath`.

### Runtime UI Integration
- Results can be displayed in a runtime dashboard by reading from `TestResultsReporter.GetResults()`.
- No UnityEditor or scene references required. 