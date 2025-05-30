#!/bin/bash

# Script to merge backend/systems/ai and backend/systems/dm into a unified directory structure
# This follows similar migration patterns as the previous reorganization scripts

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting AI and DM system merge...${NC}"

# Step 1: Create the LLM system directory structure
echo -e "${YELLOW}Creating LLM system directory structure...${NC}"

mkdir -p backend/systems/llm/services
mkdir -p backend/systems/llm/models
mkdir -p backend/systems/llm/schemas
mkdir -p backend/systems/llm/utils
mkdir -p backend/systems/llm/core
mkdir -p backend/systems/llm/routes

# Create __init__.py files
touch backend/systems/llm/__init__.py
touch backend/systems/llm/services/__init__.py
touch backend/systems/llm/models/__init__.py
touch backend/systems/llm/schemas/__init__.py
touch backend/systems/llm/utils/__init__.py
touch backend/systems/llm/core/__init__.py
touch backend/systems/llm/routes/__init__.py

echo -e "${GREEN}LLM system directory structure created.${NC}"

# Step 2: Copy files from AI and DM directories to the new LLM directory
echo -e "${YELLOW}Copying files to the new location...${NC}"

# Copy AI files
if [ -f backend/systems/ai/services/gpt_client.py ]; then
    cp backend/systems/ai/services/gpt_client.py backend/systems/llm/services/
    echo -e "${GREEN}Copied gpt_client.py to LLM services.${NC}"
else
    echo -e "${RED}Error: gpt_client.py not found at expected location.${NC}"
fi

# Copy AI README for reference
if [ -f backend/systems/ai/README.md ]; then
    # Save for reference
    cp backend/systems/ai/README.md backend/systems/llm/reference_ai_README.md
    echo -e "${GREEN}Copied AI README for reference.${NC}"
fi

# Copy DM files
if [ -f backend/systems/dm/dm_core.py ]; then
    cp backend/systems/dm/dm_core.py backend/systems/llm/core/
    echo -e "${GREEN}Copied dm_core.py to LLM core.${NC}"
else
    echo -e "${RED}Error: dm_core.py not found at expected location.${NC}"
fi

if [ -f backend/systems/dm/event_integration.py ]; then
    cp backend/systems/dm/event_integration.py backend/systems/llm/core/
    echo -e "${GREEN}Copied event_integration.py to LLM core.${NC}"
fi

if [ -f backend/systems/dm/faction_system.py ]; then
    cp backend/systems/dm/faction_system.py backend/systems/llm/core/
    echo -e "${GREEN}Copied faction_system.py to LLM core.${NC}"
fi

if [ -f backend/systems/dm/motif_system.py ]; then
    cp backend/systems/dm/motif_system.py backend/systems/llm/core/
    echo -e "${GREEN}Copied motif_system.py to LLM core.${NC}"
fi

if [ -f backend/systems/dm/rumor_system.py ]; then
    cp backend/systems/dm/rumor_system.py backend/systems/llm/core/
    echo -e "${GREEN}Copied rumor_system.py to LLM core.${NC}"
fi

if [ -f backend/systems/dm/memory_system.py ]; then
    cp backend/systems/dm/memory_system.py backend/systems/llm/core/
    echo -e "${GREEN}Copied memory_system.py to LLM core.${NC}"
fi

if [ -f backend/systems/dm/dm_routes.py ]; then
    cp backend/systems/dm/dm_routes.py backend/systems/llm/routes/
    echo -e "${GREEN}Copied dm_routes.py to LLM routes.${NC}"
fi

# Step 3: Create backward compatibility modules
echo -e "${YELLOW}Creating backward compatibility modules...${NC}"

# Create compatibility module for gpt_client.py
cat > backend/systems/ai/services/gpt_client.py << 'EOF'
"""
This module has been moved to backend.systems.llm.services.gpt_client
This is a compatibility layer that will be removed in a future release.
"""
import warnings

warnings.warn(
    "The module backend.systems.ai.services.gpt_client is deprecated. "
    "Use backend.systems.llm.services.gpt_client instead.",
    DeprecationWarning,
    stacklevel=2
)

from backend.systems.llm.services.gpt_client import *
EOF

# Create compatibility module for dm_core.py
cat > backend/systems/dm/dm_core.py << 'EOF'
"""
This module has been moved to backend.systems.llm.core.dm_core
This is a compatibility layer that will be removed in a future release.
"""
import warnings

warnings.warn(
    "The module backend.systems.dm.dm_core is deprecated. "
    "Use backend.systems.llm.core.dm_core instead.",
    DeprecationWarning,
    stacklevel=2
)

from backend.systems.llm.core.dm_core import *
EOF

# Create compatibility modules for other DM files
for file in event_integration.py faction_system.py motif_system.py rumor_system.py memory_system.py; do
    if [ -f "backend/systems/dm/$file" ]; then
        module_name=${file%.py}
        cat > "backend/systems/dm/$file" << EOF
"""
This module has been moved to backend.systems.llm.core.$file
This is a compatibility layer that will be removed in a future release.
"""
import warnings

warnings.warn(
    "The module backend.systems.dm.$module_name is deprecated. "
    "Use backend.systems.llm.core.$module_name instead.",
    DeprecationWarning,
    stacklevel=2
)

from backend.systems.llm.core.$module_name import *
EOF
        echo -e "${GREEN}Created backward compatibility module for $file.${NC}"
    fi
done

# Create compatibility module for dm_routes.py
if [ -f backend/systems/dm/dm_routes.py ]; then
    cat > backend/systems/dm/dm_routes.py << 'EOF'
"""
This module has been moved to backend.systems.llm.routes.dm_routes
This is a compatibility layer that will be removed in a future release.
"""
import warnings

warnings.warn(
    "The module backend.systems.dm.dm_routes is deprecated. "
    "Use backend.systems.llm.routes.dm_routes instead.",
    DeprecationWarning,
    stacklevel=2
)

from backend.systems.llm.routes.dm_routes import *
EOF
    echo -e "${GREEN}Created backward compatibility module for dm_routes.py.${NC}"
fi

echo -e "${GREEN}Created backward compatibility modules.${NC}"

# Step 4: Create new README for the LLM system
echo -e "${YELLOW}Creating README for the LLM system...${NC}"

cat > backend/systems/llm/README.md << 'EOF'
# LLM System

## Overview

The LLM (Language Learning Model) System provides a unified interface for all AI-powered narrative, context management, and content generation in Visual DM. It merges the previous AI and DM systems into a cohesive architecture that handles GPT integration, narrative logic, and storytelling capabilities.

## Directory Structure

- `backend/systems/llm/` - Root of the LLM System
  - `services/` - Contains client services for AI providers (OpenAI, Claude, etc.)
  - `core/` - Contains narrative generation and DM logic components
  - `routes/` - Contains API routes for LLM functionality
  - `models/` - Contains data models for AI requests/responses and narrative objects
  - `schemas/` - Contains Pydantic schemas for validation
  - `utils/` - Contains utility functions for prompt engineering and response processing

## Key Components

### GPT Client

The `GPTClient` class (`services/gpt_client.py`) provides a standardized interface for interacting with various LLM providers. It handles:

- AI request formatting
- Error handling and retries
- Response parsing and validation
- Configuration management

### DM Core

The `DungeonMaster` class (`core/dm_core.py`) provides the central orchestration for narrative generation and world management. It handles:

- Context gathering and processing
- Memory and rumor management
- Motif and theme integration
- Faction dynamics
- Combat narration
- NPC dialogue generation

### Subsystems

- **Memory System** (`core/memory_system.py`): Manages entity memories and recall
- **Rumor System** (`core/rumor_system.py`): Handles information propagation and mutation
- **Motif System** (`core/motif_system.py`): Manages narrative themes and motifs
- **Faction System** (`core/faction_system.py`): Handles faction relationships and conflicts
- **Event Integration** (`core/event_integration.py`): Event handlers for narrative events

## Usage Examples

### Getting the DM Instance

```python
from backend.systems.llm.core.dm_core import DungeonMaster

# Get the singleton instance
dm = DungeonMaster.get_instance()

# Generate narrative context
context = dm.get_full_narrative_context(entity_id="npc123", region_id="capital_hub")
```

### Using the GPT Client

```python
from backend.systems.llm.services.gpt_client import GPTClient

# Get the singleton instance
client = GPTClient.get_instance()

# Generate text with a prompt
response = await client.generate_text(
    prompt="Describe the tension in a city on the brink of war",
    system_prompt="You are a fantasy narrative assistant."
)
```

## Integration Examples

### Event Handling

```python
from backend.systems.events import EventDispatcher
from backend.systems.llm.core.event_integration import register_narrative_handlers

# Register narrative event handlers with the central event dispatcher
dispatcher = EventDispatcher.get_instance()
register_narrative_handlers(dispatcher)
```

### API Routes Integration

```python
from fastapi import APIRouter
from backend.systems.llm.routes.dm_routes import router as dm_router

# Include DM routes in a FastAPI application
app = FastAPI()
app.include_router(dm_router, prefix="/api/dm", tags=["dm"])
```

## Best Practices

1. **Use singleton instances**: Always access the DungeonMaster and GPTClient through their `get_instance()` methods.

2. **Prefer high-level methods**: Use the DungeonMaster's high-level methods that coordinate between subsystems rather than accessing subsystems directly.

3. **Handle errors gracefully**: AI services can fail. Always implement fallbacks for critical narrative paths.

4. **Optimize prompts**: Keep prompts concise while providing sufficient context. Use system prompts to guide the AI's behavior.

5. **Cache when appropriate**: Cache results for expensive operations like context gathering to reduce API costs and latency.

## Future Enhancements

1. **Model Switching**: Add support for dynamically switching between different AI providers.

2. **Token Optimization**: Implement automatic token counting and context truncation to optimize API usage.

3. **Prompt Library**: Create a versioned library of optimized prompts for different narrative scenarios.

4. **Fine-tuned Models**: Support for custom fine-tuned models for specific narrative tasks.

5. **Event-Driven Architecture**: Further enhance event-driven integration with other systems.

## See Also

- [MIGRATION_NOTES.md](../../MIGRATION_NOTES.md) - Details on the LLM system migration
- [Development_Bible.md](../../docs/Development_Bible.md) - The Visual DM architecture and systems description
EOF

echo -e "${GREEN}Created README for the LLM system.${NC}"

# Step 5: Update the migration notes to include this change
echo -e "${YELLOW}Updating migration notes...${NC}"

cat >> backend/MIGRATION_NOTES.md << 'EOF'

## AI and DM System Merge

The AI and DM systems have been merged into a single LLM (Language Learning Model) system:

- Previously separate AI client code and DM narrative logic are now unified
- New directory structure under `backend/systems/llm/`
- Import changes:

Previous AI imports:
- OLD: `from backend.systems.ai.services.gpt_client import GPTClient`
- NEW: `from backend.systems.llm.services.gpt_client import GPTClient`

Previous DM imports:
- OLD: `from backend.systems.dm.dm_core import DungeonMaster`
- NEW: `from backend.systems.llm.core.dm_core import DungeonMaster`

- OLD: `from backend.systems.dm.memory_system import Memory`
- NEW: `from backend.systems.llm.core.memory_system import Memory`

(Similar pattern for all DM modules)

The merge reflects their close relationship and dependency in the system, reducing duplication and improving cohesion.
EOF

echo -e "${GREEN}Updated migration notes.${NC}"

# Step 6: Scan for imports to update
echo -e "${YELLOW}Identifying import statements to update in the rest of the codebase...${NC}"

echo "Files importing AI services:"
grep -r "from backend.systems.ai" --include="*.py" backend || echo "No imports found"

echo "Files importing DM modules:"
grep -r "from backend.systems.dm" --include="*.py" backend || echo "No imports found"

echo -e "${YELLOW}You should manually update these imports to use the new locations.${NC}"
echo -e "${YELLOW}The backward compatibility modules will continue to work, but will generate deprecation warnings.${NC}"

echo -e "${GREEN}AI and DM system merge completed successfully!${NC}"
echo -e "${GREEN}Next steps:${NC}"
echo -e "${YELLOW}1. Review the changes to ensure everything is correct${NC}"
echo -e "${YELLOW}2. Run tests to ensure nothing is broken${NC}"
echo -e "${YELLOW}3. Update import statements in the codebase${NC}"
echo -e "${YELLOW}4. After a sufficient deprecation period, remove the backward compatibility modules${NC}" 