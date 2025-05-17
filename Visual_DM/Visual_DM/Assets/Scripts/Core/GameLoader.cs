using VisualDM.World;
using UnityEngine;
using System.Threading.Tasks;
using VisualDM.UI;
using VisualDM.Systems.EventSystem;

/// <summary>
/// Entry point for the game. Bootstraps all core systems and runtime managers.
/// </summary>
/// <remarks>
/// This script is attached to the only GameObject in the Bootstrap scene. It creates all required managers and UI at runtime, with no scene references or prefabs.
/// </remarks>
/// <example>
/// <code>
/// // GameLoader is attached to the root GameObject in Bootstrap.unity
/// // All systems are initialized automatically at runtime.
/// </code>
/// </example>
public class GameLoader : MonoBehaviour
{
    private WorldManager worldManager;
    private WebSocketClient _wsClient;

    void Awake()
    {
        // Initialize World Management System
        GameObject worldManagerObj = new GameObject("WorldManager");
        worldManager = worldManagerObj.AddComponent<WorldManager>();
        DontDestroyOnLoad(worldManagerObj);

        // Initialize UI Manager
        VisualDM.UI.UIManager.Instance.ToString(); // Ensures UIManager singleton is created

        // Initialize State Manager
        VisualDM.Core.StateManager.Instance.ToString(); // Ensures StateManager singleton is created
    }

    /// <summary>
    /// Initializes core systems including MonitoringDashboard at runtime.
    /// </summary>
    /// <remarks>
    /// Called automatically by Unity. Instantiates WebSocketClient, FeatEventTracker, and CharacterBuildOptimizerPanel. Connects to backend and subscribes to events.
    /// </remarks>
    /// <example>
    /// <code>
    /// // Called by Unity at runtime
    /// // All managers and UI are created automatically
    /// </code>
    /// </example>
    void Start()
    {
        // Create WebSocketClient at runtime
        GameObject wsObj = new GameObject("WebSocketClient");
        _wsClient = wsObj.AddComponent<WebSocketClient>();
        DontDestroyOnLoad(wsObj);

        // Instantiate FeatEventTracker at runtime
        GameObject featEventTrackerObj = new GameObject("FeatEventTracker");
        featEventTrackerObj.AddComponent<Visual_DM.FeatHistory.FeatEventTracker>();
        DontDestroyOnLoad(featEventTrackerObj);

        // --- Authentication Integration Point ---
        // Replace the following with real JWT and client_id from login/auth system.
        // These should be injected after successful login.
        string server = "localhost:8000"; // or your backend host:port
        string token = "testtoken"; // <-- Inject real JWT here
        string clientId = "testclient"; // <-- Inject real client_id here
        int width = 1280;
        int height = 720;

        // Connect to backend
        _wsClient.ConnectAsync(server, token, clientId, width, height);

        // Subscribe to notifications via EventBus
        EventBus.Instance.Subscribe<UINotificationEvent>(evt =>
        {
            Debug.Log($"[WS Notification][{evt.Level}] {evt.Message}");
        });
        // _wsClient.OnNotification += (msg, level) => Debug.Log($"[WS Notification][{level}] {msg}"); // Removed
        _wsClient.OnError += (msg, code) => Debug.LogError($"[WS Error][{code}] {msg}");

        InitializeMonitoringDashboard();

        // Instantiate CharacterBuildOptimizerPanel for demo
        var optimizerPanelGO = new GameObject("CharacterBuildOptimizerPanel");
        var optimizerPanel = optimizerPanelGO.AddComponent<CharacterBuildOptimizerPanel>();
        optimizerPanel.Initialize();
        optimizerPanelGO.transform.position = new Vector3(0, 0, 0); // Center of screen

        // --- Player Sprite Assignment Placeholder ---
        // Assign a player sprite here if/when available from the asset pipeline or user selection.
        // Example:
        // Sprite playerSprite = Resources.Load<Sprite>("Sprites/Player");
        // playerObject.GetComponent<SpriteRenderer>().sprite = playerSprite;
        // (Currently not implemented)

        // Ensure ErrorHandlingService is instantiated
        var _ = VisualDM.Utilities.ErrorHandlingService.Instance;
    }

    /// <summary>
    /// Instantiates the MonitoringDashboard UI at runtime if not already present.
    /// </summary>
    /// <remarks>
    /// Ensures only one MonitoringDashboard exists. Called during startup.
    /// </remarks>
    /// <example>
    /// <code>
    /// // Called internally by GameLoader
    /// </code>
    /// </example>
    private void InitializeMonitoringDashboard()
    {
        if (FindObjectOfType<VisualDM.UI.MonitoringDashboard>() == null)
        {
            var go = new GameObject("MonitoringDashboard");
            go.AddComponent<VisualDM.UI.MonitoringDashboard>();
            DontDestroyOnLoad(go);
        }
    }
} 