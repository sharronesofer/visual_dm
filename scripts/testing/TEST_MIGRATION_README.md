# Visual DM Test Migration

This repository previously had test files located in two places:

1. **Original location**: Inside each system's directory (e.g., `backend/systems/analytics/tests/`)
2. **Centralized location**: In the main test directory (e.g., `backend/tests/systems/analytics/`)

## Migration Process

We've created a script to systematically handle the migration of test files to maintain a consistent test structure:

1. **Identify test files** in system-specific test directories
2. **Compare files** to see if they're already duplicated in the centralized test structure
3. **Migrate or remove** test files as needed
4. **Update documentation** and add notices about relocated files

## Migration Script

The included `migrate_test_files.sh` script automates this process and:

- Compares files to ensure they're identical before removing any source files
- Generates a detailed log of all actions in markdown format
- Creates README files documenting the test structure
- Leaves notices in original locations explaining where files moved

## Usage

To run the migration:

```bash
# Make the script executable
chmod +x migrate_test_files.sh

# Run the script
./migrate_test_files.sh
```

## Migration Results

The script generates a detailed log file `test_migration_log.md` that captures all actions taken during the migration process.

## Why Centralize Tests?

Centralizing the test files offers several benefits:

1. **Easier test discovery** - All tests are in a consistent location
2. **Simplified CI/CD** - Test runners can target a single directory structure
3. **Better organization** - Tests are organized by system but kept separate from implementation
4. **Reduced duplication** - No need to maintain tests in multiple locations 