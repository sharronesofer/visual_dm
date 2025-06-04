using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.UI.Core;
using VDM.Systems.Region.Services;
using System.Collections.Generic;
using System.Linq;
using VDM.DTOs.Game.Character;

namespace VDM.UI.Systems.Region
{
    /// <summary>
    /// UI panel for displaying region maps and location information
    /// </summary>
    public class RegionMapPanel : BaseUIPanel
    {
        [Header("Map Components")]
        [SerializeField] private RawImage mapImage;
        [SerializeField] private Transform locationMarkersParent;
        [SerializeField] private GameObject locationMarkerPrefab;
        
        [Header("Region Info")]
        [SerializeField] private TextMeshProUGUI regionNameText;
        [SerializeField] private TextMeshProUGUI regionDescriptionText;
        [SerializeField] private TextMeshProUGUI climateText;
        [SerializeField] private TextMeshProUGUI dangerLevelText;
        
        [Header("Location Details")]
        [SerializeField] private GameObject locationDetailsPanel;
        [SerializeField] private TextMeshProUGUI locationNameText;
        [SerializeField] private TextMeshProUGUI locationTypeText;
        [SerializeField] private TextMeshProUGUI locationDescriptionText;
        [SerializeField] private Button travelButton;
        [SerializeField] private Button exploreButton;
        
        [Header("Navigation")]
        [SerializeField] private Button zoomInButton;
        [SerializeField] private Button zoomOutButton;
        [SerializeField] private Button centerMapButton;
        [SerializeField] private Slider zoomSlider;
        
        private RegionService regionService;
        private VDM.Systems.Region.Models.RegionModel currentRegion;
        private LocationModel selectedLocation;
        private List<GameObject> locationMarkers = new List<GameObject>();
        private Vector2 mapOffset = Vector2.zero;
        private float zoomLevel = 1f;
        
        private const float MIN_ZOOM = 0.5f;
        private const float MAX_ZOOM = 3f;
        
        protected override void Awake()
        {
            base.Awake();
            
            // Get service references
            regionService = FindObjectOfType<RegionService>();
            
            // Setup UI event handlers
            if (travelButton != null)
                travelButton.onClick.AddListener(OnTravelToLocation);
            
            if (exploreButton != null)
                exploreButton.onClick.AddListener(OnExploreLocation);
            
            if (zoomOutButton != null)
                zoomOutButton.onClick.AddListener(() => SetZoom(zoomLevel - 0.5f));
            
            if (centerMapButton != null)
                centerMapButton.onClick.AddListener(CenterMap);
            
            if (zoomSlider != null)
            {
                zoomSlider.minValue = MIN_ZOOM;
                zoomSlider.maxValue = MAX_ZOOM;
                zoomSlider.value = zoomLevel;
                zoomSlider.onValueChanged.AddListener(SetZoom);
            }
        }
        
        private void OnEnable()
        {
            // Subscribe to region events when panel becomes active
            if (regionService != null)
            {
                regionService.OnLocationDiscovered += OnLocationDiscovered;
                regionService.OnLocationUpdated += OnLocationUpdated;
                regionService.OnRegionChanged += OnRegionChanged;
            }
        }
        
        private void OnDisable()
        {
            // Unsubscribe from region events when panel becomes inactive
            if (regionService != null)
            {
                regionService.OnLocationDiscovered -= OnLocationDiscovered;
                regionService.OnLocationUpdated -= OnLocationUpdated;
                regionService.OnRegionChanged -= OnRegionChanged;
            }
        }
        
        /// <summary>
        /// Display a specific region on the map
        /// </summary>
        public void ShowRegion(VDM.Systems.Region.Models.RegionModel region)
        {
            currentRegion = region;
            UpdateRegionInfo();
            LoadMapTexture();
            CreateLocationMarkers();
            CenterMap();
            
            // Hide location details initially
            if (locationDetailsPanel != null)
                locationDetailsPanel.SetActive(false);
        }
        
        /// <summary>
        /// Update region information display
        /// </summary>
        private void UpdateRegionInfo()
        {
            if (currentRegion == null) return;
            
            if (regionNameText != null)
                regionNameText.text = currentRegion.Name;
            if (regionDescriptionText != null)
                regionDescriptionText.text = currentRegion.Description;
            if (climateText != null)
                climateText.text = $"Climate: {currentRegion.Climate}";
            if (dangerLevelText != null)
            {
                dangerLevelText.text = $"Danger Level: {currentRegion.DangerLevel}";
                dangerLevelText.color = GetDangerLevelColor(currentRegion.DangerLevel);
            }
        }
        
        /// <summary>
        /// Load and display the map texture for the current region
        /// </summary>
        private void LoadMapTexture()
        {
            if (currentRegion == null || mapImage == null) return;
            
            // Load map texture from resources or addressables
            string mapPath = $"Maps/Regions/{currentRegion.Id}";
            Texture2D mapTexture = Resources.Load<Texture2D>(mapPath);
            
            if (mapTexture != null)
            {
                mapImage.texture = mapTexture;
            }
            else
            {
                Debug.LogWarning($"Map texture not found for region: {currentRegion.Name} at path: {mapPath}");
                // Use placeholder texture
                mapImage.texture = Resources.Load<Texture2D>("Maps/placeholder_map");
            }
        }
        
        /// <summary>
        /// Create location markers on the map
        /// </summary>
        private void CreateLocationMarkers()
        {
            // Clear existing markers
            ClearLocationMarkers();
            
            if (currentRegion?.Locations == null || locationMarkersParent == null || locationMarkerPrefab == null)
                return;
            
            foreach (var location in currentRegion.Locations.Where(l => l.IsDiscovered))
            {
                GameObject marker = Instantiate(locationMarkerPrefab, locationMarkersParent);
                LocationMarker markerComponent = marker.GetComponent<LocationMarker>();
                
                if (markerComponent != null)
                {
                    markerComponent.Initialize(location, OnLocationSelected);
                    // Position marker based on location coordinates
                    Vector2 mapPosition = WorldToMapPosition(location.WorldPosition);
                    marker.transform.localPosition = mapPosition;
                }
                
                locationMarkers.Add(marker);
            }
        }
        
        /// <summary>
        /// Clear all location markers from the map
        /// </summary>
        private void ClearLocationMarkers()
        {
            foreach (var marker in locationMarkers)
            {
                if (marker != null)
                    DestroyImmediate(marker);
            }
            locationMarkers.Clear();
        }
        
        /// <summary>
        /// Convert world coordinates to map UI coordinates
        /// </summary>
        private Vector2 WorldToMapPosition(Vector2 worldPos)
        {
            if (mapImage == null) return Vector2.zero;
            
            RectTransform mapRect = mapImage.rectTransform;
            Vector2 mapSize = mapRect.sizeDelta;
            
            // Normalize world position to map bounds
            Vector2 normalizedPos = new Vector2(
                (worldPos.x - currentRegion.Bounds.min.x) / currentRegion.Bounds.size.x,
                (worldPos.y - currentRegion.Bounds.min.y) / currentRegion.Bounds.size.y
            );
            
            // Convert to map UI coordinates
            return new Vector2(
                (normalizedPos.x - 0.5f) * mapSize.x,
                (normalizedPos.y - 0.5f) * mapSize.y
            );
        }
        
        /// <summary>
        /// Handle location marker selection
        /// </summary>
        private void OnLocationSelected(LocationModel location)
        {
            selectedLocation = location;
            ShowLocationDetails(location);
        }
        
        /// <summary>
        /// Display details for the selected location
        /// </summary>
        private void ShowLocationDetails(LocationModel location)
        {
            if (locationDetailsPanel == null) return;
            
            locationDetailsPanel.SetActive(true);
            
            if (locationNameText != null)
                locationNameText.text = location.Name;
            if (locationTypeText != null)
                locationTypeText.text = location.Type.ToString();
            if (locationDescriptionText != null)
                locationDescriptionText.text = location.Description;
            
            // Update button states
            if (travelButton != null)
                travelButton.interactable = location.IsAccessible;
            if (exploreButton != null)
                exploreButton.interactable = location.IsDiscovered;
        }
        
        /// <summary>
        /// Set map zoom level
        /// </summary>
        private void SetZoom(float zoom)
        {
            zoomLevel = Mathf.Clamp(zoom, MIN_ZOOM, MAX_ZOOM);
            
            if (mapImage != null)
            {
                mapImage.transform.localScale = Vector3.one * zoomLevel;
            }
            
            if (zoomSlider != null && !Mathf.Approximately(zoomSlider.value, zoomLevel))
            {
                zoomSlider.SetValueWithoutNotify(zoomLevel);
            }
        }
        
        /// <summary>
        /// Center the map view
        /// </summary>
        private void CenterMap()
        {
            mapOffset = Vector2.zero;
            if (mapImage != null)
            {
                mapImage.transform.localPosition = Vector3.zero;
            }
        }
        
        /// <summary>
        /// Get color for danger level display
        /// </summary>
        private Color GetDangerLevelColor(int dangerLevel)
        {
            return dangerLevel switch
            {
                <= 2 => Color.green,
                <= 4 => Color.yellow,
                <= 6 => new Color(1f, 0.5f, 0f), // Orange
                <= 8 => Color.red,
                _ => Color.magenta // Extreme danger
            };
        }
        
        #region Event Handlers
        
        private void OnRegionChanged(VDM.Systems.Region.Models.RegionModel newRegion)
        {
            ShowRegion(newRegion);
        }
        
        private void OnLocationDiscovered(LocationModel location)
        {
            if (location.RegionId == currentRegion?.Id)
            {
                CreateLocationMarkers(); // Refresh markers to include new location
            }
        }
        
        private void OnLocationUpdated(LocationModel location)
        {
            // Handle location update
        }
        
        private void OnTravelToLocation()
        {
            if (selectedLocation != null && regionService != null)
            {
                regionService.TravelToLocation(selectedLocation.Id);
                Close();
            }
        }
        
        private void OnExploreLocation()
        {
            if (selectedLocation != null && regionService != null)
            {
                regionService.ExploreLocation(selectedLocation.Id);
                // Keep panel open to show exploration results
            }
        }
        
        #endregion
    }
} 