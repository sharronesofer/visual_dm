# Backend Cleanup Plan

## Directory Analysis

Based on our analysis, we've identified several duplicate folder structures in the codebase:

1. **API folders**
   - `backend/api` - imported in test_imports.py
   - `backend/src/api` - imported in app.py with "from src.api..."
   - `backend/archive/api2` - already archived

2. **Core folders**
   - `backend/core` - appears to be referenced directly
   - `backend/src/core` - imports like "from src.core" exist
   - `backend/archive/core2` - already archived

3. **Services folders**
   - `backend/services` - imported in test_imports.py
   - `backend/src/services` - imported with "from src.services"
   - `backend/archive/services2` - already archived

4. **Tests folders**
   - `backend/tests` - primary test location
   - `backend/archive/tests2` - already archived

5. **Utils folders**
   - `backend/utils` - imported in test_imports.py
   - `backend/src/utils` - doesn't appear to be imported
   - `backend/archive/utils` - already archived

## Cleanup Approach

1. **Backup Strategy**
   - Create a full backup of the backend directory before making any changes
   - Test imports after each consolidation to ensure functionality

2. **Consolidation Plan**
   - Keep both `src` and top-level folders initially
   - Create a central archive directory for unused folders
   - Gradually migrate imports to use a single consistent pattern

3. **Priority Order**
   - Start with utils (less critical)
   - Then services
   - Then api
   - Then core (most critical)

## Implementation Steps

1. **Initial setup**
   ```bash
   # Create backup
   cp -r backend backend_backup
   # Create archive directory if it doesn't exist
   mkdir -p backend/archive
   ```

2. **Utils consolidation**
   - Check all imports from utils
   - Move unique files from src/utils to utils (or vice versa)
   - Update imports
   - Test functionality

3. **Services consolidation**
   - Follow same pattern as utils

4. **API consolidation**
   - Follow same pattern as utils

5. **Core consolidation**
   - Follow same pattern as utils

6. **Testing**
   - Run tests to ensure nothing broke
   - Fix any import errors

## Next Steps

After consolidation, standardize the import convention across the codebase to prevent future duplication. 