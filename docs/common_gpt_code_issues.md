# Common GPT-Generated Code Issues Checklist

This checklist documents the most frequent issues found in GPT-generated code, with explanations and examples. Use this as a reference for code review and static analysis.

## 1. Deprecated API/Library Usage
- **Description:** Use of outdated or deprecated APIs that may break in future versions.
- **Example (Python Pillow):**
  ```python
  # Deprecated
  size = draw.textsize(text, font=font)
  # Correct
  bbox = draw.textbbox((0, 0), text, font=font)
  ```

## 2. Unclosed Resources
- **Description:** Files, sockets, or database connections not properly closed, leading to resource leaks.
- **Example (Python):**
  ```python
  # Bad
  f = open('file.txt')
  data = f.read()
  # Good
  with open('file.txt') as f:
      data = f.read()
  ```

## 3. Improper Error Handling
- **Description:** Bare excepts, missing logging, or swallowing exceptions.
- **Example:**
  ```python
  # Bad
  try:
      ...
  except:
      pass
  # Good
  try:
      ...
  except Exception as e:
      logging.error(f"Error: {e}")
      raise
  ```

## 4. Inefficient Algorithms
- **Description:** Unnecessary nested loops, O(n^2) when O(n) is possible, etc.
- **Example:**
  ```python
  # Bad
  for i in range(len(lst)):
      for j in range(len(lst)):
          if lst[i] == lst[j]:
              ...
  # Good
  seen = set()
  for item in lst:
      if item in seen:
          ...
      seen.add(item)
  ```

## 5. Security Vulnerabilities
- **Description:** SQL injection, unsafe eval, hardcoded credentials, etc.
- **Example:**
  ```python
  # Bad
  eval(user_input)
  # Good
  # Avoid eval, use safe parsing
  ```

## 6. Inconsistent Naming/Code Style
- **Description:** Mixed naming conventions, inconsistent formatting.
- **Example:**
  ```python
  # Bad
  myVariable = 1
  my_variable = 2
  # Good
  my_variable = 1
  another_variable = 2
  ```

## 7. Redundant/Dead Code
- **Description:** Unused variables, unreachable code, duplicate logic.

## 8. Missing Input Validation
- **Description:** Not checking user input for type, range, or format.
- **Example:**
  ```python
  # Bad
  def set_age(age):
      self.age = age
  # Good
  def set_age(age):
      if not isinstance(age, int) or age < 0:
          raise ValueError("Invalid age")
      self.age = age
  ```

## 9. Hardcoded Credentials/Sensitive Info
- **Description:** API keys, passwords, or secrets in code.

## 10. Incomplete Implementation
- **Description:** Functions/classes missing required logic, TODOs left in production code.

---

**Use this checklist for every code review and static analysis pass.** 