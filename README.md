# Visual DM

A comprehensive virtual Dungeon Master system using LLMs for narrative generation in RPG games.

## Overview

Visual DM is a complete system for managing tabletop RPG campaigns using AI to generate narratives, NPCs, locations, quests, and encounters. It combines procedural generation with large language models to create a dynamic and responsive game world.

## Key Features

### Narrative Generation
- Dynamic quests and storylines
- Character-driven narratives
- Adaptive story progression based on player choices

### World Building
- Procedural world generation
- Detailed location descriptions
- Connected world elements with coherent lore

### Character System
- NPC generation with personalities and motivations
- Relationship networks between characters
- Memory system for persistent interactions

### Combat System
- Strategic encounter generation
- Balanced challenge scaling
- Narrative-driven combat descriptions

### Prompt System
- **Centralized Prompt Library**: All prompt templates in a single, well-organized location
- **Flexible Templating**: Support for variables, conditionals, and includes 
- **Domain-Specific Templates**: Pre-built templates for NPCs, quests, locations, combat, and more
- **Context Aggregation**: Automatically gathers relevant context from game systems
- **Unity Integration**: Complete C# client for seamless integration with the game
- **Performance Optimizations**: Caching, token management, and batching for efficiency

## Architecture

The system consists of two main components:

1. **Backend (Python/FastAPI)**: 
   - LLM integration and prompt management
   - Game state persistence
   - Business logic for game systems
   - WebSocket and REST API endpoints

2. **Frontend (Unity/C#)**:
   - Interactive user interface
   - Real-time visualization
   - Game client logic
   - WebSocket communication with backend

## Documentation

- Backend API docs: [backend/docs/](backend/docs/)
- Prompt system: [backend/docs/prompt_library.md](backend/docs/prompt_library.md)
- Unity client: [VDM/docs/](VDM/docs/)

## Development

### Requirements
- Python 3.9+
- Unity 2022.3.5f1+
- Access to OpenAI API or other LLM provider

### Setup
1. Clone the repository
2. Set up Python environment and install dependencies
3. Configure LLM API credentials
4. Open the Unity project
5. Start the backend server and connect from Unity

## License

[License information would go here] 