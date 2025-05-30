using System.Collections.Generic;
using System.Linq;
using System;
using TMPro;
using UnityEngine.UI;
using UnityEngine;
using VDM.Runtime.Arc.Models;
using VDM.Runtime.Arc.Services;
using VDM.Runtime.UI;


namespace VDM.Runtime.Arc.UI
{
    /// <summary>
    /// UI component for displaying and managing arc progression
    /// </summary>
    public class ArcProgressionUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private Transform arcListParent;
        [SerializeField] private GameObject arcItemPrefab;
        [SerializeField] private TMP_Dropdown typeFilter;
        [SerializeField] private TMP_Dropdown statusFilter;
        [SerializeField] private Button refreshButton;
        [SerializeField] private ScrollRect scrollRect;
        
        [Header("Arc Detail Panel")]
        [SerializeField] private GameObject arcDetailPanel;
        [SerializeField] private TextMeshProUGUI arcTitleText;
        [SerializeField] private TextMeshProUGUI arcDescriptionText;
        [SerializeField] private Slider progressSlider;
        [SerializeField] private TextMeshProUGUI progressText;
        [SerializeField] private Transform arcStepsParent;
        [SerializeField] private GameObject arcStepPrefab;
        [SerializeField] private Button startArcButton;
        [SerializeField] private Button progressArcButton;
        [SerializeField] private Button completeArcButton;
        
        [Header("Arc Timeline")]
        [SerializeField] private Transform timelineParent;
        [SerializeField] private GameObject timelineStepPrefab;
        [SerializeField] private RectTransform timelineProgressBar;
        [SerializeField] private Image timelineProgressFill;
        
        [Header("Settings")]
        [SerializeField] private string currentCharacterId;
        [SerializeField] private bool autoRefresh = true;
        [SerializeField] private float refreshInterval = 30f;
        
        private ArcService arcService;
        private List<ArcDTO> allArcs = new List<ArcDTO>();
        private List<ArcDTO> filteredArcs = new List<ArcDTO>();
        private ArcDTO selectedArc;
        private List<GameObject> arcItemObjects = new List<GameObject>();
        private List<GameObject> arcStepObjects = new List<GameObject>();
        private List<GameObject> timelineStepObjects = new List<GameObject>();
        private float lastRefreshTime;
        
        // Events
        public event Action<ArcDTO> OnArcSelected;
        public event Action<ArcDTO> OnArcStarted;
        public event Action<ArcDTO> OnArcProgressed;
        public event Action<ArcDTO> OnArcCompleted;
        
        private void Awake()
        {
            arcService = new ArcService();
            InitializeUI();
        }
        
        private void Start()
        {
            RefreshArcList();
        }
        
        private void Update()
        {
            if (autoRefresh && Time.time - lastRefreshTime > refreshInterval)
            {
                RefreshArcList();
            }
        }
        
        private void InitializeUI()
        {
            // Setup filter dropdowns
            if (typeFilter != null)
            {
                typeFilter.options.Clear();
                typeFilter.options.Add(new TMP_Dropdown.OptionData("All"));
                typeFilter.options.Add(new TMP_Dropdown.OptionData("Global"));
                typeFilter.options.Add(new TMP_Dropdown.OptionData("Regional"));
                typeFilter.options.Add(new TMP_Dropdown.OptionData("Character"));
                typeFilter.options.Add(new TMP_Dropdown.OptionData("NPC"));
                typeFilter.onValueChanged.AddListener(OnFilterChanged);
            }
            
            if (statusFilter != null)
            {
                statusFilter.options.Clear();
                statusFilter.options.Add(new TMP_Dropdown.OptionData("All"));
                statusFilter.options.Add(new TMP_Dropdown.OptionData("Pending"));
                statusFilter.options.Add(new TMP_Dropdown.OptionData("Active"));
                statusFilter.options.Add(new TMP_Dropdown.OptionData("Stalled"));
                statusFilter.options.Add(new TMP_Dropdown.OptionData("Completed"));
                statusFilter.onValueChanged.AddListener(OnFilterChanged);
            }
            
            // Setup buttons
            if (refreshButton != null)
            {
                refreshButton.onClick.AddListener(RefreshArcList);
            }
            
            if (startArcButton != null)
            {
                startArcButton.onClick.AddListener(StartSelectedArc);
            }
            
            if (progressArcButton != null)
            {
                progressArcButton.onClick.AddListener(ProgressSelectedArc);
            }
            
            if (completeArcButton != null)
            {
                completeArcButton.onClick.AddListener(CompleteSelectedArc);
            }
            
            // Hide detail panel initially
            if (arcDetailPanel != null)
            {
                arcDetailPanel.SetActive(false);
            }
        }
        
        public async void RefreshArcList()
        {
            try
            {
                // Get all arcs
                var arcs = await arcService.GetArcsAsync();
                
                // If character ID is set, also get character-specific arcs
                if (!string.IsNullOrEmpty(currentCharacterId))
                {
                    var characterArcs = await arcService.GetActiveArcsForCharacterAsync(currentCharacterId);
                    arcs.AddRange(characterArcs);
                }
                
                // Remove duplicates
                allArcs = arcs.GroupBy(a => a.Id).Select(g => g.First()).ToList();
                
                ApplyFilters();
                lastRefreshTime = Time.time;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to refresh arc list: {ex.Message}");
            }
        }
        
        private void OnFilterChanged(int value)
        {
            ApplyFilters();
        }
        
        private void ApplyFilters()
        {
            filteredArcs.Clear();
            
            foreach (var arc in allArcs)
            {
                bool passesFilter = true;
                
                // Type filter
                if (typeFilter != null && typeFilter.value > 0)
                {
                    string selectedType = typeFilter.options[typeFilter.value].text.ToLower();
                    if (selectedType != "all" && !arc.Type.ToLower().Contains(selectedType))
                    {
                        passesFilter = false;
                    }
                }
                
                // Status filter
                if (statusFilter != null && statusFilter.value > 0)
                {
                    string selectedStatus = statusFilter.options[statusFilter.value].text.ToLower();
                    if (selectedStatus != "all" && !arc.Status.ToLower().Contains(selectedStatus))
                    {
                        passesFilter = false;
                    }
                }
                
                if (passesFilter)
                {
                    filteredArcs.Add(arc);
                }
            }
            
            // Sort by priority and progress
            filteredArcs = filteredArcs.OrderBy(a => GetPriorityOrder(a.Priority))
                                     .ThenByDescending(a => a.ProgressPercentage)
                                     .ToList();
            
            UpdateArcListDisplay();
        }
        
        private int GetPriorityOrder(string priority)
        {
            return priority?.ToLower() switch
            {
                "urgent" => 0,
                "high" => 1,
                "medium" => 2,
                "low" => 3,
                _ => 4
            };
        }
        
        private void UpdateArcListDisplay()
        {
            // Clear existing arc items
            foreach (var item in arcItemObjects)
            {
                if (item != null)
                {
                    Destroy(item);
                }
            }
            arcItemObjects.Clear();
            
            // Create arc items
            if (arcListParent != null && arcItemPrefab != null)
            {
                foreach (var arc in filteredArcs)
                {
                    var arcItem = Instantiate(arcItemPrefab, arcListParent);
                    var arcItemUI = arcItem.GetComponent<ArcItemUI>();
                    
                    if (arcItemUI != null)
                    {
                        arcItemUI.SetArc(arc);
                        arcItemUI.OnArcClicked += SelectArc;
                    }
                    
                    arcItemObjects.Add(arcItem);
                }
            }
        }
        
        public void SelectArc(ArcDTO arc)
        {
            selectedArc = arc;
            UpdateArcDetailDisplay();
            OnArcSelected?.Invoke(arc);
        }
        
        private void UpdateArcDetailDisplay()
        {
            if (selectedArc == null)
            {
                if (arcDetailPanel != null)
                {
                    arcDetailPanel.SetActive(false);
                }
                return;
            }
            
            if (arcDetailPanel != null)
            {
                arcDetailPanel.SetActive(true);
            }
            
            // Update arc info
            if (arcTitleText != null)
            {
                arcTitleText.text = selectedArc.Title;
            }
            
            if (arcDescriptionText != null)
            {
                arcDescriptionText.text = selectedArc.Description;
            }
            
            // Update progress
            if (progressSlider != null)
            {
                progressSlider.value = selectedArc.ProgressPercentage / 100f;
            }
            
            if (progressText != null)
            {
                progressText.text = $"{selectedArc.ProgressPercentage:F1}%";
            }
            
            // Update arc steps
            UpdateArcStepsDisplay();
            
            // Update timeline
            UpdateTimelineDisplay();
            
            // Update buttons
            UpdateArcButtons();
        }
        
        private void UpdateArcStepsDisplay()
        {
            // Clear existing step items
            foreach (var step in arcStepObjects)
            {
                if (step != null)
                {
                    Destroy(step);
                }
            }
            arcStepObjects.Clear();
            
            // Create step items
            if (arcStepsParent != null && arcStepPrefab != null && selectedArc?.Steps != null)
            {
                foreach (var step in selectedArc.Steps.OrderBy(s => s.Order))
                {
                    var stepItem = Instantiate(arcStepPrefab, arcStepsParent);
                    var stepUI = stepItem.GetComponent<ArcStepUI>();
                    
                    if (stepUI != null)
                    {
                        stepUI.SetArcStep(step);
                        stepUI.SetIsCurrentStep(step.Order == selectedArc.CurrentStep);
                    }
                    
                    arcStepObjects.Add(stepItem);
                }
            }
        }
        
        private void UpdateTimelineDisplay()
        {
            // Clear existing timeline items
            foreach (var item in timelineStepObjects)
            {
                if (item != null)
                {
                    Destroy(item);
                }
            }
            timelineStepObjects.Clear();
            
            if (timelineParent == null || timelineStepPrefab == null || selectedArc?.Steps == null)
                return;
            
            var steps = selectedArc.Steps.OrderBy(s => s.Order).ToList();
            if (steps.Count == 0) return;
            
            // Update timeline progress bar
            if (timelineProgressFill != null)
            {
                timelineProgressFill.fillAmount = selectedArc.ProgressPercentage / 100f;
            }
            
            // Create timeline step markers
            for (int i = 0; i < steps.Count; i++)
            {
                var step = steps[i];
                var timelineItem = Instantiate(timelineStepPrefab, timelineParent);
                var timelineStepUI = timelineItem.GetComponent<TimelineStepUI>();
                
                if (timelineStepUI != null)
                {
                    timelineStepUI.SetStep(step, i, steps.Count);
                    timelineStepUI.SetIsCurrentStep(step.Order == selectedArc.CurrentStep);
                    timelineStepUI.SetIsCompleted(step.Completed);
                }
                
                // Position the timeline item
                var rectTransform = timelineItem.GetComponent<RectTransform>();
                if (rectTransform != null && steps.Count > 1)
                {
                    float normalizedPosition = (float)i / (steps.Count - 1);
                    rectTransform.anchorMin = new Vector2(normalizedPosition, 0.5f);
                    rectTransform.anchorMax = new Vector2(normalizedPosition, 0.5f);
                    rectTransform.anchoredPosition = Vector2.zero;
                }
                
                timelineStepObjects.Add(timelineItem);
            }
        }
        
        private void UpdateArcButtons()
        {
            if (selectedArc == null) return;
            
            string status = selectedArc.Status?.ToLower();
            
            if (startArcButton != null)
            {
                startArcButton.gameObject.SetActive(status == "pending");
            }
            
            if (progressArcButton != null)
            {
                bool canProgress = status == "active" && selectedArc.CurrentStep < selectedArc.Steps?.Count - 1;
                progressArcButton.gameObject.SetActive(canProgress);
            }
            
            if (completeArcButton != null)
            {
                bool canComplete = status == "active" && 
                                 selectedArc.Steps?.All(s => s.Completed) == true;
                completeArcButton.gameObject.SetActive(canComplete);
            }
        }
        
        private async void StartSelectedArc()
        {
            if (selectedArc == null) return;
            
            try
            {
                var updatedArc = await arcService.StartArcAsync(selectedArc.Id);
                if (updatedArc != null)
                {
                    selectedArc = updatedArc;
                    UpdateArcDetailDisplay();
                    RefreshArcList();
                    OnArcStarted?.Invoke(updatedArc);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to start arc: {ex.Message}");
            }
        }
        
        private async void ProgressSelectedArc()
        {
            if (selectedArc == null) return;
            
            try
            {
                var progressResponse = await arcService.ProgressArcAsync(selectedArc.Id);
                if (progressResponse != null)
                {
                    // Refresh the arc to get updated data
                    var updatedArc = await arcService.GetArcAsync(selectedArc.Id);
                    if (updatedArc != null)
                    {
                        selectedArc = updatedArc;
                        UpdateArcDetailDisplay();
                        RefreshArcList();
                        OnArcProgressed?.Invoke(updatedArc);
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to progress arc: {ex.Message}");
            }
        }
        
        private async void CompleteSelectedArc()
        {
            if (selectedArc == null) return;
            
            try
            {
                var updatedArc = await arcService.CompleteArcAsync(selectedArc.Id);
                if (updatedArc != null)
                {
                    selectedArc = updatedArc;
                    UpdateArcDetailDisplay();
                    RefreshArcList();
                    OnArcCompleted?.Invoke(updatedArc);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to complete arc: {ex.Message}");
            }
        }
        
        public void SetCharacterId(string characterId)
        {
            currentCharacterId = characterId;
            RefreshArcList();
        }
        
        public void SetAutoRefresh(bool enabled, float interval = 30f)
        {
            autoRefresh = enabled;
            refreshInterval = interval;
        }
        
        public async void ShowArcAnalytics()
        {
            try
            {
                var analytics = await arcService.GetArcAnalyticsAsync();
                // TODO: Display analytics in a popup or dedicated panel
                Debug.Log($"Arc Analytics: {analytics.Count} data points");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get arc analytics: {ex.Message}");
            }
        }
        
        public async void CheckStalledArcs()
        {
            try
            {
                var stalledArcs = await arcService.GetStalledArcsAsync();
                if (stalledArcs.Count > 0)
                {
                    Debug.LogWarning($"Found {stalledArcs.Count} stalled arcs that need attention");
                    // TODO: Show notification or highlight stalled arcs in UI
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to check stalled arcs: {ex.Message}");
            }
        }
    }
} 