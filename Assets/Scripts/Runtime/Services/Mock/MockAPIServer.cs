using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using VDM.Runtime.Services.Contracts;
using VisualDM.DTOs.Core.Auth;
using VisualDM.DTOs.Core.Shared;
using VisualDM.DTOs.World.Region;

namespace VDM.Runtime.Services.Mock
{
    /// <summary>
    /// Mock API server that provides simulated backend responses for testing.
    /// Implements all API contracts with realistic but fake data.
    /// </summary>
    public class MockAPIServer : MonoBehaviour
    {
        [Header("Mock Server Configuration")]
        [SerializeField] private bool _enableLogging = true;
        [SerializeField] private float _simulatedLatencyMin = 0.1f;
        [SerializeField] private float _simulatedLatencyMax = 0.5f;
        [SerializeField] private float _failureRate = 0.05f; // 5% chance of simulated failures
        [SerializeField] private bool _autoInitialize = true;
        
        // Mock data stores
        private MockDataStore _dataStore;
        private MockCharacterAPI _characterAPI;
        private MockQuestAPI _questAPI;
        private MockWorldAPI _worldAPI;
        private MockCombatAPI _combatAPI;
        private MockNarrativeAPI _narrativeAPI;
        private MockEconomyAPI _economyAPI;
        private MockFactionAPI _factionAPI;
        
        #region Unity Lifecycle
        
        private void Start()
        {
            if (_autoInitialize)
            {
                InitializeMockServer();
            }
        }
        
        #endregion
        
        #region Initialization
        
        /// <summary>
        /// Initialize the mock API server with sample data
        /// </summary>
        public void InitializeMockServer()
        {
            if (_enableLogging)
                Debug.Log("[MockAPIServer] Initializing mock API server...");
            
            // Initialize data store with sample data
            _dataStore = new MockDataStore();
            _dataStore.GenerateSampleData();
            
            // Initialize mock API services
            _characterAPI = new MockCharacterAPI(_dataStore, this);
            _questAPI = new MockQuestAPI(_dataStore, this);
            _worldAPI = new MockWorldAPI(_dataStore, this);
            _combatAPI = new MockCombatAPI(_dataStore, this);
            _narrativeAPI = new MockNarrativeAPI(_dataStore, this);
            _economyAPI = new MockEconomyAPI(_dataStore, this);
            _factionAPI = new MockFactionAPI(_dataStore, this);
            
            if (_enableLogging)
                Debug.Log("[MockAPIServer] Mock API server initialized successfully");
        }
        
        #endregion
        
        #region API Access
        
        /// <summary>
        /// Get the mock character API implementation
        /// </summary>
        public ICharacterAPIContract GetCharacterAPI() => _characterAPI;
        
        /// <summary>
        /// Get the mock quest API implementation
        /// </summary>
        public IQuestAPIContract GetQuestAPI() => _questAPI;
        
        /// <summary>
        /// Get the mock world API implementation
        /// </summary>
        public IWorldAPIContract GetWorldAPI() => _worldAPI;
        
        /// <summary>
        /// Get the mock combat API implementation
        /// </summary>
        public ICombatAPIContract GetCombatAPI() => _combatAPI;
        
        /// <summary>
        /// Get the mock narrative API implementation
        /// </summary>
        public INarrativeAPIContract GetNarrativeAPI() => _narrativeAPI;
        
        /// <summary>
        /// Get the mock economy API implementation
        /// </summary>
        public IEconomyAPIContract GetEconomyAPI() => _economyAPI;
        
        /// <summary>
        /// Get the mock faction API implementation
        /// </summary>
        public IFactionAPIContract GetFactionAPI() => _factionAPI;
        
        #endregion
        
        #region Helper Methods
        
        /// <summary>
        /// Simulate network latency
        /// </summary>
        public async Task SimulateLatencyAsync()
        {
            float delay = UnityEngine.Random.Range(_simulatedLatencyMin, _simulatedLatencyMax);
            await Task.Delay(Mathf.RoundToInt(delay * 1000));
        }
        
        /// <summary>
        /// Check if request should fail (for testing error handling)
        /// </summary>
        public bool ShouldSimulateFailure()
        {
            return UnityEngine.Random.value < _failureRate;
        }
        
        /// <summary>
        /// Log mock API activity
        /// </summary>
        public void LogActivity(string message)
        {
            if (_enableLogging)
                Debug.Log($"[MockAPIServer] {message}");
        }
        
        #endregion
    }
    
    /// <summary>
    /// Mock data store that holds simulated game data
    /// </summary>
    public class MockDataStore
    {
        public Dictionary<string, CharacterDTO> Characters { get; private set; } = new Dictionary<string, CharacterDTO>();
        public Dictionary<string, QuestDTO> Quests { get; private set; } = new Dictionary<string, QuestDTO>();
        public Dictionary<string, RegionDTO> Regions { get; private set; } = new Dictionary<string, RegionDTO>();
        public Dictionary<string, LocationDTO> Locations { get; private set; } = new Dictionary<string, LocationDTO>();
        public Dictionary<string, ItemDTO> Items { get; private set; } = new Dictionary<string, ItemDTO>();
        public Dictionary<string, FactionDTO> Factions { get; private set; } = new Dictionary<string, FactionDTO>();
        public Dictionary<string, CombatSessionDTO> CombatSessions { get; private set; } = new Dictionary<string, CombatSessionDTO>();
        public Dictionary<string, NarrativeArcDTO> NarrativeArcs { get; private set; } = new Dictionary<string, NarrativeArcDTO>();
        
        // Character-specific data
        public Dictionary<string, CharacterInventoryDTO> CharacterInventories { get; private set; } = new Dictionary<string, CharacterInventoryDTO>();
        public Dictionary<string, List<string>> CharacterQuests { get; private set; } = new Dictionary<string, List<string>>();
        public Dictionary<string, Dictionary<string, int>> CharacterFactionStandings { get; private set; } = new Dictionary<string, Dictionary<string, int>>();
        
        /// <summary>
        /// Generate sample data for testing
        /// </summary>
        public void GenerateSampleData()
        {
            GenerateSampleCharacters();
            GenerateSampleQuests();
            GenerateSampleRegions();
            GenerateSampleLocations();
            GenerateSampleItems();
            GenerateSampleFactions();
            GenerateSampleNarrativeArcs();
            GenerateCharacterData();
        }
        
        private void GenerateSampleCharacters()
        {
            Characters["char001"] = new CharacterDTO { Id = "char001", Name = "Aeliana Stormwind" };
            Characters["char002"] = new CharacterDTO { Id = "char002", Name = "Thorin Ironbeard" };
            Characters["char003"] = new CharacterDTO { Id = "char003", Name = "Luna Shadowmere" };
            Characters["char004"] = new CharacterDTO { Id = "char004", Name = "Gareth Brightblade" };
            Characters["char005"] = new CharacterDTO { Id = "char005", Name = "Zara Fireweaver" };
        }
        
        private void GenerateSampleQuests()
        {
            Quests["quest001"] = new QuestDTO { Id = "quest001", Title = "The Ancient Prophecy" };
            Quests["quest002"] = new QuestDTO { Id = "quest002", Title = "Rescue the Village" };
            Quests["quest003"] = new QuestDTO { Id = "quest003", Title = "The Lost Artifact" };
            Quests["quest004"] = new QuestDTO { Id = "quest004", Title = "Political Intrigue" };
            Quests["quest005"] = new QuestDTO { Id = "quest005", Title = "The Dragon's Hoard" };
        }
        
        private void GenerateSampleRegions()
        {
            Regions["region001"] = new RegionDTO { Id = "region001", Name = "Elderwood Forest", Type = RegionTypeDTO.Forest };
            Regions["region002"] = new RegionDTO { Id = "region002", Name = "Frostpeak Mountains", Type = RegionTypeDTO.Mountain };
            Regions["region003"] = new RegionDTO { Id = "region003", Name = "Sunward Plains", Type = RegionTypeDTO.Grassland };
            Regions["region004"] = new RegionDTO { Id = "region004", Name = "Shadowmere Swamps", Type = RegionTypeDTO.Swamp };
            Regions["region005"] = new RegionDTO { Id = "region005", Name = "Crimson Desert", Type = RegionTypeDTO.Desert };
        }
        
        private void GenerateSampleLocations()
        {
            Locations["loc001"] = new LocationDTO { Id = "loc001", Name = "Silverleaf Tavern" };
            Locations["loc002"] = new LocationDTO { Id = "loc002", Name = "The Grand Library" };
            Locations["loc003"] = new LocationDTO { Id = "loc003", Name = "Ironforge Smithy" };
            Locations["loc004"] = new LocationDTO { Id = "loc004", Name = "Mystic Temple" };
            Locations["loc005"] = new LocationDTO { Id = "loc005", Name = "Trading Post" };
        }
        
        private void GenerateSampleItems()
        {
            Items["item001"] = new ItemDTO { Id = "item001", Name = "Sword of Valor" };
            Items["item002"] = new ItemDTO { Id = "item002", Name = "Healing Potion" };
            Items["item003"] = new ItemDTO { Id = "item003", Name = "Ancient Scroll" };
            Items["item004"] = new ItemDTO { Id = "item004", Name = "Mithril Armor" };
            Items["item005"] = new ItemDTO { Id = "item005", Name = "Magic Ring" };
        }
        
        private void GenerateSampleFactions()
        {
            Factions["faction001"] = new FactionDTO { Id = "faction001", Name = "Order of the Silver Dawn" };
            Factions["faction002"] = new FactionDTO { Id = "faction002", Name = "Thieves Guild" };
            Factions["faction003"] = new FactionDTO { Id = "faction003", Name = "Mages Circle" };
            Factions["faction004"] = new FactionDTO { Id = "faction004", Name = "Royal Guard" };
            Factions["faction005"] = new FactionDTO { Id = "faction005", Name = "Merchants Alliance" };
        }
        
        private void GenerateSampleNarrativeArcs()
        {
            NarrativeArcs["arc001"] = new NarrativeArcDTO { Id = "arc001", Title = "The Rise of the Shadow Lord" };
            NarrativeArcs["arc002"] = new NarrativeArcDTO { Id = "arc002", Title = "The Great Alliance" };
            NarrativeArcs["arc003"] = new NarrativeArcDTO { Id = "arc003", Title = "Mysteries of the Ancient World" };
        }
        
        private void GenerateCharacterData()
        {
            // Generate inventories
            foreach (var character in Characters.Values)
            {
                CharacterInventories[character.Id] = new CharacterInventoryDTO
                {
                    Items = new List<InventoryItemDTO>
                    {
                        new InventoryItemDTO { ItemId = "item002", Quantity = 3 }, // Healing Potions
                        new InventoryItemDTO { ItemId = "item003", Quantity = 1 }  // Ancient Scroll
                    }
                };
                
                // Assign some quests
                CharacterQuests[character.Id] = new List<string> { "quest001", "quest002" };
                
                // Set faction standings
                CharacterFactionStandings[character.Id] = new Dictionary<string, int>
                {
                    { "faction001", 50 },
                    { "faction002", -10 },
                    { "faction003", 25 }
                };
            }
        }
    }
}

#region Mock API Implementations

namespace VDM.Runtime.Services.Mock
{
    /// <summary>
    /// Base class for mock API implementations
    /// </summary>
    public abstract class MockAPIBase : IAPIContract
    {
        protected MockDataStore _dataStore;
        protected MockAPIServer _server;
        
        public abstract string ServiceName { get; }
        public virtual string ApiVersion => "1.0";
        public string BaseUrl { get; set; } = "http://localhost:3000/api";
        public virtual bool IsServiceAvailable => true;
        
        protected MockAPIBase(MockDataStore dataStore, MockAPIServer server)
        {
            _dataStore = dataStore;
            _server = server;
        }
        
        public virtual async Task<bool> TestConnectionAsync()
        {
            await _server.SimulateLatencyAsync();
            return !_server.ShouldSimulateFailure();
        }
        
        public virtual async Task<ServiceHealthResponse> GetHealthStatusAsync()
        {
            await _server.SimulateLatencyAsync();
            
            return new ServiceHealthResponse
            {
                IsHealthy = !_server.ShouldSimulateFailure(),
                Status = "Mock Service Online",
                ResponseTimeMs = UnityEngine.Random.Range(50, 200),
                Version = ApiVersion,
                Details = new Dictionary<string, object>
                {
                    { "service", ServiceName },
                    { "mock", true },
                    { "uptime", DateTime.UtcNow.ToString() }
                }
            };
        }
        
        public virtual async Task InitializeAsync(APIServiceConfig config)
        {
            await _server.SimulateLatencyAsync();
            BaseUrl = config.BaseUrl;
            _server.LogActivity($"{ServiceName} initialized with config");
        }
        
        public virtual async Task DisposeAsync()
        {
            await Task.CompletedTask;
            _server.LogActivity($"{ServiceName} disposed");
        }
        
        protected APIResponse<T> CreateSuccessResponse<T>(T data)
        {
            return new APIResponse<T>
            {
                IsSuccess = true,
                Data = data,
                Metadata = new APIResponseMetadata
                {
                    Timestamp = DateTime.UtcNow,
                    ResponseTimeMs = UnityEngine.Random.Range(50, 200),
                    RequestId = Guid.NewGuid().ToString(),
                    ApiVersion = ApiVersion
                }
            };
        }
        
        protected APIResponse<T> CreateErrorResponse<T>(string error, string errorCode = "MOCK_ERROR")
        {
            return new APIResponse<T>
            {
                IsSuccess = false,
                Error = error,
                ErrorCode = errorCode,
                Metadata = new APIResponseMetadata
                {
                    Timestamp = DateTime.UtcNow,
                    ResponseTimeMs = UnityEngine.Random.Range(50, 200),
                    RequestId = Guid.NewGuid().ToString(),
                    ApiVersion = ApiVersion
                }
            };
        }
    }
    
    /// <summary>
    /// Mock character API implementation
    /// </summary>
    public class MockCharacterAPI : MockAPIBase, ICharacterAPIContract
    {
        public override string ServiceName => "Character API";
        
        public MockCharacterAPI(MockDataStore dataStore, MockAPIServer server) : base(dataStore, server) { }
        
        public async Task<APIResponse<CharacterDTO>> GetCharacterAsync(string characterId)
        {
            await _server.SimulateLatencyAsync();
            _server.LogActivity($"Get character: {characterId}");
            
            if (_server.ShouldSimulateFailure())
                return CreateErrorResponse<CharacterDTO>("Simulated failure");
            
            if (_dataStore.Characters.TryGetValue(characterId, out var character))
                return CreateSuccessResponse(character);
            
            return CreateErrorResponse<CharacterDTO>("Character not found", "NOT_FOUND");
        }
        
        public async Task<APIResponse<List<CharacterDTO>>> GetCharactersAsync(APIQueryParams queryParams = null)
        {
            await _server.SimulateLatencyAsync();
            _server.LogActivity("Get characters list");
            
            if (_server.ShouldSimulateFailure())
                return CreateErrorResponse<List<CharacterDTO>>("Simulated failure");
            
            var characters = new List<CharacterDTO>(_dataStore.Characters.Values);
            return CreateSuccessResponse(characters);
        }
        
        public async Task<APIResponse<CharacterDTO>> CreateCharacterAsync(CreateCharacterRequestDTO request)
        {
            await _server.SimulateLatencyAsync();
            _server.LogActivity($"Create character: {request.Name}");
            
            if (_server.ShouldSimulateFailure())
                return CreateErrorResponse<CharacterDTO>("Simulated failure");
            
            var character = new CharacterDTO
            {
                Id = Guid.NewGuid().ToString(),
                Name = request.Name
            };
            
            _dataStore.Characters[character.Id] = character;
            return CreateSuccessResponse(character);
        }
        
        public async Task<APIResponse<CharacterDTO>> UpdateCharacterAsync(string characterId, UpdateCharacterRequestDTO request)
        {
            await _server.SimulateLatencyAsync();
            _server.LogActivity($"Update character: {characterId}");
            
            if (_server.ShouldSimulateFailure())
                return CreateErrorResponse<CharacterDTO>("Simulated failure");
            
            if (_dataStore.Characters.TryGetValue(characterId, out var character))
            {
                character.Name = request.Name;
                return CreateSuccessResponse(character);
            }
            
            return CreateErrorResponse<CharacterDTO>("Character not found", "NOT_FOUND");
        }
        
        public async Task<APIResponse<bool>> DeleteCharacterAsync(string characterId)
        {
            await _server.SimulateLatencyAsync();
            _server.LogActivity($"Delete character: {characterId}");
            
            if (_server.ShouldSimulateFailure())
                return CreateErrorResponse<bool>("Simulated failure");
            
            bool removed = _dataStore.Characters.Remove(characterId);
            return CreateSuccessResponse(removed);
        }
        
        // Character attributes and stats (simplified implementations)
        public async Task<APIResponse<CharacterAttributesDTO>> GetCharacterAttributesAsync(string characterId)
        {
            await _server.SimulateLatencyAsync();
            var attributes = new CharacterAttributesDTO();
            attributes.Attributes["Strength"] = 15;
            attributes.Attributes["Dexterity"] = 12;
            attributes.Attributes["Intelligence"] = 14;
            return CreateSuccessResponse(attributes);
        }
        
        public async Task<APIResponse<CharacterAttributesDTO>> UpdateCharacterAttributesAsync(string characterId, CharacterAttributesDTO attributes)
        {
            await _server.SimulateLatencyAsync();
            return CreateSuccessResponse(attributes);
        }
        
        public async Task<APIResponse<List<CharacterAbilityDTO>>> GetCharacterAbilitiesAsync(string characterId)
        {
            await _server.SimulateLatencyAsync();
            var abilities = new List<CharacterAbilityDTO>
            {
                new CharacterAbilityDTO { Id = "ability001", Name = "Fireball" },
                new CharacterAbilityDTO { Id = "ability002", Name = "Heal" }
            };
            return CreateSuccessResponse(abilities);
        }
        
        public async Task<APIResponse<bool>> AddCharacterAbilityAsync(string characterId, string abilityId)
        {
            await _server.SimulateLatencyAsync();
            return CreateSuccessResponse(true);
        }
        
        public async Task<APIResponse<bool>> RemoveCharacterAbilityAsync(string characterId, string abilityId)
        {
            await _server.SimulateLatencyAsync();
            return CreateSuccessResponse(true);
        }
        
        // Character equipment and inventory
        public async Task<APIResponse<CharacterInventoryDTO>> GetCharacterInventoryAsync(string characterId)
        {
            await _server.SimulateLatencyAsync();
            
            if (_dataStore.CharacterInventories.TryGetValue(characterId, out var inventory))
                return CreateSuccessResponse(inventory);
            
            return CreateSuccessResponse(new CharacterInventoryDTO());
        }
        
        public async Task<APIResponse<bool>> AddItemToInventoryAsync(string characterId, string itemId, int quantity = 1)
        {
            await _server.SimulateLatencyAsync();
            _server.LogActivity($"Add item {itemId} to character {characterId}");
            return CreateSuccessResponse(true);
        }
        
        public async Task<APIResponse<bool>> RemoveItemFromInventoryAsync(string characterId, string itemId, int quantity = 1)
        {
            await _server.SimulateLatencyAsync();
            _server.LogActivity($"Remove item {itemId} from character {characterId}");
            return CreateSuccessResponse(true);
        }
        
        public async Task<APIResponse<CharacterEquipmentDTO>> GetCharacterEquipmentAsync(string characterId)
        {
            await _server.SimulateLatencyAsync();
            var equipment = new CharacterEquipmentDTO();
            equipment.EquippedItems["weapon"] = "item001"; // Sword of Valor
            equipment.EquippedItems["armor"] = "item004";  // Mithril Armor
            return CreateSuccessResponse(equipment);
        }
        
        public async Task<APIResponse<bool>> EquipItemAsync(string characterId, string itemId, string slot)
        {
            await _server.SimulateLatencyAsync();
            _server.LogActivity($"Equip item {itemId} to slot {slot} for character {characterId}");
            return CreateSuccessResponse(true);
        }
        
        public async Task<APIResponse<bool>> UnequipItemAsync(string characterId, string slot)
        {
            await _server.SimulateLatencyAsync();
            _server.LogActivity($"Unequip slot {slot} for character {characterId}");
            return CreateSuccessResponse(true);
        }
        
        // Character relationships and social
        public async Task<APIResponse<List<CharacterRelationshipDTO>>> GetCharacterRelationshipsAsync(string characterId)
        {
            await _server.SimulateLatencyAsync();
            var relationships = new List<CharacterRelationshipDTO>
            {
                new CharacterRelationshipDTO { TargetCharacterId = "char002", RelationshipValue = 75 },
                new CharacterRelationshipDTO { TargetCharacterId = "char003", RelationshipValue = 50 }
            };
            return CreateSuccessResponse(relationships);
        }
        
        public async Task<APIResponse<CharacterRelationshipDTO>> UpdateCharacterRelationshipAsync(string characterId, string targetCharacterId, CharacterRelationshipDTO relationship)
        {
            await _server.SimulateLatencyAsync();
            _server.LogActivity($"Update relationship between {characterId} and {targetCharacterId}");
            return CreateSuccessResponse(relationship);
        }
    }
    
    // Additional mock API implementations would follow similar patterns...
    // For brevity, I'll create placeholder implementations for the other services
    
    public class MockQuestAPI : MockAPIBase, IQuestAPIContract
    {
        public override string ServiceName => "Quest API";
        public MockQuestAPI(MockDataStore dataStore, MockAPIServer server) : base(dataStore, server) { }
        
        public async Task<APIResponse<QuestDTO>> GetQuestAsync(string questId)
        {
            await _server.SimulateLatencyAsync();
            if (_dataStore.Quests.TryGetValue(questId, out var quest))
                return CreateSuccessResponse(quest);
            return CreateErrorResponse<QuestDTO>("Quest not found");
        }
        
        // Additional quest methods would be implemented similarly...
        public async Task<APIResponse<List<QuestDTO>>> GetQuestsAsync(APIQueryParams queryParams = null) => throw new NotImplementedException();
        public async Task<APIResponse<QuestDTO>> CreateQuestAsync(CreateQuestRequestDTO request) => throw new NotImplementedException();
        public async Task<APIResponse<QuestDTO>> UpdateQuestAsync(string questId, UpdateQuestRequestDTO request) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> DeleteQuestAsync(string questId) => throw new NotImplementedException();
        public async Task<APIResponse<QuestProgressDTO>> GetQuestProgressAsync(string questId, string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> StartQuestAsync(string questId, string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> CompleteQuestObjectiveAsync(string questId, string objectiveId, string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> CompleteQuestAsync(string questId, string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> AbandonQuestAsync(string questId, string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<List<QuestDTO>>> GetAvailableQuestsAsync(string characterId, string regionId = null) => throw new NotImplementedException();
        public async Task<APIResponse<List<QuestDTO>>> GetActiveQuestsAsync(string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<List<QuestDTO>>> GetCompletedQuestsAsync(string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<QuestRewardsDTO>> GetQuestRewardsAsync(string questId) => throw new NotImplementedException();
        public async Task<APIResponse<QuestRequirementsDTO>> GetQuestRequirementsAsync(string questId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> ClaimQuestRewardsAsync(string questId, string characterId) => throw new NotImplementedException();
    }
    
    // Placeholder implementations for other mock APIs
    public class MockWorldAPI : MockAPIBase, IWorldAPIContract
    {
        public override string ServiceName => "World API";
        public MockWorldAPI(MockDataStore dataStore, MockAPIServer server) : base(dataStore, server) { }
        
        // Implementing all interface methods as NotImplementedException for now
        public async Task<APIResponse<WorldStateDTO>> GetWorldStateAsync() => throw new NotImplementedException();
        public async Task<APIResponse<List<RegionDTO>>> GetRegionsAsync(APIQueryParams queryParams = null) => throw new NotImplementedException();
        public async Task<APIResponse<RegionDTO>> GetRegionAsync(string regionId) => throw new NotImplementedException();
        public async Task<APIResponse<RegionMapDTO>> GetRegionMapAsync(string regionId) => throw new NotImplementedException();
        public async Task<APIResponse<LocationDTO>> GetLocationAsync(string locationId) => throw new NotImplementedException();
        public async Task<APIResponse<List<LocationDTO>>> GetLocationsInRegionAsync(string regionId) => throw new NotImplementedException();
        public async Task<APIResponse<List<LocationDTO>>> GetNearbyLocationsAsync(CoordinateSchemaDTO coordinates, float radius) => throw new NotImplementedException();
        public async Task<APIResponse<List<PointOfInterestDTO>>> GetPointsOfInterestAsync(string regionId) => throw new NotImplementedException();
        public async Task<APIResponse<PointOfInterestDTO>> GetPointOfInterestAsync(string poiId) => throw new NotImplementedException();
        public async Task<APIResponse<List<PointOfInterestDTO>>> DiscoverNearbyPOIsAsync(string characterId, CoordinateSchemaDTO coordinates) => throw new NotImplementedException();
        public async Task<APIResponse<WeatherDataDTO>> GetCurrentWeatherAsync(string regionId) => throw new NotImplementedException();
        public async Task<APIResponse<List<WeatherDataDTO>>> GetWeatherForecastAsync(string regionId, int days = 7) => throw new NotImplementedException();
        public async Task<APIResponse<EnvironmentalDataDTO>> GetEnvironmentalDataAsync(string regionId) => throw new NotImplementedException();
        public async Task<APIResponse<List<WorldEventDTO>>> GetActiveWorldEventsAsync(string regionId = null) => throw new NotImplementedException();
        public async Task<APIResponse<WorldEventDTO>> GetWorldEventAsync(string eventId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> ParticipateInWorldEventAsync(string eventId, string characterId) => throw new NotImplementedException();
    }
    
    public class MockCombatAPI : MockAPIBase, ICombatAPIContract
    {
        public override string ServiceName => "Combat API";
        public MockCombatAPI(MockDataStore dataStore, MockAPIServer server) : base(dataStore, server) { }
        
        // Placeholder implementations
        public async Task<APIResponse<CombatSessionDTO>> CreateCombatSessionAsync(CreateCombatRequestDTO request) => throw new NotImplementedException();
        public async Task<APIResponse<CombatSessionDTO>> GetCombatSessionAsync(string sessionId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> JoinCombatSessionAsync(string sessionId, string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> LeaveCombatSessionAsync(string sessionId, string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> EndCombatSessionAsync(string sessionId) => throw new NotImplementedException();
        public async Task<APIResponse<CombatTurnDTO>> GetCurrentTurnAsync(string sessionId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> PerformCombatActionAsync(string sessionId, CombatActionRequestDTO action) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> EndTurnAsync(string sessionId, string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<List<CombatActionDTO>>> GetAvailableActionsAsync(string sessionId, string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<List<CombatantDTO>>> GetCombalantsAsync(string sessionId) => throw new NotImplementedException();
        public async Task<APIResponse<CombatantDTO>> GetCombatantStatusAsync(string sessionId, string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<List<CombatLogEntryDTO>>> GetCombatLogAsync(string sessionId, int page = 1, int pageSize = 50) => throw new NotImplementedException();
        public async Task<APIResponse<CombatStatisticsDTO>> GetCombatStatisticsAsync(string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<CombatAnalysisDTO>> GetCombatAnalysisAsync(string sessionId) => throw new NotImplementedException();
    }
    
    public class MockNarrativeAPI : MockAPIBase, INarrativeAPIContract
    {
        public override string ServiceName => "Narrative API";
        public MockNarrativeAPI(MockDataStore dataStore, MockAPIServer server) : base(dataStore, server) { }
        
        // Placeholder implementations
        public async Task<APIResponse<NarrativeArcDTO>> GetNarrativeArcAsync(string arcId) => throw new NotImplementedException();
        public async Task<APIResponse<List<NarrativeArcDTO>>> GetActiveArcsAsync(string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<NarrativeArcDTO>> CreateNarrativeArcAsync(CreateNarrativeArcRequestDTO request) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> AdvanceNarrativeArcAsync(string arcId, string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<List<StoryEventDTO>>> GetStoryEventsAsync(string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> TriggerStoryEventAsync(string eventId, string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<List<StoryTriggerDTO>>> GetAvailableTriggersAsync(string characterId, string regionId = null) => throw new NotImplementedException();
        public async Task<APIResponse<DialogueDTO>> GetDialogueAsync(string dialogueId) => throw new NotImplementedException();
        public async Task<APIResponse<DialogueStateDTO>> StartDialogueAsync(string dialogueId, string characterId, string npcId) => throw new NotImplementedException();
        public async Task<APIResponse<DialogueStateDTO>> RespondToDialogueAsync(string dialogueStateId, int responseIndex) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> EndDialogueAsync(string dialogueStateId) => throw new NotImplementedException();
        public async Task<APIResponse<CharacterProgressionDTO>> GetCharacterProgressionAsync(string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<List<AchievementDTO>>> GetCharacterAchievementsAsync(string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> UnlockAchievementAsync(string characterId, string achievementId) => throw new NotImplementedException();
        public async Task<APIResponse<List<MemoryDTO>>> GetCharacterMemoriesAsync(string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<MemoryDTO>> CreateMemoryAsync(string characterId, CreateMemoryRequestDTO request) => throw new NotImplementedException();
        public async Task<APIResponse<List<RumorDTO>>> GetRegionRumorsAsync(string regionId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> SpreadRumorAsync(string rumorId, string characterId, string targetRegionId) => throw new NotImplementedException();
    }
    
    public class MockEconomyAPI : MockAPIBase, IEconomyAPIContract
    {
        public override string ServiceName => "Economy API";
        public MockEconomyAPI(MockDataStore dataStore, MockAPIServer server) : base(dataStore, server) { }
        
        // Placeholder implementations
        public async Task<APIResponse<ItemDTO>> GetItemAsync(string itemId) => throw new NotImplementedException();
        public async Task<APIResponse<List<ItemDTO>>> GetItemsAsync(APIQueryParams queryParams = null) => throw new NotImplementedException();
        public async Task<APIResponse<ItemDTO>> CreateItemAsync(CreateItemRequestDTO request) => throw new NotImplementedException();
        public async Task<APIResponse<ItemDTO>> UpdateItemAsync(string itemId, UpdateItemRequestDTO request) => throw new NotImplementedException();
        public async Task<APIResponse<List<TradeOfferDTO>>> GetMarketplaceOffersAsync(string regionId) => throw new NotImplementedException();
        public async Task<APIResponse<TradeOfferDTO>> CreateTradeOfferAsync(CreateTradeOfferRequestDTO request) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> AcceptTradeOfferAsync(string offerId, string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> CancelTradeOfferAsync(string offerId, string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<PriceDataDTO>> GetItemPriceAsync(string itemId, string regionId) => throw new NotImplementedException();
        public async Task<APIResponse<EconomicDataDTO>> GetRegionEconomicDataAsync(string regionId) => throw new NotImplementedException();
        public async Task<APIResponse<List<PriceHistoryDTO>>> GetPriceHistoryAsync(string itemId, string regionId, int days = 30) => throw new NotImplementedException();
        public async Task<APIResponse<CurrencyBalanceDTO>> GetCharacterCurrencyAsync(string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> TransferCurrencyAsync(string fromCharacterId, string toCharacterId, CurrencyTransferRequestDTO request) => throw new NotImplementedException();
        public async Task<APIResponse<List<TransactionHistoryDTO>>> GetTransactionHistoryAsync(string characterId, APIQueryParams queryParams = null) => throw new NotImplementedException();
    }
    
    public class MockFactionAPI : MockAPIBase, IFactionAPIContract
    {
        public override string ServiceName => "Faction API";
        public MockFactionAPI(MockDataStore dataStore, MockAPIServer server) : base(dataStore, server) { }
        
        // Placeholder implementations
        public async Task<APIResponse<FactionDTO>> GetFactionAsync(string factionId) => throw new NotImplementedException();
        public async Task<APIResponse<List<FactionDTO>>> GetFactionsAsync(APIQueryParams queryParams = null) => throw new NotImplementedException();
        public async Task<APIResponse<List<FactionDTO>>> GetRegionFactionsAsync(string regionId) => throw new NotImplementedException();
        public async Task<APIResponse<FactionRelationshipDTO>> GetFactionRelationshipAsync(string factionId1, string factionId2) => throw new NotImplementedException();
        public async Task<APIResponse<List<FactionRelationshipDTO>>> GetFactionRelationshipsAsync(string factionId) => throw new NotImplementedException();
        public async Task<APIResponse<FactionStandingDTO>> GetCharacterFactionStandingAsync(string characterId, string factionId) => throw new NotImplementedException();
        public async Task<APIResponse<List<FactionStandingDTO>>> GetCharacterFactionStandingsAsync(string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<List<PoliticalEventDTO>>> GetActivePoliticalEventsAsync(string regionId = null) => throw new NotImplementedException();
        public async Task<APIResponse<PoliticalEventDTO>> GetPoliticalEventAsync(string eventId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> ParticipateInPoliticalEventAsync(string eventId, string characterId, string choice) => throw new NotImplementedException();
        public async Task<APIResponse<List<FactionMissionDTO>>> GetAvailableFactionMissionsAsync(string characterId, string factionId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> AcceptFactionMissionAsync(string missionId, string characterId) => throw new NotImplementedException();
        public async Task<APIResponse<bool>> CompleteFactionMissionAsync(string missionId, string characterId) => throw new NotImplementedException();
    }
}
#endregion 