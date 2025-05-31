using System.Collections;
using UnityEngine;
using VDM.Systems.Motifs.Models;
using TMPro;

namespace VDM.Systems.Motifs.Visualization
{
    /// <summary>
    /// Component for visualizing motifs in the 3D world
    /// </summary>
    public class MotifVisualizer : MonoBehaviour
    {
        [Header("Visual Components")]
        [SerializeField] private Renderer motifRenderer;
        [SerializeField] private ParticleSystem particleSystem;
        [SerializeField] private Light motifLight;
        [SerializeField] private TextMeshPro nameText;
        [SerializeField] private TextMeshPro descriptionText;
        [SerializeField] private SphereCollider influenceCollider;

        [Header("Visual Settings")]
        [SerializeField] private bool showInfluenceRadius = true;
        [SerializeField] private bool enableParticles = true;
        [SerializeField] private bool enableLighting = true;
        [SerializeField] private bool showText = true;
        [SerializeField] private float textDistance = 10f;
        [SerializeField] private AnimationCurve intensityCurve = AnimationCurve.Linear(0, 0, 1, 1);

        [Header("Category Colors")]
        [SerializeField] private Color defaultColor = Color.white;
        [SerializeField] private Color hopeColor = Color.yellow;
        [SerializeField] private Color fearColor = Color.red;
        [SerializeField] private Color chaosColor = Color.magenta;
        [SerializeField] private Color peaceColor = Color.blue;
        [SerializeField] private Color powerColor = Color.cyan;
        [SerializeField] private Color deathColor = Color.black;

        // State
        private Motif _currentMotif;
        private Camera _playerCamera;
        private bool _isInitialized;
        private Coroutine _animationCoroutine;

        #region Unity Lifecycle

        private void Awake()
        {
            Initialize();
        }

        private void Start()
        {
            _playerCamera = Camera.main;
            if (_playerCamera == null)
                _playerCamera = FindObjectOfType<Camera>();
        }

        private void Update()
        {
            if (_currentMotif != null && _playerCamera != null)
            {
                UpdateTextVisibility();
                UpdateLifecycleAnimation();
            }
        }

        private void OnDestroy()
        {
            if (_animationCoroutine != null)
            {
                StopCoroutine(_animationCoroutine);
            }
        }

        #endregion

        #region Initialization

        private void Initialize()
        {
            // Auto-find components if not assigned
            if (motifRenderer == null)
                motifRenderer = GetComponent<Renderer>();

            if (particleSystem == null)
                particleSystem = GetComponentInChildren<ParticleSystem>();

            if (motifLight == null)
                motifLight = GetComponentInChildren<Light>();

            if (nameText == null)
                nameText = GetComponentInChildren<TextMeshPro>();

            if (influenceCollider == null)
                influenceCollider = GetComponent<SphereCollider>();

            // Create default components if missing
            CreateDefaultComponents();

            _isInitialized = true;
        }

        private void CreateDefaultComponents()
        {
            // Create default renderer if missing
            if (motifRenderer == null)
            {
                var sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                sphere.transform.SetParent(transform);
                sphere.transform.localPosition = Vector3.zero;
                sphere.transform.localScale = Vector3.one;
                motifRenderer = sphere.GetComponent<Renderer>();
                
                // Remove the collider from the visual sphere
                var collider = sphere.GetComponent<Collider>();
                if (collider != null)
                    DestroyImmediate(collider);
            }

            // Create influence collider if missing
            if (influenceCollider == null)
            {
                influenceCollider = gameObject.AddComponent<SphereCollider>();
                influenceCollider.isTrigger = true;
            }

            // Create particle system if missing and enabled
            if (particleSystem == null && enableParticles)
            {
                var particleGO = new GameObject("Particles");
                particleGO.transform.SetParent(transform);
                particleGO.transform.localPosition = Vector3.zero;
                particleSystem = particleGO.AddComponent<ParticleSystem>();
                ConfigureDefaultParticles();
            }

            // Create light if missing and enabled
            if (motifLight == null && enableLighting)
            {
                var lightGO = new GameObject("Light");
                lightGO.transform.SetParent(transform);
                lightGO.transform.localPosition = Vector3.up * 2f;
                motifLight = lightGO.AddComponent<Light>();
                motifLight.type = LightType.Point;
                motifLight.range = 10f;
                motifLight.intensity = 1f;
            }

            // Create text if missing and enabled
            if (nameText == null && showText)
            {
                var textGO = new GameObject("NameText");
                textGO.transform.SetParent(transform);
                textGO.transform.localPosition = Vector3.up * 3f;
                nameText = textGO.AddComponent<TextMeshPro>();
                nameText.text = "Motif";
                nameText.fontSize = 4f;
                nameText.alignment = TextAlignmentOptions.Center;
                nameText.color = Color.white;
            }
        }

        private void ConfigureDefaultParticles()
        {
            if (particleSystem == null) return;

            var main = particleSystem.main;
            main.startLifetime = 3f;
            main.startSpeed = 2f;
            main.startSize = 0.1f;
            main.startColor = defaultColor;
            main.maxParticles = 50;

            var emission = particleSystem.emission;
            emission.rateOverTime = 10f;

            var shape = particleSystem.shape;
            shape.enabled = true;
            shape.shapeType = ParticleSystemShapeType.Sphere;
            shape.radius = 1f;

            var velocityOverLifetime = particleSystem.velocityOverLifetime;
            velocityOverLifetime.enabled = true;
            velocityOverLifetime.space = ParticleSystemSimulationSpace.Local;
            velocityOverLifetime.radial = new ParticleSystem.MinMaxCurve(1f);
        }

        #endregion

        #region Public API

        /// <summary>
        /// Set the motif to visualize
        /// </summary>
        public void SetMotif(Motif motif)
        {
            _currentMotif = motif;
            
            if (!_isInitialized)
                Initialize();

            UpdateVisualization();
        }

        /// <summary>
        /// Get the current motif
        /// </summary>
        public Motif GetMotif()
        {
            return _currentMotif;
        }

        /// <summary>
        /// Update the visualization based on current motif
        /// </summary>
        public void UpdateVisualization()
        {
            if (_currentMotif == null) return;

            UpdateColors();
            UpdateScale();
            UpdateText();
            UpdateInfluenceRadius();
            UpdateParticles();
            UpdateLighting();
            StartLifecycleAnimation();
        }

        #endregion

        #region Visual Updates

        private void UpdateColors()
        {
            Color motifColor = GetCategoryColor(_currentMotif.category);
            
            // Apply lifecycle modulation
            float alpha = GetLifecycleAlpha();
            motifColor.a = alpha;

            // Update renderer
            if (motifRenderer != null)
            {
                var material = motifRenderer.material;
                material.color = motifColor;
                
                // Add emission for active motifs
                if (_currentMotif.IsActive())
                {
                    material.SetColor("_EmissionColor", motifColor * 0.5f);
                    material.EnableKeyword("_EMISSION");
                }
            }

            // Update light
            if (motifLight != null && enableLighting)
            {
                motifLight.color = motifColor;
                motifLight.intensity = _currentMotif.GetInfluenceStrength() * 2f;
            }
        }

        private void UpdateScale()
        {
            float scale = _currentMotif.GetInfluenceStrength();
            scale = intensityCurve.Evaluate(scale);
            
            // Base scale between 0.5 and 2.0
            scale = Mathf.Lerp(0.5f, 2f, scale);
            
            transform.localScale = Vector3.one * scale;
        }

        private void UpdateText()
        {
            if (nameText != null && showText)
            {
                nameText.text = _currentMotif.name;
                nameText.color = GetCategoryColor(_currentMotif.category);
                
                // Add lifecycle indicator
                string lifecycleIcon = GetLifecycleIcon(_currentMotif.lifecycle);
                nameText.text = $"{lifecycleIcon} {_currentMotif.name}";
            }

            if (descriptionText != null && showText)
            {
                descriptionText.text = _currentMotif.description;
                descriptionText.color = Color.white;
                descriptionText.alpha = 0.7f;
            }
        }

        private void UpdateInfluenceRadius()
        {
            if (influenceCollider != null && _currentMotif.location != null)
            {
                influenceCollider.radius = _currentMotif.location.radius;
                influenceCollider.enabled = showInfluenceRadius;
            }
        }

        private void UpdateParticles()
        {
            if (particleSystem == null || !enableParticles) return;

            var main = particleSystem.main;
            main.startColor = GetCategoryColor(_currentMotif.category);
            
            var emission = particleSystem.emission;
            emission.rateOverTime = _currentMotif.GetInfluenceStrength() * 20f;
            
            // Adjust particle behavior based on category
            UpdateParticlesByCategory();
        }

        private void UpdateParticlesByCategory()
        {
            if (particleSystem == null) return;

            var velocityOverLifetime = particleSystem.velocityOverLifetime;
            var forceOverLifetime = particleSystem.forceOverLifetime;

            switch (_currentMotif.category)
            {
                case MotifCategory.Chaos:
                    velocityOverLifetime.radial = new ParticleSystem.MinMaxCurve(3f);
                    forceOverLifetime.enabled = true;
                    forceOverLifetime.randomized = true;
                    break;
                    
                case MotifCategory.Peace:
                    velocityOverLifetime.radial = new ParticleSystem.MinMaxCurve(0.5f);
                    var main = particleSystem.main;
                    main.startSpeed = 0.5f;
                    break;
                    
                case MotifCategory.Power:
                    velocityOverLifetime.radial = new ParticleSystem.MinMaxCurve(2f);
                    var emission = particleSystem.emission;
                    emission.rateOverTime = _currentMotif.GetInfluenceStrength() * 30f;
                    break;
                    
                case MotifCategory.Death:
                    velocityOverLifetime.radial = new ParticleSystem.MinMaxCurve(-1f);
                    var mainDeath = particleSystem.main;
                    mainDeath.startColor = Color.black;
                    break;
            }
        }

        private void UpdateLighting()
        {
            if (motifLight == null || !enableLighting) return;

            motifLight.enabled = _currentMotif.IsActive();
            
            if (_currentMotif.location != null)
            {
                motifLight.range = _currentMotif.location.radius * 0.5f;
            }
            
            // Flicker effect for certain categories
            if (_currentMotif.category == MotifCategory.Chaos || _currentMotif.category == MotifCategory.Fear)
            {
                StartFlickerEffect();
            }
        }

        private void UpdateTextVisibility()
        {
            if (nameText == null || _playerCamera == null) return;

            float distance = Vector3.Distance(transform.position, _playerCamera.transform.position);
            bool shouldShow = showText && distance <= textDistance;
            
            nameText.gameObject.SetActive(shouldShow);
            
            if (descriptionText != null)
            {
                descriptionText.gameObject.SetActive(shouldShow && distance <= textDistance * 0.5f);
            }

            // Face the camera
            if (shouldShow)
            {
                nameText.transform.LookAt(_playerCamera.transform);
                nameText.transform.Rotate(0, 180, 0);
                
                if (descriptionText != null)
                {
                    descriptionText.transform.LookAt(_playerCamera.transform);
                    descriptionText.transform.Rotate(0, 180, 0);
                }
            }
        }

        private void UpdateLifecycleAnimation()
        {
            // Continuous updates based on lifecycle
            switch (_currentMotif.lifecycle)
            {
                case MotifLifecycle.Emerging:
                    AnimateEmerging();
                    break;
                case MotifLifecycle.Waning:
                    AnimateWaning();
                    break;
                case MotifLifecycle.Fading:
                    AnimateFading();
                    break;
            }
        }

        #endregion

        #region Animation

        private void StartLifecycleAnimation()
        {
            if (_animationCoroutine != null)
            {
                StopCoroutine(_animationCoroutine);
            }

            switch (_currentMotif.lifecycle)
            {
                case MotifLifecycle.Emerging:
                    _animationCoroutine = StartCoroutine(EmergingAnimation());
                    break;
                case MotifLifecycle.Fading:
                    _animationCoroutine = StartCoroutine(FadingAnimation());
                    break;
            }
        }

        private IEnumerator EmergingAnimation()
        {
            float duration = 2f;
            float elapsed = 0f;
            Vector3 startScale = Vector3.zero;
            Vector3 targetScale = transform.localScale;

            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float progress = elapsed / duration;
                transform.localScale = Vector3.Lerp(startScale, targetScale, progress);
                yield return null;
            }

            transform.localScale = targetScale;
        }

        private IEnumerator FadingAnimation()
        {
            float duration = 3f;
            float elapsed = 0f;
            Vector3 startScale = transform.localScale;
            Vector3 targetScale = Vector3.zero;

            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float progress = elapsed / duration;
                transform.localScale = Vector3.Lerp(startScale, targetScale, progress);
                
                // Fade out materials
                if (motifRenderer != null)
                {
                    var material = motifRenderer.material;
                    var color = material.color;
                    color.a = 1f - progress;
                    material.color = color;
                }

                yield return null;
            }

            // Destroy when fully faded
            Destroy(gameObject);
        }

        private void AnimateEmerging()
        {
            // Gentle pulsing effect
            float pulse = Mathf.Sin(Time.time * 2f) * 0.1f + 1f;
            transform.localScale = Vector3.one * pulse * _currentMotif.GetInfluenceStrength();
        }

        private void AnimateWaning()
        {
            // Slower, irregular pulsing
            float pulse = Mathf.Sin(Time.time * 0.5f) * 0.2f + 0.8f;
            transform.localScale = Vector3.one * pulse * _currentMotif.GetInfluenceStrength();
        }

        private void AnimateFading()
        {
            // Flickering effect
            float flicker = Random.Range(0.3f, 1f);
            if (motifRenderer != null)
            {
                var material = motifRenderer.material;
                var color = material.color;
                color.a = flicker * 0.5f;
                material.color = color;
            }
        }

        private void StartFlickerEffect()
        {
            if (motifLight != null && Random.Range(0f, 1f) < 0.1f)
            {
                motifLight.intensity = Random.Range(0.5f, 2f) * _currentMotif.GetInfluenceStrength();
            }
        }

        #endregion

        #region Helper Methods

        private Color GetCategoryColor(MotifCategory category)
        {
            return category switch
            {
                MotifCategory.Hope => hopeColor,
                MotifCategory.Fear => fearColor,
                MotifCategory.Chaos => chaosColor,
                MotifCategory.Peace => peaceColor,
                MotifCategory.Power => powerColor,
                MotifCategory.Death => deathColor,
                _ => defaultColor
            };
        }

        private float GetLifecycleAlpha()
        {
            return _currentMotif.lifecycle switch
            {
                MotifLifecycle.Dormant => 0.2f,
                MotifLifecycle.Emerging => 0.6f,
                MotifLifecycle.Stable => 1f,
                MotifLifecycle.Waning => 0.7f,
                MotifLifecycle.Fading => 0.3f,
                _ => 1f
            };
        }

        private string GetLifecycleIcon(MotifLifecycle lifecycle)
        {
            return lifecycle switch
            {
                MotifLifecycle.Dormant => "💤",
                MotifLifecycle.Emerging => "🌱",
                MotifLifecycle.Stable => "⭐",
                MotifLifecycle.Waning => "🌙",
                MotifLifecycle.Fading => "💨",
                _ => "❓"
            };
        }

        #endregion

        #region Configuration

        /// <summary>
        /// Enable or disable influence radius visualization
        /// </summary>
        public void SetInfluenceRadiusVisible(bool visible)
        {
            showInfluenceRadius = visible;
            if (influenceCollider != null)
            {
                influenceCollider.enabled = visible;
            }
        }

        /// <summary>
        /// Enable or disable particle effects
        /// </summary>
        public void SetParticlesEnabled(bool enabled)
        {
            enableParticles = enabled;
            if (particleSystem != null)
            {
                if (enabled)
                    particleSystem.Play();
                else
                    particleSystem.Stop();
            }
        }

        /// <summary>
        /// Enable or disable lighting effects
        /// </summary>
        public void SetLightingEnabled(bool enabled)
        {
            enableLighting = enabled;
            if (motifLight != null)
            {
                motifLight.enabled = enabled && _currentMotif?.IsActive() == true;
            }
        }

        /// <summary>
        /// Enable or disable text display
        /// </summary>
        public void SetTextEnabled(bool enabled)
        {
            showText = enabled;
            if (nameText != null)
            {
                nameText.gameObject.SetActive(enabled);
            }
            if (descriptionText != null)
            {
                descriptionText.gameObject.SetActive(enabled);
            }
        }

        #endregion
    }
} 