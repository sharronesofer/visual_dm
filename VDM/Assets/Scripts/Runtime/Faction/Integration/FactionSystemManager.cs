using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.Runtime.Core.Integration;
using VDM.Runtime.Faction.Models;
using VDM.Runtime.Faction.Services;
using VDM.Runtime.Faction.UI;


namespace VDM.Runtime.Faction.Integration
{
    /// <summary>
    /// Faction System Manager
    /// Manages the faction system lifecycle, integration with Unity, and coordination with other systems
    /// </summary>
    public class FactionSystemManager : SystemManager
    {
        [Header("Faction System Configuration")]
        [SerializeField] private bool autoLoadFactions = true;
        [SerializeField] private bool enableDiplomaticEvents = true;
        [SerializeField] private float relationshipUpdateInterval = 120f; // 2 minutes

        [Header("UI References")]
        [SerializeField] private FactionPanel factionPanel;
        [SerializeField] private GameObject factionListPrefab;
        [SerializeField] private Transform factionUIContainer;

        // Services
        private FactionService _factionService;
        
        // Current state
        private FactionResponseDTO _activeFaction;
        private List<FactionResponseDTO> _loadedFactions = new List<FactionResponseDTO>();
        private Dictionary<string, FactionRelationshipResponseDTO> _loadedRelationships = new Dictionary<string, FactionRelationshipResponseDTO>();
        
        // Update timers
        private float _lastRelationshipUpdate;

        // Events
        public event Action<FactionResponseDTO> OnActiveFactionChanged;
        public event Action<List<FactionResponseDTO>> OnFactionsLoaded;
        public event Action<FactionResponseDTO> OnFactionCreated;
        public event Action<FactionResponseDTO> OnFactionUpdated;
        public event Action<int> OnFactionDeleted;
        public event Action<FactionRelationshipResponseDTO> OnRelationshipChanged;
        public event Action<FactionMembershipResponseDTO> OnMembershipChanged;
        public event Action<int, int, string> OnDiplomaticEvent;

        protected override void InitializeSystem()
        {
            base.InitializeSystem();

            // Initialize faction service
            _factionService = GetOrCreateService<FactionService>();
            
            if (_factionService != null)
            {
                // Subscribe to service events
                _factionService.OnFactionCreated += HandleFactionCreated;
                _factionService.OnFactionUpdated += HandleFactionUpdated;
                _factionService.OnFactionDeleted += HandleFactionDeleted;
                _factionService.OnFactionsLoaded += HandleFactionsLoaded;
                _factionService.OnRelationshipChanged += HandleRelationshipChanged;
                _factionService.OnMembershipChanged += HandleMembershipChanged;
                _factionService.OnDiplomaticEvent += HandleDiplomaticEvent;
            }

            // Setup UI if available
            SetupUI();

            // Auto load factions if enabled
            if (autoLoadFactions)
            {
                LoadFactions();
            }

            _lastRelationshipUpdate = Time.time;
        }

        protected override void OnDestroy()
        {
            // Cleanup service events
            if (_factionService != null)
            {
                _factionService.OnFactionCreated -= HandleFactionCreated;
                _factionService.OnFactionUpdated -= HandleFactionUpdated;
                _factionService.OnFactionDeleted -= HandleFactionDeleted;
                _factionService.OnFactionsLoaded -= HandleFactionsLoaded;
                _factionService.OnRelationshipChanged -= HandleRelationshipChanged;
                _factionService.OnMembershipChanged -= HandleMembershipChanged;
                _factionService.OnDiplomaticEvent -= HandleDiplomaticEvent;
            }

            base.OnDestroy();
        }

        private void Update()
        {
            // Periodic relationship updates
            if (enableDiplomaticEvents && _loadedFactions.Count > 0 && 
                Time.time - _lastRelationshipUpdate > relationshipUpdateInterval)
            {
                UpdateRelationshipsForActiveFaction();
                _lastRelationshipUpdate = Time.time;
            }
        }

        private void SetupUI()
        {
            if (factionPanel != null)
            {
                factionPanel.OnFactionSelected += HandleFactionSelected;
                factionPanel.OnEditRequested += HandleEditFactionRequested;
                factionPanel.OnDiplomaticActionsRequested += HandleDiplomaticActionsRequested;
                factionPanel.OnTerritoryRequested += HandleTerritoryRequested;
                factionPanel.OnFinanceRequested += HandleFinanceRequested;
                factionPanel.OnLeaderRequested += HandleLeaderRequested;
                factionPanel.OnHeadquartersRequested += HandleHeadquartersRequested;
            }
        }

        #region Public API

        /// <summary>
        /// Set the active faction
        /// </summary>
        public void SetActiveFaction(FactionResponseDTO faction)
        {
            if (faction == null) return;

            _activeFaction = faction;
            
            // Update UI
            if (factionPanel != null)
            {
                factionPanel.DisplayFaction(faction);
            }

            OnActiveFactionChanged?.Invoke(faction);
            
            if (debugLogging)
                Debug.Log($"[FactionSystemManager] Active faction set to: {faction.Name}");
        }

        /// <summary>
        /// Set active faction by ID
        /// </summary>
        public void SetActiveFactionById(int factionId)
        {
            if (_factionService == null) return;

            _factionService.GetFaction(factionId, (success, faction) =>
            {
                if (success && faction != null)
                {
                    SetActiveFaction(faction);
                }
                else
                {
                    Debug.LogError($"[FactionSystemManager] Failed to load faction {factionId}");
                }
            });
        }

        /// <summary>
        /// Get the currently active faction
        /// </summary>
        public FactionResponseDTO GetActiveFaction()
        {
            return _activeFaction;
        }

        /// <summary>
        /// Load all factions
        /// </summary>
        public void LoadFactions(int page = 1, int pageSize = 50, string factionType = null)
        {
            if (_factionService == null)
            {
                Debug.LogError("[FactionSystemManager] FactionService not available!");
                return;
            }

            _factionService.GetFactions(page, pageSize, factionType, (success, result) =>
            {
                if (success && result != null)
                {
                    _loadedFactions = result.Factions ?? new List<FactionResponseDTO>();
                    OnFactionsLoaded?.Invoke(_loadedFactions);
                    
                    if (debugLogging)
                        Debug.Log($"[FactionSystemManager] Loaded {_loadedFactions.Count} factions");
                }
                else
                {
                    Debug.LogError("[FactionSystemManager] Failed to load factions");
                }
            });
        }

        /// <summary>
        /// Create a new faction
        /// </summary>
        public void CreateFaction(FactionCreateDTO factionData)
        {
            if (_factionService == null)
            {
                Debug.LogError("[FactionSystemManager] FactionService not available!");
                return;
            }

            _factionService.CreateFaction(factionData, (success, faction) =>
            {
                if (success && faction != null)
                {
                    // Add to loaded factions
                    _loadedFactions.Add(faction);
                    OnFactionCreated?.Invoke(faction);
                    
                    // Set as active if no current active faction
                    if (_activeFaction == null)
                    {
                        SetActiveFaction(faction);
                    }
                    
                    if (debugLogging)
                        Debug.Log($"[FactionSystemManager] Created faction: {faction.Name}");
                }
                else
                {
                    Debug.LogError("[FactionSystemManager] Failed to create faction");
                }
            });
        }

        /// <summary>
        /// Update a faction
        /// </summary>
        public void UpdateFaction(int factionId, FactionUpdateDTO updateData)
        {
            if (_factionService == null)
            {
                Debug.LogError("[FactionSystemManager] FactionService not available!");
                return;
            }

            _factionService.UpdateFaction(factionId, updateData, (success, faction) =>
            {
                if (success && faction != null)
                {
                    // Update in loaded factions list
                    int index = _loadedFactions.FindIndex(f => f.Id == faction.Id);
                    if (index >= 0)
                    {
                        _loadedFactions[index] = faction;
                    }
                    
                    // Update active faction if it's the same one
                    if (_activeFaction != null && _activeFaction.Id == faction.Id)
                    {
                        _activeFaction = faction;
                        OnActiveFactionChanged?.Invoke(faction);
                    }
                    
                    OnFactionUpdated?.Invoke(faction);
                    
                    if (debugLogging)
                        Debug.Log($"[FactionSystemManager] Updated faction: {faction.Name}");
                }
                else
                {
                    Debug.LogError($"[FactionSystemManager] Failed to update faction {factionId}");
                }
            });
        }

        /// <summary>
        /// Delete a faction
        /// </summary>
        public void DeleteFaction(int factionId)
        {
            if (_factionService == null)
            {
                Debug.LogError("[FactionSystemManager] FactionService not available!");
                return;
            }

            _factionService.DeleteFaction(factionId, (success) =>
            {
                if (success)
                {
                    // Remove from loaded factions
                    _loadedFactions.RemoveAll(f => f.Id == factionId);
                    
                    // Clear active faction if it was deleted
                    if (_activeFaction != null && _activeFaction.Id == factionId)
                    {
                        _activeFaction = null;
                        OnActiveFactionChanged?.Invoke(null);
                        
                        if (factionPanel != null)
                        {
                            factionPanel.DisplayFaction(null);
                        }
                    }
                    
                    OnFactionDeleted?.Invoke(factionId);
                    
                    if (debugLogging)
                        Debug.Log($"[FactionSystemManager] Deleted faction: {factionId}");
                }
                else
                {
                    Debug.LogError($"[FactionSystemManager] Failed to delete faction {factionId}");
                }
            });
        }

        /// <summary>
        /// Set diplomatic stance between two factions
        /// </summary>
        public void SetDiplomaticStance(int factionId, int otherFactionId, DiplomaticStance stance, float? tension = null, string reason = "")
        {
            if (_factionService == null)
            {
                Debug.LogError("[FactionSystemManager] FactionService not available!");
                return;
            }

            var stanceData = new DiplomaticStanceChangeDTO
            {
                Stance = stance.ToString().ToLower(),
                Tension = tension,
                Reason = reason
            };

            _factionService.SetDiplomaticStance(factionId, otherFactionId, stanceData, (success, relationship) =>
            {
                if (success && relationship != null)
                {
                    // Update relationship cache
                    string cacheKey = $"{relationship.FactionId}_{relationship.OtherFactionId}";
                    _loadedRelationships[cacheKey] = relationship;
                    
                    OnRelationshipChanged?.Invoke(relationship);
                    
                    if (debugLogging)
                        Debug.Log($"[FactionSystemManager] Set diplomatic stance between {factionId} and {otherFactionId} to {stance}");
                }
                else
                {
                    Debug.LogError($"[FactionSystemManager] Failed to set diplomatic stance");
                }
            });
        }

        /// <summary>
        /// Add character to faction
        /// </summary>
        public void AddCharacterToFaction(int factionId, int characterId, string role = "", int rank = 0)
        {
            if (_factionService == null)
            {
                Debug.LogError("[FactionSystemManager] FactionService not available!");
                return;
            }

            var membershipData = new FactionMembershipChangeDTO
            {
                CharacterId = characterId,
                Role = role,
                Rank = rank
            };

            _factionService.AddCharacterToFaction(factionId, membershipData, (success, membership) =>
            {
                if (success && membership != null)
                {
                    OnMembershipChanged?.Invoke(membership);
                    
                    if (debugLogging)
                        Debug.Log($"[FactionSystemManager] Added character {characterId} to faction {factionId}");
                }
                else
                {
                    Debug.LogError($"[FactionSystemManager] Failed to add character to faction");
                }
            });
        }

        /// <summary>
        /// Remove character from faction
        /// </summary>
        public void RemoveCharacterFromFaction(int factionId, int characterId)
        {
            if (_factionService == null)
            {
                Debug.LogError("[FactionSystemManager] FactionService not available!");
                return;
            }

            _factionService.RemoveCharacterFromFaction(factionId, characterId, (success) =>
            {
                if (success)
                {
                    if (debugLogging)
                        Debug.Log($"[FactionSystemManager] Removed character {characterId} from faction {factionId}");
                }
                else
                {
                    Debug.LogError($"[FactionSystemManager] Failed to remove character from faction");
                }
            });
        }

        /// <summary>
        /// Get relationship between two factions
        /// </summary>
        public void GetFactionRelationship(int factionId, int otherFactionId, Action<FactionRelationshipResponseDTO> callback = null)
        {
            if (_factionService == null)
            {
                Debug.LogError("[FactionSystemManager] FactionService not available!");
                callback?.Invoke(null);
                return;
            }

            _factionService.GetFactionRelationship(factionId, otherFactionId, (success, relationship) =>
            {
                if (success && relationship != null)
                {
                    // Update relationship cache
                    string cacheKey = $"{relationship.FactionId}_{relationship.OtherFactionId}";
                    _loadedRelationships[cacheKey] = relationship;
                }
                
                callback?.Invoke(relationship);
            });
        }

        /// <summary>
        /// Get all loaded factions
        /// </summary>
        public List<FactionResponseDTO> GetLoadedFactions()
        {
            return new List<FactionResponseDTO>(_loadedFactions);
        }

        /// <summary>
        /// Get faction by ID from loaded factions
        /// </summary>
        public FactionResponseDTO GetFactionById(int factionId)
        {
            return _loadedFactions.Find(f => f.Id == factionId);
        }

        #endregion

        #region Event Handlers

        private void HandleFactionCreated(FactionResponseDTO faction)
        {
            OnFactionCreated?.Invoke(faction);
        }

        private void HandleFactionUpdated(FactionResponseDTO faction)
        {
            OnFactionUpdated?.Invoke(faction);
        }

        private void HandleFactionDeleted(int factionId)
        {
            OnFactionDeleted?.Invoke(factionId);
        }

        private void HandleFactionsLoaded(List<FactionResponseDTO> factions)
        {
            OnFactionsLoaded?.Invoke(factions);
        }

        private void HandleRelationshipChanged(FactionRelationshipResponseDTO relationship)
        {
            OnRelationshipChanged?.Invoke(relationship);
            
            // Update relationship cache
            string cacheKey = $"{relationship.FactionId}_{relationship.OtherFactionId}";
            _loadedRelationships[cacheKey] = relationship;
            
            ShowNotification($"Relationship changed between factions {relationship.FactionId} and {relationship.OtherFactionId}", NotificationType.Info);
        }

        private void HandleMembershipChanged(FactionMembershipResponseDTO membership)
        {
            OnMembershipChanged?.Invoke(membership);
            
            ShowNotification($"Membership changed for character {membership.CharacterId} in faction {membership.FactionId}", NotificationType.Info);
        }

        private void HandleDiplomaticEvent(int faction1Id, int faction2Id, string eventType)
        {
            OnDiplomaticEvent?.Invoke(faction1Id, faction2Id, eventType);
            
            ShowNotification($"Diplomatic event: {eventType} between factions {faction1Id} and {faction2Id}", NotificationType.Warning);
            
            // Refresh affected factions if they're loaded
            if (_activeFaction != null && (_activeFaction.Id == faction1Id || _activeFaction.Id == faction2Id))
            {
                SetActiveFactionById(_activeFaction.Id);
            }
        }

        private void HandleFactionSelected(FactionResponseDTO faction)
        {
            SetActiveFaction(faction);
        }

        private void HandleEditFactionRequested(FactionResponseDTO faction)
        {
            // TODO: Open faction editing interface
            Debug.Log($"[FactionSystemManager] Edit requested for faction: {faction?.Name}");
        }

        private void HandleDiplomaticActionsRequested(FactionResponseDTO faction)
        {
            // TODO: Open diplomatic actions interface
            Debug.Log($"[FactionSystemManager] Diplomatic actions requested for faction: {faction?.Name}");
        }

        private void HandleTerritoryRequested(FactionResponseDTO faction)
        {
            // TODO: Open territory management interface
            Debug.Log($"[FactionSystemManager] Territory requested for faction: {faction?.Name}");
        }

        private void HandleFinanceRequested(FactionResponseDTO faction)
        {
            // TODO: Open finance management interface
            Debug.Log($"[FactionSystemManager] Finance requested for faction: {faction?.Name}");
        }

        private void HandleLeaderRequested(int characterId)
        {
            // TODO: Open character details for faction leader
            Debug.Log($"[FactionSystemManager] Leader details requested for character: {characterId}");
        }

        private void HandleHeadquartersRequested(int locationId)
        {
            // TODO: Open location details for faction headquarters
            Debug.Log($"[FactionSystemManager] Headquarters details requested for location: {locationId}");
        }

        #endregion

        #region Relationship Updates

        private void UpdateRelationshipsForActiveFaction()
        {
            if (_activeFaction == null || _factionService == null) return;

            _factionService.GetFactionRelationships(_activeFaction.Id, (success, relationships) =>
            {
                if (success && relationships != null)
                {
                    // Update relationship cache
                    foreach (var relationship in relationships)
                    {
                        string cacheKey = $"{relationship.FactionId}_{relationship.OtherFactionId}";
                        _loadedRelationships[cacheKey] = relationship;
                    }
                    
                    if (debugLogging)
                        Debug.Log($"[FactionSystemManager] Updated {relationships.Count} relationships for faction {_activeFaction.Name}");
                }
            });
        }

        #endregion

        #region Utility Methods

        private void ShowNotification(string message, NotificationType type)
        {
            // TODO: Integrate with notification system
            Debug.Log($"[FactionSystemManager] {type}: {message}");
        }

        /// <summary>
        /// Get cached relationship without making a network request
        /// </summary>
        public FactionRelationshipResponseDTO GetCachedRelationship(int factionId, int otherFactionId)
        {
            string cacheKey = $"{factionId}_{otherFactionId}";
            return _loadedRelationships.ContainsKey(cacheKey) ? _loadedRelationships[cacheKey] : null;
        }

        /// <summary>
        /// Check if two factions are allies
        /// </summary>
        public bool AreFactionsAllied(int factionId, int otherFactionId)
        {
            var relationship = GetCachedRelationship(factionId, otherFactionId);
            return relationship?.Stance == DiplomaticStance.Allied;
        }

        /// <summary>
        /// Check if two factions are at war
        /// </summary>
        public bool AreFactionsAtWar(int factionId, int otherFactionId)
        {
            var relationship = GetCachedRelationship(factionId, otherFactionId);
            return relationship?.Stance == DiplomaticStance.AtWar || relationship?.IsAtWar == true;
        }

        #endregion
    }

    public enum NotificationType
    {
        Info,
        Success,
        Warning,
        Error
    }
} 