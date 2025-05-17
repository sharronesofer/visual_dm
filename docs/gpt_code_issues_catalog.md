# Catalog of Common GPT-Generated Code Issues

## Table of Contents
1. [Deprecated API Usage](#deprecated-api-usage)
2. [Resource Management Problems](#resource-management-problems)
3. [Error Handling Deficiencies](#error-handling-deficiencies)
4. [Security Vulnerabilities](#security-vulnerabilities)
5. [Performance Anti-Patterns](#performance-anti-patterns)
6. [Language-Specific Issues](#language-specific-issues)
7. [References](#references)

---

## 1. Deprecated API Usage
- **Description:** Use of APIs, functions, or libraries that are outdated or no longer recommended.
- **Examples:**
  - Python: Using `asyncio.get_event_loop()` (deprecated in Python 3.10+)
  - C#: Using `WebClient` instead of `HttpClient`
  - JavaScript: Using `var` instead of `let`/`const`
- **Problematic Example:**
  ```python
  # Deprecated usage
  loop = asyncio.get_event_loop()
  ```
- **Corrected Example:**
  ```python
  # Modern usage
  loop = asyncio.new_event_loop()
  ```
- **Severity:** Major
- **Frequency:** Common

---

## 2. Resource Management Problems
- **Description:** Failing to properly close files, sockets, or database connections, leading to resource leaks.
- **Examples:**
  - Python: Not using `with` for file operations
  - C#: Not disposing `IDisposable` objects
  - JavaScript: Unclosed WebSocket connections
- **Problematic Example:**
  ```python
  f = open('data.txt')
  data = f.read()
  # File not closed
  ```
- **Corrected Example:**
  ```python
  with open('data.txt') as f:
      data = f.read()
  # File automatically closed
  ```
- **Severity:** Critical
- **Frequency:** Common

---

## 3. Error Handling Deficiencies
- **Description:** Missing, overly broad, or silent error handling that can mask bugs or cause crashes.
- **Examples:**
  - Python: Catching `Exception` instead of specific errors
  - C#: Empty catch blocks
  - JavaScript: Not handling promise rejections
- **Problematic Example:**
  ```python
  try:
      risky_operation()
  except Exception:
      pass  # Silent failure
  ```
- **Corrected Example:**
  ```python
  try:
      risky_operation()
  except ValueError as e:
      print(f"Value error: {e}")
  ```
- **Severity:** Major
- **Frequency:** Common

---

## 4. Security Vulnerabilities
- **Description:** Patterns that introduce security risks, such as injection, unsafe eval, or hardcoded secrets.
- **Examples:**
  - Python: Using `eval()` on user input
  - C#: Hardcoded passwords
  - JavaScript: Unsanitized DOM manipulation
- **Problematic Example:**
  ```python
  eval(user_input)
  ```
- **Corrected Example:**
  ```python
  # Avoid eval; use safe parsing
  parsed = int(user_input)
  ```
- **Severity:** Critical
- **Frequency:** Occasional

---

## 5. Performance Anti-Patterns
- **Description:** Inefficient code that can degrade performance, such as unnecessary allocations or blocking calls.
- **Examples:**
  - Python: Using list comprehensions for side effects
  - C#: Blocking async code with `.Result`
  - JavaScript: Inefficient DOM queries in loops
- **Problematic Example:**
  ```python
  results = []
  for i in range(10000):
      results.append(i * 2)
  ```
- **Corrected Example:**
  ```python
  results = [i * 2 for i in range(10000)]
  ```
- **Severity:** Minor to Major
- **Frequency:** Common

---

## 6. Language-Specific Issues
- **Description:** Issues unique to a language, such as Python's mutable default arguments or C#'s improper IDisposable usage.
- **Examples:**
  - Python: Mutable default arguments
  - C#: Not implementing `IDisposable` correctly
  - JavaScript: Hoisting confusion
- **Problematic Example:**
  ```python
  def add_item(item, items=[]):
      items.append(item)
      return items
  ```
- **Corrected Example:**
  ```python
  def add_item(item, items=None):
      if items is None:
          items = []
      items.append(item)
      return items
  ```
- **Severity:** Major
- **Frequency:** Occasional

---

## 7. References
- [Pylint Documentation](https://pylint.pycqa.org/)
- [ESLint Rules](https://eslint.org/docs/latest/rules/)
- [Microsoft C# Best Practices](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/)
- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [SonarQube Rules](https://rules.sonarsource.com/) 