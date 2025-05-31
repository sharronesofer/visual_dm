using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using VDM.Systems.Loot.Models;
using VDM.Systems.Loot.Services;

namespace VDM.Systems.Loot.Integration
{
    /// <summary>
    /// Integration component that connects the loot system with other game systems.
    /// Handles cross-system communication and data synchronization.
    /// </summary>
    public class LootSystemIntegration : MonoBehaviour
    {
        [Header("Integration Settings")]
        [SerializeField] private bool enableInventoryIntegration = true;
        [SerializeField] private bool enableEconomyIntegration = true;
        [SerializeField] private bool enableCharacterIntegration = true;
        [SerializeField] private bool enableEventIntegration = true;
        
        [Header("Auto-Integration")]
        [SerializeField] private bool autoAddLootToInventory = true;
        [SerializeField] private bool autoUpdateEconomicFactors = true;
        [SerializeField] private bool autoTrackCharacterProgress = true;
        
        // Singleton instance
        public static LootSystemIntegration Instance { get; private set; }
        
        // Events for cross-system communication
        public event Action<LootItem> OnLootAddedToInventory;
        public event Action<LootItem, float> OnItemValueCalculated;
        public event Action<int, int> OnCharacterSkillUsed; // characterId, skillLevel
        public event Action<string, Dictionary<string, object>> OnLootEventTriggered;
        
        // System references (to be injected or found)
        private LootService lootService;
        // private InventoryService inventoryService;
        // private EconomyService economyService;
        // private CharacterService characterService;
        // private EventService eventService;
        
        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeIntegration();
            }
            else
            {
                Destroy(gameObject);
            }
        }
        
        private void InitializeIntegration()
        {
            // Get service references
            lootService = LootService.Instance;
            if (lootService == null)
            {
                Debug.LogError("LootSystemIntegration: LootService not found!");
                return;
            }
            
            // Subscribe to loot service events
            SetupLootServiceEvents();
            
            // Initialize other system integrations
            InitializeInventoryIntegration();
            InitializeEconomyIntegration();
            InitializeCharacterIntegration();
            InitializeEventIntegration();
            
            Debug.Log("LootSystemIntegration: Initialized successfully");
        }
        
        private void SetupLootServiceEvents()
        {
            lootService.OnLootGenerated += HandleLootGenerated;
            lootService.OnItemIdentified += HandleItemIdentified;
            lootService.OnItemEnhanced += HandleItemEnhanced;
            lootService.OnShopInventoryUpdated += HandleShopInventoryUpdated;
            lootService.OnShopTransactionCompleted += HandleShopTransactionCompleted;
        }
        
        #region Inventory Integration
        
        private void InitializeInventoryIntegration()
        {
            if (!enableInventoryIntegration) return;
            
            // Find and setup inventory service integration
            // inventoryService = FindObjectOfType<InventoryService>();
            
            Debug.Log("LootSystemIntegration: Inventory integration initialized");
        }
        
        /// <summary>
        /// Add a loot item to the player's inventory
        /// </summary>
        public async Task<bool> AddLootToInventoryAsync(LootItem item, int playerId)
        {
            if (!enableInventoryIntegration || item == null)
                return false;
            
            try
            {
                // Integration with inventory system
                // bool success = await inventoryService.AddItemAsync(playerId, item);
                
                // For now, simulate success
                bool success = true;
                
                if (success)
                {
                    OnLootAddedToInventory?.Invoke(item);
                    Debug.Log($"Added {item.GetDisplayName()} to inventory");
                }
                
                return success;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to add loot to inventory: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Remove an item from inventory (for selling, trading, etc.)
        /// </summary>
        public async Task<bool> RemoveFromInventoryAsync(string itemId, int playerId)
        {
            if (!enableInventoryIntegration)
                return false;
            
            try
            {
                // Integration with inventory system
                // bool success = await inventoryService.RemoveItemAsync(playerId, itemId);
                
                // For now, simulate success
                bool success = true;
                
                return success;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to remove item from inventory: {ex.Message}");
                return false;
            }
        }
        
        #endregion
        
        #region Economy Integration
        
        private void InitializeEconomyIntegration()
        {
            if (!enableEconomyIntegration) return;
            
            // Find and setup economy service integration
            // economyService = FindObjectOfType<EconomyService>();
            
            Debug.Log("LootSystemIntegration: Economy integration initialized");
        }
        
        /// <summary>
        /// Get current economic factors for a region
        /// </summary>
        public async Task<Dictionary<string, float>> GetEconomicFactorsAsync(int regionId)
        {
            if (!enableEconomyIntegration)
                return new Dictionary<string, float>();
            
            try
            {
                // Integration with economy system
                // var factors = await economyService.GetRegionalFactorsAsync(regionId);
                
                // For now, return mock data
                var factors = new Dictionary<string, float>
                {
                    ["prosperity"] = UnityEngine.Random.Range(0.8f, 1.2f),
                    ["supply"] = UnityEngine.Random.Range(0.9f, 1.1f),
                    ["demand"] = UnityEngine.Random.Range(0.9f, 1.1f),
                    ["conflict"] = UnityEngine.Random.Range(0.8f, 1.3f),
                    ["trade_routes"] = UnityEngine.Random.Range(0.9f, 1.1f),
                    ["stability"] = UnityEngine.Random.Range(0.8f, 1.2f)
                };
                
                return factors;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get economic factors: {ex.Message}");
                return new Dictionary<string, float>();
            }
        }
        
        /// <summary>
        /// Process a shop transaction through the economy system
        /// </summary>
        public async Task<bool> ProcessTransactionAsync(ShopTransaction transaction)
        {
            if (!enableEconomyIntegration)
                return true;
            
            try
            {
                // Integration with economy system
                // bool success = await economyService.ProcessTransactionAsync(transaction);
                
                // For now, simulate success
                bool success = true;
                
                if (success)
                {
                    // Update player wealth, shop reputation, etc.
                    Debug.Log($"Processed transaction: {transaction.Type} for {transaction.FinalPrice} gold");
                }
                
                return success;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to process transaction: {ex.Message}");
                return false;
            }
        }
        
        #endregion
        
        #region Character Integration
        
        private void InitializeCharacterIntegration()
        {
            if (!enableCharacterIntegration) return;
            
            // Find and setup character service integration
            // characterService = FindObjectOfType<CharacterService>();
            
            Debug.Log("LootSystemIntegration: Character integration initialized");
        }
        
        /// <summary>
        /// Get character's identification skill level
        /// </summary>
        public async Task<int> GetCharacterIdentificationSkillAsync(int characterId)
        {
            if (!enableCharacterIntegration)
                return 0;
            
            try
            {
                // Integration with character system
                // var character = await characterService.GetCharacterAsync(characterId);
                // return character.GetSkillLevel("identification");
                
                // For now, return mock data
                return UnityEngine.Random.Range(1, 20);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get character skill: {ex.Message}");
                return 0;
            }
        }
        
        /// <summary>
        /// Get character's crafting skill level
        /// </summary>
        public async Task<int> GetCharacterCraftingSkillAsync(int characterId, string craftingType)
        {
            if (!enableCharacterIntegration)
                return 0;
            
            try
            {
                // Integration with character system
                // var character = await characterService.GetCharacterAsync(characterId);
                // return character.GetSkillLevel(craftingType);
                
                // For now, return mock data
                return UnityEngine.Random.Range(1, 15);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get character crafting skill: {ex.Message}");
                return 0;
            }
        }
        
        /// <summary>
        /// Award experience for successful identification or enhancement
        /// </summary>
        public async Task AwardSkillExperienceAsync(int characterId, string skillType, int experience)
        {
            if (!enableCharacterIntegration)
                return;
            
            try
            {
                // Integration with character system
                // await characterService.AwardExperienceAsync(characterId, skillType, experience);
                
                Debug.Log($"Awarded {experience} {skillType} experience to character {characterId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to award experience: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Event Integration
        
        private void InitializeEventIntegration()
        {
            if (!enableEventIntegration) return;
            
            // Find and setup event service integration
            // eventService = FindObjectOfType<EventService>();
            
            Debug.Log("LootSystemIntegration: Event integration initialized");
        }
        
        /// <summary>
        /// Publish a loot-related event to the event system
        /// </summary>
        public void PublishLootEvent(string eventType, Dictionary<string, object> eventData)
        {
            if (!enableEventIntegration)
                return;
            
            try
            {
                // Integration with event system
                // eventService.PublishEvent(eventType, eventData);
                
                OnLootEventTriggered?.Invoke(eventType, eventData);
                Debug.Log($"Published loot event: {eventType}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to publish loot event: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Event Handlers
        
        private async void HandleLootGenerated(LootItem item)
        {
            Debug.Log($"Loot generated: {item.GetDisplayName()}");
            
            // Auto-add to inventory if enabled
            if (autoAddLootToInventory)
            {
                // Assuming player ID 1 for now
                await AddLootToInventoryAsync(item, 1);
            }
            
            // Publish event
            var eventData = new Dictionary<string, object>
            {
                ["item_id"] = item.Id,
                ["item_name"] = item.Name,
                ["item_rarity"] = item.Rarity,
                ["item_value"] = item.Value
            };
            PublishLootEvent("loot.generated", eventData);
        }
        
        private async void HandleItemIdentified(LootItem item, bool success)
        {
            Debug.Log($"Item identification: {item.GetDisplayName()} - Success: {success}");
            
            if (success && autoTrackCharacterProgress)
            {
                // Award identification experience
                await AwardSkillExperienceAsync(1, "identification", 10);
            }
            
            // Publish event
            var eventData = new Dictionary<string, object>
            {
                ["item_id"] = item.Id,
                ["item_name"] = item.Name,
                ["success"] = success,
                ["revealed_effects"] = item.RevealedEffects
            };
            PublishLootEvent("item.identified", eventData);
        }
        
        private async void HandleItemEnhanced(LootItem item, bool success)
        {
            Debug.Log($"Item enhancement: {item.GetDisplayName()} - Success: {success}");
            
            if (success && autoTrackCharacterProgress)
            {
                // Award crafting experience
                await AwardSkillExperienceAsync(1, "crafting", 15);
            }
            
            // Publish event
            var eventData = new Dictionary<string, object>
            {
                ["item_id"] = item.Id,
                ["item_name"] = item.Name,
                ["success"] = success,
                ["new_rarity"] = item.Rarity,
                ["enhancement_count"] = item.Enchantments.Count
            };
            PublishLootEvent("item.enhanced", eventData);
        }
        
        private void HandleShopInventoryUpdated(Shop shop)
        {
            Debug.Log($"Shop inventory updated: {shop.Name}");
            
            // Publish event
            var eventData = new Dictionary<string, object>
            {
                ["shop_id"] = shop.Id,
                ["shop_name"] = shop.Name,
                ["shop_type"] = shop.Type,
                ["inventory_count"] = shop.Inventory.Count
            };
            PublishLootEvent("shop.inventory_updated", eventData);
        }
        
        private async void HandleShopTransactionCompleted(ShopTransaction transaction)
        {
            Debug.Log($"Shop transaction completed: {transaction.Type} for {transaction.FinalPrice} gold");
            
            // Process through economy system
            await ProcessTransactionAsync(transaction);
            
            // Publish event
            var eventData = new Dictionary<string, object>
            {
                ["transaction_id"] = transaction.TransactionId,
                ["shop_id"] = transaction.ShopId,
                ["transaction_type"] = transaction.Type.ToString(),
                ["final_price"] = transaction.FinalPrice,
                ["success"] = transaction.TransactionSuccessful
            };
            PublishLootEvent("shop.transaction_completed", eventData);
        }
        
        #endregion
        
        #region Utility Methods
        
        /// <summary>
        /// Perform a complete item identification workflow
        /// </summary>
        public async Task<(LootItem item, bool success)> PerformItemIdentificationAsync(LootItem item, int characterId)
        {
            try
            {
                // Get character's identification skill
                int skillLevel = await GetCharacterIdentificationSkillAsync(characterId);
                
                // Create identification request
                var request = new ItemIdentificationRequest
                {
                    Item = item,
                    CharacterId = characterId,
                    SkillLevel = skillLevel,
                    Method = "skill"
                };
                
                // Perform identification
                var result = await lootService.IdentifyItemAsync(request);
                
                // Track skill usage
                OnCharacterSkillUsed?.Invoke(characterId, skillLevel);
                
                return (result.item, result.success);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to perform item identification: {ex.Message}");
                return (item, false);
            }
        }
        
        /// <summary>
        /// Perform a complete item enhancement workflow
        /// </summary>
        public async Task<(LootItem item, bool success)> PerformItemEnhancementAsync(LootItem item, int characterId, string enhancementType)
        {
            try
            {
                // Get character's crafting skill
                int craftingSkill = await GetCharacterCraftingSkillAsync(characterId, "crafting");
                
                // Create enhancement request
                var request = new ItemEnhancementRequest
                {
                    Item = item,
                    CharacterId = characterId,
                    EnhancementType = enhancementType,
                    CharacterCraftSkill = craftingSkill
                };
                
                // Perform enhancement
                var result = await lootService.EnhanceItemAsync(request);
                
                // Track skill usage
                OnCharacterSkillUsed?.Invoke(characterId, craftingSkill);
                
                return (result.item, result.success);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to perform item enhancement: {ex.Message}");
                return (item, false);
            }
        }
        
        #endregion
        
        private void OnDestroy()
        {
            // Unsubscribe from events
            if (lootService != null)
            {
                lootService.OnLootGenerated -= HandleLootGenerated;
                lootService.OnItemIdentified -= HandleItemIdentified;
                lootService.OnItemEnhanced -= HandleItemEnhanced;
                lootService.OnShopInventoryUpdated -= HandleShopInventoryUpdated;
                lootService.OnShopTransactionCompleted -= HandleShopTransactionCompleted;
            }
        }
    }
} 