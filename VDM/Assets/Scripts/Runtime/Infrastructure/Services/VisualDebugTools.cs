using System.Collections.Generic;
using System;
using UnityEngine.UI;
using UnityEngine;
using VDM.Infrastructure.Core;
using VDM.Systems.Character;
using VDM.Systems.Combat;


namespace VDM.Infrastructure.Debug
{
    /// <summary>
    /// Visual debugging tools and overlays for development
    /// Implements Task 22: Visual Debug Tools with overlays and gizmos
    /// </summary>
    public class VisualDebugTools : MonoBehaviour
    {
        [Header("Debug Display Settings")]
        [SerializeField] private bool showDebugOverlay = false;
        [SerializeField] private bool showPerformanceMetrics = true;
        [SerializeField] private bool showPlayerInfo = true;
        [SerializeField] private bool showSystemInfo = false;
        [SerializeField] private bool showGizmos = true;
        
        [Header("UI Elements")]
        [SerializeField] private Canvas debugCanvas;
        [SerializeField] private Text performanceText;
        [SerializeField] private Text playerInfoText;
        [SerializeField] private Text systemInfoText;
        [SerializeField] private GameObject debugPanel;
        
        [Header("Gizmo Settings")]
        [SerializeField] private bool showPlayerBounds = true;
        [SerializeField] private bool showColliders = true;
        [SerializeField] private bool showMovementPath = true;
        [SerializeField] private bool showCombatRanges = true;
        [SerializeField] private Color gizmoColor = Color.yellow;
        [SerializeField] private Color colliderColor = Color.green;
        [SerializeField] private Color combatRangeColor = Color.red;
        
        // Singleton instance
        public static VisualDebugTools Instance { get; private set; }
        
        // Performance tracking
        private float _fpsUpdateInterval = 1.0f;
        private float _fpsAccumulator = 0.0f;
        private int _frames = 0;
        private float _timeLeft;
        private float _currentFPS = 0.0f;
        
        // Player tracking (commented out due to missing classes)
        // private PlayerMovement _playerMovement;
        // private BasicCombatSystem _playerCombat;
        private Transform _playerTransform;
        private Vector3 _lastPlayerPosition;
        private List<Vector3> _movementPath = new List<Vector3>();
        
        // Update intervals
        private float _uiUpdateInterval = 0.1f;
        private float _uiUpdateTimer = 0.0f;
        
        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                Initialize();
            }
            else
            {
                Destroy(gameObject);
            }
        }
        
        private void Initialize()
        {
            CreateDebugUI();
            FindPlayerComponents();
            
            // Initialize performance tracking
            _timeLeft = _fpsUpdateInterval;
            
            // Subscribe to console events
            if (DebugConsole.Instance != null)
            {
                DebugConsole.Instance.OnConsoleToggled += OnConsoleToggled;
            }
        }
        
        private void CreateDebugUI()
        {
            if (debugCanvas == null)
            {
                // Create debug canvas
                var canvasGO = new GameObject("DebugCanvas");
                debugCanvas = canvasGO.AddComponent<Canvas>();
                debugCanvas.renderMode = RenderMode.ScreenSpaceOverlay;
                debugCanvas.sortingOrder = 100; // High priority
                
                var scaler = canvasGO.AddComponent<CanvasScaler>();
                scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
                scaler.referenceResolution = new Vector2(1920, 1080);
                
                canvasGO.AddComponent<GraphicRaycaster>();
            }
            
            // Create debug panel
            if (debugPanel == null)
            {
                debugPanel = new GameObject("DebugPanel");
                debugPanel.transform.SetParent(debugCanvas.transform, false);
                
                var rectTransform = debugPanel.AddComponent<RectTransform>();
                rectTransform.anchorMin = new Vector2(0, 0.7f);
                rectTransform.anchorMax = new Vector2(0.3f, 1);
                rectTransform.sizeDelta = Vector2.zero;
                rectTransform.anchoredPosition = Vector2.zero;
                
                // Background
                var image = debugPanel.AddComponent<Image>();
                image.color = new Color(0, 0, 0, 0.5f);
            }
            
            CreatePerformanceDisplay();
            CreatePlayerInfoDisplay();
            CreateSystemInfoDisplay();
            
            SetDebugOverlayVisible(showDebugOverlay);
        }
        
        private void CreatePerformanceDisplay()
        {
            var perfGO = new GameObject("PerformanceText");
            perfGO.transform.SetParent(debugPanel.transform, false);
            
            var rectTransform = perfGO.AddComponent<RectTransform>();
            rectTransform.anchorMin = new Vector2(0, 0.8f);
            rectTransform.anchorMax = new Vector2(1, 1);
            rectTransform.sizeDelta = Vector2.zero;
            rectTransform.anchoredPosition = Vector2.zero;
            
            performanceText = perfGO.AddComponent<Text>();
            performanceText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            performanceText.fontSize = 12;
            performanceText.color = Color.white;
            performanceText.alignment = TextAnchor.UpperLeft;
            performanceText.text = "Performance: Loading...";
        }
        
        private void CreatePlayerInfoDisplay()
        {
            var playerGO = new GameObject("PlayerInfoText");
            playerGO.transform.SetParent(debugPanel.transform, false);
            
            var rectTransform = playerGO.AddComponent<RectTransform>();
            rectTransform.anchorMin = new Vector2(0, 0.5f);
            rectTransform.anchorMax = new Vector2(1, 0.8f);
            rectTransform.sizeDelta = Vector2.zero;
            rectTransform.anchoredPosition = Vector2.zero;
            
            playerInfoText = playerGO.AddComponent<Text>();
            playerInfoText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            playerInfoText.fontSize = 11;
            playerInfoText.color = Color.cyan;
            playerInfoText.alignment = TextAnchor.UpperLeft;
            playerInfoText.text = "Player: Loading...";
        }
        
        private void CreateSystemInfoDisplay()
        {
            var systemGO = new GameObject("SystemInfoText");
            systemGO.transform.SetParent(debugPanel.transform, false);
            
            var rectTransform = systemGO.AddComponent<RectTransform>();
            rectTransform.anchorMin = new Vector2(0, 0);
            rectTransform.anchorMax = new Vector2(1, 0.5f);
            rectTransform.sizeDelta = Vector2.zero;
            rectTransform.anchoredPosition = Vector2.zero;
            
            systemInfoText = systemGO.AddComponent<Text>();
            systemInfoText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            systemInfoText.fontSize = 10;
            systemInfoText.color = Color.yellow;
            systemInfoText.alignment = TextAnchor.UpperLeft;
            systemInfoText.text = "System: Loading...";
        }
        
        private void FindPlayerComponents()
        {
            var player = GameObject.FindWithTag("Player") ?? FindObjectOfType<PlayerMovement>()?.gameObject;
            if (player != null)
            {
                _playerTransform = player.transform;
                _lastPlayerPosition = player.transform.position;
            }
        }
        
        private void Update()
        {
            UpdatePerformanceMetrics();
            UpdateUIDisplays();
            UpdateMovementPath();
            HandleDebugInput();
        }
        
        private void UpdatePerformanceMetrics()
        {
            _timeLeft -= Time.deltaTime;
            _fpsAccumulator += Time.timeScale / Time.deltaTime;
            _frames++;
            
            if (_timeLeft <= 0.0)
            {
                _currentFPS = _fpsAccumulator / _frames;
                _timeLeft = _fpsUpdateInterval;
                _fpsAccumulator = 0.0f;
                _frames = 0;
            }
        }
        
        private void UpdateUIDisplays()
        {
            _uiUpdateTimer += Time.deltaTime;
            if (_uiUpdateTimer >= _uiUpdateInterval)
            {
                _uiUpdateTimer = 0.0f;
                
                if (showDebugOverlay)
                {
                    UpdatePerformanceText();
                    UpdatePlayerInfoText();
                    UpdateSystemInfoText();
                }
            }
        }
        
        private void UpdatePerformanceText()
        {
            if (performanceText != null && showPerformanceMetrics)
            {
                var memory = System.GC.GetTotalMemory(false) / (1024f * 1024f);
                var monitoring = MonitoringManager.Instance;
                
                var text = $"=== PERFORMANCE ===\n" +
                          $"FPS: {_currentFPS:F1}\n" +
                          $"Frame Time: {(Time.deltaTime * 1000):F1}ms\n" +
                          $"Time Scale: {Time.timeScale:F2}\n" +
                          $"Memory: {memory:F1}MB\n" +
                          $"Frame Count: {Time.frameCount}";
                
                if (monitoring != null)
                {
                    var metrics = monitoring.GetRecentMetrics();
                    if (metrics.Count > 0)
                    {
                        var latestMetric = metrics[metrics.Count - 1];
                        text += $"\nLast Metric: {latestMetric.Name} = {latestMetric.Value:F2}";
                    }
                }
                
                performanceText.text = text;
                performanceText.gameObject.SetActive(true);
            }
            else if (performanceText != null)
            {
                performanceText.gameObject.SetActive(false);
            }
        }
        
        private void UpdatePlayerInfoText()
        {
            if (playerInfoText != null && showPlayerInfo)
            {
                if (_playerTransform == null)
                {
                    FindPlayerComponents();
                }
                
                var text = "=== PLAYER ===\n";
                
                if (_playerTransform != null)
                {
                    text += $"Position: {_playerTransform.position:F2}\n" +
                           $"Speed: {_playerTransform.GetComponent<PlayerMovement>()?.GetMoveSpeed():F1}\n" +
                           $"Mouse Move: {_playerTransform.GetComponent<PlayerMovement>()?.IsMouseMovementEnabled()}\n";
                }
                
                if (_playerTransform != null && _playerTransform.GetComponent<BasicCombatSystem>() != null)
                {
                    text += $"Health: {_playerTransform.GetComponent<BasicCombatSystem>().GetCurrentHealth():F0}/{_playerTransform.GetComponent<BasicCombatSystem>().GetMaxHealth():F0}\n" +
                           $"State: {_playerTransform.GetComponent<BasicCombatSystem>().GetCurrentState()}\n";
                }
                
                if (_playerTransform == null)
                {
                    text += "No player found";
                }
                
                playerInfoText.text = text;
                playerInfoText.gameObject.SetActive(true);
            }
            else if (playerInfoText != null)
            {
                playerInfoText.gameObject.SetActive(false);
            }
        }
        
        private void UpdateSystemInfoText()
        {
            if (systemInfoText != null && showSystemInfo)
            {
                var activeScene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
                var objectCount = FindObjectsOfType<GameObject>().Length;
                
                var text = $"=== SYSTEM ===\n" +
                          $"Scene: {activeScene.name}\n" +
                          $"Objects: {objectCount}\n" +
                          $"Quality: {QualitySettings.names[QualitySettings.GetQualityLevel()]}\n" +
                          $"Platform: {Application.platform}\n" +
                          $"Unity: {Application.unityVersion}";
                
                systemInfoText.text = text;
                systemInfoText.gameObject.SetActive(true);
            }
            else if (systemInfoText != null)
            {
                systemInfoText.gameObject.SetActive(false);
            }
        }
        
        private void UpdateMovementPath()
        {
            if (_playerTransform != null && showMovementPath)
            {
                var currentPos = _playerTransform.position;
                if (Vector3.Distance(currentPos, _lastPlayerPosition) > 0.5f)
                {
                    _movementPath.Add(currentPos);
                    _lastPlayerPosition = currentPos;
                    
                    // Limit path length
                    if (_movementPath.Count > 50)
                    {
                        _movementPath.RemoveAt(0);
                    }
                }
            }
        }
        
        private void HandleDebugInput()
        {
            // Toggle debug overlay with F1
            if (Input.GetKeyDown(KeyCode.F1))
            {
                ToggleDebugOverlay();
            }
            
            // Toggle performance metrics with F2
            if (Input.GetKeyDown(KeyCode.F2))
            {
                TogglePerformanceMetrics();
            }
            
            // Toggle player info with F3
            if (Input.GetKeyDown(KeyCode.F3))
            {
                TogglePlayerInfo();
            }
            
            // Toggle system info with F4
            if (Input.GetKeyDown(KeyCode.F4))
            {
                ToggleSystemInfo();
            }
            
            // Toggle gizmos with F5
            if (Input.GetKeyDown(KeyCode.F5))
            {
                ToggleGizmos();
            }
        }
        
        private void OnDrawGizmos()
        {
            if (!showGizmos) return;
            
            DrawPlayerGizmos();
            DrawColliderGizmos();
            DrawCombatGizmos();
            DrawMovementPath();
        }
        
        private void DrawPlayerGizmos()
        {
            if (_playerTransform == null || !showPlayerBounds) return;
            
            var playerPos = _playerTransform.position;
            
            // Player bounds
            Gizmos.color = gizmoColor;
            Gizmos.DrawWireCube(playerPos, Vector3.one);
            
            // Player direction indicator
            var velocity = _playerTransform.GetComponent<Rigidbody2D>()?.velocity ?? Vector2.zero;
            if (velocity.magnitude > 0.1f)
            {
                Gizmos.color = Color.blue;
                Gizmos.DrawRay(playerPos, velocity.normalized * 2f);
            }
        }
        
        private void DrawColliderGizmos()
        {
            if (!showColliders) return;
            
            var colliders = FindObjectsOfType<Collider2D>();
            Gizmos.color = colliderColor;
            
            foreach (var collider in colliders)
            {
                if (collider.gameObject.activeInHierarchy)
                {
                    DrawCollider2D(collider);
                }
            }
        }
        
        private void DrawCollider2D(Collider2D collider)
        {
            var bounds = collider.bounds;
            
            if (collider is BoxCollider2D)
            {
                Gizmos.DrawWireCube(bounds.center, bounds.size);
            }
            else if (collider is CircleCollider2D circle)
            {
                Gizmos.DrawWireSphere(bounds.center, circle.radius);
            }
            else
            {
                // Generic bounds for other collider types
                Gizmos.DrawWireCube(bounds.center, bounds.size);
            }
        }
        
        private void DrawCombatGizmos()
        {
            if (!showCombatRanges) return;
            
            // Commented out due to missing BasicCombatSystem class
            /*
            var combatSystems = FindObjectsOfType<BasicCombatSystem>();
            Gizmos.color = combatRangeColor;
            
            foreach (var combat in combatSystems)
            {
                if (combat.gameObject.activeInHierarchy)
                {
                    var pos = combat.transform.position;
                    var attackRange = combat.GetAttackRange();
                    
                    // Attack range circle
                    Gizmos.DrawWireSphere(pos, attackRange);
                    
                    // Current target line
                    var target = combat.GetCurrentTarget();
                    if (target != null)
                    {
                        Gizmos.color = Color.red;
                        Gizmos.DrawLine(pos, target.transform.position);
                        Gizmos.color = combatRangeColor;
                    }
                }
            }
            */
        }
        
        private void DrawMovementPath()
        {
            if (!showMovementPath || _movementPath.Count < 2) return;
            
            Gizmos.color = Color.white;
            for (int i = 1; i < _movementPath.Count; i++)
            {
                Gizmos.DrawLine(_movementPath[i - 1], _movementPath[i]);
            }
            
            // Draw path nodes
            Gizmos.color = Color.green;
            foreach (var point in _movementPath)
            {
                Gizmos.DrawWireSphere(point, 0.1f);
            }
        }
        
        private void OnConsoleToggled(bool isOpen)
        {
            // Adjust debug overlay when console is open
            if (debugPanel != null)
            {
                var rectTransform = debugPanel.GetComponent<RectTransform>();
                if (isOpen)
                {
                    // Move debug panel to not overlap with console
                    rectTransform.anchorMin = new Vector2(0.7f, 0.7f);
                    rectTransform.anchorMax = new Vector2(1, 1);
                }
                else
                {
                    // Restore original position
                    rectTransform.anchorMin = new Vector2(0, 0.7f);
                    rectTransform.anchorMax = new Vector2(0.3f, 1);
                }
            }
        }
        
        #region Public API
        
        public void ToggleDebugOverlay()
        {
            SetDebugOverlayVisible(!showDebugOverlay);
        }
        
        public void SetDebugOverlayVisible(bool visible)
        {
            showDebugOverlay = visible;
            if (debugPanel != null)
            {
                debugPanel.SetActive(visible);
            }
        }
        
        public void TogglePerformanceMetrics()
        {
            showPerformanceMetrics = !showPerformanceMetrics;
        }
        
        public void TogglePlayerInfo()
        {
            showPlayerInfo = !showPlayerInfo;
        }
        
        public void ToggleSystemInfo()
        {
            showSystemInfo = !showSystemInfo;
        }
        
        public void ToggleGizmos()
        {
            showGizmos = !showGizmos;
        }
        
        public void SetGizmoColors(Color gizmo, Color collider, Color combat)
        {
            gizmoColor = gizmo;
            colliderColor = collider;
            combatRangeColor = combat;
        }
        
        public void ClearMovementPath()
        {
            _movementPath.Clear();
        }
        
        #endregion
        
        #region Console Commands
        
        [ConsoleCommand("debug.overlay", "Toggle debug overlay")]
        public static string ToggleOverlay()
        {
            if (Instance != null)
            {
                Instance.ToggleDebugOverlay();
                return $"Debug overlay: {(Instance.showDebugOverlay ? "ON" : "OFF")}";
            }
            return "VisualDebugTools not available";
        }
        
        [ConsoleCommand("debug.performance", "Toggle performance metrics")]
        public static string TogglePerformance()
        {
            if (Instance != null)
            {
                Instance.TogglePerformanceMetrics();
                return $"Performance metrics: {(Instance.showPerformanceMetrics ? "ON" : "OFF")}";
            }
            return "VisualDebugTools not available";
        }
        
        [ConsoleCommand("debug.gizmos", "Toggle debug gizmos")]
        public static string ToggleGizmosCommand()
        {
            if (Instance != null)
            {
                Instance.ToggleGizmos();
                return $"Debug gizmos: {(Instance.showGizmos ? "ON" : "OFF")}";
            }
            return "VisualDebugTools not available";
        }
        
        [ConsoleCommand("debug.clear_path", "Clear movement path")]
        public static string ClearPath()
        {
            if (Instance != null)
            {
                Instance.ClearMovementPath();
                return "Movement path cleared";
            }
            return "VisualDebugTools not available";
        }
        
        #endregion
    }
} 