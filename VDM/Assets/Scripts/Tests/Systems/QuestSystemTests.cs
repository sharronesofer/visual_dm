using System.Collections;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using VDM.Systems.Quests;
using VDM.Core;
using VDM.Core.Events;
using VDM.Core.Models;
using System.Linq;

namespace VDM.Tests.Systems
{
    /// <summary>
    /// Comprehensive test suite for the Quest System.
    /// Tests quest loading, progress tracking, condition evaluation, reward distribution, and state transitions.
    /// </summary>
    public class QuestSystemTests : TestFramework
    {
        // Test dependencies
        private QuestSystem _questSystem;
        private EventManager _eventManager;
        private GameState _gameState;
        private PlayerState _playerState;
        
        // Test data
        private Quest _testQuest;
        private QuestObjective _testObjective;
        
        [SetUp]
        public override void Setup()
        {
            base.Setup();
            
            // Set up test dependencies
            _gameState = new GameState();
            _playerState = new PlayerState { PlayerId = "test-player", Level = 5 };
            _gameState.PlayerState = _playerState;
            
            GameObject eventManagerObject = CreateTestObject("EventManager", typeof(EventManager));
            _eventManager = eventManagerObject.GetComponent<EventManager>();
            
            GameObject questSystemObject = CreateTestObject("QuestSystem", typeof(QuestSystem));
            _questSystem = questSystemObject.GetComponent<QuestSystem>();
            _questSystem.Initialize(_gameState, _eventManager);
            
            // Set up test data
            _testQuest = CreateTestQuest();
            _testObjective = _testQuest.Objectives[0];
        }
        
        private Quest CreateTestQuest()
        {
            Quest quest = new Quest
            {
                Id = "test-quest-1",
                Title = "Test Quest",
                Description = "A quest for testing",
                MinLevel = 3,
                State = QuestState.Available,
                Objectives = new List<QuestObjective>
                {
                    new QuestObjective
                    {
                        Id = "objective-1",
                        Description = "Test objective",
                        Type = ObjectiveType.Interact,
                        TargetId = "test-npc",
                        Count = 1,
                        Progress = 0,
                        IsCompleted = false
                    }
                },
                Rewards = new QuestRewards
                {
                    Experience = 100,
                    Gold = 50,
                    Items = new List<string> { "test-item-1" }
                }
            };
            
            return quest;
        }
        
        [Test]
        public void QuestSystem_Initialization_ShouldInitializeProperly()
        {
            // Assert
            Assert.IsNotNull(_questSystem);
            Assert.IsNotNull(_questSystem.GetQuests());
            Assert.AreEqual(0, _questSystem.GetQuests().Count);
        }
        
        [Test]
        public void AddQuest_ShouldAddQuestToSystem()
        {
            // Act
            _questSystem.AddQuest(_testQuest);
            
            // Assert
            Assert.AreEqual(1, _questSystem.GetQuests().Count);
            Assert.AreEqual(_testQuest.Id, _questSystem.GetQuests()[0].Id);
        }
        
        [Test]
        public void GetQuest_ShouldReturnCorrectQuest()
        {
            // Arrange
            _questSystem.AddQuest(_testQuest);
            
            // Act
            Quest retrievedQuest = _questSystem.GetQuest(_testQuest.Id);
            
            // Assert
            Assert.IsNotNull(retrievedQuest);
            Assert.AreEqual(_testQuest.Id, retrievedQuest.Id);
            Assert.AreEqual(_testQuest.Title, retrievedQuest.Title);
        }
        
        [Test]
        public void GetQuest_WithInvalidId_ShouldReturnNull()
        {
            // Act
            Quest retrievedQuest = _questSystem.GetQuest("invalid-id");
            
            // Assert
            Assert.IsNull(retrievedQuest);
        }
        
        [Test]
        public void AcceptQuest_ShouldChangeQuestState()
        {
            // Arrange
            _questSystem.AddQuest(_testQuest);
            
            // Act
            bool result = _questSystem.AcceptQuest(_testQuest.Id, _playerState.PlayerId);
            Quest quest = _questSystem.GetQuest(_testQuest.Id);
            
            // Assert
            Assert.IsTrue(result);
            Assert.AreEqual(QuestState.Active, quest.State);
            Assert.AreEqual(_playerState.PlayerId, quest.AssignedPlayerId);
        }
        
        [Test]
        public void AcceptQuest_WithInvalidLevel_ShouldNotAcceptQuest()
        {
            // Arrange
            _testQuest.MinLevel = 10; // Set higher than player level
            _questSystem.AddQuest(_testQuest);
            
            // Act
            bool result = _questSystem.AcceptQuest(_testQuest.Id, _playerState.PlayerId);
            Quest quest = _questSystem.GetQuest(_testQuest.Id);
            
            // Assert
            Assert.IsFalse(result);
            Assert.AreEqual(QuestState.Available, quest.State);
            Assert.IsNull(quest.AssignedPlayerId);
        }
        
        [Test]
        public void UpdateObjectiveProgress_ShouldUpdateProgress()
        {
            // Arrange
            _questSystem.AddQuest(_testQuest);
            _questSystem.AcceptQuest(_testQuest.Id, _playerState.PlayerId);
            
            // Act
            bool result = _questSystem.UpdateObjectiveProgress(_testQuest.Id, _testObjective.Id, 1);
            Quest quest = _questSystem.GetQuest(_testQuest.Id);
            QuestObjective objective = quest.Objectives.FirstOrDefault(o => o.Id == _testObjective.Id);
            
            // Assert
            Assert.IsTrue(result);
            Assert.IsNotNull(objective);
            Assert.AreEqual(1, objective.Progress);
            Assert.IsTrue(objective.IsCompleted);
        }
        
        [Test]
        public void UpdateObjectiveProgress_WithInactiveQuest_ShouldNotUpdate()
        {
            // Arrange
            _questSystem.AddQuest(_testQuest); // Quest is available but not accepted
            
            // Act
            bool result = _questSystem.UpdateObjectiveProgress(_testQuest.Id, _testObjective.Id, 1);
            Quest quest = _questSystem.GetQuest(_testQuest.Id);
            QuestObjective objective = quest.Objectives.FirstOrDefault(o => o.Id == _testObjective.Id);
            
            // Assert
            Assert.IsFalse(result);
            Assert.IsNotNull(objective);
            Assert.AreEqual(0, objective.Progress);
            Assert.IsFalse(objective.IsCompleted);
        }
        
        [Test]
        public void CompleteQuest_WithAllObjectivesComplete_ShouldCompleteQuest()
        {
            // Arrange
            _questSystem.AddQuest(_testQuest);
            _questSystem.AcceptQuest(_testQuest.Id, _playerState.PlayerId);
            _questSystem.UpdateObjectiveProgress(_testQuest.Id, _testObjective.Id, 1);
            
            // Act
            QuestRewards rewards = _questSystem.CompleteQuest(_testQuest.Id);
            Quest quest = _questSystem.GetQuest(_testQuest.Id);
            
            // Assert
            Assert.IsNotNull(rewards);
            Assert.AreEqual(_testQuest.Rewards.Experience, rewards.Experience);
            Assert.AreEqual(_testQuest.Rewards.Gold, rewards.Gold);
            Assert.AreEqual(QuestState.Completed, quest.State);
        }
        
        [Test]
        public void CompleteQuest_WithIncompleteObjectives_ShouldNotComplete()
        {
            // Arrange
            _questSystem.AddQuest(_testQuest);
            _questSystem.AcceptQuest(_testQuest.Id, _playerState.PlayerId);
            // Not updating objective progress, so it remains incomplete
            
            // Act
            QuestRewards rewards = _questSystem.CompleteQuest(_testQuest.Id);
            Quest quest = _questSystem.GetQuest(_testQuest.Id);
            
            // Assert
            Assert.IsNull(rewards);
            Assert.AreEqual(QuestState.Active, quest.State);
        }
        
        [Test]
        public void GetAvailableQuests_ShouldReturnOnlyAvailableQuests()
        {
            // Arrange
            _questSystem.AddQuest(_testQuest); // Available
            
            Quest activeQuest = CreateTestQuest();
            activeQuest.Id = "active-quest";
            activeQuest.State = QuestState.Active;
            _questSystem.AddQuest(activeQuest);
            
            Quest completedQuest = CreateTestQuest();
            completedQuest.Id = "completed-quest";
            completedQuest.State = QuestState.Completed;
            _questSystem.AddQuest(completedQuest);
            
            // Act
            List<Quest> availableQuests = _questSystem.GetAvailableQuests();
            
            // Assert
            Assert.AreEqual(1, availableQuests.Count);
            Assert.AreEqual(_testQuest.Id, availableQuests[0].Id);
        }
        
        [Test]
        public void GetActiveQuests_ShouldReturnOnlyActiveQuests()
        {
            // Arrange
            _questSystem.AddQuest(_testQuest); // Available
            
            Quest activeQuest = CreateTestQuest();
            activeQuest.Id = "active-quest";
            activeQuest.State = QuestState.Active;
            activeQuest.AssignedPlayerId = _playerState.PlayerId;
            _questSystem.AddQuest(activeQuest);
            
            // Act
            List<Quest> activeQuests = _questSystem.GetActiveQuests(_playerState.PlayerId);
            
            // Assert
            Assert.AreEqual(1, activeQuests.Count);
            Assert.AreEqual(activeQuest.Id, activeQuests[0].Id);
        }
        
        [UnityTest]
        public IEnumerator QuestSystem_ShouldReceiveEvents()
        {
            // Arrange
            _questSystem.AddQuest(_testQuest);
            _questSystem.AcceptQuest(_testQuest.Id, _playerState.PlayerId);
            
            // Act
            QuestEvent questEvent = new QuestEvent
            {
                Type = QuestEventType.Interact,
                TargetId = "test-npc",
                SourceId = _playerState.PlayerId
            };
            
            _eventManager.RaiseEvent(questEvent);
            
            // Wait one frame for event processing
            yield return null;
            
            // Assert
            Quest quest = _questSystem.GetQuest(_testQuest.Id);
            QuestObjective objective = quest.Objectives[0];
            
            Assert.IsTrue(objective.IsCompleted);
            Assert.AreEqual(1, objective.Progress);
        }
        
        [Test]
        public void AbandonQuest_ShouldResetQuestState()
        {
            // Arrange
            _questSystem.AddQuest(_testQuest);
            _questSystem.AcceptQuest(_testQuest.Id, _playerState.PlayerId);
            _questSystem.UpdateObjectiveProgress(_testQuest.Id, _testObjective.Id, 1);
            
            // Act
            bool result = _questSystem.AbandonQuest(_testQuest.Id);
            Quest quest = _questSystem.GetQuest(_testQuest.Id);
            
            // Assert
            Assert.IsTrue(result);
            Assert.AreEqual(QuestState.Available, quest.State);
            Assert.IsNull(quest.AssignedPlayerId);
            Assert.IsFalse(quest.Objectives[0].IsCompleted);
            Assert.AreEqual(0, quest.Objectives[0].Progress);
        }
        
        [Test]
        public void RemoveQuest_ShouldRemoveQuestFromSystem()
        {
            // Arrange
            _questSystem.AddQuest(_testQuest);
            
            // Act
            bool result = _questSystem.RemoveQuest(_testQuest.Id);
            
            // Assert
            Assert.IsTrue(result);
            Assert.IsNull(_questSystem.GetQuest(_testQuest.Id));
            Assert.AreEqual(0, _questSystem.GetQuests().Count);
        }
    }
} 