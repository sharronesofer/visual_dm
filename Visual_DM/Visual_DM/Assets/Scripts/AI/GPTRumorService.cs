using System;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace Visual_DM.AI
{
    /// <summary>
    /// Implementation of IGPTRumorService using a WebSocket connection to a Python backend.
    /// </summary>
    public class GPTRumorService : IGPTRumorService
    {
        private readonly Uri _backendUri;
        private readonly int _timeoutMs;

        public GPTRumorService(string backendUrl = "ws://localhost:8765", int timeoutMs = 10000)
        {
            _backendUri = new Uri(backendUrl);
            _timeoutMs = timeoutMs;
        }

        public async Task<string> TransformRumorAsync(string eventData, RumorParameters parameters)
        {
            var request = new RumorRequest
            {
                EventData = eventData,
                Parameters = parameters
            };
            string requestJson = JsonConvert.SerializeObject(request);

            using (var ws = new ClientWebSocket())
            {
                try
                {
                    var cts = new CancellationTokenSource(_timeoutMs);
                    await ws.ConnectAsync(_backendUri, cts.Token);

                    var sendBuffer = new ArraySegment<byte>(Encoding.UTF8.GetBytes(requestJson));
                    await ws.SendAsync(sendBuffer, WebSocketMessageType.Text, true, cts.Token);

                    var receiveBuffer = new ArraySegment<byte>(new byte[4096]);
                    var result = await ws.ReceiveAsync(receiveBuffer, cts.Token);
                    string responseJson = Encoding.UTF8.GetString(receiveBuffer.Array, 0, result.Count);

                    var response = JsonConvert.DeserializeObject<RumorResponse>(responseJson);
                    return response?.Rumor ?? "[Rumor generation failed]";
                }
                catch (Exception ex)
                {
                    // Log error (could use a logger here)
                    return $"[Rumor generation error: {ex.Message}]";
                }
            }
        }

        private class RumorRequest
        {
            public string EventData { get; set; }
            public RumorParameters Parameters { get; set; }
        }

        private class RumorResponse
        {
            public string Rumor { get; set; }
        }
    }
}