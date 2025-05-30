#!/bin/bash

# Script to migrate the GameDataRegistry class to the systems directory
# This follows the same pattern as the main migration script

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting GameDataRegistry migration...${NC}"

# Step 1: Create the data system directory structure
echo -e "${YELLOW}Creating data system directory structure...${NC}"

mkdir -p backend/systems/data/services
mkdir -p backend/systems/data/models
mkdir -p backend/systems/data/schemas
mkdir -p backend/systems/data/utils
mkdir -p backend/systems/data/loaders

# Create __init__.py files
touch backend/systems/data/__init__.py
touch backend/systems/data/services/__init__.py
touch backend/systems/data/models/__init__.py
touch backend/systems/data/schemas/__init__.py
touch backend/systems/data/utils/__init__.py
touch backend/systems/data/loaders/__init__.py

echo -e "${GREEN}Data system directory structure created.${NC}"

# Step 2: Copy GameDataRegistry to the new location
echo -e "${YELLOW}Copying GameDataRegistry to the new location...${NC}"

if [ -f backend/data/modding/loaders/game_data_registry.py ]; then
    cp backend/data/modding/loaders/game_data_registry.py backend/systems/data/loaders/
    echo -e "${GREEN}Copied game_data_registry.py to new location.${NC}"
else
    echo -e "${RED}Error: game_data_registry.py not found at expected location.${NC}"
fi

# Step 3: Create backward compatibility module
echo -e "${YELLOW}Creating backward compatibility module...${NC}"

mkdir -p backend/data/modding/loaders
cat > backend/data/modding/loaders/game_data_registry.py << 'EOF'
"""
This module has been moved to backend.systems.data.loaders.game_data_registry
This is a compatibility layer that will be removed in a future release.
"""
import warnings

warnings.warn(
    "The module backend.data.modding.loaders.game_data_registry is deprecated. "
    "Use backend.systems.data.loaders.game_data_registry instead.",
    DeprecationWarning,
    stacklevel=2
)

from backend.systems.data.loaders.game_data_registry import *
EOF

echo -e "${GREEN}Created backward compatibility module.${NC}"

# Step 4: Scan for imports to update
echo -e "${YELLOW}Identifying import statements to update in the rest of the codebase...${NC}"

echo "Files importing game_data_registry.py:"
grep -r "from backend.data.modding.loaders.game_data_registry" --include="*.py" backend || echo "No imports found"

echo -e "${YELLOW}You should manually update these imports to use the new location.${NC}"
echo -e "${YELLOW}The backward compatibility module will continue to work, but will generate deprecation warnings.${NC}"

# Step 5: Update the migration notes to include this change
echo -e "${YELLOW}Updating migration notes...${NC}"

cat >> backend/MIGRATION_NOTES.md << 'EOF'

## Additional Changes - GameDataRegistry Migration

3. GameDataRegistry moved from `backend/data/modding/loaders/game_data_registry.py` to `backend/systems/data/loaders/game_data_registry.py`

Please update your import statements as follows:

- OLD: `from backend.data.modding.loaders.game_data_registry import GameDataRegistry`
- NEW: `from backend.systems.data.loaders.game_data_registry import GameDataRegistry`
EOF

echo -e "${GREEN}Updated migration notes.${NC}"

echo -e "${GREEN}GameDataRegistry migration completed successfully!${NC}" 