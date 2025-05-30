# Documentation System

The Visual DM Documentation System provides comprehensive documentation, tutorials, context-sensitive help, and API reference documentation to users. This document describes the architecture, usage, and extension of the documentation system.

## Overview

The documentation system consists of several components:

1. **Backend Components**:
   - Documentation schema definitions (Pydantic models)
   - Documentation manager (core documentation functionality)
   - Documentation API endpoints (REST API)
   - Documentation WebSocket handlers (real-time communication)

2. **Frontend Components**:
   - Documentation Manager (Unity C# singleton)
   - Documentation UI (MVVC pattern UI components)
   - Context-sensitive help system

3. **Documentation Types**:
   - Documentation Topics: General help articles
   - Context-sensitive Help: UI element-specific help
   - Tutorials: Step-by-step guided instructions
   - API Documentation: Reference documentation for programmers

## Architecture

### Backend Architecture

The backend documentation system is built on FastAPI and uses Pydantic models for documentation structure. The main components are:

- `DocumentationManager`: Core class responsible for loading, storing, and querying documentation
- REST API endpoints for retrieving documentation
- WebSocket handlers for real-time communication
- JSON schemas for documentation structure

### Frontend Architecture

The Unity frontend uses an MVVC pattern for the documentation UI:

- `DocumentationManager`: Singleton class that communicates with the backend
- `DocumentationUIModel`: Holds the state of the documentation UI
- `DocumentationUIController`: Handles user interactions and updates the model
- `DocumentationUIView`: Renders the UI based on the model

## Documentation Types

### Documentation Topics

General-purpose documentation articles organized by topic. Each topic has:

- ID: Unique identifier
- Type: The document type ("topic")
- Title: Display title
- Content: Main text content (supports markdown)
- Tags: Categories or keywords for filtering
- Related Topic IDs: Links to related documentation
- Order: Optional sorting order

### Context-sensitive Help

Help information tied to specific UI elements or contexts. Each context help entry has:

- Context ID: Unique identifier for the UI element/context
- Title: Display title
- Content: Help text (supports markdown)
- Related Topic IDs: Links to related topics for further reading

### Tutorials

Step-by-step guides for learning specific features. Each tutorial has:

- ID: Unique identifier
- Title: Display title
- Description: Brief overview
- Steps: A list of tutorial steps, each with:
  - Title: Step title
  - Content: Step instructions (supports markdown)
  - Target UI Element ID: Optional ID for highlighting UI elements
  - Type: Step type (information, interaction, completion)

### API Documentation

Technical documentation for programmers. Each API doc has:

- ID: Unique identifier
- Title: Display title
- Description: Overview of the API
- Sections: Content sections, each with:
  - Title: Section title
  - Content: Markdown content
- Examples: Code examples, each with:
  - Title: Example title
  - Language: Programming language
  - Code: Example code snippet

## Usage

### Adding Documentation

To add new documentation, create a JSON file in the appropriate format and place it in the backend's modding directory. The system will automatically load this documentation.

Example documentation topic:

```json
{
  "id": "getting_started",
  "type": "topic",
  "title": "Getting Started with Visual DM",
  "content": "Welcome to Visual DM, a powerful tool for creating and managing your tabletop game maps and assets...",
  "tags": ["beginner", "overview"],
  "related_topic_ids": ["basic_navigation", "creating_maps"],
  "order": 1
}
```

### Accessing Documentation

In the Unity frontend, use the `DocumentationManager` to access documentation:

```csharp
// Get a specific topic
DocumentationManager.Instance.LoadTopic("getting_started");

// Show context-sensitive help
DocumentationManager.Instance.LoadContextHelp("map_toolbar");

// Start a tutorial
DocumentationManager.Instance.LoadTutorial("basic_map_tutorial");
```

### Adding Context-sensitive Help

To add context-sensitive help to a UI element:

1. Create a context help entry in the documentation system
2. Assign the context ID to the UI element
3. Add a help button or tooltip that triggers `ShowContextHelp(contextId)`

Example:

```csharp
public class MapToolbarButton : MonoBehaviour
{
    [SerializeField] private string _contextHelpId = "map_toolbar_layers";
    [SerializeField] private Button _helpButton;
    
    private void Start()
    {
        _helpButton.onClick.AddListener(() => {
            DocumentationManager.Instance.LoadContextHelp(_contextHelpId);
        });
    }
}
```

### Creating Tutorials

Tutorials are multi-step guides that can highlight UI elements and guide users through interactions. To create a tutorial:

1. Define the tutorial steps in JSON format
2. For interactive steps, specify the target UI element ID
3. Use the `DocumentationUIController.StartTutorial()` method to begin the tutorial

## Documentation Schema Structure

The documentation system uses a defined schema in `documentation_schema.json` that specifies the structure of all documentation types. See `backend/data/modding/documentation_schema.json` for the full schema definition.

## WebSocket Communication

For real-time documentation features, the system uses WebSocket communication between the backend and frontend. Messages follow this format:

```json
{
  "type": "search",
  "query": "terrain",
  "docType": "topic",
  "tags": ["maps", "terrain"],
  "maxResults": 10
}
```

Response:

```json
{
  "type": "search_results",
  "results": [
    {
      "id": "terrain_tools",
      "type": "topic",
      "title": "Using Terrain Tools",
      "content": "...",
      "tags": ["maps", "terrain", "tools"]
    }
  ]
}
```

## Extending the Documentation System

### Adding New Documentation Types

To add a new documentation type:

1. Add the type to `documentation_schema.json`
2. Create a Pydantic model in `documentation.py`
3. Update the `DocumentationManager` to handle the new type
4. Add UI components to display the new type

### Adding Search Providers

The documentation system supports extensible search providers:

1. Create a new search provider class that implements the search interface
2. Register the provider with the `DocumentationManager`
3. The search results will be merged with results from other providers

## Best Practices

1. **Structure**: Keep documentation well-structured and organized by topic
2. **Context-sensitive Help**: Keep context help concise and specific to the UI element
3. **Tutorials**: Break tutorials into small, manageable steps
4. **Content**: Use markdown formatting to improve readability
5. **Maintenance**: Regularly update documentation to reflect changes in the application

## Conclusion

The Documentation System provides a comprehensive solution for in-app help, tutorials, and technical documentation. By following the guidelines in this document, you can efficiently create and maintain documentation that enhances the user experience of Visual DM. 