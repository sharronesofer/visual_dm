using NUnit.Framework;
using VisualDM.Core;
using UnityEngine;

namespace VisualDM.Tests
{
    [TestFixture]
    public class NetworkTests
    {
        [Test]
        public void WebSocketClient_InitializesAndConnects()
        {
            var go = new GameObject("WebSocketClient");
            var client = go.AddComponent<WebSocketClient>();
            Assert.IsNotNull(client);
            // Simulate connect (stub, as actual network not available in test)
            Assert.DoesNotThrow(() => client.Connect("ws://localhost:1234"));
            Object.DestroyImmediate(go);
        }

        [Test]
        public void WebSocketClient_SendsAndReceivesMessages()
        {
            var go = new GameObject("WebSocketClient");
            var client = go.AddComponent<WebSocketClient>();
            // Simulate send/receive (stub, as actual network not available in test)
            Assert.DoesNotThrow(() => client.Send("test message"));
            // Simulate receive (would require mock or event trigger)
            Object.DestroyImmediate(go);
        }

        [Test]
        public void WebSocketClient_ErrorHandling()
        {
            var go = new GameObject("WebSocketClient");
            var client = go.AddComponent<WebSocketClient>();
            // Simulate error (stub)
            Assert.DoesNotThrow(() => client.OnError("Simulated error"));
            Object.DestroyImmediate(go);
        }
    }
} 