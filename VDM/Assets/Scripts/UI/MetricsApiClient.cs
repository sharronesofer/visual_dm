using System;
using System.Threading.Tasks;
using UnityEngine;
using Newtonsoft.Json.Linq;
using VisualDM.Core;
using System.Collections.Generic;
using Newtonsoft.Json;
using VisualDM.Net;

namespace VisualDM.UI
{
    public class MetricsApiClient : MonoBehaviour
    {
        private string requestId;
        private Action<JObject> _onSuccess;
        private Action<string> _onError;
        private const string WebSocketKey = "metrics";

        /// <summary>
        /// Requests historical metrics from the backend via WebSocket.
        /// </summary>
        public void GetHistoricalMetrics(string startTime, string endTime, int page, int pageSize, Action<JObject> onSuccess, Action<string> onError)
        {
            requestId = Guid.NewGuid().ToString();
            _onSuccess = onSuccess;
            _onError = onError;
            var payload = new JObject
            {
                ["start_time"] = startTime,
                ["end_time"] = endTime,
                ["page"] = page,
                ["page_size"] = pageSize
            };
            var msg = new WebSocketMessage
            {
                type = "get_historical_metrics",
                payload = payload.ToObject<Dictionary<string, object>>(),
                requestId = requestId,
                timestamp = DateTime.UtcNow.ToString("o"),
                version = "1.0"
            };
            var wsManager = WebSocketManager.Instance;
            if (wsManager == null)
            {
                onError?.Invoke("WebSocketManager not found");
                return;
            }
            wsManager.Connect(WebSocketKey, "ws://localhost:8000/api/v1/ws/metrics/stream");
            wsManager.Clients[WebSocketKey].RegisterMessageHandler("historical_metrics_result", OnMetricsResult);
            wsManager.Clients[WebSocketKey].RegisterMessageHandler("error", OnError);
            wsManager.Send(WebSocketKey, msg);
        }

        private void OnMetricsResult(string json)
        {
            var obj = JObject.Parse(json);
            if ((string)obj["requestId"] != requestId) return;
            wsCleanup();
            _onSuccess?.Invoke((JObject)obj["payload"]);
        }

        private void OnError(string json)
        {
            var obj = JObject.Parse(json);
            if ((string)obj["requestId"] != requestId) return;
            wsCleanup();
            _onError?.Invoke((string)obj["message"]);
        }

        private void wsCleanup()
        {
            var wsManager = WebSocketManager.Instance;
            if (wsManager != null && wsManager.Clients.ContainsKey(WebSocketKey))
            {
                wsManager.Clients[WebSocketKey].RegisterMessageHandler("historical_metrics_result", null);
                wsManager.Clients[WebSocketKey].RegisterMessageHandler("error", null);
            }
        }
    }
}