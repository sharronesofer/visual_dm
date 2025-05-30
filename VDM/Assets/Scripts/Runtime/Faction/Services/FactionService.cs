using Newtonsoft.Json;
using System.Collections.Generic;
using System.Collections;
using System;
using UnityEngine;
using VDM.Runtime.Core.Services;
using VDM.Runtime.Faction.Models;
using VDM.Runtime.Integration;


namespace VDM.Runtime.Faction.Services
{
    /// <summary>
    /// Service for managing faction data communication with the backend
    /// Handles faction CRUD operations, relationships, memberships, and diplomatic actions
    /// </summary>
    public class FactionService : BaseHTTPClient
    {
        [Header("Faction Service Configuration")]
        [SerializeField] private bool autoSyncFactions = true;
        [SerializeField] private float syncInterval = 60f; // Longer interval for factions

        // Faction events
        public event Action<FactionResponseDTO> OnFactionCreated;
        public event Action<FactionResponseDTO> OnFactionUpdated;
        public event Action<int> OnFactionDeleted;
        public event Action<List<FactionResponseDTO>> OnFactionsLoaded;
        public event Action<FactionRelationshipResponseDTO> OnRelationshipChanged;
        public event Action<FactionMembershipResponseDTO> OnMembershipChanged;
        public event Action<int, int, string> OnDiplomaticEvent; // faction1, faction2, event type

        // Local faction cache
        private Dictionary<int, FactionResponseDTO> _factionCache = new Dictionary<int, FactionResponseDTO>();
        private Dictionary<string, FactionRelationshipResponseDTO> _relationshipCache = new Dictionary<string, FactionRelationshipResponseDTO>();
        private Dictionary<string, FactionMembershipResponseDTO> _membershipCache = new Dictionary<string, FactionMembershipResponseDTO>();

        // WebSocket integration
        private WebSocketManager _webSocketManager;

        // Coroutines
        private Coroutine _autoSyncCoroutine;

        protected override string GetClientName() => "FactionService";

        protected override void InitializeClient()
        {
            base.InitializeClient();

            // Find WebSocket manager
            _webSocketManager = FindObjectOfType<WebSocketManager>();
            if (_webSocketManager != null)
            {
                // Subscribe to faction-related WebSocket events
                _webSocketManager.RegisterMessageHandler("faction_update", HandleFactionWebSocketUpdate);
                _webSocketManager.RegisterMessageHandler("faction_relationship_change", HandleRelationshipChangeEvent);
                _webSocketManager.RegisterMessageHandler("faction_membership_change", HandleMembershipChangeEvent);
                _webSocketManager.RegisterMessageHandler("diplomatic_event", HandleDiplomaticEvent);
            }

            // Start auto sync if enabled
            if (autoSyncFactions)
            {
                StartAutoSync();
            }
        }

        protected virtual void OnDestroy()
        {
            // Cleanup
            if (_webSocketManager != null)
            {
                _webSocketManager.UnregisterMessageHandler("faction_update");
                _webSocketManager.UnregisterMessageHandler("faction_relationship_change");
                _webSocketManager.UnregisterMessageHandler("faction_membership_change");
                _webSocketManager.UnregisterMessageHandler("diplomatic_event");
            }

            if (_autoSyncCoroutine != null)
            {
                StopCoroutine(_autoSyncCoroutine);
            }

            base.OnDestroy();
        }

        #region Faction CRUD Operations

        /// <summary>
        /// Create a new faction
        /// </summary>
        public void CreateFaction(FactionCreateDTO factionData, Action<bool, FactionResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(CreateFactionCoroutine(factionData, callback));
        }

        private IEnumerator CreateFactionCoroutine(FactionCreateDTO factionData, Action<bool, FactionResponseDTO> callback)
        {
            bool success = false;
            FactionResponseDTO faction = null;

            yield return PostRequestCoroutine("/factions", factionData, (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    faction = SafeDeserialize<FactionResponseDTO>(response);
                    if (faction != null)
                    {
                        _factionCache[faction.Id] = faction;
                        OnFactionCreated?.Invoke(faction);

                        if (debugLogging)
                            Debug.Log($"[FactionService] Created faction: {faction.Name} (ID: {faction.Id})");
                    }
                }
            });

            callback?.Invoke(success, faction);
        }

        /// <summary>
        /// Get a faction by ID
        /// </summary>
        public void GetFaction(int factionId, Action<bool, FactionResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            // Check cache first
            if (_factionCache.ContainsKey(factionId))
            {
                callback?.Invoke(true, _factionCache[factionId]);
                return;
            }

            StartCoroutine(GetFactionCoroutine(factionId, callback));
        }

        private IEnumerator GetFactionCoroutine(int factionId, Action<bool, FactionResponseDTO> callback)
        {
            bool success = false;
            FactionResponseDTO faction = null;

            yield return GetRequestCoroutine($"/factions/{factionId}", (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    faction = SafeDeserialize<FactionResponseDTO>(response);
                    if (faction != null)
                    {
                        _factionCache[faction.Id] = faction;

                        if (debugLogging)
                            Debug.Log($"[FactionService] Retrieved faction: {faction.Name}");
                    }
                }
            });

            callback?.Invoke(success, faction);
        }

        /// <summary>
        /// Update a faction
        /// </summary>
        public void UpdateFaction(int factionId, FactionUpdateDTO updateData, Action<bool, FactionResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(UpdateFactionCoroutine(factionId, updateData, callback));
        }

        private IEnumerator UpdateFactionCoroutine(int factionId, FactionUpdateDTO updateData, Action<bool, FactionResponseDTO> callback)
        {
            bool success = false;
            FactionResponseDTO faction = null;

            yield return PutRequestCoroutine($"/factions/{factionId}", updateData, (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    faction = SafeDeserialize<FactionResponseDTO>(response);
                    if (faction != null)
                    {
                        _factionCache[faction.Id] = faction;
                        OnFactionUpdated?.Invoke(faction);

                        if (debugLogging)
                            Debug.Log($"[FactionService] Updated faction: {faction.Name}");
                    }
                }
            });

            callback?.Invoke(success, faction);
        }

        /// <summary>
        /// Delete a faction
        /// </summary>
        public void DeleteFaction(int factionId, Action<bool> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(DeleteFactionCoroutine(factionId, callback));
        }

        private IEnumerator DeleteFactionCoroutine(int factionId, Action<bool> callback)
        {
            bool success = false;

            yield return DeleteRequestCoroutine($"/factions/{factionId}", (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    _factionCache.Remove(factionId);
                    OnFactionDeleted?.Invoke(factionId);

                    if (debugLogging)
                        Debug.Log($"[FactionService] Deleted faction: {factionId}");
                }
            });

            callback?.Invoke(success);
        }

        /// <summary>
        /// Get a list of factions with pagination
        /// </summary>
        public void GetFactions(int page = 1, int pageSize = 10, string factionType = null, Action<bool, FactionListResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(GetFactionsCoroutine(page, pageSize, factionType, callback));
        }

        private IEnumerator GetFactionsCoroutine(int page, int pageSize, string factionType, Action<bool, FactionListResponseDTO> callback)
        {
            string endpoint = $"/factions?page={page}&page_size={pageSize}";
            if (!string.IsNullOrEmpty(factionType))
            {
                endpoint += $"&type={factionType}";
            }

            bool success = false;
            FactionListResponseDTO result = null;

            yield return GetRequestCoroutine(endpoint, (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    result = SafeDeserialize<FactionListResponseDTO>(response);
                    if (result != null && result.Factions != null)
                    {
                        // Update cache with returned factions
                        foreach (var faction in result.Factions)
                        {
                            _factionCache[faction.Id] = faction;
                        }

                        OnFactionsLoaded?.Invoke(result.Factions);

                        if (debugLogging)
                            Debug.Log($"[FactionService] Loaded {result.Factions.Count} factions");
                    }
                }
            });

            callback?.Invoke(success, result);
        }

        #endregion

        #region Faction Relationships

        /// <summary>
        /// Set diplomatic stance between two factions
        /// </summary>
        public void SetDiplomaticStance(int factionId, int otherFactionId, DiplomaticStanceChangeDTO stanceData, Action<bool, FactionRelationshipResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(SetDiplomaticStanceCoroutine(factionId, otherFactionId, stanceData, callback));
        }

        private IEnumerator SetDiplomaticStanceCoroutine(int factionId, int otherFactionId, DiplomaticStanceChangeDTO stanceData, Action<bool, FactionRelationshipResponseDTO> callback)
        {
            bool success = false;
            FactionRelationshipResponseDTO relationship = null;

            yield return PostRequestCoroutine($"/factions/{factionId}/relationships/{otherFactionId}", stanceData, (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    relationship = SafeDeserialize<FactionRelationshipResponseDTO>(response);
                    if (relationship != null)
                    {
                        string cacheKey = $"{relationship.FactionId}_{relationship.OtherFactionId}";
                        _relationshipCache[cacheKey] = relationship;
                        OnRelationshipChanged?.Invoke(relationship);

                        if (debugLogging)
                            Debug.Log($"[FactionService] Set diplomatic stance between factions {factionId} and {otherFactionId} to {stanceData.Stance}");
                    }
                }
            });

            callback?.Invoke(success, relationship);
        }

        /// <summary>
        /// Get relationship between two factions
        /// </summary>
        public void GetFactionRelationship(int factionId, int otherFactionId, Action<bool, FactionRelationshipResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            string cacheKey = $"{factionId}_{otherFactionId}";
            if (_relationshipCache.ContainsKey(cacheKey))
            {
                callback?.Invoke(true, _relationshipCache[cacheKey]);
                return;
            }

            StartCoroutine(GetFactionRelationshipCoroutine(factionId, otherFactionId, callback));
        }

        private IEnumerator GetFactionRelationshipCoroutine(int factionId, int otherFactionId, Action<bool, FactionRelationshipResponseDTO> callback)
        {
            bool success = false;
            FactionRelationshipResponseDTO relationship = null;

            yield return GetRequestCoroutine($"/factions/{factionId}/relationships/{otherFactionId}", (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    relationship = SafeDeserialize<FactionRelationshipResponseDTO>(response);
                    if (relationship != null)
                    {
                        string cacheKey = $"{relationship.FactionId}_{relationship.OtherFactionId}";
                        _relationshipCache[cacheKey] = relationship;

                        if (debugLogging)
                            Debug.Log($"[FactionService] Retrieved relationship between factions {factionId} and {otherFactionId}");
                    }
                }
            });

            callback?.Invoke(success, relationship);
        }

        /// <summary>
        /// Get all relationships for a faction
        /// </summary>
        public void GetFactionRelationships(int factionId, Action<bool, List<FactionRelationshipResponseDTO>> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(GetFactionRelationshipsCoroutine(factionId, callback));
        }

        private IEnumerator GetFactionRelationshipsCoroutine(int factionId, Action<bool, List<FactionRelationshipResponseDTO>> callback)
        {
            bool success = false;
            List<FactionRelationshipResponseDTO> relationships = null;

            yield return GetRequestCoroutine($"/factions/{factionId}/relationships", (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    relationships = SafeDeserializeList<FactionRelationshipResponseDTO>(response);
                    if (relationships != null)
                    {
                        // Update cache
                        foreach (var relationship in relationships)
                        {
                            string cacheKey = $"{relationship.FactionId}_{relationship.OtherFactionId}";
                            _relationshipCache[cacheKey] = relationship;
                        }

                        if (debugLogging)
                            Debug.Log($"[FactionService] Retrieved {relationships.Count} relationships for faction {factionId}");
                    }
                }
            });

            callback?.Invoke(success, relationships);
        }

        #endregion

        #region Faction Memberships

        /// <summary>
        /// Add a character to a faction
        /// </summary>
        public void AddCharacterToFaction(int factionId, FactionMembershipChangeDTO membershipData, Action<bool, FactionMembershipResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(AddCharacterToFactionCoroutine(factionId, membershipData, callback));
        }

        private IEnumerator AddCharacterToFactionCoroutine(int factionId, FactionMembershipChangeDTO membershipData, Action<bool, FactionMembershipResponseDTO> callback)
        {
            bool success = false;
            FactionMembershipResponseDTO membership = null;

            yield return PostRequestCoroutine($"/factions/{factionId}/members", membershipData, (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    membership = SafeDeserialize<FactionMembershipResponseDTO>(response);
                    if (membership != null)
                    {
                        string cacheKey = $"{membership.FactionId}_{membership.CharacterId}";
                        _membershipCache[cacheKey] = membership;
                        OnMembershipChanged?.Invoke(membership);

                        if (debugLogging)
                            Debug.Log($"[FactionService] Added character {membership.CharacterId} to faction {factionId}");
                    }
                }
            });

            callback?.Invoke(success, membership);
        }

        /// <summary>
        /// Update character's faction membership
        /// </summary>
        public void UpdateFactionMembership(int factionId, int characterId, FactionMembershipChangeDTO membershipData, Action<bool, FactionMembershipResponseDTO> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(UpdateFactionMembershipCoroutine(factionId, characterId, membershipData, callback));
        }

        private IEnumerator UpdateFactionMembershipCoroutine(int factionId, int characterId, FactionMembershipChangeDTO membershipData, Action<bool, FactionMembershipResponseDTO> callback)
        {
            bool success = false;
            FactionMembershipResponseDTO membership = null;

            yield return PutRequestCoroutine($"/factions/{factionId}/members/{characterId}", membershipData, (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    membership = SafeDeserialize<FactionMembershipResponseDTO>(response);
                    if (membership != null)
                    {
                        string cacheKey = $"{membership.FactionId}_{membership.CharacterId}";
                        _membershipCache[cacheKey] = membership;
                        OnMembershipChanged?.Invoke(membership);

                        if (debugLogging)
                            Debug.Log($"[FactionService] Updated membership for character {characterId} in faction {factionId}");
                    }
                }
            });

            callback?.Invoke(success, membership);
        }

        /// <summary>
        /// Remove character from faction
        /// </summary>
        public void RemoveCharacterFromFaction(int factionId, int characterId, Action<bool> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(RemoveCharacterFromFactionCoroutine(factionId, characterId, callback));
        }

        private IEnumerator RemoveCharacterFromFactionCoroutine(int factionId, int characterId, Action<bool> callback)
        {
            bool success = false;

            yield return DeleteRequestCoroutine($"/factions/{factionId}/members/{characterId}", (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    string cacheKey = $"{factionId}_{characterId}";
                    _membershipCache.Remove(cacheKey);

                    if (debugLogging)
                        Debug.Log($"[FactionService] Removed character {characterId} from faction {factionId}");
                }
            });

            callback?.Invoke(success);
        }

        /// <summary>
        /// Get faction memberships for a character
        /// </summary>
        public void GetCharacterFactionMemberships(int characterId, Action<bool, List<FactionMembershipResponseDTO>> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(GetCharacterFactionMembershipsCoroutine(characterId, callback));
        }

        private IEnumerator GetCharacterFactionMembershipsCoroutine(int characterId, Action<bool, List<FactionMembershipResponseDTO>> callback)
        {
            bool success = false;
            List<FactionMembershipResponseDTO> memberships = null;

            yield return GetRequestCoroutine($"/characters/{characterId}/factions", (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    memberships = SafeDeserializeList<FactionMembershipResponseDTO>(response);
                    if (memberships != null)
                    {
                        // Update cache
                        foreach (var membership in memberships)
                        {
                            string cacheKey = $"{membership.FactionId}_{membership.CharacterId}";
                            _membershipCache[cacheKey] = membership;
                        }

                        if (debugLogging)
                            Debug.Log($"[FactionService] Retrieved {memberships.Count} faction memberships for character {characterId}");
                    }
                }
            });

            callback?.Invoke(success, memberships);
        }

        /// <summary>
        /// Get members of a faction
        /// </summary>
        public void GetFactionMembers(int factionId, Action<bool, List<FactionMembershipResponseDTO>> callback = null)
        {
            if (!isInitialized)
            {
                InitializeClient();
            }

            StartCoroutine(GetFactionMembersCoroutine(factionId, callback));
        }

        private IEnumerator GetFactionMembersCoroutine(int factionId, Action<bool, List<FactionMembershipResponseDTO>> callback)
        {
            bool success = false;
            List<FactionMembershipResponseDTO> members = null;

            yield return GetRequestCoroutine($"/factions/{factionId}/members", (requestSuccess, response) =>
            {
                success = requestSuccess;
                if (success)
                {
                    members = SafeDeserializeList<FactionMembershipResponseDTO>(response);
                    if (members != null)
                    {
                        // Update cache
                        foreach (var member in members)
                        {
                            string cacheKey = $"{member.FactionId}_{member.CharacterId}";
                            _membershipCache[cacheKey] = member;
                        }

                        if (debugLogging)
                            Debug.Log($"[FactionService] Retrieved {members.Count} members for faction {factionId}");
                    }
                }
            });

            callback?.Invoke(success, members);
        }

        #endregion

        #region WebSocket Event Handlers

        private void HandleFactionWebSocketUpdate(string message)
        {
            try
            {
                var faction = JsonConvert.DeserializeObject<FactionResponseDTO>(message);
                if (faction != null)
                {
                    _factionCache[faction.Id] = faction;
                    OnFactionUpdated?.Invoke(faction);

                    if (debugLogging)
                        Debug.Log($"[FactionService] Faction {faction.Name} updated via WebSocket");
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[FactionService] Error handling faction update event: {e.Message}");
            }
        }

        private void HandleRelationshipChangeEvent(string message)
        {
            try
            {
                var relationship = JsonConvert.DeserializeObject<FactionRelationshipResponseDTO>(message);
                if (relationship != null)
                {
                    string cacheKey = $"{relationship.FactionId}_{relationship.OtherFactionId}";
                    _relationshipCache[cacheKey] = relationship;
                    OnRelationshipChanged?.Invoke(relationship);

                    if (debugLogging)
                        Debug.Log($"[FactionService] Relationship changed between factions {relationship.FactionId} and {relationship.OtherFactionId}");
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[FactionService] Error handling relationship change event: {e.Message}");
            }
        }

        private void HandleMembershipChangeEvent(string message)
        {
            try
            {
                var membership = JsonConvert.DeserializeObject<FactionMembershipResponseDTO>(message);
                if (membership != null)
                {
                    string cacheKey = $"{membership.FactionId}_{membership.CharacterId}";
                    _membershipCache[cacheKey] = membership;
                    OnMembershipChanged?.Invoke(membership);

                    if (debugLogging)
                        Debug.Log($"[FactionService] Membership changed for character {membership.CharacterId} in faction {membership.FactionId}");
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[FactionService] Error handling membership change event: {e.Message}");
            }
        }

        private void HandleDiplomaticEvent(string message)
        {
            try
            {
                var diplomaticEvent = JsonConvert.DeserializeObject<Dictionary<string, object>>(message);
                if (diplomaticEvent.TryGetValue("faction1_id", out object faction1Obj) &&
                    diplomaticEvent.TryGetValue("faction2_id", out object faction2Obj) &&
                    diplomaticEvent.TryGetValue("event_type", out object eventTypeObj))
                {
                    int faction1Id = Convert.ToInt32(faction1Obj);
                    int faction2Id = Convert.ToInt32(faction2Obj);
                    string eventType = eventTypeObj.ToString();

                    OnDiplomaticEvent?.Invoke(faction1Id, faction2Id, eventType);

                    if (debugLogging)
                        Debug.Log($"[FactionService] Diplomatic event: {eventType} between factions {faction1Id} and {faction2Id}");
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[FactionService] Error handling diplomatic event: {e.Message}");
            }
        }

        #endregion

        #region Auto Sync

        private void StartAutoSync()
        {
            if (_autoSyncCoroutine != null)
            {
                StopCoroutine(_autoSyncCoroutine);
            }

            _autoSyncCoroutine = StartCoroutine(AutoSyncCoroutine());
        }

        private IEnumerator AutoSyncCoroutine()
        {
            while (autoSyncFactions)
            {
                yield return new WaitForSeconds(syncInterval);

                if (_factionCache.Count > 0)
                {
                    if (debugLogging)
                        Debug.Log($"[FactionService] Auto-syncing {_factionCache.Count} cached factions");

                    // Sync cached factions
                    var factionIds = new List<int>(_factionCache.Keys);
                    foreach (var factionId in factionIds)
                    {
                        GetFaction(factionId, null);
                        yield return new WaitForSeconds(0.1f); // Small delay between requests
                    }
                }
            }
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// Get cached faction without making a network request
        /// </summary>
        public FactionResponseDTO GetCachedFaction(int factionId)
        {
            return _factionCache.ContainsKey(factionId) ? _factionCache[factionId] : null;
        }

        /// <summary>
        /// Get cached relationship without making a network request
        /// </summary>
        public FactionRelationshipResponseDTO GetCachedRelationship(int factionId, int otherFactionId)
        {
            string cacheKey = $"{factionId}_{otherFactionId}";
            return _relationshipCache.ContainsKey(cacheKey) ? _relationshipCache[cacheKey] : null;
        }

        /// <summary>
        /// Get cached membership without making a network request
        /// </summary>
        public FactionMembershipResponseDTO GetCachedMembership(int factionId, int characterId)
        {
            string cacheKey = $"{factionId}_{characterId}";
            return _membershipCache.ContainsKey(cacheKey) ? _membershipCache[cacheKey] : null;
        }

        /// <summary>
        /// Clear all caches
        /// </summary>
        public void ClearCache()
        {
            _factionCache.Clear();
            _relationshipCache.Clear();
            _membershipCache.Clear();
            if (debugLogging)
                Debug.Log("[FactionService] All caches cleared");
        }

        /// <summary>
        /// Get all cached factions
        /// </summary>
        public Dictionary<int, FactionResponseDTO> GetAllCachedFactions()
        {
            return new Dictionary<int, FactionResponseDTO>(_factionCache);
        }

        #endregion
    }
} 