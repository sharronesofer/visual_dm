# Manual Test File Review Guide

## Background

Our migration script identified numerous test files that exist in both:
1. System-specific test directories (`backend/systems/<system_name>/tests/`)
2. Centralized test structure (`backend/tests/systems/<system_name>/`)

Many of these files have differences that need manual review to determine the correct version to keep.

## Review Process

For each file pair marked for manual review, follow this process:

### 1. Compare File Contents

Use the `diff` tool to compare the files:

```bash
# Basic diff view
diff -u backend/systems/<system_name>/tests/<test_file> backend/tests/systems/<system_name>/<test_file>

# Use a visual diff tool if available
code --diff backend/systems/<system_name>/tests/<test_file> backend/tests/systems/<system_name>/<test_file>
```

### 2. Determine the Authoritative Version

Examine the differences and determine which version should be kept:

* Check file modification dates: `ls -l <file1> <file2>`
* Review git history if available: `git log -p <file>`
* Consider test coverage and functionality
* Look for test improvements, bug fixes, or more comprehensive assertions

### 3. Update the Target File if Needed

If the system-specific version is more up-to-date:

```bash
# Copy the system-specific version to the centralized location
cp -v backend/systems/<system_name>/tests/<test_file> backend/tests/systems/<system_name>/<test_file>
```

### 4. Delete the System-Specific Version

Once you've ensured the centralized version is correct and up-to-date:

```bash
# Remove the system-specific version
rm -v backend/systems/<system_name>/tests/<test_file>
```

### 5. Document the Change

Update the manual review log with the action taken:

```markdown
## <system_name> System

- `<test_file>`: [UPDATED/KEPT] - <brief note about decision>
```

## Testing After Migration

After migrating test files:

1. Run the tests to ensure they still function:
   ```bash
   # Run all tests in the centralized structure
   pytest backend/tests/systems/<system_name>/
   
   # Run a specific test
   pytest backend/tests/systems/<system_name>/<test_file>
   ```

2. Verify imports are correct and no test functionality is lost.

3. Check test coverage to ensure it remains the same or improves:
   ```bash
   pytest --cov=backend.systems.<system_name> backend/tests/systems/<system_name>/
   ```

## Common Issues to Watch For

1. **Import Differences**: The system-specific tests might use relative imports while the centralized tests use absolute imports.

2. **Path References**: Tests might reference test data using different paths based on their location.

3. **Dependencies**: Tests might have different setup/teardown code or fixture dependencies.

4. **Version Drift**: If both versions have been maintained separately, they may have divergent functionality.

## Completion Checklist

For each system, verify:

- [ ] All test files manually reviewed
- [ ] All tests passing in the centralized location
- [ ] System-specific test directory empty or containing only a README
- [ ] Test coverage maintained or improved
- [ ] Documentation updated

## Systems Requiring Review

1. **Analytics System**
2. **Character System**
3. **Combat System**
4. **Crafting System**
5. **Data System**
6. **Dialogue System**
7. **Economy System**
8. **Events System**
9. **Loot System**
10. **Motif System**
11. **POI System**
12. **Quest System**
13. **Rumor System**
14. **Tension/War System**
15. **Time System**
16. **World State System**

## Review Log Template

Start a log file for tracking the manual review process:

```markdown
# Test File Manual Review Log

## Overview

This log tracks the manual review and migration of test files.

## System Reviews

### Analytics System
- `test_analytics_service.py`: IDENTICAL - Kept centralized version
- `test_event_integration.py`: UPDATED - Centralized version updated with latest changes
- ...

### Character System
... 