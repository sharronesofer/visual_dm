using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System;
using VDM.UI.Core;
using TMPro;
using VDM.Infrastructure.Services;
using VDM.Infrastructure.Core.Core.Ui;

namespace VDM.Infrastructure.UI.Components
{
    /// <summary>
    /// HUD overlay for displaying essential game information
    /// </summary>
    public class HUDOverlay : BaseUIComponent
    {
        [Header("Health and Status")]
        [SerializeField] private Slider healthBar;
        [SerializeField] private Slider manaBar;
        [SerializeField] private Slider staminaBar;
        [SerializeField] private TextMeshProUGUI healthText;
        [SerializeField] private TextMeshProUGUI manaText;
        [SerializeField] private TextMeshProUGUI staminaText;
        
        [Header("Resources")]
        [SerializeField] private TextMeshProUGUI goldText;
        [SerializeField] private TextMeshProUGUI experienceText;
        [SerializeField] private TextMeshProUGUI levelText;
        [SerializeField] private Slider experienceBar;
        
        [Header("Time and Environment")]
        [SerializeField] private TextMeshProUGUI timeText;
        [SerializeField] private TextMeshProUGUI dayText;
        [SerializeField] private TextMeshProUGUI weatherText;
        [SerializeField] private Image timeOfDayIcon;
        [SerializeField] private Image weatherIcon;
        
        [Header("Minimap and Location")]
        [SerializeField] private RawImage minimapDisplay;
        [SerializeField] private TextMeshProUGUI locationText;
        [SerializeField] private Transform playerMarker;
        [SerializeField] private RectTransform minimapContainer;
        
        [Header("Quick Actions")]
        [SerializeField] private Button inventoryButton;
        [SerializeField] private Button questLogButton;
        [SerializeField] private Button characterSheetButton;
        [SerializeField] private Button settingsButton;
        [SerializeField] private Button menuButton;
        
        [Header("Notifications")]
        [SerializeField] private Transform notificationContainer;
        [SerializeField] private GameObject notificationPrefab;
        [SerializeField] private TextMeshProUGUI messageText;
        [SerializeField] private float notificationDuration = 3f;
        
        [Header("Hotbar")]
        [SerializeField] private Transform hotbarContainer;
        [SerializeField] private GameObject hotbarSlotPrefab;
        [SerializeField] private int hotbarSlotCount = 10;
        
        // Bar animation settings
        [Header("Animation Settings")]
        [SerializeField] private float barAnimationSpeed = 2f;
        [SerializeField] private bool animateBarChanges = true;
        [SerializeField] private Color lowHealthColor = Color.red;
        [SerializeField] private Color normalHealthColor = Color.green;
        [SerializeField] private float lowHealthThreshold = 0.25f;
        
        // Events
        public event Action OnInventoryRequested;
        public event Action OnQuestLogRequested;
        public event Action OnCharacterSheetRequested;
        public event Action OnSettingsRequested;
        public event Action OnMenuRequested;
        
        // Current values for animation
        private float currentHealth = 1f;
        private float currentMana = 1f;
        private float currentStamina = 1f;
        private float currentExperience = 0f;
        
        // Target values
        private float targetHealth = 1f;
        private float targetMana = 1f;
        private float targetStamina = 1f;
        private float targetExperience = 0f;
        
        // Hotbar slots
        private HotbarSlot[] hotbarSlots;
        
        // Notification queue
        private System.Collections.Generic.Queue<string> notificationQueue = new System.Collections.Generic.Queue<string>();
        private bool isShowingNotification = false;
        
        #region Initialization
        
        protected override void OnInitialize()
        {
            base.OnInitialize();
            
            // Initialize UI components
            InitializeButtons();
            InitializeBars();
            InitializeHotbar();
            
            // Set initial values
            ResetToDefaults();
            
            Debug.Log("HUD Overlay initialized");
        }
        
        /// <summary>
        /// Initialize button components and events
        /// </summary>
        private void InitializeButtons()
        {
            if (inventoryButton)
                inventoryButton.onClick.AddListener(() => OnInventoryRequested?.Invoke());
            
            if (questLogButton)
                questLogButton.onClick.AddListener(() => OnQuestLogRequested?.Invoke());
            
            if (characterSheetButton)
                characterSheetButton.onClick.AddListener(() => OnCharacterSheetRequested?.Invoke());
            
            if (settingsButton)
                settingsButton.onClick.AddListener(() => OnSettingsRequested?.Invoke());
            
            if (menuButton)
                menuButton.onClick.AddListener(() => OnMenuRequested?.Invoke());
        }
        
        /// <summary>
        /// Initialize health/mana/stamina bars
        /// </summary>
        private void InitializeBars()
        {
            if (healthBar)
            {
                healthBar.minValue = 0f;
                healthBar.maxValue = 1f;
                healthBar.value = 1f;
            }
            
            if (manaBar)
            {
                manaBar.minValue = 0f;
                manaBar.maxValue = 1f;
                manaBar.value = 1f;
            }
            
            if (staminaBar)
            {
                staminaBar.minValue = 0f;
                staminaBar.maxValue = 1f;
                staminaBar.value = 1f;
            }
            
            if (experienceBar)
            {
                experienceBar.minValue = 0f;
                experienceBar.maxValue = 1f;
                experienceBar.value = 0f;
            }
        }
        
        /// <summary>
        /// Initialize hotbar slots
        /// </summary>
        private void InitializeHotbar()
        {
            if (!hotbarContainer || !hotbarSlotPrefab) return;
            
            hotbarSlots = new HotbarSlot[hotbarSlotCount];
            
            for (int i = 0; i < hotbarSlotCount; i++)
            {
                var slotObj = Instantiate(hotbarSlotPrefab, hotbarContainer);
                var slot = slotObj.GetComponent<HotbarSlot>();
                
                if (!slot)
                {
                    slot = slotObj.AddComponent<HotbarSlot>();
                }
                
                slot.Initialize(i);
                hotbarSlots[i] = slot;
            }
        }
        
        /// <summary>
        /// Reset all values to defaults
        /// </summary>
        private void ResetToDefaults()
        {
            UpdateHealth(100, 100);
            UpdateMana(100, 100);
            UpdateStamina(100, 100);
            UpdateExperience(0, 100);
            UpdateGold(0);
            UpdateLevel(1);
            UpdateLocation("Unknown");
            UpdateTime(12, 0); // Noon
            UpdateDay(1);
            UpdateWeather("Clear");
        }
        
        #endregion
        
        #region Update Methods
        
        private void Update()
        {
            if (animateBarChanges)
            {
                AnimateBars();
            }
            
            // Process notification queue
            if (!isShowingNotification && notificationQueue.Count > 0)
            {
                ProcessNotificationQueue();
            }
        }
        
        /// <summary>
        /// Animate bar value changes smoothly
        /// </summary>
        private void AnimateBars()
        {
            float deltaTime = UnityEngine.Time.deltaTime;
            float speed = barAnimationSpeed;
            
            // Animate health bar
            if (Mathf.Abs(currentHealth - targetHealth) > 0.01f)
            {
                currentHealth = Mathf.MoveTowards(currentHealth, targetHealth, speed * deltaTime);
                if (healthBar)
                    healthBar.value = currentHealth;
                
                UpdateHealthBarColor();
            }
            
            // Animate mana bar
            if (Mathf.Abs(currentMana - targetMana) > 0.01f)
            {
                currentMana = Mathf.MoveTowards(currentMana, targetMana, speed * deltaTime);
                if (manaBar)
                    manaBar.value = currentMana;
            }
            
            // Animate stamina bar
            if (Mathf.Abs(currentStamina - targetStamina) > 0.01f)
            {
                currentStamina = Mathf.MoveTowards(currentStamina, targetStamina, speed * deltaTime);
                if (staminaBar)
                    staminaBar.value = currentStamina;
            }
            
            // Animate experience bar
            if (Mathf.Abs(currentExperience - targetExperience) > 0.01f)
            {
                currentExperience = Mathf.MoveTowards(currentExperience, targetExperience, speed * deltaTime);
                if (experienceBar)
                    experienceBar.value = currentExperience;
            }
        }
        
        /// <summary>
        /// Update health bar color based on current health
        /// </summary>
        private void UpdateHealthBarColor()
        {
            if (!healthBar) return;
            
            var fillImage = healthBar.fillRect?.GetComponent<Image>();
            if (!fillImage) return;
            
            if (currentHealth <= lowHealthThreshold)
            {
                fillImage.color = Color.Lerp(lowHealthColor, normalHealthColor, currentHealth / lowHealthThreshold);
            }
            else
            {
                fillImage.color = normalHealthColor;
            }
        }
        
        #endregion
        
        #region Health/Mana/Stamina Updates
        
        /// <summary>
        /// Update health display
        /// </summary>
        public void UpdateHealth(float current, float max)
        {
            targetHealth = Mathf.Clamp01(current / max);
            
            if (!animateBarChanges)
            {
                currentHealth = targetHealth;
                if (healthBar)
                    healthBar.value = currentHealth;
                UpdateHealthBarColor();
            }
            
            if (healthText)
                healthText.text = $"{current:F0}/{max:F0}";
        }
        
        /// <summary>
        /// Update mana display
        /// </summary>
        public void UpdateMana(float current, float max)
        {
            targetMana = Mathf.Clamp01(current / max);
            
            if (!animateBarChanges)
            {
                currentMana = targetMana;
                if (manaBar)
                    manaBar.value = currentMana;
            }
            
            if (manaText)
                manaText.text = $"{current:F0}/{max:F0}";
        }
        
        /// <summary>
        /// Update stamina display
        /// </summary>
        public void UpdateStamina(float current, float max)
        {
            targetStamina = Mathf.Clamp01(current / max);
            
            if (!animateBarChanges)
            {
                currentStamina = targetStamina;
                if (staminaBar)
                    staminaBar.value = currentStamina;
            }
            
            if (staminaText)
                staminaText.text = $"{current:F0}/{max:F0}";
        }
        
        #endregion
        
        #region Resource Updates
        
        /// <summary>
        /// Update gold display
        /// </summary>
        public void UpdateGold(int amount)
        {
            if (goldText)
                goldText.text = $"{amount:N0}";
        }
        
        /// <summary>
        /// Update experience display
        /// </summary>
        public void UpdateExperience(float current, float required)
        {
            targetExperience = Mathf.Clamp01(current / required);
            
            if (!animateBarChanges)
            {
                currentExperience = targetExperience;
                if (experienceBar)
                    experienceBar.value = currentExperience;
            }
            
            if (experienceText)
                experienceText.text = $"{current:F0}/{required:F0}";
        }
        
        /// <summary>
        /// Update level display
        /// </summary>
        public void UpdateLevel(int level)
        {
            if (levelText)
                levelText.text = $"Level {level}";
        }
        
        #endregion
        
        #region Time and Environment Updates
        
        /// <summary>
        /// Update time display
        /// </summary>
        public void UpdateTime(int hour, int minute)
        {
            if (timeText)
            {
                string period = hour >= 12 ? "PM" : "AM";
                int displayHour = hour > 12 ? hour - 12 : (hour == 0 ? 12 : hour);
                timeText.text = $"{displayHour}:{minute:D2} {period}";
            }
            
            UpdateTimeOfDayIcon(hour);
        }
        
        /// <summary>
        /// Update day display
        /// </summary>
        public void UpdateDay(int day)
        {
            if (dayText)
                dayText.text = $"Day {day}";
        }
        
        /// <summary>
        /// Update weather display
        /// </summary>
        public void UpdateWeather(string weather)
        {
            if (weatherText)
                weatherText.text = weather;
            
            UpdateWeatherIcon(weather);
        }
        
        /// <summary>
        /// Update location display
        /// </summary>
        public void UpdateLocation(string location)
        {
            if (locationText)
                locationText.text = location;
        }
        
        /// <summary>
        /// Update time of day icon based on hour
        /// </summary>
        private void UpdateTimeOfDayIcon(int hour)
        {
            if (!timeOfDayIcon) return;
            
            // This would load appropriate sprites for different times
            // For now, just change color
            if (hour >= 6 && hour < 18)
            {
                timeOfDayIcon.color = Color.yellow; // Day
            }
            else if (hour >= 18 && hour < 20)
            {
                timeOfDayIcon.color = Color.orange; // Evening
            }
            else
            {
                timeOfDayIcon.color = Color.blue; // Night
            }
        }
        
        /// <summary>
        /// Update weather icon based on weather type
        /// </summary>
        private void UpdateWeatherIcon(string weather)
        {
            if (!weatherIcon) return;
            
            // This would load appropriate sprites for different weather
            // For now, just change color as example
            switch (weather.ToLower())
            {
                case "sunny":
                case "clear":
                    weatherIcon.color = Color.yellow;
                    break;
                case "cloudy":
                    weatherIcon.color = Color.gray;
                    break;
                case "rain":
                case "rainy":
                    weatherIcon.color = Color.blue;
                    break;
                case "storm":
                    weatherIcon.color = Color.red;
                    break;
                default:
                    weatherIcon.color = Color.white;
                    break;
            }
        }
        
        #endregion
        
        #region Minimap Updates
        
        /// <summary>
        /// Update minimap texture
        /// </summary>
        public void UpdateMinimap(Texture2D mapTexture)
        {
            if (minimapDisplay && mapTexture)
            {
                minimapDisplay.texture = mapTexture;
            }
        }
        
        /// <summary>
        /// Update player position on minimap
        /// </summary>
        public void UpdatePlayerPosition(Vector2 worldPosition, Vector2 mapSize)
        {
            if (!playerMarker || !minimapContainer) return;
            
            // Convert world position to minimap position
            var minimapRect = minimapContainer.rect;
            var minimapPos = new Vector2(
                (worldPosition.x / mapSize.x) * minimapRect.width - minimapRect.width * 0.5f,
                (worldPosition.y / mapSize.y) * minimapRect.height - minimapRect.height * 0.5f
            );
            
            playerMarker.localPosition = minimapPos;
        }
        
        #endregion
        
        #region Notifications
        
        /// <summary>
        /// Show a notification message
        /// </summary>
        public void ShowNotification(string message)
        {
            notificationQueue.Enqueue(message);
        }
        
        /// <summary>
        /// Process notification queue
        /// </summary>
        private void ProcessNotificationQueue()
        {
            if (isShowingNotification || notificationQueue.Count == 0) return;
            
            string message = notificationQueue.Dequeue();
            StartCoroutine(DisplayNotification(message));
        }
        
        /// <summary>
        /// Display a notification for a specified duration
        /// </summary>
        private System.Collections.IEnumerator DisplayNotification(string message)
        {
            isShowingNotification = true;
            
            if (messageText)
            {
                messageText.text = message;
                messageText.gameObject.SetActive(true);
                
                // Fade in
                var canvasGroup = messageText.GetComponent<CanvasGroup>();
                if (canvasGroup)
                {
                    canvasGroup.alpha = 0f;
                    float elapsed = 0f;
                    float fadeTime = 0.3f;
                    
                    while (elapsed < fadeTime)
                    {
                        elapsed += Time.deltaTime;
                        canvasGroup.alpha = Mathf.Lerp(0f, 1f, elapsed / fadeTime);
                        yield return null;
                    }
                    canvasGroup.alpha = 1f;
                }
                
                // Wait
                yield return new WaitForSeconds(notificationDuration);
                
                // Fade out
                if (canvasGroup)
                {
                    float elapsed = 0f;
                    float fadeTime = 0.3f;
                    
                    while (elapsed < fadeTime)
                    {
                        elapsed += Time.deltaTime;
                        canvasGroup.alpha = Mathf.Lerp(1f, 0f, elapsed / fadeTime);
                        yield return null;
                    }
                    canvasGroup.alpha = 0f;
                }
                
                messageText.gameObject.SetActive(false);
            }
            
            isShowingNotification = false;
        }
        
        #endregion
        
        #region Hotbar Management
        
        /// <summary>
        /// Update hotbar slot
        /// </summary>
        public void UpdateHotbarSlot(int slotIndex, Sprite icon, string tooltip = null, bool isUsable = true)
        {
            if (hotbarSlots == null || slotIndex < 0 || slotIndex >= hotbarSlots.Length) return;
            
            hotbarSlots[slotIndex].UpdateSlot(icon, tooltip, isUsable);
        }
        
        /// <summary>
        /// Clear hotbar slot
        /// </summary>
        public void ClearHotbarSlot(int slotIndex)
        {
            if (hotbarSlots == null || slotIndex < 0 || slotIndex >= hotbarSlots.Length) return;
            
            hotbarSlots[slotIndex].ClearSlot();
        }
        
        /// <summary>
        /// Set hotbar slot cooldown
        /// </summary>
        public void SetHotbarCooldown(int slotIndex, float cooldownTime)
        {
            if (hotbarSlots == null || slotIndex < 0 || slotIndex >= hotbarSlots.Length) return;
            
            hotbarSlots[slotIndex].StartCooldown(cooldownTime);
        }
        
        #endregion
        
        #region Visibility Control
        
        /// <summary>
        /// Show or hide specific HUD elements
        /// </summary>
        public void SetElementVisibility(string elementName, bool visible)
        {
            switch (elementName.ToLower())
            {
                case "health":
                    if (healthBar) healthBar.transform.parent.gameObject.SetActive(visible);
                    break;
                case "mana":
                    if (manaBar) manaBar.transform.parent.gameObject.SetActive(visible);
                    break;
                case "stamina":
                    if (staminaBar) staminaBar.transform.parent.gameObject.SetActive(visible);
                    break;
                case "minimap":
                    if (minimapContainer) minimapContainer.gameObject.SetActive(visible);
                    break;
                case "hotbar":
                    if (hotbarContainer) hotbarContainer.gameObject.SetActive(visible);
                    break;
                case "time":
                    if (timeText) timeText.transform.parent.gameObject.SetActive(visible);
                    break;
                default:
                    Debug.LogWarning($"Unknown HUD element: {elementName}");
                    break;
            }
        }
        
        /// <summary>
        /// Toggle combat mode (show/hide certain elements)
        /// </summary>
        public void SetCombatMode(bool inCombat)
        {
            // In combat mode, emphasize health/mana/stamina
            float alpha = inCombat ? 1f : 0.7f;
            
            SetBarAlpha(healthBar, alpha);
            SetBarAlpha(manaBar, alpha);
            SetBarAlpha(staminaBar, alpha);
        }
        
        /// <summary>
        /// Set bar alpha value
        /// </summary>
        private void SetBarAlpha(Slider bar, float alpha)
        {
            if (!bar) return;
            
            var canvasGroup = bar.GetComponent<CanvasGroup>();
            if (!canvasGroup)
                canvasGroup = bar.gameObject.AddComponent<CanvasGroup>();
            
            canvasGroup.alpha = alpha;
        }
        
        #endregion
        
        #region Cleanup
        
        private void OnCleanup()
        {
            // Clean up button listeners
            if (inventoryButton)
                inventoryButton.onClick.RemoveAllListeners();
            
            if (questLogButton)
                questLogButton.onClick.RemoveAllListeners();
            
            if (characterSheetButton)
                characterSheetButton.onClick.RemoveAllListeners();
            
            if (settingsButton)
                settingsButton.onClick.RemoveAllListeners();
            
            if (menuButton)
                menuButton.onClick.RemoveAllListeners();
            
            // Stop any running coroutines
            StopAllCoroutines();
        }
        
        // Call this in OnDestroy
        private void OnDestroy()
        {
            OnCleanup();
        }
        
        #endregion
    }
    
    /// <summary>
    /// Hotbar slot component
    /// </summary>
    [System.Serializable]
    public class HotbarSlot : MonoBehaviour
    {
        [SerializeField] private Image iconImage;
        [SerializeField] private Button slotButton;
        [SerializeField] private TextMeshProUGUI keyBindText;
        [SerializeField] private Image cooldownOverlay;
        [SerializeField] private TextMeshProUGUI cooldownText;
        
        private int slotIndex;
        private bool isOnCooldown = false;
        private float cooldownEndTime;
        
        public event Action<int> OnSlotClicked;
        
        /// <summary>
        /// Initialize the hotbar slot
        /// </summary>
        public void Initialize(int index)
        {
            slotIndex = index;
            
            if (slotButton)
                slotButton.onClick.AddListener(() => OnSlotClicked?.Invoke(slotIndex));
            
            if (keyBindText)
                keyBindText.text = (index + 1).ToString();
            
            if (cooldownOverlay)
                cooldownOverlay.gameObject.SetActive(false);
            
            ClearSlot();
        }
        
        /// <summary>
        /// Update slot content
        /// </summary>
        public void UpdateSlot(Sprite icon, string tooltip = null, bool isUsable = true)
        {
            if (iconImage)
            {
                iconImage.sprite = icon;
                iconImage.gameObject.SetActive(icon != null);
            }
            
            if (slotButton)
                slotButton.interactable = isUsable && !isOnCooldown;
            
            // Set tooltip if system exists
            // This would integrate with a tooltip system
        }
        
        /// <summary>
        /// Clear slot content
        /// </summary>
        public void ClearSlot()
        {
            if (iconImage)
            {
                iconImage.sprite = null;
                iconImage.gameObject.SetActive(false);
            }
            
            if (slotButton)
                slotButton.interactable = false;
        }
        
        /// <summary>
        /// Start cooldown animation
        /// </summary>
        public void StartCooldown(float duration)
        {
            isOnCooldown = true;
            cooldownEndTime = UnityEngine.Time.time + duration;
            
            if (cooldownOverlay)
                cooldownOverlay.gameObject.SetActive(true);
            
            if (slotButton)
                slotButton.interactable = false;
            
            StartCoroutine(CooldownCoroutine());
        }
        
        /// <summary>
        /// Cooldown animation coroutine
        /// </summary>
        private System.Collections.IEnumerator CooldownCoroutine()
        {
            while (isOnCooldown && UnityEngine.Time.time < cooldownEndTime)
            {
                float remaining = cooldownEndTime - UnityEngine.Time.time;
                
                if (cooldownText)
                    cooldownText.text = $"{remaining:F1}s";
                
                if (cooldownOverlay)
                {
                    float progress = remaining / (cooldownEndTime - (UnityEngine.Time.time - remaining));
                    cooldownOverlay.fillAmount = progress;
                }
                
                yield return null;
            }
            
            // Cooldown finished
            isOnCooldown = false;
            
            if (cooldownOverlay)
                cooldownOverlay.gameObject.SetActive(false);
            
            if (slotButton && iconImage && iconImage.sprite)
                slotButton.interactable = true;
        }
    }
} 