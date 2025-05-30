# Asset Bundle System

This document provides an overview of the Asset Bundle system in Visual DM, explaining how to create, load, and use asset bundles for modding.

## Overview

The Asset Bundle system provides a way to load external assets (sprites, textures, models, etc.) at runtime. This is particularly useful for implementing mods that can add new visual content to the game without requiring the core game code to be modified.

The system consists of the following components:

1. **AssetBundleManager**: Manages the loading, caching, and unloading of asset bundles.
2. **AssetReference**: A reference to a specific asset within a bundle.
3. **SpriteLoader**: A helper class for working with sprite assets.
4. **AssetBundleManagerWindow**: An editor window for creating and managing asset bundles.

## Creating Asset Bundles

### Using the Asset Bundle Manager Window

1. Open the Asset Bundle Manager window by selecting `VisualDM > Asset Bundle Manager` from the menu bar.
2. Create a new bundle by entering a name and clicking "Create Bundle".
3. Drag and drop assets (textures, sprites, etc.) onto the drop area to add them to the bundle.
4. Configure the build options as needed.
5. Click "Build All Bundles" to build the asset bundles.
6. The bundles will be built to the specified output path, and optionally copied to the StreamingAssets folder.

### Programmatically Creating Asset Bundles

You can also create asset bundles through code by setting the `assetBundleName` property in the asset importer:

```csharp
AssetImporter importer = AssetImporter.GetAtPath("Assets/Path/To/Asset.png");
importer.assetBundleName = "my_bundle";
importer.SaveAndReimport();
```

## Using Asset Bundles

### Loading Asset Bundles

You can load asset bundles using the `AssetBundleManager` class:

```csharp
// Get the AssetBundleManager instance
var bundleManager = VisualDM.Systems.AssetBundleManager.Instance;

// Load a bundle
AssetBundle bundle = bundleManager.LoadAssetBundle("my_bundle");

// Or load a bundle asynchronously
AssetBundle bundle = await bundleManager.LoadAssetBundleAsync("my_bundle");
```

### Loading Assets from Bundles

Once a bundle is loaded, you can load assets from it:

```csharp
// Load a sprite from a bundle
Sprite sprite = bundleManager.LoadAsset<Sprite>("my_bundle", "my_sprite");

// Load a sprite asynchronously
Sprite sprite = await bundleManager.LoadAssetAsync<Sprite>("my_bundle", "my_sprite");
```

### Using AssetReference

The `AssetReference` class provides a convenient way to reference assets within bundles:

```csharp
// Create an asset reference
AssetReference reference = new AssetReference("my_bundle", "my_sprite");

// Load the asset
Sprite sprite = reference.LoadAsset<Sprite>();

// Load the asset asynchronously
Sprite sprite = await reference.LoadAssetAsync<Sprite>();
```

### Using SpriteLoader

The `SpriteLoader` class provides a simplified API for working with sprite assets:

```csharp
// Get the SpriteLoader instance
var spriteLoader = VisualDM.Systems.SpriteLoader.Instance;

// Register a sprite
spriteLoader.RegisterSprite("player_icon", "my_bundle", "player_sprite");

// Load the sprite
Sprite sprite = spriteLoader.LoadSprite("player_icon");

// Load the sprite asynchronously
Sprite sprite = await spriteLoader.LoadSpriteAsync("player_icon");
```

### Using the GameManager

The `GameManager` provides helper methods for working with asset bundles:

```csharp
// Load a mod asset bundle
GameManager.Instance.LoadModAssetBundle("my_mod", "my_bundle");

// Register a mod sprite
GameManager.Instance.RegisterModSprite("my_mod", "player_icon", "my_bundle", "player_sprite");

// Load a sprite
Sprite sprite = GameManager.Instance.LoadSprite("player_icon");
```

## Unloading Asset Bundles

When you're done with an asset bundle, you should unload it to free up memory:

```csharp
// Unload a bundle
bundleManager.UnloadAssetBundle("my_bundle", false);

// Unload all bundles
bundleManager.UnloadAllAssetBundles(false);

// Unload all bundles for a specific mod
bundleManager.UnloadModBundles("my_mod", false);
```

The second parameter (`unloadAllLoadedObjects`) determines whether to unload all assets that were loaded from the bundle. If set to `true`, any assets that were loaded from the bundle will become invalid.

## Mod Integration

The asset bundle system is designed to work with mods. When creating a mod, you should:

1. Create asset bundles for your mod's assets.
2. Place the asset bundles in a location where they can be loaded by the game.
3. Register the asset bundles with the `AssetBundleManager` using the `RegisterModBundle` method.
4. Register your mod's sprites with the `SpriteLoader` using the `RegisterSprite` method.

When your mod is unloaded, you should:

1. Unload your mod's asset bundles using the `UnloadModBundles` method.
2. Unregister your mod's sprites using the `UnregisterModSprites` method.

## Directory Structure

By default, asset bundles are stored in the following locations:

- **Base game bundles**: `[StreamingAssets]/AssetBundles/`
- **Mod bundles**: `[PersistentDataPath]/Mods/AssetBundles/`

This structure allows the game to distinguish between base game assets and mod assets, and ensures that mod assets can be loaded and unloaded independently of the base game assets.

## Performance Considerations

- Asset bundles are cached in memory, so loading the same bundle multiple times won't cause multiple copies to be loaded.
- Assets loaded from bundles are also cached, so loading the same asset multiple times is efficient.
- Unloading bundles with `unloadAllLoadedObjects = true` will free up memory, but any objects that were loaded from the bundle will become invalid.
- Asynchronous loading methods should be used for large bundles to avoid blocking the main thread.
- The `AssetBundleManager` uses reference counting to track bundle usage, so a bundle won't be unloaded until all references to it are released.

## Troubleshooting

- If an asset can't be loaded, check that the bundle name and asset name are correct.
- If a bundle can't be loaded, check that the bundle file exists in the correct location.
- If you're getting errors when loading assets, check that the asset type is correct.
- If you're getting "missing script" errors, make sure all required scripts are included in the bundle or are part of the base game.

## Example: Loading a Mod Bundle

Here's a complete example of loading a mod bundle and using its assets:

```csharp
// Load the mod bundle
bool success = GameManager.Instance.LoadModAssetBundle("myMod", "my_mod_bundle");
if (!success)
{
    Debug.LogError("Failed to load mod bundle");
    return;
}

// Register sprites from the bundle
GameManager.Instance.RegisterModSprite("myMod", "character_icon", "my_mod_bundle", "character_sprite");
GameManager.Instance.RegisterModSprite("myMod", "item_icon", "my_mod_bundle", "item_sprite");

// Load and use a sprite
Sprite characterSprite = GameManager.Instance.LoadSprite("character_icon");
if (characterSprite != null)
{
    // Use the sprite
    spriteRenderer.sprite = characterSprite;
}

// When done with the mod, unload its bundles
GameManager.Instance.UnloadModAssetBundles("myMod");
```

This system provides a flexible and efficient way to load and use external assets in Visual DM, enabling modders to add new visual content to the game without modifying the core game code. 