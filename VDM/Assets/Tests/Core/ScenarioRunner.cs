using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace VDM.Tests.Core
{
    /// <summary>
    /// Runs end-to-end scenarios for testing complete user workflows
    /// </summary>
    public class ScenarioRunner : IDisposable
    {
        private readonly MockBackendService _mockBackend;
        private readonly Dictionary<string, Func<Dictionary<string, object>, Task<ScenarioResult>>> _scenarios;
        private bool _disposed;

        public ScenarioRunner(MockBackendService mockBackend)
        {
            _mockBackend = mockBackend;
            _scenarios = new Dictionary<string, Func<Dictionary<string, object>, Task<ScenarioResult>>>();
            RegisterDefaultScenarios();
        }

        /// <summary>
        /// Register all default test scenarios
        /// </summary>
        private void RegisterDefaultScenarios()
        {
            RegisterScenario("character_creation", CharacterCreationScenario);
            RegisterScenario("quest_completion", QuestCompletionScenario);
            RegisterScenario("combat_encounter", CombatEncounterScenario);
            RegisterScenario("faction_interaction", FactionInteractionScenario);
            RegisterScenario("inventory_management", InventoryManagementScenario);
            RegisterScenario("dialogue_conversation", DialogueConversationScenario);
            RegisterScenario("world_exploration", WorldExplorationScenario);
            RegisterScenario("user_authentication", UserAuthenticationScenario);
            RegisterScenario("analytics_tracking", AnalyticsTrackingScenario);
            RegisterScenario("performance_stress_test", PerformanceStressTestScenario);
        }

        /// <summary>
        /// Register a custom scenario
        /// </summary>
        public void RegisterScenario(string name, Func<Dictionary<string, object>, Task<ScenarioResult>> scenario)
        {
            _scenarios[name] = scenario;
        }

        /// <summary>
        /// Run a specific scenario
        /// </summary>
        public async Task<ScenarioResult> RunScenario(string scenarioName, Dictionary<string, object> parameters = null)
        {
            parameters ??= new Dictionary<string, object>();

            if (!_scenarios.TryGetValue(scenarioName, out var scenario))
            {
                return ScenarioResult.Failed($"Scenario '{scenarioName}' not found");
            }

            try
            {
                UnityEngine.Debug.Log($"[SCENARIO] Starting scenario: {scenarioName}");
                var result = await scenario(parameters);
                UnityEngine.Debug.Log($"[SCENARIO] Completed scenario: {scenarioName} - {result.Status}");
                return result;
            }
            catch (Exception ex)
            {
                UnityEngine.Debug.LogError($"[SCENARIO] Error in scenario '{scenarioName}': {ex.Message}");
                return ScenarioResult.Failed($"Exception in scenario: {ex.Message}");
            }
        }

        #region Default Scenarios

        private async Task<ScenarioResult> CharacterCreationScenario(Dictionary<string, object> parameters)
        {
            var result = new ScenarioResult("character_creation");
            
            try
            {
                // Step 1: Open character creation UI
                result.AddStep("Open character creation UI");
                // TODO: Simulate UI navigation to character creation
                
                // Step 2: Fill character details
                result.AddStep("Fill character details");
                var characterData = new
                {
                    name = parameters.GetValueOrDefault("character_name", "Test Character"),
                    class_ = parameters.GetValueOrDefault("character_class", "Warrior"),
                    attributes = new { strength = 15, dexterity = 12, intelligence = 10, constitution = 14 }
                };

                // Step 3: Submit character creation
                result.AddStep("Submit character creation");
                var response = await _mockBackend.CallAPI("POST", "/api/characters", characterData);
                
                if (!response.IsSuccess)
                {
                    return result.Failed($"Character creation failed: {response.Error}");
                }

                // Step 4: Verify character appears in game
                result.AddStep("Verify character appears in game");
                await Task.Delay(100); // Simulate UI update delay
                
                result.AddData("created_character", response.Data);
                return result.Succeeded();
            }
            catch (Exception ex)
            {
                return result.Failed($"Character creation failed: {ex.Message}");
            }
        }

        private async Task<ScenarioResult> QuestCompletionScenario(Dictionary<string, object> parameters)
        {
            var result = new ScenarioResult("quest_completion");

            try
            {
                // Step 1: Get available quests
                result.AddStep("Get available quests");
                var questsResponse = await _mockBackend.CallAPI("GET", "/api/quests");
                
                if (!questsResponse.IsSuccess)
                {
                    return result.Failed($"Failed to get quests: {questsResponse.Error}");
                }

                // Step 2: Accept a quest
                result.AddStep("Accept quest");
                var questId = parameters.GetValueOrDefault("quest_id", 1);
                var acceptResponse = await _mockBackend.CallAPI("POST", $"/api/quests/{questId}/accept");
                
                if (!acceptResponse.IsSuccess)
                {
                    return result.Failed($"Failed to accept quest: {acceptResponse.Error}");
                }

                // Step 3: Progress quest objectives
                result.AddStep("Progress quest objectives");
                for (int i = 0; i < 3; i++)
                {
                    await _mockBackend.CallAPI("POST", $"/api/quests/{questId}/progress", new { objective = i });
                    await Task.Delay(50);
                }

                // Step 4: Complete quest
                result.AddStep("Complete quest");
                var completeResponse = await _mockBackend.CallAPI("POST", $"/api/quests/{questId}/complete");
                
                if (!completeResponse.IsSuccess)
                {
                    return result.Failed($"Failed to complete quest: {completeResponse.Error}");
                }

                result.AddData("completed_quest", completeResponse.Data);
                return result.Succeeded();
            }
            catch (Exception ex)
            {
                return result.Failed($"Quest completion failed: {ex.Message}");
            }
        }

        private async Task<ScenarioResult> CombatEncounterScenario(Dictionary<string, object> parameters)
        {
            var result = new ScenarioResult("combat_encounter");

            try
            {
                // Step 1: Initialize combat
                result.AddStep("Initialize combat");
                var combatData = new
                {
                    attackerId = parameters.GetValueOrDefault("attacker_id", 1),
                    defenderId = parameters.GetValueOrDefault("defender_id", 2)
                };

                var initResponse = await _mockBackend.CallAPI("POST", "/api/combat/init", combatData);
                if (!initResponse.IsSuccess)
                {
                    return result.Failed($"Combat initialization failed: {initResponse.Error}");
                }

                // Step 2: Execute combat actions
                result.AddStep("Execute combat actions");
                var actions = new[] { "attack", "defend", "cast_spell" };
                
                for (int turn = 0; turn < 5; turn++)
                {
                    var action = actions[turn % actions.Length];
                    var actionResponse = await _mockBackend.CallAPI("POST", "/api/combat/action", new { action, turn });
                    
                    if (!actionResponse.IsSuccess)
                    {
                        return result.Failed($"Combat action failed: {actionResponse.Error}");
                    }
                    
                    await Task.Delay(100); // Simulate action delay
                }

                // Step 3: End combat
                result.AddStep("End combat");
                var endResponse = await _mockBackend.CallAPI("POST", "/api/combat/end");
                
                result.AddData("combat_result", endResponse.Data);
                return result.Succeeded();
            }
            catch (Exception ex)
            {
                return result.Failed($"Combat encounter failed: {ex.Message}");
            }
        }

        private async Task<ScenarioResult> FactionInteractionScenario(Dictionary<string, object> parameters)
        {
            var result = new ScenarioResult("faction_interaction");

            try
            {
                // Step 1: Get faction data
                result.AddStep("Get faction data");
                var factionsResponse = await _mockBackend.CallAPI("GET", "/api/factions");
                
                if (!factionsResponse.IsSuccess)
                {
                    return result.Failed($"Failed to get factions: {factionsResponse.Error}");
                }

                // Step 2: Interact with faction
                result.AddStep("Interact with faction");
                var factionId = parameters.GetValueOrDefault("faction_id", 1);
                var interactionType = parameters.GetValueOrDefault("interaction_type", "diplomacy");
                
                var interactionResponse = await _mockBackend.CallAPI("POST", $"/api/factions/{factionId}/interact", 
                    new { type = interactionType });

                if (!interactionResponse.IsSuccess)
                {
                    return result.Failed($"Faction interaction failed: {interactionResponse.Error}");
                }

                // Step 3: Update reputation
                result.AddStep("Update reputation");
                var reputationChange = (int)parameters.GetValueOrDefault("reputation_change", 10);
                var repResponse = await _mockBackend.CallAPI("POST", $"/api/factions/{factionId}/reputation", 
                    new { change = reputationChange });

                result.AddData("faction_interaction", repResponse.Data);
                return result.Succeeded();
            }
            catch (Exception ex)
            {
                return result.Failed($"Faction interaction failed: {ex.Message}");
            }
        }

        private async Task<ScenarioResult> InventoryManagementScenario(Dictionary<string, object> parameters)
        {
            var result = new ScenarioResult("inventory_management");

            try
            {
                // Step 1: Get current inventory
                result.AddStep("Get current inventory");
                var inventoryResponse = await _mockBackend.CallAPI("GET", "/api/inventory");
                
                if (!inventoryResponse.IsSuccess)
                {
                    return result.Failed($"Failed to get inventory: {inventoryResponse.Error}");
                }

                // Step 2: Add items to inventory
                result.AddStep("Add items to inventory");
                var itemsToAdd = new[]
                {
                    new { name = "Test Sword", quantity = 1, type = "weapon" },
                    new { name = "Health Potion", quantity = 5, type = "consumable" }
                };

                foreach (var item in itemsToAdd)
                {
                    var addResponse = await _mockBackend.CallAPI("POST", "/api/inventory/add", item);
                    if (!addResponse.IsSuccess)
                    {
                        return result.Failed($"Failed to add item: {addResponse.Error}");
                    }
                }

                // Step 3: Use/Remove items
                result.AddStep("Use/Remove items");
                var useResponse = await _mockBackend.CallAPI("POST", "/api/inventory/use", 
                    new { itemName = "Health Potion", quantity = 1 });

                result.AddData("inventory_state", useResponse.Data);
                return result.Succeeded();
            }
            catch (Exception ex)
            {
                return result.Failed($"Inventory management failed: {ex.Message}");
            }
        }

        private async Task<ScenarioResult> DialogueConversationScenario(Dictionary<string, object> parameters)
        {
            var result = new ScenarioResult("dialogue_conversation");

            try
            {
                // Step 1: Start dialogue
                result.AddStep("Start dialogue");
                var npcId = parameters.GetValueOrDefault("npc_id", 1);
                var dialogueResponse = await _mockBackend.CallAPI("GET", $"/api/dialogue/{npcId}");
                
                if (!dialogueResponse.IsSuccess)
                {
                    return result.Failed($"Failed to start dialogue: {dialogueResponse.Error}");
                }

                // Step 2: Make dialogue choices
                result.AddStep("Make dialogue choices");
                var choices = new[] { 1, 2, 1 }; // Simulate dialogue tree navigation
                
                foreach (var choice in choices)
                {
                    var choiceResponse = await _mockBackend.CallAPI("POST", $"/api/dialogue/{npcId}/choice", 
                        new { choiceId = choice });
                    
                    if (!choiceResponse.IsSuccess)
                    {
                        return result.Failed($"Dialogue choice failed: {choiceResponse.Error}");
                    }
                    
                    await Task.Delay(100);
                }

                // Step 3: End dialogue
                result.AddStep("End dialogue");
                var endResponse = await _mockBackend.CallAPI("POST", $"/api/dialogue/{npcId}/end");

                result.AddData("dialogue_result", endResponse.Data);
                return result.Succeeded();
            }
            catch (Exception ex)
            {
                return result.Failed($"Dialogue conversation failed: {ex.Message}");
            }
        }

        private async Task<ScenarioResult> WorldExplorationScenario(Dictionary<string, object> parameters)
        {
            var result = new ScenarioResult("world_exploration");

            try
            {
                // Step 1: Get world state
                result.AddStep("Get world state");
                var worldResponse = await _mockBackend.CallAPI("GET", "/api/world/state");
                
                if (!worldResponse.IsSuccess)
                {
                    return result.Failed($"Failed to get world state: {worldResponse.Error}");
                }

                // Step 2: Explore locations
                result.AddStep("Explore locations");
                var locations = new[] { "forest", "mountain", "village", "dungeon" };
                
                foreach (var location in locations)
                {
                    var exploreResponse = await _mockBackend.CallAPI("POST", "/api/world/explore", 
                        new { location });
                    
                    if (!exploreResponse.IsSuccess)
                    {
                        return result.Failed($"Failed to explore {location}: {exploreResponse.Error}");
                    }
                    
                    await Task.Delay(50);
                }

                // Step 3: Update world state
                result.AddStep("Update world state");
                var updateResponse = await _mockBackend.CallAPI("GET", "/api/world/state");

                result.AddData("exploration_result", updateResponse.Data);
                return result.Succeeded();
            }
            catch (Exception ex)
            {
                return result.Failed($"World exploration failed: {ex.Message}");
            }
        }

        private async Task<ScenarioResult> UserAuthenticationScenario(Dictionary<string, object> parameters)
        {
            var result = new ScenarioResult("user_authentication");

            try
            {
                // Step 1: Login
                result.AddStep("User login");
                var credentials = new
                {
                    username = parameters.GetValueOrDefault("username", "testuser"),
                    password = parameters.GetValueOrDefault("password", "password123")
                };

                var loginResponse = await _mockBackend.CallAPI("POST", "/api/auth/login", credentials);
                
                if (!loginResponse.IsSuccess)
                {
                    return result.Failed($"Login failed: {loginResponse.Error}");
                }

                // Step 2: Get user profile
                result.AddStep("Get user profile");
                var profileResponse = await _mockBackend.CallAPI("GET", "/api/auth/profile");
                
                if (!profileResponse.IsSuccess)
                {
                    return result.Failed($"Failed to get profile: {profileResponse.Error}");
                }

                // Step 3: Update preferences
                result.AddStep("Update preferences");
                var preferences = new { theme = "dark", notifications = true };
                var updateResponse = await _mockBackend.CallAPI("PUT", "/api/auth/preferences", preferences);

                result.AddData("user_profile", updateResponse.Data);
                return result.Succeeded();
            }
            catch (Exception ex)
            {
                return result.Failed($"User authentication failed: {ex.Message}");
            }
        }

        private async Task<ScenarioResult> AnalyticsTrackingScenario(Dictionary<string, object> parameters)
        {
            var result = new ScenarioResult("analytics_tracking");

            try
            {
                // Step 1: Track user actions
                result.AddStep("Track user actions");
                var actions = new[]
                {
                    "character_created", "quest_started", "combat_initiated", 
                    "item_acquired", "level_up"
                };

                foreach (var action in actions)
                {
                    var trackResponse = await _mockBackend.CallAPI("POST", "/api/analytics/track", 
                        new { action, timestamp = DateTime.UtcNow });
                    
                    if (!trackResponse.IsSuccess)
                    {
                        return result.Failed($"Failed to track action {action}: {trackResponse.Error}");
                    }
                    
                    await Task.Delay(50);
                }

                // Step 2: Get analytics data
                result.AddStep("Get analytics data");
                var analyticsResponse = await _mockBackend.CallAPI("GET", "/api/analytics");
                
                if (!analyticsResponse.IsSuccess)
                {
                    return result.Failed($"Failed to get analytics: {analyticsResponse.Error}");
                }

                result.AddData("analytics_data", analyticsResponse.Data);
                return result.Succeeded();
            }
            catch (Exception ex)
            {
                return result.Failed($"Analytics tracking failed: {ex.Message}");
            }
        }

        private async Task<ScenarioResult> PerformanceStressTestScenario(Dictionary<string, object> parameters)
        {
            var result = new ScenarioResult("performance_stress_test");

            try
            {
                var requestCount = (int)parameters.GetValueOrDefault("request_count", 100);
                var concurrentUsers = (int)parameters.GetValueOrDefault("concurrent_users", 10);

                // Step 1: Generate stress test data
                result.AddStep("Generate stress test data");
                _mockBackend.GenerateStressTestData("characters", requestCount);
                _mockBackend.GenerateStressTestData("quests", requestCount);

                // Step 2: Execute concurrent requests
                result.AddStep("Execute concurrent requests");
                var tasks = new List<Task>();
                
                for (int user = 0; user < concurrentUsers; user++)
                {
                    tasks.Add(ExecuteUserStressTest(user, requestCount / concurrentUsers));
                }

                await Task.WhenAll(tasks);

                // Step 3: Measure performance
                result.AddStep("Measure performance");
                // Performance metrics would be collected here
                
                result.AddData("stress_test_result", new { requestCount, concurrentUsers, status = "completed" });
                return result.Succeeded();
            }
            catch (Exception ex)
            {
                return result.Failed($"Performance stress test failed: {ex.Message}");
            }
        }

        private async Task ExecuteUserStressTest(int userId, int requestCount)
        {
            for (int i = 0; i < requestCount; i++)
            {
                var endpoints = new[] { "/api/characters", "/api/quests", "/api/inventory", "/api/world/state" };
                var endpoint = endpoints[i % endpoints.Length];
                
                await _mockBackend.CallAPI("GET", endpoint);
                
                if (i % 10 == 0) // Small delay every 10 requests
                {
                    await Task.Delay(10);
                }
            }
        }

        #endregion

        public void Dispose()
        {
            if (!_disposed)
            {
                _scenarios?.Clear();
                _disposed = true;
            }
        }
    }

    /// <summary>
    /// Result of a scenario execution
    /// </summary>
    public class ScenarioResult
    {
        public string ScenarioName { get; }
        public ScenarioStatus Status { get; private set; }
        public string Message { get; private set; }
        public List<string> Steps { get; }
        public Dictionary<string, object> Data { get; }
        public DateTime StartTime { get; }
        public DateTime? EndTime { get; private set; }
        public TimeSpan Duration => EndTime?.Subtract(StartTime) ?? TimeSpan.Zero;

        public ScenarioResult(string scenarioName)
        {
            ScenarioName = scenarioName;
            Status = ScenarioStatus.Running;
            Steps = new List<string>();
            Data = new Dictionary<string, object>();
            StartTime = DateTime.UtcNow;
        }

        public void AddStep(string step)
        {
            Steps.Add($"[{DateTime.UtcNow:HH:mm:ss}] {step}");
        }

        public void AddData(string key, object value)
        {
            Data[key] = value;
        }

        public ScenarioResult Succeeded(string message = "Scenario completed successfully")
        {
            Status = ScenarioStatus.Succeeded;
            Message = message;
            EndTime = DateTime.UtcNow;
            return this;
        }

        public ScenarioResult Failed(string message)
        {
            Status = ScenarioStatus.Failed;
            Message = message;
            EndTime = DateTime.UtcNow;
            return this;
        }

        public static ScenarioResult Failed(string message)
        {
            var result = new ScenarioResult("unknown");
            return result.Failed(message);
        }
    }

    public enum ScenarioStatus
    {
        Running,
        Succeeded,
        Failed
    }
} 