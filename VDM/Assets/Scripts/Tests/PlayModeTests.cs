namespace VisualDM.Tests
{
    using NUnit.Framework;
    using UnityEngine;
    using UnityEngine.TestTools;
    using System.Collections;

    public class PlayModeTests
    {
        [UnityTest]
        public IEnumerator GameLoader_InitializesCoreSystems()
        {
            // Create GameLoader at runtime
            var go = new GameObject("GameLoader");
            var loader = go.AddComponent<GameLoader>();
            yield return null; // Wait a frame for Awake

            // Check WorldManager exists
            var worldManagerObj = GameObject.Find("WorldManager");
            Assert.IsNotNull(worldManagerObj);
            Assert.IsNotNull(worldManagerObj.GetComponent<VisualDM.World.WorldManager>());

            // Check UIManager singleton
            Assert.IsNotNull(VisualDM.UI.UIManager.Instance);
            // Check StateManager singleton
            Assert.IsNotNull(VisualDM.Core.StateManager.Instance);

            Object.DestroyImmediate(go);
            Object.DestroyImmediate(worldManagerObj);
        }

        [UnityTest]
        public IEnumerator GameLoader_CreatesWebSocketClient()
        {
            var go = new GameObject("GameLoader");
            var loader = go.AddComponent<GameLoader>();
            yield return new WaitForSeconds(0.2f); // Wait for Start async
            var wsObj = GameObject.Find("WebSocketClient");
            Assert.IsNotNull(wsObj);
            Assert.IsNotNull(wsObj.GetComponent<WebSocketClient>());
            Object.DestroyImmediate(go);
            Object.DestroyImmediate(wsObj);
        }
    }
} 