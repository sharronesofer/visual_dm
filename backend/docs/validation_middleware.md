## Centralized Validation Middleware

All mutating API endpoints (POST, PUT, PATCH, DELETE) are now protected by a centralized validation middleware. This ensures consistent, secure, and extensible input validation across the backend.

### How It Works
- The middleware intercepts all mutating requests.
- It looks up a registry of validation schemas/functions for the endpoint (by method and path).
- If a schema is registered, it validates the request body (or runs custom logic).
- On validation failure, it logs the error and returns a standardized error response.
- On success, the request proceeds as normal.

### Registering Validation for an Endpoint

Use the `register_validation` decorator in your endpoint module:

```python
from backend.app.middleware.validation import register_validation
from .schemas import MyCreateSchema

register_validation('POST', '/api/v1/my-resource', schema=MyCreateSchema)(lambda x: x)
```

- The first argument is the HTTP method (POST, PUT, PATCH, DELETE).
- The second argument is the full path (as seen by FastAPI, e.g., `/api/v1/characters`).
- The `schema` argument is a Pydantic model for validation.
- Optionally, you can provide a `custom_validator` callable for advanced cases.

### Best Practices
- Register a validation schema for every mutating endpoint.
- Use Pydantic models for request bodies whenever possible.
- For complex or cross-field/game-state validation, use a custom validator function.
- All validation failures are logged and returned in a consistent error format.

See `backend/app/middleware/validation.py` for implementation details. 