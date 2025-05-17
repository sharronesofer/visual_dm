// RULES FOR CURSOR:
// - All code must use Unity 2D runtime
// - Use SpriteRenderer not MeshRenderer
// - Use runtime-only constructs (no UnityEditor)
// - Do not use prebuilt scenes, tags, or GameObject.Find
// - Bootstrap scene contains only GameLoader
// - Scripts go in: Core/, World/, Entities/, Systems/, UI/
// - All objects must be created by script at runtime

using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.World;
using VisualDM.Entities;
using VisualDM.UI;
using VisualDM.Core;

namespace VisualDM.Core
{
    public class GameLoader : MonoBehaviour
    {
        // Seed for world generation
        public int seed = 12345; // You can set this in the Inspector or change as needed

        // Start is called before the first frame update
        void Start()
        {
            // Create Camera at runtime
            var camGO = new GameObject("Main Camera");
            var cam = camGO.AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 60;
            camGO.transform.position = new Vector3(50, 50, -10);
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = Color.black;
            camGO.tag = "MainCamera";

            // Create Player at runtime
            var playerGO = new GameObject("Player");
            playerGO.transform.position = new Vector3(50, 50, 0);
            var sr = playerGO.AddComponent<SpriteRenderer>();
            sr.sprite = null; // TODO: assign a player sprite if available
            var rb = playerGO.AddComponent<Rigidbody2D>();
            rb.gravityScale = 0;
            var collider = playerGO.AddComponent<CircleCollider2D>();
            collider.isTrigger = true;
            playerGO.tag = "Player";

            // Generate the world and get the parent object
            GameObject worldParent = WorldGenerator.GenerateWorld(seed);
            // Spawn all NPCs, passing the world parent
            NPCSpawner.SpawnAll(worldParent);
            // Initialize the HUD
            UIManager.InitializeHUD();
            UIManager.CreateDialogueUI();
            // Destroy this loader object after initialization
            Destroy(gameObject);
        }

        // Update is called once per frame
        void Update()
        {
            
        }
    }
}
