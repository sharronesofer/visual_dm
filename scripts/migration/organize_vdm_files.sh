#!/bin/bash

# Script to organize files in the VDM root directory

echo "===== VDM File Organization Script ====="
echo "This script will organize the scattered files in the VDM root directory."
echo

# Check if the VDM directory exists
if [ ! -d "VDM" ]; then
    echo "Error: VDM directory does not exist."
    exit 1
fi

# Create directories if they don't exist
echo "1. Creating organization directories..."
mkdir -p "VDM/ProjectFiles"

echo "   Created VDM/ProjectFiles for project-related files"

# Move project files to the ProjectFiles directory
echo "2. Moving project files to ProjectFiles directory..."
mv VDM/*.csproj VDM/ProjectFiles/ 2>/dev/null
mv VDM/*.sln VDM/ProjectFiles/ 2>/dev/null

# Count files moved
PROJECT_FILES_COUNT=$(find VDM/ProjectFiles -type f | wc -l)
echo "   Moved ${PROJECT_FILES_COUNT} project files to ProjectFiles directory"

# Move crash logs to Logs directory
echo "3. Moving crash logs to Logs directory..."
mkdir -p "VDM/Logs/CrashLogs"
mv VDM/mono_crash*.json VDM/Logs/CrashLogs/ 2>/dev/null

# Count crash logs moved
CRASH_LOGS_COUNT=$(find VDM/Logs/CrashLogs -type f | wc -l)
echo "   Moved ${CRASH_LOGS_COUNT} crash logs to Logs/CrashLogs directory"

# List remaining files in the VDM root
REMAINING_FILES=$(find VDM -maxdepth 1 -type f -not -name "README.md" | wc -l)

if [ $REMAINING_FILES -gt 0 ]; then
    echo
    echo "4. Remaining files in VDM root directory:"
    find VDM -maxdepth 1 -type f -not -name "README.md" | sort
    echo
    echo "   You may want to review these files manually to determine where they should go."
else
    echo
    echo "4. No other files remain in the VDM root directory except README.md."
fi

echo
echo "Organization completed successfully."

# Create a symbolic link to the solution file for convenience
echo "5. Creating symbolic link to the solution file in the VDM root for convenience..."
SOLUTION_FILE=$(find VDM/ProjectFiles -name "*.sln" | head -1)

if [ -n "$SOLUTION_FILE" ]; then
    SOLUTION_BASENAME=$(basename "$SOLUTION_FILE")
    ln -sf "ProjectFiles/$SOLUTION_BASENAME" "VDM/$SOLUTION_BASENAME"
    echo "   Created symbolic link for $SOLUTION_BASENAME in VDM root"
else
    echo "   No solution file found to create symbolic link"
fi

echo
echo "VDM files have been organized successfully!"
echo "- Project files (.csproj, .sln) are now in VDM/ProjectFiles/"
echo "- Crash logs (mono_crash*.json) are now in VDM/Logs/CrashLogs/"
echo "- README.md remains in the VDM root"
echo "- A symbolic link to the solution file was created in the VDM root"

exit 0 