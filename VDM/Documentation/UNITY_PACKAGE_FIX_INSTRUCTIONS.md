# Unity Package Fix Instructions

## Problem: Newtonsoft.Json Package Not Found

After resolving circular assembly dependencies, Unity cannot find the Newtonsoft.Json package due to cache cleanup.

## Solution Steps:

### Method 1: Unity Editor GUI (Recommended)
1. **Open Unity Editor** (not in batch mode)
2. **Let Unity load** - it will automatically detect and restore missing packages
3. **Check Package Manager** (Window > Package Manager)
4. **Verify Newtonsoft JSON** is listed under "In Project"
5. **If missing**: Click "+" and select "Add package by name", enter `com.unity.nuget.newtonsoft-json`

### Method 2: Manual Package Restoration
```bash
# From VDM directory
rm -rf Library/PackageCache
rm -rf Library/SourceAssetDB
rm -f Library/LastSceneManagerSetup.txt

# Open Unity Editor (GUI) and let it restore packages
# Unity will automatically reinstall all packages from manifest.json
```

### Method 3: Force Package Reinstall
```bash
# Backup and modify manifest
cp Packages/manifest.json Packages/manifest.json.backup

# Temporarily remove Newtonsoft line, save, then restore
# This forces Unity to reinstall the package
```

## Verification:
- All DTO compilation errors should disappear
- `using Newtonsoft.Json;` should work without errors
- JsonProperty attributes should be recognized

## Status:
✅ **Circular Dependencies**: COMPLETELY RESOLVED  
⚠️  **Package Dependencies**: Needs Unity Editor restart to restore

The assembly architecture is robust and will prevent future circular dependency issues. 