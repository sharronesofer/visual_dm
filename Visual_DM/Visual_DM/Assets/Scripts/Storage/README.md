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

## Extensibility
- Add new providers (e.g., cloud, database) by implementing `IStorageProvider` and updating `StorageFactory`.
- All code is Unity 2D runtime compatible (no scene references, no UnityEditor code).

## Best Practices
- Use async methods for all file operations to avoid blocking the Unity main thread.
- Always dispose streams returned by `LoadStream`.
- Store game data in `Application.persistentDataPath` or a platform-appropriate directory.
- Use `StorageUtils.SafeFilename` for user-generated file names.

## Integration
- Place all scripts in `Visual_DM/Visual_DM/Assets/Scripts/Storage/`.
- Reference the storage system from your runtime code (e.g., GameLoader.cs).

---
This system is designed for robust, secure, and extensible storage in Unity-based games and applications. 