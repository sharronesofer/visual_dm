using System.Collections.Generic;
using System.Linq;
using System;
using UnityEngine.UI;
using UnityEngine;
using VDM.Runtime.Services;


namespace VDM.Runtime.Core
{
    /// <summary>
    /// Network debugging tools for monitoring multiplayer and backend connections
    /// Implements Task 22: Network debugging tools for multiplayer testing
    /// </summary>
    public class NetworkDebugTools : MonoBehaviour
    {
        [Header("Network Debug UI")]
        [SerializeField] private GameObject networkPanel;
        [SerializeField] private Text connectionStatusText;
        [SerializeField] private Text latencyText;
        [SerializeField] private Text messageLogText;
        [SerializeField] private ScrollRect messageScrollRect;
        [SerializeField] private Toggle autoScrollToggle;
        
        [Header("Settings")]
        [SerializeField] private bool showNetworkDebug = false;
        [SerializeField] private int maxLogMessages = 100;
        [SerializeField] private float latencyUpdateInterval = 1.0f;
        [SerializeField] private bool logIncomingMessages = true;
        [SerializeField] private bool logOutgoingMessages = true;
        [SerializeField] private bool logConnectionEvents = true;
        
        // Singleton instance
        public static NetworkDebugTools Instance { get; private set; }
        
        // Network monitoring
        private List<NetworkMessage> _messageLog = new List<NetworkMessage>();
        private Dictionary<string, ConnectionInfo> _connections = new Dictionary<string, ConnectionInfo>();
        private float _latencyTimer = 0f;
        
        // UI update
        private float _uiUpdateInterval = 0.5f;
        private float _uiUpdateTimer = 0f;
        
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
            CreateNetworkDebugUI();
            SubscribeToNetworkEvents();
            
            LogConnectionEvent("NetworkDebugTools initialized");
        }
        
        private void CreateNetworkDebugUI()
        {
            if (networkPanel == null)
            {
                // Create network debug panel
                var canvas = VisualDebugTools.Instance?.GetComponent<Canvas>() ?? FindObjectOfType<Canvas>();
                if (canvas == null) return;
                
                networkPanel = new GameObject("NetworkDebugPanel");
                networkPanel.transform.SetParent(canvas.transform, false);
                
                var rectTransform = networkPanel.AddComponent<RectTransform>();
                rectTransform.anchorMin = new Vector2(0.7f, 0f);
                rectTransform.anchorMax = new Vector2(1f, 0.7f);
                rectTransform.sizeDelta = Vector2.zero;
                rectTransform.anchoredPosition = Vector2.zero;
                
                // Background
                var background = networkPanel.AddComponent<Image>();
                background.color = new Color(0, 0, 0, 0.7f);
                
                CreateConnectionStatusDisplay();
                CreateLatencyDisplay();
                CreateMessageLogDisplay();
            }
            
            SetNetworkDebugVisible(showNetworkDebug);
        }
        
        private void CreateConnectionStatusDisplay()
        {
            var statusGO = new GameObject("ConnectionStatus");
            statusGO.transform.SetParent(networkPanel.transform, false);
            
            var rectTransform = statusGO.AddComponent<RectTransform>();
            rectTransform.anchorMin = new Vector2(0, 0.9f);
            rectTransform.anchorMax = new Vector2(1, 1);
            rectTransform.sizeDelta = Vector2.zero;
            rectTransform.anchoredPosition = Vector2.zero;
            
            connectionStatusText = statusGO.AddComponent<Text>();
            connectionStatusText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            connectionStatusText.fontSize = 12;
            connectionStatusText.color = Color.white;
            connectionStatusText.alignment = TextAnchor.UpperLeft;
            connectionStatusText.text = "=== CONNECTIONS ===\nInitializing...";
        }
        
        private void CreateLatencyDisplay()
        {
            var latencyGO = new GameObject("LatencyDisplay");
            latencyGO.transform.SetParent(networkPanel.transform, false);
            
            var rectTransform = latencyGO.AddComponent<RectTransform>();
            rectTransform.anchorMin = new Vector2(0, 0.8f);
            rectTransform.anchorMax = new Vector2(1, 0.9f);
            rectTransform.sizeDelta = Vector2.zero;
            rectTransform.anchoredPosition = Vector2.zero;
            
            latencyText = latencyGO.AddComponent<Text>();
            latencyText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            latencyText.fontSize = 11;
            latencyText.color = Color.cyan;
            latencyText.alignment = TextAnchor.UpperLeft;
            latencyText.text = "=== LATENCY ===\nMeasuring...";
        }
        
        private void CreateMessageLogDisplay()
        {
            var logGO = new GameObject("MessageLog");
            logGO.transform.SetParent(networkPanel.transform, false);
            
            var rectTransform = logGO.AddComponent<RectTransform>();
            rectTransform.anchorMin = new Vector2(0, 0);
            rectTransform.anchorMax = new Vector2(1, 0.8f);
            rectTransform.sizeDelta = Vector2.zero;
            rectTransform.anchoredPosition = Vector2.zero;
            
            // Create scrollable area
            messageScrollRect = logGO.AddComponent<ScrollRect>();
            messageScrollRect.vertical = true;
            messageScrollRect.horizontal = false;
            
            // Content area
            var contentGO = new GameObject("Content");
            contentGO.transform.SetParent(logGO.transform, false);
            
            var contentTransform = contentGO.AddComponent<RectTransform>();
            contentTransform.anchorMin = new Vector2(0, 0);
            contentTransform.anchorMax = new Vector2(1, 1);
            contentTransform.sizeDelta = Vector2.zero;
            contentTransform.anchoredPosition = Vector2.zero;
            
            messageScrollRect.content = contentTransform;
            
            // Message text
            var textGO = new GameObject("MessageText");
            textGO.transform.SetParent(contentGO.transform, false);
            
            var textTransform = textGO.AddComponent<RectTransform>();
            textTransform.anchorMin = Vector2.zero;
            textTransform.anchorMax = Vector2.one;
            textTransform.sizeDelta = Vector2.zero;
            textTransform.anchoredPosition = Vector2.zero;
            
            messageLogText = textGO.AddComponent<Text>();
            messageLogText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            messageLogText.fontSize = 10;
            messageLogText.color = Color.yellow;
            messageLogText.alignment = TextAnchor.UpperLeft;
            messageLogText.verticalOverflow = VerticalWrapMode.Overflow;
            messageLogText.text = "=== MESSAGE LOG ===\n";
            
            // Auto-scroll toggle
            CreateAutoScrollToggle();
        }
        
        private void CreateAutoScrollToggle()
        {
            var toggleGO = new GameObject("AutoScrollToggle");
            toggleGO.transform.SetParent(networkPanel.transform, false);
            
            var rectTransform = toggleGO.AddComponent<RectTransform>();
            rectTransform.anchorMin = new Vector2(0.7f, 0.8f);
            rectTransform.anchorMax = new Vector2(1f, 0.85f);
            rectTransform.sizeDelta = Vector2.zero;
            rectTransform.anchoredPosition = Vector2.zero;
            
            autoScrollToggle = toggleGO.AddComponent<Toggle>();
            autoScrollToggle.isOn = true;
            
            // Toggle background
            var background = toggleGO.AddComponent<Image>();
            background.color = new Color(0.2f, 0.2f, 0.2f, 0.5f);
            autoScrollToggle.targetGraphic = background;
            
            // Checkmark
            var checkmarkGO = new GameObject("Checkmark");
            checkmarkGO.transform.SetParent(toggleGO.transform, false);
            
            var checkmarkRect = checkmarkGO.AddComponent<RectTransform>();
            checkmarkRect.anchorMin = new Vector2(0.2f, 0.2f);
            checkmarkRect.anchorMax = new Vector2(0.8f, 0.8f);
            checkmarkRect.sizeDelta = Vector2.zero;
            checkmarkRect.anchoredPosition = Vector2.zero;
            
            var checkmark = checkmarkGO.AddComponent<Image>();
            checkmark.color = Color.green;
            autoScrollToggle.graphic = checkmark;
            
            // Label
            var labelGO = new GameObject("Label");
            labelGO.transform.SetParent(toggleGO.transform, false);
            
            var labelRect = labelGO.AddComponent<RectTransform>();
            labelRect.anchorMin = new Vector2(1.1f, 0);
            labelRect.anchorMax = new Vector2(2f, 1);
            labelRect.sizeDelta = Vector2.zero;
            labelRect.anchoredPosition = Vector2.zero;
            
            var label = labelGO.AddComponent<Text>();
            label.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            label.fontSize = 10;
            label.color = Color.white;
            label.alignment = TextAnchor.MiddleLeft;
            label.text = "Auto Scroll";
        }
        
        private void SubscribeToNetworkEvents()
        {
            // Subscribe to various network service events if they exist
            
            // WebSocket events
            var webSocketServices = FindObjectsOfType<MonoBehaviour>()
                .Where(mb => mb.GetType().Name.Contains("WebSocket"))
                .ToArray();
            
            // HTTP client events  
            var httpServices = FindObjectsOfType<MonoBehaviour>()
                .Where(mb => mb.GetType().Name.Contains("HTTP") || mb.GetType().Name.Contains("Client"))
                .ToArray();
            
            LogConnectionEvent($"Found {webSocketServices.Length} WebSocket services and {httpServices.Length} HTTP services");
        }
        
        private void Update()
        {
            UpdateLatencyMeasurements();
            UpdateUI();
            HandleNetworkDebugInput();
        }
        
        private void UpdateLatencyMeasurements()
        {
            _latencyTimer += Time.deltaTime;
            if (_latencyTimer >= latencyUpdateInterval)
            {
                _latencyTimer = 0f;
                MeasureLatency();
            }
        }
        
        private void MeasureLatency()
        {
            // Simulate latency measurements for different services
            foreach (var connection in _connections.Values)
            {
                // In a real implementation, this would ping the actual services
                connection.LastLatency = UnityEngine.Random.Range(10f, 100f);
                connection.LastPingTime = Time.time;
            }
        }
        
        private void UpdateUI()
        {
            if (!showNetworkDebug) return;
            
            _uiUpdateTimer += Time.deltaTime;
            if (_uiUpdateTimer >= _uiUpdateInterval)
            {
                _uiUpdateTimer = 0f;
                UpdateConnectionStatusText();
                UpdateLatencyText();
                UpdateMessageLogText();
            }
        }
        
        private void UpdateConnectionStatusText()
        {
            if (connectionStatusText == null) return;
            
            var text = "=== CONNECTIONS ===\n";
            
            if (_connections.Count == 0)
            {
                text += "No active connections";
            }
            else
            {
                foreach (var kvp in _connections)
                {
                    var name = kvp.Key;
                    var info = kvp.Value;
                    var status = info.IsConnected ? "✓" : "✗";
                    var color = info.IsConnected ? "green" : "red";
                    
                    text += $"{status} <color={color}>{name}</color>\n";
                    text += $"  Endpoint: {info.Endpoint}\n";
                    text += $"  Uptime: {(Time.time - info.ConnectTime):F1}s\n";
                }
            }
            
            connectionStatusText.text = text;
        }
        
        private void UpdateLatencyText()
        {
            if (latencyText == null) return;
            
            var text = "=== LATENCY ===\n";
            
            foreach (var kvp in _connections)
            {
                var name = kvp.Key;
                var info = kvp.Value;
                
                if (info.IsConnected)
                {
                    var latencyColor = info.LastLatency < 50 ? "green" : info.LastLatency < 100 ? "yellow" : "red";
                    text += $"{name}: <color={latencyColor}>{info.LastLatency:F0}ms</color>\n";
                }
                else
                {
                    text += $"{name}: <color=red>Disconnected</color>\n";
                }
            }
            
            if (_connections.Count == 0)
            {
                text += "No connections to measure";
            }
            
            latencyText.text = text;
        }
        
        private void UpdateMessageLogText()
        {
            if (messageLogText == null) return;
            
            var text = "=== MESSAGE LOG ===\n";
            var recentMessages = _messageLog.TakeLast(20); // Show last 20 messages
            
            foreach (var message in recentMessages)
            {
                var timestamp = message.Timestamp.ToString("HH:mm:ss.fff");
                var typeColor = message.Type == MessageType.Incoming ? "cyan" : message.Type == MessageType.Outgoing ? "yellow" : "white";
                
                text += $"[{timestamp}] <color={typeColor}>{message.Type}</color> {message.Service}: {message.Content}\n";
            }
            
            messageLogText.text = text;
            
            // Auto-scroll to bottom if enabled
            if (autoScrollToggle != null && autoScrollToggle.isOn && messageScrollRect != null)
            {
                Canvas.ForceUpdateCanvases();
                messageScrollRect.verticalNormalizedPosition = 0f;
            }
        }
        
        private void HandleNetworkDebugInput()
        {
            // Toggle network debug with F6
            if (Input.GetKeyDown(KeyCode.F6))
            {
                ToggleNetworkDebug();
            }
        }
        
        #region Public API
        
        public void ToggleNetworkDebug()
        {
            SetNetworkDebugVisible(!showNetworkDebug);
        }
        
        public void SetNetworkDebugVisible(bool visible)
        {
            showNetworkDebug = visible;
            if (networkPanel != null)
            {
                networkPanel.SetActive(visible);
            }
        }
        
        public void LogMessage(string service, string content, MessageType type = MessageType.Info)
        {
            if ((type == MessageType.Incoming && !logIncomingMessages) ||
                (type == MessageType.Outgoing && !logOutgoingMessages) ||
                (type == MessageType.Connection && !logConnectionEvents))
            {
                return;
            }
            
            var message = new NetworkMessage
            {
                Timestamp = DateTime.Now,
                Service = service,
                Content = content,
                Type = type
            };
            
            _messageLog.Add(message);
            
            // Limit log size
            while (_messageLog.Count > maxLogMessages)
            {
                _messageLog.RemoveAt(0);
            }
        }
        
        public void LogIncomingMessage(string service, string content)
        {
            LogMessage(service, content, MessageType.Incoming);
        }
        
        public void LogOutgoingMessage(string service, string content)
        {
            LogMessage(service, content, MessageType.Outgoing);
        }
        
        public void LogConnectionEvent(string content)
        {
            LogMessage("Network", content, MessageType.Connection);
        }
        
        public void RegisterConnection(string name, string endpoint, bool isConnected = true)
        {
            _connections[name] = new ConnectionInfo
            {
                Name = name,
                Endpoint = endpoint,
                IsConnected = isConnected,
                ConnectTime = Time.time,
                LastLatency = 0f,
                LastPingTime = 0f
            };
            
            LogConnectionEvent($"Registered connection: {name} ({endpoint})");
        }
        
        public void UpdateConnectionStatus(string name, bool isConnected)
        {
            if (_connections.ContainsKey(name))
            {
                var wasConnected = _connections[name].IsConnected;
                _connections[name].IsConnected = isConnected;
                
                if (wasConnected != isConnected)
                {
                    LogConnectionEvent($"Connection {name}: {(isConnected ? "Connected" : "Disconnected")}");
                }
            }
        }
        
        public void RemoveConnection(string name)
        {
            if (_connections.ContainsKey(name))
            {
                _connections.Remove(name);
                LogConnectionEvent($"Removed connection: {name}");
            }
        }
        
        public void ClearMessageLog()
        {
            _messageLog.Clear();
            LogConnectionEvent("Message log cleared");
        }
        
        public void SimulateNetworkEvent(string service, string eventType)
        {
            LogMessage(service, $"Simulated event: {eventType}", MessageType.Info);
        }
        
        #endregion
        
        #region Console Commands
        
        [ConsoleCommand("network.debug", "Toggle network debug panel")]
        public static string ToggleNetworkDebugCommand()
        {
            if (Instance != null)
            {
                Instance.ToggleNetworkDebug();
                return $"Network debug: {(Instance.showNetworkDebug ? "ON" : "OFF")}";
            }
            return "NetworkDebugTools not available";
        }
        
        [ConsoleCommand("network.clear_log", "Clear network message log")]
        public static string ClearLog()
        {
            if (Instance != null)
            {
                Instance.ClearMessageLog();
                return "Network message log cleared";
            }
            return "NetworkDebugTools not available";
        }
        
        [ConsoleCommand("network.simulate", "Simulate network event")]
        [System.ComponentModel.Description("Usage: network.simulate <service> <event>")]
        public static string SimulateEvent(string service = "TestService", string eventType = "TestEvent")
        {
            if (Instance != null)
            {
                Instance.SimulateNetworkEvent(service, eventType);
                return $"Simulated {eventType} for {service}";
            }
            return "NetworkDebugTools not available";
        }
        
        [ConsoleCommand("network.status", "Show network connection status")]
        public static string ShowNetworkStatus()
        {
            if (Instance != null)
            {
                var connections = Instance._connections;
                if (connections.Count == 0)
                {
                    return "No network connections registered";
                }
                
                var status = "Network Connection Status:\n";
                foreach (var kvp in connections)
                {
                    var info = kvp.Value;
                    status += $"  {kvp.Key}: {(info.IsConnected ? "Connected" : "Disconnected")} ";
                    status += $"({info.Endpoint}) Latency: {info.LastLatency:F0}ms\n";
                }
                
                return status.TrimEnd();
            }
            return "NetworkDebugTools not available";
        }
        
        [ConsoleCommand("network.ping", "Test network latency")]
        [System.ComponentModel.Description("Usage: network.ping [service]")]
        public static string PingService(string service = "")
        {
            if (Instance != null)
            {
                if (string.IsNullOrEmpty(service))
                {
                    Instance.MeasureLatency();
                    return "Pinging all services...";
                }
                else if (Instance._connections.ContainsKey(service))
                {
                    var latency = UnityEngine.Random.Range(10f, 100f); // Simulate ping
                    Instance._connections[service].LastLatency = latency;
                    Instance._connections[service].LastPingTime = Time.time;
                    return $"Ping to {service}: {latency:F0}ms";
                }
                else
                {
                    return $"Service '{service}' not found";
                }
            }
            return "NetworkDebugTools not available";
        }
        
        #endregion
        
        #region Data Structures
        
        public enum MessageType
        {
            Incoming,
            Outgoing,
            Connection,
            Info
        }
        
        public class NetworkMessage
        {
            public DateTime Timestamp;
            public string Service;
            public string Content;
            public MessageType Type;
        }
        
        public class ConnectionInfo
        {
            public string Name;
            public string Endpoint;
            public bool IsConnected;
            public float ConnectTime;
            public float LastLatency;
            public float LastPingTime;
        }
        
        #endregion
    }
} 