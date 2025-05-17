# Guide: Understanding and Avoiding Common GPT-Generated Code Issues

## Introduction

Large Language Models (LLMs) like GPT can generate code quickly, but often introduce subtle or critical issues. This guide explains the most common categories of problems, why they occur, and how to avoid them using best practices and automated tools.

---

## Issue Categories & Best Practices

### 1. Deprecated API Usage
- **Why it happens:** LLMs are trained on historical data, so they may suggest outdated APIs.
- **Best Practice:** Always check official documentation for current APIs. Use linters to flag deprecated usage.
- **Example (Python):**
  ```python
  # ❌ Deprecated
  loop = asyncio.get_event_loop()
  # ✅ Modern
  loop = asyncio.new_event_loop()
  ```

### 2. Resource Management Problems
- **Why it happens:** LLMs may omit context needed for proper resource cleanup.
- **Best Practice:** Use context managers (`with` in Python, `using` in C#) for files, sockets, DB connections.
- **Example (Python):**
  ```python
  # ❌
  f = open('data.txt')
  data = f.read()
  # ✅
  with open('data.txt') as f:
      data = f.read()
  ```

### 3. Error Handling Deficiencies
- **Why it happens:** LLMs often use broad or silent error handling to avoid breaking code.
- **Best Practice:** Catch specific exceptions, log errors, and avoid silent failures.
- **Example (Python):**
  ```python
  # ❌
  try:
      risky()
  except Exception:
      pass
  # ✅
  try:
      risky()
  except ValueError as e:
      print(f"Value error: {e}")
  ```

### 4. Security Vulnerabilities
- **Why it happens:** LLMs may not recognize context where user input is unsafe.
- **Best Practice:** Never use `eval` on user input, avoid hardcoded secrets, sanitize all inputs.
- **Example (Python):**
  ```python
  # ❌
  eval(user_input)
  # ✅
  import ast
  ast.literal_eval(user_input)
  ```

### 5. Performance Anti-Patterns
- **Why it happens:** LLMs may generate code that is correct but inefficient.
- **Best Practice:** Use idiomatic constructs (list comprehensions, async IO, etc.), profile code for bottlenecks.
- **Example (Python):**
  ```python
  # ❌
  results = []
  for i in range(10000):
      results.append(i * 2)
  # ✅
  results = [i * 2 for i in range(10000)]
  ```

### 6. Language-Specific Issues
- **Why it happens:** LLMs may not handle language quirks (e.g., Python mutable defaults).
- **Best Practice:** Learn language-specific pitfalls and use static analysis tools.
- **Example (Python):**
  ```python
  # ❌
  def add_item(item, items=[]):
      items.append(item)
      return items
  # ✅
  def add_item(item, items=None):
      if items is None:
          items = []
      items.append(item)
      return items
  ```

---

## Cheat Sheet: Issues & Solutions

| Category                  | Problem Example                | Solution Example                |
|---------------------------|--------------------------------|---------------------------------|
| Deprecated API            | `asyncio.get_event_loop()`     | `asyncio.new_event_loop()`      |
| Resource Management       | `f = open('file')`             | `with open('file') as f:`       |
| Error Handling            | `except:` or `except Exception:`| `except ValueError as e:`      |
| Security                  | `eval(user_input)`             | `ast.literal_eval(user_input)`  |
| Performance               | `for ... append()`             | `[...] for ... in ...`          |
| Mutable Default Args      | `def f(x, y=[])`               | `def f(x, y=None)`              |

---

## Using Automated Tools

- **Static Analysis:** Run `scripts/gpt_code_static_analysis.py` to detect and optionally fix issues.
- **CI Integration:** The provided GitHub Actions workflow runs static analysis on every push/PR and fails the build on critical/security issues.
- **Autofix:** Use `--autofix` to automatically apply safe fixes (backups are made).

---

## References & Further Reading
- [Pylint Documentation](https://pylint.pycqa.org/)
- [ESLint Rules](https://eslint.org/docs/latest/rules/)
- [Microsoft C# Best Practices](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/)
- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [SonarQube Rules](https://rules.sonarsource.com/)

---

## Feedback

If you have suggestions or spot issues not covered here, please contribute to the catalog or open an issue in the repository. 