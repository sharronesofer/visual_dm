#!/bin/bash
echo "🔄 Forcing Unity project refresh..."

# Remove all Unity caches and temp files
echo "Removing Unity caches..."
rm -rf Library/PackageCache
rm -rf Library/Artifacts  
rm -rf Library/ScriptAssemblies
rm -rf Library/ShaderCache
rm -rf Library/metadata
rm -rf Library/AssetImportState
rm -rf Library/SourceAssetDB
rm -rf Library/BuildPlayerData
rm -rf Temp/

# Remove lock files
echo "Removing lock files..."
rm -f Packages/packages-lock.json

# Force meta file regeneration
echo "Cleaning meta files..."
find Assets -name "*.meta" -delete

echo "✅ Unity project refresh complete!"
echo "📝 Next steps:"
echo "1. Close Unity completely (if open)"
echo "2. Reopen Unity project"
echo "3. Unity will automatically reimport everything"
echo "4. Check console for compilation success" 