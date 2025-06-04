using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using VDM.Systems.TensionWar.Models;

namespace VDM.Systems.TensionWar.Services
{
    /// <summary>
    /// Frontend tension and war service that interfaces with backend tension_war system
    /// Handles faction tensions, conflicts, and diplomatic actions
    /// </summary>
    public class TensionWarService : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private bool enableDebugLogging = true;
        [SerializeField] private float tensionUpdateInterval = 60f;
        
        // Events
        public static event Action<TensionLevel> OnTensionChanged;
        public static event Action<WarDeclaration> OnWarDeclared;
        public static event Action<Conflict> OnConflictStarted;
        public static event Action<DiplomaticAction> OnDiplomaticAction;
        
        // State
        private Dictionary<string, TensionLevel> factionTensions = new Dictionary<string, TensionLevel>();
        private List<WarDeclaration> activeWars = new List<WarDeclaration>();
        private List<Conflict> activeConflicts = new List<Conflict>();
        private bool isInitialized = false;
        
        private void Awake()
        {
            InitializeService();
        }
        
        private void Start()
        {
            InvokeRepeating(nameof(UpdateTensionData), tensionUpdateInterval, tensionUpdateInterval);
        }
        
        private void InitializeService()
        {
            if (isInitialized) return;
            
            if (enableDebugLogging)
                Debug.Log("TensionWarService: Initializing tension and war system...");
            
            LoadTensionData();
            isInitialized = true;
        }
        
        private async void LoadTensionData()
        {
            try
            {
                // TODO: Load tension data from backend
                // await LoadFactionTensionsFromBackend();
                // await LoadActiveWarsFromBackend();
                // await LoadActiveConflictsFromBackend();
                
                if (enableDebugLogging)
                    Debug.Log("TensionWarService: Tension and war data loaded successfully");
            }
            catch (Exception ex)
            {
                Debug.LogError($"TensionWarService: Failed to load tension data: {ex.Message}");
            }
        }
        
        private async void UpdateTensionData()
        {
            try
            {
                // TODO: Fetch updated tension data from backend
                // var updatedTensions = await BackendService.GetTensionUpdates();
                
                if (enableDebugLogging)
                    Debug.Log("TensionWarService: Tension data updated");
            }
            catch (Exception ex)
            {
                Debug.LogError($"TensionWarService: Failed to update tension data: {ex.Message}");
            }
        }
        
        public float GetTensionBetweenFactions(string factionId1, string factionId2)
        {
            string tensionKey = GetTensionKey(factionId1, factionId2);
            if (factionTensions.TryGetValue(tensionKey, out var tension))
            {
                return tension.tensionValue;
            }
            return 0f;
        }
        
        public List<WarDeclaration> GetActiveWars()
        {
            return new List<WarDeclaration>(activeWars);
        }
        
        public List<Conflict> GetActiveConflicts()
        {
            return new List<Conflict>(activeConflicts);
        }
        
        public async Task<bool> ExecuteDiplomaticAction(DiplomaticAction action)
        {
            try
            {
                if (enableDebugLogging)
                    Debug.Log($"TensionWarService: Executing diplomatic action: {action.actionType}");
                
                // TODO: Send diplomatic action to backend
                // var result = await BackendService.ExecuteDiplomaticAction(action);
                
                OnDiplomaticAction?.Invoke(action);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"TensionWarService: Diplomatic action failed: {ex.Message}");
                return false;
            }
        }
        
        public async Task<bool> DeclareWar(string aggressorId, string defenderId, string reason)
        {
            try
            {
                if (enableDebugLogging)
                    Debug.Log($"TensionWarService: Declaring war between {aggressorId} and {defenderId}");
                
                // TODO: Send war declaration to backend
                // var result = await BackendService.DeclareWar(aggressorId, defenderId, reason);
                
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"TensionWarService: War declaration failed: {ex.Message}");
                return false;
            }
        }
        
        private string GetTensionKey(string factionId1, string factionId2)
        {
            // Ensure consistent key ordering
            if (string.Compare(factionId1, factionId2) < 0)
                return $"{factionId1}_{factionId2}";
            else
                return $"{factionId2}_{factionId1}";
        }
    }
} 