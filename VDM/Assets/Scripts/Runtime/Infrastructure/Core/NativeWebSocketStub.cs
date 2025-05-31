using System;
using System.Threading.Tasks;

// Temporary stub for NativeWebSocket to allow compilation
// This should be removed once the actual NativeWebSocket package is properly installed
namespace NativeWebSocket
{
    public enum WebSocketState
    {
        Connecting,
        Open,
        Closing,
        Closed
    }

    public enum WebSocketCloseCode
    {
        Normal = 1000,
        Away = 1001,
        ProtocolError = 1002,
        UnsupportedData = 1003,
        Undefined = 1005,
        Abnormal = 1006,
        InvalidData = 1007,
        PolicyViolation = 1008,
        TooBig = 1009,
        MandatoryExtension = 1010,
        ServerError = 1011,
        ServiceRestart = 1012,
        TryAgainLater = 1013,
        BadGateway = 1014,
        TlsHandshakeFailure = 1015
    }

    public class WebSocket
    {
        public WebSocketState State { get; private set; } = WebSocketState.Closed;
        
        public event Action OnOpen;
        public event Action<string> OnError;
        public event Action<WebSocketCloseCode> OnClose;
        public event Action<byte[]> OnMessage;

        public WebSocket(string url)
        {
            // Stub implementation
        }

        public async Task Connect()
        {
            // Stub implementation
            State = WebSocketState.Open;
            OnOpen?.Invoke();
            await Task.CompletedTask;
        }

        public async Task Close()
        {
            // Stub implementation
            State = WebSocketState.Closed;
            OnClose?.Invoke(WebSocketCloseCode.Normal);
            await Task.CompletedTask;
        }

        public async Task SendText(string text)
        {
            // Stub implementation
            await Task.CompletedTask;
        }

        public void DispatchMessageQueue()
        {
            // Stub implementation
        }
    }
} 