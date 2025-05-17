using UnityEngine;

public static class WorldGenerator
{
    public static void GenerateWorld(float seed)
    {
        int width = 100;
        int height = 100;
        float scale = 10f;
        GameObject worldParent = new GameObject("World");

        for (int x = 0; x < width; x++)
        {
            for (int y = 0; y < height; y++)
            {
                float perlin = Mathf.PerlinNoise((x + seed) / scale, (y + seed) / scale);
                Color tileColor;
                if (perlin < 0.4f)
                {
                    tileColor = Color.blue; // Water
                }
                else if (perlin < 0.7f)
                {
                    tileColor = Color.green; // Grass
                }
                else
                {
                    tileColor = Color.gray; // Mountain
                }

                GameObject tile = new GameObject($"Tile_{x}_{y}");
                tile.transform.position = new Vector3(x, y, 0);
                tile.transform.parent = worldParent.transform;
                var sr = tile.AddComponent<SpriteRenderer>();
                sr.color = tileColor;
                // Optionally, assign a default square sprite if available
                // sr.sprite = ...
            }
        }
    }
} 