using VisualDM.World;
using UnityEngine;
using System.Threading.Tasks;
using VisualDM.UI;

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
    void Start()
    {
        // Create WebSocketClient at runtime
        GameObject wsObj = new GameObject("WebSocketClient");
        _wsClient = wsObj.AddComponent<WebSocketClient>();
        DontDestroyOnLoad(wsObj);

        // TODO: Replace with real JWT and client_id from login/auth
        string server = "localhost:8000"; // or your backend host:port
        string token = "testtoken";
        string clientId = "testclient";
        int width = 1280;
        int height = 720;

        // Connect to backend
        _wsClient.ConnectAsync(server, token, clientId, width, height);

        // Subscribe to events
        _wsClient.OnNotification += (msg, level) => Debug.Log($"[WS Notification][{level}] {msg}");
        _wsClient.OnError += (msg, code) => Debug.LogError($"[WS Error][{code}] {msg}");

        InitializeMonitoringDashboard();

        // Instantiate CharacterBuildOptimizerPanel for demo
        var optimizerPanelGO = new GameObject("CharacterBuildOptimizerPanel");
        var optimizerPanel = optimizerPanelGO.AddComponent<CharacterBuildOptimizerPanel>();
        optimizerPanel.Initialize();
        optimizerPanelGO.transform.position = new Vector3(0, 0, 0); // Center of screen
    }

    /// <summary>
    /// Instantiates the MonitoringDashboard UI at runtime if not already present.
    /// </summary>
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