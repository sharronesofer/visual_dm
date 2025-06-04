# Arc System - Business Logic

## Overview
The Arc System provides comprehensive narrative arc management for Visual DM, supporting both global campaign narratives and personal character development storylines. This is the business logic layer that works with technical infrastructure to deliver dynamic, player-driven narrative experiences.

## Updated Architecture - JSON Configuration System ✅

The Arc system now uses a **multi-tier JSON configuration structure** for maximum flexibility and security:

### Configuration Tiers

**Public Tier** (`/data/public/templates/`): Builder/modder accessible content
- `arc/arc_templates.json`: Arc generation templates and prompts
- `quest/quest_tag_mappings.json`: Quest generation mappings and templates

**System Tier** (`/data/system/config/arc/`): Internal system configuration  
- `arc_business_rules.json`: Validation rules, defaults, and business logic

This replaces the legacy `/rules/` directory with proper access control.

## Key Components

### 1. Arc Management ✅ FULLY IMPLEMENTED
**Purpose**: Core business logic for creating, tracking, and managing narrative arcs.

**Key Components**:
- `ArcManager`: Primary service for arc lifecycle management
- `ArcRepository`: Data persistence layer (moved to infrastructure)
- Business validation and rules enforcement

**Business Logic**: Arcs have types (global, regional, character, NPC, exploration, mystery), priorities, and complex dependency relationships. The system ensures narrative coherence while supporting flexible storytelling.

### 2. Arc Generation ✅ NOW USES JSON CONFIG
**Purpose**: AI-powered arc creation using configurable templates.

**Key Components**:
- `ArcGenerator`: AI-powered arc creation using configurable templates from `/data/public/templates/arc/arc_templates.json`
- Template-based prompt generation for different arc types
- Quality validation and retry logic

**Business Logic**: Different arc types use specialized templates (global=6 steps/high complexity, regional=4 steps/medium complexity, character=3 steps/low complexity). AI generation includes fallback mechanisms and quality thresholds.

### 3. Player Arc Management ✅ FULL DATABASE INTEGRATION
**Purpose**: Tracks individual player progression through arcs with persistent state.

**Key Components**:
- `PlayerArcManager`: Manages individual player arc relationships
- `ProgressionTracker`: Real-time progression monitoring and analytics
- Database-backed progression persistence

**Business Logic**: Each player can have multiple active arc progressions. The system tracks which steps are completed, choices made, and provides analytics on progression patterns.

### 4. Arc Step System ✅ COMPREHENSIVE IMPLEMENTATION  
**Purpose**: Manages the individual steps within arcs and their completion logic.

**Key Components**:
- `ArcStep` models with completion criteria and prerequisites
- Step validation and progression logic
- Choice tracking and branching narrative support

**Business Logic**: Each player can have multiple active arc progressions. The system tracks which steps are completed, choices made, and provides analytics on progression patterns.

### 5. Quest Integration ✅ NOW USES JSON CONFIG
**Purpose**: Bridges arcs with the quest system to generate complementary content.

**Key Components**:
- `QuestIntegrationService`: Generates quests based on arc content and tags from `/data/public/templates/quest/quest_tag_mappings.json`
- Protocol-based dependency injection prevents circular imports
- Tag mapping system for automatic quest generation

**Business Logic**: Arcs automatically generate supporting quests based on their content and tags. Quest templates and tag mappings are now externalized to JSON configuration files.

### 6. Configuration Management ✅ NEW MULTI-TIER SYSTEM
**Purpose**: Centralized management of arc system configuration through multi-tier JSON structure.

**Key Components**:
- `ConfigLoader`: Utility class for loading and caching JSON configurations with access control
- **Public configurations** in `/data/public/templates/`:
  - `arc/arc_templates.json`: Arc generation templates and prompts (builder-modifiable)
  - `quest/quest_tag_mappings.json`: Tag mappings and quest templates (builder-modifiable)
- **System configurations** in `/data/system/config/arc/`:
  - `arc_business_rules.json`: Validation rules, defaults, and business logic (system-internal)
- Automatic fallback to hardcoded values if configuration loading fails
- Multi-tier access control system

**Business Logic**: All hardcoded templates, mappings, and business rules are now externalized to JSON files with appropriate access levels. The system distinguishes between user-modifiable content (public tier) and system-critical settings (system tier).

## Integration Points

### Database Integration
- Uses repository pattern for data persistence
- Models use SQLAlchemy with UUID primary keys
- Supports both SQLite (development) and PostgreSQL (production)

### Quest System Integration  
- Bidirectional integration with quest system via protocol interfaces
- Automatic quest generation based on arc content
- Quest completion can trigger arc progression

### War System Integration
- Faction-based arcs can trigger during wars
- War events can influence ongoing arcs
- Arc outcomes can affect faction relationships

### API Integration
- RESTful endpoints for all arc operations
- WebSocket support for real-time progression updates
- Event-driven architecture for cross-system communication

## Configuration Files ✅ MULTI-TIER IMPLEMENTATION

### `/data/public/templates/arc/arc_templates.json` (Builder-Modifiable)
Contains templates for different arc types with enhanced metadata:
- **Global**: World-spanning narratives (6 steps, high complexity, 90 days duration)
- **Regional**: Location-specific storylines (4 steps, medium complexity, 45 days duration)  
- **Character**: Personal development arcs (3 steps, low complexity, 30 days duration)
- **NPC**: Supporting character storylines (3 steps, low complexity, 21 days duration)
- **Exploration**: Discovery and exploration narratives (4 steps, medium complexity, 35 days duration)
- **Mystery**: Investigation storylines (5 steps, medium complexity, 40 days duration)

### `/data/public/templates/quest/quest_tag_mappings.json` (Builder-Modifiable)
Contains quest generation settings with enhanced templates:
- **Tag Mappings**: Arc type to quest tag associations
- **Keyword Mappings**: Keywords to tag extraction rules
- **Quest Templates**: Standardized quest structures with duration and scaling
- **Difficulty Settings**: Quest difficulty calculation parameters

### `/data/system/config/arc/arc_business_rules.json` (System-Internal)
Contains core business logic and security settings:
- **Validation Rules**: Field requirements, status transitions, limits
- **Defaults**: Default values for arc creation
- **Step Validation**: Rules for step creation and validation
- **Progression Rules**: Player progression limitations and timeouts
- **Generation Settings**: AI generation parameters
- **Integration Rules**: Cross-system integration settings including chaos system
- **Security Settings**: Rate limiting, audit controls, system-only fields
- **Performance Settings**: Caching, batch processing, timeout configuration

## Maintenance Concerns - RESOLVED ✅

All critical maintenance issues have been addressed:

### ✅ Database Implementation Complete
- **Previous Issue**: PlayerArcManager had TODO comments for database operations
- **Resolution**: Implemented full database integration with ArcRepository, proper create/update operations, and comprehensive error handling

### ✅ Dynamic Data Handling
- **Previous Issue**: Hardcoded `total_steps = 5` placeholder in progression tracker
- **Resolution**: Dynamic step counting based on actual arc data, flexible progression calculation, and proper step validation

### ✅ Configuration Externalization  
- **Previous Issue**: Hardcoded templates, mappings, and business rules throughout the codebase
- **Resolution**: Created comprehensive multi-tier JSON configuration system with automatic loading, caching, hot-reloading capabilities, and access control

### ✅ Circular Import Prevention
- **Previous Issue**: Direct imports between arc and quest systems causing dependency issues
- **Resolution**: Implemented protocol-based dependency injection, clean service boundaries, and optional dependencies with graceful degradation

### ✅ Testing Infrastructure  
- **Previous Issue**: Complex business logic was difficult to test due to hardcoded dependencies
- **Resolution**: Externalized configuration enables easy test fixture creation, mock data setup, and isolated unit testing

## Business Rules and Validation

The system enforces several business rules through the configuration:

### Arc Type Rules
- Global arcs require high priority and multiple faction involvement
- Character arcs must have character_id
- Regional arcs must have region_id  
- Faction arcs must have at least one faction_id

### Status Progression Rules
- Completed arcs must have 100% completion
- Active arcs cannot have 100% completion  
- Status transitions follow defined state machine

### Performance and Security
- Rate limiting: 10 arc creations per hour, 30 progression updates per minute
- Concurrent limits: Max 3 active progressions per player
- Timeout handling: 90-day progression timeout, 30-second database timeout
- Audit controls: System-only fields and admin-only operations

## Testing and Validation

### Configuration Validation
```python
from backend.systems.arc.utils.config_loader import config_loader

# Validate all configurations
validation_results = config_loader.validate_config_files()
for config_name, is_valid in validation_results.items():
    print(f"{config_name}: {'✅ Valid' if is_valid else '❌ Invalid'}")
```

### Access Level Checking
```python
# Check access level of configuration
access_level = config_loader.get_access_level("arc_templates")
print(f"Arc templates access level: {access_level}")  # builder_modifiable
```

## Future Enhancements

1. **Hot Configuration Reloading**: Runtime updates without restart
2. **JSON Schema Validation**: Comprehensive validation schemas
3. **Configuration Versioning**: Track configuration changes over time
4. **Localization Support**: Multi-language template support
5. **Advanced Analytics**: Enhanced progression tracking and insights

This multi-tier architecture provides a robust foundation for narrative management while maintaining security, flexibility, and ease of use for both developers and content creators. 