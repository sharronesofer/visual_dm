# Unity Consolidation Tools

This directory contains utilities for Unity asset reorganization and code consolidation for the Visual DM project.

## Overview

These tools help you identify, analyze, and safely consolidate duplicated functionality in the Visual DM Unity project, as well as reorganize the project's assets according to the consolidation plan documented in `docs/Unity_Consolidation_Plan.md`.

## Prerequisites

- Python 3.6+
- Unity 2020.3+ project
- Backup of project before running tools

## Tool Descriptions

### 1. Unity Consolidation Helper (`unity_consolidation_helper.py`)

**Purpose**: Analyzes the codebase to identify duplicate implementations, circular dependencies, and static references.

**Features**:
- Scans the entire Unity project for C# scripts
- Identifies duplicate class implementations
- Detects circular dependencies between classes
- Finds static references that may cause issues during consolidation
- Generates detailed reports for review

**Usage**:
```bash
python unity_consolidation_helper.py --project-path ../VDM --output-dir analysis_results
```

**Arguments**:
- `--project-path`: Path to the Unity project (default: `../VDM`)
- `--output-dir`: Directory to store analysis reports (default: `analysis_results`)
- `--detailed`: Generate detailed reports with code snippets
- `--scan-deps`: Perform deep dependency scanning (slower but more thorough)
- `--target-patterns`: Comma-separated list of patterns to specifically target (e.g., `GameLoader,Manager`)

### 2. Unity Asset Reorganizer (`unity_asset_reorganizer.py`)

**Purpose**: Reorganizes Unity assets according to the consolidation plan, moving files to their new locations and updating references.

**Features**:
- Creates backups before moving files
- Preserves meta files and GUIDs to maintain Unity references
- Updates script references in prefabs, scenes, and other assets
- Handles C# namespace changes
- Provides rollback capability if issues occur

**Usage**:
```bash
python unity_asset_reorganizer.py --project-path ../VDM --config consolidation_config.json --backup
```

**Arguments**:
- `--project-path`: Path to the Unity project (default: `../VDM`)
- `--config`: Path to configuration file defining the file moves (default: `consolidation_config.json`)
- `--backup`: Create backups before moving files (recommended)
- `--dry-run`: Show what would happen without making changes
- `--skip-meta`: Skip moving meta files (not recommended)
- `--rollback`: Restore from the last backup

**Configuration File Example**:
```json
{
  "file_moves": [
    {
      "source": "Assets/Scripts/VisualDM/Networking/NetworkManager.cs",
      "destination": "Assets/Scripts/Networking/API/RestApiClient.cs",
      "update_namespaces": true,
      "rename_class": "RestApiClient"
    },
    {
      "source": "Assets/VisualDM/Systems/EventManager.cs",
      "destination": "Assets/Scripts/Systems/Events/EventManager.cs",
      "update_namespaces": true
    }
  ]
}
```

### 3. Bootstrap Scene Updater (`update_bootstrap_scene.py`)

**Purpose**: Updates the Bootstrap.unity scene to use the consolidated components after reorganization.

**Features**:
- Automatically updates GameObject references to consolidated scripts
- Handles component renames
- Creates backups of scenes before modification
- Validates references before and after changes

**Usage**:
```bash
python update_bootstrap_scene.py --project-path ../VDM --scene-path Assets/Scenes/Bootstrap.unity
```

**Arguments**:
- `--project-path`: Path to the Unity project (default: `../VDM`)
- `--scene-path`: Path to the Bootstrap scene (default: `Assets/Scenes/Bootstrap.unity`)
- `--backup`: Create backup before modifying (default: `True`)
- `--dry-run`: Show what would happen without making changes
- `--validate`: Validate references after update

## Workflow for Consolidation

Follow these steps to safely consolidate your Unity project:

1. **Analysis Phase**
   ```bash
   python unity_consolidation_helper.py --project-path ../VDM --output-dir analysis
   ```
   - Review the reports in the `analysis` directory
   - Identify which components need to be consolidated

2. **Backup Your Project**
   - Always create a full backup of your Unity project before proceeding
   - Version control (git) is also highly recommended

3. **Create a Consolidation Configuration**
   - Create a JSON file mapping source files to their destinations
   - Include class rename info where needed
   - See example above or the `consolidation_config_example.json` file

4. **Dry Run the Asset Reorganizer**
   ```bash
   python unity_asset_reorganizer.py --project-path ../VDM --config my_config.json --dry-run
   ```
   - Review the output to ensure it looks correct

5. **Execute the Asset Reorganization**
   ```bash
   python unity_asset_reorganizer.py --project-path ../VDM --config my_config.json --backup
   ```

6. **Update the Bootstrap Scene**
   ```bash
   python update_bootstrap_scene.py --project-path ../VDM
   ```

7. **Validate Your Changes**
   - Open the Unity project
   - Resolve any compilation errors
   - Test the core functionality
   - If issues occur, use the rollback feature:
     ```bash
     python unity_asset_reorganizer.py --project-path ../VDM --rollback
     ```

## Best Practices

1. **Always Make Backups**
   - Use the `--backup` flag with all tools
   - Keep a full project copy before starting

2. **Use Dry Run First**
   - Run tools with `--dry-run` to preview changes
   - Verify the expected outputs before making changes

3. **Incremental Consolidation**
   - Consolidate one component at a time
   - Test thoroughly after each consolidation
   - Commit changes to version control after successful consolidation

4. **Unity Editor Considerations**
   - Close Unity before running major reorganizations
   - After reorganization, let Unity fully import all assets
   - Clear the Library folder if references are still broken after reimport

5. **Handle Special Cases**
   - Some assets may require manual intervention
   - Pay special attention to Prefabs, ScriptableObjects, and Scene references
   - Update UI references manually if automatic updates fail

## Troubleshooting

### Missing References After Consolidation
- Check if GUID preservation worked correctly
- Look for namespace mismatches in scripts
- Check if Unity has reimported all assets

### Script Compilation Errors
- Verify namespace changes in your configuration
- Look for scripts with hardcoded type names
- Check for serialized fields that need manual updating

### Scene Corruption
- Restore from backup
- Use the `--validate` flag with `update_bootstrap_scene.py`
- Consider manually updating critical scenes

## Additional Resources

- See complete consolidation plan in `docs/Unity_Consolidation_Plan.md`
- Unity documentation on [Script Serialization](https://docs.unity3d.com/Manual/script-Serialization.html)
- Unity Asset Database overview for reference management 