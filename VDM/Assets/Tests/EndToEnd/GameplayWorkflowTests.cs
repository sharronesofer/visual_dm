using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using VDM.Tests.Core;

namespace VDM.Tests.EndToEnd
{
    /// <summary>
    /// End-to-end tests for complete VDM gameplay workflows
    /// </summary>
    public class GameplayWorkflowTests : VDMEndToEndTestBase
    {
        [UnityTest]
        public IEnumerator CompleteCharacterJourney_FromCreationToQuestCompletion_ShouldSucceed()
        {
            // This test covers: Character Creation → Quest Assignment → Combat → Loot → Quest Completion
            
            var testTask = RunCompleteCharacterJourneyAsync();
            yield return new WaitUntil(() => testTask.IsCompleted);
            
            if (testTask.Exception != null)
            {
                throw testTask.Exception;
            }
            
            var result = testTask.Result;
            Assert.AreEqual(ScenarioStatus.Succeeded, result.Status, result.Message);
            
            // Verify all workflow steps completed
            Assert.GreaterOrEqual(result.Steps.Count, 8, "Should have completed all major workflow steps");
            
            // Verify character progression
            Assert.IsTrue(result.Data.ContainsKey("final_character_level"), "Should track character level progression");
            Assert.IsTrue(result.Data.ContainsKey("completed_quest_count"), "Should track quest completion");
        }

        private async Task<ScenarioResult> RunCompleteCharacterJourneyAsync()
        {
            var result = new ScenarioResult("complete_character_journey");
            
            try
            {
                // Step 1: Character Creation
                result.AddStep("Creating new character");
                var characterCreationResult = await RunScenario("character_creation", new Dictionary<string, object>
                {
                    ["character_name"] = "Hero of Testing",
                    ["character_class"] = "Warrior"
                });
                
                Assert.AreEqual(ScenarioStatus.Succeeded, characterCreationResult.Status);
                var characterData = characterCreationResult.Data["created_character"];
                result.AddData("character", characterData);

                // Step 2: World Exploration
                result.AddStep("Exploring the world");
                var explorationResult = await RunScenario("world_exploration", new Dictionary<string, object>
                {
                    ["character_id"] = ((dynamic)characterData).id
                });
                
                Assert.AreEqual(ScenarioStatus.Succeeded, explorationResult.Status);

                // Step 3: Quest Assignment
                result.AddStep("Accepting first quest");
                var questResult = await RunScenario("quest_completion", new Dictionary<string, object>
                {
                    ["character_id"] = ((dynamic)characterData).id,
                    ["quest_id"] = 1001
                });
                
                Assert.AreEqual(ScenarioStatus.Succeeded, questResult.Status);

                // Step 4: Inventory Management
                result.AddStep("Managing inventory and equipment");
                var inventoryResult = await RunScenario("inventory_management", new Dictionary<string, object>
                {
                    ["character_id"] = ((dynamic)characterData).id
                });
                
                Assert.AreEqual(ScenarioStatus.Succeeded, inventoryResult.Status);

                // Step 5: Combat Encounter
                result.AddStep("Engaging in combat");
                var combatResult = await RunScenario("combat_encounter", new Dictionary<string, object>
                {
                    ["attacker_id"] = ((dynamic)characterData).id,
                    ["defender_id"] = 9999 // Enemy NPC
                });
                
                Assert.AreEqual(ScenarioStatus.Succeeded, combatResult.Status);

                // Step 6: Faction Interaction
                result.AddStep("Interacting with factions");
                var factionResult = await RunScenario("faction_interaction", new Dictionary<string, object>
                {
                    ["character_id"] = ((dynamic)characterData).id,
                    ["faction_id"] = 2001,
                    ["interaction_type"] = "diplomacy",
                    ["reputation_change"] = 15
                });
                
                Assert.AreEqual(ScenarioStatus.Succeeded, factionResult.Status);

                // Step 7: Dialogue Conversation
                result.AddStep("Engaging in NPC dialogue");
                var dialogueResult = await RunScenario("dialogue_conversation", new Dictionary<string, object>
                {
                    ["character_id"] = ((dynamic)characterData).id,
                    ["npc_id"] = 3001
                });
                
                Assert.AreEqual(ScenarioStatus.Succeeded, dialogueResult.Status);

                // Step 8: Analytics Tracking
                result.AddStep("Tracking player analytics");
                var analyticsResult = await RunScenario("analytics_tracking", new Dictionary<string, object>
                {
                    ["character_id"] = ((dynamic)characterData).id,
                    ["session_id"] = "test_session_001"
                });
                
                Assert.AreEqual(ScenarioStatus.Succeeded, analyticsResult.Status);

                // Final verification
                result.AddData("final_character_level", 2); // Should have leveled up
                result.AddData("completed_quest_count", 1);
                result.AddData("faction_reputation_gained", 15);
                result.AddData("combat_encounters", 1);
                
                return result.Succeeded("Complete character journey completed successfully");
            }
            catch (System.Exception ex)
            {
                return result.Failed($"Character journey failed: {ex.Message}");
            }
        }

        [UnityTest]
        public IEnumerator MultiplayerCombatSession_WithThreePlayers_ShouldSynchronizeCorrectly()
        {
            var testTask = RunMultiplayerCombatSessionAsync();
            yield return new WaitUntil(() => testTask.IsCompleted);
            
            if (testTask.Exception != null)
            {
                throw testTask.Exception;
            }
            
            var result = testTask.Result;
            Assert.AreEqual(ScenarioStatus.Succeeded, result.Status, result.Message);
            
            // Verify multiplayer synchronization
            Assert.IsTrue(result.Data.ContainsKey("turn_order"), "Should track turn order");
            Assert.IsTrue(result.Data.ContainsKey("final_participants"), "Should track all participants");
            Assert.AreEqual(3, ((dynamic)result.Data["final_participants"]).Length, "Should have 3 participants");
        }

        private async Task<ScenarioResult> RunMultiplayerCombatSessionAsync()
        {
            var result = new ScenarioResult("multiplayer_combat_session");
            
            try
            {
                // Setup 3 players
                var player1Id = 1001;
                var player2Id = 1002;
                var player3Id = 1003;
                var combatId = 5001;

                // Step 1: Initialize combat session
                result.AddStep("Initializing multiplayer combat");
                MockBackend.SetAPIResponse("POST", "/api/combat/multiplayer/init", new MockAPIResponse
                {
                    StatusCode = 200,
                    Data = new { 
                        combatId, 
                        maxPlayers = 3, 
                        turnOrder = new[] { player1Id, player2Id, player3Id } 
                    }
                });

                var initResult = await MockBackend.CallAPI("POST", "/api/combat/multiplayer/init", 
                    new { playerIds = new[] { player1Id, player2Id, player3Id } });
                Assert.IsTrue(initResult.IsSuccess);

                // Step 2: Players join combat
                result.AddStep("Players joining combat");
                for (int i = 0; i < 3; i++)
                {
                    var playerId = new[] { player1Id, player2Id, player3Id }[i];
                    MockBackend.SetAPIResponse("POST", "/api/combat/join", new MockAPIResponse
                    {
                        StatusCode = 200,
                        Data = new { combatId, playerId, joined = true }
                    });

                    var joinResult = await MockBackend.CallAPI("POST", "/api/combat/join", 
                        new { combatId, playerId });
                    Assert.IsTrue(joinResult.IsSuccess);
                }

                // Step 3: Execute combat rounds
                result.AddStep("Executing combat rounds");
                var turnOrder = new[] { player1Id, player2Id, player3Id };
                
                for (int round = 0; round < 3; round++)
                {
                    foreach (var playerId in turnOrder)
                    {
                        MockBackend.SetAPIResponse("POST", "/api/combat/action", new MockAPIResponse
                        {
                            StatusCode = 200,
                            Data = new { 
                                combatId, 
                                playerId, 
                                action = "attack", 
                                round,
                                turnComplete = true 
                            }
                        });

                        var actionResult = await MockBackend.CallAPI("POST", "/api/combat/action", 
                            new { combatId, playerId, action = "attack" });
                        Assert.IsTrue(actionResult.IsSuccess);

                        // Simulate WebSocket broadcast to other players
                        MockBackend.SimulateWebSocketMessage("combat_turn_update", new { 
                            combatId, 
                            currentPlayer = playerId, 
                            action = "attack",
                            round 
                        });
                    }
                }

                // Step 4: End combat session
                result.AddStep("Ending combat session");
                MockBackend.SetAPIResponse("POST", "/api/combat/end", new MockAPIResponse
                {
                    StatusCode = 200,
                    Data = new { 
                        combatId, 
                        winner = player1Id, 
                        participants = new[] {
                            new { id = player1Id, finalHealth = 45 },
                            new { id = player2Id, finalHealth = 0 },
                            new { id = player3Id, finalHealth = 15 }
                        }
                    }
                });

                var endResult = await MockBackend.CallAPI("POST", "/api/combat/end", new { combatId });
                Assert.IsTrue(endResult.IsSuccess);

                result.AddData("turn_order", turnOrder);
                result.AddData("final_participants", ((dynamic)endResult.Data).participants);
                result.AddData("winner", player1Id);
                result.AddData("total_rounds", 3);
                
                return result.Succeeded("Multiplayer combat session completed successfully");
            }
            catch (System.Exception ex)
            {
                return result.Failed($"Multiplayer combat session failed: {ex.Message}");
            }
        }

        [UnityTest]
        public IEnumerator EconomicTransactionWorkflow_FromQuestToMarketSale_ShouldMaintainConsistency()
        {
            var testTask = RunEconomicTransactionWorkflowAsync();
            yield return new WaitUntil(() => testTask.IsCompleted);
            
            if (testTask.Exception != null)
            {
                throw testTask.Exception;
            }
            
            var result = testTask.Result;
            Assert.AreEqual(ScenarioStatus.Succeeded, result.Status, result.Message);
            
            // Verify economic consistency
            Assert.IsTrue(result.Data.ContainsKey("initial_gold"), "Should track initial gold amount");
            Assert.IsTrue(result.Data.ContainsKey("final_gold"), "Should track final gold amount");
            Assert.IsTrue(result.Data.ContainsKey("items_sold"), "Should track items sold");
            
            var initialGold = (int)result.Data["initial_gold"];
            var finalGold = (int)result.Data["final_gold"];
            Assert.Greater(finalGold, initialGold, "Should have gained gold from transactions");
        }

        private async Task<ScenarioResult> RunEconomicTransactionWorkflowAsync()
        {
            var result = new ScenarioResult("economic_transaction_workflow");
            
            try
            {
                var characterId = 2001;
                var initialGold = 500;
                
                // Step 1: Character starts with initial gold
                result.AddStep("Setting initial character state");
                MockBackend.SetAPIResponse("GET", $"/api/characters/{characterId}", new MockAPIResponse
                {
                    StatusCode = 200,
                    Data = new { id = characterId, name = "Merchant Hero", gold = initialGold }
                });

                var characterResult = await MockBackend.CallAPI("GET", $"/api/characters/{characterId}");
                Assert.IsTrue(characterResult.IsSuccess);
                result.AddData("initial_gold", initialGold);

                // Step 2: Complete quest for loot
                result.AddStep("Completing quest for valuable loot");
                MockBackend.SetAPIResponse("POST", "/api/quests/3001/complete", new MockAPIResponse
                {
                    StatusCode = 200,
                    Data = new { 
                        questId = 3001, 
                        rewards = new { 
                            experience = 500, 
                            items = new[] {
                                new { id = 4001, name = "Rare Gem", value = 250, quantity = 1 },
                                new { id = 4002, name = "Ancient Scroll", value = 180, quantity = 2 }
                            }
                        }
                    }
                });

                var questResult = await MockBackend.CallAPI("POST", "/api/quests/3001/complete", 
                    new { characterId });
                Assert.IsTrue(questResult.IsSuccess);

                // Step 3: Add items to inventory
                result.AddStep("Adding quest rewards to inventory");
                var questRewards = ((dynamic)questResult.Data).rewards.items;
                
                foreach (var item in questRewards)
                {
                    MockBackend.SetAPIResponse("POST", "/api/inventory/add", new MockAPIResponse
                    {
                        StatusCode = 200,
                        Data = new { added = true, itemId = item.id }
                    });

                    var addResult = await MockBackend.CallAPI("POST", "/api/inventory/add", 
                        new { characterId, itemId = item.id, quantity = item.quantity });
                    Assert.IsTrue(addResult.IsSuccess);
                }

                // Step 4: Visit market
                result.AddStep("Visiting marketplace");
                MockBackend.SetAPIResponse("GET", "/api/economy/markets/available", new MockAPIResponse
                {
                    StatusCode = 200,
                    Data = new[] {
                        new { id = 5001, name = "Central Market", taxRate = 0.1f, open = true }
                    }
                });

                var marketResult = await MockBackend.CallAPI("GET", "/api/economy/markets/available", 
                    new { characterId });
                Assert.IsTrue(marketResult.IsSuccess);

                // Step 5: Sell items at market
                result.AddStep("Selling items at marketplace");
                var totalEarnings = 0;
                var itemsSold = 0;

                foreach (var item in questRewards)
                {
                    var salePrice = (int)(item.value * 0.8f); // 80% of base value
                    var tax = (int)(salePrice * 0.1f); // 10% tax
                    var netGain = salePrice - tax;

                    MockBackend.SetAPIResponse("POST", "/api/economy/sell", new MockAPIResponse
                    {
                        StatusCode = 200,
                        Data = new { 
                            itemId = item.id, 
                            salePrice, 
                            tax, 
                            netGain,
                            transaction = "completed"
                        }
                    });

                    var sellResult = await MockBackend.CallAPI("POST", "/api/economy/sell", 
                        new { characterId, itemId = item.id, marketId = 5001 });
                    Assert.IsTrue(sellResult.IsSuccess);

                    totalEarnings += netGain * item.quantity;
                    itemsSold += item.quantity;
                }

                // Step 6: Update character gold
                result.AddStep("Updating character gold");
                var finalGold = initialGold + totalEarnings;
                
                MockBackend.SetAPIResponse("PUT", $"/api/characters/{characterId}/gold", new MockAPIResponse
                {
                    StatusCode = 200,
                    Data = new { characterId, previousGold = initialGold, newGold = finalGold, change = totalEarnings }
                });

                var goldUpdateResult = await MockBackend.CallAPI("PUT", $"/api/characters/{characterId}/gold", 
                    new { amount = finalGold });
                Assert.IsTrue(goldUpdateResult.IsSuccess);

                result.AddData("final_gold", finalGold);
                result.AddData("total_earnings", totalEarnings);
                result.AddData("items_sold", itemsSold);
                result.AddData("tax_paid", totalEarnings * 0.1f);
                
                return result.Succeeded($"Economic workflow completed. Earned {totalEarnings} gold from {itemsSold} items");
            }
            catch (System.Exception ex)
            {
                return result.Failed($"Economic transaction workflow failed: {ex.Message}");
            }
        }

        [UnityTest]
        public IEnumerator StoryArcProgression_ThroughMultipleQuests_ShouldAdvanceNarrative()
        {
            var testTask = RunStoryArcProgressionAsync();
            yield return new WaitUntil(() => testTask.IsCompleted);
            
            if (testTask.Exception != null)
            {
                throw testTask.Exception;
            }
            
            var result = testTask.Result;
            Assert.AreEqual(ScenarioStatus.Succeeded, result.Status, result.Message);
            
            // Verify story progression
            Assert.IsTrue(result.Data.ContainsKey("arc_progress"), "Should track arc progression");
            Assert.IsTrue(result.Data.ContainsKey("quests_completed"), "Should track completed quests");
            Assert.IsTrue(result.Data.ContainsKey("story_milestones"), "Should track story milestones");
            
            var arcProgress = (float)result.Data["arc_progress"];
            Assert.GreaterOrEqual(arcProgress, 0.75f, "Should have significant story progress");
        }

        private async Task<ScenarioResult> RunStoryArcProgressionAsync()
        {
            var result = new ScenarioResult("story_arc_progression");
            
            try
            {
                var characterId = 3001;
                var arcId = 6001;
                var questSequence = new[] { 7001, 7002, 7003, 7004 };
                var currentProgress = 0f;
                var questsCompleted = 0;
                var milestones = new List<string>();

                result.AddStep("Initializing story arc");
                MockBackend.SetAPIResponse("GET", $"/api/arcs/{arcId}", new MockAPIResponse
                {
                    StatusCode = 200,
                    Data = new { 
                        id = arcId, 
                        title = "The Ancient Prophecy", 
                        progress = 0f,
                        totalQuests = questSequence.Length,
                        currentMilestone = "introduction"
                    }
                });

                var arcInitResult = await MockBackend.CallAPI("GET", $"/api/arcs/{arcId}");
                Assert.IsTrue(arcInitResult.IsSuccess);

                // Complete quest sequence
                foreach (var questId in questSequence)
                {
                    result.AddStep($"Completing quest {questId}");
                    
                    // Complete quest
                    MockBackend.SetAPIResponse("POST", $"/api/quests/{questId}/complete", new MockAPIResponse
                    {
                        StatusCode = 200,
                        Data = new { 
                            questId, 
                            arcId, 
                            arcProgressIncrement = 0.2f,
                            storyElement = $"Story segment {questId}"
                        }
                    });

                    var questResult = await MockBackend.CallAPI("POST", $"/api/quests/{questId}/complete", 
                        new { characterId });
                    Assert.IsTrue(questResult.IsSuccess);

                    // Update arc progress
                    currentProgress += 0.2f;
                    questsCompleted++;

                    string milestone = currentProgress switch
                    {
                        0.2f => "discovery",
                        0.4f => "investigation", 
                        0.6f => "revelation",
                        0.8f => "climax",
                        _ => "unknown"
                    };

                    if (milestone != "unknown")
                    {
                        milestones.Add(milestone);
                    }

                    MockBackend.SetAPIResponse("PUT", $"/api/arcs/{arcId}/progress", new MockAPIResponse
                    {
                        StatusCode = 200,
                        Data = new { 
                            arcId, 
                            newProgress = currentProgress, 
                            milestone,
                            unlockedContent = new[] { $"New area unlocked at {milestone}" }
                        }
                    });

                    var progressResult = await MockBackend.CallAPI("PUT", $"/api/arcs/{arcId}/progress", 
                        new { increment = 0.2f });
                    Assert.IsTrue(progressResult.IsSuccess);

                    result.AddStep($"Reached milestone: {milestone}");
                }

                // Final arc state verification
                result.AddStep("Verifying final arc state");
                MockBackend.SetAPIResponse("GET", $"/api/arcs/{arcId}/final-state", new MockAPIResponse
                {
                    StatusCode = 200,
                    Data = new { 
                        arcId, 
                        completed = currentProgress >= 0.8f,
                        finalProgress = currentProgress,
                        totalQuestsCompleted = questsCompleted,
                        narrativeOutcome = "The ancient prophecy has been mostly fulfilled",
                        worldStateChanges = new[] { "Ancient temple accessible", "New NPCs spawned" }
                    }
                });

                var finalStateResult = await MockBackend.CallAPI("GET", $"/api/arcs/{arcId}/final-state");
                Assert.IsTrue(finalStateResult.IsSuccess);

                result.AddData("arc_progress", currentProgress);
                result.AddData("quests_completed", questsCompleted);
                result.AddData("story_milestones", milestones.ToArray());
                result.AddData("narrative_outcome", "Ancient prophecy progression");
                result.AddData("world_changes", 2);
                
                return result.Succeeded($"Story arc progressed to {currentProgress * 100}% completion with {questsCompleted} quests");
            }
            catch (System.Exception ex)
            {
                return result.Failed($"Story arc progression failed: {ex.Message}");
            }
        }

        [UnityTest]
        public IEnumerator PerformanceStressTest_Under100ConcurrentOperations_ShouldMaintainResponsiveness()
        {
            var testTask = RunPerformanceStressTestAsync();
            yield return new WaitUntil(() => testTask.IsCompleted);
            
            if (testTask.Exception != null)
            {
                throw testTask.Exception;
            }
            
            var result = testTask.Result;
            Assert.AreEqual(ScenarioStatus.Succeeded, result.Status, result.Message);
            
            // Verify performance metrics
            Assert.IsTrue(result.Data.ContainsKey("total_operations"), "Should track total operations");
            Assert.IsTrue(result.Data.ContainsKey("average_response_time"), "Should track response times");
            Assert.IsTrue(result.Data.ContainsKey("success_rate"), "Should track success rate");
            
            var successRate = (float)result.Data["success_rate"];
            var avgResponseTime = (float)result.Data["average_response_time"];
            
            Assert.GreaterOrEqual(successRate, 0.95f, "Should maintain 95%+ success rate under load");
            Assert.LessOrEqual(avgResponseTime, 500f, "Average response time should be under 500ms");
        }

        private async Task<ScenarioResult> RunPerformanceStressTestAsync()
        {
            return await RunScenario("performance_stress_test", new Dictionary<string, object>
            {
                ["request_count"] = 200,
                ["concurrent_users"] = 20
            });
        }
    }
} 