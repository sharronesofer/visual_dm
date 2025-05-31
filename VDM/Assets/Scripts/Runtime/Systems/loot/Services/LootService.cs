using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using Newtonsoft.Json;
using VDM.Systems.Loot.Models;
using VDM.Infrastructure.Services;

namespace VDM.Systems.Loot.Services
{
    /// <summary>
    /// Main service for interacting with the loot system backend API.
    /// Handles loot generation, item identification, enhancement, and shop operations.
    /// </summary>
    public class LootService : MonoBehaviour
    {
        [Header("API Configuration")]
        [SerializeField] private string baseUrl = "http://localhost:8000/api/v1";
        [SerializeField] private string lootEndpoint = "/loot";
        [SerializeField] private float requestTimeout = 30f;
        
        [Header("Caching")]
        [SerializeField] private bool enableCaching = true;
        [SerializeField] private float cacheExpiration = 300f; // 5 minutes
        
        // Singleton instance
        public static LootService Instance { get; private set; }
        
        // Events for real-time updates
        public event Action<LootItem> OnLootGenerated;
        public event Action<LootItem, bool> OnItemIdentified;
        public event Action<LootItem, bool> OnItemEnhanced;
        public event Action<Shop> OnShopInventoryUpdated;
        public event Action<ShopTransaction> OnShopTransactionCompleted;
        
        // Private fields
        private IApiService apiService;
        private Dictionary<string, CachedData> cache = new Dictionary<string, CachedData>();
        
        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeService();
            }
            else
            {
                Destroy(gameObject);
            }
        }
        
        private void InitializeService()
        {
            // Get the API service (assuming it exists in the core services)
            apiService = FindObjectOfType<ApiService>();
            if (apiService == null)
            {
                Debug.LogError("LootService: ApiService not found! Please ensure ApiService is available.");
            }
        }
        
        #region Loot Generation
        
        /// <summary>
        /// Generate loot based on monster levels and location context
        /// </summary>
        public async Task<Dictionary<string, object>> GenerateLootAsync(LootGenerationRequest request)
        {
            try
            {
                string endpoint = $"{lootEndpoint}/generate";
                string jsonData = JsonConvert.SerializeObject(request);
                
                Debug.Log($"Generating loot: {jsonData}");
                
                var response = await apiService.PostAsync<Dictionary<string, object>>(endpoint, jsonData);
                
                if (response != null)
                {
                    // Emit event for real-time updates
                    if (response.ContainsKey("equipment") && response["equipment"] is List<object> equipment)
                    {
                        foreach (var item in equipment)
                        {
                            if (item is Dictionary<string, object> itemDict)
                            {
                                var lootItem = JsonConvert.DeserializeObject<LootItem>(JsonConvert.SerializeObject(itemDict));
                                OnLootGenerated?.Invoke(lootItem);
                            }
                        }
                    }
                }
                
                return response;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to generate loot: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Generate loot from combat with simple monster levels
        /// </summary>
        public async Task<Dictionary<string, object>> GenerateCombatLootAsync(List<int> monsterLevels, int? locationId = null, int? regionId = null)
        {
            var request = new LootGenerationRequest
            {
                MonsterLevels = monsterLevels,
                LocationId = locationId,
                RegionId = regionId,
                SourceType = "combat"
            };
            
            return await GenerateLootAsync(request);
        }
        
        /// <summary>
        /// Generate a random item of specified category and rarity
        /// </summary>
        public async Task<LootItem> GenerateRandomItemAsync(string category, string rarity = "common", bool magical = false, int minLevel = 1, int maxLevel = 10)
        {
            try
            {
                string endpoint = $"{lootEndpoint}/generate/random-item";
                var requestData = new
                {
                    category = category,
                    rarity = rarity,
                    magical = magical,
                    min_level = minLevel,
                    max_level = maxLevel
                };
                
                string jsonData = JsonConvert.SerializeObject(requestData);
                var response = await apiService.PostAsync<Dictionary<string, object>>(endpoint, jsonData);
                
                if (response != null && response.ContainsKey("item"))
                {
                    var itemJson = JsonConvert.SerializeObject(response["item"]);
                    var lootItem = JsonConvert.DeserializeObject<LootItem>(itemJson);
                    
                    OnLootGenerated?.Invoke(lootItem);
                    return lootItem;
                }
                
                return null;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to generate random item: {ex.Message}");
                throw;
            }
        }
        
        #endregion
        
        #region Item Identification
        
        /// <summary>
        /// Attempt to identify an item using character skills
        /// </summary>
        public async Task<(LootItem item, bool success, string description)> IdentifyItemAsync(ItemIdentificationRequest request)
        {
            try
            {
                string endpoint = $"{lootEndpoint}/identify";
                string jsonData = JsonConvert.SerializeObject(request);
                
                var response = await apiService.PostAsync<Dictionary<string, object>>(endpoint, jsonData);
                
                if (response != null)
                {
                    var itemJson = JsonConvert.SerializeObject(response["item"]);
                    var identifiedItem = JsonConvert.DeserializeObject<LootItem>(itemJson);
                    bool success = (bool)response["success"];
                    string description = response["description"]?.ToString() ?? "";
                    
                    OnItemIdentified?.Invoke(identifiedItem, success);
                    
                    return (identifiedItem, success, description);
                }
                
                return (request.Item, false, "Failed to identify item");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to identify item: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Completely identify an item using powerful magic
        /// </summary>
        public async Task<(LootItem item, string description)> CompleteIdentificationAsync(LootItem item, int characterId, string method = "magic")
        {
            try
            {
                string endpoint = $"{lootEndpoint}/identify/complete";
                var requestData = new
                {
                    item = item,
                    character_id = characterId,
                    method = method
                };
                
                string jsonData = JsonConvert.SerializeObject(requestData);
                var response = await apiService.PostAsync<Dictionary<string, object>>(endpoint, jsonData);
                
                if (response != null)
                {
                    var itemJson = JsonConvert.SerializeObject(response["item"]);
                    var identifiedItem = JsonConvert.DeserializeObject<LootItem>(itemJson);
                    string description = response["description"]?.ToString() ?? "";
                    
                    OnItemIdentified?.Invoke(identifiedItem, true);
                    
                    return (identifiedItem, description);
                }
                
                return (item, "Failed to identify item");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to complete identification: {ex.Message}");
                throw;
            }
        }
        
        #endregion
        
        #region Item Enhancement
        
        /// <summary>
        /// Attempt to enhance an item
        /// </summary>
        public async Task<(LootItem item, bool success, string description)> EnhanceItemAsync(ItemEnhancementRequest request)
        {
            try
            {
                string endpoint = $"{lootEndpoint}/enhance";
                string jsonData = JsonConvert.SerializeObject(request);
                
                var response = await apiService.PostAsync<Dictionary<string, object>>(endpoint, jsonData);
                
                if (response != null)
                {
                    var itemJson = JsonConvert.SerializeObject(response["item"]);
                    var enhancedItem = JsonConvert.DeserializeObject<LootItem>(itemJson);
                    bool success = (bool)response["success"];
                    string description = response["description"]?.ToString() ?? "";
                    
                    OnItemEnhanced?.Invoke(enhancedItem, success);
                    
                    return (enhancedItem, success, description);
                }
                
                return (request.Item, false, "Failed to enhance item");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to enhance item: {ex.Message}");
                throw;
            }
        }
        
        #endregion
        
        #region Shop Operations
        
        /// <summary>
        /// Generate shop inventory
        /// </summary>
        public async Task<List<ShopItem>> GenerateShopInventoryAsync(
            int shopId, 
            string shopType, 
            int shopTier = 1, 
            string shopSpecialty = null,
            int? regionId = null, 
            int? locationId = null, 
            int? factionId = null,
            string motif = null,
            bool includeMagical = true,
            int? inventorySize = null)
        {
            try
            {
                string cacheKey = $"shop_inventory_{shopId}_{shopType}_{shopTier}";
                
                // Check cache first
                if (enableCaching && cache.ContainsKey(cacheKey) && !cache[cacheKey].IsExpired(cacheExpiration))
                {
                    return cache[cacheKey].Data as List<ShopItem>;
                }
                
                string endpoint = $"{lootEndpoint}/shop/generate-inventory";
                var requestData = new
                {
                    shop_id = shopId,
                    shop_type = shopType,
                    shop_tier = shopTier,
                    shop_specialty = shopSpecialty,
                    region_id = regionId,
                    location_id = locationId,
                    faction_id = factionId,
                    motif = motif,
                    include_magical = includeMagical,
                    inventory_size = inventorySize
                };
                
                string jsonData = JsonConvert.SerializeObject(requestData);
                var response = await apiService.PostAsync<List<Dictionary<string, object>>>(endpoint, jsonData);
                
                if (response != null)
                {
                    var shopItems = new List<ShopItem>();
                    foreach (var itemData in response)
                    {
                        var itemJson = JsonConvert.SerializeObject(itemData);
                        var shopItem = JsonConvert.DeserializeObject<ShopItem>(itemJson);
                        shopItems.Add(shopItem);
                    }
                    
                    // Cache the result
                    if (enableCaching)
                    {
                        cache[cacheKey] = new CachedData { Data = shopItems, Timestamp = DateTime.UtcNow };
                    }
                    
                    return shopItems;
                }
                
                return new List<ShopItem>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to generate shop inventory: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Update shop prices based on economic conditions
        /// </summary>
        public async Task<List<ShopItem>> UpdateShopPricesAsync(List<ShopItem> inventory, int regionId, string motif = null, List<string> worldEvents = null)
        {
            try
            {
                string endpoint = $"{lootEndpoint}/update-prices";
                var requestData = new
                {
                    inventory = inventory,
                    region_id = regionId,
                    motif = motif,
                    world_events = worldEvents
                };
                
                string jsonData = JsonConvert.SerializeObject(requestData);
                var response = await apiService.PostAsync<List<Dictionary<string, object>>>(endpoint, jsonData);
                
                if (response != null)
                {
                    var updatedItems = new List<ShopItem>();
                    foreach (var itemData in response)
                    {
                        var itemJson = JsonConvert.SerializeObject(itemData);
                        var shopItem = JsonConvert.DeserializeObject<ShopItem>(itemJson);
                        updatedItems.Add(shopItem);
                    }
                    
                    return updatedItems;
                }
                
                return inventory;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update shop prices: {ex.Message}");
                return inventory;
            }
        }
        
        /// <summary>
        /// Get dynamic price for an item
        /// </summary>
        public async Task<float> GetItemPriceAsync(LootItem item, int regionId, string motif = null, List<string> worldEvents = null)
        {
            try
            {
                string endpoint = $"{lootEndpoint}/price";
                var query = $"?item_data={Uri.EscapeDataString(JsonConvert.SerializeObject(item))}&region_id={regionId}";
                
                if (!string.IsNullOrEmpty(motif))
                    query += $"&motif={Uri.EscapeDataString(motif)}";
                
                if (worldEvents != null && worldEvents.Count > 0)
                    query += $"&world_events={Uri.EscapeDataString(string.Join(",", worldEvents))}";
                
                var response = await apiService.GetAsync<Dictionary<string, object>>(endpoint + query);
                
                if (response != null && response.ContainsKey("price"))
                {
                    return Convert.ToSingle(response["price"]);
                }
                
                return item.Value; // Fallback to item's base value
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get item price: {ex.Message}");
                return item.Value;
            }
        }
        
        #endregion
        
        #region Utility Methods
        
        /// <summary>
        /// Get item description based on player knowledge level
        /// </summary>
        public async Task<string> GetItemDescriptionAsync(LootItem item, int knowledgeLevel = 0)
        {
            try
            {
                string endpoint = $"{lootEndpoint}/item/description";
                var query = $"?item_data={Uri.EscapeDataString(JsonConvert.SerializeObject(item))}&knowledge_level={knowledgeLevel}";
                
                var response = await apiService.GetAsync<Dictionary<string, object>>(endpoint + query);
                
                if (response != null && response.ContainsKey("description"))
                {
                    return response["description"].ToString();
                }
                
                return item.Description ?? "No description available.";
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get item description: {ex.Message}");
                return item.Description ?? "No description available.";
            }
        }
        
        /// <summary>
        /// Clear cache for specific key or all cache
        /// </summary>
        public void ClearCache(string key = null)
        {
            if (string.IsNullOrEmpty(key))
            {
                cache.Clear();
                Debug.Log("LootService: All cache cleared");
            }
            else if (cache.ContainsKey(key))
            {
                cache.Remove(key);
                Debug.Log($"LootService: Cache cleared for key: {key}");
            }
        }
        
        /// <summary>
        /// Clean expired cache entries
        /// </summary>
        public void CleanExpiredCache()
        {
            var expiredKeys = new List<string>();
            
            foreach (var kvp in cache)
            {
                if (kvp.Value.IsExpired(cacheExpiration))
                {
                    expiredKeys.Add(kvp.Key);
                }
            }
            
            foreach (var key in expiredKeys)
            {
                cache.Remove(key);
            }
            
            if (expiredKeys.Count > 0)
            {
                Debug.Log($"LootService: Cleaned {expiredKeys.Count} expired cache entries");
            }
        }
        
        #endregion
        
        private void Update()
        {
            // Clean expired cache periodically
            if (enableCaching && Time.time % 60f < Time.deltaTime) // Every minute
            {
                CleanExpiredCache();
            }
        }
        
        /// <summary>
        /// Helper class for caching data
        /// </summary>
        private class CachedData
        {
            public object Data { get; set; }
            public DateTime Timestamp { get; set; }
            
            public bool IsExpired(float expirationSeconds)
            {
                return (DateTime.UtcNow - Timestamp).TotalSeconds > expirationSeconds;
            }
        }
    }
} 