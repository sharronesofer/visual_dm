using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VDM.UI.Core;
using VDM.Systems.Region.Models;
using VDM.Systems.Worldgeneration.Models;
using VDM.Systems.Region.Services;
using System.Collections.Generic;
using System.Linq;

namespace VDM.UI.Systems.World
{
    /// <summary>
    /// UI panel for world map display and region navigation
    /// </summary>
    public class WorldMapPanel : BaseUIPanel
    {
        [Header("Map Display")]
        [SerializeField] private RawImage worldMapImage;
        [SerializeField] private Transform regionMarkersParent;
        [SerializeField] private GameObject regionMarkerPrefab;
        [SerializeField] private ScrollRect mapScrollRect;
        
        [Header("Map Controls")]
        [SerializeField] private Button zoomInButton;
        [SerializeField] private Button zoomOutButton;
        [SerializeField] private Button centerMapButton;
        [SerializeField] private Slider zoomSlider;
        [SerializeField] private Button fullscreenButton;
        
        [Header("Region Info")]
        [SerializeField] private GameObject regionInfoPanel;
        [SerializeField] private TextMeshProUGUI regionNameText;
        [SerializeField] private TextMeshProUGUI regionDescriptionText;
        [SerializeField] private TextMeshProUGUI regionLevelText;
        [SerializeField] private TextMeshProUGUI regionClimateText;
        [SerializeField] private TextMeshProUGUI regionDangerText;
        [SerializeField] private Image regionPreviewImage;
        
        [Header("Travel Options")]
        [SerializeField] private Button travelButton;
        [SerializeField] private Button exploreButton;
        [SerializeField] private Button fastTravelButton;
        [SerializeField] private TextMeshProUGUI travelTimeText;
        [SerializeField] private TextMeshProUGUI travelCostText;
        
        [Header("Legend")]
        [SerializeField] private GameObject legendPanel;
        [SerializeField] private Button toggleLegendButton;
        [SerializeField] private Transform legendEntriesParent;
        [SerializeField] private GameObject legendEntryPrefab;
        
        [Header("Player Location")]
        [SerializeField] private GameObject playerMarker;
        [SerializeField] private Image playerLocationIndicator;
        [SerializeField] private TextMeshProUGUI currentLocationText;
        
        [Header("Filters")]
        [SerializeField] private Toggle showDiscoveredToggle;
        [SerializeField] private Toggle showUndiscoveredToggle;
        [SerializeField] private Toggle showQuestLocationsToggle;
        [SerializeField] private Toggle showDangerousAreasToggle;
        [SerializeField] private TMP_Dropdown regionTypeFilter;
        
        private WorldService worldService;
        private WorldModel currentWorld;
        private RegionModel selectedRegion;
        private RegionModel currentPlayerRegion;
        private List<GameObject> regionMarkers = new List<GameObject>();
        private List<GameObject> legendEntries = new List<GameObject>();
        
        private float zoomLevel = 1f;
        private Vector2 mapOffset = Vector2.zero;
        private const float MIN_ZOOM = 0.3f;
        private const float MAX_ZOOM = 2f;
        
        protected override void Awake()
        {
            base.Awake();
            worldService = FindObjectOfType<WorldService>();
            
            // Setup map controls
            if (zoomInButton != null)
                zoomInButton.onClick.AddListener(() => SetZoom(zoomLevel + 0.2f));
            if (zoomOutButton != null)
                zoomOutButton.onClick.AddListener(() => SetZoom(zoomLevel - 0.2f));
            if (centerMapButton != null)
                centerMapButton.onClick.AddListener(CenterOnPlayerLocation);
            if (zoomSlider != null)
                zoomSlider.onValueChanged.AddListener(SetZoom);
            if (fullscreenButton != null)
                fullscreenButton.onClick.AddListener(ToggleFullscreen);
            
            // Setup travel buttons
            if (travelButton != null)
                travelButton.onClick.AddListener(TravelToSelectedRegion);
            if (exploreButton != null)
                exploreButton.onClick.AddListener(ExploreSelectedRegion);
            if (fastTravelButton != null)
                fastTravelButton.onClick.AddListener(FastTravelToSelectedRegion);
            
            // Setup UI toggles
            if (toggleLegendButton != null)
                toggleLegendButton.onClick.AddListener(ToggleLegend);
            if (showDiscoveredToggle != null)
                showDiscoveredToggle.onValueChanged.AddListener(OnFilterChanged);
            if (showUndiscoveredToggle != null)
                showUndiscoveredToggle.onValueChanged.AddListener(OnFilterChanged);
            if (showQuestLocationsToggle != null)
                showQuestLocationsToggle.onValueChanged.AddListener(OnFilterChanged);
            if (showDangerousAreasToggle != null)
                showDangerousAreasToggle.onValueChanged.AddListener(OnFilterChanged);
            if (regionTypeFilter != null)
                regionTypeFilter.onValueChanged.AddListener(OnRegionTypeFilterChanged);
        }
        
        protected override void OnEnable()
        {
            base.OnEnable();
            if (worldService != null)
            {
                worldService.OnWorldChanged += OnWorldChanged;
                worldService.OnRegionDiscovered += OnRegionDiscovered;
                worldService.OnPlayerLocationChanged += OnPlayerLocationChanged;
                worldService.OnRegionStatusChanged += OnRegionStatusChanged;
            }
        }
        
        protected override void OnDisable()
        {
            base.OnDisable();
            if (worldService != null)
            {
                worldService.OnWorldChanged -= OnWorldChanged;
                worldService.OnRegionDiscovered -= OnRegionDiscovered;
                worldService.OnPlayerLocationChanged -= OnPlayerLocationChanged;
                worldService.OnRegionStatusChanged -= OnRegionStatusChanged;
            }
        }
        
        /// <summary>
        /// Display the world map
        /// </summary>
        public void ShowWorldMap(WorldModel world, RegionModel playerRegion)
        {
            currentWorld = world;
            currentPlayerRegion = playerRegion;
            
            LoadWorldMapTexture();
            CreateRegionMarkers();
            UpdatePlayerLocation();
            CreateLegend();
            CenterOnPlayerLocation();
            
            if (regionInfoPanel != null)
                regionInfoPanel.SetActive(false);
        }
        
        /// <summary>
        /// Load and display the world map texture
        /// </summary>
        private void LoadWorldMapTexture()
        {
            if (currentWorld == null || worldMapImage == null) return;
            
            string mapPath = $"Maps/World/{currentWorld.Id}";
            Texture2D worldTexture = Resources.Load<Texture2D>(mapPath);
            
            if (worldTexture != null)
            {
                worldMapImage.texture = worldTexture;
            }
            else
            {
                Debug.LogWarning($"World map texture not found: {mapPath}");
                worldMapImage.texture = Resources.Load<Texture2D>("Maps/placeholder_world_map");
            }
        }
        
        /// <summary>
        /// Create region markers on the world map
        /// </summary>
        private void CreateRegionMarkers()
        {
            ClearRegionMarkers();
            
            if (currentWorld?.Regions == null || regionMarkersParent == null || regionMarkerPrefab == null)
                return;
            
            foreach (var region in GetFilteredRegions())
            {
                GameObject marker = Instantiate(regionMarkerPrefab, regionMarkersParent);
                RegionMarker markerComponent = marker.GetComponent<RegionMarker>();
                
                if (markerComponent != null)
                {
                    markerComponent.Initialize(region, OnRegionSelected);
                    // Position marker based on region coordinates
                    Vector2 mapPosition = WorldToMapPosition(region.WorldPosition);
                    marker.transform.localPosition = mapPosition;
                }
                
                regionMarkers.Add(marker);
            }
        }
        
        /// <summary>
        /// Get filtered regions based on current filter settings
        /// </summary>
        private List<RegionModel> GetFilteredRegions()
        {
            if (currentWorld?.Regions == null)
                return new List<RegionModel>();
            
            var regions = currentWorld.Regions.AsEnumerable();
            
            // Apply discovery filter
            if (showDiscoveredToggle != null && !showDiscoveredToggle.isOn)
                regions = regions.Where(r => !r.IsDiscovered);
            if (showUndiscoveredToggle != null && !showUndiscoveredToggle.isOn)
                regions = regions.Where(r => r.IsDiscovered);
            
            // Apply quest location filter
            if (showQuestLocationsToggle != null && showQuestLocationsToggle.isOn)
                regions = regions.Where(r => r.HasActiveQuests);
            
            // Apply danger filter
            if (showDangerousAreasToggle != null && !showDangerousAreasToggle.isOn)
                regions = regions.Where(r => r.DangerLevel <= 5);
            
            // Apply region type filter
            if (regionTypeFilter != null && regionTypeFilter.value > 0)
            {
                var selectedType = (RegionType)(regionTypeFilter.value - 1);
                regions = regions.Where(r => r.Type == selectedType);
            }
            
            return regions.ToList();
        }
        
        /// <summary>
        /// Convert world coordinates to map UI coordinates
        /// </summary>
        private Vector2 WorldToMapPosition(Vector2 worldPos)
        {
            if (worldMapImage == null || currentWorld == null) return Vector2.zero;
            
            RectTransform mapRect = worldMapImage.rectTransform;
            Vector2 mapSize = mapRect.sizeDelta;
            
            // Normalize world position to map bounds
            Vector2 normalizedPos = new Vector2(
                (worldPos.x - currentWorld.Bounds.min.x) / currentWorld.Bounds.size.x,
                (worldPos.y - currentWorld.Bounds.min.y) / currentWorld.Bounds.size.y
            );
            
            // Convert to map UI coordinates
            return new Vector2(
                (normalizedPos.x - 0.5f) * mapSize.x,
                (normalizedPos.y - 0.5f) * mapSize.y
            );
        }
        
        /// <summary>
        /// Update player location marker
        /// </summary>
        private void UpdatePlayerLocation()
        {
            if (currentPlayerRegion == null || playerMarker == null) return;
            
            Vector2 playerMapPos = WorldToMapPosition(currentPlayerRegion.WorldPosition);
            playerMarker.transform.localPosition = playerMapPos;
            
            if (currentLocationText != null)
                currentLocationText.text = $"Current Location: {currentPlayerRegion.Name}";
        }
        
        /// <summary>
        /// Show region information panel
        /// </summary>
        private void ShowRegionInfo(RegionModel region)
        {
            selectedRegion = region;
            
            if (regionInfoPanel == null) return;
            
            regionInfoPanel.SetActive(true);
            
            if (regionNameText != null)
                regionNameText.text = region.Name;
            if (regionDescriptionText != null)
                regionDescriptionText.text = region.Description;
            if (regionLevelText != null)
                regionLevelText.text = $"Recommended Level: {region.RecommendedLevel}";
            if (regionClimateText != null)
                regionClimateText.text = $"Climate: {region.Climate}";
            if (regionDangerText != null)
            {
                regionDangerText.text = $"Danger Level: {region.DangerLevel}/10";
                regionDangerText.color = GetDangerLevelColor(region.DangerLevel);
            }
            
            // Load region preview image
            if (regionPreviewImage != null && !string.IsNullOrEmpty(region.PreviewImagePath))
            {
                Sprite preview = Resources.Load<Sprite>(region.PreviewImagePath);
                if (preview != null)
                    regionPreviewImage.sprite = preview;
            }
            
            UpdateTravelOptions();
        }
        
        /// <summary>
        /// Update travel options for selected region
        /// </summary>
        private void UpdateTravelOptions()
        {
            if (selectedRegion == null) return;
            
            bool canTravel = selectedRegion.IsAccessible && selectedRegion != currentPlayerRegion;
            bool canFastTravel = selectedRegion.IsDiscovered && selectedRegion.HasFastTravelPoint;
            
            if (travelButton != null)
                travelButton.interactable = canTravel;
            if (exploreButton != null)
                exploreButton.interactable = selectedRegion.CanExplore;
            if (fastTravelButton != null)
                fastTravelButton.interactable = canFastTravel;
            
            // Calculate travel time and cost
            if (currentPlayerRegion != null && selectedRegion != null)
            {
                float distance = Vector2.Distance(currentPlayerRegion.WorldPosition, selectedRegion.WorldPosition);
                int travelTime = Mathf.RoundToInt(distance * currentWorld.TravelTimeMultiplier);
                int travelCost = Mathf.RoundToInt(distance * currentWorld.TravelCostMultiplier);
                
                if (travelTimeText != null)
                    travelTimeText.text = $"Travel Time: {travelTime} hours";
                if (travelCostText != null)
                    travelCostText.text = $"Travel Cost: {travelCost} gold";
            }
        }
        
        /// <summary>
        /// Create map legend
        /// </summary>
        private void CreateLegend()
        {
            ClearLegend();
            
            if (legendEntriesParent == null || legendEntryPrefab == null) return;
            
            var legendData = new Dictionary<string, Color>
            {
                { "Discovered Regions", Color.green },
                { "Undiscovered Regions", Color.gray },
                { "Quest Locations", Color.yellow },
                { "Dangerous Areas", Color.red },
                { "Safe Areas", Color.blue },
                { "Current Location", Color.cyan }
            };
            
            foreach (var entry in legendData)
            {
                GameObject legendEntry = Instantiate(legendEntryPrefab, legendEntriesParent);
                LegendEntry entryComponent = legendEntry.GetComponent<LegendEntry>();
                
                if (entryComponent != null)
                {
                    entryComponent.Initialize(entry.Key, entry.Value);
                }
                
                legendEntries.Add(legendEntry);
            }
        }
        
        /// <summary>
        /// Set map zoom level
        /// </summary>
        private void SetZoom(float zoom)
        {
            zoomLevel = Mathf.Clamp(zoom, MIN_ZOOM, MAX_ZOOM);
            
            if (worldMapImage != null)
            {
                worldMapImage.transform.localScale = Vector3.one * zoomLevel;
            }
            
            if (zoomSlider != null && !Mathf.Approximately(zoomSlider.value, zoomLevel))
            {
                zoomSlider.SetValueWithoutNotify(zoomLevel);
            }
        }
        
        /// <summary>
        /// Center map on player location
        /// </summary>
        private void CenterOnPlayerLocation()
        {
            if (currentPlayerRegion == null || mapScrollRect == null) return;
            
            Vector2 playerMapPos = WorldToMapPosition(currentPlayerRegion.WorldPosition);
            
            // Calculate normalized position for scroll rect
            RectTransform content = mapScrollRect.content;
            Vector2 normalizedPos = new Vector2(
                (playerMapPos.x + content.rect.width * 0.5f) / content.rect.width,
                (playerMapPos.y + content.rect.height * 0.5f) / content.rect.height
            );
            
            mapScrollRect.normalizedPosition = normalizedPos;
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
        
        /// <summary>
        /// Clear region markers
        /// </summary>
        private void ClearRegionMarkers()
        {
            foreach (var marker in regionMarkers)
            {
                if (marker != null)
                    DestroyImmediate(marker);
            }
            regionMarkers.Clear();
        }
        
        /// <summary>
        /// Clear legend entries
        /// </summary>
        private void ClearLegend()
        {
            foreach (var entry in legendEntries)
            {
                if (entry != null)
                    DestroyImmediate(entry);
            }
            legendEntries.Clear();
        }
        
        #region Event Handlers
        
        private void OnRegionSelected(RegionModel region)
        {
            ShowRegionInfo(region);
        }
        
        private void OnFilterChanged(bool value)
        {
            CreateRegionMarkers();
        }
        
        private void OnRegionTypeFilterChanged(int value)
        {
            CreateRegionMarkers();
        }
        
        private void OnWorldChanged(WorldModel world)
        {
            ShowWorldMap(world, currentPlayerRegion);
        }
        
        private void OnRegionDiscovered(RegionModel region)
        {
            CreateRegionMarkers(); // Refresh to show newly discovered region
            NotificationSystem.Instance?.ShowNotification(
                $"Discovered new region: {region.Name}",
                NotificationType.Success
            );
        }
        
        private void OnPlayerLocationChanged(RegionModel newRegion)
        {
            currentPlayerRegion = newRegion;
            UpdatePlayerLocation();
            UpdateTravelOptions();
        }
        
        private void OnRegionStatusChanged(RegionModel region)
        {
            CreateRegionMarkers(); // Refresh to show status changes
        }
        
        private void TravelToSelectedRegion()
        {
            if (selectedRegion != null && worldService != null)
            {
                worldService.TravelToRegion(selectedRegion.Id);
                Close();
            }
        }
        
        private void ExploreSelectedRegion()
        {
            if (selectedRegion != null && worldService != null)
            {
                worldService.ExploreRegion(selectedRegion.Id);
                // Keep panel open to show exploration results
            }
        }
        
        private void FastTravelToSelectedRegion()
        {
            if (selectedRegion != null && worldService != null)
            {
                ModalSystem.Instance?.ShowConfirmation(
                    "Fast Travel",
                    $"Fast travel to {selectedRegion.Name}?",
                    () => {
                        worldService.FastTravelToRegion(selectedRegion.Id);
                        Close();
                    },
                    null
                );
            }
        }
        
        private void ToggleLegend()
        {
            if (legendPanel != null)
                legendPanel.SetActive(!legendPanel.activeSelf);
        }
        
        private void ToggleFullscreen()
        {
            // Toggle fullscreen mode
            // Implementation depends on fullscreen requirements
        }
        
        #endregion
    }
} 