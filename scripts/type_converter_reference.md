# TypeScript to Python Type Conversion Reference

## Overview
This document describes the logic, rules, and mappings used to convert TypeScript types to Python type annotations using the `TypeConverter` class and the `ts2py.py` tool.

---

## Primitive Type Mappings
| TypeScript      | Python    |
|----------------|-----------|
| `string`       | `str`     |
| `number`       | `float`   |
| `boolean`      | `bool`    |
| `any`          | `Any`     |
| `void`         | `None`    |
| `null`         | `None`    |
| `undefined`    | `None`    |
| `object`       | `dict`    |
| `Object`       | `dict`    |

---

## Generics and Collections
| TypeScript         | Python           |
|-------------------|------------------|
| `Array<T>`        | `List[T]`        |
| `T[]`             | `List[T]`        |
| `Map<K, V>`       | `Dict[K, V]`     |
| `Record<K, V>`    | `Dict[K, V]`     |
| `Set<T>`          | `Set[T]`         |
| `Promise<T>`      | `Awaitable[T]`   |

---

## Utility Types
| TypeScript         | Python Equivalent         | Notes                       |
|-------------------|-------------------------|-----------------------------|
| `Partial<T>`      | `Optional[T]`           | Best-effort                 |
| `Required<T>`     | `T`                     | No-op                       |
| `Readonly<T>`     | `T`                     | No-op                       |
| `Pick<T, K>`      | `T`                     | No direct mapping           |
| `Omit<T, K>`      | `T`                     | No direct mapping           |

---

## Advanced Types
- **Union Types (`A | B`)**: Converted to `Union[A, B]`. If one type is `None`, uses `Optional[A]`.
- **Intersection Types (`A & B`)**: Converted to `Union[A, B]  # Intersection type, best-effort`.
- **Mapped Types (`{ [K in keyof T]: T[K] }`)**: Converted to `Dict[str, T[K]]  # Mapped type, best-effort`.
- **Conditional Types (`T extends U ? X : Y`)**: Converted to `Any  # Conditional type, not directly supported`.
- **Literal Types (`'foo' | 'bar'`)**: Converted to `Literal['foo', 'bar']` (requires `typing_extensions` for Python < 3.8).
- **TypeScript Object/Interface**: Converted to a Python `TypedDict` (heuristic, placeholder if not fully parsed).

---

## Examples
- `string | null` → `Optional[str]`
- `Array<string | number>` → `List[Union[str, float]]`
- `{ [K in keyof T]: T[K] }` → `Dict[str, T[K]]  # Mapped type, best-effort`
- `Partial<User>` → `Optional[User]`
- `'foo' | 'bar' | 'baz'` → `Literal['foo', 'bar', 'baz']`

---

## Configuration Options
The `TypeConverter` and `TypeScriptToPythonConverter` accept options via a config dictionary:
- `strict_mode` (bool): Raise on unsupported types if True, fallback to `Any` if False.
- `fallback_to_any` (bool): Use `Any` for unknown types if True.
- `log_level` (str): Logging level for conversion operations.

---

## Known Limitations & Edge Cases
- Mapped and conditional types are best-effort and may not always map directly.
- Complex nested generics and recursive types may require manual review.
- TypedDict generation is heuristic and may not capture all interface semantics.
- Some TypeScript utility types (e.g., Pick, Omit) are mapped as pass-throughs.
- TypeScript enums, namespaces, and advanced decorators are not handled by the type converter.

---

## Usage Notes
- All type conversion is routed through the `TypeConverter` class in `ts2py.py`.
- Imports for `typing` and `typing_extensions` are managed automatically.
- Logging is available for all type conversion operations.
- The converter is extensible: add new mappings or override methods for custom logic.

---

## Contributing & Extending
- To add support for new TypeScript constructs, extend the `TypeConverter` class.
- Add new mappings to the `TYPE_MAPPING` dictionary or utility type handlers.
- Update this reference and add tests for new features.

---

## See Also
- `scripts/type_converter.py` (core logic)
- `scripts/ts2py.py` (integration and CLI)
- `scripts/test_python_conversion.py` (unit tests) 