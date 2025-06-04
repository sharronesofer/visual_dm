# Mock Implementations and Technical Debt

This document tracks all mock implementations, placeholders, and technical debt in the World Generation system that need to be addressed for production use.

## Critical Mock Functions (Database Integration Required)

### 1. `refresh_cleared_pois()` - Lines 596-602 in `world_generation_utils.py`

**Current Status**: Mock implementation  
**Description**: Function that should refresh POIs that have been cleared by players after a certain time period.  
**Mock Behavior**: Returns empty list instead of querying database for cleared POIs.

```python
# Current mock implementation
def refresh_cleared_pois():
    # Mock implementation - replace with actual database logic
    return []
```

**Required Integration**:
- Connect to game database to query cleared POIs
- Implement time-based refresh logic
- Update POI status in database when regenerating

**Impact**: Players cannot experience refreshed content in cleared dungeons and exploration sites.

---

### 2. `generate_monsters_for_tile()` - Lines 617-640 in `world_generation_utils.py`

**Current Status**: Mock implementation  
**Description**: Generates monsters for combat encounters based on danger level and party challenge rating.  
**Mock Behavior**: Returns sample monster data instead of real monster instances.

```python
# Current mock implementation returns sample data
return [
    {
        "name": "Goblin",
        "cr": 0.25,
        "type": "humanoid",
        "hp": 7
    }
]
```

**Required Integration**:
- Connect to monster database or bestiary system
- Implement proper CR calculations based on party level
- Generate appropriate encounter compositions
- Consider biome-specific monster types

**Impact**: Combat encounters are not properly balanced or varied.

---

### 3. `attempt_rest()` - Lines 656-670 in `world_generation_utils.py`

**Current Status**: Mock implementation  
**Description**: Handles player rest attempts with safety checks and consequences.  
**Mock Behavior**: Always returns successful rest without actual game state changes.

```python
# Current mock - always successful
return {
    "success": True,
    "message": "Rest completed successfully",
    "dangers": []
}
```

**Required Integration**:
- Connect to player state management system
- Implement actual HP/MP restoration
- Random encounter checks during rest
- Environmental danger calculations

**Impact**: Rest mechanics don't function properly in gameplay.

---

### 4. `generate_social_poi()` - Lines 684-690 in `world_generation_utils.py`

**Current Status**: Mock implementation  
**Description**: Creates social points of interest like taverns, shops, and guilds.  
**Mock Behavior**: Returns basic placeholder data without NPCs or services.

```python
# Current mock returns minimal data
return {
    "type": "tavern",
    "name": "Mock Tavern",
    "services": []
}
```

**Required Integration**:
- Connect to NPC generation system
- Implement service and inventory systems
- Generate appropriate social interactions
- Link to economy and quest systems

**Impact**: Social gameplay elements are not functional.

---

### 5. `generate_tile()` - Lines 705-718 in `world_generation_utils.py`

**Current Status**: Mock implementation  
**Description**: Generates individual hex tiles with terrain, POIs, and features.  
**Mock Behavior**: Returns simplified tile data without proper integration.

```python
# Mock returns basic structure
return {
    "coordinate": coordinate,
    "terrain": "forest",
    "features": [],
    "poi": None
}
```

**Required Integration**:
- Connect to tile database/storage system
- Implement proper terrain generation algorithms
- Integrate with map rendering system
- Link to movement and exploration systems

**Impact**: World tiles are not properly persistent or detailed.

---

## Weather System Integration - Lines 180-200 in `world_generation_utils.py`

**Current Status**: Placeholder returning mock data  
**Description**: Should fetch real weather data based on region coordinates.  
**Mock Behavior**: Returns static weather data.

```python
# Mock weather data
return {
    "temperature": 72,
    "condition": "partly_cloudy", 
    "humidity": 45,
    "wind_speed": 8
}
```

**Required Integration**:
- Implement OpenWeatherMap API integration
- Handle API errors and fallbacks
- Cache weather data appropriately
- Map game coordinates to real-world locations

**Impact**: Weather doesn't affect gameplay or immersion.

---

## Region Memory Placeholders - Lines 489-491 in `world_generation_utils.py`

**Current Status**: Placeholder fields  
**Description**: Region metadata that should track significant events and story elements.

```python
# Placeholder fields that need implementation
"memory": "Placeholder for region memory (major events)",
"arc": "Placeholder for arc (meta-quest)",
"metropolis_type": "Placeholder for metropolis type"
```

**Required Integration**:
- Design event tracking system
- Implement quest arc management
- Create metropolis classification system
- Store and retrieve historical data

**Impact**: Regions don't develop personality or history over time.

---

## Database Connectivity Issues

### Missing Database References

Throughout the codebase, there are commented-out references indicating the system was designed to work with a database but currently operates in isolation:

```python
# Example patterns found in the code:
# db_session.query(POI).filter(...)  # Commented out
# region_data = database.get_region(...)  # Missing implementation
```

**Required Actions**:
1. Implement proper database session management
2. Create database models for world generation entities
3. Add proper error handling for database operations
4. Implement transaction management for world generation

---

## Priority Implementation Order

1. **High Priority** - Database connectivity and session management
2. **High Priority** - `generate_tile()` and `generate_monsters_for_tile()` - Core gameplay
3. **Medium Priority** - `refresh_cleared_pois()` and `attempt_rest()` - Player experience
4. **Medium Priority** - Weather system integration - Environmental immersion
5. **Low Priority** - `generate_social_poi()` - Social features
6. **Low Priority** - Region memory system - Long-term content

---

## Testing Recommendations

Before implementing production versions:

1. **Unit Tests**: Create tests for each mock function's expected behavior
2. **Integration Tests**: Test database connectivity and transaction handling
3. **Performance Tests**: Ensure generation algorithms scale with world size
4. **Error Handling**: Test failure scenarios for external API calls
5. **Data Validation**: Verify generated content meets game balance requirements

---

## Configuration Dependencies

Some mocks depend on the new configuration system:

- Monster generation needs CR calculation parameters
- POI generation needs type weights and constraints
- Rest mechanics need danger level modifiers
- Weather system needs coordinate mapping parameters

Ensure the `GenerationConfigManager` is fully implemented before addressing these mocks. 