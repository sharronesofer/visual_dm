using System.Collections.Generic;
using UnityEngine;
using VDM.Systems.Motifs.Models;
using VDM.Systems.Motifs.Services;

namespace VDM.Systems.Motifs.Visualization
{
    /// <summary>
    /// Visualizes motifs in world space with dynamic effects and area indicators.
    /// Handles different visualization modes for different motif types and scopes.
    /// </summary>
    public class MotifVisualization : MonoBehaviour
    {
        [Header("Visualization Settings")]
        [SerializeField] private bool _enableVisualization = true;
        [SerializeField] private bool _showGlobalMotifs = true;
        [SerializeField] private bool _showRegionalMotifs = true;
        [SerializeField] private bool _showLocalMotifs = true;
        [SerializeField] private float _updateInterval = 5f;
        [SerializeField] private float _maxVisualizationDistance = 1000f;
        [SerializeField] private int _maxVisibleMotifs = 50;

        [Header("Prefabs")]
        [SerializeField] private GameObject _globalMotifPrefab;
        [SerializeField] private GameObject _regionalMotifPrefab;
        [SerializeField] private GameObject _localMotifPrefab;
        [SerializeField] private GameObject _motifEffectPrefab;

        [Header("Global Motif Settings")]
        [SerializeField] private Transform _globalMotifContainer;
        [SerializeField] private Vector3 _globalMotifPosition = Vector3.up * 100f;
        [SerializeField] private float _globalMotifSpacing = 20f;

        [Header("Regional/Local Motif Settings")]
        [SerializeField] private Transform _spatialMotifContainer;
        [SerializeField] private float _motifHeightOffset = 5f;
        [SerializeField] private float _motifScaleMultiplier = 1f;

        [Header("Visual Effects")]
        [SerializeField] private bool _enableParticleEffects = true;
        [SerializeField] private bool _enableLightEffects = true;
        [SerializeField] private bool _enableAreaIndicators = true;
        [SerializeField] private float _effectIntensityMultiplier = 1f;

        private Dictionary<string, MotifVisualInstance> _activeVisualizations = new Dictionary<string, MotifVisualInstance>();
        private Camera _mainCamera;
        private Transform _cameraTransform;
        private bool _isInitialized = false;

        #region Unity Lifecycle

        private void Start()
        {
            Initialize();
            
            if (_enableVisualization)
            {
                InvokeRepeating(nameof(UpdateVisualizations), 0f, _updateInterval);
            }
        }

        private void Update()
        {
            if (_enableVisualization && _isInitialized)
            {
                UpdateVisualizationDistances();
                UpdateEffectIntensities();
            }
        }

        private void OnDisable()
        {
            ClearAllVisualizations();
        }

        #endregion

        #region Initialization

        private void Initialize()
        {
            _mainCamera = Camera.main;
            if (_mainCamera != null)
            {
                _cameraTransform = _mainCamera.transform;
            }

            // Create containers if they don't exist
            if (_globalMotifContainer == null)
            {
                GameObject container = new GameObject("Global Motifs");
                container.transform.SetParent(transform);
                _globalMotifContainer = container.transform;
            }

            if (_spatialMotifContainer == null)
            {
                GameObject container = new GameObject("Spatial Motifs");
                container.transform.SetParent(transform);
                _spatialMotifContainer = container.transform;
            }

            _isInitialized = true;
        }

        #endregion

        #region Visualization Updates

        private async void UpdateVisualizations()
        {
            if (!_enableVisualization || MotifManager.Instance == null) return;

            try
            {
                // Get all active motifs
                var motifs = await MotifManager.Instance.GetActiveMotifsAsync();
                
                // Filter motifs based on settings and distance
                var visibleMotifs = FilterVisibleMotifs(motifs);
                
                // Update visualizations
                UpdateMotifVisualizations(visibleMotifs);
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"MotifVisualization: Error updating visualizations: {ex.Message}");
            }
        }

        private List<Motif> FilterVisibleMotifs(List<Motif> motifs)
        {
            var visibleMotifs = new List<Motif>();
            Vector3 cameraPos = _cameraTransform != null ? _cameraTransform.position : Vector3.zero;

            foreach (var motif in motifs)
            {
                // Check scope filters
                if (!ShouldShowMotifScope(motif.scope)) continue;

                // Check distance for spatial motifs
                if (motif.scope != MotifScope.Global)
                {
                    if (motif.location != null)
                    {
                        Vector3 motifPos = new Vector3(motif.location.position.x, 0, motif.location.position.y);
                        float distance = Vector3.Distance(cameraPos, motifPos);
                        
                        if (distance > _maxVisualizationDistance) continue;
                    }
                }

                visibleMotifs.Add(motif);
                
                // Limit number of visible motifs for performance
                if (visibleMotifs.Count >= _maxVisibleMotifs) break;
            }

            return visibleMotifs;
        }

        private bool ShouldShowMotifScope(MotifScope scope)
        {
            return scope switch
            {
                MotifScope.Global => _showGlobalMotifs,
                MotifScope.Regional => _showRegionalMotifs,
                MotifScope.Local => _showLocalMotifs,
                _ => false
            };
        }

        private void UpdateMotifVisualizations(List<Motif> visibleMotifs)
        {
            // Track which motifs are currently visible
            var currentMotifIds = new HashSet<string>();
            
            foreach (var motif in visibleMotifs)
            {
                currentMotifIds.Add(motif.id);
                
                if (_activeVisualizations.TryGetValue(motif.id, out var existingInstance))
                {
                    // Update existing visualization
                    existingInstance.UpdateMotif(motif);
                }
                else
                {
                    // Create new visualization
                    CreateMotifVisualization(motif);
                }
            }
            
            // Remove visualizations for motifs that are no longer visible
            var toRemove = new List<string>();
            foreach (var kvp in _activeVisualizations)
            {
                if (!currentMotifIds.Contains(kvp.Key))
                {
                    toRemove.Add(kvp.Key);
                }
            }
            
            foreach (var motifId in toRemove)
            {
                RemoveMotifVisualization(motifId);
            }
        }

        #endregion

        #region Motif Visualization Creation

        private void CreateMotifVisualization(Motif motif)
        {
            GameObject prefab = GetMotifPrefab(motif.scope);
            if (prefab == null) return;

            Transform parent = GetMotifParent(motif.scope);
            Vector3 position = GetMotifPosition(motif);

            GameObject instance = Instantiate(prefab, position, Quaternion.identity, parent);
            var visualInstance = instance.GetComponent<MotifVisualInstance>();
            
            if (visualInstance == null)
            {
                visualInstance = instance.AddComponent<MotifVisualInstance>();
            }

            visualInstance.Initialize(motif, this);
            _activeVisualizations[motif.id] = visualInstance;
        }

        private void RemoveMotifVisualization(string motifId)
        {
            if (_activeVisualizations.TryGetValue(motifId, out var instance))
            {
                if (instance != null)
                {
                    instance.Destroy();
                }
                _activeVisualizations.Remove(motifId);
            }
        }

        private GameObject GetMotifPrefab(MotifScope scope)
        {
            return scope switch
            {
                MotifScope.Global => _globalMotifPrefab,
                MotifScope.Regional => _regionalMotifPrefab,
                MotifScope.Local => _localMotifPrefab,
                _ => null
            };
        }

        private Transform GetMotifParent(MotifScope scope)
        {
            return scope switch
            {
                MotifScope.Global => _globalMotifContainer,
                _ => _spatialMotifContainer
            };
        }

        private Vector3 GetMotifPosition(Motif motif)
        {
            switch (motif.scope)
            {
                case MotifScope.Global:
                    // Position global motifs in a circular pattern above the world
                    int globalIndex = 0;
                    foreach (var kvp in _activeVisualizations)
                    {
                        if (kvp.Value.GetMotif().scope == MotifScope.Global)
                            globalIndex++;
                    }
                    
                    float angle = globalIndex * (360f / 8f) * Mathf.Deg2Rad; // Max 8 global motifs in circle
                    return _globalMotifPosition + new Vector3(
                        Mathf.Cos(angle) * _globalMotifSpacing,
                        0,
                        Mathf.Sin(angle) * _globalMotifSpacing
                    );

                case MotifScope.Regional:
                case MotifScope.Local:
                    if (motif.location != null)
                    {
                        return new Vector3(
                            motif.location.position.x,
                            _motifHeightOffset,
                            motif.location.position.y
                        );
                    }
                    break;
            }

            return Vector3.zero;
        }

        #endregion

        #region Visual Effects Updates

        private void UpdateVisualizationDistances()
        {
            if (_cameraTransform == null) return;

            Vector3 cameraPos = _cameraTransform.position;

            foreach (var kvp in _activeVisualizations)
            {
                var instance = kvp.Value;
                if (instance != null)
                {
                    float distance = Vector3.Distance(cameraPos, instance.transform.position);
                    instance.UpdateDistanceEffects(distance, _maxVisualizationDistance);
                }
            }
        }

        private void UpdateEffectIntensities()
        {
            foreach (var kvp in _activeVisualizations)
            {
                var instance = kvp.Value;
                if (instance != null)
                {
                    instance.UpdateEffectIntensity(_effectIntensityMultiplier);
                }
            }
        }

        #endregion

        #region Public API

        /// <summary>
        /// Enable or disable motif visualization
        /// </summary>
        public void SetVisualizationEnabled(bool enabled)
        {
            _enableVisualization = enabled;
            
            if (!enabled)
            {
                ClearAllVisualizations();
            }
            else
            {
                UpdateVisualizations();
            }
        }

        /// <summary>
        /// Set which motif scopes should be visualized
        /// </summary>
        public void SetScopeVisibility(MotifScope scope, bool visible)
        {
            switch (scope)
            {
                case MotifScope.Global:
                    _showGlobalMotifs = visible;
                    break;
                case MotifScope.Regional:
                    _showRegionalMotifs = visible;
                    break;
                case MotifScope.Local:
                    _showLocalMotifs = visible;
                    break;
            }
            
            if (_enableVisualization)
            {
                UpdateVisualizations();
            }
        }

        /// <summary>
        /// Focus on a specific motif
        /// </summary>
        public void FocusOnMotif(string motifId)
        {
            if (_activeVisualizations.TryGetValue(motifId, out var instance))
            {
                instance.Highlight(2f);
                
                // Move camera if it's a spatial motif
                if (_mainCamera != null && instance.GetMotif().scope != MotifScope.Global)
                {
                    Vector3 targetPos = instance.transform.position + Vector3.back * 20f + Vector3.up * 10f;
                    StartCoroutine(SmoothCameraMove(targetPos));
                }
            }
        }

        /// <summary>
        /// Clear all active visualizations
        /// </summary>
        public void ClearAllVisualizations()
        {
            foreach (var kvp in _activeVisualizations)
            {
                if (kvp.Value != null)
                {
                    kvp.Value.Destroy();
                }
            }
            _activeVisualizations.Clear();
        }

        /// <summary>
        /// Get visualization settings for external configuration
        /// </summary>
        public VisualizationSettings GetSettings()
        {
            return new VisualizationSettings
            {
                enableVisualization = _enableVisualization,
                showGlobalMotifs = _showGlobalMotifs,
                showRegionalMotifs = _showRegionalMotifs,
                showLocalMotifs = _showLocalMotifs,
                maxVisualizationDistance = _maxVisualizationDistance,
                maxVisibleMotifs = _maxVisibleMotifs,
                enableParticleEffects = _enableParticleEffects,
                enableLightEffects = _enableLightEffects,
                enableAreaIndicators = _enableAreaIndicators
            };
        }

        /// <summary>
        /// Apply visualization settings
        /// </summary>
        public void ApplySettings(VisualizationSettings settings)
        {
            _enableVisualization = settings.enableVisualization;
            _showGlobalMotifs = settings.showGlobalMotifs;
            _showRegionalMotifs = settings.showRegionalMotifs;
            _showLocalMotifs = settings.showLocalMotifs;
            _maxVisualizationDistance = settings.maxVisualizationDistance;
            _maxVisibleMotifs = settings.maxVisibleMotifs;
            _enableParticleEffects = settings.enableParticleEffects;
            _enableLightEffects = settings.enableLightEffects;
            _enableAreaIndicators = settings.enableAreaIndicators;
            
            UpdateVisualizations();
        }

        #endregion

        #region Helper Methods

        private System.Collections.IEnumerator SmoothCameraMove(Vector3 targetPosition)
        {
            if (_mainCamera == null) yield break;
            
            Vector3 startPos = _mainCamera.transform.position;
            float duration = 2f;
            float elapsed = 0f;
            
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / duration;
                t = Mathf.SmoothStep(0f, 1f, t);
                
                _mainCamera.transform.position = Vector3.Lerp(startPos, targetPosition, t);
                yield return null;
            }
        }

        #endregion

        #region Settings Data Structure

        [System.Serializable]
        public class VisualizationSettings
        {
            public bool enableVisualization;
            public bool showGlobalMotifs;
            public bool showRegionalMotifs;
            public bool showLocalMotifs;
            public float maxVisualizationDistance;
            public int maxVisibleMotifs;
            public bool enableParticleEffects;
            public bool enableLightEffects;
            public bool enableAreaIndicators;
        }

        #endregion
    }
} 