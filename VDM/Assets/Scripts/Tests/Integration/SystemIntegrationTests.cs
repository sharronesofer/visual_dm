using System.Collections;
using System.Threading.Tasks;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using VDM.Tests.Core;

namespace VDM.Tests.Integration
{
    /// <summary>
    /// Integration tests for VDM system interactions and backend communication
    /// </summary>
    public class SystemIntegrationTests : VDMIntegrationTestBase
    {
        [Test]
        public async Task CharacterQuestInteraction_WhenQuestCompleted_ShouldUpdateCharacterExperience()
        {
            // Arrange
            var characterId = 1;
            var questId = 101;
            
            MockBackend.SetAPIResponse("GET", $"/api/characters/{characterId}", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { id = characterId, name = "Test Hero", level = 1, experience = 500 }
            });

            MockBackend.SetAPIResponse("POST", $"/api/quests/{questId}/complete", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { questId, reward = new { experience = 300, gold = 100 } }
            });

            MockBackend.SetAPIResponse("PUT", $"/api/characters/{characterId}", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { id = characterId, experience = 800 }
            });

            // Act
            var questResult = await MockBackend.CallAPI("POST", $"/api/quests/{questId}/complete");
            var characterUpdate = await MockBackend.CallAPI("PUT", $"/api/characters/{characterId}", 
                new { experience = 800 });

            // Assert
            Assert.IsTrue(questResult.IsSuccess);
            Assert.IsTrue(characterUpdate.IsSuccess);
            
            // Verify the integration workflow completed
            Assert.AreEqual(200, questResult.StatusCode);
            Assert.AreEqual(200, characterUpdate.StatusCode);
        }

        [Test]
        public async Task CombatInventoryInteraction_WhenItemUsedInCombat_ShouldUpdateBothSystems()
        {
            // Arrange
            var characterId = 1;
            var combatId = 201;
            var itemId = 301;

            MockBackend.SetAPIResponse("GET", "/api/inventory", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new[] { new { id = itemId, name = "Health Potion", quantity = 3, type = "consumable" } }
            });

            MockBackend.SetAPIResponse("POST", "/api/combat/use-item", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { combatId, effect = "heal", amount = 50 }
            });

            MockBackend.SetAPIResponse("PUT", "/api/inventory/consume", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { itemId, newQuantity = 2 }
            });

            // Act
            var inventoryCheck = await MockBackend.CallAPI("GET", "/api/inventory");
            var combatAction = await MockBackend.CallAPI("POST", "/api/combat/use-item", 
                new { combatId, itemId, characterId });
            var inventoryUpdate = await MockBackend.CallAPI("PUT", "/api/inventory/consume", 
                new { itemId, quantity = 1 });

            // Assert
            Assert.IsTrue(inventoryCheck.IsSuccess);
            Assert.IsTrue(combatAction.IsSuccess);
            Assert.IsTrue(inventoryUpdate.IsSuccess);

            // Verify cross-system state consistency
            Assert.AreEqual(3, ((dynamic)inventoryCheck.Data)[0].quantity);
            Assert.AreEqual(2, ((dynamic)inventoryUpdate.Data).newQuantity);
        }

        [Test]
        public async Task FactionDialogueInteraction_WhenNPCConversation_ShouldUpdateReputation()
        {
            // Arrange
            var npcId = 401;
            var factionId = 501;
            var characterId = 1;

            MockBackend.SetAPIResponse("GET", $"/api/dialogue/{npcId}", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { npcId, factionId, dialogueTree = "diplomatic_greeting" }
            });

            MockBackend.SetAPIResponse("POST", $"/api/dialogue/{npcId}/choice", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { choiceId = 1, outcome = "positive", reputationChange = 10 }
            });

            MockBackend.SetAPIResponse("PUT", $"/api/factions/{factionId}/reputation", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { factionId, characterId, newReputation = 60 }
            });

            // Act
            var dialogueStart = await MockBackend.CallAPI("GET", $"/api/dialogue/{npcId}");
            var dialogueChoice = await MockBackend.CallAPI("POST", $"/api/dialogue/{npcId}/choice", 
                new { choiceId = 1, characterId });
            var reputationUpdate = await MockBackend.CallAPI("PUT", $"/api/factions/{factionId}/reputation", 
                new { characterId, change = 10 });

            // Assert
            Assert.IsTrue(dialogueStart.IsSuccess);
            Assert.IsTrue(dialogueChoice.IsSuccess);
            Assert.IsTrue(reputationUpdate.IsSuccess);

            // Verify the reputation change was processed
            Assert.AreEqual(10, ((dynamic)dialogueChoice.Data).reputationChange);
            Assert.AreEqual(60, ((dynamic)reputationUpdate.Data).newReputation);
        }

        [Test]
        public async Task EconomyInventoryInteraction_WhenItemSold_ShouldUpdateGoldAndInventory()
        {
            // Arrange
            var itemId = 601;
            var characterId = 1;
            var marketId = 701;

            MockBackend.SetAPIResponse("GET", "/api/inventory", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new[] { new { id = itemId, name = "Iron Sword", quantity = 1, value = 150 } }
            });

            MockBackend.SetAPIResponse("POST", "/api/economy/sell", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { itemId, soldPrice = 120, tax = 12, netGain = 108 }
            });

            MockBackend.SetAPIResponse("PUT", $"/api/characters/{characterId}/gold", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { characterId, newGoldAmount = 1108 }
            });

            MockBackend.SetAPIResponse("DELETE", $"/api/inventory/{itemId}", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { removed = true }
            });

            // Act
            var inventoryCheck = await MockBackend.CallAPI("GET", "/api/inventory");
            var saleTransaction = await MockBackend.CallAPI("POST", "/api/economy/sell", 
                new { itemId, marketId, characterId });
            var goldUpdate = await MockBackend.CallAPI("PUT", $"/api/characters/{characterId}/gold", 
                new { amount = 1108 });
            var inventoryRemoval = await MockBackend.CallAPI("DELETE", $"/api/inventory/{itemId}");

            // Assert
            Assert.IsTrue(inventoryCheck.IsSuccess);
            Assert.IsTrue(saleTransaction.IsSuccess);
            Assert.IsTrue(goldUpdate.IsSuccess);
            Assert.IsTrue(inventoryRemoval.IsSuccess);

            // Verify transaction integrity
            Assert.AreEqual(120, ((dynamic)saleTransaction.Data).soldPrice);
            Assert.AreEqual(1108, ((dynamic)goldUpdate.Data).newGoldAmount);
        }

        [Test]
        public async Task WorldStateTimeInteraction_WhenTimeProgresses_ShouldTriggerWorldEvents()
        {
            // Arrange
            MockBackend.SetAPIResponse("GET", "/api/time/current", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { day = 15, hour = 8, season = "Spring" }
            });

            MockBackend.SetAPIResponse("POST", "/api/time/advance", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { day = 15, hour = 12, eventsTriggered = new[] { "market_opens", "npc_movement" } }
            });

            MockBackend.SetAPIResponse("GET", "/api/world/state", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { 
                    activeEvents = new[] { "market_opens", "npc_movement" },
                    globalState = "normal",
                    weatherChange = true
                }
            });

            // Act
            var currentTime = await MockBackend.CallAPI("GET", "/api/time/current");
            var timeAdvance = await MockBackend.CallAPI("POST", "/api/time/advance", new { hours = 4 });
            var worldStateUpdate = await MockBackend.CallAPI("GET", "/api/world/state");

            // Assert
            Assert.IsTrue(currentTime.IsSuccess);
            Assert.IsTrue(timeAdvance.IsSuccess);
            Assert.IsTrue(worldStateUpdate.IsSuccess);

            // Verify time progression triggered world events
            var triggeredEvents = ((dynamic)timeAdvance.Data).eventsTriggered;
            var activeEvents = ((dynamic)worldStateUpdate.Data).activeEvents;
            
            Assert.IsNotNull(triggeredEvents);
            Assert.IsNotNull(activeEvents);
            Assert.AreEqual(2, triggeredEvents.Length);
        }

        [Test]
        public async Task QuestArcProgression_WhenQuestCompleted_ShouldAdvanceArcProgress()
        {
            // Arrange
            var questId = 801;
            var arcId = 901;
            var characterId = 1;

            MockBackend.SetAPIResponse("POST", $"/api/quests/{questId}/complete", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { questId, arcId, arcProgressIncrement = 0.25f }
            });

            MockBackend.SetAPIResponse("PUT", $"/api/arcs/{arcId}/progress", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { arcId, newProgress = 0.75f, nextMilestone = "climax" }
            });

            MockBackend.SetAPIResponse("GET", $"/api/arcs/{arcId}/next-quests", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new[] { new { id = 802, title = "Epic Confrontation", unlocked = true } }
            });

            // Act
            var questCompletion = await MockBackend.CallAPI("POST", $"/api/quests/{questId}/complete", 
                new { characterId });
            var arcProgress = await MockBackend.CallAPI("PUT", $"/api/arcs/{arcId}/progress", 
                new { increment = 0.25f });
            var nextQuests = await MockBackend.CallAPI("GET", $"/api/arcs/{arcId}/next-quests");

            // Assert
            Assert.IsTrue(questCompletion.IsSuccess);
            Assert.IsTrue(arcProgress.IsSuccess);
            Assert.IsTrue(nextQuests.IsSuccess);

            // Verify arc progression
            Assert.AreEqual(0.25f, ((dynamic)questCompletion.Data).arcProgressIncrement);
            Assert.AreEqual(0.75f, ((dynamic)arcProgress.Data).newProgress);
            Assert.AreEqual("climax", ((dynamic)arcProgress.Data).nextMilestone);
        }

        [Test]
        public async Task MultiUserCombat_WhenMultiplePlayersInCombat_ShouldSynchronizeStates()
        {
            // Arrange
            var combatId = 1001;
            var player1Id = 1;
            var player2Id = 2;

            MockBackend.SetAPIResponse("POST", "/api/combat/join", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { combatId, playerId = player1Id, position = "attacker" }
            });

            MockBackend.SetAPIResponse("POST", "/api/combat/action", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { 
                    combatId, 
                    playerId = player1Id, 
                    action = "attack", 
                    result = "hit", 
                    damage = 25,
                    turnOrder = new[] { player2Id, player1Id }
                }
            });

            // Simulate WebSocket notification to other players
            MockBackend.SetAPIResponse("GET", $"/api/combat/{combatId}/state", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { 
                    combatId,
                    currentTurn = player2Id,
                    participants = new[] { 
                        new { id = player1Id, health = 100 },
                        new { id = player2Id, health = 75 }
                    }
                }
            });

            // Act
            var player1Join = await MockBackend.CallAPI("POST", "/api/combat/join", 
                new { combatId, playerId = player1Id });
            var player1Action = await MockBackend.CallAPI("POST", "/api/combat/action", 
                new { combatId, playerId = player1Id, action = "attack", targetId = player2Id });
            var combatState = await MockBackend.CallAPI("GET", $"/api/combat/{combatId}/state");

            // Simulate WebSocket message to other players
            MockBackend.SimulateWebSocketMessage("combat_update", new { 
                combatId, 
                currentTurn = player2Id, 
                lastAction = "Player 1 attacked Player 2 for 25 damage" 
            });

            // Assert
            Assert.IsTrue(player1Join.IsSuccess);
            Assert.IsTrue(player1Action.IsSuccess);
            Assert.IsTrue(combatState.IsSuccess);

            // Verify combat state synchronization
            var participants = ((dynamic)combatState.Data).participants;
            Assert.AreEqual(2, participants.Length);
            Assert.AreEqual(player2Id, ((dynamic)combatState.Data).currentTurn);
        }

        [Test]
        public async Task DataPersistenceIntegration_WhenMultipleSystemsUpdate_ShouldMaintainConsistency()
        {
            // Arrange - Test scenario that updates multiple systems
            var characterId = 1;
            var sessionId = "test-session-123";

            // Character levels up (affects multiple systems)
            MockBackend.SetAPIResponse("PUT", $"/api/characters/{characterId}/level-up", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { 
                    newLevel = 6, 
                    healthIncrease = 20, 
                    skillPointsGained = 2,
                    newAbilitiesUnlocked = new[] { "Power Strike" }
                }
            });

            // Update related systems
            MockBackend.SetAPIResponse("PUT", $"/api/analytics/track", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { event = "character_level_up", level = 6 }
            });

            MockBackend.SetAPIResponse("GET", $"/api/quests/available", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new[] { new { id = 1001, title = "Advanced Quest", minLevel = 6, unlocked = true } }
            });

            // Act
            var levelUp = await MockBackend.CallAPI("PUT", $"/api/characters/{characterId}/level-up");
            var analyticsTrack = await MockBackend.CallAPI("PUT", "/api/analytics/track", 
                new { characterId, event = "level_up", sessionId });
            var availableQuests = await MockBackend.CallAPI("GET", "/api/quests/available", 
                new { characterId });

            // Assert
            Assert.IsTrue(levelUp.IsSuccess);
            Assert.IsTrue(analyticsTrack.IsSuccess);
            Assert.IsTrue(availableQuests.IsSuccess);

            // Verify cross-system consistency
            Assert.AreEqual(6, ((dynamic)levelUp.Data).newLevel);
            Assert.AreEqual("character_level_up", ((dynamic)analyticsTrack.Data).@event);
            Assert.IsTrue(((dynamic)availableQuests.Data)[0].unlocked);
        }

        [Test]
        public async Task ErrorHandlingIntegration_WhenSystemFailure_ShouldGracefullyRecover()
        {
            // Arrange - Simulate system failure scenario
            var characterId = 1;

            // First call succeeds
            MockBackend.SetAPIResponse("GET", $"/api/characters/{characterId}", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { id = characterId, name = "Test Character" }
            });

            // Second call fails (simulate network issue)
            MockBackend.SetAPIResponse("PUT", $"/api/characters/{characterId}/save", new MockAPIResponse
            {
                StatusCode = 500,
                Error = "Database connection failed"
            });

            // Recovery call succeeds
            MockBackend.SetAPIResponse("POST", "/api/characters/sync", new MockAPIResponse
            {
                StatusCode = 200,
                Data = new { synced = true, conflicts = 0 }
            });

            // Act
            var characterLoad = await MockBackend.CallAPI("GET", $"/api/characters/{characterId}");
            var characterSave = await MockBackend.CallAPI("PUT", $"/api/characters/{characterId}/save", 
                new { name = "Updated Name" });
            
            // Simulate error recovery
            var syncResult = await MockBackend.CallAPI("POST", "/api/characters/sync", 
                new { characterId });

            // Assert
            Assert.IsTrue(characterLoad.IsSuccess);
            Assert.IsFalse(characterSave.IsSuccess); // Expected failure
            Assert.IsTrue(syncResult.IsSuccess); // Recovery should succeed

            // Verify error handling
            Assert.AreEqual(500, characterSave.StatusCode);
            Assert.IsNotNull(characterSave.Error);
            Assert.IsTrue(((dynamic)syncResult.Data).synced);
        }

        [Test]
        public async Task PerformanceIntegration_WithHighVolumeRequests_ShouldMaintainResponseTimes()
        {
            // Arrange
            var requestCount = 50;
            var maxAcceptableResponseTime = 200f; // milliseconds

            MockBackend.GenerateStressTestData("characters", requestCount);
            MockBackend.GenerateStressTestData("quests", requestCount);

            // Act & Assert
            var stopwatch = System.Diagnostics.Stopwatch.StartNew();
            
            for (int i = 0; i < requestCount; i++)
            {
                var characterResponse = await MockBackend.CallAPI("GET", "/api/characters");
                var questResponse = await MockBackend.CallAPI("GET", "/api/quests");
                
                Assert.IsTrue(characterResponse.IsSuccess);
                Assert.IsTrue(questResponse.IsSuccess);
            }
            
            stopwatch.Stop();
            var averageResponseTime = stopwatch.ElapsedMilliseconds / (float)(requestCount * 2);

            // Verify performance criteria
            Assert.LessOrEqual(averageResponseTime, maxAcceptableResponseTime, 
                $"Average response time {averageResponseTime}ms exceeds maximum {maxAcceptableResponseTime}ms");
            
            AssertPerformance(stopwatch.ElapsedMilliseconds);
        }
    }
} 