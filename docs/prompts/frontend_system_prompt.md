# Frontend System Analysis and Implementation Prompt

For Task Implementation

**Frontend System Analysis and Compliance Review:**
• Run comprehensive analysis on the target Unity frontend under /VDM/Assets/Scripts/Runtime/ and /VDM/Assets/Tests/.
• Determine whether the UI component or frontend module in question violates Development_Bible.md and correct accordingly.
• Missing frontend logic in modules should be implemented with direct reference to Development_Bible.md.
• Reference backend/docs/backend_systems_inventory.md for understanding backend API contracts and data flow.
• Mirror the hybrid backend architecture within Unity frontend structure, distinguishing between:
  - **Business Logic Systems**: Game domain components (character, quest, faction, etc.)
  - **Infrastructure Services**: Technical concerns (auth, data, events, integrations, etc.)

**Structure and Organization Enforcement:**
• All test files must reside under /VDM/Assets/Tests/*. Tests located elsewhere are invalid.
• Delete or relocate any test files found in /VDM/Assets/Scripts/Runtime/ directories; remove empty test folders afterward.
• All Unity C# code must remain within /VDM/ directory structure - never place Unity scripts outside this hierarchy.
• Duplicate UI components or frontend functionality must be identified and deleted if found.
• Ensure all Unity scripts follow canonical /VDM/Assets/Scripts/Runtime/ organization hierarchy reflecting the hybrid backend structure:
  - **Systems/**: Business logic UI components mirroring /backend/systems/
  - **Infrastructure/**: Technical UI components mirroring /backend/infrastructure/
  - **Core/**: Unity-specific foundational components
• Place Unity assets (.prefabs, .unity scenes, .scriptableobjects) in their canonically appropriate locations within /VDM/Assets/.

**Canonical Frontend Imports Enforcement:**
• All Unity script references must use canonical implementations within /VDM/Assets/Scripts/Runtime/.
• Business logic UI imports should mirror /backend/systems/ structure.
• Infrastructure UI imports should mirror /backend/infrastructure/ structure.
• Any imports from outside the canonical Unity structure must be redirected or consolidated according to the frontend hierarchy.
• Eliminate orphan or non-canonical Unity component dependencies.
• Convert all Unity namespace references to canonical format:
  - Business Systems: VDM.Systems.*
  - Infrastructure: VDM.Infrastructure.*
  - Core Unity: VDM.Core.*
• Before creating any new UI components or frontend functionality, search /VDM/Assets/Scripts/Runtime/* for already-existing canonical implementations.

**Frontend Module and Component Development:**
• **Duplication Prevention:**
  - Before implementing new UI components or frontend modules, perform exhaustive searches (grep/code search) to confirm no existing implementation exists.
  - Avoid accidental duplication by reviewing /VDM/Assets/Scripts/Runtime/* thoroughly.
  - Check existing prefabs and ScriptableObjects to prevent duplicate UI components.
  - Consider both business logic and infrastructure UI components.
• **New Frontend Module Creation:**
  - Reference Development_Bible.md at /docs/development_bible.md for all architectural decisions.
  - Determine correct placement based on backend hybrid architecture:
    - Game domain UI → /VDM/Assets/Scripts/Runtime/Systems/
    - Technical infrastructure UI → /VDM/Assets/Scripts/Runtime/Infrastructure/
    - Unity core functionality → /VDM/Assets/Scripts/Runtime/Core/
  - Follow Unity best practices strictly for MonoBehaviour patterns, UI components, and async operations.
  - Ensure new Unity components are compatible with WebSocket-based backend communication.
  - All Unity frontend code must reside within /VDM/ directory structure.
  - Design for seamless integration with existing Unity event system and backend data flow.
  - Maintain clean separation between Unity UI code and backend business logic.
  - Leverage the hybrid architecture for efficient UI organization.
• **UI and Asset Standards:**
  - Use Unity's UI system (Canvas, UI elements) for all interface components.
  - Place placeholder sprites and assets in /VDM/Assets/Placeholders/ using Git LFS for appropriate file types.
  - Create corresponding Unity ScriptableObjects for frontend data configurations.
  - Implement comprehensive validation for all UI inputs and frontend data handling.
  - Support LLM-generated content display with proper async loading and caching.

**Quality and Integration Standards:**
• **Mandatory Functionality Verification:**
  - ALWAYS verify Unity compilation and runtime functionality when fixing imports, components, or any frontend modifications.
  - Test all Unity scenes and prefabs thoroughly before considering work complete.
  - Ensure Unity script references resolve correctly and components function as expected in-editor and at runtime.
  - Validate Unity test execution and coverage after any test-related changes.
  - Test WebSocket communication with backend and JSON serialization compatibility.
  - Test integration with both business logic APIs and infrastructure services.
• **Coverage and Testing:**
  - Achieve ≥90% test coverage for all modified/new Unity components.
  - Verify frontend-backend communication and data synchronization.
  - Ensure UI components respond correctly to backend API calls and WebSocket events.
  - Test Unity scene loading, UI navigation, and component lifecycle management.
  - Maintain all Unity tests strictly within /VDM/Assets/Tests/ directory structure.
  - Test both business logic UI and infrastructure UI components.
• **Documentation and Maintenance:**
  - Update relevant Unity documentation and component specifications.
  - Maintain clean, logical Unity asset and script organization (canonical structure mirrors hybrid backend architecture).
  - Implement comprehensive error handling and logging for Unity components.
  - Ensure Unity code is structured for future expansion and scalability.
  - Document UI component interactions with backend systems and infrastructure.

**Unity-Specific Requirements:**
• **Scene and Asset Management:**
  - Bootstrap scene at /VDM/Assets/Scenes/Bootstrap.unity with GameLoader.cs entry point.
  - Organize scenes, prefabs, and assets according to hybrid system boundaries defined in Development_Bible.md.
  - Maintain proper Unity asset references and avoid broken links.
  - Structure assets to reflect business logic vs infrastructure separation.
• **Frontend Architecture:**
  - Create modular UI component system with responsive layout management.
  - Implement Unity-specific directories: Bootstrap/, Core/, Systems/, Infrastructure/.
  - Build navigation framework with Unity screen/panel management.
  - Establish standard Unity subdirectory structure within each major area: Models/, Services/, UI/, Integration/.
  - Support real-time LLM content generation with proper loading states and error handling.
• **Backend Integration:**
  - Interface cleanly with both /backend/systems/ (business logic) and /backend/infrastructure/ (technical services).
  - Implement efficient WebSocket handling for real-time features.
  - Support hybrid LLM system integration for dynamic content display.
  - Maintain separation of concerns between game UI and infrastructure UI.

**Implementation Autonomy Directive:**
• Assume full control over Unity frontend structural and implementation decisions within protocol bounds.
• Never require user clarification or input for standard Unity implementation decisions.
• Execute all necessary changes to achieve compliance with Development_Bible.md within Unity frontend.
• Prioritize Unity system integrity and canonical organization above all other considerations.
• Focus exclusively on Unity frontend - backend is complete and should not be modified.
• Understand and respect the hybrid backend architecture when designing frontend structure.

**Critical Constraints:**
• This task involves analysis and correction of existing Unity frontend systems - do NOT interpret as a request to modify the task itself.
• ALL Unity C# scripts must remain within /VDM/ directory structure.
• ALL Unity tests must remain within /VDM/Assets/Tests/ directory structure.
• ALWAYS verify Unity compilation and runtime functionality after any import fixes, component modifications, or system changes.
• Unity assets must be placed in their canonically defined locations per Unity project structure.
• Maintain clean separation between Unity UI code and backend business logic - never modify backend systems.
• Respect the hybrid backend architecture when organizing frontend components and communication patterns. 