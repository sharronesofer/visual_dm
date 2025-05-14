# Utils Directory

This directory contains utility functions and helpers, including:
- HTTP utilities
- Validation utilities
- Data manipulation utilities
- Cache utilities
- Logging utilities
- Error handling utilities
- WebSocket utilities

## Directory Structure

- `formatting/` - Data formatting and transformation utilities
- `validation/` - Input validation and error checking
- `api/` - API-related utilities and interceptors
- `storage/` - Local storage and caching utilities
- `testing/` - Test helpers and mock data generators

## Guidelines

1. Utility Functions:
   - Should be pure functions when possible
   - Must be thoroughly tested
   - Should handle edge cases gracefully
   - Must be properly typed with TypeScript
   - Should include comprehensive error handling

2. File Structure:
   ```
   utils/
   ├── formatting/
   │   ├── date.ts
   │   └── number.ts
   ├── validation/
   │   ├── input.ts
   │   └── schema.ts
   ├── api/
   │   ├── interceptors.ts
   │   └── errorHandling.ts
   ├── storage/
   │   ├── local.ts
   │   └── session.ts
   └── testing/
       ├── mocks.ts
       └── factories.ts
   ```

3. Best Practices:
   - Write modular, single-responsibility functions
   - Document parameters and return types
   - Include usage examples in comments
   - Export through index files
   - Use meaningful error messages

4. Testing:
   - Include unit tests for all utilities
   - Test edge cases and error conditions
   - Use meaningful test descriptions
   - Group related tests together 