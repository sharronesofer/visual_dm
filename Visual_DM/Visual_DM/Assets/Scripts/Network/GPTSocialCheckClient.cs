using System;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

namespace VisualDM.Network
{
    /// <summary>
    /// Client for communicating with the GPT Social Check Python WebSocket server.
    /// </summary>
    public class GPTSocialCheckClient
    {
        private const string ServerUri = "ws://localhost:8766";

        /// <summary>
        /// Sends a social check request and receives the classification result.
        /// </summary>
        /// <param name="dialogue">Player dialogue string</param>
        /// <param name="npcPersonality">NPC personality description</param>
        /// <param name="relationship">Relationship context</param>
        /// <param name="history">Recent interaction history</param>
        /// <returns>JSON result from the server</returns>
        public static async Task<string> AnalyzeAsync(string dialogue, string npcPersonality, string relationship, string history)
        {
            using (var ws = new ClientWebSocket())
            {
                var uri = new Uri(ServerUri);
                await ws.ConnectAsync(uri, CancellationToken.None);

                var requestObj = new
                {
                    Dialogue = dialogue,
                    NpcPersonality = npcPersonality,
                    Relationship = relationship,
                    History = history
                };
                string requestJson = JsonUtility.ToJson(requestObj);
                var requestBytes = Encoding.UTF8.GetBytes(requestJson);
                await ws.SendAsync(new ArraySegment<byte>(requestBytes), WebSocketMessageType.Text, true, CancellationToken.None);

                var buffer = new byte[2048];
                var result = await ws.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
                string responseJson = Encoding.UTF8.GetString(buffer, 0, result.Count);
                return responseJson;
            }
        }
    }
}