using UnityEngine;
using System.Collections.Generic;

namespace VisualDM.Entities
{
    public static class NPCSpawner
    {
        public static void SpawnAll(GameObject worldParent)
        {
            int npcCount = 10;
            string npcSpritePath = "Sprites/npc";
            Sprite npcSprite = Resources.Load<Sprite>(npcSpritePath);
            if (npcSprite == null)
            {
                npcSprite = GenerateColoredSprite(new Color(1f, 0f, 1f, 1f)); // Magenta placeholder
            }

            // Find all grass tiles
            List<Vector3> grassPositions = new List<Vector3>();
            if (worldParent == null)
            {
                Debug.LogError("worldParent is null. Make sure WorldGenerator ran first and passed the parent.");
                return;
            }
            foreach (Transform tile in worldParent.transform)
            {
                var sr = tile.GetComponent<SpriteRenderer>();
                if (sr != null && sr.sprite != null && IsGrassSprite(sr))
                {
                    grassPositions.Add(tile.position);
                }
            }
            if (grassPositions.Count == 0)
            {
                Debug.LogError("No grass tiles found for NPC placement.");
                return;
            }

            // Create NPCs parent
            GameObject npcsParent = new GameObject("NPCs");

            // Shuffle grass positions for random placement
            for (int i = 0; i < grassPositions.Count; i++)
            {
                Vector3 temp = grassPositions[i];
                int randomIndex = Random.Range(i, grassPositions.Count);
                grassPositions[i] = grassPositions[randomIndex];
                grassPositions[randomIndex] = temp;
            }

            for (int i = 0; i < npcCount && i < grassPositions.Count; i++)
            {
                GameObject npc = new GameObject($"NPC_{i}");
                npc.transform.position = grassPositions[i];
                npc.transform.parent = npcsParent.transform;
                var sr = npc.AddComponent<SpriteRenderer>();
                sr.sprite = npcSprite;
                npc.AddComponent<NPCController>();
            }
        }

        // Determines if a SpriteRenderer is a grass tile (by color or sprite name)
        private static bool IsGrassSprite(SpriteRenderer sr)
        {
            // If using generated placeholder, check color
            if (sr.sprite.texture != null && sr.sprite.texture.width == 1 && sr.sprite.texture.height == 1)
            {
                Color c = sr.sprite.texture.GetPixel(0, 0);
                return c == Color.green;
            }
            // If using a real sprite, check name
            return sr.sprite.name.ToLower().Contains("grass");
        }

        // Generates a 1x1 solid color sprite
        private static Sprite GenerateColoredSprite(Color color)
        {
            Texture2D tex = new Texture2D(1, 1);
            tex.SetPixel(0, 0, color);
            tex.Apply();
            return Sprite.Create(tex, new Rect(0, 0, 1, 1), new Vector2(0.5f, 0.5f), 1);
        }
    }

    // MonoBehaviour for NPCs
    public class NPCController : MonoBehaviour
    {
        private bool playerInRange = false;
        private GameObject player;

        void Update()
        {
            if (playerInRange && Input.GetKeyDown(KeyCode.E))
            {
                TriggerDialogue();
            }
        }

        void OnTriggerEnter2D(Collider2D other)
        {
            if (other.CompareTag("Player"))
            {
                playerInRange = true;
                player = other.gameObject;
            }
        }

        void OnTriggerExit2D(Collider2D other)
        {
            if (other.CompareTag("Player"))
            {
                playerInRange = false;
                player = null;
            }
        }

        private void TriggerDialogue()
        {
            Debug.Log($"Dialogue requested with NPC: {gameObject.name}");
            DialogueStateManager.SetState(DialogueState.Pending, $"Talking to {gameObject.name}...", "");
            DialogueService.RequestDialogue(this, gameObject.name, (response) => {
                if (response.StartsWith("[Error"))
                    DialogueStateManager.SetState(DialogueState.Error, "", response);
                else
                    DialogueStateManager.SetState(DialogueState.Received, response, "");
            });
        }
    }
} 