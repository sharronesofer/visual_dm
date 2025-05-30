#!/bin/bash

# Backend Directory Reorganization Script
# This script implements the reorganization plan for the backend directory structure

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting backend directory reorganization...${NC}"

# Step 1: Create new directory structures
echo -e "${YELLOW}Creating new directory structures...${NC}"

# Analytics System
mkdir -p backend/systems/analytics/services
mkdir -p backend/systems/analytics/models
mkdir -p backend/systems/analytics/schemas
mkdir -p backend/systems/analytics/utils

# AI System
mkdir -p backend/systems/ai/services
mkdir -p backend/systems/ai/models
mkdir -p backend/systems/ai/schemas
mkdir -p backend/systems/ai/utils

# Shared utilities for system-wide use
mkdir -p backend/systems/shared/utils
mkdir -p backend/systems/shared/models

echo -e "${GREEN}New directory structures created.${NC}"

# Step 2: Copy files to new locations
echo -e "${YELLOW}Copying files to new locations...${NC}"

# Analytics Service
if [ -f backend/app/core/analytics/analytics_service.py ]; then
    cp backend/app/core/analytics/analytics_service.py backend/systems/analytics/services/
    echo -e "${GREEN}Copied analytics_service.py to new location.${NC}"
else
    echo -e "${RED}Error: analytics_service.py not found at expected location.${NC}"
fi

# GPT Client
if [ -f backend/core/ai/gpt_client.py ]; then
    cp backend/core/ai/gpt_client.py backend/systems/ai/services/
    echo -e "${GREEN}Copied gpt_client.py to new location.${NC}"
else
    echo -e "${RED}Error: gpt_client.py not found at expected location.${NC}"
fi

# Create __init__.py files to make the directories proper Python packages
touch backend/systems/analytics/__init__.py
touch backend/systems/analytics/services/__init__.py
touch backend/systems/analytics/models/__init__.py
touch backend/systems/analytics/schemas/__init__.py
touch backend/systems/analytics/utils/__init__.py

touch backend/systems/ai/__init__.py
touch backend/systems/ai/services/__init__.py
touch backend/systems/ai/models/__init__.py
touch backend/systems/ai/schemas/__init__.py
touch backend/systems/ai/utils/__init__.py

touch backend/systems/shared/__init__.py
touch backend/systems/shared/utils/__init__.py
touch backend/systems/shared/models/__init__.py

echo -e "${GREEN}Created __init__.py files in all new directories.${NC}"

# Step 3: Update imports in the moved files
echo -e "${YELLOW}Updating imports in moved files...${NC}"

# Update imports in analytics_service.py
if [ -f backend/systems/analytics/services/analytics_service.py ]; then
    # Replace the import for EventBase
    sed -i '' 's|from backend.systems.events.models.event_dispatcher import EventBase|from backend.systems.events import EventBase|g' backend/systems/analytics/services/analytics_service.py
    echo -e "${GREEN}Updated imports in analytics_service.py.${NC}"
else
    echo -e "${RED}Error: analytics_service.py not found in new location.${NC}"
fi

# No need to update imports in gpt_client.py as it doesn't have any backend-specific imports

# Step 4: Create backward compatibility modules
echo -e "${YELLOW}Creating backward compatibility modules...${NC}"

# Create backward compatibility module for analytics_service.py
mkdir -p backend/app/core/analytics
cat > backend/app/core/analytics/analytics_service.py << 'EOF'
"""
This module has been moved to backend.systems.analytics.services.analytics_service
This is a compatibility layer that will be removed in a future release.
"""
import warnings

warnings.warn(
    "The module backend.app.core.analytics.analytics_service is deprecated. "
    "Use backend.systems.analytics.services.analytics_service instead.",
    DeprecationWarning,
    stacklevel=2
)

from backend.systems.analytics.services.analytics_service import *
EOF

# Create backward compatibility module for gpt_client.py
mkdir -p backend/core/ai
cat > backend/core/ai/gpt_client.py << 'EOF'
"""
This module has been moved to backend.systems.ai.services.gpt_client
This is a compatibility layer that will be removed in a future release.
"""
import warnings

warnings.warn(
    "The module backend.core.ai.gpt_client is deprecated. "
    "Use backend.systems.ai.services.gpt_client instead.",
    DeprecationWarning,
    stacklevel=2
)

from backend.systems.ai.services.gpt_client import *
EOF

echo -e "${GREEN}Created backward compatibility modules.${NC}"

# Step 5: Scan for imports to update
echo -e "${YELLOW}Identifying import statements to update in the rest of the codebase...${NC}"

# Find all Python files that import the moved modules
echo "Files importing analytics_service.py:"
grep -r "from backend.app.core.analytics.analytics_service" --include="*.py" backend || echo "No imports found"

echo "Files importing gpt_client.py:"
grep -r "from backend.core.ai.gpt_client" --include="*.py" backend || echo "No imports found"

echo -e "${YELLOW}You should manually update these imports to use the new locations.${NC}"
echo -e "${YELLOW}The backward compatibility modules will continue to work, but will generate deprecation warnings.${NC}"

# Step 6: Add documentation for the changes
echo -e "${YELLOW}Adding documentation for the changes...${NC}"

cat > backend/MIGRATION_NOTES.md << 'EOF'
# Backend Reorganization Migration Notes

## Overview

As part of improving the backend architecture, we have reorganized the directory structure to follow a more consistent domain-driven design.

## Changes Made

1. Analytics service moved from `backend/app/core/analytics/analytics_service.py` to `backend/systems/analytics/services/analytics_service.py`
2. GPT client moved from `backend/core/ai/gpt_client.py` to `backend/systems/ai/services/gpt_client.py`

## Migration Guide for Developers

Please update your import statements as follows:

- OLD: `from backend.app.core.analytics.analytics_service import AnalyticsService`
- NEW: `from backend.systems.analytics.services.analytics_service import AnalyticsService`

- OLD: `from backend.core.ai.gpt_client import GPTClient`
- NEW: `from backend.systems.ai.services.gpt_client import GPTClient`

While the old import paths will continue to work temporarily through backward compatibility modules,
they will generate deprecation warnings. These compatibility modules will be removed in a future release.

## Testing

After updating your imports, please run the test suite to ensure everything continues to work as expected.
EOF

echo -e "${GREEN}Added migration documentation.${NC}"

echo -e "${GREEN}Backend reorganization completed successfully!${NC}"
echo -e "${GREEN}Next steps:${NC}"
echo -e "${YELLOW}1. Review the changes to ensure everything is correct${NC}"
echo -e "${YELLOW}2. Run tests to ensure nothing is broken${NC}"
echo -e "${YELLOW}3. Update import statements in the codebase${NC}"
echo -e "${YELLOW}4. After a sufficient deprecation period, remove the backward compatibility modules${NC}" 