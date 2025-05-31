using System;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.Systems.Motifs.Models;

namespace VDM.Systems.Motifs.Ui
{
    /// <summary>
    /// UI component for displaying individual motifs in a list.
    /// Handles motif selection and provides visual feedback for motif states.
    /// </summary>
    public class MotifListItem : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private Button _selectButton;
        [SerializeField] private TextMeshProUGUI _nameText;
        [SerializeField] private TextMeshProUGUI _categoryText;
        [SerializeField] private TextMeshProUGUI _scopeText;
        [SerializeField] private TextMeshProUGUI _lifecycleText;
        [SerializeField] private TextMeshProUGUI _intensityText;
        [SerializeField] private TextMeshProUGUI _descriptionText;
        [SerializeField] private Image _categoryColorIndicator;
        [SerializeField] private Image _lifecycleIcon;
        [SerializeField] private Image _scopeIcon;
        [SerializeField] private GameObject _activeIndicator;
        [SerializeField] private Slider _intensitySlider;

        [Header("Visual Settings")]
        [SerializeField] private Color _selectedColor = Color.yellow;
        [SerializeField] private Color _normalColor = Color.white;
        [SerializeField] private Color _inactiveColor = Color.gray;

        [Header("Category Colors")]
        [SerializeField] private Color _ascensionColor = new Color(1f, 0.8f, 0.2f); // Gold
        [SerializeField] private Color _betrayalColor = new Color(0.8f, 0.2f, 0.2f); // Dark Red
        [SerializeField] private Color _chaosColor = new Color(0.6f, 0.2f, 0.8f); // Purple
        [SerializeField] private Color _deathColor = new Color(0.1f, 0.1f, 0.1f); // Black
        [SerializeField] private Color _hopeColor = new Color(0.2f, 0.8f, 0.4f); // Green
        [SerializeField] private Color _powerColor = new Color(0.8f, 0.4f, 0.2f); // Orange
        [SerializeField] private Color _defaultColor = new Color(0.5f, 0.5f, 0.5f); // Gray

        private Motif _motif;
        private Action<Motif> _onSelected;
        private bool _isSelected = false;

        #region Initialization

        /// <summary>
        /// Initialize the list item with motif data and selection callback
        /// </summary>
        public void Initialize(Motif motif, Action<Motif> onSelected)
        {
            _motif = motif;
            _onSelected = onSelected;
            
            UpdateDisplay();
            SetupEventListeners();
        }

        private void SetupEventListeners()
        {
            if (_selectButton != null)
            {
                _selectButton.onClick.RemoveAllListeners();
                _selectButton.onClick.AddListener(OnItemClicked);
            }
        }

        #endregion

        #region Display Updates

        private void UpdateDisplay()
        {
            if (_motif == null) return;

            // Basic information
            UpdateTextSafely(_nameText, _motif.name);
            UpdateTextSafely(_categoryText, _motif.category.ToString());
            UpdateTextSafely(_scopeText, _motif.scope.ToString());
            UpdateTextSafely(_lifecycleText, _motif.lifecycle.ToString());
            UpdateTextSafely(_intensityText, $"{_motif.intensity}/10");
            
            // Description (truncated if necessary)
            if (_descriptionText != null)
            {
                string description = _motif.description;
                if (description.Length > 100)
                {
                    description = description.Substring(0, 97) + "...";
                }
                _descriptionText.text = description;
            }

            // Visual indicators
            UpdateCategoryColorIndicator();
            UpdateLifecycleIcon();
            UpdateScopeIcon();
            UpdateActiveIndicator();
            UpdateIntensitySlider();
            UpdateItemColors();
        }

        private void UpdateTextSafely(TextMeshProUGUI textComponent, string text)
        {
            if (textComponent != null)
            {
                textComponent.text = text;
            }
        }

        private void UpdateCategoryColorIndicator()
        {
            if (_categoryColorIndicator == null) return;
            
            Color categoryColor = GetCategoryColor(_motif.category);
            _categoryColorIndicator.color = categoryColor;
        }

        private void UpdateLifecycleIcon()
        {
            if (_lifecycleIcon == null) return;
            
            // Set icon color based on lifecycle
            Color lifecycleColor = _motif.lifecycle switch
            {
                MotifLifecycle.Dormant => new Color(0.3f, 0.3f, 0.3f), // Dark gray
                MotifLifecycle.Emerging => new Color(0.8f, 0.8f, 0.2f), // Yellow
                MotifLifecycle.Stable => new Color(0.2f, 0.8f, 0.2f), // Green
                MotifLifecycle.Waning => new Color(0.8f, 0.5f, 0.2f), // Orange
                MotifLifecycle.Fading => new Color(0.8f, 0.2f, 0.2f), // Red
                _ => Color.gray
            };
            
            _lifecycleIcon.color = lifecycleColor;
        }

        private void UpdateScopeIcon()
        {
            if (_scopeIcon == null) return;
            
            // Set icon color based on scope
            Color scopeColor = _motif.scope switch
            {
                MotifScope.Global => new Color(0.2f, 0.4f, 0.8f), // Blue
                MotifScope.Regional => new Color(0.6f, 0.4f, 0.8f), // Purple
                MotifScope.Local => new Color(0.8f, 0.6f, 0.2f), // Yellow-orange
                _ => Color.gray
            };
            
            _scopeIcon.color = scopeColor;
        }

        private void UpdateActiveIndicator()
        {
            if (_activeIndicator == null) return;
            
            bool isActive = _motif.IsActive();
            _activeIndicator.SetActive(isActive);
        }

        private void UpdateIntensitySlider()
        {
            if (_intensitySlider == null) return;
            
            _intensitySlider.value = _motif.intensity / 10f;
            
            // Color the slider based on intensity
            var fillImage = _intensitySlider.fillRect?.GetComponent<Image>();
            if (fillImage != null)
            {
                fillImage.color = Color.Lerp(Color.green, Color.red, _motif.intensity / 10f);
            }
        }

        private void UpdateItemColors()
        {
            Color targetColor;
            
            if (_isSelected)
            {
                targetColor = _selectedColor;
            }
            else if (!_motif.IsActive())
            {
                targetColor = _inactiveColor;
            }
            else
            {
                targetColor = _normalColor;
            }
            
            // Apply color to the button or background
            if (_selectButton != null)
            {
                var colors = _selectButton.colors;
                colors.normalColor = targetColor;
                colors.selectedColor = targetColor;
                _selectButton.colors = colors;
            }
        }

        #endregion

        #region Color Management

        private Color GetCategoryColor(MotifCategory category)
        {
            return category switch
            {
                MotifCategory.Ascension => _ascensionColor,
                MotifCategory.Betrayal => _betrayalColor,
                MotifCategory.Chaos => _chaosColor,
                MotifCategory.Death => _deathColor,
                MotifCategory.Hope => _hopeColor,
                MotifCategory.Power => _powerColor,
                MotifCategory.Control => _powerColor,
                MotifCategory.Fear => _betrayalColor,
                MotifCategory.Madness => _chaosColor,
                MotifCategory.Peace => _hopeColor,
                MotifCategory.Shadow => _deathColor,
                MotifCategory.Truth => _ascensionColor,
                _ => _defaultColor
            };
        }

        #endregion

        #region Event Handlers

        private void OnItemClicked()
        {
            _onSelected?.Invoke(_motif);
        }

        #endregion

        #region Public API

        /// <summary>
        /// Set the selection state of this item
        /// </summary>
        public void SetSelected(bool selected)
        {
            _isSelected = selected;
            UpdateItemColors();
        }

        /// <summary>
        /// Get the motif associated with this list item
        /// </summary>
        public Motif GetMotif()
        {
            return _motif;
        }

        /// <summary>
        /// Update the display with current motif data
        /// </summary>
        public void RefreshDisplay()
        {
            UpdateDisplay();
        }

        /// <summary>
        /// Check if this item represents the given motif
        /// </summary>
        public bool RepresentsMotif(string motifId)
        {
            return _motif?.id == motifId;
        }

        /// <summary>
        /// Highlight the item temporarily (e.g., for search results)
        /// </summary>
        public void HighlightTemporarily(float duration = 2f)
        {
            StartCoroutine(HighlightCoroutine(duration));
        }

        private System.Collections.IEnumerator HighlightCoroutine(float duration)
        {
            Color originalColor = _normalColor;
            Color highlightColor = Color.cyan;
            
            // Fade to highlight
            float elapsed = 0f;
            float fadeTime = 0.3f;
            
            while (elapsed < fadeTime)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / fadeTime;
                
                if (_selectButton != null)
                {
                    var colors = _selectButton.colors;
                    colors.normalColor = Color.Lerp(originalColor, highlightColor, t);
                    _selectButton.colors = colors;
                }
                
                yield return null;
            }
            
            // Wait
            yield return new WaitForSeconds(duration - (fadeTime * 2));
            
            // Fade back
            elapsed = 0f;
            while (elapsed < fadeTime)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / fadeTime;
                
                if (_selectButton != null)
                {
                    var colors = _selectButton.colors;
                    colors.normalColor = Color.Lerp(highlightColor, originalColor, t);
                    _selectButton.colors = colors;
                }
                
                yield return null;
            }
            
            // Restore original state
            UpdateItemColors();
        }

        #endregion

        #region Tooltip Support

        /// <summary>
        /// Get tooltip text for this motif
        /// </summary>
        public string GetTooltipText()
        {
            if (_motif == null) return "";
            
            string tooltip = $"<b>{_motif.name}</b>\n";
            tooltip += $"Category: {_motif.category}\n";
            tooltip += $"Scope: {_motif.scope}\n";
            tooltip += $"Lifecycle: {_motif.lifecycle}\n";
            tooltip += $"Intensity: {_motif.intensity}/10\n";
            tooltip += $"Duration: {_motif.durationDays} days\n";
            
            if (_motif.effects != null && _motif.effects.Count > 0)
            {
                tooltip += $"Effects: {_motif.effects.Count}\n";
            }
            
            tooltip += $"\n{_motif.description}";
            
            return tooltip;
        }

        #endregion

        #region Animation Support

        /// <summary>
        /// Animate the item appearing
        /// </summary>
        public void AnimateAppear()
        {
            transform.localScale = Vector3.zero;
            LeanTween.scale(gameObject, Vector3.one, 0.3f).setEaseOutBack();
        }

        /// <summary>
        /// Animate the item disappearing
        /// </summary>
        public void AnimateDisappear(System.Action onComplete = null)
        {
            LeanTween.scale(gameObject, Vector3.zero, 0.2f)
                .setEaseInBack()
                .setOnComplete(() => onComplete?.Invoke());
        }

        #endregion
    }
} 