# Visual DM Storage System

## Overview
This storage system provides a flexible, extensible backend for file and data storage in Unity projects. It is designed for runtime use (no UnityEditor dependencies) and supports multiple storage providers, starting with a robust file system implementation.

## Components

### 1. `IStorageProvider`
Defines the interface for all storage providers. Methods include:
- `Task<string> Save(string path, byte[] data)`
- `Task<byte[]> Load(string path)`
- `Task<bool> Delete(string path)`
- `Task<bool> Exists(string path)`
- `Task<string[]> List(string directory)`
- `Task<string> SaveStream(string path, Stream inputStream)`
- `Task<Stream> LoadStream(string path)`

### 2. `FileSystemStorageProvider`
Implements `IStorageProvider` using the local file system. Features:
- Path normalization and security (prevents traversal)
- Metadata support via sidecar JSON files
- Async stream support for large files
- Robust error handling with custom exceptions

#### Example Usage
```csharp
var provider = new FileSystemStorageProvider("/tmp/storage");
await provider.Save("folder/file.txt", Encoding.UTF8.GetBytes("Hello World"));
var data = await provider.Load("folder/file.txt");
string text = Encoding.UTF8.GetString(data);
```

### 3. `StorageFactory`
Static factory for instantiating providers. Example:
```csharp
var provider = StorageFactory.GetProvider("filesystem", "/tmp/storage");
```

### 4. `StorageUtils`
Utility methods for path normalization, validation, and safe filename generation.

### 5. Custom Exceptions
- `StorageException` (base)
- `StorageNotFoundException`
- `StorageUnauthorizedException`

### 6. `IStorable`
Defines the interface for objects that can be persisted by the PersistenceManager. Methods include:
- `string GetStorageKey()`
- `byte[] Serialize()`
- `void Deserialize(byte[] data)`
- `int DataVersion { get; }`

Implement this interface on any object you want to save/load using the persistence system.

### 7. `PersistenceManager`
Central singleton manager for all persistence operations. Features:
- Modular backend support (filesystem, future: cloud, database)
- Optional encryption via `IEncryptionService`
- Async save/load/delete/list operations for `IStorable` objects
- Configurable via `PersistenceConfig`

#### Example Usage
```csharp
// Configure and initialize
var config = new PersistenceConfig {
    StorageProviderType = "filesystem",
    StorageProviderConfig = Application.persistentDataPath + "/saves",
    EnableEncryption = false, // or true if using encryption
    EnableAutosave = true,
    AutosaveIntervalSeconds = 300,
    AutosaveRetentionCount = 5,
    EnableCloudSync = false,
    CloudProviderConfig = ""
};
PersistenceManager.Instance.Initialize(config);

// Save an object
await PersistenceManager.Instance.SaveAsync(myStorableObject);

// Load an object
await PersistenceManager.Instance.LoadAsync(myStorableObject);

// Delete an object
await PersistenceManager.Instance.DeleteAsync(myStorableObject);

// List saves
var saves = await PersistenceManager.Instance.ListSavesAsync();
```

### 8. `SerializationHelper`
Static helper for standardized serialization and deserialization:
- `ToJsonBytes<T>(T obj)`, `FromJsonBytes<T>(byte[])`
- `ToBinary<T>(T obj)`, `FromBinary<T>(byte[])`
- `ValidateVersioned<T>(T obj, int expectedVersion)`
- `Migrate<T>(T oldObj, int fromVersion, int toVersion, Func<T, int, int, T> migrationFunc)`

**Best Practices:**
- Use JSON for most data unless binary is required for performance.
- Always validate schema version after deserialization.
- Provide migration functions for backward compatibility.
- Avoid BinaryFormatter for untrusted data (use only for trusted, internal formats).

#### Example Usage
```csharp
// Serialize to JSON
var bytes = SerializationHelper.ToJsonBytes(myObject);
// Deserialize from JSON
var obj = SerializationHelper.FromJsonBytes<MyType>(bytes);
// Validate version
if (!SerializationHelper.ValidateVersioned(obj, expectedVersion)) {
    obj = SerializationHelper.Migrate(obj, oldVersion, expectedVersion, MyMigrationFunc);
}
```

### 9. `AutosaveManager`
Manages timed autosaves and event-based checkpoint saves for registered IStorable objects. Features:
- Configurable autosave interval and retention policy
- Save queuing to prevent performance spikes
- Checkpoint support for key game events
- Register/unregister IStorable objects for autosave
- Integrates with PersistenceManager

#### Example Usage
```csharp
// Configure autosave (5 min interval, retain 5 saves)
AutosaveManager.Instance.Configure(300, 5);
// Register an object for autosave
AutosaveManager.Instance.RegisterAutosaveTarget(myStorableObject);
// Trigger manual checkpoint
await AutosaveManager.Instance.TriggerCheckpoint("level_complete");
```

### 10. `CloudStorageProvider`
Stub implementation of IStorageProvider for cloud sync (Steam Cloud, iCloud, Google Drive, etc.).
- Use via StorageFactory (future integration)
- All methods currently throw NotImplementedException

### Checkpoints
- Use AutosaveManager.TriggerCheckpoint to save at key events (level completion, achievements, etc.)
- Checkpoints are versioned and timestamped

### Best Practices
- Register all major game state objects with AutosaveManager
- Use checkpoints for critical game events
- Use cloud storage for cross-device sync (when implemented)

### PersistenceConfig (updated)
- `EnableAutosave` (bool): Enable autosave system (default: false)
- `AutosaveIntervalSeconds` (int): Autosave interval in seconds (default: 300)
- `AutosaveRetentionCount` (int): Number of autosaves to retain (default: 5)
- `EnableCloudSync` (bool): Enable cloud sync (future, default: false)
- `CloudProviderConfig` (string): Cloud provider config string (future)

#### Example Usage
```csharp
var config = new PersistenceConfig {
    StorageProviderType = "cloud",
    StorageProviderConfig = "user@cloudservice",
    EnableEncryption = true,
    EncryptionService = new EncryptionService(key, hmacKey),
    EnableAutosave = true,
    AutosaveIntervalSeconds = 180,
    AutosaveRetentionCount = 10,
    EnableCloudSync = true,
    CloudProviderConfig = "steamcloud:appid=12345"
};
PersistenceManager.Instance.Initialize(config);
```

### Save Data Migration & Versioning
- Always increment IStorable.DataVersion when making breaking changes to data format
- Use SerializationHelper.Migrate to provide migration logic between versions
- Validate version after deserialization and migrate if needed
- Maintain backward compatibility for old save files

#### Example
```csharp
if (!SerializationHelper.ValidateVersioned(obj, expectedVersion)) {
    obj = SerializationHelper.Migrate(obj, oldVersion, expectedVersion, MyMigrationFunc);
}
```

### Cloud Sync & Conflict Resolution (future)
- Use CloudStorageProvider for cross-device save data (when implemented)
- Implement background sync with retry logic for failed uploads/downloads
- Detect and resolve conflicts (e.g., last-write-wins, user prompt)
- Notify user of sync status and conflicts
- Test offline operation and subsequent synchronization

### UI Integration (planned)
- Implement SaveLoadUIController for save/load browser, progress indicators, and error dialogs
- Show autosave and checkpoint notifications (non-intrusive)
- Display progress bars for long-running operations
- Provide clear error messages for failed saves/loads

### Test Strategy
- Unit tests for each storage component (PersistenceManager, providers, encryption, autosave)
- Test data integrity through serialization/deserialization cycles
- Verify encryption/decryption operations maintain data fidelity
- Test version compatibility with mock legacy data formats
- Integration tests with game systems (inventory, combat, time)
- Test autosave triggers and checkpoint creation
- Performance tests for save/load operations and memory usage
- Security tests for unauthorized access and data integrity
- User experience tests for UI feedback and autosave notifications
- Regression tests for backward compatibility

### Developer Guide & Extension Points
- Implement new storage providers by extending IStorageProvider (see FileSystemStorageProvider, SQLiteStorageProvider, CloudStorageProvider)
- Add new encryption algorithms by implementing IEncryptionService
- Extend autosave logic by modifying AutosaveManager
- Register new UI components for save/load feedback
- Document all changes in this README and Development_Bible.md

---

## Changelog

### 2025 Update
- Added AutosaveManager for timed autosaves and checkpoints
- Added CloudStorageProvider stub for future cloud sync
- Extended PersistenceConfig with autosave and cloud sync fields
- Documented migration/versioning best practices
- Added sections for UI integration, test strategy, and developer extension points