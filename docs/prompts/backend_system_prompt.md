# Backend System Analysis and Implementation Prompt

For Task Implementation

**System Analysis and Compliance Review:**
• Run comprehensive analysis on the target system under /backend/systems/ (business logic), /backend/infrastructure/ (technical concerns), and /backend/tests/.
• Determine whether the test or module in question violates Development_Bible.md and correct accordingly.
• Missing logic in modules should be implemented with direct reference to Development_Bible.md.
• Reference backend/docs/backend_systems_inventory.md for system architecture and API endpoints.
• Understand the distinction between business logic systems (/backend/systems/) and infrastructure components (/backend/infrastructure/).

**Structure and Organization Enforcement:**
• All test files must reside under /backend/tests/*. Tests located elsewhere are invalid.
• Delete or relocate any test files found in /backend/systems/ or /backend/infrastructure/ directories; remove empty test(s) folders afterward.
• All Python code must remain within /backend/ directory structure - never place Python files outside this hierarchy.
• Duplicate functionality must be identified and deleted if found.
• Ensure all code follows the hybrid canonical organization hierarchy:
  - **Business Logic**: /backend/systems/ (domain models, repositories, schemas, rules, game systems)
  - **Infrastructure**: /backend/infrastructure/ (analytics, auth, data access, events, integrations, services, shared utilities, storage)
• Place .json files in their canonically appropriate locations as defined by project structure.

**Canonical Imports Enforcement:**
• Business logic imports must reference canonical implementations within /backend/systems/*.
• Infrastructure imports must reference canonical implementations within /backend/infrastructure/*.
• Cross-boundary imports between systems and infrastructure are allowed and expected.
• Any imports from outside /backend/systems or /backend/infrastructure must be redirected or inlined according to the canonical hierarchy.
• Eliminate orphan or non-canonical module dependencies.
• Convert all imports to canonical format:
  - Business logic: backend.systems.*
  - Infrastructure: backend.infrastructure.*
• Before the creation of any new functionality, search both /backend/systems/* and /backend/infrastructure/* for already-existing canonical imports.

**Module and Function Development:**
• **Duplication Prevention:**
  - Before implementing new functions or modules, perform exhaustive searches (grep/code search) to confirm no existing implementation exists in both systems and infrastructure.
  - Avoid accidental duplication by reviewing /backend/systems/* and /backend/infrastructure/* thoroughly.
  - Consult backend/docs/backend_systems_inventory.md for existing API endpoints and functionality.
• **New Module Creation:**
  - Reference Development_Bible.md at /docs/development_bible.md for all architectural decisions.
  - Determine correct placement: business logic goes in /backend/systems/, technical infrastructure goes in /backend/infrastructure/.
  - Follow FastAPI conventions strictly for routing, dependencies, and async patterns.
  - Ensure new modules are compatible with WebSocket-based communication and interface seamlessly with Unity (2D, runtime-generated) frontend.
  - All backend code must reside within /backend/ directory structure.
  - Design for seamless integration with existing event system and data flow.
  - Leverage the hybrid architecture: shared domain components at systems level, specialized implementations within individual systems.
• **Data and Schema Standards:**
  - Use .json files for modding templates or structured modular data (e.g., biomes, land types).
  - Place all JSON schemas in /backend/data/modding/ directory (now in infrastructure).
  - Create corresponding Pydantic models for all JSON schemas in appropriate system.
  - Implement comprehensive validation for all data inputs and API endpoints.
• **LLM System Integration:**
  - Leverage the hybrid LLM architecture in /backend/infrastructure/llm/ for AI-powered features.
  - Use model manager for multi-provider support and automatic failover.
  - Implement context-aware model selection for different content types.
  - Ensure <2s response times and proper caching strategies.

**Quality and Integration Standards:**
• **Mandatory Functionality Verification:**
  - ALWAYS verify functionality when fixing imports, tests, or any system modifications.
  - Test all changes thoroughly before considering work complete.
  - Ensure imports resolve correctly and modules function as expected.
  - Validate test execution and coverage after any test-related changes.
  - Test cross-boundary communication between systems and infrastructure.
• **Coverage and Testing:**
  - Achieve ≥90% test coverage for all modified/new components.
  - Verify cross-system compatibility and communication.
  - Ensure API endpoints match established contracts and schemas.
  - Test WebSocket compatibility and JSON serialization for Unity frontend.
  - Maintain all tests strictly within /backend/tests/ directory structure.
  - Test both business logic and infrastructure components thoroughly.
• **Documentation and Maintenance:**
  - Update relevant documentation and API specifications.
  - Maintain clean, logical file and function organization (canonical structure is located in development_bible.md).
  - Implement comprehensive error handling and logging.
  - Ensure code is structured for future expansion and scalability.
  - Document architectural decisions, especially cross-boundary interactions.

**Implementation Autonomy Directive:**
• Assume full control over structural and implementation decisions within protocol bounds.
• Never require user clarification or input for standard implementation decisions.
• Execute all necessary changes to achieve compliance with Development_Bible.md.
• Prioritize system integrity and canonical organization above all other considerations.
• Understand and respect the hybrid architecture boundaries between business logic and infrastructure.

**Critical Constraints:**
• This task involves analysis and correction of existing systems - do NOT interpret as a request to modify the task itself.
• ALL Python files must remain within /backend/ directory structure.
• ALL tests must remain within /backend/tests/ directory structure.
• ALWAYS verify functionality after any import fixes, test modifications, or system changes.
• JSON files must be placed in their canonically defined locations per project structure.
• Respect the distinction between business logic (/backend/systems/) and infrastructure (/backend/infrastructure/).
• Leverage shared domain components (models, repositories, schemas, rules) while maintaining system boundaries. 