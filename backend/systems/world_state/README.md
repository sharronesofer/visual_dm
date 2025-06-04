# World State System

The World State System is the central nervous system for tracking and managing the dynamic state of the game world. It serves as the authoritative source for all world information including regions, factions, NPCs, events, and ongoing effects.

## Core Features

### 🌍 World State Management
- **Centralized State**: Single source of truth for all world information
- **Real-time Updates**: Dynamic state changes propagated throughout the system
- **Event-driven Architecture**: State changes trigger appropriate events
- **Persistence**: Automatic saving and loading with backup support

### 📰 Regional Newspaper System
- **Printing Press Requirements**: Settlements automatically generate printing presses based on population
  - Large cities (1000+ pop): Broadsheet newspapers with wide circulation
  - Towns (300+ pop): Local heralds with regional focus  
  - Villages (100+ pop): Town criers with basic announcements
- **Regional Content**: News filtered and prioritized by regional relevance
- **Content Sections**:
  - Headline news for major events
  - Regional news and developments
  - Trade reports and economic updates
  - Rumors and gossip for flavor
  - Editorial content and opinions
  - Weather reports and seasonal outlook
  - Public announcements and notices
- **Quality Effects**: Printing press condition affects article readability
- **Archives**: Historical newspaper editions stored for reference

### 🚀 Modern Performance Features
- **Compression Support**: Automatic state compression for large worlds
- **Intelligent Caching**: Frequently accessed data cached with TTL
- **Batch Operations**: Efficient bulk event processing
- **Storage Management**: Automatic cleanup of old backups
- **Storage Statistics**: Monitoring of disk usage

### 🔧 Enhanced World Generation
- **Optimized Algorithms**: Efficient world content generation
- **Scalable Complexity**: Simple, medium, and complex world generation modes
- **Regional Generation**: Batch region creation with relationships
- **Faction Networks**: Intelligent faction relationship modeling
- **Settlement Growth**: Dynamic POI evolution and metropolitan expansion

## System Architecture

```
World State System/
├── core/
│   ├── loader.py          # Enhanced state persistence with compression
│   └── types.py           # Core data structures and enums
├── services/
│   └── world_state_service.py  # Business logic and CRUD operations
├── events/
│   └── handlers.py        # Event processing and state updates
├── utils/
│   ├── newspaper_system.py     # Regional newspaper generation
│   ├── world_event_utils.py    # Event creation and filtering
│   ├── world_utils.py          # World management utilities
│   └── optimized_worldgen.py   # Efficient world generation
└── manager.py             # Main coordination and API
```

## Quick Start

### Basic Usage

```python
from backend.systems.world_state import (
    WorldStateManager, 
    regional_newspaper_system,
    world_generator
)

# Initialize the world state system
manager = WorldStateManager()

# Load current world state
world_state = manager.get_state()

# Generate newspaper for a region
newspaper_system = regional_newspaper_system
newspaper_system.discover_printing_presses()
edition = newspaper_system.publish_regional_edition("region_1")

# Generate new world content
generator = world_generator
new_world = generator.generate_world_state(
    region_count=5, 
    faction_count=3,
    complexity_level="medium"
)
```

### Event Management

```python
from backend.systems.world_state.utils.world_event_utils import (
    create_world_event,
    filter_events_by_visibility
)

# Create a world event
event = create_world_event(
    event_type="faction_change",
    description="The Iron Brotherhood has gained influence in the region",
    region="northern_kingdoms",
    severity=6
)

# Filter events for player visibility
visible_events = filter_events_by_visibility(
    events=[event],
    player_region="northern_kingdoms",
    player_knowledge_level=5
)
```

### Newspaper System

```python
from backend.systems.world_state.utils.newspaper_system import (
    RegionalNewspaperSystem,
    NewspaperType
)

# Initialize newspaper system
newspaper_system = RegionalNewspaperSystem()

# Discover printing presses in settlements
presses = newspaper_system.discover_printing_presses()

# Publish regional edition
edition = newspaper_system.publish_regional_edition("region_1")

# Get recent editions
recent_news = newspaper_system.get_recent_editions("settlement_1", count=3)

# Check printing press status
press_status = newspaper_system.get_printing_press_status("settlement_1")
```

## Regional Newspaper Features

### Printing Press Generation
The system automatically creates printing presses based on settlement characteristics:

- **Population Thresholds**: Minimum 100 population required
- **Press Sizes**: Large (cities), Medium (towns), Small (villages)
- **Operating Costs**: Scaled by press size and complexity
- **Maintenance**: Presses degrade over time and need upkeep
- **Quality Effects**: Poor maintenance affects article readability

### Content Generation
Each newspaper edition includes:

1. **Headline News**: Major regional events (severity 7+)
2. **Regional News**: Medium importance local stories
3. **Trade Reports**: Economic activity and market conditions
4. **Rumors**: Procedurally generated gossip and speculation
5. **Editorial**: Opinion pieces on regional topics
6. **Weather**: Current conditions and seasonal outlook
7. **Announcements**: Public notices and local information

### Regional Filtering
News content is filtered based on:
- Geographic relevance to the region
- Event severity and importance
- Player knowledge and information networks
- Settlement size and communication capabilities

## Performance Features

### State Compression
- Automatic compression for large world states
- Transparent loading of compressed/uncompressed files
- Fallback to uncompressed format if compression fails

### Intelligent Caching
- 5-minute TTL for world state cache
- Automatic cache invalidation on state changes
- Memory-efficient caching with configurable size limits

### Batch Operations
- Efficient bulk event loading and saving
- Enhanced filtering with datetime and type support
- Performance optimized for large event datasets

### Storage Management
- Automatic backup cleanup (configurable retention period)
- Storage usage statistics and monitoring
- Disk space optimization through compression

## API Reference

### WorldStateManager
Main interface for world state operations:
- `get_state()`: Load current world state
- `update_state(changes)`: Apply state changes
- `save_state()`: Persist state to disk
- `get_storage_stats()`: Get storage usage information

### RegionalNewspaperSystem
Regional newspaper generation and management:
- `discover_printing_presses()`: Find settlement printing presses
- `publish_regional_edition(region_id)`: Generate newspaper edition
- `get_recent_editions(settlement_id)`: Get historical newspapers
- `get_printing_press_status(settlement_id)`: Check press condition

### World Event Utils
Event creation and management:
- `create_world_event()`: Standardized event creation
- `filter_events_by_visibility()`: Player-appropriate event filtering
- `format_event_for_newspaper()`: Convert events to articles
- `aggregate_similar_events()`: Combine related events

## Integration Points

### Database Integration
- Seamless integration with the main database system
- Automatic relationship management with POI and faction systems
- Efficient querying for regional content generation

### Event System
- Publishes state change events for system integration
- Subscribes to relevant world events for automatic updates
- Supports custom event handlers for specialized processing

### Region & POI Systems
- Direct integration with settlement and POI data
- Automatic printing press discovery based on POI characteristics
- Regional content generation using POI and settlement information

## Configuration

Environment variables for customization:
- `WORLD_STATE_COMPRESSION=true`: Enable state compression
- `WORLD_STATE_CACHE_TTL=300`: Cache TTL in seconds
- `WORLD_STATE_BACKUP_RETENTION=30`: Backup retention in days
- `NEWSPAPER_GENERATION=true`: Enable newspaper system

## Recent Improvements

### ✅ Legacy Cleanup
- Removed deprecated mod system components
- Modernized loader architecture with Path objects
- Enhanced error handling and recovery
- Improved code organization and documentation

### ✅ Newspaper System Enhancements
- Added printing press requirements based on settlement size
- Implemented regional news filtering and aggregation
- Created rumor generation system for flavor content
- Added editorial and announcement sections
- Integrated with world event system

### ✅ Performance Optimizations
- Added state compression support
- Implemented intelligent caching system
- Enhanced batch operations for better throughput
- Added storage management and cleanup tools
- Improved error handling and recovery mechanisms

The World State System now provides a robust, performant, and feature-rich foundation for dynamic world simulation with engaging regional content generation.
