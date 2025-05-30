using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Runtime.Combat
{
    /// <summary>
    /// Turn-based combat controller implementing tactical combat mechanics
    /// including initiative, actions, damage calculation, and combat conditions.
    /// </summary>
    public class TurnBasedCombatController : MonoBehaviour
    {
        [Header("Combat Configuration")]
        [SerializeField] private bool debugMode = false;
        [SerializeField] private float actionTimeout = 30f;
        
        // Core combat systems
        public TurnManager TurnManager { get; private set; }
        public EntityTracker EntityTracker { get; private set; }
        public StateValidator StateValidator { get; private set; }
        public ActionProcessor ActionProcessor { get; private set; }
        
        // Combat state
        private bool _combatActive = false;
        private List<GameObject> _combatants = new List<GameObject>();
        
        // Events
        public event Action<GameObject> OnCombatantAdded;
        public event Action<GameObject> OnCombatantRemoved;
        public event Action OnCombatStarted;
        public event Action OnCombatEnded;
        
        private void Awake()
        {
            InitializeSystems();
        }
        
        private void InitializeSystems()
        {
            TurnManager = new TurnManager();
            EntityTracker = new EntityTracker();
            StateValidator = new StateValidator();
            ActionProcessor = new ActionProcessor();
            
            // Wire up events
            TurnManager.OnTurnEnded += HandleTurnEnded;
            ActionProcessor.OnActionCompleted += HandleActionCompleted;
        }
        
        /// <summary>
        /// Start combat with the given list of combatants
        /// </summary>
        public void StartCombat(List<GameObject> combatants)
        {
            if (combatants == null || combatants.Count == 0)
            {
                Debug.LogWarning("Cannot start combat with no combatants");
                return;
            }
            
            _combatants.Clear();
            _combatants.AddRange(combatants);
            
            // Initialize all combatants in systems
            foreach (var combatant in combatants)
            {
                EntityTracker.TrackEntity(combatant);
                TurnManager.AddCombatant(combatant);
            }
            
            // Initialize turn order based on initiative
            TurnManager.InitializeTurnOrder();
            
            _combatActive = true;
            OnCombatStarted?.Invoke();
            
            if (debugMode)
                Debug.Log($"Combat started with {combatants.Count} combatants");
        }
        
        /// <summary>
        /// Add a combatant to active combat
        /// </summary>
        public void AddCombatant(GameObject combatant)
        {
            if (combatant == null || _combatants.Contains(combatant))
                return;
                
            _combatants.Add(combatant);
            EntityTracker.TrackEntity(combatant);
            TurnManager.AddCombatant(combatant);
            
            OnCombatantAdded?.Invoke(combatant);
            
            if (debugMode)
                Debug.Log($"Added combatant: {combatant.name}");
        }
        
        /// <summary>
        /// Remove a combatant from active combat
        /// </summary>
        public void RemoveCombatant(GameObject combatant)
        {
            if (combatant == null || !_combatants.Contains(combatant))
                return;
                
            _combatants.Remove(combatant);
            TurnManager.RemoveCombatant(combatant);
            EntityTracker.UntrackEntity(combatant);
            
            OnCombatantRemoved?.Invoke(combatant);
            
            if (debugMode)
                Debug.Log($"Removed combatant: {combatant.name}");
                
            // Check if combat should end
            CheckCombatEndConditions();
        }
        
        /// <summary>
        /// Process a combat action
        /// </summary>
        public void ProcessAction(ActionRequest request, CharacterState characterState)
        {
            if (!_combatActive)
            {
                Debug.LogWarning("Cannot process action: Combat not active");
                return;
            }
            
            // Validate action
            if (!StateValidator.ValidateAction(request, characterState))
            {
                Debug.LogWarning($"Invalid action: {request.ActionType}");
                return;
            }
            
            // Process the action
            ActionProcessor.ProcessAction(request, characterState);
            
            // End current turn
            TurnManager.EndCurrentTurn();
        }
        
        /// <summary>
        /// End combat immediately
        /// </summary>
        public void EndCombat()
        {
            if (!_combatActive)
                return;
                
            _combatActive = false;
            TurnManager.Reset();
            EntityTracker.ClearTracking();
            _combatants.Clear();
            
            OnCombatEnded?.Invoke();
            
            if (debugMode)
                Debug.Log("Combat ended");
        }
        
        private void HandleTurnEnded(GameObject entity)
        {
            // Process end-of-turn effects
            var state = EntityTracker.GetState(entity);
            if (state != null)
            {
                ProcessEndOfTurnEffects(entity, state);
            }
            
            // Check combat end conditions
            CheckCombatEndConditions();
        }
        
        private void HandleActionCompleted(ActionRequest request, ActionResult result)
        {
            // Update entity states based on action results
            if (result.TargetEntity != null)
            {
                var targetState = EntityTracker.GetState(result.TargetEntity);
                if (targetState != null)
                {
                    ApplyActionResults(targetState, result);
                }
            }
        }
        
        private void ProcessEndOfTurnEffects(GameObject entity, CharacterState state)
        {
            // Handle ongoing effects, regeneration, etc.
            // This would be expanded based on specific game rules
        }
        
        private void ApplyActionResults(CharacterState targetState, ActionResult result)
        {
            // Apply damage, healing, conditions, etc.
            if (result.Damage > 0)
            {
                targetState.CurrentHP = Mathf.Max(0, targetState.CurrentHP - result.Damage);
                if (targetState.CurrentHP <= 0)
                {
                    targetState.IsAlive = false;
                }
            }
        }
        
        private void CheckCombatEndConditions()
        {
            // Check if any faction has been eliminated
            // This would be more sophisticated in a real implementation
            var aliveCombatants = _combatants.FindAll(c => 
            {
                var state = EntityTracker.GetState(c);
                return state != null && state.IsAlive;
            });
            
            if (aliveCombatants.Count <= 1)
            {
                EndCombat();
            }
        }
        
        private void OnDestroy()
        {
            if (TurnManager != null)
                TurnManager.OnTurnEnded -= HandleTurnEnded;
                
            if (ActionProcessor != null)
                ActionProcessor.OnActionCompleted -= HandleActionCompleted;
        }
    }
    
    /// <summary>
    /// Action types available in combat
    /// </summary>
    public enum ActionType
    {
        Attack,
        Cast,
        Dodge,
        Dash,
        Disengage,
        Hide,
        Help,
        Ready,
        ChainAction
    }
    
    /// <summary>
    /// Request for a combat action
    /// </summary>
    [System.Serializable]
    public class ActionRequest
    {
        public ActionType ActionType { get; set; }
        public int EntityId { get; set; }
        public float Timestamp { get; set; }
        public GameObject Target { get; set; }
        public Vector3 Position { get; set; }
        public Dictionary<string, object> Parameters { get; set; }
        
        public ActionRequest(ActionType actionType, int entityId, float timestamp)
        {
            ActionType = actionType;
            EntityId = entityId;
            Timestamp = timestamp;
            Parameters = new Dictionary<string, object>();
        }
    }
    
    /// <summary>
    /// Character state for combat tracking
    /// </summary>
    [System.Serializable]
    public class CharacterState
    {
        public int MaxHP { get; set; } = 100;
        public int CurrentHP { get; set; } = 100;
        public int ArmorClass { get; set; } = 10;
        public int Initiative { get; set; } = 0;
        public bool IsAlive { get; set; } = true;
        public bool CanAct { get; set; } = true;
        public List<string> Conditions { get; set; } = new List<string>();
        public Dictionary<string, int> Stats { get; set; } = new Dictionary<string, int>();
    }
} 