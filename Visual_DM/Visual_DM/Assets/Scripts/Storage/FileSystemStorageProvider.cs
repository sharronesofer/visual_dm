using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Linq;
using System.Collections.Generic;
using Newtonsoft.Json; // For metadata serialization
using Visual_DM.Storage;

namespace Visual_DM.Storage
{
    /// <summary>
    /// File system-based implementation of IStorageProvider.
    /// </summary>
    /// <example>
    /// // Example usage:
    /// var provider = new FileSystemStorageProvider("/tmp/storage");
    /// await provider.Save("folder/file.txt", Encoding.UTF8.GetBytes("Hello World"));
    /// var data = await provider.Load("folder/file.txt");
    /// string text = Encoding.UTF8.GetString(data);
    /// </example>
    public class FileSystemStorageProvider : IStorageProvider
    {
        private readonly string _rootDirectory;

        public FileSystemStorageProvider(string rootDirectory)
        {
            _rootDirectory = Path.GetFullPath(rootDirectory);
            if (!Directory.Exists(_rootDirectory))
                Directory.CreateDirectory(_rootDirectory);
        }

        /// <summary>
        /// Normalizes and secures a path to prevent traversal outside the root.
        /// </summary>
        private string NormalizePath(string path)
        {
            var combined = Path.Combine(_rootDirectory, path);
            var full = Path.GetFullPath(combined);
            if (!full.StartsWith(_rootDirectory))
                throw new StorageUnauthorizedException("Attempted path traversal outside storage root.");
            return full;
        }

        public async Task<string> Save(string path, byte[] data)
        {
            var fullPath = NormalizePath(path);
            var dir = Path.GetDirectoryName(fullPath);
            if (!Directory.Exists(dir))
                Directory.CreateDirectory(dir);
            await File.WriteAllBytesAsync(fullPath, data);
            return fullPath;
        }

        public async Task<byte[]> Load(string path)
        {
            var fullPath = NormalizePath(path);
            if (!File.Exists(fullPath))
                throw new StorageNotFoundException($"File not found: {path}");
            return await File.ReadAllBytesAsync(fullPath);
        }

        public Task<bool> Delete(string path)
        {
            var fullPath = NormalizePath(path);
            if (File.Exists(fullPath))
            {
                File.Delete(fullPath);
                // Delete metadata if exists
                var metaPath = fullPath + ".meta.json";
                if (File.Exists(metaPath))
                    File.Delete(metaPath);
                return Task.FromResult(true);
            }
            return Task.FromResult(false);
        }

        public Task<bool> Exists(string path)
        {
            var fullPath = NormalizePath(path);
            return Task.FromResult(File.Exists(fullPath));
        }

        public Task<string[]> List(string directory)
        {
            var dirPath = NormalizePath(directory);
            if (!Directory.Exists(dirPath))
                return Task.FromResult(Array.Empty<string>());
            var files = Directory.GetFiles(dirPath)
                .Where(f => !f.EndsWith(".meta.json"))
                .Select(f => Path.GetFileName(f))
                .ToArray();
            return Task.FromResult(files);
        }

        /// <summary>
        /// Saves metadata as a sidecar JSON file.
        /// </summary>
        public async Task SaveMetadata(string path, object metadata)
        {
            var fullPath = NormalizePath(path) + ".meta.json";
            var json = JsonConvert.SerializeObject(metadata, Formatting.Indented);
            await File.WriteAllTextAsync(fullPath, json, Encoding.UTF8);
        }

        /// <summary>
        /// Loads metadata from a sidecar JSON file.
        /// </summary>
        public async Task<T> LoadMetadata<T>(string path)
        {
            var fullPath = NormalizePath(path) + ".meta.json";
            if (!File.Exists(fullPath))
                throw new StorageNotFoundException($"Metadata not found for: {path}");
            var json = await File.ReadAllTextAsync(fullPath, Encoding.UTF8);
            return JsonConvert.DeserializeObject<T>(json);
        }

        /// <summary>
        /// Saves data from a stream to the specified path (for large files).
        /// </summary>
        public async Task<string> SaveStream(string path, Stream inputStream)
        {
            var fullPath = NormalizePath(path);
            var dir = Path.GetDirectoryName(fullPath);
            if (!Directory.Exists(dir))
                Directory.CreateDirectory(dir);
            using (var fileStream = new FileStream(fullPath, FileMode.Create, FileAccess.Write, FileShare.None, 81920, true))
            {
                await inputStream.CopyToAsync(fileStream);
            }
            return fullPath;
        }

        /// <summary>
        /// Loads data as a stream from the specified path (for large files).
        /// Caller is responsible for disposing the returned stream.
        /// </summary>
        public Task<Stream> LoadStream(string path)
        {
            var fullPath = NormalizePath(path);
            if (!File.Exists(fullPath))
                throw new StorageNotFoundException($"File not found: {path}");
            Stream stream = new FileStream(fullPath, FileMode.Open, FileAccess.Read, FileShare.Read, 81920, true);
            return Task.FromResult(stream);
        }
    }
} 