# Data Directory Analysis

## Current Structure
- `/data/system/runtime/` - Contains JSON data files and rule definitions
  - `adjacency.json` - Contains biome adjacency rules
  - `/modding/` - Contains modding-related files
  - `/rules_json/` - Contains game rules in JSON format

## Analysis

The `/data` directory appears to contain:
1. Configuration files
2. Game rules
3. Reference data for the game systems
4. Modding-related data

These are all **static resources** used by the various systems, rather than code that belongs to a specific system. As such, the data directory serves as a centralized location for these resources, making them easily accessible to all systems.

## Recommendation

**Keep the data directory separate** for the following reasons:

1. **Separation of Concerns**: Data files represent configuration and content, not business logic. Keeping them separate maintains clean boundaries.

2. **Cross-System Access**: Many systems likely need access to the same data files. Having them in a central location prevents duplication.

3. **Simplified Backup/Deployment**: Keeping all data files in one location makes it easier to backup or deploy just the data separately from code.

4. **Modding Support**: As mentioned in the Development Bible, the game supports modding. Keeping data in a centralized directory makes it easier for modders to find and modify game data.

5. **Convention**: It's a common convention in game development to separate data files from code, especially for games with modding support.

## Example Usage Pattern

```python
# Typical usage pattern
import json
from pathlib import Path

# Get path to data file
data_path = Path(__file__).resolve().parent.parent.parent / "data" / "adjacency.json"

# Load data
with open(data_path, "r") as f:
    adjacency_data = json.load(f)
    
# Use data in system logic
# ...
```

This pattern allows all systems to access the data files without needing to know where they are in relation to the system's location.

## Future Considerations

As the project grows, consider:

1. Creating a `DataManager` service in `backend/systems/data/services/` that provides centralized, cached access to data files.

2. Implementing a `DataAccessLayer` that abstracts away the specifics of how data is stored and accessed.

3. Adding versioning and migration support for data files to ensure backward compatibility. 