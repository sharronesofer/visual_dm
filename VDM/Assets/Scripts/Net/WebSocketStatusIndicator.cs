using UnityEngine;
using VisualDM.Net;

/// <summary>
/// Displays the connection status of a WebSocket connection as a colored indicator in the scene.
/// </summary>
public class WebSocketStatusIndicator : MonoBehaviour
{
    /// <summary>
    /// The key of the WebSocket connection to monitor.
    /// </summary>
    public string connectionKey;
    private SpriteRenderer spriteRenderer;

    /// <summary>
    /// Unity Awake lifecycle method. Initializes the indicator.
    /// </summary>
    private void Awake()
    {
        spriteRenderer = gameObject.AddComponent<SpriteRenderer>();
        UpdateIndicator(WebSocketConnectionStatus.Disconnected);
    }

    /// <summary>
    /// Unity OnEnable lifecycle method. Subscribes to status change events.
    /// </summary>
    private void OnEnable()
    {
        if (WebSocketManager.Instance != null)
            WebSocketManager.Instance.OnStatusChanged += HandleStatusChanged;
    }

    /// <summary>
    /// Unity OnDisable lifecycle method. Unsubscribes from status change events.
    /// </summary>
    private void OnDisable()
    {
        if (WebSocketManager.Instance != null)
            WebSocketManager.Instance.OnStatusChanged -= HandleStatusChanged;
    }

    /// <summary>
    /// Handles status change events for the monitored connection.
    /// </summary>
    /// <param name="key">The connection key.</param>
    /// <param name="status">The new connection status.</param>
    private void HandleStatusChanged(string key, WebSocketConnectionStatus status)
    {
        if (key == connectionKey)
            UpdateIndicator(status);
    }

    /// <summary>
    /// Updates the visual indicator color based on the connection status.
    /// </summary>
    /// <param name="status">The current connection status.</param>
    private void UpdateIndicator(WebSocketConnectionStatus status)
    {
        switch (status)
        {
            case WebSocketConnectionStatus.Connected:
                spriteRenderer.color = Color.green;
                break;
            case WebSocketConnectionStatus.Connecting:
                spriteRenderer.color = Color.yellow;
                break;
            case WebSocketConnectionStatus.Reconnecting:
                spriteRenderer.color = new Color(1f, 0.5f, 0f); // orange
                break;
            case WebSocketConnectionStatus.Error:
                spriteRenderer.color = Color.red;
                break;
            default:
                spriteRenderer.color = Color.gray;
                break;
        }
    }
} 