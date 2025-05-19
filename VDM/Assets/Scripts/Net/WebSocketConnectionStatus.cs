using System;

namespace VisualDM.Net
{
    /// <summary>
    /// Represents the connection status of a WebSocket.
    /// </summary>
    public enum WebSocketConnectionStatus
    {
        /// <summary>
        /// WebSocket is disconnected.
        /// </summary>
        Disconnected,
        
        /// <summary>
        /// WebSocket is currently connecting.
        /// </summary>
        Connecting,
        
        /// <summary>
        /// WebSocket is fully connected.
        /// </summary>
        Connected,
        
        /// <summary>
        /// WebSocket is attempting to reconnect after being disconnected.
        /// </summary>
        Reconnecting,
        
        /// <summary>
        /// WebSocket has encountered an error.
        /// </summary>
        Error
    }
} 