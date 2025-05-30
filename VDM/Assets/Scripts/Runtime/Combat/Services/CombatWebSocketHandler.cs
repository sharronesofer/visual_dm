using Newtonsoft.Json;
using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.Runtime.Combat.Models;
using VDM.Runtime.Services;


namespace VDM.Runtime.Combat.Services
{
    /// <summary>
    /// Handles real-time combat updates via WebSocket
    /// </summary>
    public class CombatWebSocketHandler : BaseWebSocketHandler
    {
        // Events
        public event Action<CombatEvent> OnCombatEventReceived;
        public event Action<CombatState> OnCombatStateUpdated;
        public event Action<string, List<CombatAction>> OnAvailableActionsUpdated;
        public event Action<string, StatusEffect> OnStatusEffectApplied;
        public event Action<string, StatusEffect> OnStatusEffectRemoved;
        
        private Dictionary<string, CombatState> _activeCombats = new Dictionary<string, CombatState>();
        
        protected override void OnConnected()
        {
            base.OnConnected();
            Debug.Log("Combat WebSocket connected");
            
            // Subscribe to combat events
            Subscribe("combat.event");
            Subscribe("combat.state_update");
            Subscribe("combat.action_available");
            Subscribe("combat.status_effect");
        }
        
        protected override void OnDisconnected()
        {
            base.OnDisconnected();
            Debug.Log("Combat WebSocket disconnected");
            _activeCombats.Clear();
        }
        
        protected override void OnMessageReceived(string message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<dynamic>(message);
                string eventType = data.type;
                
                switch (eventType)
                {
                    case "combat.event":
                        HandleCombatEvent(data);
                        break;
                    case "combat.state_update":
                        HandleStateUpdate(data);
                        break;
                    case "combat.action_available":
                        HandleActionAvailable(data);
                        break;
                    case "combat.status_effect":
                        HandleStatusEffect(data);
                        break;
                    default:
                        Debug.LogWarning($"Unknown combat event type: {eventType}");
                        break;
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error processing combat WebSocket message: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Join a combat room for real-time updates
        /// </summary>
        public void JoinCombat(string combatId)
        {
            var message = new
            {
                type = "join_combat",
                combat_id = combatId,
                timestamp = DateTime.UtcNow
            };
            
            SendMessage(JsonConvert.SerializeObject(message));
        }
        
        /// <summary>
        /// Leave a combat room
        /// </summary>
        public void LeaveCombat(string combatId)
        {
            var message = new
            {
                type = "leave_combat",
                combat_id = combatId,
                timestamp = DateTime.UtcNow
            };
            
            SendMessage(JsonConvert.SerializeObject(message));
            
            if (_activeCombats.ContainsKey(combatId))
            {
                _activeCombats.Remove(combatId);
            }
        }
        
        /// <summary>
        /// Send a combat action via WebSocket for immediate processing
        /// </summary>
        public void SendCombatAction(string combatId, string actorId, CombatAction action, string targetId = null)
        {
            var message = new
            {
                type = "combat_action",
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
            
            SendMessage(JsonConvert.SerializeObject(message));
        }
        
        private void HandleCombatEvent(dynamic data)
        {
            try
            {
                var combatEvent = new CombatEvent
                {
                    Message = data.payload.message,
                    Timestamp = data.payload.timestamp ?? Time.time
                };
                
                // Parse event type
                if (Enum.TryParse<CombatEventType>(data.payload.event_type, true, out var eventType))
                {
                    combatEvent.Type = eventType;
                }
                
                // Parse participant if present
                if (data.payload.participant != null)
                {
                    combatEvent.Participant = new Combatant
                    {
                        Name = data.payload.participant.name,
                        CurrentHealth = data.payload.participant.current_health ?? 0,
                        MaxHealth = data.payload.participant.max_health ?? 0,
                        ArmorClass = data.payload.participant.armor_class ?? 0
                    };
                }
                
                OnCombatEventReceived?.Invoke(combatEvent);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling combat event: {ex.Message}");
            }
        }
        
        private void HandleStateUpdate(dynamic data)
        {
            try
            {
                string combatId = data.payload.combat_id;
                
                var state = new CombatState
                {
                    CombatId = combatId,
                    IsActive = data.payload.is_active ?? false,
                    CurrentTurn = data.payload.current_turn ?? 0,
                    Round = data.payload.round ?? 0,
                    Participants = new List<Combatant>()
                };
                
                // Parse participants
                if (data.payload.participants != null)
                {
                    foreach (var participant in data.payload.participants)
                    {
                        var combatant = new Combatant
                        {
                            Name = participant.name,
                            CurrentHealth = participant.current_health ?? 0,
                            MaxHealth = participant.max_health ?? 0,
                            ArmorClass = participant.armor_class ?? 0,
                            Initiative = participant.initiative ?? 0,
                            StatusEffects = new List<StatusEffect>()
                        };
                        
                        // Parse status effects
                        if (participant.status_effects != null)
                        {
                            foreach (var effect in participant.status_effects)
                            {
                                var statusEffect = new StatusEffect
                                {
                                    Name = effect.name,
                                    Duration = effect.duration ?? 0,
                                    Magnitude = effect.magnitude ?? 0,
                                    IsBuff = effect.is_buff ?? false
                                };
                                
                                if (Enum.TryParse<StatusEffectType>(effect.type, true, out var effectType))
                                {
                                    statusEffect.Type = effectType;
                                }
                                
                                combatant.StatusEffects.Add(statusEffect);
                            }
                        }
                        
                        state.Participants.Add(combatant);
                    }
                }
                
                // Update local cache
                _activeCombats[combatId] = state;
                
                OnCombatStateUpdated?.Invoke(state);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling state update: {ex.Message}");
            }
        }
        
        private void HandleActionAvailable(dynamic data)
        {
            try
            {
                string combatantId = data.payload.combatant_id;
                var actions = new List<CombatAction>();
                
                if (data.payload.actions != null)
                {
                    foreach (var actionData in data.payload.actions)
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
                
                OnAvailableActionsUpdated?.Invoke(combatantId, actions);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling action available: {ex.Message}");
            }
        }
        
        private void HandleStatusEffect(dynamic data)
        {
            try
            {
                string targetId = data.payload.target_id;
                string action = data.payload.action; // "applied" or "removed"
                
                var effect = new StatusEffect
                {
                    Name = data.payload.effect.name,
                    Duration = data.payload.effect.duration ?? 0,
                    Magnitude = data.payload.effect.magnitude ?? 0,
                    IsBuff = data.payload.effect.is_buff ?? false
                };
                
                if (Enum.TryParse<StatusEffectType>(data.payload.effect.type, true, out var effectType))
                {
                    effect.Type = effectType;
                }
                
                if (action == "applied")
                {
                    OnStatusEffectApplied?.Invoke(targetId, effect);
                }
                else if (action == "removed")
                {
                    OnStatusEffectRemoved?.Invoke(targetId, effect);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling status effect: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Get cached combat state
        /// </summary>
        public CombatState GetCachedCombatState(string combatId)
        {
            return _activeCombats.TryGetValue(combatId, out var state) ? state : null;
        }
        
        /// <summary>
        /// Get all active combat IDs
        /// </summary>
        public List<string> GetActiveCombatIds()
        {
            return new List<string>(_activeCombats.Keys);
        }
    }
} 