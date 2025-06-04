# Motif System Documentation

## Overview

The Motif System is a comprehensive narrative framework designed to manage and generate contextual storytelling elements for AI-driven role-playing games. It provides structured motifs that represent thematic elements, emotional tones, and narrative directions to guide AI systems in creating coherent and engaging story experiences.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Layer    │────│ Service Layer   │────│Repository Layer│
│  (FastAPI)     │    │ (Business Logic)│    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Models &      │    │   Utilities     │    │  Configuration  │
│   Schemas       │    │   & Helpers     │    │     & Data      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

1. **Models & Schemas** (`backend/infrastructure/systems/motif/models.py`)
   - Core data models (Motif, MotifCreate, MotifUpdate, MotifFilter)
   - Enums (MotifCategory, MotifScope, MotifLifecycle)
   - Response schemas for API consistency

2. **Service Layer** (`backend/systems/motif/services/service.py`)
   - Business logic and orchestration
   - AI integration and narrative context generation
   - Evolution and lifecycle management
   - Conflict resolution and interaction analysis

3. **Repository Layer** (`backend/infrastructure/systems/motif/repositories.py`)
   - Database operations with SQLAlchemy async support
   - Filtering, pagination, and spatial queries
   - Error handling and transaction management

4. **API Layer** (`backend/infrastructure/systems/motif/routers/router.py`)
   - RESTful API endpoints with FastAPI
   - Authentication and input validation
   - Comprehensive error handling and logging

5. **Utilities** (`backend/systems/motif/utils/`)
   - Motif generation and synthesis functions
   - Configuration validation
   - Chaos event integration

## Key Features

### 🎭 **Narrative Context Generation**
Generate rich narrative context for AI systems:
```python
# Get context for AI narrative generation
context = await motif_service.get_motif_context(x=100.0, y=200.0)
enhanced_context = await motif_service.get_enhanced_narrative_context(context_size="large")
```

### 🔄 **Lifecycle Management**
Automated motif evolution through five lifecycle states:
- **EMERGING**: New motifs gaining influence
- **STABLE**: Established motifs with consistent impact  
- **WANING**: Declining motifs losing influence
- **DORMANT**: Inactive but potentially reactivatable motifs
- **CONCLUDED**: Completed narrative arcs

### 🌍 **Spatial Awareness**
Three scope levels for different narrative scales:
- **GLOBAL**: World-spanning themes affecting all locations
- **REGIONAL**: Area-specific motifs affecting geographic regions
- **LOCAL**: Location-specific motifs with limited influence
- **PLAYER_CHARACTER**: Personal motifs tied to individual characters

### ⚡ **Evolution System**
Dynamic motif evolution based on:
- Time progression and narrative events
- Player actions and choices
- Intensity thresholds and triggers
- System analysis and automation

### 🔍 **Conflict Resolution**
Intelligent handling of opposing themes:
- Detection of conflicting motifs (hope vs despair)
- Analysis of narrative tension opportunities
- Automatic resolution or preservation for dramatic effect

### 📊 **Analytics & Optimization**
Comprehensive system monitoring:
- Distribution analysis across scopes and regions
- Interaction analysis between motifs
- Performance statistics and health monitoring
- Optimization recommendations

## API Endpoints

### Core CRUD Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/motif/` | Create a new motif |
| `GET` | `/motif/` | List motifs with filtering |
| `GET` | `/motif/{id}` | Get specific motif details |
| `PUT` | `/motif/{id}` | Update motif |
| `DELETE` | `/motif/{id}` | Delete motif |

### Lifecycle Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/motif/{id}/lifecycle` | Update lifecycle state |
| `POST` | `/motif/lifecycle/advance` | Advance all eligible lifecycles |
| `POST` | `/motif/{id}/evolve` | Manually trigger evolution |

### Spatial Queries

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/motif/spatial/position` | Get motifs at position |
| `GET` | `/motif/spatial/region/{id}` | Get regional motifs |
| `GET` | `/motif/spatial/global` | Get global motifs |

### Narrative Context

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/motif/context/position` | Get narrative context at position |
| `GET` | `/motif/context/global` | Get global narrative context |

### Player Character Motifs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/motif/player/{id}` | Get player's motifs |

### Analytics & Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/motif/stats/summary` | System statistics |
| `GET` | `/motif/conflicts` | Active conflicts |
| `POST` | `/motif/conflicts/resolve` | Resolve conflicts |
| `GET` | `/motif/analysis/interactions` | Interaction analysis |
| `GET` | `/motif/analysis/distribution` | Distribution optimization |

### Advanced System Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/motif/canonical/generate` | Generate canonical motifs |
| `POST` | `/motif/evolution/process` | Process evolution triggers |
| `POST` | `/motif/maintenance/cleanup` | Cleanup expired motifs |

## Configuration

### JSON Configuration (`data/systems/motif/motif_config.json`)

The system uses a comprehensive JSON configuration file containing:

- **Chaos Events**: Categorized random events for narrative disruption
- **Action-to-Motif Mapping**: Maps player actions to motif categories  
- **Theme Relationships**: Opposing and complementary theme pairs
- **Name Generation**: Templates for generating motif names
- **System Settings**: Tunable parameters for system behavior

### Environment Variables

Configure the system through environment variables:

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_key_here

# Database (when using real database)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db

# Optional tuning
DEFAULT_MOTIF_INTENSITY=5
MAX_CONCURRENT_MOTIFS_PER_REGION=5
MOTIF_DECAY_RATE_DAYS=0.1
CHAOS_TRIGGER_THRESHOLD=7.5
```

## Usage Examples

### Creating a Motif

```python
from backend.systems.motif.services.service import MotifService
from backend.infrastructure.systems.motif.models import MotifCreate, MotifCategory, MotifScope

# Create motif service
service = MotifService(repository=motif_repository)

# Create a new hope motif
motif_data = MotifCreate(
    name="Dawn of Hope",
    description="A new hope emerges in the darkest hour",
    category=MotifCategory.HOPE,
    scope=MotifScope.REGIONAL,
    intensity=7,
    theme="hope against adversity"
)

motif = await service.create_motif(motif_data)
```

### Getting Narrative Context

```python
# Get context for AI narrative generation
context = await service.get_motif_context(x=100.0, y=200.0)

# Enhanced context for detailed AI prompts
enhanced = await service.get_enhanced_narrative_context(context_size="large")

# Use in AI prompt
prompt = f"Generate narrative with this context: {enhanced['prompt_text']}"
```

### Evolution and Lifecycle

```python
# Trigger manual evolution
result = await service.trigger_motif_evolution(
    motif_id="motif_123",
    trigger_type=MotifEvolutionTrigger.PLAYER_ACTION,
    trigger_description="Player heroic deed intensifies hope motif"
)

# Process all evolution triggers automatically
evolution_summary = await service.process_evolution_triggers()
```

### Conflict Analysis

```python
# Analyze motif interactions in a region
analysis = await service.analyze_motif_interactions(region_id="region_1")

# Get current conflicts
conflicts = await service.get_active_conflicts()

# Resolve conflicts automatically
resolved_count = await service.resolve_conflicts(auto_resolve=True)
```

## Testing

The system includes comprehensive test coverage across all layers:

```bash
# Run all motif system tests
python -m pytest backend/tests/systems/motif/ -v

# Run specific test categories
python -m pytest backend/tests/systems/motif/test_service.py -v
python -m pytest backend/tests/systems/motif/test_models.py -v
python -m pytest backend/tests/systems/motif/test_repositories.py -v
```

### Test Coverage

- **Models**: Validation, enum compliance, schema completeness
- **Service**: Business logic, AI integration, lifecycle management
- **Repository**: Database operations, filtering, error handling
- **Routers**: API endpoints, authentication, input validation
- **Utilities**: Helper functions, config validation, chaos integration

## Integration with Other Systems

### AI/LLM Integration

The motif system provides structured narrative context for AI systems:

```python
# For GPT/Claude prompts
context = await service.get_enhanced_narrative_context(context_size="medium")
prompt = f"Continue the story with: {context['prompt_text']}"

# For fine-tuned models
motifs = await service.get_motifs_at_position(x, y)
features = [motif.category.value for motif in motifs]
```

### Event System Integration

```python
# React to game events
if player_action == "heroic_deed":
    # Create or intensify hope motif
    motif_data = MotifCreate(
        name="Heroic Inspiration",
        category=MotifCategory.HOPE,
        # ... other fields
    )
    await service.create_motif(motif_data)
```

### Database Integration

The repository layer supports:
- **SQLAlchemy Async**: Full async/await database operations
- **Filtering & Pagination**: Efficient querying with complex filters
- **Spatial Queries**: Position-based motif retrieval
- **Transaction Management**: ACID compliance with rollback support

## Development Bible Compliance

The system strictly adheres to the Development Bible requirements:

✅ **49 Motif Categories**: All categories from Bible implemented  
✅ **Lifecycle States**: All five states with proper transitions  
✅ **Scope Levels**: Global, Regional, Local, Player Character  
✅ **AI Integration**: Narrative context generation for LLMs  
✅ **Spatial Awareness**: Position-based queries and regional filtering  
✅ **Evolution System**: Dynamic motif progression based on events  
✅ **Configuration**: External JSON config with validation  
✅ **Test Coverage**: Comprehensive testing ensuring compliance  

## Performance Considerations

### Optimization Features

- **Async Operations**: Non-blocking database and service operations
- **Pagination**: Efficient large dataset handling
- **Caching**: Built-in cache duration settings
- **Lazy Loading**: On-demand motif synthesis and analysis
- **Batch Operations**: Bulk evolution processing and cleanup

### Recommended Database Indices

```sql
-- For efficient filtering
CREATE INDEX idx_motif_category ON motifs(category);
CREATE INDEX idx_motif_scope ON motifs(scope);
CREATE INDEX idx_motif_lifecycle ON motifs(lifecycle);
CREATE INDEX idx_motif_intensity ON motifs(intensity);

-- For spatial queries  
CREATE INDEX idx_motif_position ON motifs(x, y);
CREATE INDEX idx_motif_region ON motifs(region_id);

-- For lifecycle management
CREATE INDEX idx_motif_timestamps ON motifs(created_at, updated_at);
```

## Monitoring and Maintenance

### Health Checks

```bash
# System health
curl http://localhost:8000/motif/health

# System information
curl http://localhost:8000/motif/info

# Statistics
curl http://localhost:8000/motif/stats/summary
```

### Maintenance Operations

```bash
# Generate canonical motifs (run once)
curl -X POST http://localhost:8000/motif/canonical/generate

# Process evolution triggers (run periodically)
curl -X POST http://localhost:8000/motif/evolution/process

# Cleanup expired motifs (run daily)
curl -X POST http://localhost:8000/motif/maintenance/cleanup
```

## Troubleshooting

### Common Issues

**Config Validation Errors**
```bash
# Validate configuration
PYTHONPATH=/path/to/project python backend/systems/motif/utils/config_validator.py
```

**Database Connection Issues**
- Ensure async SQLAlchemy session is properly configured
- Check database URL and credentials
- Verify database schema is created

**Performance Issues**
- Check database indices are created
- Monitor query performance with database logs
- Consider caching for frequently accessed data

### Logging

The system provides detailed logging at multiple levels:
- **DEBUG**: Detailed operation tracing
- **INFO**: System operations and statistics  
- **WARN**: Configuration and performance warnings
- **ERROR**: Operation failures and exceptions

## Future Enhancements

### Planned Features

- **Machine Learning Integration**: Predictive motif evolution
- **Advanced Spatial Queries**: Geographic information system integration
- **Real-time Updates**: WebSocket support for live motif changes
- **Analytics Dashboard**: Web interface for system monitoring
- **Export/Import**: Motif data exchange between systems

### Extensibility Points

- **Custom Evolution Triggers**: Pluggable evolution logic
- **Theme Relationship Engine**: Advanced relationship detection
- **Integration Adapters**: Connectors for external narrative systems
- **Custom Motif Types**: Domain-specific motif categories

---

**For additional support or questions, refer to the test files for usage examples or consult the Development Bible for system requirements.**
