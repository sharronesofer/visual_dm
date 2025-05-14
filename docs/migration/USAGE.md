# TypeScript to Python Migration Tools Usage Guide

This guide explains how to use the migration tools to continue the TypeScript to Python conversion process and address the remaining issues.

## Prerequisites

Before using these tools, ensure you have:

1. Python 3.8+ installed
2. Required Python packages installed via:
   ```
   pip install -r requirements.txt
   ```
3. Sufficient disk space for the conversion process

## Migration Workflow

### 1. Complete Migration Process

To run the entire migration process from start to finish:

```bash
./scripts/run_complete_migration.sh
```

This script:
- Analyzes TypeScript dependencies
- Converts TypeScript files to Python
- Applies post-processing fixes
- Tests the converted modules
- Integrates with the existing codebase
- Generates a final report

### 2. Individual Tool Usage

#### TypeScript Dependency Analysis

```bash
python scripts/analyze_ts_dependencies.py --src-dir <source_directory> --output <output_file.json>
```

#### TypeScript to Python Conversion

```bash
python scripts/ts2py.py --input <typescript_file.ts> --output <python_file.py>
```

For batch conversion:

```bash
python scripts/ts2py.py --batch-file <batch_config.json>
```

#### Post-Processing Fixes

```bash
python scripts/fix_py_conversions.py --dir <python_directory>
```

#### Module Integration

```bash
python scripts/integrate_py_modules.py --source-dir <converted_directory> --target-dir <backend_directory>
```

Use `--dry-run` to see changes without applying them.

#### Testing Converted Modules

```bash
python scripts/test_converted_modules.py --modules-dir <directory_with_modules>
```

Options:
- `--run-mypy`: Run static type checking (default: true)
- `--run-lint`: Run linting with flake8 (default: true)
- `--run-tests`: Run pytest unit tests (default: true)
- `--report-file`: Save results to a JSON file

#### Finalization

```bash
python scripts/finalize_ts_migration.py --converted-dir <converted_directory>
```

## Addressing Common Issues

### Import Errors

The primary source of errors is import resolution. To address these:

1. Create `__init__.py` files in all directories to ensure proper Python module structure:
   ```bash
   find backend/app -type d -exec touch {}/__init__.py \;
   ```

2. For JavaScript/TypeScript libraries without Python equivalents:
   - Create stub modules in the Python codebase
   - Use Python alternatives (e.g., replace React with FastAPI templates)
   - Mock dependencies for testing

### Linting Issues

To fix linting issues automatically:

```bash
# Install black and isort if not already installed
pip install black isort

# Format Python code
black backend/app --exclude node_modules
isort backend/app --profile black --skip node_modules
```

## Batch Management

To create new batch configurations for remaining files:

1. Edit `scripts/ts_conversion/remaining_batches.json`
2. Add new batch entries following the existing pattern:
   ```json
   {
     "name": "batch_name",
     "description": "Batch description",
     "source_dir": "path/to/source",
     "files": ["**/*.ts"],
     "excludes": ["**/*.spec.ts"],
     "target_dir": "python_converted/batch_output_dir",
     "dependencies": ["other_module_paths"]
   }
   ```

## Templates

Use the provided templates when creating new Python modules:

- Module template: `scripts/templates/module_template.py`
- Test template: `scripts/templates/test_template.py`

## Monitoring Progress

Track conversion progress in the logs directory:

```bash
ls -la logs/migration/
```

The latest conversion report is available at:

```
docs/migration/conversion_status_report.md
```

## Getting Help

If you encounter issues:

1. Check the logs in `logs/migration/`
2. Refer to the comprehensive migration plan in `docs/typescript_to_python_migration_plan.md`
3. Review the Python migration guide at `docs/python_migration_guide.md`

## Next Steps

After completing the initial conversion:

1. Fix import errors systematically by module/directory
2. Implement a testing strategy for converted modules
3. Run formatting and linting fixes
4. Begin phased replacement of TypeScript modules with their Python equivalents 