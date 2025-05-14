# OpenAPI/Swagger Documentation Maintenance

This document describes the process for maintaining and updating the OpenAPI/Swagger documentation for the Visual DM API.

## Location of OpenAPI Spec
- The OpenAPI configuration is located in [`swagger.config.js`](../swagger.config.js).
- The documentation is served via the Express API server at:
  - Swagger UI: `http://localhost:3001/api/docs/`
  - Raw OpenAPI JSON: `http://localhost:3001/api/openapi.json`

## Updating Endpoints
- Add or update endpoint definitions in `swagger.config.js` under the `paths` section.
- For each endpoint, specify:
  - Path and HTTP method
  - Summary and description
  - Tags (for grouping)
  - Parameters (path, query, header, etc.)
  - Request body schema (if applicable)
  - Response schemas for all status codes
  - Security requirements (e.g., JWT, API key)

## Updating Schemas
- Define or update schemas in the `components.schemas` section of `swagger.config.js`.
- Use TypeScript interfaces from `src/models/` and `src/types/` as the source of truth.
- Add field descriptions, types, constraints, and example values.

## Adding Example Payloads
- For each endpoint, add realistic example requests and responses in the `examples` field.
- Include both success and error scenarios.

## Authentication & Security
- Document all authentication methods in `components.securitySchemes`.
- Specify security requirements per endpoint in the `security` field.

## Validation
- Validate the OpenAPI spec using online tools (e.g., https://editor.swagger.io/) or CLI tools (e.g., `swagger-cli validate swagger.config.js`).
- Ensure there are no syntax errors or missing required fields.

## Serving Documentation Locally
- Start the API server: `node src/api/server.js`
- Access Swagger UI at [http://localhost:3001/api/docs/](http://localhost:3001/api/docs/)
- Access the raw OpenAPI JSON at [http://localhost:3001/api/openapi.json](http://localhost:3001/api/openapi.json)

## Keeping Docs in Sync
- Update the OpenAPI spec whenever API endpoints, request/response models, or authentication methods change.
- Review and update example payloads as the API evolves.
- Encourage developers to reference the Swagger UI for the latest API details.

## Versioning
- Update the `info.version` field in `swagger.config.js` when making breaking changes to the API.
- Consider maintaining versioned documentation if supporting multiple API versions.

---

For questions or suggestions, contact the API maintainers or open an issue in the repository. 