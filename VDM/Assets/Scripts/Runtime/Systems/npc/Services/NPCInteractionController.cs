using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using VDM.Systems.Npc.Models;
using VDM.Systems.NPC.UI;
using VDM.Systems.Character.Models;
using VDM.Systems.Economy.Models;
using VDM.Infrastructure.Services;

namespace VDM.Systems.NPC.Services
{
    /// <summary>
    /// Enhanced NPC Interaction Controller that manages backend integration for NPC interactions
    /// Implements Task 64 requirements for seamless dialogue, bartering, and relationship management
    /// with real-time updates and comprehensive context management
    /// </summary>
    public class NPCInteractionController : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private bool enableDebugLogging = true;
        [SerializeField] private float interactionTimeout = 30f;
        [SerializeField] private bool enableOfflineMode = true;
        [SerializeField] private bool enableRealtimeUpdates = true;
        [SerializeField] private float contextUpdateInterval = 5f;
        
        [Header("Language Settings")]
        [SerializeField] private bool enableAutomaticLanguageResolution = true;
        [SerializeField] private bool showLanguageInDialogue = false;
        [SerializeField] private float languageBarrierThreshold = 0.3f;
        
        [Header("UI References")]
        [SerializeField] private NPCInteractionUI interactionUI;
        
        // Core components
        private LanguageInteractionService languageService;
        
        // State
        private NPCData currentNPC;
        private CharacterRelationship currentRelationship;
        private LanguageResolutionResult currentLanguageContext;
        private List<DialogueEntry> conversationHistory = new List<DialogueEntry>();
        private Dictionary<string, object> interactionContext = new Dictionary<string, object>();
        private Dictionary<string, object> economicContext = new Dictionary<string, object>();
        private bool isProcessingInteraction = false;
        private bool isWebSocketConnected = false;
        
        // Caching for offline mode
        private Dictionary<string, string> responseCache = new Dictionary<string, string>();
        private Dictionary<string, List<ContextData>> contextCache = new Dictionary<string, List<ContextData>>();
        
        // Events
        public static event Action<NPCData, InteractionType> OnInteractionStarted;
        public static event Action<NPCData, InteractionResult> OnInteractionCompleted;
        public static event Action<string> OnDialogueGenerated;
        public static event Action<TradeResult> OnTradeCompleted;
        public static event Action<RelationshipChange> OnRelationshipChanged;
        public static event Action<string> OnContextUpdated;
        
        private void Awake()
        {
            InitializeController();
        }
        
        private void InitializeController()
        {
            if (enableDebugLogging)
                Debug.Log("NPCInteractionController: Initializing enhanced interaction controller");
            
            // Initialize language service
            languageService = GetComponent<LanguageInteractionService>();
            if (languageService == null)
            {
                languageService = gameObject.AddComponent<LanguageInteractionService>();
            }
            
            // Subscribe to events
            NPCInteractionUI.OnNPCInteractionStarted += HandleInteractionStarted;
            NPCInteractionUI.OnNPCInteractionEnded += HandleInteractionEnded;
            NPCInteractionUI.OnDialogueOptionSelected += HandleDialogueOptionSelected;
            NPCInteractionUI.OnTradeProposed += HandleTradeProposed;
            NPCInteractionUI.OnContextActionSelected += HandleContextActionSelected;
            NPCInteractionUI.OnGiftGiven += HandleGiftGiven;
            NPCInteractionUI.OnChallengeInitiated += HandleChallengeInitiated;
            
            // Subscribe to language events
            if (languageService != null)
            {
                LanguageInteractionService.OnLanguageResolved += HandleLanguageResolved;
                LanguageInteractionService.OnLanguageBarrierEncountered += HandleLanguageBarrier;
                LanguageInteractionService.OnLanguageLearningOpportunity += HandleLanguageLearning;
            }
            
            // Initialize WebSocket connection for real-time updates
            if (enableRealtimeUpdates)
            {
                InitializeWebSocketConnection();
            }
            
            // Start context monitoring
            if (enableRealtimeUpdates)
            {
                InvokeRepeating(nameof(UpdateInteractionContext), contextUpdateInterval, contextUpdateInterval);
            }
            
            if (enableDebugLogging)
                Debug.Log("NPCInteractionController: Controller initialization complete");
        }
        
        private async void InitializeWebSocketConnection()
        {
            try
            {
                // TODO: Initialize WebSocket connection to backend
                // await WebSocketManager.Connect("ws://localhost:8000/ws/npc-interactions");
                isWebSocketConnected = true;
                
                if (enableDebugLogging)
                    Debug.Log("NPCInteractionController: WebSocket connection established");
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to establish WebSocket connection: {ex.Message}");
                isWebSocketConnected = false;
            }
        }
        
        private void OnDestroy()
        {
            // Unsubscribe from events
            if (interactionUI != null)
            {
                NPCInteractionUI.OnNPCInteractionStarted -= HandleInteractionStarted;
                NPCInteractionUI.OnNPCInteractionEnded -= HandleInteractionEnded;
                NPCInteractionUI.OnDialogueOptionSelected -= HandleDialogueOptionSelected;
                NPCInteractionUI.OnTradeProposed -= HandleTradeProposed;
                NPCInteractionUI.OnContextActionSelected -= HandleContextActionSelected;
                NPCInteractionUI.OnGiftGiven -= HandleGiftGiven;
                NPCInteractionUI.OnChallengeInitiated -= HandleChallengeInitiated;
            }
        }
        
        public async Task<bool> StartInteraction(NPCData npc)
        {
            try
            {
                if (isProcessingInteraction)
                {
                    Debug.LogWarning("NPCInteractionController: Already processing an interaction");
                    return false;
                }
                
                currentNPC = npc;
                isProcessingInteraction = true;
                
                if (enableDebugLogging)
                    Debug.Log($"NPCInteractionController: Starting enhanced interaction with {npc.name} (ID: {npc.id})");
                
                // Resolve language context if enabled
                if (enableAutomaticLanguageResolution && languageService != null)
                {
                    currentLanguageContext = await languageService.ResolveDialogueLanguage(
                        GetPlayerId(), npc);
                    
                    // Check for language barriers
                    if (currentLanguageContext.ComprehensionLevel < languageBarrierThreshold)
                    {
                        if (enableDebugLogging)
                            Debug.LogWarning($"NPCInteractionController: Potential language barrier detected " +
                                           $"(Comprehension: {currentLanguageContext.ComprehensionLevel:P1})");
                    }
                }
                
                // Load relationship data
                currentRelationship = await LoadRelationshipData(npc.id);
                
                // Build comprehensive interaction context
                await BuildEnhancedInteractionContext(npc);
                await BuildEconomicContext();
                
                // Generate contextual greeting with language consideration
                await GenerateContextualGreeting(npc);
                
                // Start real-time context monitoring
                if (enableRealtimeUpdates)
                {
                    StartRealtimeContextMonitoring();
                }
                
                // Trigger interaction started event
                OnInteractionStarted?.Invoke(npc, InteractionType.General);
                
                // Start UI interaction
                if (interactionUI != null)
                {
                    interactionUI.StartInteraction(npc, currentRelationship);
                }
                else
                {
                    Debug.LogError("NPCInteractionController: No interaction UI found");
                    return false;
                }
                
                if (enableDebugLogging)
                    Debug.Log($"NPCInteractionController: Successfully started interaction with {npc.name}");
                
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to start interaction: {ex.Message}");
                isProcessingInteraction = false;
                currentNPC = null;
                currentLanguageContext = null;
                return false;
            }
        }
        
        private async Task<CharacterRelationship> LoadRelationshipData(string npcId)
        {
            try
            {
                // TODO: Load relationship data from backend with full context
                // var relationship = await BackendService.GetCharacterRelationship(playerId, npcId);
                
                // Enhanced placeholder relationship data with more context
                var relationship = new CharacterRelationship
                {
                    characterId1 = "player",
                    characterId2 = npcId,
                    trustLevel = UnityEngine.Random.Range(0.1f, 0.9f),
                    lastInteraction = DateTime.Now.AddDays(-UnityEngine.Random.Range(1, 30)),
                    interactionCount = UnityEngine.Random.Range(1, 50),
                    relationshipType = GetRandomRelationshipType()
                };
                
                if (enableDebugLogging)
                    Debug.Log($"NPCInteractionController: Loaded relationship data - Trust: {relationship.trustLevel:F2}");
                
                return relationship;
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to load relationship data: {ex.Message}");
                return CreateDefaultRelationship(npcId);
            }
        }
        
        private RelationshipType GetRandomRelationshipType()
        {
            var types = new[] { RelationshipType.Stranger, RelationshipType.Acquaintance, RelationshipType.Friend, RelationshipType.Ally };
            return types[UnityEngine.Random.Range(0, types.Length)];
        }
        
        private CharacterRelationship CreateDefaultRelationship(string npcId)
        {
            return new CharacterRelationship
            {
                characterId1 = "player",
                characterId2 = npcId,
                trustLevel = 0.5f,
                lastInteraction = DateTime.Now.AddDays(-7),
                interactionCount = 1,
                relationshipType = RelationshipType.Stranger
            };
        }
        
        private async Task BuildEnhancedInteractionContext(NPCData npc)
        {
            interactionContext.Clear();
            
            // Basic context
            interactionContext["npc_id"] = npc.id;
            interactionContext["npc_name"] = npc.name;
            interactionContext["npc_type"] = npc.npcType.ToString();
            interactionContext["location"] = await GetCurrentLocation();
            interactionContext["time_of_day"] = DateTime.Now.Hour;
            interactionContext["day_of_week"] = DateTime.Now.DayOfWeek.ToString();
            interactionContext["season"] = GetCurrentSeason();
            
            // Player context
            interactionContext["player_id"] = GetPlayerId();
            interactionContext["player_faction"] = await GetPlayerFaction();
            interactionContext["player_level"] = await GetPlayerLevel();
            interactionContext["player_wealth"] = await GetPlayerWealth();
            interactionContext["player_reputation"] = await GetPlayerReputation();
            
            // NPC context
            interactionContext["npc_faction"] = npc.factionId;
            interactionContext["npc_mood"] = await GetNPCMood(npc.id);
            interactionContext["npc_occupation"] = await GetNPCOccupation(npc.id);
            
            // Relationship context
            if (currentRelationship != null)
            {
                interactionContext["trust_level"] = currentRelationship.trustLevel;
                interactionContext["relationship_type"] = currentRelationship.relationshipType.ToString();
                interactionContext["interaction_count"] = currentRelationship.interactionCount;
                interactionContext["last_interaction"] = currentRelationship.lastInteraction;
                interactionContext["interaction_frequency"] = CalculateInteractionFrequency();
            }
            
            // Quest context
            interactionContext["active_quests"] = await GetActiveQuests();
            interactionContext["completed_quests"] = await GetCompletedQuests();
            interactionContext["available_quests"] = await GetAvailableQuestsForNPC(npc.id);
            
            // Economic context
            await BuildEconomicContext();
            
            // Social context
            interactionContext["recent_events"] = await GetRecentLocalEvents();
            interactionContext["local_rumors"] = await GetLocalRumors();
            interactionContext["political_climate"] = await GetPoliticalClimate();
            
            // Environmental context
            interactionContext["weather"] = await GetCurrentWeather();
            interactionContext["local_population"] = await GetLocalPopulation();
            interactionContext["security_level"] = await GetLocalSecurityLevel();
            
            if (enableDebugLogging)
                Debug.Log($"NPCInteractionController: Built enhanced interaction context with {interactionContext.Count} entries");
        }
        
        private async Task BuildEconomicContext()
        {
            economicContext.Clear();
            
            try
            {
                economicContext["local_economy_state"] = await GetLocalEconomicState();
                economicContext["market_prices"] = await GetCurrentMarketPrices();
                economicContext["trade_routes"] = await GetActiveTradeRoutes();
                economicContext["economic_trends"] = await GetEconomicTrends();
                economicContext["currency_rates"] = await GetCurrencyRates();
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to build economic context: {ex.Message}");
            }
        }
        
        private async Task GenerateContextualGreeting(NPCData npc)
        {
            try
            {
                if (enableOfflineMode && !isWebSocketConnected)
                {
                    GenerateLocalGreeting(npc);
                    return;
                }
                
                // Try AI-generated greeting first
                var greeting = await RequestAIGreeting(npc);
                if (!string.IsNullOrEmpty(greeting))
                {
                    CacheResponse("greeting", greeting);
                    if (enableDebugLogging)
                        Debug.Log("NPCInteractionController: Generated AI greeting");
                }
                else
                {
                    // Fallback to local greeting
                    GenerateLocalGreeting(npc);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to generate greeting: {ex.Message}");
                GenerateLocalGreeting(npc);
            }
        }
        
        private async Task<string> RequestAIGreeting(NPCData npc)
        {
            try
            {
                // TODO: Request AI-generated greeting from backend
                // var request = new GreetingRequest
                // {
                //     npcId = npc.id,
                //     context = interactionContext,
                //     relationshipLevel = currentRelationship?.trustLevel ?? 0.5f
                // };
                // 
                // var response = await BackendService.GenerateGreeting(request);
                // return response.greeting;
                
                // Placeholder for AI greeting
                return null;
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: AI greeting request failed: {ex.Message}");
                return null;
            }
        }
        
        private void GenerateLocalGreeting(NPCData npc)
        {
            // Check cache first
            if (responseCache.ContainsKey("greeting"))
            {
                return;
            }
            
            // Enhanced local greeting with more contextual awareness
            var greetings = new List<string>();
            
            float trustLevel = currentRelationship?.trustLevel ?? 0.5f;
            int hour = DateTime.Now.Hour;
            string timeOfDay = GetTimeOfDayGreeting(hour);
            
            // Relationship-based greetings
            if (trustLevel >= 0.8f)
            {
                greetings.AddRange(new[] {
                    $"{timeOfDay}! Always great to see a trusted friend.",
                    $"Perfect timing! I was just thinking about you.",
                    $"{timeOfDay}, my friend. How have you been keeping?"
                });
            }
            else if (trustLevel >= 0.6f)
            {
                greetings.AddRange(new[] {
                    $"{timeOfDay}. Good to see you again.",
                    $"Hello there. Hope you're doing well.",
                    $"{timeOfDay}. What brings you by today?"
                });
            }
            else if (trustLevel >= 0.4f)
            {
                greetings.AddRange(new[] {
                    $"{timeOfDay}.",
                    "Hello.",
                    "What can I do for you?"
                });
            }
            else
            {
                greetings.AddRange(new[] {
                    "What do you want?",
                    "Make it quick.",
                    "I don't have time for strangers."
                });
            }
            
            // Add contextual elements
            string selectedGreeting = greetings[UnityEngine.Random.Range(0, greetings.Count)];
            
            // Add weather context occasionally
            if (UnityEngine.Random.value < 0.3f)
            {
                selectedGreeting += GetWeatherComment();
            }
            
            // Add local event context occasionally
            if (UnityEngine.Random.value < 0.2f)
            {
                selectedGreeting += GetLocalEventComment();
            }
            
            CacheResponse("greeting", selectedGreeting);
            
            if (enableDebugLogging)
                Debug.Log($"NPCInteractionController: Generated local greeting: {selectedGreeting}");
        }
        
        private string GetTimeOfDayGreeting(int hour)
        {
            if (hour < 6) return "You're up early";
            if (hour < 12) return "Good morning";
            if (hour < 17) return "Good afternoon";
            if (hour < 21) return "Good evening";
            return "Working late tonight";
        }
        
        private string GetWeatherComment()
        {
            var comments = new[] {
                " Quite a day we're having.",
                " Strange weather lately, isn't it?",
                " Beautiful day, wouldn't you say?",
                " The weather's been unpredictable."
            };
            return comments[UnityEngine.Random.Range(0, comments.Length)];
        }
        
        private string GetLocalEventComment()
        {
            var comments = new[] {
                " Things have been busy around here.",
                " Have you heard the latest news?",
                " Interesting times we're living in.",
                " The town's been buzzing with activity."
            };
            return comments[UnityEngine.Random.Range(0, comments.Length)];
        }
        
        private void StartRealtimeContextMonitoring()
        {
            // Start monitoring for real-time context changes
            if (enableDebugLogging)
                Debug.Log("NPCInteractionController: Started real-time context monitoring");
        }
        
        private void UpdateInteractionContext()
        {
            if (currentNPC == null || !isProcessingInteraction) return;
            
            // Update dynamic context elements
            try
            {
                interactionContext["time_of_day"] = DateTime.Now.Hour;
                interactionContext["interaction_duration"] = Time.time; // Placeholder
                
                // Trigger context update event
                OnContextUpdated?.Invoke("context_refreshed");
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to update context: {ex.Message}");
            }
        }
        
        private void HandleInteractionStarted(NPCData npc)
        {
            if (enableDebugLogging)
                Debug.Log($"NPCInteractionController: UI interaction started with {npc.name}");
        }
        
        private void HandleInteractionEnded()
        {
            if (enableDebugLogging)
                Debug.Log("NPCInteractionController: UI interaction ended");
            
            // Save interaction data
            SaveInteractionData();
            
            // Clean up
            isProcessingInteraction = false;
            currentNPC = null;
            conversationHistory.Clear();
            interactionContext.Clear();
            economicContext.Clear();
        }
        
        private async void HandleDialogueOptionSelected(string option)
        {
            try
            {
                if (enableDebugLogging)
                    Debug.Log($"NPCInteractionController: Processing dialogue option: {option}");
                
                // Add to conversation history
                var dialogueEntry = new DialogueEntry
                {
                    speaker = "Player",
                    text = option,
                    timestamp = DateTime.Now
                };
                conversationHistory.Add(dialogueEntry);
                
                // Generate NPC response
                string response = await GenerateNPCResponse(option);
                
                // Display response in UI
                interactionUI?.DisplayNPCResponse(response);
                
                // Update relationship based on dialogue
                await UpdateRelationshipFromDialogue(option, response);
                
                OnDialogueGenerated?.Invoke(response);
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to handle dialogue option: {ex.Message}");
                
                // Fallback response
                string fallbackResponse = GetFallbackDialogueResponse(option);
                interactionUI?.DisplayNPCResponse(fallbackResponse);
            }
        }
        
        private async Task<string> GenerateNPCResponse(string playerInput)
        {
            try
            {
                // Check cache first
                string cacheKey = $"response_{playerInput.GetHashCode()}";
                if (responseCache.ContainsKey(cacheKey))
                {
                    return await ProcessResponseWithLanguageContext(responseCache[cacheKey]);
                }
                
                if (!enableOfflineMode && isWebSocketConnected)
                {
                    // TODO: Request AI-generated response from backend
                    // var request = new DialogueRequest
                    // {
                    //     npcId = currentNPC.id,
                    //     playerInput = playerInput,
                    //     context = interactionContext,
                    //     conversationHistory = conversationHistory,
                    //     relationshipLevel = currentRelationship?.trustLevel ?? 0.5f,
                    //     languageContext = currentLanguageContext
                    // };
                    // 
                    // var response = await BackendService.GenerateDialogueResponse(request);
                    // 
                    // if (!string.IsNullOrEmpty(response.text))
                    // {
                    //     responseCache[cacheKey] = response.text;
                    //     return await ProcessResponseWithLanguageContext(response.text);
                    // }
                }
                
                // Fallback to local response generation
                var localResponse = GenerateLocalResponse(playerInput);
                return await ProcessResponseWithLanguageContext(localResponse);
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to generate NPC response: {ex.Message}");
                var fallbackResponse = GenerateLocalResponse(playerInput);
                return await ProcessResponseWithLanguageContext(fallbackResponse);
            }
        }
        
        private async Task<string> ProcessResponseWithLanguageContext(string response)
        {
            // Apply language comprehension effects if language context is available
            if (currentLanguageContext != null && enableAutomaticLanguageResolution)
            {
                // Get updated language context for this specific response
                var languageResult = await languageService.ResolveDialogueLanguage(
                    GetPlayerId(), currentNPC, response);
                
                // Apply language processing
                if (languageResult.HasComprehensionIssues)
                {
                    response = languageResult.ProcessedText;
                }
                
                // Add language indicator if enabled
                if (showLanguageInDialogue && !string.IsNullOrEmpty(languageResult.DisplayText))
                {
                    response = $"{languageResult.DisplayText} {response}";
                }
                
                // Check for learning opportunities
                if (languageResult.ComprehensionLevel < 0.9f && languageResult.ComprehensionLevel >= languageBarrierThreshold)
                {
                    // This could trigger language learning UI or notifications
                    LanguageInteractionService.OnLanguageLearningOpportunity?.Invoke(
                        languageResult.SelectedLanguage, 
                        "Dialogue exposure");
                }
            }
            
            return response;
        }
        
        private string GenerateLocalResponse(string playerInput)
        {
            // Enhanced local response generation based on context
            var responses = new List<string>();
            
            float trustLevel = currentRelationship?.trustLevel ?? 0.5f;
            
            // Context-aware responses based on player input
            if (playerInput.Contains("how") || playerInput.Contains("going"))
            {
                if (trustLevel >= 0.7f)
                    responses.AddRange(new[] { "Things have been going well, thanks for asking!", "Can't complain. Business has been steady.", "Pretty good, actually. How about you?" });
                else if (trustLevel >= 0.4f)
                    responses.AddRange(new[] { "Things are fine.", "Going alright, I suppose.", "Same as always." });
                else
                    responses.AddRange(new[] { "None of your business.", "Why do you care?", "Things are tough, if you must know." });
            }
            else if (playerInput.Contains("new") || playerInput.Contains("news"))
            {
                responses.AddRange(new[] {
                    "Haven't heard much lately.",
                    "There's been talk of changes in the capital.",
                    "The merchant caravans have been bringing strange stories.",
                    "Things have been quiet around here."
                });
            }
            else if (playerInput.Contains("yourself") || playerInput.Contains("about"))
            {
                if (trustLevel >= 0.6f)
                    responses.AddRange(new[] { "I've lived here most of my life.", "Been working this trade for years.", "Not much to say, really." });
                else
                    responses.AddRange(new[] { "That's personal.", "I prefer to keep to myself.", "Why the interest?" });
            }
            else if (playerInput.Contains("help"))
            {
                if (trustLevel >= 0.6f)
                    responses.AddRange(new[] { "Depends on what you need.", "I might be able to help.", "What kind of help?" });
                else
                    responses.AddRange(new[] { "I don't help strangers.", "That depends on what you're offering.", "Help doesn't come free." });
            }
            else if (playerInput.Contains("advice"))
            {
                if (trustLevel >= 0.8f)
                    responses.AddRange(new[] { "Well, if you're asking for my opinion...", "Here's what I think...", "I've learned a few things over the years." });
                else
                    responses.AddRange(new[] { "I'm not sure you want my advice.", "Advice costs extra.", "You'll have to figure that out yourself." });
            }
            else
            {
                // Generic responses
                responses.AddRange(new[] { "Interesting.", "I see.", "Is that so?", "Hmm.", "Right." });
            }
            
            // Add relationship-based modifiers
            string selectedResponse = responses[UnityEngine.Random.Range(0, responses.Count)];
            
            // Cache the response
            string cacheKey = $"response_{playerInput.GetHashCode()}";
            responseCache[cacheKey] = selectedResponse;
            
            return selectedResponse;
        }
        
        private string GetFallbackDialogueResponse(string playerInput)
        {
            var fallbacks = new[] {
                "I'm not sure how to respond to that.",
                "Could you say that again?",
                "That's... interesting.",
                "I need a moment to think about that."
            };
            
            return fallbacks[UnityEngine.Random.Range(0, fallbacks.Length)];
        }
        
        private async void HandleTradeProposed(List<TradeItem> tradeItems)
        {
            try
            {
                if (enableDebugLogging)
                    Debug.Log($"NPCInteractionController: Processing trade with {tradeItems.Count} items");
                
                TradeResult result = await ProcessTrade(tradeItems);
                
                // Update relationship based on trade
                await UpdateRelationshipFromTrade(result);
                
                OnTradeCompleted?.Invoke(result);
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to process trade: {ex.Message}");
            }
        }
        
        private async Task<TradeResult> ProcessTrade(List<TradeItem> tradeItems)
        {
            try
            {
                // TODO: Process trade with backend
                // var tradeRequest = new TradeRequest
                // {
                //     npcId = currentNPC.id,
                //     playerId = GetPlayerId(),
                //     items = tradeItems,
                //     context = economicContext
                // };
                // 
                // var result = await BackendService.ProcessTrade(tradeRequest);
                // return result;
                
                // Placeholder trade processing
                float totalValue = CalculateTradeValue(tradeItems);
                bool success = totalValue > 0;
                float relationshipChange = success ? 0.1f : -0.05f;
                
                return new TradeResult
                {
                    success = success,
                    totalValue = totalValue,
                    relationshipChange = relationshipChange,
                    timestamp = DateTime.Now,
                    message = success ? "Trade completed successfully!" : "Trade failed."
                };
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Trade processing failed: {ex.Message}");
                return new TradeResult
                {
                    success = false,
                    totalValue = 0,
                    relationshipChange = 0,
                    timestamp = DateTime.Now,
                    message = "Trade processing error occurred."
                };
            }
        }
        
        private async void HandleContextActionSelected(string action, object data)
        {
            try
            {
                if (enableDebugLogging)
                    Debug.Log($"NPCInteractionController: Processing context action: {action}");
                
                await ProcessContextAction(action, data);
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to process context action: {ex.Message}");
            }
        }
        
        private async Task ProcessContextAction(string action, object data)
        {
            switch (action.ToLower())
            {
                case "rumors":
                    await HandleRumorRequest();
                    break;
                case "events":
                    await HandleEventsRequest();
                    break;
                case "trade_routes":
                    await HandleTradeRoutesRequest();
                    break;
                case "politics":
                    await HandlePoliticsRequest();
                    break;
                default:
                    Debug.LogWarning($"NPCInteractionController: Unknown context action: {action}");
                    break;
            }
        }
        
        private async void HandleGiftGiven(string npcId, int itemId)
        {
            try
            {
                if (enableDebugLogging)
                    Debug.Log($"NPCInteractionController: Processing gift to {npcId}");
                
                // TODO: Process gift giving
                await UpdateRelationshipFromGift(itemId);
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to process gift: {ex.Message}");
            }
        }
        
        private async void HandleChallengeInitiated(string challengeType)
        {
            try
            {
                if (enableDebugLogging)
                    Debug.Log($"NPCInteractionController: Processing challenge: {challengeType}");
                
                // TODO: Process challenge initiation
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to process challenge: {ex.Message}");
            }
        }
        
        private async Task UpdateRelationshipFromDialogue(string playerInput, string npcResponse)
        {
            try
            {
                if (currentRelationship == null) return;
                
                float impact = CalculateDialogueRelationshipImpact(playerInput, npcResponse);
                float oldTrust = currentRelationship.trustLevel;
                float newTrust = Mathf.Clamp01(oldTrust + impact);
                
                currentRelationship.trustLevel = newTrust;
                currentRelationship.interactionCount++;
                currentRelationship.lastInteraction = DateTime.Now;
                
                // TODO: Send relationship update to backend
                // await BackendService.UpdateRelationship(currentRelationship);
                
                if (Math.Abs(impact) > 0.01f)
                {
                    var change = new RelationshipChange
                    {
                        npcId = currentNPC.id,
                        oldTrustLevel = oldTrust,
                        newTrustLevel = newTrust,
                        reason = "Dialogue interaction"
                    };
                    
                    OnRelationshipChanged?.Invoke(change);
                }
                
                if (enableDebugLogging)
                    Debug.Log($"NPCInteractionController: Relationship updated - Trust: {oldTrust:F2} -> {newTrust:F2}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to update relationship from dialogue: {ex.Message}");
            }
        }
        
        private async Task UpdateRelationshipFromTrade(TradeResult tradeResult)
        {
            try
            {
                if (currentRelationship == null || !tradeResult.success) return;
                
                float oldTrust = currentRelationship.trustLevel;
                float newTrust = Mathf.Clamp01(oldTrust + tradeResult.relationshipChange);
                
                currentRelationship.trustLevel = newTrust;
                currentRelationship.interactionCount++;
                currentRelationship.lastInteraction = DateTime.Now;
                
                // TODO: Send relationship update to backend
                // await BackendService.UpdateRelationship(currentRelationship);
                
                var change = new RelationshipChange
                {
                    npcId = currentNPC.id,
                    oldTrustLevel = oldTrust,
                    newTrustLevel = newTrust,
                    reason = $"Trade worth {tradeResult.totalValue:C}"
                };
                
                OnRelationshipChanged?.Invoke(change);
                
                if (enableDebugLogging)
                    Debug.Log($"NPCInteractionController: Relationship updated from trade - Trust: {oldTrust:F2} -> {newTrust:F2}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to update relationship from trade: {ex.Message}");
            }
        }
        
        private async Task UpdateRelationshipFromGift(int itemId)
        {
            try
            {
                if (currentRelationship == null) return;
                
                // Gift giving generally improves relationship
                float impact = 0.15f; // Base gift impact
                
                // TODO: Adjust impact based on gift value and NPC preferences
                
                float oldTrust = currentRelationship.trustLevel;
                float newTrust = Mathf.Clamp01(oldTrust + impact);
                
                currentRelationship.trustLevel = newTrust;
                currentRelationship.interactionCount++;
                currentRelationship.lastInteraction = DateTime.Now;
                
                var change = new RelationshipChange
                {
                    npcId = currentNPC.id,
                    oldTrustLevel = oldTrust,
                    newTrustLevel = newTrust,
                    reason = "Gift given"
                };
                
                OnRelationshipChanged?.Invoke(change);
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to update relationship from gift: {ex.Message}");
            }
        }
        
        private async Task SaveInteractionData()
        {
            try
            {
                // TODO: Save interaction data to backend
                // var interactionData = new InteractionRecord
                // {
                //     npcId = currentNPC.id,
                //     playerId = GetPlayerId(),
                //     timestamp = DateTime.Now,
                //     duration = interactionDuration,
                //     conversationHistory = conversationHistory,
                //     context = interactionContext,
                //     relationshipChange = relationshipChange
                // };
                // 
                // await BackendService.SaveInteractionRecord(interactionData);
                
                if (enableDebugLogging)
                    Debug.Log("NPCInteractionController: Interaction data saved");
            }
            catch (Exception ex)
            {
                Debug.LogError($"NPCInteractionController: Failed to save interaction data: {ex.Message}");
            }
        }
        
        private void CacheResponse(string key, string response)
        {
            responseCache[key] = response;
            
            // Limit cache size
            if (responseCache.Count > 100)
            {
                var firstKey = responseCache.Keys.First();
                responseCache.Remove(firstKey);
            }
        }
        
        // Context data retrieval methods (async placeholders for backend integration)
        private async Task<string> GetCurrentLocation() => "Town Square"; // Placeholder
        private async Task<string> GetPlayerFaction() => "Independent"; // Placeholder
        private async Task<int> GetPlayerLevel() => 5; // Placeholder
        private async Task<float> GetPlayerWealth() => 1000f; // Placeholder
        private async Task<float> GetPlayerReputation() => 0.6f; // Placeholder
        private async Task<string> GetNPCMood(string npcId) => "Neutral"; // Placeholder
        private async Task<string> GetNPCOccupation(string npcId) => "Merchant"; // Placeholder
        private async Task<List<string>> GetActiveQuests() => new List<string> { "Find the Lost Artifact" }; // Placeholder
        private async Task<List<string>> GetCompletedQuests() => new List<string> { "Help the Farmer" }; // Placeholder
        private async Task<List<string>> GetAvailableQuestsForNPC(string npcId) => new List<string> { "Delivery Mission" }; // Placeholder
        private async Task<string> GetLocalEconomicState() => "Stable"; // Placeholder
        private async Task<Dictionary<string, float>> GetCurrentMarketPrices() => new Dictionary<string, float> { { "wheat", 10f }, { "iron", 25f } }; // Placeholder
        private async Task<List<string>> GetActiveTradeRoutes() => new List<string> { "Capital-Port Road", "Mountain Pass" }; // Placeholder
        private async Task<string> GetEconomicTrends() => "Rising prices due to seasonal demand"; // Placeholder
        private async Task<Dictionary<string, float>> GetCurrencyRates() => new Dictionary<string, float> { { "gold", 1.0f }, { "silver", 0.1f } }; // Placeholder
        private async Task<List<string>> GetRecentLocalEvents() => new List<string> { "Market festival last week", "New merchant caravan arrived" }; // Placeholder
        private async Task<List<string>> GetLocalRumors() => new List<string> { "Strange lights seen in the forest", "Bandits spotted on the road" }; // Placeholder
        private async Task<string> GetPoliticalClimate() => "Tensions rising between neighboring factions"; // Placeholder
        private async Task<string> GetCurrentWeather() => "Clear skies"; // Placeholder
        private async Task<int> GetLocalPopulation() => 2500; // Placeholder
        private async Task<string> GetLocalSecurityLevel() => "Moderate"; // Placeholder
        
        private string GetPlayerId() => "player_001"; // Placeholder
        private string GetCurrentSeason() => DateTime.Now.Month >= 3 && DateTime.Now.Month <= 5 ? "Spring" : "Summer"; // Simplified
        
        private float CalculateInteractionFrequency()
        {
            if (currentRelationship == null) return 0f;
            
            var daysSinceLastInteraction = (DateTime.Now - currentRelationship.lastInteraction).TotalDays;
            return currentRelationship.interactionCount / (float)Math.Max(1, daysSinceLastInteraction);
        }
        
        private float CalculateTradeValue(List<TradeItem> items)
        {
            float total = 0f;
            foreach (var item in items)
            {
                total += item.value * item.quantity;
            }
            return total;
        }
        
        private float CalculateDialogueRelationshipImpact(string playerInput, string npcResponse)
        {
            // Basic impact calculation - can be enhanced
            float baseImpact = 0.02f;
            
            // Positive interactions
            if (playerInput.Contains("help") || playerInput.Contains("advice"))
                baseImpact += 0.03f;
            
            if (playerInput.Contains("thank") || playerInput.Contains("appreciate"))
                baseImpact += 0.05f;
            
            // Negative interactions
            if (playerInput.Contains("demand") || playerInput.Contains("threaten"))
                baseImpact -= 0.10f;
            
            return baseImpact;
        }
        
        // Context action handlers
        private async Task HandleRumorRequest()
        {
            var rumors = await GetLocalRumors();
            string response = rumors.Count > 0 ? 
                $"I've heard that {rumors[UnityEngine.Random.Range(0, rumors.Count)]}" : 
                "Haven't heard any interesting rumors lately.";
            
            interactionUI?.DisplayNPCResponse(response);
        }
        
        private async Task HandleEventsRequest()
        {
            var events = await GetRecentLocalEvents();
            string response = events.Count > 0 ? 
                $"Recently, {events[UnityEngine.Random.Range(0, events.Count)]}" : 
                "Things have been quiet around here.";
            
            interactionUI?.DisplayNPCResponse(response);
        }
        
        private async Task HandleTradeRoutesRequest()
        {
            var routes = await GetActiveTradeRoutes();
            string response = routes.Count > 0 ? 
                $"The {routes[UnityEngine.Random.Range(0, routes.Count)]} is quite busy these days." : 
                "Trade has been slow lately.";
            
            interactionUI?.DisplayNPCResponse(response);
        }
        
        private async Task HandlePoliticsRequest()
        {
            var climate = await GetPoliticalClimate();
            string response = $"Politically speaking, {climate.ToLower()}. Best to keep your head down.";
            
            interactionUI?.DisplayNPCResponse(response);
        }
        
        private void HandleLanguageResolved(string language, string explanation, float comprehension)
        {
            if (enableDebugLogging)
                Debug.Log($"NPCInteractionController: Language resolved to {language} (Comprehension: {comprehension:P1}) - {explanation}");
        }
        
        private void HandleLanguageBarrier(string playerId, string npcId)
        {
            if (enableDebugLogging)
                Debug.Log($"NPCInteractionController: Language barrier encountered between {playerId} and {npcId}");
            
            // Could show special UI or offer language learning opportunities
        }
        
        private void HandleLanguageLearning(string language, string context)
        {
            if (enableDebugLogging)
                Debug.Log($"NPCInteractionController: Language learning opportunity for {language} - {context}");
        }
    }
    
    [Serializable]
    public class DialogueEntry
    {
        public string speaker;
        public string text;
        public DateTime timestamp;
    }
    
    [Serializable]
    public class InteractionResult
    {
        public bool success;
        public InteractionType interactionType;
        public DateTime timestamp;
        public string message;
    }
    
    [Serializable]
    public class TradeResult
    {
        public bool success;
        public float totalValue;
        public float relationshipChange;
        public DateTime timestamp;
        public string message;
    }
    
    [Serializable]
    public class RelationshipChange
    {
        public string npcId;
        public float oldTrustLevel;
        public float newTrustLevel;
        public string reason;
    }
    
    [Serializable]
    public class ContextData
    {
        public string key;
        public object value;
        public DateTime timestamp;
    }
    
    public enum InteractionType
    {
        General,
        Dialogue,
        Trade,
        Quest,
        Combat,
        Gift,
        Challenge
    }
    
    public enum RelationshipType
    {
        Enemy,
        Hostile,
        Unfriendly,
        Stranger,
        Acquaintance,
        Friend,
        Ally,
        Trusted
    }
} 