using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.DTOs.Common;


namespace VDM.Infrastructure.Data.Services
{
    /// <summary>
    /// Generic data service implementation with Unity integration and backend synchronization.
    /// </summary>
    /// <typeparam name="T">Type of data model</typeparam>
    public class DataService<T> : IDataService<T> where T : class, IDataModel, new()
    {
        private readonly Dictionary<string, T> _cache = new();
        private readonly string _dataPath;
        private readonly bool _enablePersistence;
        private readonly bool _enableBackendSync;

        /// <summary>
        /// Create a new data service
        /// </summary>
        /// <param name="dataPath">Local storage path for persistence</param>
        /// <param name="enablePersistence">Enable local file persistence</param>
        /// <param name="enableBackendSync">Enable backend synchronization</param>
        public DataService(string dataPath = null, bool enablePersistence = true, bool enableBackendSync = true)
        {
            _dataPath = dataPath ?? $"{Application.persistentDataPath}/Data/{typeof(T).Name}";
            _enablePersistence = enablePersistence;
            _enableBackendSync = enableBackendSync;
            
            // Ensure directory exists
            if (_enablePersistence)
            {
                var directory = System.IO.Path.GetDirectoryName(_dataPath);
                if (!System.IO.Directory.Exists(directory))
                {
                    System.IO.Directory.CreateDirectory(directory);
                }
            }
        }

        public async Task<T> GetByIdAsync(string id)
        {
            if (string.IsNullOrEmpty(id))
                throw new ArgumentException("ID cannot be null or empty", nameof(id));

            // Check cache first
            if (_cache.TryGetValue(id, out var cachedItem))
            {
                return cachedItem;
            }

            // Try to load from local storage
            if (_enablePersistence)
            {
                var item = await LoadFromFileAsync(id);
                if (item != null)
                {
                    _cache[id] = item;
                    return item;
                }
            }

            // Try to fetch from backend
            if (_enableBackendSync)
            {
                var item = await FetchFromBackendAsync(id);
                if (item != null)
                {
                    _cache[id] = item;
                    if (_enablePersistence)
                    {
                        await SaveToFileAsync(item);
                    }
                    return item;
                }
            }

            return null;
        }

        public async Task<List<T>> GetAllAsync()
        {
            var results = new List<T>();

            // Add cached items
            results.AddRange(_cache.Values);

            // Load from local storage
            if (_enablePersistence)
            {
                var localItems = await LoadAllFromFilesAsync();
                foreach (var item in localItems)
                {
                    if (!_cache.ContainsKey(item.Id))
                    {
                        _cache[item.Id] = item;
                        results.Add(item);
                    }
                }
            }

            // Sync with backend if enabled
            if (_enableBackendSync)
            {
                try
                {
                    var backendItems = await FetchAllFromBackendAsync();
                    foreach (var item in backendItems)
                    {
                        if (!_cache.ContainsKey(item.Id))
                        {
                            _cache[item.Id] = item;
                            results.Add(item);
                            
                            if (_enablePersistence)
                            {
                                await SaveToFileAsync(item);
                            }
                        }
                    }
                }
                catch (Exception ex)
                {
                    Debug.LogWarning($"[DataService<{typeof(T).Name}>] Failed to sync with backend: {ex.Message}");
                }
            }

            return results;
        }

        public async Task<T> CreateAsync(T item)
        {
            if (item == null)
                throw new ArgumentNullException(nameof(item));

            // Validate the item
            if (!await ValidateAsync(item))
            {
                throw new InvalidOperationException($"Validation failed for {typeof(T).Name}");
            }

            // Generate ID if not set
            if (string.IsNullOrEmpty(item.Id))
            {
                item.Id = GenerateId();
            }

            // Update metadata
            item.LastUpdated = DateTime.UtcNow;
            if (item.Version <= 0)
            {
                item.Version = 1;
            }

            // Save to backend first
            if (_enableBackendSync)
            {
                try
                {
                    item = await CreateInBackendAsync(item);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"[DataService<{typeof(T).Name}>] Failed to create in backend: {ex.Message}");
                    throw;
                }
            }

            // Cache the item
            _cache[item.Id] = item;

            // Save to local storage
            if (_enablePersistence)
            {
                await SaveToFileAsync(item);
            }

            Debug.Log($"[DataService<{typeof(T).Name}>] Created item with ID: {item.Id}");
            return item;
        }

        public async Task<T> UpdateAsync(T item)
        {
            if (item == null)
                throw new ArgumentNullException(nameof(item));

            if (string.IsNullOrEmpty(item.Id))
                throw new ArgumentException("Item ID cannot be null or empty", nameof(item));

            // Validate the item
            if (!await ValidateAsync(item))
            {
                throw new InvalidOperationException($"Validation failed for {typeof(T).Name}");
            }

            // Update metadata
            item.LastUpdated = DateTime.UtcNow;
            item.Version++;

            // Update in backend first
            if (_enableBackendSync)
            {
                try
                {
                    item = await UpdateInBackendAsync(item);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"[DataService<{typeof(T).Name}>] Failed to update in backend: {ex.Message}");
                    throw;
                }
            }

            // Update cache
            _cache[item.Id] = item;

            // Save to local storage
            if (_enablePersistence)
            {
                await SaveToFileAsync(item);
            }

            Debug.Log($"[DataService<{typeof(T).Name}>] Updated item with ID: {item.Id}");
            return item;
        }

        public async Task<bool> DeleteAsync(string id)
        {
            if (string.IsNullOrEmpty(id))
                throw new ArgumentException("ID cannot be null or empty", nameof(id));

            // Delete from backend first
            if (_enableBackendSync)
            {
                try
                {
                    await DeleteFromBackendAsync(id);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"[DataService<{typeof(T).Name}>] Failed to delete from backend: {ex.Message}");
                    throw;
                }
            }

            // Remove from cache
            _cache.Remove(id);

            // Delete from local storage
            if (_enablePersistence)
            {
                await DeleteFileAsync(id);
            }

            Debug.Log($"[DataService<{typeof(T).Name}>] Deleted item with ID: {id}");
            return true;
        }

        public async Task<bool> ValidateAsync(T item)
        {
            if (item == null) return false;

            try
            {
                // Basic validation
                if (string.IsNullOrEmpty(item.Id) && item.Version > 0)
                {
                    Debug.LogWarning($"[DataService<{typeof(T).Name}>] Item has version but no ID");
                    return false;
                }

                // Call item's own validation
                return item.Validate();
            }
            catch (Exception ex)
            {
                Debug.LogError($"[DataService<{typeof(T).Name}>] Validation error: {ex.Message}");
                return false;
            }
        }

        public async Task<bool> ExistsAsync(string id)
        {
            if (string.IsNullOrEmpty(id)) return false;

            // Check cache first
            if (_cache.ContainsKey(id)) return true;

            // Check local storage
            if (_enablePersistence && await FileExistsAsync(id)) return true;

            // Check backend
            if (_enableBackendSync)
            {
                try
                {
                    return await ExistsInBackendAsync(id);
                }
                catch (Exception ex)
                {
                    Debug.LogWarning($"[DataService<{typeof(T).Name}>] Failed to check existence in backend: {ex.Message}");
                }
            }

            return false;
        }

        public async Task SynchronizeAsync()
        {
            if (!_enableBackendSync) return;

            try
            {
                Debug.Log($"[DataService<{typeof(T).Name}>] Starting synchronization with backend");

                // Get all items from backend
                var backendItems = await FetchAllFromBackendAsync();
                
                foreach (var item in backendItems)
                {
                    // Update cache
                    _cache[item.Id] = item;
                    
                    // Save to local storage
                    if (_enablePersistence)
                    {
                        await SaveToFileAsync(item);
                    }
                }

                Debug.Log($"[DataService<{typeof(T).Name}>] Synchronized {backendItems.Count()} items");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[DataService<{typeof(T).Name}>] Synchronization failed: {ex.Message}");
                throw;
            }
        }

        public void ClearCache()
        {
            _cache.Clear();
            Debug.Log($"[DataService<{typeof(T).Name}>] Cache cleared");
        }

        // Private helper methods

        private string GenerateId()
        {
            return Guid.NewGuid().ToString();
        }

        private async Task<T> LoadFromFileAsync(string id)
        {
            try
            {
                var filePath = GetFilePath(id);
                if (!System.IO.File.Exists(filePath)) return null;

                var json = await System.IO.File.ReadAllTextAsync(filePath);
                return Newtonsoft.Json.JsonConvert.DeserializeObject<T>(json);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[DataService<{typeof(T).Name}>] Failed to load from file: {ex.Message}");
                return null;
            }
        }

        private async Task<IEnumerable<T>> LoadAllFromFilesAsync()
        {
            var results = new List<T>();
            
            try
            {
                var directory = System.IO.Path.GetDirectoryName(_dataPath);
                if (!System.IO.Directory.Exists(directory)) return results;

                var files = System.IO.Directory.GetFiles(directory, "*.json");
                
                foreach (var file in files)
                {
                    try
                    {
                        var json = await System.IO.File.ReadAllTextAsync(file);
                        var item = Newtonsoft.Json.JsonConvert.DeserializeObject<T>(json);
                        if (item != null)
                        {
                            results.Add(item);
                        }
                    }
                    catch (Exception ex)
                    {
                        Debug.LogWarning($"[DataService<{typeof(T).Name}>] Failed to load file {file}: {ex.Message}");
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[DataService<{typeof(T).Name}>] Failed to load from files: {ex.Message}");
            }

            return results;
        }

        private async Task SaveToFileAsync(T item)
        {
            try
            {
                var filePath = GetFilePath(item.Id);
                var json = item.Serialize();
                await System.IO.File.WriteAllTextAsync(filePath, json);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[DataService<{typeof(T).Name}>] Failed to save to file: {ex.Message}");
            }
        }

        private async Task DeleteFileAsync(string id)
        {
            try
            {
                var filePath = GetFilePath(id);
                if (System.IO.File.Exists(filePath))
                {
                    System.IO.File.Delete(filePath);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[DataService<{typeof(T).Name}>] Failed to delete file: {ex.Message}");
            }
        }

        private async Task<bool> FileExistsAsync(string id)
        {
            try
            {
                var filePath = GetFilePath(id);
                return System.IO.File.Exists(filePath);
            }
            catch
            {
                return false;
            }
        }

        private string GetFilePath(string id)
        {
            return System.IO.Path.Combine(System.IO.Path.GetDirectoryName(_dataPath), $"{id}.json");
        }

        // Backend integration methods (to be implemented based on specific backend API)

        private async Task<T> FetchFromBackendAsync(string id)
        {
            // TODO: Implement backend API call
            await Task.CompletedTask;
            return null;
        }

        private async Task<IEnumerable<T>> FetchAllFromBackendAsync()
        {
            // TODO: Implement backend API call
            await Task.CompletedTask;
            return new List<T>();
        }

        private async Task<T> CreateInBackendAsync(T item)
        {
            // TODO: Implement backend API call
            await Task.CompletedTask;
            return item;
        }

        private async Task<T> UpdateInBackendAsync(T item)
        {
            // TODO: Implement backend API call
            await Task.CompletedTask;
            return item;
        }

        private async Task DeleteFromBackendAsync(string id)
        {
            // TODO: Implement backend API call
            await Task.CompletedTask;
        }

        private async Task<bool> ExistsInBackendAsync(string id)
        {
            // TODO: Implement backend API call
            await Task.CompletedTask;
            return false;
        }

        // IDataService interface methods
        public bool ValidateModel(T model)
        {
            if (model == null) return false;

            try
            {
                // Basic validation
                if (string.IsNullOrEmpty(model.Id) && model.Version > 0)
                {
                    return false;
                }

                // Call model's own validation
                return model.Validate();
            }
            catch
            {
                return false;
            }
        }

        public List<string> GetValidationErrors(T model)
        {
            var errors = new List<string>();

            if (model == null)
            {
                errors.Add("Model cannot be null");
                return errors;
            }

            try
            {
                // Basic validation
                if (string.IsNullOrEmpty(model.Id) && model.Version > 0)
                {
                    errors.Add("Model has version but no ID");
                }

                // Additional validation can be added here
                if (!model.Validate())
                {
                    errors.Add("Model failed custom validation");
                }
            }
            catch (Exception ex)
            {
                errors.Add($"Validation error: {ex.Message}");
            }

            return errors;
        }

        public async Task<bool> SaveAsync()
        {
            if (!_enablePersistence) return true;

            try
            {
                foreach (var item in _cache.Values)
                {
                    await SaveToFileAsync(item);
                }
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[DataService<{typeof(T).Name}>] Failed to save: {ex.Message}");
                return false;
            }
        }

        public async Task<bool> LoadAsync()
        {
            if (!_enablePersistence) return true;

            try
            {
                var items = await LoadAllFromFilesAsync();
                _cache.Clear();
                foreach (var item in items)
                {
                    _cache[item.Id] = item;
                }
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[DataService<{typeof(T).Name}>] Failed to load: {ex.Message}");
                return false;
            }
        }

        public void Clear()
        {
            _cache.Clear();
            
            if (_enablePersistence)
            {
                try
                {
                    var directory = System.IO.Path.GetDirectoryName(_dataPath);
                    if (System.IO.Directory.Exists(directory))
                    {
                        var files = System.IO.Directory.GetFiles(directory, "*.json");
                        foreach (var file in files)
                        {
                            System.IO.File.Delete(file);
                        }
                    }
                }
                catch (Exception ex)
                {
                    Debug.LogError($"[DataService<{typeof(T).Name}>] Failed to clear files: {ex.Message}");
                }
            }
        }

        public int Count => _cache.Count;
    }
} 