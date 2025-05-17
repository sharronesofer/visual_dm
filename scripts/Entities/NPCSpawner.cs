using UnityEngine;
using System.Collections.Generic;

public static class NPCSpawner
{
    public static void SpawnAll(List<Vector2> grassTilePositions)
    {
        int npcCount = 10;
        GameObject npcParent = new GameObject("NPCs");
        Sprite npcSprite = Resources.Load<Sprite>("Sprites/npc");
        var usedIndices = new HashSet<int>();
        var rand = new System.Random();

        for (int i = 0; i < npcCount; i++)
        {
            // Pick a random grass tile position that hasn't been used
            int idx;
            do {
                idx = rand.Next(grassTilePositions.Count);
            } while (usedIndices.Contains(idx) && usedIndices.Count < grassTilePositions.Count);
            usedIndices.Add(idx);
            Vector2 pos = grassTilePositions[idx];

            GameObject npc = new GameObject($"NPC_{i}");
            npc.transform.position = new Vector3(pos.x, pos.y, 0);
            npc.transform.parent = npcParent.transform;
            var sr = npc.AddComponent<SpriteRenderer>();
            if (npcSprite != null)
                sr.sprite = npcSprite;
            npc.AddComponent<NPCController>();
        }
    }
} 