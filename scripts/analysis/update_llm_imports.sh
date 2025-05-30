#!/bin/bash

# Script to update import statements in the LLM system files
# This fixes circular dependencies by updating the imports within the copied files

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting LLM imports update...${NC}"

# Update imports in all core files
echo -e "${YELLOW}Updating imports in core files...${NC}"

# Find all Python files in the llm/core directory
FILES=$(find backend/systems/llm/core -name "*.py")

# Update each file
for file in $FILES; do
    echo -e "${YELLOW}Processing $file...${NC}"
    
    # Update imports from backend.systems.dm to backend.systems.llm.core
    sed -i '' 's|from backend.systems.dm\.|from backend.systems.llm.core.|g' "$file"
    
    # Update imports from specific dm modules
    sed -i '' 's|from backend.systems.dm.event_integration|from backend.systems.llm.core.event_integration|g' "$file"
    sed -i '' 's|from backend.systems.dm.memory_system|from backend.systems.llm.core.memory_system|g' "$file"
    sed -i '' 's|from backend.systems.dm.rumor_system|from backend.systems.llm.core.rumor_system|g' "$file"
    sed -i '' 's|from backend.systems.dm.motif_system|from backend.systems.llm.core.motif_system|g' "$file"
    sed -i '' 's|from backend.systems.dm.faction_system|from backend.systems.llm.core.faction_system|g' "$file"
    sed -i '' 's|from backend.systems.dm.dm_core|from backend.systems.llm.core.dm_core|g' "$file"
    
    # Update imports from old AI system to new LLM system
    sed -i '' 's|from backend.systems.ai.services.gpt_client|from backend.systems.llm.services.gpt_client|g' "$file"
    sed -i '' 's|from backend.core.ai.gpt_client|from backend.systems.llm.services.gpt_client|g' "$file"
    
    echo -e "${GREEN}Updated imports in $file${NC}"
done

# Update imports in routes files
echo -e "${YELLOW}Updating imports in routes files...${NC}"

# Find all Python files in the llm/routes directory
ROUTE_FILES=$(find backend/systems/llm/routes -name "*.py")

# Update each file
for file in $ROUTE_FILES; do
    echo -e "${YELLOW}Processing $file...${NC}"
    
    # Update imports
    sed -i '' 's|from backend.systems.dm\.|from backend.systems.llm.core.|g' "$file"
    sed -i '' 's|from backend.systems.dm.dm_core|from backend.systems.llm.core.dm_core|g' "$file"
    
    echo -e "${GREEN}Updated imports in $file${NC}"
done

echo -e "${GREEN}LLM imports update completed successfully!${NC}" 