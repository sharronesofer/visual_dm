# Duplicate Code Consolidation Guide

This guide provides detailed instructions on how to use the code consolidation scripts for the Visual DM project.

## Overview

The Visual DM project has accumulated duplicate code over time, causing maintenance challenges and inconsistent behavior. This set of scripts helps identify, analyze, and consolidate duplicate code into a cleaner structure with a single "source of truth" for each component.

## Prerequisites

- Python 3.6+
- Bash shell environment
- rsync (for backup)
- Access to the Visual DM project repository

## Getting Started

1. Clone or download the Visual DM repository
2. Navigate to the root directory of the project
3. Make sure all scripts in the `scripts` directory are executable:
   ```bash
   chmod +x scripts/*.sh
   ```

## Step 1: Create a Backup

Before making any changes, create a backup of the entire project:

```bash
./scripts/backup_project.sh /path/to/Dreamforge
```

This will create a timestamped backup in `/path/to/Dreamforge/backups/full_backup_{timestamp}`.

## Step 2: Find Duplicate C# Files

Run the duplicate C# files finder to analyze the codebase for duplicated C# code:

```bash
python3 scripts/find_duplicate_cs_files.py /path/to/Dreamforge/VDM/Assets /path/to/Dreamforge/scripts/cs_duplicates_report.json
```

This will generate two files:
- `cs_duplicates_report.json` - Detailed JSON report of all duplicates found
- `cs_duplicates_report.txt` - Human-readable version of the report

The script identifies these types of duplicates:
- Exact duplicates (identical file content)
- Class duplicates (same class name in different files)
- Singleton duplicates (different singleton implementations)
- Manager duplicates (e.g., multiple "TimeManager" implementations)
- Similar files (high code similarity but not identical)

## Step 3: Find Duplicate Python Modules

Run the duplicate Python modules finder to analyze Python code:

```bash
python3 scripts/find_duplicate_python_modules.py /path/to/Dreamforge/backend /path/to/Dreamforge/scripts/py_duplicates_report.json
```

This will generate:
- `py_duplicates_report.json` - Detailed JSON report of Python duplicates
- `py_duplicates_report.txt` - Human-readable version of the report

The script identifies these types of duplicates:
- Exact duplicates (identical module content)
- Module duplicates (similar functionality in different modules)
- Similar files (modules with similar code but not identical)
- Function duplicates (similar functions across different modules)

## Step 4: Merge Duplicates

After analyzing the duplicates, use the merge script to create a merge plan:

```bash
python3 scripts/merge_duplicates.py /path/to/Dreamforge/scripts/cs_duplicates_report.json /path/to/Dreamforge/scripts/py_duplicates_report.json /path/to/Dreamforge /path/to/Dreamforge/scripts/consolidation
```

This will:
1. Analyze the duplicate reports
2. Determine the best file to keep for each set of duplicates
3. Generate a merge plan in `scripts/consolidation/merge_plan.json` and `scripts/consolidation/merge_plan.txt`

**Important:** By default, this script runs in "dry-run" mode and won't make any changes. Review the merge plan carefully before proceeding.

To execute the merge plan (after reviewing):

```bash
python3 scripts/merge_duplicates.py /path/to/Dreamforge/scripts/cs_duplicates_report.json /path/to/Dreamforge/scripts/py_duplicates_report.json /path/to/Dreamforge /path/to/Dreamforge/scripts/consolidation --execute
```

This will:
1. Create backups of all affected files
2. Copy the "best" version of each file to its new location
3. Add deprecation notices to files that should no longer be used
4. Log all operations performed

## Step 5: Update References

After merging duplicates, update references throughout the codebase:

```bash
python3 scripts/update_references.py --project-root=/path/to/Dreamforge --merge-report=/path/to/Dreamforge/scripts/consolidation/merge_plan.json --dry-run
```

Review the output to ensure the updates look correct. Then run without the `--dry-run` flag:

```bash
python3 scripts/update_references.py --project-root=/path/to/Dreamforge --merge-report=/path/to/Dreamforge/scripts/consolidation/merge_plan.json
```

This will:
1. Create backups of all modified files
2. Update references in C# files (namespace imports, class references, etc.)
3. Update references in Python files (import statements, module references)
4. Generate a reference update report

## Step 6: Restructure Directories

Finally, restructure the directories to provide a cleaner organization:

```bash
./scripts/restructure_directories.sh /path/to/Dreamforge
```

This will:
1. Create a consolidated directory structure
2. Move files according to the merge plan
3. Create appropriate meta files for Unity
4. Clean up deprecated or empty directories
5. Generate a directory restructuring summary

## Verifying the Consolidation

After running all scripts, verify the consolidation:

1. Check the generated reports in the `scripts` directory
2. Ensure Unity can still build the project without errors
3. Run any existing automated tests
4. Manually verify key functionality

If any issues are found, you can restore from the backup created in Step 1.

## Generated Reports

The consolidation process generates several reports to help track and verify the changes:

- `cs_duplicates_report.txt` - Analysis of duplicate C# files
- `py_duplicates_report.txt` - Analysis of duplicate Python modules
- `merge_plan.txt` - Plan for merging duplicate files
- `reference_update_report.txt` - Summary of reference updates
- `directory_restructure_summary.md` - Summary of directory restructuring

## Tips and Troubleshooting

- **Unity Meta Files**: The scripts preserve and generate `.meta` files for Unity assets to maintain asset references.
- **Manual Verification**: Always manually verify key functionality after consolidation.
- **Incremental Approach**: Consider running the consolidation on one system at a time (e.g., just manager classes first) if you want a more incremental approach.
- **Version Control**: Commit changes after each major step to allow for more granular rollback if needed.
- **Dependencies**: Some scripts depend on the output of previous scripts, so run them in the order specified.

## Additional Options

Each script provides additional options for customizing the consolidation process:

### find_duplicate_cs_files.py
- Controls for similarity threshold
- Detailed analysis of specific patterns

### find_duplicate_python_modules.py
- Module naming pattern detection
- Function similarity analysis

### merge_duplicates.py
- Custom weighting for selection criteria
- Directory-specific preservation rules
- Handling of conflicting changes

### update_references.py
- C# only or Python only updates
- Detailed logging of each reference change
- Namespace mapping options

### restructure_directories.sh
- Custom directory structure options
- Special handling for specific file types
- Unity-specific organization options

See each script's help text for detailed information:

```bash
python3 scripts/script_name.py --help
```

## Conclusion

Following this process should result in a significantly cleaner, more maintainable codebase with clear "sources of truth" for all components. The consolidation reduces technical debt and sets the foundation for more efficient future development. 