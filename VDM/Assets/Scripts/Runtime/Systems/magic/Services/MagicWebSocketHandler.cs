using NativeWebSocket;
using System;
using System.Collections.Generic;
using UnityEngine;
using VDM.Infrastructure.Services.Websocket;
using VDM.Systems.Magic.Models;


namespace VDM.Systems.Magic.Services
{
    /// <summary>
    /// WebSocket handler for real-time magic system updates
    /// </summary>
    public class MagicWebSocketHandler : BaseWebSocketHandler
    {
        #region Events

        public event Action<MagicEvent> OnMagicEvent;
        public event Action<MagicSystemState> OnMagicStateUpdated;
        public event Action<SpellCastingResult> OnSpellCast;
        public event Action<ActiveSpellEffect> OnSpellEffectAdded;
        public event Action<string> OnSpellEffectRemoved;
        public event Action<Spellcaster> OnSpellcasterUpdated;
        public event Action<string, int> OnManaChanged;
        public event Action<string, int> OnConcentrationChanged;

        #endregion

        #region Private Fields

        private MagicSystemState _cachedMagicState;
        private Dictionary<string, Spellcaster> _cachedSpellcasters = new Dictionary<string, Spellcaster>();

        #endregion

        #region Initialization

        public MagicWebSocketHandler() : base()
        {
            _cachedMagicState = new MagicSystemState();
        }

        protected override void HandleMessage(string message)
        {
            try
            {
                var data = JsonUtility.FromJson<Dictionary<string, object>>(message);
                if (data.ContainsKey("type"))
                {
                    string eventType = data["type"].ToString();
                    string eventData = data.ContainsKey("data") ? data["data"].ToString() : message;
                    
                    switch (eventType)
                    {
                        case "magic_event":
                            HandleMagicEvent(eventData);
                            break;
                        case "magic_state_updated":
                            HandleMagicStateUpdated(eventData);
                            break;
                        case "spell_cast":
                            HandleSpellCast(eventData);
                            break;
                        case "spell_effect_added":
                            HandleSpellEffectAdded(eventData);
                            break;
                        case "spell_effect_removed":
                            HandleSpellEffectRemoved(eventData);
                            break;
                        case "spellcaster_updated":
                            HandleSpellcasterUpdated(eventData);
                            break;
                        case "mana_changed":
                            HandleManaChanged(eventData);
                            break;
                        case "concentration_changed":
                            HandleConcentrationChanged(eventData);
                            break;
                        case "magic_session_joined":
                            HandleMagicSessionJoined(eventData);
                            break;
                        case "magic_session_left":
                            HandleMagicSessionLeft(eventData);
                            break;
                        case "magic_session_ended":
                            HandleMagicSessionEnded(eventData);
                            break;
                        default:
                            Debug.LogWarning($"Unknown magic event type: {eventType}");
                            break;
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error handling magic WebSocket message: {ex.Message}");
            }
        }

        #endregion

        #region Room Management

        /// <summary>
        /// Join a magic session for real-time updates
        /// </summary>
        public void JoinMagicSession(string sessionId)
        {
            var message = new
            {
                type = "join_magic_session",
                sessionId = sessionId
            };
            SendMessage(message);
        }

        /// <summary>
        /// Leave the current magic session
        /// </summary>
        public void LeaveMagicSession()
        {
            var message = new
            {
                type = "leave_magic_session"
            };
            SendMessage(message);
        }

        #endregion

        #region Message Handlers

        private void HandleMagicEvent(string data)
        {
            try
            {
                var magicEvent = JsonUtility.FromJson<MagicEvent>(data);
                if (magicEvent != null)
                {
                    _cachedMagicState.AddEvent(magicEvent);
                    OnMagicEvent?.Invoke(magicEvent);
                    
                    Debug.Log($"Magic event received: {magicEvent.EventType}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to handle magic event: {ex.Message}");
            }
        }

        private void HandleMagicStateUpdated(string data)
        {
            try
            {
                var magicState = JsonUtility.FromJson<MagicSystemState>(data);
                if (magicState != null)
                {
                    _cachedMagicState = magicState;
                    OnMagicStateUpdated?.Invoke(magicState);
                    
                    Debug.Log("Magic system state updated");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to handle magic state update: {ex.Message}");
            }
        }

        private void HandleSpellCast(string data)
        {
            try
            {
                var castingResult = JsonUtility.FromJson<SpellCastingResult>(data);
                if (castingResult != null)
                {
                    OnSpellCast?.Invoke(castingResult);
                    
                    Debug.Log($"Spell cast: {castingResult.Spell?.Name} by {castingResult.Caster?.Name} - Result: {castingResult.Result}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to handle spell cast: {ex.Message}");
            }
        }

        private void HandleSpellEffectAdded(string data)
        {
            try
            {
                var spellEffect = JsonUtility.FromJson<ActiveSpellEffect>(data);
                if (spellEffect != null)
                {
                    _cachedMagicState.GlobalEffects.Add(spellEffect);
                    OnSpellEffectAdded?.Invoke(spellEffect);
                    
                    Debug.Log($"Spell effect added: {spellEffect.SpellId} on {spellEffect.Target?.name}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to handle spell effect added: {ex.Message}");
            }
        }

        private void HandleSpellEffectRemoved(string data)
        {
            try
            {
                if (!string.IsNullOrEmpty(data))
                {
                    // Remove from cached state
                    _cachedMagicState.GlobalEffects.RemoveAll(e => e.EffectId == data);
                    OnSpellEffectRemoved?.Invoke(data);
                    
                    Debug.Log($"Spell effect removed: {data}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to handle spell effect removed: {ex.Message}");
            }
        }

        private void HandleSpellcasterUpdated(string data)
        {
            try
            {
                var spellcaster = JsonUtility.FromJson<Spellcaster>(data);
                if (spellcaster != null)
                {
                    _cachedSpellcasters[spellcaster.Name] = spellcaster;
                    
                    // Update in magic state if present
                    var existingCaster = _cachedMagicState.ActiveCasters.Find(c => c.Name == spellcaster.Name);
                    if (existingCaster != null)
                    {
                        var index = _cachedMagicState.ActiveCasters.IndexOf(existingCaster);
                        _cachedMagicState.ActiveCasters[index] = spellcaster;
                    }
                    
                    OnSpellcasterUpdated?.Invoke(spellcaster);
                    
                    Debug.Log($"Spellcaster updated: {spellcaster.Name}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to handle spellcaster update: {ex.Message}");
            }
        }

        private void HandleManaChanged(string data)
        {
            try
            {
                var manaData = JsonUtility.FromJson<ManaChangeData>(data);
                if (manaData != null)
                {
                    // Update cached spellcaster if available
                    if (_cachedSpellcasters.TryGetValue(manaData.CasterId, out var caster))
                    {
                        caster.CurrentMana = manaData.NewMana;
                    }
                    
                    OnManaChanged?.Invoke(manaData.CasterId, manaData.NewMana);
                    
                    Debug.Log($"Mana changed for {manaData.CasterId}: {manaData.NewMana}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to handle mana change: {ex.Message}");
            }
        }

        private void HandleConcentrationChanged(string data)
        {
            try
            {
                var concentrationData = JsonUtility.FromJson<ConcentrationChangeData>(data);
                if (concentrationData != null)
                {
                    // Update cached spellcaster if available
                    if (_cachedSpellcasters.TryGetValue(concentrationData.CasterId, out var caster))
                    {
                        caster.CurrentConcentration = concentrationData.NewConcentration;
                    }
                    
                    OnConcentrationChanged?.Invoke(concentrationData.CasterId, concentrationData.NewConcentration);
                    
                    Debug.Log($"Concentration changed for {concentrationData.CasterId}: {concentrationData.NewConcentration}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to handle concentration change: {ex.Message}");
            }
        }

        private void HandleMagicSessionJoined(string data)
        {
            try
            {
                var sessionData = JsonUtility.FromJson<MagicSessionData>(data);
                if (sessionData != null)
                {
                    Debug.Log($"Joined magic session: {sessionData.SessionId}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to handle magic session joined: {ex.Message}");
            }
        }

        private void HandleMagicSessionLeft(string data)
        {
            try
            {
                Debug.Log("Left magic session");
                
                // Clear cached data
                _cachedMagicState = new MagicSystemState();
                _cachedSpellcasters.Clear();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to handle magic session left: {ex.Message}");
            }
        }

        private void HandleMagicSessionEnded(string data)
        {
            try
            {
                Debug.Log("Magic session ended");
                
                // Clear cached data
                _cachedMagicState = new MagicSystemState();
                _cachedSpellcasters.Clear();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to handle magic session ended: {ex.Message}");
            }
        }

        #endregion

        #region Public Methods

        /// <summary>
        /// Get the current cached magic system state
        /// </summary>
        public MagicSystemState GetCachedMagicState()
        {
            return _cachedMagicState;
        }

        /// <summary>
        /// Get a cached spellcaster by name
        /// </summary>
        public Spellcaster GetCachedSpellcaster(string casterId)
        {
            return _cachedSpellcasters.TryGetValue(casterId, out var caster) ? caster : null;
        }

        /// <summary>
        /// Get all cached spellcasters
        /// </summary>
        public Dictionary<string, Spellcaster> GetCachedSpellcasters()
        {
            return new Dictionary<string, Spellcaster>(_cachedSpellcasters);
        }

        /// <summary>
        /// Request current magic state from server
        /// </summary>
        public void RequestMagicState()
        {
            var message = new
            {
                type = "request_magic_state"
            };
            SendMessage(message);
        }

        /// <summary>
        /// Request spellcaster information
        /// </summary>
        public void RequestSpellcasterInfo(string casterId)
        {
            var message = new
            {
                type = "request_spellcaster_info",
                casterId = casterId
            };
            SendMessage(message);
        }

        #endregion

        #region Cleanup

        protected override void OnDestroy()
        {
            base.OnDestroy();
            
            // Clear cached data
            _cachedMagicState = null;
            _cachedSpellcasters?.Clear();
        }

        #endregion
    }

    #region Data Transfer Objects

    [Serializable]
    public class ManaChangeData
    {
        public string CasterId;
        public int NewMana;
        public int MaxMana;
        public int Change;
    }

    [Serializable]
    public class ConcentrationChangeData
    {
        public string CasterId;
        public int NewConcentration;
        public int MaxConcentration;
        public int Change;
    }

    [Serializable]
    public class MagicSessionData
    {
        public string SessionId;
        public List<string> Participants = new List<string>();
        public bool IsActive;
    }

    #endregion
} 