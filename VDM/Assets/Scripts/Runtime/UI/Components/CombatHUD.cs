using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.UI.Core;
using VDM.Systems.Combat.Models;
using VDM.Systems.Character.Models;
using VDM.Systems.Combat.Services;
using System.Collections.Generic;
using System.Linq;
using VDM.DTOs.Game.Character;

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
        private List<AttackOption> attackOptions = new List<AttackOption>();
        private List<SpellOption> spellOptions = new List<SpellOption>();
        private List<ItemOption> itemOptions = new List<ItemOption>();
        private List<TargetButton> targetButtons = new List<TargetButton>();
        private List<EnemyDisplay> enemyDisplays = new List<EnemyDisplay>();
        private List<CombatLogEntry> combatLogEntries = new List<CombatLogEntry>();
        
        private VDM.DTOs.Combat.CombatActionDTO pendingAction;
        private bool isSelectingTarget = false;
        
        protected override void Awake()
        {
            base.Awake();
            combatService = FindObjectOfType<CombatService>();
            
            // Setup action buttons
            if (attackButton != null)
                attackButton.onClick.AddListener(() => ShowActionPanel(ActionType.Attack));
            if (defendButton != null)
                defendButton.onClick.AddListener(OnDefendAction);
            if (castSpellButton != null)
                castSpellButton.onClick.AddListener(() => ShowActionPanel(ActionType.CastSpell));
            if (useItemButton != null)
                useItemButton.onClick.AddListener(() => ShowActionPanel(ActionType.UseItem));
            if (moveButton != null)
                moveButton.onClick.AddListener(() => ShowActionPanel(ActionType.Move));
            if (endTurnButton != null)
                endTurnButton.onClick.AddListener(OnEndTurn);
            if (cancelTargetingButton != null)
                cancelTargetingButton.onClick.AddListener(CancelTargeting);
        }
        
        private void OnEnable()
        {
            // Subscribe to combat events when panel becomes active
            if (combatService != null)
            {
                combatService.OnCombatStarted += OnCombatStarted;
                combatService.OnCombatEnded += OnCombatEnded;
                combatService.OnTurnChanged += OnTurnChanged;
                combatService.OnActionExecuted += OnActionExecuted;
            }
        }
        
        private void OnDisable()
        {
            // Unsubscribe from combat events when panel becomes inactive
            if (combatService != null)
            {
                combatService.OnCombatStarted -= OnCombatStarted;
                combatService.OnCombatEnded -= OnCombatEnded;
                combatService.OnTurnChanged -= OnTurnChanged;
                combatService.OnActionExecuted -= OnActionExecuted;
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
            
            AddCombatLogEntry(new CombatLogData(CombatLogType.SystemMessage, "Combat begins!"));
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
                GameObject enemyDisplayObj = Instantiate(enemyDisplayPrefab, enemiesParent);
                EnemyDisplay enemyComponent = enemyDisplayObj.GetComponent<EnemyDisplay>();
                
                if (enemyComponent != null)
                {
                    enemyComponent.Initialize(enemy, OnEnemySelected);
                    enemyDisplays.Add(enemyComponent);
                }
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
        private void ShowActionPanel(ActionType actionType)
        {
            HideAllActionPanels();
            
            switch (actionType)
            {
                case ActionType.Attack:
                    if (attackPanel != null) attackPanel.SetActive(true);
                    PopulateAttackOptions();
                    break;
                case ActionType.CastSpell:
                    if (spellPanel != null) spellPanel.SetActive(true);
                    PopulateSpellOptions();
                    break;
                case ActionType.UseItem:
                    if (itemPanel != null) itemPanel.SetActive(true);
                    PopulateItemOptions();
                    break;
                case ActionType.Move:
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
                GameObject optionObj = Instantiate(attackOptionPrefab, attackOptionsParent);
                AttackOption optionComponent = optionObj.GetComponent<AttackOption>();
                
                if (optionComponent != null)
                {
                    optionComponent.Initialize(weapon, () => OnAttackSelected(weapon));
                    attackOptions.Add(optionComponent);
                }
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
                GameObject optionObj = Instantiate(spellOptionPrefab, spellOptionsParent);
                SpellOption optionComponent = optionObj.GetComponent<SpellOption>();
                
                if (optionComponent != null)
                {
                    optionComponent.Initialize(spell, () => OnSpellSelected(spell), playerCharacter.CombatStats.CurrentMana);
                    spellOptions.Add(optionComponent);
                }
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
                GameObject optionObj = Instantiate(itemOptionPrefab, itemOptionsParent);
                ItemOption optionComponent = optionObj.GetComponent<ItemOption>();
                
                if (optionComponent != null)
                {
                    optionComponent.Initialize(item, () => OnItemSelected(item));
                    itemOptions.Add(optionComponent);
                }
            }
        }
        
        /// <summary>
        /// Show target selection for an action
        /// </summary>
        private void ShowTargetSelection(VDM.DTOs.Combat.CombatActionDTO action)
        {
            pendingAction = action;
            isSelectingTarget = true;
            
            if (targetSelectionPanel != null)
                targetSelectionPanel.SetActive(true);
            
            ClearTargetButtons();
            
            var validTargets = GetValidTargets(action);
            
            foreach (var target in validTargets)
            {
                GameObject targetButtonObj = Instantiate(targetButtonPrefab, targetsParent);
                TargetButton targetButtonComponent = targetButtonObj.GetComponent<TargetButton>();
                
                if (targetButtonComponent != null)
                {
                    targetButtonComponent.Initialize(target, () => OnTargetSelected(target));
                    targetButtons.Add(targetButtonComponent);
                }
            }
        }
        
        /// <summary>
        /// Get valid targets for an action
        /// </summary>
        private List<CombatCharacter> GetValidTargets(VDM.DTOs.Combat.CombatActionDTO action)
        {
            var targets = new List<CombatCharacter>();
            
            if (currentEncounter == null) return targets;
            
            // For attacks, target enemies
            if (action.Type == ActionType.Attack)
            {
                targets.AddRange(currentEncounter.Participants.Where(p => p.IsAlive && !p.IsPlayerCharacter));
            }
            // For spells, depends on spell type (simplified logic)
            else if (action.Type == ActionType.CastSpell)
            {
                if (action.Name.ToLower().Contains("heal") || action.Name.ToLower().Contains("buff"))
                {
                    // Healing/buff spells target allies
                    targets.AddRange(currentEncounter.Participants.Where(p => p.IsAlive && p.IsAlly));
                }
                else
                {
                    // Damage spells target enemies
                    targets.AddRange(currentEncounter.Participants.Where(p => p.IsAlive && !p.IsPlayerCharacter));
                }
            }
            // For items, usually target self or allies
            else if (action.Type == ActionType.UseItem)
            {
                targets.AddRange(currentEncounter.Participants.Where(p => p.IsAlive && p.IsAlly));
            }
            
            return targets;
        }
        
        /// <summary>
        /// Add entry to combat log
        /// </summary>
        private void AddCombatLogEntry(CombatLogData logData)
        {
            if (combatLogContent == null || combatLogEntryPrefab == null) return;
            
            // Remove old entries if we have too many
            while (combatLogEntries.Count >= maxLogEntries)
            {
                var oldEntry = combatLogEntries[0];
                combatLogEntries.RemoveAt(0);
                if (oldEntry != null)
                    oldEntry.FadeOut();
            }
            
            // Create new log entry
            GameObject entryObj = Instantiate(combatLogEntryPrefab, combatLogContent);
            CombatLogEntry entryComponent = entryObj.GetComponent<CombatLogEntry>();
            
            if (entryComponent != null)
            {
                entryComponent.Initialize(logData);
                combatLogEntries.Add(entryComponent);
            }
            
            // Auto-scroll to bottom
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
                Destroy(child.gameObject);
            }
            
            // Add current status effects
            foreach (var effect in playerCharacter.StatusEffects)
            {
                // Create simple status effect icon/text
                GameObject effectObj = new GameObject($"StatusEffect_{effect.Name}");
                effectObj.transform.SetParent(playerStatusEffectsParent);
                
                var effectText = effectObj.AddComponent<TextMeshProUGUI>();
                effectText.text = effect.Name;
                effectText.fontSize = 12;
                effectText.color = effect.IsBuff ? Color.green : Color.red;
            }
        }
        
        #region Clear Methods
        
        private void ClearAttackOptions()
        {
            foreach (var option in attackOptions)
            {
                if (option != null && option.gameObject != null) 
                    DestroyImmediate(option.gameObject);
            }
            attackOptions.Clear();
        }
        
        private void ClearSpellOptions()
        {
            foreach (var option in spellOptions)
            {
                if (option != null && option.gameObject != null) 
                    DestroyImmediate(option.gameObject);
            }
            spellOptions.Clear();
        }
        
        private void ClearItemOptions()
        {
            foreach (var option in itemOptions)
            {
                if (option != null && option.gameObject != null) 
                    DestroyImmediate(option.gameObject);
            }
            itemOptions.Clear();
        }
        
        private void ClearTargetButtons()
        {
            foreach (var button in targetButtons)
            {
                if (button != null && button.gameObject != null) 
                    DestroyImmediate(button.gameObject);
            }
            targetButtons.Clear();
        }
        
        private void ClearEnemyDisplays()
        {
            foreach (var display in enemyDisplays)
            {
                if (display != null && display.gameObject != null) 
                    DestroyImmediate(display.gameObject);
            }
            enemyDisplays.Clear();
        }
        
        private void ClearCombatLog()
        {
            foreach (var entry in combatLogEntries)
            {
                if (entry != null && entry.gameObject != null) 
                    DestroyImmediate(entry.gameObject);
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
            var logType = result.Victory ? CombatLogType.SystemMessage : CombatLogType.Critical;
            AddCombatLogEntry(new CombatLogData(logType, message));
            
            // Hide combat HUD after a delay
            Invoke(nameof(Close), 3f);
        }
        
        private void OnTurnChanged(CombatCharacter character)
        {
            UpdateTurnOrder();
            UpdateActionButtons();
            AddCombatLogEntry(new CombatLogData(CombatLogType.TurnStart, $"{character.Name}'s turn begins."));
        }
        
        private void OnActionExecuted(VDM.DTOs.Combat.CombatActionDTO action, CombatResult result)
        {
            string message = $"{action.Actor.Name} uses {action.ActionName}";
            if (action.Target != null)
                message += $" on {action.Target.Name}";
            
            AddCombatLogEntry(new CombatLogData(CombatLogType.CombatAction, message));
            
            UpdatePlayerDisplay();
            UpdateEnemyDisplays();
        }
        
        private void OnCharacterDamaged(CombatCharacter character, int damage)
        {
            var logData = new CombatLogData(CombatLogType.Damage, $"{character.Name} takes {damage} damage!")
            {
                TargetName = character.Name,
                DamageAmount = damage
            };
            AddCombatLogEntry(logData);
        }
        
        private void OnCharacterHealed(CombatCharacter character, int healing)
        {
            var logData = new CombatLogData(CombatLogType.Healing, $"{character.Name} recovers {healing} health!")
            {
                TargetName = character.Name,
                HealingAmount = healing
            };
            AddCombatLogEntry(logData);
        }
        
        private void OnAttackSelected(WeaponModel weapon)
        {
            var action = new VDM.DTOs.Combat.CombatActionDTO
            {
                Type = ActionType.Attack,
                Name = weapon.Name,
                Description = $"Attack with {weapon.Name}",
                Damage = weapon.Damage,
                Range = weapon.Range
            };
            
            ShowTargetSelection(action);
        }
        
        private void OnSpellSelected(SpellModel spell)
        {
            var action = new VDM.DTOs.Combat.CombatActionDTO
            {
                Type = ActionType.CastSpell,
                Name = spell.Name,
                Description = spell.Description,
                ManaCost = spell.ManaCost,
                Range = spell.Range
            };
            
            ShowTargetSelection(action);
        }
        
        private void OnItemSelected(ItemModel item)
        {
            var action = new VDM.DTOs.Combat.CombatActionDTO
            {
                Type = ActionType.UseItem,
                Name = item.Name,
                Description = $"Use {item.Name}"
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
            // Show enemy details or handle selection for targeting
            Debug.Log($"Enemy selected: {enemy.Name}");
        }
        
        private void OnDefendAction()
        {
            var action = new VDM.DTOs.Combat.CombatActionDTO
            {
                Type = ActionType.Defend,
                Name = "Defend",
                Description = "Defensive stance"
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