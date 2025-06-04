# Chaos System LLM Integration

## Overview

The Chaos System has been enhanced with Large Language Model (LLM) integration to provide dynamic, context-aware narrative generation and intelligent analysis. This integration enhances procedural generation with AI-powered creativity while maintaining deterministic fallbacks for reliability.

## Features

### 1. Dynamic Event Description Generation

- **LLM-Enhanced Event Templates**: Event templates can now use LLM services to generate contextually appropriate titles, descriptions, and flavor text
- **Regional Context Awareness**: Descriptions adapt to regional culture, government type, and current tensions
- **Fallback System**: Automatically falls back to template-based generation if LLM services are unavailable

### 2. Warning System Narrative Enhancement

- **Contextual Warning Generation**: Warnings adapt their language and tone based on the specific situation and region
- **Phase-Appropriate Messaging**: Rumor, early warning, and imminent phases each have appropriate narrative styles
- **Cultural Sensitivity**: Warnings consider regional culture and communication preferences

### 3. Intelligent Cascade Analysis

- **AI-Powered Cascade Prediction**: LLM analyzes events and world context to predict realistic cascade effects
- **Narrative Reasoning**: Each cascade includes reasoning for why it makes narrative sense
- **Rule-Based Backup**: Traditional rule-based cascades still operate as fallback and validation

### 4. Dynamic Mitigation Suggestions

- **Context-Aware Recommendations**: Mitigation suggestions consider available resources, political climate, and cultural factors
- **Creative Problem Solving**: LLM can suggest novel approaches that template systems might miss
- **Feasibility Assessment**: Automatically evaluates feasibility based on available resources

## Architecture

### Core Components

1. **ChaosLLMService** (`services/llm_service.py`)
   - Central service managing all LLM interactions
   - Supports both OpenAI and Anthropic APIs
   - Handles prompt construction, response parsing, and error handling

2. **Enhanced Components**:
   - **WarningSystem**: Enhanced with LLM-powered warning narratives
   - **CascadeEngine**: Uses LLM for intelligent cascade analysis
   - **MitigationService**: Provides LLM-enhanced mitigation suggestions
   - **EventTemplate**: Supports LLM-generated event content

### Configuration

All LLM features can be configured via environment variables or the `ChaosConfig` class:

```python
# Enable/disable LLM features
CHAOS_LLM_ENABLED=true
CHAOS_LLM_EVENTS=true
CHAOS_LLM_WARNINGS=true
CHAOS_LLM_CASCADES=true
CHAOS_LLM_MITIGATIONS=true

# API Configuration
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
CHAOS_LLM_MODEL_PREFERENCE=openai  # or "anthropic" or "auto"

# Model Selection
CHAOS_OPENAI_MODEL=gpt-4
CHAOS_ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Performance Settings
CHAOS_LLM_TIMEOUT=30
CHAOS_LLM_MAX_RETRIES=2
CHAOS_LLM_FALLBACK=true
```

## Usage Examples

### 1. Generate LLM-Enhanced Event

```python
# Through ChaosManager
chaos_manager = ChaosManager()
await chaos_manager.initialize()

event = await chaos_manager.generate_llm_enhanced_event(
    event_type="political_upheaval",
    severity="major",
    regions=["capital_region"],
    context={
        "government_type": "monarchy",
        "recent_events": ["tax_increase", "food_shortage"],
        "key_figures": ["King Aldric", "Chancellor Maren"]
    }
)
```

### 2. Get AI-Powered Mitigation Suggestions

```python
# Through MitigationService
mitigation_service = MitigationService(config)
mitigation_service.set_llm_service(llm_service)

recommendations = await mitigation_service.get_mitigation_recommendations(
    chaos_event=political_crisis,
    available_resources={
        "diplomatic": {"allies": ["kingdom_of_eldoria"], "ambassadors": 3},
        "economic": {"treasury": "moderate", "trade_routes": 5},
        "military": {"standing_army": 1000, "fortifications": "strong"}
    }
)
```

### 3. Monitor LLM Performance

```python
# Get LLM usage metrics
llm_metrics = await chaos_manager.get_llm_metrics()
print(f"LLM warnings generated: {llm_metrics['warning_system']['llm_generated_warnings']}")
print(f"Template fallbacks: {llm_metrics['warning_system']['template_fallbacks']}")
```

## Prompts and Response Formats

### Event Generation Prompt

The system uses carefully crafted prompts that include:
- Event type and severity
- Regional context (culture, government, economic situation)
- Recent events and current tensions
- Character relationships and motivations

### Expected Response Formats

All LLM responses follow structured JSON formats:

```json
{
  "title": "The Great Merchant Strike",
  "description": "Growing discontent among merchants...",
  "flavor_text": "Whispers spread through the marketplace...",
  "narrative_impact": "This event will strain relationships..."
}
```

## Performance Considerations

### Caching and Optimization

- **Response Caching**: Similar prompts are cached to reduce API calls
- **Async Processing**: All LLM calls are asynchronous and non-blocking
- **Timeout Handling**: Configurable timeouts prevent hanging operations
- **Graceful Degradation**: Always falls back to template-based generation

### Cost Management

- **Smart Fallbacks**: Only uses LLM when templates are insufficient
- **Prompt Optimization**: Efficient prompts minimize token usage
- **Rate Limiting**: Built-in rate limiting prevents API abuse
- **Feature Toggles**: Individual LLM features can be disabled

## Error Handling

The system includes comprehensive error handling:

1. **API Failures**: Automatic fallback to template generation
2. **Malformed Responses**: JSON parsing with fallback content
3. **Rate Limiting**: Exponential backoff and retry logic
4. **Network Issues**: Timeout handling and graceful degradation

## Metrics and Monitoring

### Available Metrics

- `llm_generated_warnings`: Count of LLM-generated warnings
- `template_fallbacks`: Count of fallbacks to template system
- `llm_analyzed_cascades`: Count of LLM cascade analyses
- `llm_suggestions_generated`: Count of LLM mitigation suggestions

### Monitoring Dashboard

```python
async def get_llm_status():
    metrics = await chaos_manager.get_llm_metrics()
    
    return {
        "llm_enabled": metrics["llm_service"]["enabled"],
        "success_rate": calculate_success_rate(metrics),
        "performance": {
            "warnings": metrics["warning_system"],
            "cascades": metrics["cascade_engine"],
            "mitigations": metrics["mitigation_service"]
        }
    }
```

## Best Practices

### 1. Configuration
- Always provide fallback configurations
- Test with LLM disabled to ensure system reliability
- Monitor API usage and costs

### 2. Development
- Use the debug mode to log LLM interactions
- Test edge cases where LLM might fail
- Validate LLM responses before using them

### 3. Production
- Set appropriate timeouts based on your tolerance
- Monitor fallback rates to detect issues
- Keep template systems updated as backups

## Troubleshooting

### Common Issues

1. **No LLM Responses**
   - Check API keys are set correctly
   - Verify network connectivity
   - Check API quotas and rate limits

2. **High Fallback Rates**
   - Review timeout settings
   - Check API service status
   - Monitor error logs for patterns

3. **Poor Quality Responses**
   - Review prompt templates
   - Adjust model selection
   - Provide more context in prompts

### Debug Commands

```python
# Enable debug logging
config.debug_mode = True

# Check LLM service status
await llm_service.test_connection()

# Get detailed error logs
error_history = chaos_manager.get_error_history()
```

## Future Enhancements

### Planned Features
- **Narrative Consistency**: Cross-reference previous events for consistency
- **Character Memory**: Remember character personalities and relationships
- **Dynamic World Building**: Generate new locations and NPCs as needed
- **Multi-Language Support**: Generate content in different languages

### Research Areas
- **Fine-tuned Models**: Training models specifically for fantasy world simulation
- **Embedding Integration**: Using embeddings for better context retrieval
- **Multimodal Generation**: Adding image generation for events and locations

## API Reference

### ChaosLLMService Methods

- `generate_event_content(event_template, context)`: Generate event descriptions
- `generate_warning_narrative(phase, event_type, context)`: Create warning messages
- `analyze_cascade_potential(event, world_context)`: Analyze cascade effects
- `suggest_mitigations(event, resources)`: Generate mitigation recommendations
- `test_connection()`: Test API connectivity

### Configuration Options

See the `ChaosConfig` class for all available configuration options and their descriptions.

---

For more details, see the individual component documentation and the main chaos system README. 