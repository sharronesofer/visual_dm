using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace VisualDM.Storage
{
    /// <summary>
    /// Central manager for all persistence operations. Supports modular storage backends, encryption, and autosave configuration.
    /// </summary>
    public class PersistenceManager
    {
        private static PersistenceManager _instance;
        public static PersistenceManager Instance => _instance ??= new PersistenceManager();

        private IStorageProvider _storageProvider;
        private IEncryptionService _encryptionService;
        private PersistenceConfig _config;

        private PersistenceManager() { }

        /// <summary>
        /// Initializes the persistence manager with the given configuration.
        /// </summary>
        public void Initialize(PersistenceConfig config)
        {
            _config = config;
            _storageProvider = StorageFactory.GetProvider(config.StorageProviderType, config.StorageProviderConfig);
            _encryptionService = config.EncryptionService;
            if (config.EnableAutosave)
                AutosaveManager.Instance.Configure(config.AutosaveIntervalSeconds, config.AutosaveRetentionCount);
        }

        /// <summary>
        /// Saves a storable object asynchronously.
        /// </summary>
        public async Task SaveAsync(IStorable storable)
        {
            var data = storable.Serialize();
            if (_encryptionService != null && _config.EnableEncryption)
                data = _encryptionService.Encrypt(data);
            await _storageProvider.Save(storable.GetStorageKey(), data, storable.DataVersion);
        }

        /// <summary>
        /// Loads a storable object asynchronously and populates the given instance.
        /// </summary>
        public async Task<bool> LoadAsync(IStorable storable)
        {
            if (!await _storageProvider.Exists(storable.GetStorageKey()))
                return false;
            var data = await _storageProvider.Load(storable.GetStorageKey(), storable.DataVersion);
            if (_encryptionService != null && _config.EnableEncryption)
                data = _encryptionService.Decrypt(data);
            storable.Deserialize(data);
            return true;
        }

        /// <summary>
        /// Deletes a storable object asynchronously.
        /// </summary>
        public async Task<bool> DeleteAsync(IStorable storable)
        {
            return await _storageProvider.Delete(storable.GetStorageKey());
        }

        /// <summary>
        /// Lists all saved objects in the configured storage directory.
        /// </summary>
        public async Task<string[]> ListSavesAsync(string directory = "")
        {
            return await _storageProvider.List(directory);
        }

        /// <summary>
        /// Gets or sets the current storage provider (for advanced scenarios).
        /// </summary>
        public IStorageProvider StorageProvider
        {
            get => _storageProvider;
            set => _storageProvider = value;
        }

        /// <summary>
        /// Gets or sets the encryption service (for advanced scenarios).
        /// </summary>
        public IEncryptionService EncryptionService
        {
            get => _encryptionService;
            set => _encryptionService = value;
        }

        /// <summary>
        /// Gets the current configuration.
        /// </summary>
        public PersistenceConfig Config => _config;
    }

    /// <summary>
    /// Configuration for the persistence manager.
    /// </summary>
    public class PersistenceConfig
    {
        public string StorageProviderType { get; set; } = "filesystem";
        public string StorageProviderConfig { get; set; } = "";
        public bool EnableEncryption { get; set; } = false;
        public IEncryptionService EncryptionService { get; set; }
        // Autosave options
        public bool EnableAutosave { get; set; } = false;
        public int AutosaveIntervalSeconds { get; set; } = 300;
        public int AutosaveRetentionCount { get; set; } = 5;
        // Cloud sync options (future)
        public bool EnableCloudSync { get; set; } = false;
        public string CloudProviderConfig { get; set; } = "";
    }

    /// <summary>
    /// Interface for encryption services.
    /// </summary>
    public interface IEncryptionService
    {
        byte[] Encrypt(byte[] data);
        byte[] Decrypt(byte[] data);
    }
} 