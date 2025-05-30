using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Combat.Models;
using VDM.Runtime.Services;


namespace VDM.Runtime.Combat.Services
{
    /// <summary>
    /// Service for communicating with backend combat system
    /// </summary>
    public class CombatService : BaseHttpService
    {
        private const string COMBAT_ENDPOINT = "/api/combat";
        
        // Events
        public event Action<CombatEvent> OnCombatEventReceived;
        public event Action<string> OnCombatStarted;
        public event Action<string> OnCombatEnded;
        
        /// <summary>
        /// Start a new combat encounter
        /// </summary>
        public async Task<string> StartCombatAsync(List<string> participantIds, string encounterType = "standard")
        {
            var request = new
            {
                participants = participantIds,
                encounter_type = encounterType,
                timestamp = DateTime.UtcNow
            };
            
            try
            {
                var response = await PostAsync<dynamic>($"{COMBAT_ENDPOINT}/start", request);
                string combatId = response.combat_id;
                
                OnCombatStarted?.Invoke(combatId);
                return combatId;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to start combat: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// End a combat encounter
        /// </summary>
        public async Task EndCombatAsync(string combatId, string reason = "completed")
        {
            var request = new
            {
                combat_id = combatId,
                reason = reason,
                timestamp = DateTime.UtcNow
            };
            
            try
            {
                await PostAsync($"{COMBAT_ENDPOINT}/end", request);
                OnCombatEnded?.Invoke(combatId);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to end combat: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Submit a combat action to the backend
        /// </summary>
        public async Task<CombatResult> SubmitActionAsync(string combatId, string actorId, CombatAction action, string targetId = null)
        {
            var request = new
            {
                combat_id = combatId,
                actor_id = actorId,
                action = new
                {
                    name = action.Name,
                    type = action.Type.ToString(),
                    damage = action.Damage,
                    damage_type = action.DamageType.ToString(),
                    range = action.Range,
                    mana_cost = action.ManaCost
                },
                target_id = targetId,
                timestamp = DateTime.UtcNow
            };
            
            try
            {
                var response = await PostAsync<dynamic>($"{COMBAT_ENDPOINT}/action", request);
                
                // Convert response to CombatResult
                var result = new CombatResult
                {
                    Action = action,
                    Success = response.success,
                    Damage = response.damage ?? 0,
                    Message = response.message
                };
                
                return result;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to submit combat action: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get current combat state from backend
        /// </summary>
        public async Task<CombatState> GetCombatStateAsync(string combatId)
        {
            try
            {
                var response = await GetAsync<dynamic>($"{COMBAT_ENDPOINT}/{combatId}/state");
                
                // Convert response to CombatState
                var state = new CombatState
                {
                    CombatId = response.combat_id,
                    IsActive = response.is_active,
                    CurrentTurn = response.current_turn,
                    Round = response.round,
                    Participants = new List<Combatant>()
                };
                
                // Parse participants
                if (response.participants != null)
                {
                    foreach (var participant in response.participants)
                    {
                        var combatant = new Combatant
                        {
                            Name = participant.name,
                            CurrentHealth = participant.current_health,
                            MaxHealth = participant.max_health,
                            ArmorClass = participant.armor_class,
                            Initiative = participant.initiative
                        };
                        state.Participants.Add(combatant);
                    }
                }
                
                return state;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get combat state: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get available actions for a combatant
        /// </summary>
        public async Task<List<CombatAction>> GetAvailableActionsAsync(string combatId, string combatantId)
        {
            try
            {
                var response = await GetAsync<dynamic>($"{COMBAT_ENDPOINT}/{combatId}/combatant/{combatantId}/actions");
                var actions = new List<CombatAction>();
                
                if (response.actions != null)
                {
                    foreach (var actionData in response.actions)
                    {
                        var action = new CombatAction
                        {
                            Name = actionData.name,
                            Description = actionData.description,
                            Damage = actionData.damage ?? 0,
                            Range = actionData.range ?? 0,
                            ManaCost = actionData.mana_cost ?? 0
                        };
                        
                        // Parse action type
                        if (Enum.TryParse<ActionType>(actionData.type, true, out var actionType))
                        {
                            action.Type = actionType;
                        }
                        
                        // Parse damage type
                        if (Enum.TryParse<DamageType>(actionData.damage_type, true, out var damageType))
                        {
                            action.DamageType = damageType;
                        }
                        
                        actions.Add(action);
                    }
                }
                
                return actions;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get available actions: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Apply status effect to a combatant
        /// </summary>
        public async Task ApplyStatusEffectAsync(string combatId, string targetId, StatusEffect effect)
        {
            var request = new
            {
                combat_id = combatId,
                target_id = targetId,
                effect = new
                {
                    name = effect.Name,
                    type = effect.Type.ToString(),
                    duration = effect.Duration,
                    magnitude = effect.Magnitude,
                    is_buff = effect.IsBuff
                },
                timestamp = DateTime.UtcNow
            };
            
            try
            {
                await PostAsync($"{COMBAT_ENDPOINT}/status-effect", request);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to apply status effect: {ex.Message}");
                throw;
            }
        }
        
        /// <summary>
        /// Get combat history/log
        /// </summary>
        public async Task<List<CombatEvent>> GetCombatHistoryAsync(string combatId)
        {
            try
            {
                var response = await GetAsync<dynamic>($"{COMBAT_ENDPOINT}/{combatId}/history");
                var events = new List<CombatEvent>();
                
                if (response.events != null)
                {
                    foreach (var eventData in response.events)
                    {
                        var combatEvent = new CombatEvent
                        {
                            Message = eventData.message,
                            Timestamp = eventData.timestamp ?? Time.time
                        };
                        
                        // Parse event type
                        if (Enum.TryParse<CombatEventType>(eventData.type, true, out var eventType))
                        {
                            combatEvent.Type = eventType;
                        }
                        
                        events.Add(combatEvent);
                    }
                }
                
                return events;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get combat history: {ex.Message}");
                throw;
            }
        }
    }
    
    /// <summary>
    /// Represents the current state of a combat encounter
    /// </summary>
    [Serializable]
    public class CombatState
    {
        public string CombatId;
        public bool IsActive;
        public int CurrentTurn;
        public int Round;
        public List<Combatant> Participants = new List<Combatant>();
        public List<CombatEvent> RecentEvents = new List<CombatEvent>();
    }
} 