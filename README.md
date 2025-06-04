# Dreamforge (Visual DM)

A comprehensive virtual Dungeon Master system using LLMs for narrative generation in RPG games.

## 📖 **Complete Project Information**

For a comprehensive overview of the entire project, see:
**[📋 DREAMFORGE COMPLETE PROJECT SUMMARY](DREAMFORGE_COMPLETE_PROJECT_SUMMARY.md)**

This document consolidates all project information including:
- Complete system architecture and 26 game systems
- Development progress (8/10 phases complete)
- Technical achievements and innovations
- Migration history and current status

## Overview

Dreamforge is a complete system for managing tabletop RPG campaigns using AI to generate narratives, NPCs, locations, quests, and encounters. It combines procedural generation with large language models to create a dynamic and responsive game world.

**Current Status: 80% Complete (8/10 Development Phases)**

## Key Features

### Narrative Generation
- Dynamic quests and storylines powered by AI
- Character-driven narratives that adapt to player choices
- Real-time story progression with meaningful consequences

### World Building
- Procedural world generation with 26 interconnected systems
- Detailed location descriptions and coherent world lore
- Living world simulation that evolves based on player actions

### Character System
- AI-driven NPC generation with personalities and motivations
- Complex relationship networks between characters
- Persistent memory system for continuous interactions

### Revolutionary Equipment System
- **Learn-by-Disenchanting**: Players sacrifice magical items to learn enchantments
- **Quality-Based Durability**: Basic/Military/Noble tiers with time-based degradation
- **Utilization-Based Wear**: Equipment degrades through use, requiring maintenance
- **Semantic Set Detection**: AI-driven thematic grouping for equipment bonuses
- **Economic Balance**: Sophisticated cost structures prevent exploitation

### Advanced AI Integration
- **Centralized Prompt Library**: Organized template management system
- **Context-Aware Generation**: AI maintains continuity across all game systems  
- **Performance Optimizations**: Intelligent caching and token management
- **Multi-Model Support**: Flexible LLM provider integration

## Architecture

The system uses a clean modular architecture with strict separation of concerns:

### **Backend (Python/FastAPI)**
- **26 Business Logic Systems**: Character, Equipment, Economy, Combat, etc.
- **Technical Infrastructure**: Database, API, WebSocket, AI integration
- **364 API Endpoints**: Comprehensive REST API with real-time updates
- **Comprehensive Testing**: 276+ tests with 97.5% success rate

### **Frontend (Unity/C#)**
- **Interactive Game Interface**: Real-time visualization and control
- **WebSocket Communication**: Live updates and state synchronization
- **Modular UI Components**: Extensible interface architecture
- **Performance Optimized**: 60fps operation with efficient networking

## Documentation

### **Core Documentation**
- **[Development Bible](docs/Development_Bible.md)**: Complete technical documentation (122KB)
- **[Complete Project Summary](DREAMFORGE_COMPLETE_PROJECT_SUMMARY.md)**: Consolidated overview
- **[API Documentation](docs/api_contracts.md)**: Complete API specifications

### **Archived Documentation**
- **[Historical Documentation](archives/)**: Migration reports, system summaries, phase completion reports
- All completed migrations and refactoring documentation preserved in organized archives

### **System Documentation**
- Backend systems: [backend/docs/](backend/docs/)
- Unity client: [VDM/docs/](VDM/docs/)
- Configuration data: [data/systems/](data/systems/)

## Development

### Requirements
- Python 3.9+
- Unity 2022.3.5f1+
- OpenAI API or other LLM provider access

### Quick Start
1. Clone the repository
2. Set up Python environment: `pip install -r requirements.txt`
3. Configure API credentials in environment variables
4. Start backend server: `python -m backend.main`
5. Open Unity project and connect to backend

### Current Development Status
- ✅ **Phases 1-8 Complete**: Core systems, integration, testing
- ⏳ **Phase 9 Pending**: Code refactoring and optimization  
- ⏳ **Phase 10 Pending**: Sprite placeholder system

## Project Achievements

- **26 Core Game Systems** fully implemented and integrated
- **Revolutionary Equipment Mechanics** with industry-first features
- **AI-Powered Storytelling** with sophisticated narrative generation
- **Clean Architecture** with proper separation of concerns
- **Comprehensive Testing** ensuring reliability and quality
- **80% Development Complete** with clear path to completion

## License

[License information would go here] 