using VDM.Systems.Motifs.Models;
using UnityEngine;

namespace VDM.Systems.Motifs.Visualization
{
    /// <summary>
    /// Represents a single motif visualization instance in the world.
    /// Handles visual effects, animations, and user interaction for individual motifs.
    /// </summary>
    public class MotifVisualInstance : MonoBehaviour
    {
        [Header("Visual Components")]
        [SerializeField] private Renderer _mainRenderer;
        [SerializeField] private ParticleSystem _particleSystem;
        [SerializeField] private Light _motifLight;
        [SerializeField] private GameObject _areaIndicator;
        [SerializeField] private LineRenderer _connectionLines;

        [Header("Animation Settings")]
        [SerializeField] private bool _enableFloating = true;
        [SerializeField] private float _floatAmplitude = 1f;
        [SerializeField] private float _floatSpeed = 1f;
        [SerializeField] private bool _enableRotation = true;
        [SerializeField] private float _rotationSpeed = 30f;

        [Header("Distance Effects")]
        [SerializeField] private AnimationCurve _scaleCurve = AnimationCurve.Linear(0f, 1f, 1f, 0.1f);
        [SerializeField] private AnimationCurve _opacityCurve = AnimationCurve.Linear(0f, 1f, 1f, 0f);

        private Motif _motif;
        private MotifVisualization _parentVisualization;
        private Vector3 _basePosition;
        private Color _baseColor;
        private Material _instanceMaterial;
        private bool _isInitialized = false;
        private bool _isHighlighted = false;

        #region Initialization

        /// <summary>
        /// Initialize the visual instance with motif data
        /// </summary>
        public void Initialize(Motif motif, MotifVisualization parentVisualization)
        {
            _motif = motif;
            _parentVisualization = parentVisualization;
            _basePosition = transform.position;

            SetupVisualComponents();
            SetupMaterial();
            SetupEffects();
            SetupAreaIndicator();

            _isInitialized = true;
        }

        private void SetupVisualComponents()
        {
            // Find components if not assigned
            if (_mainRenderer == null)
                _mainRenderer = GetComponentInChildren<Renderer>();
            
            if (_particleSystem == null)
                _particleSystem = GetComponentInChildren<ParticleSystem>();
            
            if (_motifLight == null)
                _motifLight = GetComponentInChildren<Light>();
            
            if (_connectionLines == null)
                _connectionLines = GetComponentInChildren<LineRenderer>();
        }

        private void SetupMaterial()
        {
            if (_mainRenderer != null)
            {
                // Create instance material to avoid shared material modifications
                _instanceMaterial = new Material(_mainRenderer.material);
                _mainRenderer.material = _instanceMaterial;
                
                // Set base color based on motif category
                _baseColor = GetCategoryColor(_motif.category);
                _instanceMaterial.color = _baseColor;
                
                // Set emission based on intensity
                if (_instanceMaterial.HasProperty("_EmissionColor"))
                {
                    Color emissionColor = _baseColor * (_motif.intensity / 10f);
                    _instanceMaterial.SetColor("_EmissionColor", emissionColor);
                }
            }
        }

        private void SetupEffects()
        {
            // Setup particle system
            if (_particleSystem != null)
            {
                var main = _particleSystem.main;
                main.startColor = _baseColor;
                main.maxParticles = Mathf.RoundToInt(_motif.intensity * 10);
                
                var emission = _particleSystem.emission;
                emission.rateOverTime = _motif.intensity * 2;
                
                // Adjust particle system based on motif lifecycle
                switch (_motif.lifecycle)
                {
                    case MotifLifecycle.Emerging:
                        main.startSpeed = 2f;
                        break;
                    case MotifLifecycle.Stable:
                        main.startSpeed = 1f;
                        break;
                    case MotifLifecycle.Waning:
                        main.startSpeed = 0.5f;
                        break;
                    case MotifLifecycle.Fading:
                        main.startSpeed = 0.2f;
                        break;
                }
            }

            // Setup light
            if (_motifLight != null)
            {
                _motifLight.color = _baseColor;
                _motifLight.intensity = _motif.intensity / 5f; // Scale down for reasonable lighting
                _motifLight.range = _motif.intensity * 2f;
            }
        }

        private void SetupAreaIndicator()
        {
            if (_areaIndicator != null && _motif.location != null)
            {
                // Scale area indicator based on motif radius
                float radius = _motif.location.radius;
                if (radius > 0)
                {
                    _areaIndicator.transform.localScale = Vector3.one * radius;
                }
                
                // Color the area indicator
                var areaRenderer = _areaIndicator.GetComponent<Renderer>();
                if (areaRenderer != null)
                {
                    var areaMaterial = new Material(areaRenderer.material);
                    areaMaterial.color = new Color(_baseColor.r, _baseColor.g, _baseColor.b, 0.3f);
                    areaRenderer.material = areaMaterial;
                }
            }
        }

        #endregion

        #region Unity Lifecycle

        private void Update()
        {
            if (!_isInitialized) return;

            UpdateAnimations();
            UpdateLifecycleEffects();
        }

        private void OnDestroy()
        {
            if (_instanceMaterial != null)
            {
                Destroy(_instanceMaterial);
            }
        }

        #endregion

        #region Visual Updates

        private void UpdateAnimations()
        {
            if (_enableFloating)
            {
                float floatOffset = Mathf.Sin(Time.time * _floatSpeed) * _floatAmplitude;
                transform.position = _basePosition + Vector3.up * floatOffset;
            }

            if (_enableRotation)
            {
                transform.Rotate(Vector3.up, _rotationSpeed * Time.deltaTime);
            }
        }

        private void UpdateLifecycleEffects()
        {
            float lifecycleIntensity = GetLifecycleIntensity();
            
            // Update material emission
            if (_instanceMaterial != null && _instanceMaterial.HasProperty("_EmissionColor"))
            {
                Color emissionColor = _baseColor * lifecycleIntensity;
                _instanceMaterial.SetColor("_EmissionColor", emissionColor);
            }

            // Update light intensity
            if (_motifLight != null)
            {
                _motifLight.intensity = (_motif.intensity / 5f) * lifecycleIntensity;
            }

            // Update particle emission
            if (_particleSystem != null)
            {
                var emission = _particleSystem.emission;
                emission.rateOverTime = _motif.intensity * 2 * lifecycleIntensity;
            }
        }

        private float GetLifecycleIntensity()
        {
            return _motif.lifecycle switch
            {
                MotifLifecycle.Dormant => 0.1f,
                MotifLifecycle.Emerging => 0.6f,
                MotifLifecycle.Stable => 1.0f,
                MotifLifecycle.Waning => 0.7f,
                MotifLifecycle.Fading => 0.3f,
                _ => 0.5f
            };
        }

        #endregion

        #region Public API

        /// <summary>
        /// Update the motif data for this instance
        /// </summary>
        public void UpdateMotif(Motif motif)
        {
            _motif = motif;
            
            // Update visual components if needed
            if (_motif.intensity != _motif.intensity || _motif.lifecycle != _motif.lifecycle)
            {
                SetupEffects();
            }
        }

        /// <summary>
        /// Get the motif associated with this instance
        /// </summary>
        public Motif GetMotif()
        {
            return _motif;
        }

        /// <summary>
        /// Update distance-based effects
        /// </summary>
        public void UpdateDistanceEffects(float distance, float maxDistance)
        {
            float normalizedDistance = distance / maxDistance;
            
            // Update scale based on distance
            float scale = _scaleCurve.Evaluate(normalizedDistance);
            transform.localScale = Vector3.one * scale;
            
            // Update opacity based on distance
            float opacity = _opacityCurve.Evaluate(normalizedDistance);
            UpdateOpacity(opacity);
        }

        /// <summary>
        /// Update effect intensity multiplier
        /// </summary>
        public void UpdateEffectIntensity(float multiplier)
        {
            if (_particleSystem != null)
            {
                var emission = _particleSystem.emission;
                emission.rateOverTime = _motif.intensity * 2 * multiplier * GetLifecycleIntensity();
            }

            if (_motifLight != null)
            {
                _motifLight.intensity = (_motif.intensity / 5f) * multiplier * GetLifecycleIntensity();
            }
        }

        /// <summary>
        /// Highlight this motif instance
        /// </summary>
        public void Highlight(float duration = 1f)
        {
            if (_isHighlighted) return;
            
            StartCoroutine(HighlightCoroutine(duration));
        }

        /// <summary>
        /// Destroy this visual instance
        /// </summary>
        public void Destroy()
        {
            if (_instanceMaterial != null)
            {
                UnityEngine.Object.Destroy(_instanceMaterial);
            }
            UnityEngine.Object.Destroy(gameObject);
        }

        #endregion

        #region Helper Methods

        private void UpdateOpacity(float opacity)
        {
            if (_instanceMaterial != null)
            {
                Color color = _instanceMaterial.color;
                color.a = opacity;
                _instanceMaterial.color = color;
            }

            // Update particle system alpha
            if (_particleSystem != null)
            {
                var main = _particleSystem.main;
                Color particleColor = main.startColor.color;
                particleColor.a = opacity;
                main.startColor = particleColor;
            }
        }

        private Color GetCategoryColor(MotifCategory category)
        {
            return category switch
            {
                MotifCategory.Ascension => new Color(1f, 0.8f, 0.2f), // Gold
                MotifCategory.Betrayal => new Color(0.8f, 0.2f, 0.2f), // Dark Red
                MotifCategory.Chaos => new Color(0.6f, 0.2f, 0.8f), // Purple
                MotifCategory.Collapse => new Color(0.5f, 0.3f, 0.2f), // Brown
                MotifCategory.Control => new Color(0.8f, 0.4f, 0.2f), // Orange
                MotifCategory.Death => new Color(0.1f, 0.1f, 0.1f), // Black
                MotifCategory.Deception => new Color(0.7f, 0.3f, 0.7f), // Magenta
                MotifCategory.Desire => new Color(1f, 0.4f, 0.6f), // Pink
                MotifCategory.Fear => new Color(0.4f, 0.1f, 0.1f), // Dark Red
                MotifCategory.Hope => new Color(0.2f, 0.8f, 0.4f), // Green
                MotifCategory.Justice => new Color(0.2f, 0.4f, 0.8f), // Blue
                MotifCategory.Madness => new Color(0.8f, 0.2f, 0.8f), // Bright Purple
                MotifCategory.Peace => new Color(0.6f, 0.8f, 0.9f), // Light Blue
                MotifCategory.Power => new Color(0.8f, 0.4f, 0.2f), // Orange-Red
                MotifCategory.Shadow => new Color(0.2f, 0.2f, 0.3f), // Dark Gray
                MotifCategory.Truth => new Color(0.9f, 0.9f, 0.2f), // Bright Yellow
                MotifCategory.Vengeance => new Color(0.9f, 0.1f, 0.1f), // Bright Red
                _ => new Color(0.5f, 0.5f, 0.5f) // Default Gray
            };
        }

        private System.Collections.IEnumerator HighlightCoroutine(float duration)
        {
            _isHighlighted = true;
            
            Color originalColor = _baseColor;
            Color highlightColor = Color.white;
            float originalIntensity = _motifLight?.intensity ?? 0f;
            float highlightIntensity = originalIntensity * 2f;
            
            // Highlight phase
            float elapsed = 0f;
            float highlightTime = 0.3f;
            
            while (elapsed < highlightTime)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / highlightTime;
                
                // Lerp colors
                Color currentColor = Color.Lerp(originalColor, highlightColor, t);
                if (_instanceMaterial != null)
                {
                    _instanceMaterial.color = currentColor;
                    if (_instanceMaterial.HasProperty("_EmissionColor"))
                    {
                        _instanceMaterial.SetColor("_EmissionColor", currentColor * 2f);
                    }
                }
                
                // Lerp light intensity
                if (_motifLight != null)
                {
                    _motifLight.intensity = Mathf.Lerp(originalIntensity, highlightIntensity, t);
                }
                
                yield return null;
            }
            
            // Hold phase
            yield return new WaitForSeconds(duration - (highlightTime * 2));
            
            // Fade back phase
            elapsed = 0f;
            while (elapsed < highlightTime)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / highlightTime;
                
                // Lerp back to original
                Color currentColor = Color.Lerp(highlightColor, originalColor, t);
                if (_instanceMaterial != null)
                {
                    _instanceMaterial.color = currentColor;
                    if (_instanceMaterial.HasProperty("_EmissionColor"))
                    {
                        Color emissionColor = currentColor * (_motif.intensity / 10f);
                        _instanceMaterial.SetColor("_EmissionColor", emissionColor);
                    }
                }
                
                // Lerp light intensity back
                if (_motifLight != null)
                {
                    _motifLight.intensity = Mathf.Lerp(highlightIntensity, originalIntensity, t);
                }
                
                yield return null;
            }
            
            _isHighlighted = false;
        }

        #endregion

        #region Interaction Support

        private void OnMouseDown()
        {
            // Handle click interaction
            if (_motif != null)
            {
                Debug.Log($"Clicked motif: {_motif.name}");
                
                // You can add custom interaction logic here
                // For example, opening a detail panel or triggering events
            }
        }

        private void OnMouseEnter()
        {
            // Handle hover enter
            if (!_isHighlighted)
            {
                // Add subtle hover effect
                if (_instanceMaterial != null)
                {
                    Color hoverColor = _baseColor * 1.2f;
                    _instanceMaterial.color = hoverColor;
                }
            }
        }

        private void OnMouseExit()
        {
            // Handle hover exit
            if (!_isHighlighted)
            {
                // Restore original color
                if (_instanceMaterial != null)
                {
                    _instanceMaterial.color = _baseColor;
                }
            }
        }

        #endregion
    }
} 