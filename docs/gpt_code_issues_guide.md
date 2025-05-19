# Guide: Preventing and Fixing Common GPT-Generated Code Issues

This guide summarizes the most frequent issues found in GPT-generated code and provides best practices for detection and prevention. Use this as a reference for code review, static analysis, and future code generation.

## 1. Deprecated API/Library Usage
- **Detection:** Use static analysis tools (e.g., `pylint`, `bandit`, Roslyn analyzers) and check release notes for libraries.
- **Prevention:** Always check library documentation for current best practices.
- **Example (Python Pillow):** Use `textbbox()` instead of `textsize()`.
- **Example (C#):** Use `File.ReadAllText` with `using` instead of legacy file APIs.

## 2. Unclosed Resources
- **Detection:** Search for `open()`, `File.Open()`, or similar without `with`/`using`.
- **Prevention:** Always use context managers (`with` in Python, `using` in C#).

## 3. Improper Error Handling
- **Detection:** Look for bare `except:` or `catch {}` blocks.
- **Prevention:** Catch specific exceptions, log errors, and avoid swallowing exceptions.

## 4. Inefficient Algorithms
- **Detection:** Profile code, look for nested loops, and use static analysis for complexity.
- **Prevention:** Use sets/dictionaries for lookups, prefer built-in functions, and optimize for O(n) where possible.

## 5. Security Vulnerabilities
- **Detection:** Use `bandit` (Python), security analyzers (C#), and code review for unsafe patterns.
- **Prevention:** Never use `eval` on user input, validate all inputs, and keep secrets out of code.

## 6. Inconsistent Naming/Code Style
- **Detection:** Use linters (`flake8`, `pylint`, StyleCop).
- **Prevention:** Follow project style guides and enforce with CI.

## 7. Redundant/Dead Code
- **Detection:** Use static analysis and code coverage tools.
- **Prevention:** Remove unused variables, functions, and unreachable code.

## 8. Missing Input Validation
- **Detection:** Review all user input points.
- **Prevention:** Validate type, range, and format for all inputs.

## 9. Hardcoded Credentials/Sensitive Info
- **Detection:** Search for API keys, passwords, or secrets in code.
- **Prevention:** Use environment variables or secure vaults.

## 10. Incomplete Implementation
- **Detection:** Search for TODOs, unfinished functions, or missing logic.
- **Prevention:** Ensure all requirements are implemented and tested.

---

## Tooling Recommendations
- **Python:** `flake8`, `pylint`, `bandit`, `pytest`
- **C#:** Roslyn analyzers, StyleCop, NUnit
- **CI/CD:** Integrate all static analysis and tests into your pipeline.

## Example: Python Context Manager
```python
# Good
with open('file.txt') as f:
    data = f.read()
```

## Example: C# Using Statement
```csharp
// Good
using (var file = File.OpenRead("file.txt"))
{
    // ...
}
```

---

**Review this guide regularly and update as new issues are discovered.** 