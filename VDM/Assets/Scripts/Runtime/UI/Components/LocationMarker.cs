using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using TMPro;
using VDM.UI.Core;
using VDM.Systems.Region.Models;
using System;
using VDM.DTOs.Game.Character;

namespace VDM.UI.Systems.Region
{
    /// <summary>
    /// UI component for location markers on the region map
    /// </summary>
    public class LocationMarker : MonoBehaviour, IPointerClickHandler, IPointerEnterHandler, IPointerExitHandler
    {
        [Header("Visual Components")]
        [SerializeField] private Image markerIcon;
        [SerializeField] private TextMeshProUGUI locationNameText;
        [SerializeField] private GameObject tooltip;
        [SerializeField] private TextMeshProUGUI tooltipText;
        [SerializeField] private CanvasGroup canvasGroup;
        
        [Header("Marker Settings")]
        [SerializeField] private Color defaultColor = Color.white;
        [SerializeField] private Color hoverColor = Color.yellow;
        [SerializeField] private Color selectedColor = Color.green;
        [SerializeField] private float hoverScale = 1.2f;
        [SerializeField] private float animationDuration = 0.2f;
        
        [Header("Location Type Icons")]
        [SerializeField] private Sprite cityIcon;
        [SerializeField] private Sprite townIcon;
        [SerializeField] private Sprite villageIcon;
        [SerializeField] private Sprite dungeonIcon;
        [SerializeField] private Sprite ruinsIcon;
        [SerializeField] private Sprite landmarkIcon;
        [SerializeField] private Sprite resourceIcon;
        [SerializeField] private Sprite questIcon;
        
        private LocationModel location;
        private Action<LocationModel> onLocationSelected;
        private bool isSelected = false;
        private Vector3 originalScale;
        private Coroutine animationCoroutine;
        
        private void Awake()
        {
            originalScale = transform.localScale;
            
            if (tooltip != null)
                tooltip.SetActive(false);
                
            if (canvasGroup == null)
                canvasGroup = GetComponent<CanvasGroup>();
        }
        
        /// <summary>
        /// Initialize the location marker with location data and callback
        /// </summary>
        public void Initialize(LocationModel locationData, Action<LocationModel> selectionCallback)
        {
            location = locationData;
            onLocationSelected = selectionCallback;
            
            UpdateVisuals();
            UpdateAccessibility();
        }
        
        /// <summary>
        /// Update the visual representation of the marker
        /// </summary>
        private void UpdateVisuals()
        {
            if (location == null) return;
            
            // Set location name
            if (locationNameText != null)
                locationNameText.text = location.Name;
            
            // Set appropriate icon based on location type
            if (markerIcon != null)
            {
                markerIcon.sprite = GetLocationTypeIcon(location.Type);
                markerIcon.color = GetLocationStatusColor();
            }
            
            // Update tooltip
            if (tooltipText != null)
            {
                tooltipText.text = $"{location.Name}\n{location.Type}\n{location.Description}";
            }
        }
        
        /// <summary>
        /// Update marker accessibility based on location state
        /// </summary>
        private void UpdateAccessibility()
        {
            if (location == null || canvasGroup == null) return;
            
            // Adjust alpha based on accessibility
            canvasGroup.alpha = location.IsAccessible ? 1f : 0.6f;
            canvasGroup.interactable = location.IsDiscovered;
        }
        
        /// <summary>
        /// Get the appropriate icon for the location type
        /// </summary>
        private Sprite GetLocationTypeIcon(LocationType locationType)
        {
            return locationType switch
            {
                LocationType.City => cityIcon,
                LocationType.Town => townIcon,
                LocationType.Village => villageIcon,
                LocationType.Dungeon => dungeonIcon,
                LocationType.Ruins => ruinsIcon,
                LocationType.Landmark => landmarkIcon,
                LocationType.Resource => resourceIcon,
                LocationType.Quest => questIcon,
                _ => landmarkIcon // Default fallback
            };
        }
        
        /// <summary>
        /// Get color based on location status
        /// </summary>
        private Color GetLocationStatusColor()
        {
            if (isSelected)
                return selectedColor;
            
            if (!location.IsDiscovered)
                return Color.gray;
            
            if (!location.IsAccessible)
                return Color.red;
            
            return defaultColor;
        }
        
        /// <summary>
        /// Set the selected state of this marker
        /// </summary>
        public void SetSelected(bool selected)
        {
            isSelected = selected;
            
            if (markerIcon != null)
                markerIcon.color = GetLocationStatusColor();
        }
        
        /// <summary>
        /// Animate the marker scale
        /// </summary>
        private void AnimateScale(Vector3 targetScale)
        {
            if (animationCoroutine != null)
                StopCoroutine(animationCoroutine);
            
            animationCoroutine = StartCoroutine(AnimateScaleCoroutine(targetScale));
        }
        
        private System.Collections.IEnumerator AnimateScaleCoroutine(Vector3 targetScale)
        {
            Vector3 startScale = transform.localScale;
            float elapsed = 0f;
            
            while (elapsed < animationDuration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / animationDuration;
                
                // Use smooth step for better animation feel
                t = t * t * (3f - 2f * t);
                
                transform.localScale = Vector3.Lerp(startScale, targetScale, t);
                yield return null;
            }
            
            transform.localScale = targetScale;
            animationCoroutine = null;
        }
        
        /// <summary>
        /// Show visual feedback for interaction
        /// </summary>
        private void ShowHoverEffect()
        {
            if (markerIcon != null)
                markerIcon.color = hoverColor;
            
            AnimateScale(originalScale * hoverScale);
        }
        
        /// <summary>
        /// Hide visual feedback for interaction
        /// </summary>
        private void HideHoverEffect()
        {
            if (markerIcon != null)
                markerIcon.color = GetLocationStatusColor();
            
            AnimateScale(originalScale);
        }
        
        #region Event Handlers
        
        public void OnPointerClick(PointerEventData eventData)
        {
            if (location != null && location.IsDiscovered)
            {
                onLocationSelected?.Invoke(location);
            }
        }
        
        public void OnPointerEnter(PointerEventData eventData)
        {
            if (location != null && location.IsDiscovered)
            {
                ShowHoverEffect();
                
                if (tooltip != null)
                {
                    tooltip.SetActive(true);
                    // Position tooltip relative to mouse
                    Vector3 mousePos = Input.mousePosition;
                    tooltip.transform.position = mousePos + Vector3.up * 50f;
                }
            }
        }
        
        public void OnPointerExit(PointerEventData eventData)
        {
            HideHoverEffect();
            
            if (tooltip != null)
                tooltip.SetActive(false);
        }
        
        #endregion
        
        #region Public Methods
        
        /// <summary>
        /// Update the marker when location data changes
        /// </summary>
        public void RefreshMarker()
        {
            UpdateVisuals();
            UpdateAccessibility();
        }
        
        /// <summary>
        /// Get the location data associated with this marker
        /// </summary>
        public LocationModel GetLocation()
        {
            return location;
        }
        
        /// <summary>
        /// Check if this marker represents the specified location
        /// </summary>
        public bool RepresentsLocation(string locationId)
        {
            return location?.Id == locationId;
        }
        
        #endregion
    }
} 