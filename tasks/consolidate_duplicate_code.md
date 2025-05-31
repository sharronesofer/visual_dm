# Task: Consolidate Duplicate Code in VDM Project

**Priority:** High

## Description
The VDM project has accumulated duplicate code across multiple directories, including redundant manager classes, duplicate singleton implementations, and parallel code structures. This task involves using the scripts we created to identify and merge these duplicates into a consolidated structure.

## Dependencies
None

## Implementation Details

### Preparation
1. Ensure all scripts in the `/scripts` directory are executable:
   ```bash
   chmod +x scripts/backup_project.sh scripts/restructure_directories.sh scripts/*.py
   ```

### Execution Steps
Follow these steps in sequence:

#### Step 1: Create a Backup
```bash
cd /Users/Sharrone/Visual_DM
bash scripts/backup_project.sh
```
- Verify that the backup was created in the `/backups` directory
- Note the timestamp of the backup for reference

#### Step 2: Find Duplicate C# Files
```bash
cd /Users/Sharrone/Visual_DM
python scripts/find_duplicate_cs_files.py
```
- Review the generated report at `scripts/duplicate_cs_files.txt`
- Verify that the identified duplicates are correct
- Note any potential issues or false positives

#### Step 3: Find Duplicate Python Modules
```bash
cd /Users/Sharrone/Visual_DM
python scripts/find_duplicate_python_modules.py
```
- Review the generated report at `scripts/duplicate_python_modules.txt`
- Verify that the identified duplicates are correct
- Note any potential issues or false positives

#### Step 4: Merge Duplicates
```bash
cd /Users/Sharrone/Visual_DM
python scripts/merge_duplicates.py
```
- Review the merge report at `scripts/merge_report.txt`
- Verify that the consolidated files were created correctly in:
  - C# files: `/VDM/Assets/VisualDM/Consolidated/`
  - Python files: `/backend/core/`
- Manually check a sample of the consolidated files to ensure they contain all necessary functionality

#### Step 5: Update References
```bash
cd /Users/Sharrone/Visual_DM
python scripts/update_references.py
```
- Review the reference update report at `scripts/reference_update_report.txt`
- Verify that references were updated correctly
- Check for any failed updates that might need manual intervention

#### Step 6: Restructure Directories
```bash
cd /Users/Sharrone/Visual_DM
bash scripts/restructure_directories.sh
```
- Review the temporary directory structure at `/VDM/Temp/ConsolidationTemp`
- If satisfied with the restructuring, manually apply it to the project

### Post-Consolidation Tasks
After running the scripts:

1. Open the Unity project and allow it to rebuild references
2. Run the Python backend to verify functionality
3. Fix any remaining reference issues manually
4. Update import statements and references as needed
5. Remove unused or duplicate files from the project
6. Update Unity references to use the consolidated prefabs and scenes
7. Document the "source of truth" for each system in the Wiki or documentation

## Test Strategy

### Unity Project Testing
1. Open the Unity project and verify it compiles without errors
2. Run the game and verify basic functionality
3. Test specific functionalities that involve the consolidated components:
   - Entity Management
   - Event System
   - Time Management
   - World Generation
   - Mod Data Management
4. Verify that prefabs and scenes are still functioning correctly

### Backend Testing
1. Run the backend server
2. Verify API endpoints function correctly
3. Test specific functionalities that involve the consolidated modules
4. Perform integration tests between Unity and the backend

### Validation Criteria
- No compile errors in Unity project
- No runtime errors during gameplay
- No errors when running the backend server
- All functionality works the same as before consolidation
- Project size should be smaller due to removal of duplicate code

## Notes
- If issues arise during any step, restore from the backup created in Step 1
- Keep detailed notes of any manual changes made during the consolidation process
- Consider adding comments to the consolidated files to indicate their origin
- Update the project Wiki to document the new structure and "source of truth" locations 