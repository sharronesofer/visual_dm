#!/bin/bash

echo "🚨 COMPLETE UNITY PROJECT FIX 🚨"
echo "This script will completely reset Unity's package system"
echo ""

# Step 1: Force close Unity if running
echo "Step 1: Checking for running Unity processes..."
if pgrep -f "Unity" > /dev/null; then
    echo "⚠️  Unity is running! Please close Unity completely before continuing."
    echo "Press Enter after closing Unity, or Ctrl+C to cancel"
    read -r
fi

# Step 2: Complete cache cleanup
echo "Step 2: Removing ALL Unity caches..."
rm -rf Library/PackageCache
rm -rf Library/Artifacts  
rm -rf Library/ScriptAssemblies
rm -rf Library/ShaderCache
rm -rf Library/metadata
rm -rf Library/AssetImportState
rm -rf Library/SourceAssetDB
rm -rf Library/BuildPlayerData
rm -rf Library/PlayerDataCache
rm -rf Library/ScriptMapper
rm -rf Library/StateCache
rm -rf Temp/
rm -rf obj/
rm -rf .vs/

# Step 3: Remove all lock and temp files
echo "Step 3: Removing lock files..."
rm -f Packages/packages-lock.json
rm -f *.tmp
rm -f *.log

# Step 4: Clean meta files
echo "Step 4: Regenerating meta files..."
find Assets -name "*.meta" -delete

# Step 5: Create clean project structure
echo "Step 5: Ensuring clean project structure..."
mkdir -p Assets/Scripts/Core/VisualDM/Data
mkdir -p Assets/Scripts/Core/VisualDM/Systems  
mkdir -p Assets/Scripts/Core/VDM/Systems/Population
mkdir -p Assets/Scripts/Core/VDM/Runtime/Region

# Step 6: Reset Unity preferences for this project
echo "Step 6: Resetting Unity project preferences..."
rm -f ProjectSettings/ProjectVersion.txt
rm -f UserSettings/EditorUserSettings.asset 2>/dev/null

echo ""
echo "✅ COMPLETE UNITY FIX FINISHED!"
echo ""
echo "🔧 NEXT STEPS:"
echo "1. Open Unity Hub"
echo "2. Add this project to Unity Hub if not already added"
echo "3. Open the project with Unity 2022.3.62f1"
echo "4. Wait for Unity to completely reimport everything"
echo "5. Check console - should be clean!"
echo ""
echo "If you still get errors, the issue might be:"
echo "- Wrong Unity version (use 2022.3.62f1)"
echo "- Wrong project path in Unity Hub"
echo "- Corrupted Unity installation" 