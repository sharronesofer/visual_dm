using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using VisualDM.Core;
using VisualDM.Core.EventChannels;

namespace VisualDM.Examples
{
    /// <summary>
    /// Example event data classes
    /// </summary>
    [Serializable]
    public class PlayerData
    {
        public string PlayerId;
        public Vector3 Position;
        public int Health;
        public int Level;
    }

    [Serializable]
    public class DamageEvent
    {
        public string TargetId;
        public int Damage;
        public string Source;
    }

    [Serializable]
    public class LevelUpEvent
    {
        public string PlayerId;
        public int NewLevel;
        public List<string> UnlockedAbilities;
    }

    /// <summary>
    /// Example MonoBehaviour showing how to use the EventBus
    /// </summary>
    public class EventBusUsage : MonoBehaviour
    {
        // ScriptableObject event channels can be assigned in the inspector
        [SerializeField] private VoidEventChannel gameStartChannel;
        [SerializeField] private GameObjectEventChannel playerSpawnChannel;
        [SerializeField] private StringEventChannel chatMessageChannel;
        
        // The global event bus instance
        private static readonly EventBus EventBus = new EventBus();
        
        // Keep track of subscriptions to clean up when destroying
        private List<Action> cleanupActions = new List<Action>();
        
        private void Awake()
        {
            Debug.Log("EventBusUsage: Initializing and connecting to event bus...");
            
            // Subscribe to various events
            cleanupActions.Add(
                EventBus.Subscribe<PlayerData>(OnPlayerDataReceived, EventPriority.High)
            );
            
            cleanupActions.Add(
                EventBus.Subscribe<DamageEvent>(OnDamageReceived)
            );
            
            cleanupActions.Add(
                EventBus.SubscribeAsync<LevelUpEvent>(OnLevelUpReceivedAsync)
            );
            
            // Connect ScriptableObject event channels to the event bus
            if (gameStartChannel != null)
            {
                cleanupActions.Add(
                    gameStartChannel.Subscribe(() => 
                    {
                        Debug.Log("Game start event received via ScriptableObject channel!");
                        // Publish to event bus
                        EventBus.Publish(new PlayerData { PlayerId = "Player1", Health = 100, Level = 1 });
                    })
                );
            }
            
            if (playerSpawnChannel != null)
            {
                cleanupActions.Add(
                    EventBus.ConnectToEventChannel(playerSpawnChannel)
                );
            }
            
            if (chatMessageChannel != null)
            {
                cleanupActions.Add(
                    EventBus.ConnectEventChannel(chatMessageChannel)
                );
            }
        }
        
        private void OnDestroy()
        {
            // Clean up all subscriptions
            foreach (var cleanup in cleanupActions)
            {
                cleanup?.Invoke();
            }
            cleanupActions.Clear();
        }
        
        // Example handlers for different event types
        private void OnPlayerDataReceived(PlayerData data)
        {
            Debug.Log($"Player {data.PlayerId} data received: Position={data.Position}, Health={data.Health}, Level={data.Level}");
        }
        
        private void OnDamageReceived(DamageEvent damage)
        {
            Debug.Log($"{damage.TargetId} took {damage.Damage} damage from {damage.Source}");
            
            // Example of conditional event publishing based on received event
            if (damage.TargetId == "Player1" && damage.Damage > 0)
            {
                var playerData = new PlayerData
                {
                    PlayerId = damage.TargetId,
                    Health = 100 - damage.Damage,  // Just an example calculation
                    Level = 1
                };
                
                // Publish updated player data
                EventBus.Publish(playerData);
            }
        }
        
        private async Task OnLevelUpReceivedAsync(LevelUpEvent levelUp)
        {
            Debug.Log($"Player {levelUp.PlayerId} leveled up to {levelUp.NewLevel}!");
            
            // Example of async event handling
            await Task.Delay(1000); // Simulate some async work
            
            Debug.Log("Async processing of level up completed!");
            
            foreach (var ability in levelUp.UnlockedAbilities)
            {
                Debug.Log($"Unlocked: {ability}");
            }
        }
        
        // Example methods that could be called from UI buttons
        public void SimulateDamage()
        {
            EventBus.Publish(new DamageEvent 
            { 
                TargetId = "Player1", 
                Damage = 25, 
                Source = "Enemy1" 
            });
        }
        
        public void SimulateLevelUp()
        {
            EventBus.Publish(new LevelUpEvent 
            { 
                PlayerId = "Player1", 
                NewLevel = 2, 
                UnlockedAbilities = new List<string> { "Fireball", "Sprint" } 
            });
        }
        
        public void SimulateGameStart()
        {
            if (gameStartChannel != null)
            {
                gameStartChannel.RaiseEvent();
            }
        }
        
        public void SendChatMessage(string message)
        {
            if (chatMessageChannel != null)
            {
                chatMessageChannel.RaiseEvent($"Player1: {message}");
            }
            else
            {
                // Direct use of EventBus if channel is not available
                EventBus.Publish($"Player1: {message}");
            }
        }
    }
} 