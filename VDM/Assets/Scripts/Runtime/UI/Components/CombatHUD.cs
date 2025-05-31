using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.UI.Core;
using VDM.Systems.Combat.Models;
using VDM.Systems.Character.Models;
using VDM.Systems.Combat.Services;
using System.Collections.Generic;
using System.Linq;

namespace VDM.UI.Systems.Combat
{
    /// <summary>
    /// UI component for combat interface and action management during battles
    /// </summary>
    public class CombatHUD : BaseUIPanel
    {
        [Header("Combat Status")]
        [SerializeField] private TextMeshProUGUI turnOrderText;
        [SerializeField] private TextMeshProUGUI currentTurnText;
        [SerializeField] private TextMeshProUGUI roundCountText;
        [SerializeField] private Image initiativeIndicator;
        
        [Header("Player Character")]
        [SerializeField] private Image playerPortrait;
        [SerializeField] private TextMeshProUGUI playerNameText;
        [SerializeField] private Slider playerHealthSlider;
        [SerializeField] private TextMeshProUGUI playerHealthText;
        [SerializeField] private Slider playerManaSlider;
        [SerializeField] private TextMeshProUGUI playerManaText;
        [SerializeField] private Transform playerStatusEffectsParent;
        
        [Header("Action Buttons")]
        [SerializeField] private Button attackButton;
        [SerializeField] private Button defendButton;
        [SerializeField] private Button castSpellButton;
        [SerializeField] private Button useItemButton;
        [SerializeField] private Button moveButton;
        [SerializeField] private Button endTurnButton;
        
        [Header("Action Panels")]
        [SerializeField] private GameObject attackPanel;
        [SerializeField] private GameObject spellPanel;
        [SerializeField] private GameObject itemPanel;
        [SerializeField] private GameObject movePanel;
        
        [Header("Attack Options")]
        [SerializeField] private Transform attackOptionsParent;
        [SerializeField] private GameObject attackOptionPrefab;
        
        [Header("Spell Options")]
        [SerializeField] private Transform spellOptionsParent;
        [SerializeField] private GameObject spellOptionPrefab;
        [SerializeField] private ScrollRect spellScrollRect;
        
        [Header("Item Options")]
        [SerializeField] private Transform itemOptionsParent;
        [SerializeField] private GameObject itemOptionPrefab;
        [SerializeField] private ScrollRect itemScrollRect;
        
        [Header("Target Selection")]
        [SerializeField] private GameObject targetSelectionPanel;
        [SerializeField] private Transform targetsParent;
        [SerializeField] private GameObject targetButtonPrefab;
        [SerializeField] private Button cancelTargetingButton;
        
        [Header("Combat Log")]
        [SerializeField] private ScrollRect combatLogScrollRect;
        [SerializeField] private Transform combatLogContent;
        [SerializeField] private GameObject combatLogEntryPrefab;
        [SerializeField] private int maxLogEntries = 50;
        
        [Header("Enemy Display")]
        [SerializeField] private Transform enemiesParent;
        [SerializeField] private GameObject enemyDisplayPrefab;
        
        private CombatService combatService;
        private CombatEncounter currentEncounter;
        private CharacterModel playerCharacter;
        private List<GameObject> attackOptions = new List<GameObject>();
        private List<GameObject> spellOptions = new List<GameObject>();
        private List<GameObject> itemOptions = new List<GameObject>();
        private List<GameObject> targetButtons = new List<GameObject>();
        private List<GameObject> enemyDisplays = new List<GameObject>();
        private List<GameObject> combatLogEntries = new List<GameObject>();
        
        private VDM.DTOs.Combat.CombatActionDTO pendingAction;
        private bool isSelectingTarget = false;
        
        protected override void Awake()
        {
            base.Awake();
            combatService = FindObjectOfType<CombatService>();
            
            // Setup action buttons
            if (attackButton != null)
                attackButton.onClick.AddListener(() => ShowActionPanel(VDM.DTOs.Combat.CombatActionDTOType.Attack));
            if (defendButton != null)
                defendButton.onClick.AddListener(OnDefendAction);
            if (castSpellButton != null)
                castSpellButton.onClick.AddListener(() => ShowActionPanel(VDM.DTOs.Combat.CombatActionDTOType.CastSpell));
            if (useItemButton != null)
                useItemButton.onClick.AddListener(() => ShowActionPanel(VDM.DTOs.Combat.CombatActionDTOType.UseItem));
            if (moveButton != null)
                moveButton.onClick.AddListener(() => ShowActionPanel(VDM.DTOs.Combat.CombatActionDTOType.Move));
            if (endTurnButton != null)
                endTurnButton.onClick.AddListener(OnEndTurn);
            if (cancelTargetingButton != null)
                cancelTargetingButton.onClick.AddListener(CancelTargeting);
        }
        
        protected override void OnEnable()
        {
            base.OnEnable();
            if (combatService != null)
            {
                combatService.OnCombatStarted += OnCombatStarted;
                combatService.OnCombatEnded += OnCombatEnded;
                combatService.OnTurnChanged += OnTurnChanged;
                combatService.OnActionExecuted += OnActionExecuted;
                combatService.OnCharacterDamaged += OnCharacterDamaged;
                combatService.OnCharacterHealed += OnCharacterHealed;
            }
        }
        
        protected override void OnDisable()
        {
            base.OnDisable();
            if (combatService != null)
            {
                combatService.OnCombatStarted -= OnCombatStarted;
                combatService.OnCombatEnded -= OnCombatEnded;
                combatService.OnTurnChanged -= OnTurnChanged;
                combatService.OnActionExecuted -= OnActionExecuted;
                combatService.OnCharacterDamaged -= OnCharacterDamaged;
                combatService.OnCharacterHealed -= OnCharacterHealed;
            }
        }
        
        /// <summary>
        /// Initialize combat HUD for a new encounter
        /// </summary>
        public void InitializeCombat(CombatEncounter encounter, CharacterModel player)
        {
            currentEncounter = encounter;
            playerCharacter = player;
            
            UpdatePlayerDisplay();
            UpdateEnemyDisplays();
            UpdateTurnOrder();
            UpdateActionButtons();
            ClearCombatLog();
            HideAllActionPanels();
            
            AddCombatLogEntry("Combat begins!", Color.yellow);
        }
        
        /// <summary>
        /// Update player character display
        /// </summary>
        private void UpdatePlayerDisplay()
        {
            if (playerCharacter == null) return;
            
            if (playerNameText != null)
                playerNameText.text = playerCharacter.Name;
            
            if (playerHealthSlider != null)
                playerHealthSlider.value = (float)playerCharacter.CombatStats.CurrentHealth / playerCharacter.CombatStats.MaxHealth;
            if (playerHealthText != null)
                playerHealthText.text = $"{playerCharacter.CombatStats.CurrentHealth}/{playerCharacter.CombatStats.MaxHealth}";
            
            if (playerManaSlider != null)
                playerManaSlider.value = (float)playerCharacter.CombatStats.CurrentMana / playerCharacter.CombatStats.MaxMana;
            if (playerManaText != null)
                playerManaText.text = $"{playerCharacter.CombatStats.CurrentMana}/{playerCharacter.CombatStats.MaxMana}";
            
            // Update portrait
            if (playerPortrait != null && !string.IsNullOrEmpty(playerCharacter.PortraitPath))
            {
                Sprite portrait = Resources.Load<Sprite>(playerCharacter.PortraitPath);
                if (portrait != null)
                    playerPortrait.sprite = portrait;
            }
            
            // Update status effects
            UpdatePlayerStatusEffects();
        }
        
        /// <summary>
        /// Update enemy displays
        /// </summary>
        private void UpdateEnemyDisplays()
        {
            ClearEnemyDisplays();
            
            if (currentEncounter?.Enemies == null || enemiesParent == null || enemyDisplayPrefab == null)
                return;
            
            foreach (var enemy in currentEncounter.Enemies.Where(e => e.IsAlive))
            {
                GameObject enemyDisplay = Instantiate(enemyDisplayPrefab, enemiesParent);
                EnemyDisplay enemyComponent = enemyDisplay.GetComponent<EnemyDisplay>();
                
                if (enemyComponent != null)
                {
                    enemyComponent.Initialize(enemy, OnEnemySelected);
                }
                
                enemyDisplays.Add(enemyDisplay);
            }
        }
        
        /// <summary>
        /// Update turn order display
        /// </summary>
        private void UpdateTurnOrder()
        {
            if (currentEncounter == null) return;
            
            if (turnOrderText != null)
            {
                var turnOrder = currentEncounter.TurnOrder.Take(5); // Show next 5 turns
                turnOrderText.text = "Turn Order: " + string.Join(" → ", turnOrder.Select(c => c.Name));
            }
            
            if (currentTurnText != null)
            {
                var currentCharacter = currentEncounter.CurrentTurn;
                currentTurnText.text = $"Current Turn: {currentCharacter?.Name ?? "None"}";
            }
            
            if (roundCountText != null)
                roundCountText.text = $"Round: {currentEncounter.RoundCount}";
        }
        
        /// <summary>
        /// Update action button availability
        /// </summary>
        private void UpdateActionButtons()
        {
            bool isPlayerTurn = currentEncounter?.IsPlayerTurn ?? false;
            bool hasActionsRemaining = playerCharacter?.CombatStats.ActionsRemaining > 0;
            
            if (attackButton != null)
                attackButton.interactable = isPlayerTurn && hasActionsRemaining;
            if (defendButton != null)
                defendButton.interactable = isPlayerTurn && hasActionsRemaining;
            if (castSpellButton != null)
                castSpellButton.interactable = isPlayerTurn && hasActionsRemaining && playerCharacter.CombatStats.CurrentMana > 0;
            if (useItemButton != null)
                useItemButton.interactable = isPlayerTurn && hasActionsRemaining;
            if (moveButton != null)
                moveButton.interactable = isPlayerTurn && hasActionsRemaining;
            if (endTurnButton != null)
                endTurnButton.interactable = isPlayerTurn;
        }
        
        /// <summary>
        /// Show specific action panel
        /// </summary>
        private void ShowActionPanel(VDM.DTOs.Combat.CombatActionDTOType actionType)
        {
            HideAllActionPanels();
            
            switch (actionType)
            {
                case VDM.DTOs.Combat.CombatActionDTOType.Attack:
                    if (attackPanel != null) attackPanel.SetActive(true);
                    PopulateAttackOptions();
                    break;
                case VDM.DTOs.Combat.CombatActionDTOType.CastSpell:
                    if (spellPanel != null) spellPanel.SetActive(true);
                    PopulateSpellOptions();
                    break;
                case VDM.DTOs.Combat.CombatActionDTOType.UseItem:
                    if (itemPanel != null) itemPanel.SetActive(true);
                    PopulateItemOptions();
                    break;
                case VDM.DTOs.Combat.CombatActionDTOType.Move:
                    if (movePanel != null) movePanel.SetActive(true);
                    // Handle movement options
                    break;
            }
        }
        
        /// <summary>
        /// Hide all action panels
        /// </summary>
        private void HideAllActionPanels()
        {
            if (attackPanel != null) attackPanel.SetActive(false);
            if (spellPanel != null) spellPanel.SetActive(false);
            if (itemPanel != null) itemPanel.SetActive(false);
            if (movePanel != null) movePanel.SetActive(false);
            if (targetSelectionPanel != null) targetSelectionPanel.SetActive(false);
        }
        
        /// <summary>
        /// Populate attack options
        /// </summary>
        private void PopulateAttackOptions()
        {
            ClearAttackOptions();
            
            if (playerCharacter?.Equipment?.EquippedWeapons == null || attackOptionsParent == null || attackOptionPrefab == null)
                return;
            
            foreach (var weapon in playerCharacter.Equipment.EquippedWeapons)
            {
                GameObject option = Instantiate(attackOptionPrefab, attackOptionsParent);
                AttackOption optionComponent = option.GetComponent<AttackOption>();
                
                if (optionComponent != null)
                {
                    optionComponent.Initialize(weapon, () => OnAttackSelected(weapon));
                }
                
                attackOptions.Add(option);
            }
        }
        
        /// <summary>
        /// Populate spell options
        /// </summary>
        private void PopulateSpellOptions()
        {
            ClearSpellOptions();
            
            if (playerCharacter?.Spells == null || spellOptionsParent == null || spellOptionPrefab == null)
                return;
            
            var availableSpells = playerCharacter.Spells.Where(s => s.ManaCost <= playerCharacter.CombatStats.CurrentMana);
            
            foreach (var spell in availableSpells)
            {
                GameObject option = Instantiate(spellOptionPrefab, spellOptionsParent);
                SpellOption optionComponent = option.GetComponent<SpellOption>();
                
                if (optionComponent != null)
                {
                    optionComponent.Initialize(spell, () => OnSpellSelected(spell));
                }
                
                spellOptions.Add(option);
            }
        }
        
        /// <summary>
        /// Populate item options
        /// </summary>
        private void PopulateItemOptions()
        {
            ClearItemOptions();
            
            if (playerCharacter?.Inventory?.UsableItems == null || itemOptionsParent == null || itemOptionPrefab == null)
                return;
            
            foreach (var item in playerCharacter.Inventory.UsableItems.Where(i => i.Quantity > 0))
            {
                GameObject option = Instantiate(itemOptionPrefab, itemOptionsParent);
                ItemOption optionComponent = option.GetComponent<ItemOption>();
                
                if (optionComponent != null)
                {
                    optionComponent.Initialize(item, () => OnItemSelected(item));
                }
                
                itemOptions.Add(option);
            }
        }
        
        /// <summary>
        /// Show target selection for an action
        /// </summary>
        private void ShowTargetSelection(VDM.DTOs.Combat.CombatActionDTO action)
        {
            pendingAction = action;
            isSelectingTarget = true;
            
            ClearTargetButtons();
            
            if (targetSelectionPanel != null)
                targetSelectionPanel.SetActive(true);
            
            // Add valid targets based on action type
            var validTargets = GetValidTargets(action);
            
            foreach (var target in validTargets)
            {
                GameObject targetButton = Instantiate(targetButtonPrefab, targetsParent);
                TargetButton buttonComponent = targetButton.GetComponent<TargetButton>();
                
                if (buttonComponent != null)
                {
                    buttonComponent.Initialize(target, () => OnTargetSelected(target));
                }
                
                targetButtons.Add(targetButton);
            }
        }
        
        /// <summary>
        /// Get valid targets for an action
        /// </summary>
        private List<CombatCharacter> GetValidTargets(VDM.DTOs.Combat.CombatActionDTO action)
        {
            var targets = new List<CombatCharacter>();
            
            switch (action.TargetType)
            {
                case TargetType.Enemy:
                    targets.AddRange(currentEncounter.Enemies.Where(e => e.IsAlive));
                    break;
                case TargetType.Ally:
                    targets.Add(playerCharacter);
                    // Add party members if applicable
                    break;
                case TargetType.Self:
                    targets.Add(playerCharacter);
                    break;
                case TargetType.Any:
                    targets.AddRange(currentEncounter.Enemies.Where(e => e.IsAlive));
                    targets.Add(playerCharacter);
                    break;
            }
            
            return targets;
        }
        
        /// <summary>
        /// Add entry to combat log
        /// </summary>
        private void AddCombatLogEntry(string message, Color color)
        {
            if (combatLogContent == null || combatLogEntryPrefab == null) return;
            
            GameObject logEntry = Instantiate(combatLogEntryPrefab, combatLogContent);
            TextMeshProUGUI logText = logEntry.GetComponent<TextMeshProUGUI>();
            
            if (logText != null)
            {
                logText.text = $"[{System.DateTime.Now:HH:mm:ss}] {message}";
                logText.color = color;
            }
            
            combatLogEntries.Add(logEntry);
            
            // Remove old entries if we exceed the limit
            while (combatLogEntries.Count > maxLogEntries)
            {
                GameObject oldEntry = combatLogEntries[0];
                combatLogEntries.RemoveAt(0);
                if (oldEntry != null)
                    DestroyImmediate(oldEntry);
            }
            
            // Scroll to bottom
            if (combatLogScrollRect != null)
            {
                Canvas.ForceUpdateCanvases();
                combatLogScrollRect.verticalNormalizedPosition = 0f;
            }
        }
        
        /// <summary>
        /// Update player status effects display
        /// </summary>
        private void UpdatePlayerStatusEffects()
        {
            if (playerStatusEffectsParent == null || playerCharacter?.StatusEffects == null) return;
            
            // Clear existing status effect displays
            foreach (Transform child in playerStatusEffectsParent)
            {
                DestroyImmediate(child.gameObject);
            }
            
            // Add current status effects
            foreach (var effect in playerCharacter.StatusEffects)
            {
                // Create status effect icon/display
                // Implementation depends on status effect prefab structure
            }
        }
        
        #region Clear Methods
        
        private void ClearAttackOptions()
        {
            foreach (var option in attackOptions)
            {
                if (option != null) DestroyImmediate(option);
            }
            attackOptions.Clear();
        }
        
        private void ClearSpellOptions()
        {
            foreach (var option in spellOptions)
            {
                if (option != null) DestroyImmediate(option);
            }
            spellOptions.Clear();
        }
        
        private void ClearItemOptions()
        {
            foreach (var option in itemOptions)
            {
                if (option != null) DestroyImmediate(option);
            }
            itemOptions.Clear();
        }
        
        private void ClearTargetButtons()
        {
            foreach (var button in targetButtons)
            {
                if (button != null) DestroyImmediate(button);
            }
            targetButtons.Clear();
        }
        
        private void ClearEnemyDisplays()
        {
            foreach (var display in enemyDisplays)
            {
                if (display != null) DestroyImmediate(display);
            }
            enemyDisplays.Clear();
        }
        
        private void ClearCombatLog()
        {
            foreach (var entry in combatLogEntries)
            {
                if (entry != null) DestroyImmediate(entry);
            }
            combatLogEntries.Clear();
        }
        
        #endregion
        
        #region Event Handlers
        
        private void OnCombatStarted(CombatEncounter encounter)
        {
            InitializeCombat(encounter, playerCharacter);
        }
        
        private void OnCombatEnded(CombatResult result)
        {
            string message = result.Victory ? "Victory!" : "Defeat!";
            Color color = result.Victory ? Color.green : Color.red;
            AddCombatLogEntry(message, color);
            
            // Hide combat HUD after a delay
            Invoke(nameof(Close), 3f);
        }
        
        private void OnTurnChanged(CombatCharacter character)
        {
            UpdateTurnOrder();
            UpdateActionButtons();
            AddCombatLogEntry($"{character.Name}'s turn begins.", Color.cyan);
        }
        
        private void OnActionExecuted(VDM.DTOs.Combat.CombatActionDTO action, CombatResult result)
        {
            string message = $"{action.Actor.Name} uses {action.ActionName}";
            if (action.Target != null)
                message += $" on {action.Target.Name}";
            
            AddCombatLogEntry(message, Color.white);
            
            UpdatePlayerDisplay();
            UpdateEnemyDisplays();
        }
        
        private void OnCharacterDamaged(CombatCharacter character, int damage)
        {
            AddCombatLogEntry($"{character.Name} takes {damage} damage!", Color.red);
        }
        
        private void OnCharacterHealed(CombatCharacter character, int healing)
        {
            AddCombatLogEntry($"{character.Name} recovers {healing} health!", Color.green);
        }
        
        private void OnAttackSelected(WeaponModel weapon)
        {
            var action = new VDM.DTOs.Combat.CombatActionDTO
            {
                ActionType = VDM.DTOs.Combat.CombatActionDTOType.Attack,
                Actor = playerCharacter,
                Weapon = weapon,
                TargetType = TargetType.Enemy
            };
            
            ShowTargetSelection(action);
        }
        
        private void OnSpellSelected(SpellModel spell)
        {
            var action = new VDM.DTOs.Combat.CombatActionDTO
            {
                ActionType = VDM.DTOs.Combat.CombatActionDTOType.CastSpell,
                Actor = playerCharacter,
                Spell = spell,
                TargetType = spell.TargetType
            };
            
            ShowTargetSelection(action);
        }
        
        private void OnItemSelected(ItemModel item)
        {
            var action = new VDM.DTOs.Combat.CombatActionDTO
            {
                ActionType = VDM.DTOs.Combat.CombatActionDTOType.UseItem,
                Actor = playerCharacter,
                Item = item,
                TargetType = item.TargetType
            };
            
            ShowTargetSelection(action);
        }
        
        private void OnTargetSelected(CombatCharacter target)
        {
            if (pendingAction != null)
            {
                pendingAction.Target = target;
                combatService?.ExecuteAction(pendingAction);
                
                CancelTargeting();
                HideAllActionPanels();
            }
        }
        
        private void OnEnemySelected(EnemyModel enemy)
        {
            // Show enemy details or handle selection
        }
        
        private void OnDefendAction()
        {
            var action = new VDM.DTOs.Combat.CombatActionDTO
            {
                ActionType = VDM.DTOs.Combat.CombatActionDTOType.Defend,
                Actor = playerCharacter,
                Target = playerCharacter
            };
            
            combatService?.ExecuteAction(action);
            HideAllActionPanels();
        }
        
        private void OnEndTurn()
        {
            combatService?.EndTurn();
            HideAllActionPanels();
        }
        
        private void CancelTargeting()
        {
            isSelectingTarget = false;
            pendingAction = null;
            
            if (targetSelectionPanel != null)
                targetSelectionPanel.SetActive(false);
            
            ClearTargetButtons();
        }
        
        #endregion
    }
} 