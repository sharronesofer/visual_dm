# Visual DM Test Suite

This directory contains the comprehensive test suite for the Visual DM project, encompassing both backend (Python/FastAPI) and frontend (Unity/C#) tests.

## Test Structure

### Backend Tests

The backend tests are organized into the following categories:

1. **API Tests** (`backend/tests/api/`): Tests for the FastAPI endpoints.
2. **Integration Tests** (`backend/tests/integration/`): Tests that verify multiple components working together.
3. **Unit Tests** (`backend/tests/unit/`): Tests for individual functions and classes.

### Frontend Tests

The Unity frontend tests are organized into:

1. **System Tests** (`VDM/Assets/Scripts/Tests/Systems/`): Tests for game systems like the quest system, dialogue system, etc.
2. **UI Tests** (`VDM/Assets/Scripts/Tests/UI/`): Tests for user interface components.
3. **Other Tests** (`VDM/Assets/Scripts/Tests/`): Additional test categories for various components.

## Running Tests

### Automated All-in-One Approach

To run all tests at once and get a combined report, use the `run_all_tests.py` script:

```bash
python run_all_tests.py
```

This script will:
1. Run all backend tests using pytest
2. Run all frontend tests using Unity's test runner
3. Generate a combined test report

#### Command-line Options

- `--backend-only`: Run only the backend tests
- `--frontend-only`: Run only the frontend tests
- `--report`: Generate detailed test reports
- `--coverage`: Generate code coverage reports
- `--verbose`: Show detailed test output

Example:

```bash
python run_all_tests.py --coverage --report
```

### Running Backend Tests Individually

You can also run the backend tests using the dedicated backend test runner:

```bash
cd backend
python run_tests.py
```

Or using pytest directly:

```bash
cd backend
pytest tests/
```

For specific test categories:

```bash
pytest tests/api/          # API tests only
pytest tests/unit/         # Unit tests only
pytest tests/integration/  # Integration tests only
```

### Running Frontend Tests Individually

Frontend tests can be run from within the Unity Editor:

1. Open the Unity project (`VDM/`)
2. Go to `Window > General > Test Runner`
3. In the Test Runner window, click on `Run All` or select specific tests to run

Or use the TestRunner class from code:

```csharp
// From Unity C# code
VDM.Tests.TestRunner.RunAllTests();
// or 
VDM.Tests.TestRunner.RunPlayModeTests();
// or
VDM.Tests.TestRunner.RunEditModeTests();
```

## Test Reports

Test reports will be generated in the following locations:

- Backend test logs: `backend_test_results_*.txt`
- Backend coverage report: `reports/backend-coverage/`
- Frontend test logs: `unity_test_results_*.xml`
- Combined test report: `reports/combined_test_report_*.txt`
- Summary report: `test_results_summary.txt`

## Adding New Tests

### Adding Backend Tests

1. Create a new test file in the appropriate directory (`api/`, `unit/`, or `integration/`)
2. Use the pytest framework and follow the naming convention `test_*.py`
3. Write test functions with the prefix `test_`
4. Use fixtures from `conftest.py` for common setup

Example:

```python
# backend/tests/unit/test_new_feature.py
import pytest

def test_my_new_feature():
    # Test code here
    assert True
```

### Adding Frontend Tests

1. Create a new test class in the appropriate directory
2. Inherit from `TestFramework` base class
3. Use the NUnit test attributes (`[Test]`, `[SetUp]`, etc.)
4. Use `UnityTest` attribute for coroutine-based tests

Example:

```csharp
// VDM/Assets/Scripts/Tests/Systems/NewFeatureTests.cs
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace VDM.Tests
{
    public class NewFeatureTests : TestFramework
    {
        [SetUp]
        public override void Setup()
        {
            base.Setup();
            // Additional setup
        }
        
        [Test]
        public void MyNewFeature_ShouldWorkAsExpected()
        {
            // Test code here
            Assert.IsTrue(true);
        }
    }
}
```

## Continuous Integration

This test suite is designed to work with CI/CD pipelines. The `run_all_tests.py` script will return a non-zero exit code if any tests fail, making it suitable for automated testing.

## Troubleshooting

If you encounter issues running the tests:

1. Ensure all dependencies are installed (`pip install -r requirements-test.txt`)
2. Check that Unity is properly installed and the project path is correct
3. Verify that the Python environment has pytest and other required packages
4. Check the log files for detailed error messages 