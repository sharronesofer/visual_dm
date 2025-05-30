using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using VisualDM.DTOs.Core.Auth;
using VisualDM.DTOs.Core.Shared;
using VisualDM.DTOs.World.Region;
using VDM.Runtime.Services.Contracts;

namespace VDM.Runtime.Services.Contracts
{
    /// <summary>
    /// API contract for character management system
    /// </summary>
    public interface ICharacterAPIContract : IAPIContract
    {
        // Character CRUD operations
        Task<APIResponse<CharacterDTO>> GetCharacterAsync(string characterId);
        Task<APIResponse<List<CharacterDTO>>> GetCharactersAsync(APIQueryParams queryParams = null);
        Task<APIResponse<CharacterDTO>> CreateCharacterAsync(CreateCharacterRequestDTO request);
        Task<APIResponse<CharacterDTO>> UpdateCharacterAsync(string characterId, UpdateCharacterRequestDTO request);
        Task<APIResponse<bool>> DeleteCharacterAsync(string characterId);
        
        // Character attributes and stats
        Task<APIResponse<CharacterAttributesDTO>> GetCharacterAttributesAsync(string characterId);
        Task<APIResponse<CharacterAttributesDTO>> UpdateCharacterAttributesAsync(string characterId, CharacterAttributesDTO attributes);
        Task<APIResponse<List<CharacterAbilityDTO>>> GetCharacterAbilitiesAsync(string characterId);
        Task<APIResponse<bool>> AddCharacterAbilityAsync(string characterId, string abilityId);
        Task<APIResponse<bool>> RemoveCharacterAbilityAsync(string characterId, string abilityId);
        
        // Character equipment and inventory
        Task<APIResponse<CharacterInventoryDTO>> GetCharacterInventoryAsync(string characterId);
        Task<APIResponse<bool>> AddItemToInventoryAsync(string characterId, string itemId, int quantity = 1);
        Task<APIResponse<bool>> RemoveItemFromInventoryAsync(string characterId, string itemId, int quantity = 1);
        Task<APIResponse<CharacterEquipmentDTO>> GetCharacterEquipmentAsync(string characterId);
        Task<APIResponse<bool>> EquipItemAsync(string characterId, string itemId, string slot);
        Task<APIResponse<bool>> UnequipItemAsync(string characterId, string slot);
        
        // Character relationships and social
        Task<APIResponse<List<CharacterRelationshipDTO>>> GetCharacterRelationshipsAsync(string characterId);
        Task<APIResponse<CharacterRelationshipDTO>> UpdateCharacterRelationshipAsync(string characterId, string targetCharacterId, CharacterRelationshipDTO relationship);
    }
    
    /// <summary>
    /// API contract for quest management system
    /// </summary>
    public interface IQuestAPIContract : IAPIContract
    {
        // Quest CRUD operations
        Task<APIResponse<QuestDTO>> GetQuestAsync(string questId);
        Task<APIResponse<List<QuestDTO>>> GetQuestsAsync(APIQueryParams queryParams = null);
        Task<APIResponse<QuestDTO>> CreateQuestAsync(CreateQuestRequestDTO request);
        Task<APIResponse<QuestDTO>> UpdateQuestAsync(string questId, UpdateQuestRequestDTO request);
        Task<APIResponse<bool>> DeleteQuestAsync(string questId);
        
        // Quest progression and state
        Task<APIResponse<QuestProgressDTO>> GetQuestProgressAsync(string questId, string characterId);
        Task<APIResponse<bool>> StartQuestAsync(string questId, string characterId);
        Task<APIResponse<bool>> CompleteQuestObjectiveAsync(string questId, string objectiveId, string characterId);
        Task<APIResponse<bool>> CompleteQuestAsync(string questId, string characterId);
        Task<APIResponse<bool>> AbandonQuestAsync(string questId, string characterId);
        
        // Quest discovery and availability
        Task<APIResponse<List<QuestDTO>>> GetAvailableQuestsAsync(string characterId, string regionId = null);
        Task<APIResponse<List<QuestDTO>>> GetActiveQuestsAsync(string characterId);
        Task<APIResponse<List<QuestDTO>>> GetCompletedQuestsAsync(string characterId);
        
        // Quest rewards and requirements
        Task<APIResponse<QuestRewardsDTO>> GetQuestRewardsAsync(string questId);
        Task<APIResponse<QuestRequirementsDTO>> GetQuestRequirementsAsync(string questId);
        Task<APIResponse<bool>> ClaimQuestRewardsAsync(string questId, string characterId);
    }
    
    /// <summary>
    /// API contract for world and location management system
    /// </summary>
    public interface IWorldAPIContract : IAPIContract
    {
        // World and region operations
        Task<APIResponse<WorldStateDTO>> GetWorldStateAsync();
        Task<APIResponse<List<RegionDTO>>> GetRegionsAsync(APIQueryParams queryParams = null);
        Task<APIResponse<RegionDTO>> GetRegionAsync(string regionId);
        Task<APIResponse<RegionMapDTO>> GetRegionMapAsync(string regionId);
        
        // Location operations
        Task<APIResponse<LocationDTO>> GetLocationAsync(string locationId);
        Task<APIResponse<List<LocationDTO>>> GetLocationsInRegionAsync(string regionId);
        Task<APIResponse<List<LocationDTO>>> GetNearbyLocationsAsync(CoordinateSchemaDTO coordinates, float radius);
        
        // Points of interest
        Task<APIResponse<List<PointOfInterestDTO>>> GetPointsOfInterestAsync(string regionId);
        Task<APIResponse<PointOfInterestDTO>> GetPointOfInterestAsync(string poiId);
        Task<APIResponse<List<PointOfInterestDTO>>> DiscoverNearbyPOIsAsync(string characterId, CoordinateSchemaDTO coordinates);
        
        // Weather and environmental data
        Task<APIResponse<WeatherDataDTO>> GetCurrentWeatherAsync(string regionId);
        Task<APIResponse<List<WeatherDataDTO>>> GetWeatherForecastAsync(string regionId, int days = 7);
        Task<APIResponse<EnvironmentalDataDTO>> GetEnvironmentalDataAsync(string regionId);
        
        // World events and dynamic content
        Task<APIResponse<List<WorldEventDTO>>> GetActiveWorldEventsAsync(string regionId = null);
        Task<APIResponse<WorldEventDTO>> GetWorldEventAsync(string eventId);
        Task<APIResponse<bool>> ParticipateInWorldEventAsync(string eventId, string characterId);
    }
    
    /// <summary>
    /// API contract for combat system
    /// </summary>
    public interface ICombatAPIContract : IAPIContract
    {
        // Combat session management
        Task<APIResponse<CombatSessionDTO>> CreateCombatSessionAsync(CreateCombatRequestDTO request);
        Task<APIResponse<CombatSessionDTO>> GetCombatSessionAsync(string sessionId);
        Task<APIResponse<bool>> JoinCombatSessionAsync(string sessionId, string characterId);
        Task<APIResponse<bool>> LeaveCombatSessionAsync(string sessionId, string characterId);
        Task<APIResponse<bool>> EndCombatSessionAsync(string sessionId);
        
        // Combat actions and turns
        Task<APIResponse<CombatTurnDTO>> GetCurrentTurnAsync(string sessionId);
        Task<APIResponse<bool>> PerformCombatActionAsync(string sessionId, CombatActionRequestDTO action);
        Task<APIResponse<bool>> EndTurnAsync(string sessionId, string characterId);
        Task<APIResponse<List<CombatActionDTO>>> GetAvailableActionsAsync(string sessionId, string characterId);
        
        // Combat state and status
        Task<APIResponse<List<CombatantDTO>>> GetCombalantsAsync(string sessionId);
        Task<APIResponse<CombatantDTO>> GetCombatantStatusAsync(string sessionId, string characterId);
        Task<APIResponse<List<CombatLogEntryDTO>>> GetCombatLogAsync(string sessionId, int page = 1, int pageSize = 50);
        
        // Combat statistics and analysis
        Task<APIResponse<CombatStatisticsDTO>> GetCombatStatisticsAsync(string characterId);
        Task<APIResponse<CombatAnalysisDTO>> GetCombatAnalysisAsync(string sessionId);
    }
    
    /// <summary>
    /// API contract for narrative and story management system
    /// </summary>
    public interface INarrativeAPIContract : IAPIContract
    {
        // Narrative arc management
        Task<APIResponse<NarrativeArcDTO>> GetNarrativeArcAsync(string arcId);
        Task<APIResponse<List<NarrativeArcDTO>>> GetActiveArcsAsync(string characterId);
        Task<APIResponse<NarrativeArcDTO>> CreateNarrativeArcAsync(CreateNarrativeArcRequestDTO request);
        Task<APIResponse<bool>> AdvanceNarrativeArcAsync(string arcId, string characterId);
        
        // Story events and triggers
        Task<APIResponse<List<StoryEventDTO>>> GetStoryEventsAsync(string characterId);
        Task<APIResponse<bool>> TriggerStoryEventAsync(string eventId, string characterId);
        Task<APIResponse<List<StoryTriggerDTO>>> GetAvailableTriggersAsync(string characterId, string regionId = null);
        
        // Dialogue and conversation system
        Task<APIResponse<DialogueDTO>> GetDialogueAsync(string dialogueId);
        Task<APIResponse<DialogueStateDTO>> StartDialogueAsync(string dialogueId, string characterId, string npcId);
        Task<APIResponse<DialogueStateDTO>> RespondToDialogueAsync(string dialogueStateId, int responseIndex);
        Task<APIResponse<bool>> EndDialogueAsync(string dialogueStateId);
        
        // Character development and progression
        Task<APIResponse<CharacterProgressionDTO>> GetCharacterProgressionAsync(string characterId);
        Task<APIResponse<List<AchievementDTO>>> GetCharacterAchievementsAsync(string characterId);
        Task<APIResponse<bool>> UnlockAchievementAsync(string characterId, string achievementId);
        
        // Memory and rumor system
        Task<APIResponse<List<MemoryDTO>>> GetCharacterMemoriesAsync(string characterId);
        Task<APIResponse<MemoryDTO>> CreateMemoryAsync(string characterId, CreateMemoryRequestDTO request);
        Task<APIResponse<List<RumorDTO>>> GetRegionRumorsAsync(string regionId);
        Task<APIResponse<bool>> SpreadRumorAsync(string rumorId, string characterId, string targetRegionId);
    }
    
    /// <summary>
    /// API contract for item and economy management system
    /// </summary>
    public interface IEconomyAPIContract : IAPIContract
    {
        // Item management
        Task<APIResponse<ItemDTO>> GetItemAsync(string itemId);
        Task<APIResponse<List<ItemDTO>>> GetItemsAsync(APIQueryParams queryParams = null);
        Task<APIResponse<ItemDTO>> CreateItemAsync(CreateItemRequestDTO request);
        Task<APIResponse<ItemDTO>> UpdateItemAsync(string itemId, UpdateItemRequestDTO request);
        
        // Trading and marketplace
        Task<APIResponse<List<TradeOfferDTO>>> GetMarketplaceOffersAsync(string regionId);
        Task<APIResponse<TradeOfferDTO>> CreateTradeOfferAsync(CreateTradeOfferRequestDTO request);
        Task<APIResponse<bool>> AcceptTradeOfferAsync(string offerId, string characterId);
        Task<APIResponse<bool>> CancelTradeOfferAsync(string offerId, string characterId);
        
        // Economy and pricing
        Task<APIResponse<PriceDataDTO>> GetItemPriceAsync(string itemId, string regionId);
        Task<APIResponse<EconomicDataDTO>> GetRegionEconomicDataAsync(string regionId);
        Task<APIResponse<List<PriceHistoryDTO>>> GetPriceHistoryAsync(string itemId, string regionId, int days = 30);
        
        // Currency and transactions
        Task<APIResponse<CurrencyBalanceDTO>> GetCharacterCurrencyAsync(string characterId);
        Task<APIResponse<bool>> TransferCurrencyAsync(string fromCharacterId, string toCharacterId, CurrencyTransferRequestDTO request);
        Task<APIResponse<List<TransactionHistoryDTO>>> GetTransactionHistoryAsync(string characterId, APIQueryParams queryParams = null);
    }
    
    /// <summary>
    /// API contract for faction and politics system
    /// </summary>
    public interface IFactionAPIContract : IAPIContract
    {
        // Faction management
        Task<APIResponse<FactionDTO>> GetFactionAsync(string factionId);
        Task<APIResponse<List<FactionDTO>>> GetFactionsAsync(APIQueryParams queryParams = null);
        Task<APIResponse<List<FactionDTO>>> GetRegionFactionsAsync(string regionId);
        
        // Faction relationships and diplomacy
        Task<APIResponse<FactionRelationshipDTO>> GetFactionRelationshipAsync(string factionId1, string factionId2);
        Task<APIResponse<List<FactionRelationshipDTO>>> GetFactionRelationshipsAsync(string factionId);
        Task<APIResponse<FactionStandingDTO>> GetCharacterFactionStandingAsync(string characterId, string factionId);
        Task<APIResponse<List<FactionStandingDTO>>> GetCharacterFactionStandingsAsync(string characterId);
        
        // Political events and conflicts
        Task<APIResponse<List<PoliticalEventDTO>>> GetActivePoliticalEventsAsync(string regionId = null);
        Task<APIResponse<PoliticalEventDTO>> GetPoliticalEventAsync(string eventId);
        Task<APIResponse<bool>> ParticipateInPoliticalEventAsync(string eventId, string characterId, string choice);
        
        // Faction missions and activities
        Task<APIResponse<List<FactionMissionDTO>>> GetAvailableFactionMissionsAsync(string characterId, string factionId);
        Task<APIResponse<bool>> AcceptFactionMissionAsync(string missionId, string characterId);
        Task<APIResponse<bool>> CompleteFactionMissionAsync(string missionId, string characterId);
    }
}

#region DTO Placeholder Definitions
// Note: These would typically be defined in separate DTO files
// Including minimal definitions here for contract completeness

namespace VDM.Runtime.Services.Contracts
{
    // Character DTOs
    [Serializable] public class CharacterDTO { public string Id { get; set; } public string Name { get; set; } }
    [Serializable] public class CreateCharacterRequestDTO { public string Name { get; set; } }
    [Serializable] public class UpdateCharacterRequestDTO { public string Name { get; set; } }
    [Serializable] public class CharacterAttributesDTO { public Dictionary<string, int> Attributes { get; set; } = new Dictionary<string, int>(); }
    [Serializable] public class CharacterAbilityDTO { public string Id { get; set; } public string Name { get; set; } }
    [Serializable] public class CharacterInventoryDTO { public List<InventoryItemDTO> Items { get; set; } = new List<InventoryItemDTO>(); }
    [Serializable] public class CharacterEquipmentDTO { public Dictionary<string, string> EquippedItems { get; set; } = new Dictionary<string, string>(); }
    [Serializable] public class CharacterRelationshipDTO { public string TargetCharacterId { get; set; } public int RelationshipValue { get; set; } }
    [Serializable] public class InventoryItemDTO { public string ItemId { get; set; } public int Quantity { get; set; } }
    
    // Quest DTOs
    [Serializable] public class QuestDTO { public string Id { get; set; } public string Title { get; set; } }
    [Serializable] public class CreateQuestRequestDTO { public string Title { get; set; } }
    [Serializable] public class UpdateQuestRequestDTO { public string Title { get; set; } }
    [Serializable] public class QuestProgressDTO { public string QuestId { get; set; } public int Progress { get; set; } }
    [Serializable] public class QuestRewardsDTO { public List<string> Items { get; set; } = new List<string>(); }
    [Serializable] public class QuestRequirementsDTO { public int Level { get; set; } }
    
    // World DTOs
    [Serializable] public class WorldStateDTO { public string CurrentSeason { get; set; } }
    [Serializable] public class LocationDTO { public string Id { get; set; } public string Name { get; set; } }
    [Serializable] public class PointOfInterestDTO { public string Id { get; set; } public string Name { get; set; } }
    [Serializable] public class WeatherDataDTO { public string Weather { get; set; } }
    [Serializable] public class EnvironmentalDataDTO { public string Environment { get; set; } }
    [Serializable] public class WorldEventDTO { public string Id { get; set; } public string Name { get; set; } }
    
    // Combat DTOs
    [Serializable] public class CombatSessionDTO { public string Id { get; set; } public bool IsActive { get; set; } }
    [Serializable] public class CreateCombatRequestDTO { public List<string> Participants { get; set; } = new List<string>(); }
    [Serializable] public class CombatTurnDTO { public string CurrentCharacterId { get; set; } }
    [Serializable] public class CombatActionRequestDTO { public string ActionType { get; set; } }
    [Serializable] public class CombatActionDTO { public string Id { get; set; } public string Name { get; set; } }
    [Serializable] public class CombatantDTO { public string CharacterId { get; set; } public int Health { get; set; } }
    [Serializable] public class CombatLogEntryDTO { public string Message { get; set; } }
    [Serializable] public class CombatStatisticsDTO { public int Wins { get; set; } public int Losses { get; set; } }
    [Serializable] public class CombatAnalysisDTO { public string Summary { get; set; } }
    
    // Additional DTOs for other contracts...
    [Serializable] public class NarrativeArcDTO { public string Id { get; set; } public string Title { get; set; } }
    [Serializable] public class CreateNarrativeArcRequestDTO { public string Title { get; set; } }
    [Serializable] public class StoryEventDTO { public string Id { get; set; } public string Description { get; set; } }
    [Serializable] public class StoryTriggerDTO { public string Id { get; set; } public string Condition { get; set; } }
    [Serializable] public class DialogueDTO { public string Id { get; set; } public string Text { get; set; } }
    [Serializable] public class DialogueStateDTO { public string Id { get; set; } public string CurrentNode { get; set; } }
    [Serializable] public class CharacterProgressionDTO { public string CharacterId { get; set; } public int Level { get; set; } }
    [Serializable] public class AchievementDTO { public string Id { get; set; } public string Name { get; set; } }
    [Serializable] public class MemoryDTO { public string Id { get; set; } public string Content { get; set; } }
    [Serializable] public class CreateMemoryRequestDTO { public string Content { get; set; } }
    [Serializable] public class RumorDTO { public string Id { get; set; } public string Content { get; set; } }
    
    [Serializable] public class ItemDTO { public string Id { get; set; } public string Name { get; set; } }
    [Serializable] public class CreateItemRequestDTO { public string Name { get; set; } }
    [Serializable] public class UpdateItemRequestDTO { public string Name { get; set; } }
    [Serializable] public class TradeOfferDTO { public string Id { get; set; } public string ItemId { get; set; } }
    [Serializable] public class CreateTradeOfferRequestDTO { public string ItemId { get; set; } }
    [Serializable] public class PriceDataDTO { public string ItemId { get; set; } public decimal Price { get; set; } }
    [Serializable] public class EconomicDataDTO { public string RegionId { get; set; } public decimal GdpPerCapita { get; set; } }
    [Serializable] public class PriceHistoryDTO { public DateTime Date { get; set; } public decimal Price { get; set; } }
    [Serializable] public class CurrencyBalanceDTO { public Dictionary<string, decimal> Balances { get; set; } = new Dictionary<string, decimal>(); }
    [Serializable] public class CurrencyTransferRequestDTO { public string CurrencyType { get; set; } public decimal Amount { get; set; } }
    [Serializable] public class TransactionHistoryDTO { public string Id { get; set; } public decimal Amount { get; set; } }
    
    [Serializable] public class FactionDTO { public string Id { get; set; } public string Name { get; set; } }
    [Serializable] public class FactionRelationshipDTO { public string Faction1Id { get; set; } public string Faction2Id { get; set; } public int Standing { get; set; } }
    [Serializable] public class FactionStandingDTO { public string FactionId { get; set; } public int Standing { get; set; } }
    [Serializable] public class PoliticalEventDTO { public string Id { get; set; } public string Description { get; set; } }
    [Serializable] public class FactionMissionDTO { public string Id { get; set; } public string Title { get; set; } }
}
#endregion 