#!/bin/bash
# Rumor System Refactoring Cleanup

# Remove duplicate files at the root that have been replaced by more robust implementations
rm backend/systems/rumor/service.py
rm backend/systems/rumor/repository.py
rm backend/systems/rumor/rumor_transformer.py

# Remove empty or unused directories
rm -rf backend/systems/rumor/routers
rm -rf backend/systems/rumor/utils
rm -rf backend/systems/rumor/models/repositories

# Add note to REFACTORING.md about completion
echo '
## Refactoring Completed

The rumor system has been refactored to eliminate duplicated functionality. The more robust implementations from services/ and repositories/ directories have been chosen as the canonical ones.' >> backend/systems/rumor/REFACTORING.md

