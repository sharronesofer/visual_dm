using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using DG.Tweening;
using VDM.Systems.Character.UI;
using VDM.Core.DTOs;

namespace VDM.UI.SkillCheck
{
    public class SkillCheckUIComponent : MonoBehaviour
    {
        [Header("UI Panels")]
        [SerializeField] private GameObject skillCheckPanel;
        [SerializeField] private GameObject selectionTab;
        [SerializeField] private GameObject confirmTab;
        [SerializeField] private GameObject rollingTab;
        [SerializeField] private GameObject resultTab;

        [Header("Selection Tab")]
        [SerializeField] private Transform skillOptionsContainer;
        [SerializeField] private GameObject skillOptionPrefab;
        [SerializeField] private TextMeshProUGUI contextText;
        [SerializeField] private Transform environmentalBadgesContainer;
        [SerializeField] private GameObject environmentalBadgePrefab;

        [Header("Confirm Tab")]
        [SerializeField] private TextMeshProUGUI selectedSkillText;
        [SerializeField] private TextMeshProUGUI skillModifierText;
        [SerializeField] private TextMeshProUGUI difficultyClassText;
        [SerializeField] private TextMeshProUGUI advantageText;
        [SerializeField] private Button confirmButton;
        [SerializeField] private Button backButton;

        [Header("Rolling Tab")]
        [SerializeField] private Image[] diceImages;
        [SerializeField] private TextMeshProUGUI rollingText;
        [SerializeField] private Slider progressBar;
        [SerializeField] private ParticleSystem diceParticles;

        [Header("Result Tab")]
        [SerializeField] private TextMeshProUGUI resultTitleText;
        [SerializeField] private TextMeshProUGUI resultDescriptionText;
        [SerializeField] private TextMeshProUGUI diceRollText;
        [SerializeField] private TextMeshProUGUI totalRollText;
        [SerializeField] private TextMeshProUGUI outcomeText;
        [SerializeField] private Image resultIcon;
        [SerializeField] private Button closeButton;
        [SerializeField] private Button retryButton;

        [Header("Dice Sprites")]
        [SerializeField] private Sprite[] diceFaceSprites; // D20 faces 1-20
        [SerializeField] private Sprite successIcon;
        [SerializeField] private Sprite failureIcon;
        [SerializeField] private Sprite criticalSuccessIcon;
        [SerializeField] private Sprite criticalFailureIcon;

        [Header("Animation Settings")]
        [SerializeField] private float diceRollDuration = 2f;
        [SerializeField] private float diceAnimationSpeed = 0.1f;
        [SerializeField] private float panelTransitionDuration = 0.3f;

        [Header("Audio")]
        [SerializeField] private AudioSource audioSource;
        [SerializeField] private AudioClip diceRollSound;
        [SerializeField] private AudioClip successSound;
        [SerializeField] private AudioClip failureSound;

        // Current skill check data
        private List<SkillCheckOptionDTO> currentOptions;
        private SkillCheckOptionDTO selectedOption;
        private SkillCheckRequestDTO currentRequest;
        private SkillCheckResultDTO currentResult;
        private string currentContext;

        // UI State
        private bool isAnimating = false;
        private Coroutine diceAnimationCoroutine;

        // Events
        public event Action<SkillCheckResultDTO> OnSkillCheckCompleted;
        public event Action OnSkillCheckCancelled;

        private void Awake()
        {
            SetupEventListeners();
            HideAllTabs();
        }

        private void SetupEventListeners()
        {
            confirmButton.onClick.AddListener(ExecuteSkillCheck);
            backButton.onClick.AddListener(GoBackToSelection);
            closeButton.onClick.AddListener(CloseSkillCheck);
            retryButton.onClick.AddListener(RetrySkillCheck);

            // Subscribe to SkillCheckManager events
            SkillCheckManager.OnSkillCheckCompleted += HandleSkillCheckResult;
            SkillCheckManager.OnSkillCheckError += HandleSkillCheckError;
        }

        private void OnDestroy()
        {
            SkillCheckManager.OnSkillCheckCompleted -= HandleSkillCheckResult;
            SkillCheckManager.OnSkillCheckError -= HandleSkillCheckError;
        }

        #region Public Interface

        public void ShowSkillCheckOptions(List<SkillCheckOptionDTO> options, string context = "")
        {
            currentOptions = options;
            currentContext = context;
            
            skillCheckPanel.SetActive(true);
            ShowSelectionTab();
            PopulateSkillOptions();
            
            if (!string.IsNullOrEmpty(context))
            {
                contextText.text = context;
                contextText.gameObject.SetActive(true);
            }
            else
            {
                contextText.gameObject.SetActive(false);
            }
        }

        public void ShowEnvironmentalConditions(List<string> conditions)
        {
            ClearEnvironmentalBadges();

            foreach (var condition in conditions)
            {
                var badge = Instantiate(environmentalBadgePrefab, environmentalBadgesContainer);
                var badgeText = badge.GetComponentInChildren<TextMeshProUGUI>();
                if (badgeText != null)
                {
                    badgeText.text = FormatEnvironmentalCondition(condition);
                }

                // Color code badges based on condition type
                var badgeImage = badge.GetComponent<Image>();
                if (badgeImage != null)
                {
                    badgeImage.color = GetEnvironmentalConditionColor(condition);
                }
            }
        }

        public void Hide()
        {
            skillCheckPanel.SetActive(false);
            StopAllAnimations();
        }

        #endregion

        #region Tab Management

        private void HideAllTabs()
        {
            selectionTab.SetActive(false);
            confirmTab.SetActive(false);
            rollingTab.SetActive(false);
            resultTab.SetActive(false);
        }

        private void ShowSelectionTab()
        {
            if (isAnimating) return;
            
            StartCoroutine(TransitionToTab(selectionTab));
        }

        private void ShowConfirmTab()
        {
            if (isAnimating) return;
            
            PopulateConfirmationData();
            StartCoroutine(TransitionToTab(confirmTab));
        }

        private void ShowRollingTab()
        {
            if (isAnimating) return;
            
            StartCoroutine(TransitionToTab(rollingTab));
            StartDiceRollingAnimation();
        }

        private void ShowResultTab()
        {
            if (isAnimating) return;
            
            PopulateResultData();
            StartCoroutine(TransitionToTab(resultTab));
        }

        private IEnumerator TransitionToTab(GameObject targetTab)
        {
            isAnimating = true;

            // Fade out current tab
            var currentTab = GetCurrentActiveTab();
            if (currentTab != null)
            {
                yield return FadeOut(currentTab);
                currentTab.SetActive(false);
            }

            // Fade in target tab
            targetTab.SetActive(true);
            yield return FadeIn(targetTab);

            isAnimating = false;
        }

        private GameObject GetCurrentActiveTab()
        {
            if (selectionTab.activeInHierarchy) return selectionTab;
            if (confirmTab.activeInHierarchy) return confirmTab;
            if (rollingTab.activeInHierarchy) return rollingTab;
            if (resultTab.activeInHierarchy) return resultTab;
            return null;
        }

        private IEnumerator FadeOut(GameObject tab)
        {
            var canvasGroup = tab.GetComponent<CanvasGroup>();
            if (canvasGroup == null) canvasGroup = tab.AddComponent<CanvasGroup>();

            yield return canvasGroup.DOFade(0f, panelTransitionDuration).WaitForCompletion();
        }

        private IEnumerator FadeIn(GameObject tab)
        {
            var canvasGroup = tab.GetComponent<CanvasGroup>();
            if (canvasGroup == null) canvasGroup = tab.AddComponent<CanvasGroup>();

            canvasGroup.alpha = 0f;
            yield return canvasGroup.DOFade(1f, panelTransitionDuration).WaitForCompletion();
        }

        #endregion

        #region Selection Tab

        private void PopulateSkillOptions()
        {
            ClearSkillOptions();

            foreach (var option in currentOptions)
            {
                var optionUI = Instantiate(skillOptionPrefab, skillOptionsContainer);
                var skillButton = optionUI.GetComponent<Button>();
                var skillText = optionUI.GetComponentInChildren<TextMeshProUGUI>();

                if (skillText != null)
                {
                    skillText.text = $"{option.SkillName} (+{option.SkillModifier})";
                }

                if (skillButton != null)
                {
                    var optionCopy = option; // Capture for closure
                    skillButton.onClick.AddListener(() => SelectSkillOption(optionCopy));
                }

                // Add advantage/disadvantage indicator
                var statusIndicator = optionUI.transform.Find("StatusIndicator");
                if (statusIndicator != null)
                {
                    var statusText = statusIndicator.GetComponent<TextMeshProUGUI>();
                    if (statusText != null)
                    {
                        if (option.HasAdvantage)
                            statusText.text = "ADV";
                        else if (option.HasDisadvantage)
                            statusText.text = "DIS";
                        else
                            statusText.text = "";
                    }
                }
            }
        }

        private void SelectSkillOption(SkillCheckOptionDTO option)
        {
            selectedOption = option;
            ShowConfirmTab();
        }

        private void ClearSkillOptions()
        {
            foreach (Transform child in skillOptionsContainer)
            {
                Destroy(child.gameObject);
            }
        }

        private void ClearEnvironmentalBadges()
        {
            foreach (Transform child in environmentalBadgesContainer)
            {
                Destroy(child.gameObject);
            }
        }

        #endregion

        #region Confirm Tab

        private void PopulateConfirmationData()
        {
            if (selectedOption == null) return;

            selectedSkillText.text = selectedOption.SkillName;
            skillModifierText.text = $"Modifier: +{selectedOption.SkillModifier}";
            difficultyClassText.text = $"DC: {selectedOption.DifficultyClass}";

            string advantageStatus = "";
            if (selectedOption.HasAdvantage)
                advantageStatus = "Advantage";
            else if (selectedOption.HasDisadvantage)
                advantageStatus = "Disadvantage";
            else
                advantageStatus = "Normal";

            advantageText.text = $"Roll Type: {advantageStatus}";
        }

        private void GoBackToSelection()
        {
            selectedOption = null;
            ShowSelectionTab();
        }

        #endregion

        #region Rolling Tab

        private void StartDiceRollingAnimation()
        {
            rollingText.text = "Rolling dice...";
            progressBar.value = 0;

            if (diceParticles != null)
                diceParticles.Play();

            if (audioSource != null && diceRollSound != null)
                audioSource.PlayOneShot(diceRollSound);

            diceAnimationCoroutine = StartCoroutine(AnimateDiceRolling());
        }

        private IEnumerator AnimateDiceRolling()
        {
            float elapsed = 0f;
            
            while (elapsed < diceRollDuration)
            {
                // Animate dice faces
                foreach (var diceImage in diceImages)
                {
                    if (diceImage != null && diceFaceSprites.Length > 0)
                    {
                        var randomFace = UnityEngine.Random.Range(0, diceFaceSprites.Length);
                        diceImage.sprite = diceFaceSprites[randomFace];
                    }
                }

                // Update progress bar
                progressBar.value = elapsed / diceRollDuration;

                elapsed += diceAnimationSpeed;
                yield return new WaitForSeconds(diceAnimationSpeed);
            }

            progressBar.value = 1f;

            if (diceParticles != null)
                diceParticles.Stop();
        }

        #endregion

        #region Result Tab

        private void PopulateResultData()
        {
            if (currentResult == null) return;

            // Set dice to final result
            if (diceImages.Length > 0 && diceFaceSprites.Length >= currentResult.DiceRoll)
            {
                diceImages[0].sprite = diceFaceSprites[currentResult.DiceRoll - 1];
            }

            resultTitleText.text = currentResult.Success ? "Success!" : "Failure";
            resultDescriptionText.text = currentResult.ResultDescription ?? "";
            diceRollText.text = $"Dice Roll: {currentResult.DiceRoll}";
            totalRollText.text = $"Total: {currentResult.TotalRoll}";
            outcomeText.text = $"vs DC {currentResult.DifficultyClass}";

            // Set result icon and color
            if (currentResult.IsCriticalSuccess)
            {
                resultIcon.sprite = criticalSuccessIcon;
                resultTitleText.text = "Critical Success!";
                resultTitleText.color = Color.yellow;
            }
            else if (currentResult.IsCriticalFailure)
            {
                resultIcon.sprite = criticalFailureIcon;
                resultTitleText.text = "Critical Failure!";
                resultTitleText.color = Color.red;
            }
            else if (currentResult.Success)
            {
                resultIcon.sprite = successIcon;
                resultTitleText.color = Color.green;
            }
            else
            {
                resultIcon.sprite = failureIcon;
                resultTitleText.color = Color.red;
            }

            // Play appropriate sound
            if (audioSource != null)
            {
                if (currentResult.Success && successSound != null)
                    audioSource.PlayOneShot(successSound);
                else if (!currentResult.Success && failureSound != null)
                    audioSource.PlayOneShot(failureSound);
            }

            // Show retry button only for certain skill types
            retryButton.gameObject.SetActive(CanRetrySkillCheck(currentResult.SkillName));
        }

        private bool CanRetrySkillCheck(string skillName)
        {
            // Some skills can be retried, others cannot (like one-time perception checks)
            var retryableSkills = new HashSet<string> { "Investigation", "Athletics", "Acrobatics", "Sleight of Hand" };
            return retryableSkills.Contains(skillName);
        }

        #endregion

        #region Skill Check Execution

        private void ExecuteSkillCheck()
        {
            if (selectedOption == null) return;

            // Build request DTO
            currentRequest = new SkillCheckRequestDTO
            {
                CharacterId = selectedOption.CharacterId,
                SkillName = selectedOption.SkillName,
                DifficultyClass = selectedOption.DifficultyClass,
                SkillModifier = selectedOption.SkillModifier,
                HasAdvantage = selectedOption.HasAdvantage,
                HasDisadvantage = selectedOption.HasDisadvantage,
                EnvironmentalConditions = selectedOption.EnvironmentalConditions ?? new List<string>(),
                Context = currentContext
            };

            ShowRollingTab();

            // Execute skill check through manager
            SkillCheckManager.ExecuteSkillCheck(currentRequest);
        }

        private void HandleSkillCheckResult(SkillCheckResultDTO result)
        {
            currentResult = result;
            
            // Wait for dice animation to complete
            StartCoroutine(WaitForAnimationThenShowResult());
        }

        private IEnumerator WaitForAnimationThenShowResult()
        {
            // Wait for dice animation to finish
            if (diceAnimationCoroutine != null)
            {
                yield return diceAnimationCoroutine;
            }

            // Small delay for dramatic effect
            yield return new WaitForSeconds(0.5f);

            ShowResultTab();
        }

        private void HandleSkillCheckError(string error)
        {
            Debug.LogError($"Skill check error: {error}");
            
            // Show error in result tab
            currentResult = new SkillCheckResultDTO
            {
                Success = false,
                ResultDescription = $"Error: {error}",
                SkillName = selectedOption?.SkillName ?? "Unknown"
            };

            ShowResultTab();
        }

        private void RetrySkillCheck()
        {
            if (currentRequest != null)
            {
                ShowRollingTab();
                SkillCheckManager.ExecuteSkillCheck(currentRequest);
            }
        }

        #endregion

        #region UI Actions

        private void CloseSkillCheck()
        {
            OnSkillCheckCompleted?.Invoke(currentResult);
            Hide();
        }

        private void StopAllAnimations()
        {
            if (diceAnimationCoroutine != null)
            {
                StopCoroutine(diceAnimationCoroutine);
                diceAnimationCoroutine = null;
            }

            if (diceParticles != null)
                diceParticles.Stop();

            isAnimating = false;
        }

        #endregion

        #region Utility Methods

        private string FormatEnvironmentalCondition(string condition)
        {
            // Convert snake_case to readable format
            return condition.Replace("_", " ").ToTitleCase();
        }

        private Color GetEnvironmentalConditionColor(string condition)
        {
            // Color code environmental conditions
            if (condition.Contains("advantage") || condition.Contains("bonus"))
                return Color.green;
            else if (condition.Contains("disadvantage") || condition.Contains("penalty"))
                return Color.red;
            else
                return Color.gray;
        }

        #endregion
    }

    // Extension method for string formatting
    public static class StringExtensions
    {
        public static string ToTitleCase(this string input)
        {
            if (string.IsNullOrEmpty(input))
                return input;

            var words = input.Split(' ');
            for (int i = 0; i < words.Length; i++)
            {
                if (words[i].Length > 0)
                {
                    words[i] = char.ToUpper(words[i][0]) + words[i].Substring(1).ToLower();
                }
            }
            return string.Join(" ", words);
        }
    }
} 