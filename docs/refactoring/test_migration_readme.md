# Backend Tests Migration Guide

This guide explains the process of migrating backend tests from `backend/systems` to `backend/tests/systems`.

## Overview

The migration process moves all test files (`test_*.py`) from the systems directories to a mirrored structure in the tests directory. The goal is to separate test code from implementation code while maintaining the same organizational structure.

## Migration Scripts

Three Python scripts have been created to assist with this migration:

1. **prepare_test_structure.py**: Creates the necessary directory structure in `backend/tests/systems` mirroring `backend/systems`.
2. **migrate_tests.py**: Finds all test files in `backend/systems`, copies them to the corresponding location in `backend/tests/systems`, and optionally removes the original files.
3. **verify_tests.py**: Runs pytest on each migrated test file to verify that it still works in the new location.

## Migration Process

Follow these steps to migrate the tests:

1. **Prepare the test directory structure**:
   ```bash
   python prepare_test_structure.py
   ```
   This will create all the necessary directories and `__init__.py` files in `backend/tests/systems`.

2. **Migrate the test files**:
   ```bash
   python migrate_tests.py
   ```
   This will copy all test files to their new location and prompt you to confirm removal of the original files.

3. **Verify the migrated tests**:
   ```bash
   python verify_tests.py
   ```
   This will run pytest on each migrated test file to ensure it still works.

## Handling Import Issues

If you encounter import issues after migration, consider the following solutions:

1. **Absolute imports**: Most test files already use absolute imports (e.g., `from backend.systems.X import Y`), which should continue to work after migration.

2. **Relative imports**: If a test file uses relative imports (e.g., `from ..X import Y`), you may need to update these imports to use absolute paths.

3. **Circular imports**: If you encounter circular import issues, consider refactoring the code to break the circular dependency.

4. **Missing modules**: If a test file imports a module that can't be found, check that all necessary `__init__.py` files are in place.

## After Migration

After successfully migrating the tests:

1. Update any CI/CD pipelines to run tests from the new location.
2. Update any documentation or README files to reflect the new test location.
3. Run a full test suite to ensure all tests work together in the new structure.

## Troubleshooting

If you encounter issues during migration:

1. **Import errors**: Check that the test file's imports are correct for the new location.
2. **Missing modules**: Ensure all required modules are available in the Python path.
3. **Fixture issues**: Update fixture paths if they reference files relative to the old location.
4. **Configuration issues**: Check that any test configuration files are properly referenced. 