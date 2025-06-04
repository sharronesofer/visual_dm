# Dreamforge Coding Standards

This document outlines the coding standards enforced by our C# static analysis tools (StyleCop, Roslyn analyzers, SonarAnalyzer) and provides guidance for compliance.

## Enforced Rules

- **Cyclomatic Complexity (CA1502):**
  - Methods should not exceed a complexity of 15.
  - Refactor large methods into smaller, focused functions.
- **Method Length (SA1502):**
  - Methods should not be excessively long (recommended max: 50 lines).
  - Use helper methods to break up logic.
- **Class Coupling (CA1505):**
  - Classes should not depend on too many other types.
  - Use interfaces and dependency injection to reduce coupling.
- **Inheritance Depth (S1200):**
  - Avoid deep inheritance hierarchies.
  - Prefer composition over inheritance.
- **Naming Conventions:**
  - Interfaces must begin with 'I' (e.g., `IService`).
  - Use PascalCase for class, method, and property names.

## Suppressing Warnings

If you must suppress a warning, use the following syntax in your code:

```csharp
#pragma warning disable CA1502 // Avoid excessive complexity
// ... code ...
#pragma warning restore CA1502 // Avoid excessive complexity
```

Or for a single line:

```csharp
[System.Diagnostics.CodeAnalysis.SuppressMessage("Major Code Smell", "CA1502:Avoid excessive complexity", Justification = "Reviewed and accepted complexity.")]
```

## Common Violations and Fixes

### Example: High Cyclomatic Complexity
**Violation:**
```csharp
public void ProcessData(int[] data) {
    if (data == null) return;
    for (int i = 0; i < data.Length; i++) {
        if (data[i] > 0) {
            // ...
        } else if (data[i] < 0) {
            // ...
        } else {
            // ...
        }
    }
    // ... many more branches ...
}
```
**Fix:**
Refactor into smaller methods for each branch.

### Example: Excessive Method Length
**Violation:**
```csharp
public void LongMethod() {
    // 100+ lines of code
}
```
**Fix:**
Break into multiple helper methods.

### Example: Excessive Class Coupling
**Violation:**
```csharp
public class DataManager {
    private ServiceA _a;
    private ServiceB _b;
    private ServiceC _c;
    // ... many more dependencies ...
}
```
**Fix:**
Use interfaces and inject only what is needed.

## IDE Integration
- Visual Studio and VS Code will show warnings/errors inline.
- Fix issues as you code to avoid build failures.

## CI Pipeline
- The build will fail if critical rules are violated (once rules are set to error).
- Review the build logs for details on violations.

## Running Static Analysis Locally
- Run `dotnet build Dreamforge/Assembly-CSharp.csproj` to see analyzer warnings and errors.
- Fix issues before pushing code to avoid CI failures.

## Running Static Analysis in CI
- The GitHub Actions workflow in `.github/workflows/ci.yml` will automatically run analyzers on every push and pull request to `main`.
- Builds will fail if critical rules are violated (once rules are set to error).
- Review the uploaded build logs for details on violations.

## Questions?
Contact the maintainers or review the .editorconfig and ruleset files for more details. 