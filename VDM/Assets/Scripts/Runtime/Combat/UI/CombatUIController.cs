using System.Collections.Generic;
using System.Linq;
using System;
using TMPro;
using UnityEngine.UI;
using UnityEngine;
using VDM.Runtime.Combat.Models;
using VDM.Runtime.Combat.Services;
using VDM.Runtime.UI;


namespace VDM.Runtime.Combat.UI
{
    /// <summary>
    /// Controls the combat user interface and interactions
    /// </summary>
    public class CombatUIController : UIController
    {
        [Header("Combat UI References")]
        [SerializeField] private GameObject combatPanel;
        [SerializeField] private Transform participantsContainer;
        [SerializeField] private Transform actionsContainer;
        [SerializeField] private ScrollRect combatLogScrollRect;
        [SerializeField] private Transform combatLogContent;
        [SerializeField] private Button endTurnButton;
        [SerializeField] private TextMeshProUGUI currentTurnText;
        [SerializeField] private TextMeshProUGUI roundText;
        
        [Header("Prefabs")]
        [SerializeField] private GameObject combatantUIPrefab;
        [SerializeField] private GameObject actionButtonPrefab;
        [SerializeField] private GameObject combatLogEntryPrefab;
        
        [Header("Combat Configuration")]
        [SerializeField] private float actionAnimationDuration = 1f;
        [SerializeField] private int maxLogEntries = 50;
        
        // Services
        private CombatService _combatService;
        private CombatWebSocketHandler _webSocketHandler;
        
        // State
        private string _currentCombatId;
        private CombatState _currentState;
        private Dictionary<string, GameObject> _combatantUIs = new Dictionary<string, GameObject>();
        private List<CombatAction> _availableActions = new List<CombatAction>();
        private string _selectedTargetId;
        
        // Events
        public event Action<CombatAction, string> OnActionSelected;
        public event Action OnTurnEnded;
        public event Action OnCombatExited;
        
        protected override void Awake()
        {
            base.Awake();
            
            // Get services
            _combatService = ServiceLocator.Get<CombatService>();
            _webSocketHandler = ServiceLocator.Get<CombatWebSocketHandler>();
            
            // Setup UI events
            if (endTurnButton != null)
            {
                endTurnButton.onClick.AddListener(EndTurn);
            }
        }
        
        protected override void OnEnable()
        {
            base.OnEnable();
            
            // Subscribe to combat events
            if (_combatService != null)
            {
                _combatService.OnCombatStarted += HandleCombatStarted;
                _combatService.OnCombatEnded += HandleCombatEnded;
            }
            
            if (_webSocketHandler != null)
            {
                _webSocketHandler.OnCombatEventReceived += HandleCombatEvent;
                _webSocketHandler.OnCombatStateUpdated += HandleStateUpdate;
                _webSocketHandler.OnAvailableActionsUpdated += HandleActionsUpdated;
                _webSocketHandler.OnStatusEffectApplied += HandleStatusEffectApplied;
                _webSocketHandler.OnStatusEffectRemoved += HandleStatusEffectRemoved;
            }
        }
        
        protected override void OnDisable()
        {
            base.OnDisable();
            
            // Unsubscribe from combat events
            if (_combatService != null)
            {
                _combatService.OnCombatStarted -= HandleCombatStarted;
                _combatService.OnCombatEnded -= HandleCombatEnded;
            }
            
            if (_webSocketHandler != null)
            {
                _webSocketHandler.OnCombatEventReceived -= HandleCombatEvent;
                _webSocketHandler.OnCombatStateUpdated -= HandleStateUpdate;
                _webSocketHandler.OnAvailableActionsUpdated -= HandleActionsUpdated;
                _webSocketHandler.OnStatusEffectApplied -= HandleStatusEffectApplied;
                _webSocketHandler.OnStatusEffectRemoved -= HandleStatusEffectRemoved;
            }
        }
        
        /// <summary>
        /// Initialize combat UI with a combat state
        /// </summary>
        public void InitializeCombat(string combatId, CombatState initialState = null)
        {
            _currentCombatId = combatId;
            _currentState = initialState;
            
            // Show combat panel
            if (combatPanel != null)
            {
                combatPanel.SetActive(true);
            }
            
            // Join WebSocket room for real-time updates
            _webSocketHandler?.JoinCombat(combatId);
            
            // Initialize UI
            if (initialState != null)
            {
                UpdateCombatUI(initialState);
            }
            
            // Load initial data if not provided
            if (initialState == null)
            {
                LoadCombatState();
            }
        }
        
        /// <summary>
        /// Close combat UI and clean up
        /// </summary>
        public void CloseCombat()
        {
            // Leave WebSocket room
            if (!string.IsNullOrEmpty(_currentCombatId))
            {
                _webSocketHandler?.LeaveCombat(_currentCombatId);
            }
            
            // Hide combat panel
            if (combatPanel != null)
            {
                combatPanel.SetActive(false);
            }
            
            // Clear state
            _currentCombatId = null;
            _currentState = null;
            _combatantUIs.Clear();
            _availableActions.Clear();
            _selectedTargetId = null;
            
            OnCombatExited?.Invoke();
        }
        
        /// <summary>
        /// Execute a combat action
        /// </summary>
        public async void ExecuteAction(CombatAction action, string targetId = null)
        {
            if (string.IsNullOrEmpty(_currentCombatId))
            {
                Debug.LogError("No active combat to execute action in");
                return;
            }
            
            try
            {
                // Disable action buttons during execution
                SetActionsEnabled(false);
                
                // Send action via WebSocket for immediate feedback
                _webSocketHandler?.SendCombatAction(_currentCombatId, "player", action, targetId);
                
                // Also send via HTTP for reliability
                var result = await _combatService.SubmitActionAsync(_currentCombatId, "player", action, targetId);
                
                // Log the action result
                AddCombatLogEntry($"Action: {action.Name} - {result.Message}");
                
                OnActionSelected?.Invoke(action, targetId);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to execute combat action: {ex.Message}");
                AddCombatLogEntry($"Action failed: {ex.Message}");
            }
            finally
            {
                // Re-enable actions
                SetActionsEnabled(true);
            }
        }
        
        /// <summary>
        /// End the current turn
        /// </summary>
        public void EndTurn()
        {
            if (string.IsNullOrEmpty(_currentCombatId))
            {
                return;
            }
            
            // Create an end turn action
            var endTurnAction = new CombatAction
            {
                Name = "End Turn",
                Type = ActionType.Wait,
                Description = "End current turn"
            };
            
            ExecuteAction(endTurnAction);
            OnTurnEnded?.Invoke();
        }
        
        private async void LoadCombatState()
        {
            if (string.IsNullOrEmpty(_currentCombatId))
            {
                return;
            }
            
            try
            {
                var state = await _combatService.GetCombatStateAsync(_currentCombatId);
                UpdateCombatUI(state);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to load combat state: {ex.Message}");
            }
        }
        
        private void UpdateCombatUI(CombatState state)
        {
            _currentState = state;
            
            // Update turn and round display
            if (currentTurnText != null)
            {
                currentTurnText.text = $"Turn: {state.CurrentTurn}";
            }
            
            if (roundText != null)
            {
                roundText.text = $"Round: {state.Round}";
            }
            
            // Update participants
            UpdateParticipantsUI(state.Participants);
            
            // Update recent events
            foreach (var combatEvent in state.RecentEvents)
            {
                AddCombatLogEntry(combatEvent.Message);
            }
        }
        
        private void UpdateParticipantsUI(List<Combatant> participants)
        {
            if (participantsContainer == null || combatantUIPrefab == null)
            {
                return;
            }
            
            // Clear existing UI elements
            foreach (var ui in _combatantUIs.Values)
            {
                if (ui != null)
                {
                    Destroy(ui);
                }
            }
            _combatantUIs.Clear();
            
            // Create UI for each participant
            foreach (var participant in participants)
            {
                var uiObject = Instantiate(combatantUIPrefab, participantsContainer);
                var combatantUI = uiObject.GetComponent<CombatantUI>();
                
                if (combatantUI != null)
                {
                    combatantUI.Initialize(participant);
                    combatantUI.OnTargetSelected += HandleTargetSelected;
                }
                
                _combatantUIs[participant.Name] = uiObject;
            }
        }
        
        private void UpdateActionsUI(List<CombatAction> actions)
        {
            if (actionsContainer == null || actionButtonPrefab == null)
            {
                return;
            }
            
            // Clear existing action buttons
            foreach (Transform child in actionsContainer)
            {
                Destroy(child.gameObject);
            }
            
            _availableActions = actions;
            
            // Create buttons for each action
            foreach (var action in actions)
            {
                var buttonObject = Instantiate(actionButtonPrefab, actionsContainer);
                var button = buttonObject.GetComponent<Button>();
                var text = buttonObject.GetComponentInChildren<TextMeshProUGUI>();
                
                if (button != null && text != null)
                {
                    text.text = action.Name;
                    button.onClick.AddListener(() => SelectAction(action));
                }
            }
        }
        
        private void SelectAction(CombatAction action)
        {
            // If action requires a target, wait for target selection
            if (action.Range > 0 && action.Type == ActionType.Attack)
            {
                // Highlight targetable combatants
                HighlightTargets(true);
                
                // Store selected action for when target is chosen
                _selectedAction = action;
            }
            else
            {
                // Execute immediately for non-targeted actions
                ExecuteAction(action);
            }
        }
        
        private CombatAction _selectedAction;
        
        private void HandleTargetSelected(string targetId)
        {
            _selectedTargetId = targetId;
            
            if (_selectedAction != null)
            {
                ExecuteAction(_selectedAction, targetId);
                _selectedAction = null;
                HighlightTargets(false);
            }
        }
        
        private void HighlightTargets(bool highlight)
        {
            foreach (var ui in _combatantUIs.Values)
            {
                var combatantUI = ui.GetComponent<CombatantUI>();
                combatantUI?.SetTargetable(highlight);
            }
        }
        
        private void SetActionsEnabled(bool enabled)
        {
            if (actionsContainer != null)
            {
                foreach (Transform child in actionsContainer)
                {
                    var button = child.GetComponent<Button>();
                    if (button != null)
                    {
                        button.interactable = enabled;
                    }
                }
            }
            
            if (endTurnButton != null)
            {
                endTurnButton.interactable = enabled;
            }
        }
        
        private void AddCombatLogEntry(string message)
        {
            if (combatLogContent == null || combatLogEntryPrefab == null)
            {
                return;
            }
            
            // Create log entry
            var entryObject = Instantiate(combatLogEntryPrefab, combatLogContent);
            var text = entryObject.GetComponentInChildren<TextMeshProUGUI>();
            
            if (text != null)
            {
                text.text = $"[{DateTime.Now:HH:mm:ss}] {message}";
            }
            
            // Limit number of log entries
            if (combatLogContent.childCount > maxLogEntries)
            {
                Destroy(combatLogContent.GetChild(0).gameObject);
            }
            
            // Scroll to bottom
            Canvas.ForceUpdateCanvases();
            combatLogScrollRect.verticalNormalizedPosition = 0f;
        }
        
        // Event handlers
        private void HandleCombatStarted(string combatId)
        {
            if (combatId == _currentCombatId)
            {
                AddCombatLogEntry("Combat started!");
            }
        }
        
        private void HandleCombatEnded(string combatId)
        {
            if (combatId == _currentCombatId)
            {
                AddCombatLogEntry("Combat ended!");
                CloseCombat();
            }
        }
        
        private void HandleCombatEvent(CombatEvent combatEvent)
        {
            AddCombatLogEntry(combatEvent.Message);
        }
        
        private void HandleStateUpdate(CombatState state)
        {
            if (state.CombatId == _currentCombatId)
            {
                UpdateCombatUI(state);
            }
        }
        
        private void HandleActionsUpdated(string combatantId, List<CombatAction> actions)
        {
            // Update actions if this is for the player
            if (combatantId == "player")
            {
                UpdateActionsUI(actions);
            }
        }
        
        private void HandleStatusEffectApplied(string targetId, StatusEffect effect)
        {
            AddCombatLogEntry($"{targetId} gained {effect.Name}");
            
            // Update combatant UI if it exists
            if (_combatantUIs.TryGetValue(targetId, out var ui))
            {
                var combatantUI = ui.GetComponent<CombatantUI>();
                combatantUI?.AddStatusEffect(effect);
            }
        }
        
        private void HandleStatusEffectRemoved(string targetId, StatusEffect effect)
        {
            AddCombatLogEntry($"{targetId} lost {effect.Name}");
            
            // Update combatant UI if it exists
            if (_combatantUIs.TryGetValue(targetId, out var ui))
            {
                var combatantUI = ui.GetComponent<CombatantUI>();
                combatantUI?.RemoveStatusEffect(effect);
            }
        }
    }
} 