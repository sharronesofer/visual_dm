using UnityEngine;
using System.Collections.Generic;
using VisualDM.Core;

namespace VisualDM.UI
{
    /// <summary>
    /// Manages runtime UI panels and navigation for the game. All UI is generated at runtime.
    /// </summary>
    /// <remarks>
    /// This singleton is created at runtime and persists across scenes. All UI panels are generated and managed here.
    /// </remarks>
    /// <example>
    /// <code>
    /// // Access the UIManager singleton
    /// var ui = UIManager.Instance;
    /// // Create a new panel
    /// var panel = ui.CreatePanel("InventoryPanel", new Vector2(400, 300), new Vector2(0, 0), Color.gray);
    /// // Show the panel
    /// ui.ShowPanel("InventoryPanel");
    /// </code>
    /// </example>
    public class UIManager : MonoBehaviour
    {
        private static UIManager _instance;
        /// <summary>
        /// Singleton instance of the UIManager. Created at runtime if not present.
        /// </summary>
        /// <remarks>
        /// Access this property to interact with the UI system. The instance is created automatically if it does not exist.
        /// </remarks>
        public static UIManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    GameObject go = new GameObject("UIManager");
                    _instance = go.AddComponent<UIManager>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        private readonly Dictionary<string, GameObject> panels = new Dictionary<string, GameObject>();
        private GameObject currentPanel;

        /// <summary>
        /// Breakpoint categories for responsive UI layout.
        /// </summary>
        /// <remarks>
        /// Used to adapt UI layout to different screen sizes at runtime.
        /// </remarks>
        public enum Breakpoint { Mobile, Tablet, Desktop, LargeDesktop }

        /// <summary>
        /// The current UI breakpoint, updated automatically on screen resize.
        /// </summary>
        public Breakpoint CurrentBreakpoint { get; private set; }

        /// <summary>
        /// Event triggered when the UI breakpoint changes (e.g., on screen resize).
        /// </summary>
        /// <remarks>
        /// Subscribe to this event to update UI layout dynamically.
        /// </remarks>
        public event System.Action<Breakpoint> OnBreakpointChanged;

        private Vector2Int lastScreenSize;

        void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            _instance = this;
            DontDestroyOnLoad(gameObject);
        }

        void Start()
        {
            lastScreenSize = new Vector2Int(Screen.width, Screen.height);
            UpdateBreakpoint();
        }

        void Update()
        {
            if (Screen.width != lastScreenSize.x || Screen.height != lastScreenSize.y)
            {
                lastScreenSize = new Vector2Int(Screen.width, Screen.height);
                UpdateBreakpoint();
            }
        }

        private void UpdateBreakpoint()
        {
            Breakpoint newBreakpoint = GetBreakpoint(Screen.width);
            if (newBreakpoint != CurrentBreakpoint)
            {
                CurrentBreakpoint = newBreakpoint;
                OnBreakpointChanged?.Invoke(CurrentBreakpoint);
            }
        }

        /// <summary>
        /// Determines the breakpoint category for a given screen width.
        /// </summary>
        /// <param name="width">The screen width in pixels.</param>
        /// <returns>The corresponding <see cref="Breakpoint"/> value.</returns>
        /// <example>
        /// <code>
        /// var bp = UIManager.Instance.GetBreakpoint(Screen.width);
        /// </code>
        /// </example>
        public Breakpoint GetBreakpoint(int width)
        {
            if (width < 600) return Breakpoint.Mobile;
            if (width < 900) return Breakpoint.Tablet;
            if (width < 1400) return Breakpoint.Desktop;
            return Breakpoint.LargeDesktop;
        }

        /// <summary>
        /// Create and register a new UI panel at runtime.
        /// </summary>
        /// <param name="panelName">Unique name for the panel.</param>
        /// <param name="size">Size of the panel in pixels.</param>
        /// <param name="position">Position of the panel in world space.</param>
        /// <param name="bgColor">Background color of the panel.</param>
        /// <returns>The created <see cref="GameObject"/> representing the panel.</returns>
        /// <remarks>
        /// Panels are generated at runtime and managed by the UIManager. Use <see cref="ShowPanel"/> to display.
        /// </remarks>
        /// <example>
        /// <code>
        /// var panel = UIManager.Instance.CreatePanel("SettingsPanel", new Vector2(300, 200), new Vector2(0, 0), Color.white);
        /// </code>
        /// </example>
        public GameObject CreatePanel(string panelName, Vector2 size, Vector2 position, Color bgColor)
        {
            if (panels.ContainsKey(panelName))
                return panels[panelName];

            GameObject panel = new GameObject(panelName);
            panel.transform.SetParent(transform);
            panel.transform.localPosition = new Vector3(position.x, position.y, 0);

            // Add a SpriteRenderer for 2D UI background
            var sr = panel.AddComponent<SpriteRenderer>();
            sr.sprite = GenerateRectSprite((int)size.x, (int)size.y, bgColor);
            sr.sortingOrder = 100; // UI on top

            panels[panelName] = panel;
            panel.SetActive(false);
            return panel;
        }

        /// <summary>
        /// Show a registered panel and hide the current one.
        /// </summary>
        /// <param name="panelName">The name of the panel to show.</param>
        /// <remarks>
        /// Only one panel is visible at a time. Hides the previously active panel.
        /// </remarks>
        /// <example>
        /// <code>
        /// UIManager.Instance.ShowPanel("InventoryPanel");
        /// </code>
        /// </example>
        public void ShowPanel(string panelName)
        {
            if (currentPanel != null)
                currentPanel.SetActive(false);
            if (panels.TryGetValue(panelName, out var panel))
            {
                panel.SetActive(true);
                currentPanel = panel;
            }
        }

        /// <summary>
        /// Hide a specific panel.
        /// </summary>
        /// <param name="panelName">The name of the panel to hide.</param>
        /// <example>
        /// <code>
        /// UIManager.Instance.HidePanel("SettingsPanel");
        /// </code>
        /// </example>
        public void HidePanel(string panelName)
        {
            if (panels.TryGetValue(panelName, out var panel))
                panel.SetActive(false);
        }

        /// <summary>
        /// Utility to generate a solid color rectangle sprite for UI backgrounds.
        /// </summary>
        private Sprite GenerateRectSprite(int width, int height, Color color)
        {
            Texture2D tex = new Texture2D(width, height);
            Color[] pixels = new Color[width * height];
            for (int i = 0; i < pixels.Length; i++)
                pixels[i] = color;
            tex.SetPixels(pixels);
            tex.Apply();
            return Sprite.Create(tex, new Rect(0, 0, width, height), new Vector2(0.5f, 0.5f));
        }
    }
} 