using UnityEngine;
using UnityEngine.UI;
using System;
using VDM.UI.Core;
using VDM.Infrastructure.Ui.Ui.Framework;
using TMPro;

namespace VDM.Infrastructure.UI.Screens
{
    /// <summary>
    /// Main menu screen for game navigation and initialization
    /// </summary>
    public class MainMenuScreen : BaseUIScreen
    {
        [Header("Main Menu Components")]
        [SerializeField] private Button newGameButton;
        [SerializeField] private Button loadGameButton;
        [SerializeField] private Button settingsButton;
        [SerializeField] private Button exitButton;
        [SerializeField] private Button creditsButton;
        
        [Header("Title and Version")]
        [SerializeField] private TextMeshProUGUI titleText;
        [SerializeField] private TextMeshProUGUI versionText;
        [SerializeField] private TextMeshProUGUI copyrightText;
        
        [Header("Panels")]
        [SerializeField] private GameObject mainPanel;
        [SerializeField] private GameObject loadingPanel;
        [SerializeField] private Slider loadingProgressBar;
        [SerializeField] private TextMeshProUGUI loadingStatusText;
        
        [Header("Background and Effects")]
        [SerializeField] private Image backgroundImage;
        [SerializeField] private ParticleSystem backgroundParticles;
        [SerializeField] private AudioSource backgroundMusic;
        
        // Events
        public event Action OnNewGameRequested;
        public event Action OnLoadGameRequested;
        public event Action OnSettingsRequested;
        public event Action OnCreditsRequested;
        public event Action OnExitRequested;
        
        // State
        private bool isLoading = false;
        
        #region Initialization
        
        protected override void OnInitialize()
        {
            base.OnInitialize();
            
            // Set screen configuration
            SetScreenConfig("MainMenu", ScreenLayer.Main, 0);
            SetTransitionConfig(ScreenTransition.Fade, ScreenTransition.Fade, 0.5f, 0.3f);
            
            // Initialize UI elements
            InitializeButtons();
            InitializeTexts();
            InitializeBackground();
            
            Debug.Log("Main Menu Screen initialized");
        }
        
        /// <summary>
        /// Initialize button components and events
        /// </summary>
        private void InitializeButtons()
        {
            if (newGameButton)
            {
                newGameButton.onClick.AddListener(OnNewGameButtonClicked);
            }
            
            if (loadGameButton)
            {
                loadGameButton.onClick.AddListener(OnLoadGameButtonClicked);
            }
            
            if (settingsButton)
            {
                settingsButton.onClick.AddListener(OnSettingsButtonClicked);
            }
            
            if (creditsButton)
            {
                creditsButton.onClick.AddListener(OnCreditsButtonClicked);
            }
            
            if (exitButton)
            {
                exitButton.onClick.AddListener(OnExitButtonClicked);
            }
        }
        
        /// <summary>
        /// Initialize text components
        /// </summary>
        private void InitializeTexts()
        {
            if (titleText)
            {
                titleText.text = "Visual Dynamic Multiverse";
            }
            
            if (versionText)
            {
                versionText.text = $"Version {Application.version}";
            }
            
            if (copyrightText)
            {
                copyrightText.text = $"© {DateTime.Now.Year} VDM Studios";
            }
        }
        
        /// <summary>
        /// Initialize background elements
        /// </summary>
        private void InitializeBackground()
        {
            if (backgroundParticles)
            {
                backgroundParticles.Play();
            }
            
            if (backgroundMusic)
            {
                backgroundMusic.Play();
            }
        }
        
        #endregion
        
        #region Screen Lifecycle
        
        protected override void OnScreenWillShow()
        {
            base.OnScreenWillShow();
            
            // Reset to main panel
            ShowMainPanel();
            
            // Check for saved games to enable/disable load button
            UpdateLoadGameButton();
            
            // Start background effects
            if (backgroundParticles && !backgroundParticles.isPlaying)
            {
                backgroundParticles.Play();
            }
            
            if (backgroundMusic && !backgroundMusic.isPlaying)
            {
                backgroundMusic.Play();
            }
        }
        
        protected override void OnScreenWillHide()
        {
            base.OnScreenWillHide();
            
            // Stop background effects if needed
            if (backgroundMusic && backgroundMusic.isPlaying)
            {
                backgroundMusic.Stop();
            }
        }
        
        #endregion
        
        #region Button Handlers
        
        /// <summary>
        /// Handle new game button click
        /// </summary>
        private void OnNewGameButtonClicked()
        {
            if (isLoading) return;
            
            Debug.Log("New Game button clicked");
            
            // Show loading and start new game
            ShowLoadingPanel("Creating new game...");
            OnNewGameRequested?.Invoke();
            
            // Navigate to game setup or directly to game scene
            StartCoroutine(SimulateGameCreation());
        }
        
        /// <summary>
        /// Handle load game button click
        /// </summary>
        private void OnLoadGameButtonClicked()
        {
            if (isLoading) return;
            
            Debug.Log("Load Game button clicked");
            
            OnLoadGameRequested?.Invoke();
            
            // Navigate to save game selection screen
            NavigateToScreen("SaveGameSelect");
        }
        
        /// <summary>
        /// Handle settings button click
        /// </summary>
        private void OnSettingsButtonClicked()
        {
            if (isLoading) return;
            
            Debug.Log("Settings button clicked");
            
            OnSettingsRequested?.Invoke();
            
            // Show settings as popup
            ShowPopup("SettingsMenu");
        }
        
        /// <summary>
        /// Handle credits button click
        /// </summary>
        private void OnCreditsButtonClicked()
        {
            if (isLoading) return;
            
            Debug.Log("Credits button clicked");
            
            OnCreditsRequested?.Invoke();
            
            // Navigate to credits screen
            NavigateToScreen("Credits");
        }
        
        /// <summary>
        /// Handle exit button click
        /// </summary>
        private void OnExitButtonClicked()
        {
            if (isLoading) return;
            
            Debug.Log("Exit button clicked");
            
            OnExitRequested?.Invoke();
            
            // Show confirmation dialog
            ShowModal("ExitConfirmation");
        }
        
        #endregion
        
        #region Loading Management
        
        /// <summary>
        /// Show the loading panel with status text
        /// </summary>
        private void ShowLoadingPanel(string statusText = "Loading...")
        {
            isLoading = true;
            
            if (mainPanel)
                mainPanel.SetActive(false);
            
            if (loadingPanel)
                loadingPanel.SetActive(true);
            
            if (loadingStatusText)
                loadingStatusText.text = statusText;
            
            if (loadingProgressBar)
                loadingProgressBar.value = 0f;
                
            SetInteractable(false);
        }
        
        /// <summary>
        /// Show the main panel and hide loading
        /// </summary>
        private void ShowMainPanel()
        {
            isLoading = false;
            
            if (loadingPanel)
                loadingPanel.SetActive(false);
            
            if (mainPanel)
                mainPanel.SetActive(true);
                
            SetInteractable(true);
        }
        
        /// <summary>
        /// Update loading progress
        /// </summary>
        public void UpdateLoadingProgress(float progress, string statusText = null)
        {
            if (loadingProgressBar)
            {
                loadingProgressBar.value = Mathf.Clamp01(progress);
            }
            
            if (!string.IsNullOrEmpty(statusText) && loadingStatusText)
            {
                loadingStatusText.text = statusText;
            }
        }
        
        /// <summary>
        /// Simulate game creation with loading progress
        /// </summary>
        private System.Collections.IEnumerator SimulateGameCreation()
        {
            float progress = 0f;
            string[] steps = {
                "Initializing world...",
                "Creating terrain...",
                "Spawning entities...",
                "Loading assets...",
                "Finalizing setup..."
            };
            
            for (int i = 0; i < steps.Length; i++)
            {
                UpdateLoadingProgress(progress, steps[i]);
                
                // Simulate loading time
                yield return new WaitForSeconds(0.5f);
                
                progress = (float)(i + 1) / steps.Length;
            }
            
            UpdateLoadingProgress(1f, "Complete!");
            yield return new WaitForSeconds(0.3f);
            
            // Navigate to main game
            NavigateToScreen("GameWorld");
        }
        
        #endregion
        
        #region Save Game Management
        
        /// <summary>
        /// Update the load game button based on available saves
        /// </summary>
        private void UpdateLoadGameButton()
        {
            if (!loadGameButton) return;
            
            // Check if there are any saved games
            bool hasSavedGames = CheckForSavedGames();
            
            loadGameButton.interactable = hasSavedGames;
            
            // Update button appearance based on availability
            var buttonImage = loadGameButton.GetComponent<Image>();
            if (buttonImage)
            {
                buttonImage.color = hasSavedGames ? Color.white : Color.gray;
            }
        }
        
        /// <summary>
        /// Check if there are any saved games available
        /// </summary>
        private bool CheckForSavedGames()
        {
            // This would check actual save file system
            // For now, return true if any save files exist
            return System.IO.Directory.Exists(Application.persistentDataPath + "/saves") &&
                   System.IO.Directory.GetFiles(Application.persistentDataPath + "/saves", "*.save").Length > 0;
        }
        
        #endregion
        
        #region Audio and Visual Effects
        
        /// <summary>
        /// Set background music volume
        /// </summary>
        public void SetMusicVolume(float volume)
        {
            if (backgroundMusic)
            {
                backgroundMusic.volume = Mathf.Clamp01(volume);
            }
        }
        
        /// <summary>
        /// Enable or disable particle effects
        /// </summary>
        public void SetParticleEffects(bool enabled)
        {
            if (backgroundParticles)
            {
                if (enabled && !backgroundParticles.isPlaying)
                {
                    backgroundParticles.Play();
                }
                else if (!enabled && backgroundParticles.isPlaying)
                {
                    backgroundParticles.Stop();
                }
            }
        }
        
        /// <summary>
        /// Change background image
        /// </summary>
        public void SetBackgroundImage(Sprite newBackground)
        {
            if (backgroundImage && newBackground)
            {
                backgroundImage.sprite = newBackground;
            }
        }
        
        #endregion
        
        #region Custom Transitions
        
        /// <summary>
        /// Custom show transition for main menu
        /// </summary>
        protected override void ShowCustomTransition(Action onComplete = null)
        {
            // Custom fade in with title animation
            if (titleText)
            {
                titleText.color = Color.clear;
                StartCoroutine(FadeInTitle(onComplete));
            }
            else
            {
                FadeIn(showDuration, onComplete);
            }
        }
        
        /// <summary>
        /// Fade in title text with special effect
        /// </summary>
        private System.Collections.IEnumerator FadeInTitle(Action onComplete = null)
        {
            // Fade in the screen first
            FadeIn(showDuration * 0.7f);
            
            yield return new WaitForSeconds(showDuration * 0.7f);
            
            // Then animate the title
            float elapsed = 0f;
            float titleDuration = showDuration * 0.3f;
            
            while (elapsed < titleDuration)
            {
                elapsed += UnityEngine.Time.deltaTime;
                float t = Mathf.Clamp01(elapsed / titleDuration);
                
                if (titleText)
                {
                    titleText.color = Color.Lerp(Color.clear, Color.white, EaseInOut(t));
                }
                
                yield return null;
            }
            
            if (titleText)
            {
                titleText.color = Color.white;
            }
            
            onComplete?.Invoke();
        }
        
        #endregion
        
        #region Screen Validation
        
        /// <summary>
        /// Check if the main menu can be shown
        /// </summary>
        public override bool CanShow()
        {
            return !isLoading && base.CanShow();
        }
        
        /// <summary>
        /// Check if the main menu can be hidden
        /// </summary>
        public override bool CanHide()
        {
            // Can always hide main menu unless in critical loading state
            return base.CanHide();
        }
        
        #endregion
        
        #region Cleanup
        
        private void OnCleanup()
        {
            // Clean up button listeners
            if (newGameButton)
                newGameButton.onClick.RemoveAllListeners();
            
            if (loadGameButton)
                loadGameButton.onClick.RemoveAllListeners();
            
            if (settingsButton)
                settingsButton.onClick.RemoveAllListeners();
            
            if (creditsButton)
                creditsButton.onClick.RemoveAllListeners();
            
            if (exitButton)
                exitButton.onClick.RemoveAllListeners();
            
            // Stop audio and effects
            if (backgroundMusic && backgroundMusic.isPlaying)
                backgroundMusic.Stop();
            
            if (backgroundParticles && backgroundParticles.isPlaying)
                backgroundParticles.Stop();
        }
        
        // Override OnDestroy to call cleanup
        private void OnDestroy()
        {
            OnCleanup();
        }
        
        #endregion
    }
} 