# Database Model Type System & Mapping Guide

## Purpose
This document defines the standard type system and mapping for all database models in the codebase. It ensures consistency, type safety, and maintainability across all model definitions.

---

## 1. Type Mapping Table

| Data Category      | Python Type         | SQLAlchemy Type         | DB Column Type         | Example Usage                |
|-------------------|--------------------|------------------------|------------------------|------------------------------|
| Integer           | `int`              | `Integer`              | `INTEGER`              | `age: Mapped[int] = mapped_column(Integer)` |
| String            | `str`              | `String(length)`       | `VARCHAR(length)`      | `name: Mapped[str] = mapped_column(String(100))` |
| Boolean           | `bool`             | `Boolean`              | `BOOLEAN`              | `is_active: Mapped[bool] = mapped_column(Boolean)` |
| Float             | `float`            | `Float`                | `FLOAT`                | `weight: Mapped[float] = mapped_column(Float)` |
| DateTime          | `datetime`         | `DateTime`             | `TIMESTAMP`            | `created_at: Mapped[datetime] = mapped_column(DateTime)` |
| JSON/Dict         | `dict`/`list`      | `JSON`                 | `JSONB`/`TEXT`         | `properties: Mapped[dict] = mapped_column(JSON, default=dict)` |
| Enum              | `Enum`             | `Enum(EnumClass)`      | `VARCHAR`/`ENUM`       | `status: Mapped[Status] = mapped_column(Enum(Status))` |
| UUID              | `UUID`/`str`       | `UUID(as_uuid=True)`   | `UUID`                 | `id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)` |
| Foreign Key       | `int`/`str`/`UUID` | `ForeignKey`           | `INTEGER`/`UUID`       | `user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))` |

---

## 2. Guidelines

### a. Type Annotations
- All model fields must use explicit Python type annotations with `Mapped[]` and `mapped_column`.
- Example:
  ```python
  name: Mapped[str] = mapped_column(String(100), nullable=False)
  ```

### b. Enum Fields
- Use Python `Enum` classes for all enumerated types.
- Use SQLAlchemy `Enum(EnumClass)` for DB columns.
- Example:
  ```python
  class Status(Enum):
      ACTIVE = "active"
      INACTIVE = "inactive"
  status: Mapped[Status] = mapped_column(Enum(Status), default=Status.ACTIVE)
  ```

### c. JSON Fields
- Use `dict` or `list` as the Python type.
- Always set a default factory (`default=dict` or `default=list`).
- Example:
  ```python
  properties: Mapped[dict] = mapped_column(JSON, default=dict)
  ```

### d. Relationships
- Use SQLAlchemy `relationship()` for all relationships.
- Use explicit type annotations for relationship fields (e.g., `Mapped[List[ChildModel]]`).
- Use string references only if necessary to avoid circular imports.
- Example:
  ```python
  children: Mapped[List['ChildModel']] = relationship('ChildModel', back_populates='parent')
  ```

### e. Foreign Keys
- Use explicit type and `ForeignKey` constraint.
- Example:
  ```python
  user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
  ```

### f. Naming Conventions
- Use `snake_case` for all field and table names.
- Use consistent suffixes for foreign keys (e.g., `user_id`, `owner_id`).
- Use plural table names for collections (e.g., `users`, `items`).
- Use singular for single-entity tables (e.g., `user`, `item`).

### g. Docstrings
- Every model and field must have a docstring describing its purpose and expected type.
- Example:
  ```python
  class User(BaseModel):
      """User account model."""
      id: Mapped[int] = mapped_column(Integer, primary_key=True)  # Unique user ID
  ```

### h. Default Values
- Use explicit default values for all fields where appropriate.
- Use `default_factory` for mutable types (dict, list).

### i. Type Validation
- Implement runtime type validation for complex/custom types using SQLAlchemy events or Pydantic models as needed.

---

## 3. Example Model
```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Enum, JSON
from datetime import datetime
from enum import Enum as PyEnum

class Status(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class User(BaseModel):
    """User account model."""
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.ACTIVE)
    profile: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    posts: Mapped[List['Post']] = relationship('Post', back_populates='user')
```

---

## 4. Migration & Compatibility
- All type changes must be reflected in Alembic migration scripts.
- When changing types, provide data migration logic for existing data.
- Maintain backward compatibility where possible; document any breaking changes.

---

## 5. Reference
- Use this document as the canonical reference for all future model definitions and refactors.
- Update this guide as new types or patterns are introduced. 