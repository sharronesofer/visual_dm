using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.Systems.Npc.Models;
using VDM.Systems.Character.Models;
using VDM.Systems.Economy.Models;
using VDM.Core;
using VDM.Core.Events;

namespace VDM.Systems.NPC.UI
{
    /// <summary>
    /// Enhanced NPC Interaction UI that seamlessly integrates dialogue, bartering, and relationship management
    /// Implements Task 64 requirements for comprehensive NPC interaction interface with immediate response
    /// and enhanced user experience features
    /// </summary>
    public class NPCInteractionUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private GameObject interactionPanel;
        [SerializeField] private TextMeshProUGUI npcNameText;
        [SerializeField] private TextMeshProUGUI npcGreetingText;
        [SerializeField] private Image npcPortrait;
        [SerializeField] private Slider relationshipSlider;
        [SerializeField] private TextMeshProUGUI relationshipText;
        [SerializeField] private Image factionIcon;
        
        [Header("Interaction Buttons")]
        [SerializeField] private Button talkButton;
        [SerializeField] private Button barterButton;
        [SerializeField] private Button askAboutButton;
        [SerializeField] private Button giveGiftButton;
        [SerializeField] private Button challengeButton;
        [SerializeField] private Button closeButton;
        
        [Header("Dialogue Panel")]
        [SerializeField] private GameObject dialoguePanel;
        [SerializeField] private TextMeshProUGUI dialogueText;
        [SerializeField] private Transform dialogueOptionsParent;
        [SerializeField] private Button dialogueOptionPrefab;
        [SerializeField] private TextMeshProUGUI typingIndicator;
        [SerializeField] private ScrollRect conversationHistory;
        [SerializeField] private Transform historyContent;
        [SerializeField] private TextMeshProUGUI historyEntryPrefab;
        [SerializeField] private Button resumeConversationButton;
        
        [Header("Barter Panel")]
        [SerializeField] private GameObject barterPanel;
        [SerializeField] private Transform playerInventoryParent;
        [SerializeField] private Transform npcInventoryParent;
        [SerializeField] private Transform tradeOfferParent;
        [SerializeField] private Button confirmTradeButton;
        [SerializeField] private Button cancelTradeButton;
        [SerializeField] private TextMeshProUGUI tradeValueText;
        [SerializeField] private TextMeshProUGUI relationshipImpactText;
        [SerializeField] private TMP_InputField itemFilterInput;
        [SerializeField] private Toggle availabilityFilter;
        [SerializeField] private TextMeshProUGUI priceComparisonText;
        
        [Header("Context Panel")]
        [SerializeField] private GameObject contextPanel;
        [SerializeField] private TextMeshProUGUI contextTitle;
        [SerializeField] private TextMeshProUGUI contextDescription;
        [SerializeField] private Transform contextOptionsParent;
        [SerializeField] private Button contextOptionPrefab;
        
        [Header("Gift Panel")]
        [SerializeField] private GameObject giftPanel;
        [SerializeField] private Transform giftInventoryParent;
        [SerializeField] private Button confirmGiftButton;
        [SerializeField] private Button cancelGiftButton;
        [SerializeField] private TextMeshProUGUI giftImpactText;
        
        [Header("Challenge Panel")]
        [SerializeField] private GameObject challengePanel;
        [SerializeField] private Transform challengeOptionsParent;
        [SerializeField] private Button challengeOptionPrefab;
        
        [Header("Configuration")]
        [SerializeField] private float typingSpeed = 0.05f;
        [SerializeField] private bool enableAccessibility = true;
        [SerializeField] private bool showRelationshipChanges = true;
        [SerializeField] private bool enableOfflineMode = true;
        [SerializeField] private float responseTimeout = 10f;
        [SerializeField] private int maxConversationHistory = 50;
        
        // State
        private NPCData currentNPC;
        private CharacterRelationship currentRelationship;
        private List<DialogueOption> currentDialogueOptions = new List<DialogueOption>();
        private List<TradeItem> currentTradeOffer = new List<TradeItem>();
        private List<DialogueHistoryEntry> conversationHistoryList = new List<DialogueHistoryEntry>();
        private bool isTyping = false;
        private bool isProcessingInput = false;
        private InteractionMode currentMode = InteractionMode.Main;
        private Coroutine typingCoroutine;
        
        // Events
        public static event Action<NPCData> OnNPCInteractionStarted;
        public static event Action OnNPCInteractionEnded;
        public static event Action<string> OnDialogueOptionSelected;
        public static event Action<List<TradeItem>> OnTradeProposed;
        public static event Action<string, object> OnContextActionSelected;
        public static event Action<string, int> OnGiftGiven;
        public static event Action<string> OnChallengeInitiated;
        
        private enum InteractionMode
        {
            Main,
            Dialogue,
            Barter,
            Context,
            Gift,
            Challenge
        }
        
        private void Awake()
        {
            InitializeUI();
        }
        
        private void InitializeUI()
        {
            // Setup button listeners
            talkButton.onClick.AddListener(() => StartDialogue());
            barterButton.onClick.AddListener(() => StartBarter());
            askAboutButton.onClick.AddListener(() => ShowContextMenu());
            giveGiftButton.onClick.AddListener(() => ShowGiftMenu());
            challengeButton.onClick.AddListener(() => ShowChallengeMenu());
            closeButton.onClick.AddListener(() => CloseInteraction());
            
            confirmTradeButton.onClick.AddListener(() => ConfirmTrade());
            cancelTradeButton.onClick.AddListener(() => CancelTrade());
            
            confirmGiftButton.onClick.AddListener(() => ConfirmGift());
            cancelGiftButton.onClick.AddListener(() => CancelGift());
            
            resumeConversationButton.onClick.AddListener(() => ResumeConversation());
            
            // Setup filter listeners
            if (itemFilterInput != null)
                itemFilterInput.onValueChanged.AddListener(FilterTradeItems);
            
            if (availabilityFilter != null)
                availabilityFilter.onValueChanged.AddListener((value) => FilterTradeItems(itemFilterInput.text));
            
            // Initially hide all panels
            SetAllPanelsInactive();
        }
        
        public void StartInteraction(NPCData npc, CharacterRelationship relationship)
        {
            currentNPC = npc;
            currentRelationship = relationship;
            currentMode = InteractionMode.Main;
            
            // Show main interaction panel with immediate response
            interactionPanel.SetActive(true);
            
            // Immediate visual acknowledgment
            ShowImmediateAcknowledgment();
            
            // Update NPC information
            UpdateNPCDisplay();
            
            // Generate context-aware greeting
            GenerateContextualGreeting();
            
            // Update interaction options availability
            UpdateInteractionOptions();
            
            OnNPCInteractionStarted?.Invoke(npc);
        }
        
        private void ShowImmediateAcknowledgment()
        {
            // Immediate visual feedback before processing
            npcGreetingText.text = "...";
            
            // Flash the portrait or add visual acknowledgment
            if (npcPortrait != null)
            {
                StartCoroutine(FlashPortrait());
            }
        }
        
        private IEnumerator FlashPortrait()
        {
            Color originalColor = npcPortrait.color;
            npcPortrait.color = Color.white;
            yield return new WaitForSeconds(0.1f);
            npcPortrait.color = originalColor;
        }
        
        private void UpdateNPCDisplay()
        {
            if (currentNPC == null) return;
            
            npcNameText.text = currentNPC.name;
            
            // Update relationship display with detailed information
            if (currentRelationship != null)
            {
                relationshipSlider.value = currentRelationship.trustLevel;
                relationshipText.text = GetDetailedRelationshipDescription(currentRelationship.trustLevel);
                
                if (showRelationshipChanges)
                {
                    // Show relationship level with color coding
                    Color relationshipColor = GetRelationshipColor(currentRelationship.trustLevel);
                    relationshipText.color = relationshipColor;
                }
            }
            
            // Update faction display
            if (factionIcon != null && !string.IsNullOrEmpty(currentNPC.factionId))
            {
                // TODO: Load faction icon
                factionIcon.gameObject.SetActive(true);
            }
            
            // TODO: Load NPC portrait with fallback
            // LoadNPCPortrait(currentNPC.id);
        }
        
        private void GenerateContextualGreeting()
        {
            if (currentNPC == null) return;
            
            string greeting = GenerateEnhancedContextualGreeting();
            
            // Type the greeting with animation
            if (typingCoroutine != null)
                StopCoroutine(typingCoroutine);
            
            typingCoroutine = StartCoroutine(TypeDialogue(greeting, npcGreetingText));
        }
        
        private string GenerateEnhancedContextualGreeting()
        {
            var greetings = new List<string>();
            
            // Base greeting based on relationship
            if (currentRelationship != null)
            {
                float trust = currentRelationship.trustLevel;
                string playerName = GetPlayerName();
                
                if (trust >= 0.9f)
                {
                    greetings.Add($"My dear friend {playerName}! Always a pleasure to see you.");
                    greetings.Add($"{playerName}! You're exactly who I was hoping to see today.");
                }
                else if (trust >= 0.7f)
                {
                    greetings.Add($"Good to see you again, {playerName}.");
                    greetings.Add($"Hello there, {playerName}. How have you been?");
                }
                else if (trust >= 0.4f)
                {
                    greetings.Add("Hello there.");
                    greetings.Add("Good day to you.");
                }
                else if (trust >= 0.2f)
                {
                    greetings.Add("What do you want?");
                    greetings.Add("I suppose you need something.");
                }
                else
                {
                    greetings.Add("I don't have time for you.");
                    greetings.Add("Make it quick.");
                }
            }
            else
            {
                greetings.Add("Hello, stranger.");
                greetings.Add("Haven't seen you around here before.");
            }
            
            // Add time-based context
            var currentHour = DateTime.Now.Hour;
            string timeGreeting = "";
            if (currentHour < 6) timeGreeting = "You're up early";
            else if (currentHour < 12) timeGreeting = "Good morning";
            else if (currentHour < 18) timeGreeting = "Good afternoon";
            else if (currentHour < 22) timeGreeting = "Good evening";
            else timeGreeting = "Working late tonight";
            
            // Add faction context
            string factionContext = "";
            if (!string.IsNullOrEmpty(currentNPC.factionId))
            {
                // TODO: Get faction relationship
                // factionContext = GetFactionContextualGreeting(currentNPC.factionId);
            }
            
            // Add location context
            string locationContext = GetLocationContextualGreeting();
            
            // Combine contextual elements
            string selectedGreeting = greetings[UnityEngine.Random.Range(0, greetings.Count)];
            
            if (!string.IsNullOrEmpty(factionContext))
                selectedGreeting += " " + factionContext;
            
            if (!string.IsNullOrEmpty(locationContext))
                selectedGreeting += " " + locationContext;
            
            return selectedGreeting;
        }
        
        private string GetLocationContextualGreeting()
        {
            // TODO: Get actual location context
            var locations = new[] { 
                "Things have been quiet around here lately.",
                "Busy day at the market today.",
                "The weather's been strange lately, hasn't it?",
                "Have you heard the latest news from the capital?"
            };
            
            return locations[UnityEngine.Random.Range(0, locations.Length)];
        }
        
        private void UpdateInteractionOptions()
        {
            if (currentNPC == null) return;
            
            // Universal availability - all NPCs can talk and barter (Task 64 requirement)
            talkButton.interactable = true;
            barterButton.interactable = true;
            askAboutButton.interactable = HasContextualInformation();
            giveGiftButton.interactable = HasGiftableItems();
            challengeButton.interactable = CanChallenge();
            
            // Update button text with contextual information
            UpdateButtonText();
        }
        
        private void UpdateButtonText()
        {
            // Contextual button text based on NPC type and relationship
            if (currentRelationship?.trustLevel >= 0.7f)
            {
                talkButton.GetComponentInChildren<TextMeshProUGUI>().text = "Chat";
                barterButton.GetComponentInChildren<TextMeshProUGUI>().text = "Trade";
            }
            else if (currentRelationship?.trustLevel <= 0.3f)
            {
                talkButton.GetComponentInChildren<TextMeshProUGUI>().text = "Speak";
                barterButton.GetComponentInChildren<TextMeshProUGUI>().text = "Business";
            }
            else
            {
                talkButton.GetComponentInChildren<TextMeshProUGUI>().text = "Talk";
                barterButton.GetComponentInChildren<TextMeshProUGUI>().text = "Barter";
            }
            
            // Context-sensitive Ask About text
            askAboutButton.GetComponentInChildren<TextMeshProUGUI>().text = 
                GetContextualAskAboutText();
        }
        
        private string GetContextualAskAboutText()
        {
            // TODO: Get actual location/context
            var options = new[] { "Ask About Local News", "Ask About Rumors", "Ask About Area", "Ask About Politics" };
            return options[UnityEngine.Random.Range(0, options.Length)];
        }
        
        private void StartDialogue()
        {
            currentMode = InteractionMode.Dialogue;
            SetAllPanelsInactive();
            dialoguePanel.SetActive(true);
            
            // Show conversation history if available
            LoadConversationHistory();
            
            // Generate initial dialogue options
            GenerateDialogueOptions();
            
            // Show typing indicator while processing
            ShowTypingIndicator(true);
            
            OnDialogueOptionSelected?.Invoke("start_dialogue");
        }
        
        private void StartBarter()
        {
            currentMode = InteractionMode.Barter;
            SetAllPanelsInactive();
            barterPanel.SetActive(true);
            
            // Load inventories
            LoadNPCInventory();
            LoadPlayerInventory();
            
            // Update trade interface
            UpdateTradeInterface();
        }
        
        private void ShowContextMenu()
        {
            currentMode = InteractionMode.Context;
            SetAllPanelsInactive();
            contextPanel.SetActive(true);
            
            // Generate context-specific options
            GenerateContextOptions();
        }
        
        private void ShowGiftMenu()
        {
            currentMode = InteractionMode.Gift;
            SetAllPanelsInactive();
            giftPanel.SetActive(true);
            
            // Load giftable items
            LoadGiftableItems();
        }
        
        private void ShowChallengeMenu()
        {
            currentMode = InteractionMode.Challenge;
            SetAllPanelsInactive();
            challengePanel.SetActive(true);
            
            // Generate challenge options
            GenerateChallengeOptions();
        }
        
        private void CloseInteraction()
        {
            // Save conversation for resume functionality
            SaveConversationState();
            
            SetAllPanelsInactive();
            interactionPanel.SetActive(false);
            
            // Stop any ongoing typing animation
            if (typingCoroutine != null)
            {
                StopCoroutine(typingCoroutine);
                typingCoroutine = null;
            }
            
            OnNPCInteractionEnded?.Invoke();
        }
        
        private void SetAllPanelsInactive()
        {
            dialoguePanel.SetActive(false);
            barterPanel.SetActive(false);
            contextPanel.SetActive(false);
            giftPanel.SetActive(false);
            challengePanel.SetActive(false);
        }
        
        // Enhanced typing system with real-time indicators
        private IEnumerator TypeDialogue(string text, TextMeshProUGUI textComponent)
        {
            isTyping = true;
            textComponent.text = "";
            
            ShowTypingIndicator(true);
            
            for (int i = 0; i < text.Length; i++)
            {
                textComponent.text += text[i];
                yield return new WaitForSeconds(typingSpeed);
            }
            
            ShowTypingIndicator(false);
            isTyping = false;
        }
        
        private void ShowTypingIndicator(bool show)
        {
            if (typingIndicator != null)
            {
                typingIndicator.gameObject.SetActive(show);
                if (show)
                {
                    typingIndicator.text = "typing...";
                    StartCoroutine(AnimateTypingIndicator());
                }
            }
        }
        
        private IEnumerator AnimateTypingIndicator()
        {
            var states = new[] { "typing", "typing.", "typing..", "typing..." };
            int index = 0;
            
            while (typingIndicator.gameObject.activeInHierarchy)
            {
                typingIndicator.text = states[index];
                index = (index + 1) % states.Length;
                yield return new WaitForSeconds(0.5f);
            }
        }
        
        private void GenerateDialogueOptions()
        {
            // Clear existing options
            foreach (Transform child in dialogueOptionsParent)
            {
                Destroy(child.gameObject);
            }
            
            currentDialogueOptions.Clear();
            
            // Generate context-aware dialogue options
            var options = new List<DialogueOption>
            {
                new DialogueOption { text = "How are things going?", responseId = "general_wellbeing" },
                new DialogueOption { text = "What's new around here?", responseId = "local_news" },
                new DialogueOption { text = "Tell me about yourself.", responseId = "personal_info" }
            };
            
            // Add relationship-dependent options
            if (currentRelationship?.trustLevel >= 0.6f)
            {
                options.Add(new DialogueOption { text = "Can you help me with something?", responseId = "request_help" });
            }
            
            if (currentRelationship?.trustLevel >= 0.8f)
            {
                options.Add(new DialogueOption { text = "I need your advice.", responseId = "seek_advice" });
            }
            
            // Create UI for each option
            foreach (var option in options)
            {
                CreateDialogueOptionButton(option);
                currentDialogueOptions.Add(option);
            }
        }
        
        private void CreateDialogueOptionButton(DialogueOption option)
        {
            var optionButton = Instantiate(dialogueOptionPrefab, dialogueOptionsParent);
            optionButton.GetComponentInChildren<TextMeshProUGUI>().text = option.text;
            optionButton.onClick.AddListener(() => SelectDialogueOption(option.responseId));
            optionButton.gameObject.SetActive(true);
        }
        
        private void SelectDialogueOption(string option)
        {
            // Disable options during processing
            SetDialogueOptionsInteractable(false);
            
            // Add to conversation history
            AddToConversationHistory("Player", GetOptionText(option));
            
            // Show typing indicator
            ShowTypingIndicator(true);
            
            OnDialogueOptionSelected?.Invoke(option);
        }
        
        private void SetDialogueOptionsInteractable(bool interactable)
        {
            foreach (Transform child in dialogueOptionsParent)
            {
                var button = child.GetComponent<Button>();
                if (button != null)
                    button.interactable = interactable;
            }
        }
        
        private string GetOptionText(string responseId)
        {
            var option = currentDialogueOptions.Find(o => o.responseId == responseId);
            return option?.text ?? responseId;
        }
        
        public void DisplayNPCResponse(string response)
        {
            // Stop typing indicator
            ShowTypingIndicator(false);
            
            // Add to conversation history
            AddToConversationHistory(currentNPC.name, response);
            
            // Type the response
            if (typingCoroutine != null)
                StopCoroutine(typingCoroutine);
            
            typingCoroutine = StartCoroutine(TypeDialogue(response, dialogueText));
            
            // Re-enable dialogue options
            SetDialogueOptionsInteractable(true);
            
            // Generate new dialogue options based on response
            StartCoroutine(DelayedDialogueOptionsRefresh());
        }
        
        private IEnumerator DelayedDialogueOptionsRefresh()
        {
            yield return new WaitForSeconds(1f);
            GenerateDialogueOptions();
        }
        
        private void AddToConversationHistory(string speaker, string text)
        {
            var entry = new DialogueHistoryEntry
            {
                speaker = speaker,
                text = text,
                timestamp = DateTime.Now
            };
            
            conversationHistoryList.Add(entry);
            
            // Limit history size
            if (conversationHistoryList.Count > maxConversationHistory)
            {
                conversationHistoryList.RemoveAt(0);
            }
            
            // Update UI
            UpdateConversationHistoryUI();
        }
        
        private void UpdateConversationHistoryUI()
        {
            // Clear existing history
            foreach (Transform child in historyContent)
            {
                Destroy(child.gameObject);
            }
            
            // Add each history entry
            foreach (var entry in conversationHistoryList)
            {
                var historyEntry = Instantiate(historyEntryPrefab, historyContent);
                historyEntry.text = $"<b>{entry.speaker}:</b> {entry.text}";
                historyEntry.gameObject.SetActive(true);
            }
            
            // Scroll to bottom
            StartCoroutine(ScrollToBottom());
        }
        
        private IEnumerator ScrollToBottom()
        {
            yield return new WaitForEndOfFrame();
            conversationHistory.verticalNormalizedPosition = 0f;
        }
        
        private void LoadConversationHistory()
        {
            // Show resume button if there's existing conversation
            if (conversationHistoryList.Count > 0)
            {
                resumeConversationButton.gameObject.SetActive(true);
                UpdateConversationHistoryUI();
            }
            else
            {
                resumeConversationButton.gameObject.SetActive(false);
            }
        }
        
        private void ResumeConversation()
        {
            // Continue from where conversation left off
            GenerateDialogueOptions();
            resumeConversationButton.gameObject.SetActive(false);
        }
        
        private void SaveConversationState()
        {
            // TODO: Persist conversation state for future sessions
        }
        
        // Enhanced barter system with filtering and price comparison
        private void LoadNPCInventory()
        {
            // TODO: Load NPC inventory from backend
            // For now, placeholder implementation
        }
        
        private void LoadPlayerInventory()
        {
            // TODO: Load player inventory from backend
            // For now, placeholder implementation
        }
        
        private void FilterTradeItems(string filter)
        {
            // TODO: Implement item filtering based on availability tier and search text
        }
        
        private void UpdateTradeInterface()
        {
            // Calculate trade values
            float tradeValue = CalculateTradeValue();
            tradeValueText.text = $"Trade Value: {tradeValue:C}";
            
            // Show relationship impact
            string relationshipImpact = CalculateRelationshipImpact();
            relationshipImpactText.text = relationshipImpact;
            
            // Update price comparison
            UpdatePriceComparison();
        }
        
        private void UpdatePriceComparison()
        {
            // TODO: Compare prices with base market values
            priceComparisonText.text = "Market comparison: Fair price";
        }
        
        private void ConfirmTrade()
        {
            if (currentTradeOffer.Count == 0)
            {
                // Show error message
                return;
            }
            
            OnTradeProposed?.Invoke(currentTradeOffer);
        }
        
        private void CancelTrade()
        {
            currentTradeOffer.Clear();
            currentMode = InteractionMode.Main;
            SetAllPanelsInactive();
        }
        
        // Gift system implementation
        private void LoadGiftableItems()
        {
            // TODO: Load items that can be given as gifts
        }
        
        private void ConfirmGift()
        {
            // TODO: Process gift giving
            OnGiftGiven?.Invoke(currentNPC.id, 1); // placeholder
        }
        
        private void CancelGift()
        {
            currentMode = InteractionMode.Main;
            SetAllPanelsInactive();
        }
        
        // Challenge system implementation
        private void GenerateChallengeOptions()
        {
            // TODO: Generate available challenge types
        }
        
        // Context menu implementation
        private void GenerateContextOptions()
        {
            // Clear existing options
            foreach (Transform child in contextOptionsParent)
            {
                Destroy(child.gameObject);
            }
            
            // Generate location-specific options
            var contextOptions = new List<ContextOption>
            {
                new ContextOption { text = "Local Rumors", action = "rumors" },
                new ContextOption { text = "Recent Events", action = "events" },
                new ContextOption { text = "Trade Routes", action = "trade_routes" },
                new ContextOption { text = "Political Situation", action = "politics" }
            };
            
            contextTitle.text = "Ask About";
            contextDescription.text = "What would you like to know about this area?";
            
            // Create UI for each option
            foreach (var option in contextOptions)
            {
                CreateContextOptionButton(option);
            }
        }
        
        private void CreateContextOptionButton(ContextOption option)
        {
            var optionButton = Instantiate(contextOptionPrefab, contextOptionsParent);
            optionButton.GetComponentInChildren<TextMeshProUGUI>().text = option.text;
            optionButton.onClick.AddListener(() => SelectContextOption(option.action));
            optionButton.gameObject.SetActive(true);
        }
        
        private void SelectContextOption(string action)
        {
            OnContextActionSelected?.Invoke(action, null);
        }
        
        // Enhanced relationship and UI utility methods
        private string GetDetailedRelationshipDescription(float trustLevel)
        {
            if (trustLevel >= 0.9f) return "Best Friend";
            if (trustLevel >= 0.8f) return "Close Friend";
            if (trustLevel >= 0.7f) return "Good Friend";
            if (trustLevel >= 0.6f) return "Friend";
            if (trustLevel >= 0.5f) return "Acquaintance";
            if (trustLevel >= 0.4f) return "Neutral";
            if (trustLevel >= 0.3f) return "Suspicious";
            if (trustLevel >= 0.2f) return "Distrustful";
            if (trustLevel >= 0.1f) return "Hostile";
            return "Enemy";
        }
        
        private Color GetRelationshipColor(float trustLevel)
        {
            if (trustLevel >= 0.7f) return Color.green;
            if (trustLevel >= 0.4f) return Color.yellow;
            if (trustLevel >= 0.2f) return Color.orange;
            return Color.red;
        }
        
        private string GetPlayerName()
        {
            // TODO: Get actual player name from game state
            return "Traveler";
        }
        
        private bool HasContextualInformation()
        {
            // Always true - context is location/time based
            return true;
        }
        
        private bool HasGiftableItems()
        {
            // TODO: Check player inventory for giftable items
            return true; // Placeholder
        }
        
        private bool CanChallenge()
        {
            // TODO: Check if NPC accepts challenges
            return currentNPC?.npcType.ToString() != "Civilian"; // Placeholder
        }
        
        private float CalculateTradeValue()
        {
            // TODO: Calculate actual trade value
            return 100.0f; // Placeholder
        }
        
        private string CalculateRelationshipImpact()
        {
            // TODO: Calculate how trade will affect relationship
            return "This NPC will trust you more";
        }
    }
    
    [Serializable]
    public class DialogueOption
    {
        public string text;
        public string responseId;
        public bool requiresRelationship;
        public float minTrustLevel;
    }
    
    [Serializable]
    public class TradeItem
    {
        public string itemId;
        public int quantity;
        public float value;
        public bool isPlayerItem;
    }
    
    [Serializable]
    public class DialogueHistoryEntry
    {
        public string speaker;
        public string text;
        public DateTime timestamp;
    }
    
    [Serializable]
    public class ContextOption
    {
        public string text;
        public string action;
    }
} 