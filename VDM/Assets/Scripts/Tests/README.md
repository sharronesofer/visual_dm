# VDM Unity Frontend Testing Suite

## Overview

This comprehensive testing suite provides complete test coverage for the VDM Unity frontend restructuring project. The testing framework includes unit tests, integration tests, UI tests, end-to-end tests, and performance tests to ensure the frontend meets all quality requirements.

## Architecture

### Test Framework Structure

```
VDM/Assets/Scripts/Tests/
├── Core/                          # Core testing framework and utilities
│   ├── TestFramework.cs          # Base test classes for different test types
│   ├── MockBackendService.cs     # Mock backend for testing
│   ├── UITestHelper.cs           # UI testing utilities
│   ├── TestDataFactory.cs       # Test data generation
│   └── ScenarioRunner.cs         # End-to-end scenario testing
├── Core/Character/               # Unit tests for Character system
│   └── CharacterSystemTests.cs  # Character component unit tests
├── Integration/                  # Integration tests
│   └── SystemIntegrationTests.cs # Cross-system integration tests
├── UI/                          # UI component tests
│   └── UIComponentTests.cs      # Unity UI component testing
├── EndToEnd/                    # End-to-end workflow tests
│   └── GameplayWorkflowTests.cs # Complete gameplay scenario tests
├── TestRunner/                  # Test execution and reporting
│   └── ComprehensiveTestRunner.cs # Main test runner with reporting
└── README.md                    # This documentation
```

## Test Types

### 1. Unit Tests

Unit tests focus on testing individual components in isolation. They use the `VDMUnitTestBase` class and mock dependencies.

**Example:**
```csharp
public class CharacterSystemTests : VDMUnitTestBase
{
    [Test]
    public void CharacterCreation_WithValidData_ShouldSucceed()
    {
        // Arrange
        var characterData = new { name = "Test Hero", class_ = "Warrior" };
        
        // Act
        var character = CreateCharacter(characterData);
        
        // Assert
        Assert.IsNotNull(character);
        Assert.AreEqual("Test Hero", character.Name);
    }
}
```

### 2. Integration Tests

Integration tests verify that different systems work correctly together. They use the `VDMIntegrationTestBase` class and mock backend services.

**Example:**
```csharp
public class SystemIntegrationTests : VDMIntegrationTestBase
{
    [Test]
    public async Task CharacterQuestInteraction_WhenQuestCompleted_ShouldUpdateCharacterExperience()
    {
        // Test character-quest system integration
        var questResult = await MockBackend.CallAPI("POST", "/api/quests/101/complete");
        var characterUpdate = await MockBackend.CallAPI("PUT", "/api/characters/1", 
            new { experience = 800 });
            
        Assert.IsTrue(questResult.IsSuccess);
        Assert.IsTrue(characterUpdate.IsSuccess);
    }
}
```

### 3. UI Tests

UI tests verify Unity interface components work correctly. They use the `VDMUITestBase` class and UI testing utilities.

**Example:**
```csharp
public class UIComponentTests : VDMUITestBase
{
    [UnityTest]
    public IEnumerator CharacterCreationUI_WhenFormCompleted_ShouldEnableCreateButton()
    {
        // Arrange
        var nameInput = UIHelper.CreateTestInputField("Enter character name");
        var createButton = UIHelper.CreateTestButton("Create Character");
        
        // Act
        UIHelper.SimulateTextInput(nameInput, "Test Hero");
        yield return new WaitForEndOfFrame();
        
        // Assert
        Assert.AreEqual("Test Hero", nameInput.text);
    }
}
```

### 4. End-to-End Tests

End-to-end tests verify complete user workflows from start to finish. They use the `VDMEndToEndTestBase` class and scenario runner.

**Example:**
```csharp
public class GameplayWorkflowTests : VDMEndToEndTestBase
{
    [UnityTest]
    public IEnumerator CompleteCharacterJourney_FromCreationToQuestCompletion_ShouldSucceed()
    {
        var testTask = RunCompleteCharacterJourneyAsync();
        yield return new WaitUntil(() => testTask.IsCompleted);
        
        var result = testTask.Result;
        Assert.AreEqual(ScenarioStatus.Succeeded, result.Status);
    }
}
```

### 5. Performance Tests

Performance tests verify system performance under various conditions including memory usage, frame rate, and stress testing.

## Core Components

### TestFramework.cs

Provides base classes for all test types:
- `VDMTestBase` - Common functionality for all tests
- `VDMUnitTestBase` - Unit test base with offline mock backend
- `VDMIntegrationTestBase` - Integration test base with mock API responses
- `VDMUITestBase` - UI test base with UI helper utilities
- `VDMEndToEndTestBase` - End-to-end test base with scenario runner

### MockBackendService.cs

Comprehensive mock backend that simulates API responses:
- **Three modes**: Offline, Mock, Live
- **Default mock data** for all 9 core systems
- **API response simulation** with network delays and failure simulation
- **WebSocket message simulation** for real-time features
- **Stress testing data generation**

### UITestHelper.cs

Unity UI testing utilities:
- **Test canvas creation** and event system setup
- **UI element factories** (buttons, inputs, toggles, sliders)
- **Interaction simulation** (clicks, text input, toggles)
- **Assertion methods** for UI visibility and state
- **Screenshot capture** for visual regression testing

### TestDataFactory.cs

Generic test data creation system:
- **Property override support** for customized test data
- **Intelligent default values** based on property names/types
- **Complex type support** (Vector2/3, Color, DateTime, Lists, Enums)
- **System-specific generators** for VDM data types

### ScenarioRunner.cs

End-to-end testing framework:
- **10 predefined scenarios** covering major gameplay workflows
- **Custom scenario registration** system
- **ScenarioResult tracking** with execution status and timing
- **Complete user workflow simulation**

## Usage Guide

### Running Tests

#### Option 1: Unity Test Runner
1. Open **Window > General > Test Runner**
2. Select **PlayMode** or **EditMode** tab
3. Click **Run All** or select specific tests

#### Option 2: Comprehensive Test Runner
1. Add `ComprehensiveTestRunner` component to a GameObject
2. Configure test settings in inspector
3. Run via **Context Menu > Run All Tests** or set `Run On Start`

#### Option 3: Command Line
```bash
# Run all tests
Unity -batchmode -projectPath /path/to/VDM -runTests -testResults results.xml

# Run specific test suite
Unity -batchmode -projectPath /path/to/VDM -runTests -testCategory "Unit" -testResults unit-results.xml
```

### Creating New Tests

#### 1. Unit Test Example
```csharp
using NUnit.Framework;
using VDM.Tests.Core;

namespace VDM.Tests.Core.MySystem
{
    public class MySystemTests : VDMUnitTestBase
    {
        [Test]
        public void MyComponent_WhenValidInput_ShouldSucceed()
        {
            // Arrange
            var testData = CreateTestData<MyTestData>();
            
            // Act
            var result = MyComponent.Process(testData);
            
            // Assert
            Assert.IsTrue(result.IsSuccess);
            
            // Performance validation
            AssertPerformance(100f); // Should complete within 100ms
        }
    }
}
```

#### 2. Integration Test Example
```csharp
using System.Threading.Tasks;
using NUnit.Framework;
using VDM.Tests.Core;

namespace VDM.Tests.Integration
{
    public class MyIntegrationTests : VDMIntegrationTestBase
    {
        [Test]
        public async Task SystemInteraction_WhenCalled_ShouldUpdateBothSystems()
        {
            // Arrange
            MockBackend.SetAPIResponse("GET", "/api/system1", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { id = 1, value = "test" }
            });
            
            // Act
            var result = await MockBackend.CallAPI("GET", "/api/system1");
            
            // Assert
            Assert.IsTrue(result.IsSuccess);
        }
    }
}
```

#### 3. UI Test Example
```csharp
using System.Collections;
using UnityEngine.TestTools;
using VDM.Tests.Core;

namespace VDM.Tests.UI
{
    public class MyUITests : VDMUITestBase
    {
        [UnityTest]
        public IEnumerator MyUIComponent_WhenInteracted_ShouldUpdateCorrectly()
        {
            // Arrange
            var button = UIHelper.CreateTestButton("Test Button");
            var wasClicked = false;
            button.onClick.AddListener(() => wasClicked = true);
            
            // Act
            UIHelper.SimulateClick(button.gameObject);
            yield return new WaitForEndOfFrame();
            
            // Assert
            Assert.IsTrue(wasClicked);
            UIHelper.AssertUIElementVisible(button.gameObject);
        }
    }
}
```

### Best Practices

#### Test Organization
- **One test class per system component**
- **Group related tests using nested classes**
- **Use descriptive test method names** following the pattern: `Method_When_Should`
- **Organize tests by functionality**, not alphabetically

#### Test Data Management
- **Use TestDataFactory** for consistent test data creation
- **Override only necessary properties** in test data
- **Avoid hardcoded values** - use constants or test data generation
- **Clean up test data** in TearDown methods

#### Assertions and Validation
- **Use specific assertions** rather than generic Assert.IsTrue
- **Include meaningful failure messages** in assertions
- **Test both positive and negative cases**
- **Validate performance metrics** using AssertPerformance

#### Mock Usage
- **Set up mocks before each test** in SetUp methods
- **Use realistic mock data** that matches production patterns
- **Test error scenarios** with mock failures
- **Verify mock interactions** when testing integration points

## Coverage Requirements

### Target Coverage Metrics
- **≥90% Code Coverage** across all systems
- **100% Critical Path Coverage** for essential workflows
- **Zero Compilation Errors** in all test configurations
- **≤200ms Average API Response Time** in performance tests
- **≥60 FPS Maintained** during UI performance tests

### Coverage Areas

#### Systems Coverage
- ✅ Character System (Creation, progression, equipment)
- ✅ Quest System (Assignment, progression, completion)
- ✅ Combat System (Actions, damage, turn management)
- ✅ Inventory System (Items, storage, organization)
- ✅ Faction System (Relationships, reputation, politics)
- ✅ Dialogue System (Conversations, choices, branching)
- ✅ Economy System (Trading, markets, currency)
- ✅ World System (State, exploration, events)
- ✅ Time System (Progression, scheduling, events)
- ✅ Analytics System (Tracking, reporting, metrics)

#### UI Coverage
- ✅ Character Creation Interface
- ✅ Inventory Management UI
- ✅ Quest Log and Tracking
- ✅ Combat Action Interface
- ✅ Dialogue Choice System
- ✅ Market and Trading UI
- ✅ World Map Interface
- ✅ Settings and Configuration
- ✅ Loading and Progress Screens
- ✅ Modal Dialogs and Confirmations

#### Integration Coverage
- ✅ Character-Quest Integration
- ✅ Combat-Inventory Integration
- ✅ Faction-Dialogue Integration
- ✅ Economy-Inventory Integration
- ✅ World-Time Integration
- ✅ Multi-system Workflows
- ✅ Error Handling and Recovery
- ✅ Performance Under Load

## Continuous Integration

### GitHub Actions Integration

Create `.github/workflows/tests.yml`:
```yaml
name: Unity Tests
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: game-ci/unity-test-runner@v2
      with:
        projectPath: VDM
        testMode: playmode
        artifactsPath: test-results
        coverageOptions: 'generateAdditionalMetrics;generateHtmlReport;generateBadgeReport'
    
    - uses: actions/upload-artifact@v2
      with:
        name: test-results
        path: test-results
```

### Local Development Workflow

1. **Write tests first** (TDD approach recommended)
2. **Run tests locally** before committing
3. **Maintain coverage** - don't decrease overall coverage percentage
4. **Fix failing tests immediately** - don't accumulate technical debt
5. **Review test results** in PR reviews

## Troubleshooting

### Common Issues

#### Tests Not Running
- **Check Unity Test Framework** is installed in Package Manager
- **Verify assembly references** in test .asmdef files
- **Ensure test methods** have proper attributes ([Test], [UnityTest])

#### Mock Backend Issues
- **Reset mock data** between tests in SetUp methods
- **Check API endpoint paths** match exactly (case-sensitive)
- **Verify mock response format** matches expected data structure

#### UI Test Failures
- **Wait for frame updates** using `yield return new WaitForEndOfFrame()`
- **Check UI hierarchy** - elements must be children of test canvas
- **Verify UI element states** before interactions

#### Performance Test Inconsistency
- **Run on consistent hardware** for reliable performance metrics
- **Account for Unity Editor overhead** when setting thresholds
- **Use multiple iterations** and average results for stability

### Debug Strategies

#### Enabling Detailed Logging
```csharp
// In test setup
UnityEngine.Debug.unityLogger.logEnabled = true;
UnityEngine.Debug.unityLogger.filterLogType = LogType.Log;
```

#### Test Data Inspection
```csharp
// In test methods
Debug.Log($"Test Data: {JsonUtility.ToJson(testData, true)}");
Debug.Log($"Mock Response: {JsonUtility.ToJson(mockResponse.Data, true)}");
```

#### Performance Profiling
```csharp
// In performance tests
using (new ProfilerScope("Test Operation"))
{
    // Test code here
}
```

## Reporting and Metrics

### Test Reports

The `ComprehensiveTestRunner` generates detailed reports including:
- **Execution Summary** with pass/fail counts and percentages
- **Performance Metrics** for response times and frame rates
- **Coverage Analysis** showing tested vs untested code areas
- **Test Duration Analysis** identifying slow tests
- **Error Categorization** grouping similar failures

### Coverage Reports

Generated coverage reports include:
- **Line Coverage** percentage by file and system
- **Branch Coverage** for conditional logic paths
- **Method Coverage** for public API surface area
- **Integration Coverage** for cross-system interactions

### Performance Dashboards

Performance test results track:
- **API Response Times** across all endpoints
- **Memory Usage** patterns during test execution
- **Frame Rate** stability under various loads
- **Stress Test** success rates and failure points

## Contributing

### Adding New Tests

1. **Create test class** in appropriate directory
2. **Inherit from correct base class** for test type
3. **Follow naming conventions** and documentation standards
4. **Include performance assertions** where applicable
5. **Update this README** if adding new patterns or frameworks

### Modifying Test Framework

1. **Discuss changes** in GitHub issues before implementation
2. **Maintain backward compatibility** where possible
3. **Update all affected tests** when changing base classes
4. **Document breaking changes** in commit messages and PR descriptions
5. **Ensure all existing tests pass** with framework changes

---

## Quick Reference

### Key Classes
- `VDMTestBase` - Base for all tests
- `MockBackendService` - API mocking
- `UITestHelper` - UI interaction utilities
- `TestDataFactory` - Test data generation
- `ScenarioRunner` - End-to-end workflows
- `ComprehensiveTestRunner` - Complete test execution

### Important Directories
- `Core/` - Framework and utilities
- `Integration/` - Cross-system tests
- `UI/` - Interface component tests
- `EndToEnd/` - Complete workflow tests
- `TestRunner/` - Execution and reporting

### Coverage Targets
- **90%** overall code coverage
- **≤200ms** API response times
- **≥60 FPS** UI performance
- **95%** stress test success rate

For more detailed information, see individual component documentation in their respective files. 