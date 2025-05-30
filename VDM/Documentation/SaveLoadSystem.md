# Save/Load System Documentation

## Overview

The Save/Load System provides comprehensive game state persistence capabilities for the Visual DM Unity project. It integrates with the existing backend storage infrastructure and supports multiple save slots, auto-save, encryption, and cloud synchronization.

## Architecture

### Components

1. **Unity Components**
   - `SaveLoadService`: Core Unity service managing save/load operations
   - `SaveLoadUI`: UI controller for user interaction
   - `SaveSlotUI`: Individual save slot display component

2. **Backend Components**
   - `save_load_endpoints.py`: FastAPI endpoints for save/load operations
   - Integration with existing `StorageManager` and `EncryptionService`

3. **Data Transfer Objects (DTOs)**
   - `SaveLoadDTO.cs`: Comprehensive DTOs for all save/load operations
   - Covers player data, world state, character data, quest data, inventory, time, and settings

## Features

### Core Features
- **Multiple Save Slots**: Support for up to 10 save slots (configurable)
- **Auto-Save**: Configurable automatic saving at specified intervals
- **Manual Save/Load**: User-initiated save and load operations
- **Save File Management**: List, delete, and manage save files
- **Progress Indication**: Real-time progress feedback during operations

### Advanced Features
- **Encryption**: AES-256 encryption for save files (when enabled)
- **Cloud Synchronization**: Integration with cloud storage systems
- **Integrity Validation**: Checksum validation and corruption detection
- **Version Management**: Save file versioning and migration support
- **Local Backup**: Offline backup system for save files

## Usage

### Basic Usage

```csharp
// Get the SaveLoadService instance
SaveLoadService saveLoadService = FindObjectOfType<SaveLoadService>();

// Save game
await saveLoadService.SaveGameAsync("MyGameSave", "Save before boss battle");

// Load game
await saveLoadService.LoadGameAsync("MyGameSave");

// Get list of saves
SaveGameMetadataDTO[] saves = await saveLoadService.GetSaveListAsync();

// Delete a save
await saveLoadService.DeleteSaveAsync("MyGameSave");
```

### UI Integration

```csharp
// Get the SaveLoadUI instance
SaveLoadUI saveLoadUI = FindObjectOfType<SaveLoadUI>();

// Show save/load panel
saveLoadUI.ShowSaveLoadPanel();

// Quick save
saveLoadUI.QuickSave();

// Quick load (loads most recent save)
saveLoadUI.QuickLoad();
```

### Event Handling

```csharp
// Listen for save/load events
saveLoadService.OnSaveCompleted += (success) => {
    if (success) {
        Debug.Log("Save completed successfully!");
    } else {
        Debug.LogError("Save failed!");
    }
};

saveLoadService.OnLoadCompleted += (success) => {
    if (success) {
        Debug.Log("Load completed successfully!");
    } else {
        Debug.LogError("Load failed!");
    }
};

saveLoadService.OnSaveProgress += (progress) => {
    Debug.Log($"Save progress: {progress * 100:F0}%");
};
```

## Configuration

### Unity Inspector Settings

The `SaveLoadService` can be configured via the Unity Inspector:

- **Enable Auto Save**: Toggle automatic saving
- **Auto Save Interval**: Time between auto-saves (in minutes)
- **Max Save Slots**: Maximum number of save slots
- **Enable Cloud Sync**: Enable/disable cloud synchronization
- **Enable Encryption**: Enable/disable save file encryption

### Runtime Configuration

```csharp
// Configure auto-save
saveLoadService.SetAutoSaveConfig(true, 5.0f); // Enable, every 5 minutes

// Check if operation is in progress
bool inProgress = saveLoadService.IsOperationInProgress;
```

## Data Structure

### Game Save Data

The save system captures comprehensive game state:

```csharp
GameSaveDataDTO saveData = new GameSaveDataDTO
{
    Version = 1,
    PlayerData = new PlayerSaveDataDTO
    {
        PlayerId = "player123",
        Level = 25,
        Experience = 50000,
        Position = new Vector3DTO(100, 0, 200),
        Health = 95.5f,
        MaxHealth = 100f
    },
    WorldState = new WorldSaveDataDTO
    {
        WorldId = "main_world",
        Seed = "random_seed_123",
        GlobalFlags = new Dictionary<string, bool>
        {
            { "intro_completed", true },
            { "boss_defeated", false }
        }
    },
    CharacterData = characterData,
    QuestData = questData,
    InventoryData = inventoryData,
    TimeData = timeData,
    SettingsData = settingsData
};
```

## Backend Integration

### API Endpoints

The system uses the following backend endpoints:

- `POST /api/world-state/save` - Save game state
- `POST /api/world-state/load` - Load game state
- `GET /api/world-state/saves` - List save files
- `DELETE /api/world-state/save/{slot_name}` - Delete save file
- `POST /api/world-state/validate` - Validate save file integrity

### Database Schema

Save files are stored with the following structure:

```python
{
    "save_id": "unique_save_identifier",
    "slot_name": "user_defined_slot_name",
    "user_id": "user_identifier",
    "save_data": { ... },  # Encrypted game data
    "metadata": {
        "save_name": "User Friendly Name",
        "description": "Save description",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:30:00Z",
        "play_time": 7200000,  # milliseconds
        "character_level": 25,
        "location": "Forest Temple"
    },
    "checksum": "sha256_hash",
    "encryption_key": "encrypted_key",
    "file_size": 1024,
    "is_auto_save": false
}
```

## Error Handling

The system provides comprehensive error handling:

### Common Errors

1. **Save File Not Found**: When attempting to load a non-existent save
2. **Corrupted Save File**: When checksum validation fails
3. **Insufficient Storage**: When storage quota is exceeded
4. **Network Errors**: When cloud sync fails
5. **Permission Errors**: When file system access is denied

### Error Recovery

```csharp
saveLoadService.OnSaveError += (error) => {
    switch (error.ErrorType) {
        case SaveErrorType.FileNotFound:
            ShowMessage("Save file not found");
            break;
        case SaveErrorType.Corrupted:
            ShowMessage("Save file is corrupted");
            OfferCorruptionRecovery();
            break;
        case SaveErrorType.NetworkError:
            ShowMessage("Network error - will retry when connection is restored");
            break;
    }
};
```

## Testing

### Integration Tests

The system includes comprehensive integration tests:

```csharp
[UnityTest]
public IEnumerator TestBasicSaveLoad()
{
    // Test basic save/load cycle
    string testSlot = "test_save";
    
    // Save
    await saveLoadService.SaveGameAsync(testSlot, "Test save");
    
    // Load
    bool loadSuccess = await saveLoadService.LoadGameAsync(testSlot);
    
    Assert.IsTrue(loadSuccess);
}
```

### Performance Testing

Monitor save/load performance:

```csharp
// Measure save time
var stopwatch = System.Diagnostics.Stopwatch.StartNew();
await saveLoadService.SaveGameAsync("perf_test", "Performance test");
stopwatch.Stop();
Debug.Log($"Save took: {stopwatch.ElapsedMilliseconds}ms");
```

## Security Considerations

### Encryption

Save files are encrypted using AES-256 encryption:

```csharp
// Encryption is handled automatically when enabled
// Keys are managed by the EncryptionService
```

### Integrity Validation

```csharp
// Checksums are automatically calculated and verified
// Corrupted files are detected and reported
```

### Access Control

```csharp
// Save files are associated with user IDs
// Users can only access their own save files
```

## Troubleshooting

### Common Issues

1. **Save Operation Hangs**
   - Check network connectivity
   - Verify backend service is running
   - Check for permission issues

2. **Load Operation Fails**
   - Verify save file exists
   - Check for corruption
   - Ensure compatible save version

3. **Auto-Save Not Working**
   - Verify auto-save is enabled
   - Check interval settings
   - Ensure service is initialized

### Debug Information

Enable debug logging:

```csharp
// Set log level in Unity console
Debug.Log($"Save operation status: {saveLoadService.IsOperationInProgress}");
Debug.Log($"Current save slot: {saveLoadService.CurrentSaveSlot}");
```

## Best Practices

1. **Always check operation status** before starting new operations
2. **Handle errors gracefully** with user-friendly messages
3. **Validate save data** before attempting to save
4. **Use auto-save** for better user experience
5. **Test thoroughly** with various save scenarios
6. **Monitor performance** for large save files
7. **Backup critical saves** to prevent data loss

## Future Enhancements

- **Cross-platform save sync**: Sync saves across different platforms
- **Save file compression**: Reduce save file sizes
- **Incremental saves**: Only save changed data
- **Save file analytics**: Track save/load patterns
- **Advanced corruption recovery**: Automatic repair of corrupted saves 