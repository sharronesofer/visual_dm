using UnityEngine;
using System.Collections.Generic;
using VisualDM.Core;

namespace VisualDM.UI
{
    /// <summary>
    /// Manages runtime UI panels and navigation for the game. All UI is generated at runtime.
    /// </summary>
    public class UIManager : MonoBehaviour
    {
        private static UIManager _instance;
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

        public enum Breakpoint { Mobile, Tablet, Desktop, LargeDesktop }
        public Breakpoint CurrentBreakpoint { get; private set; }
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