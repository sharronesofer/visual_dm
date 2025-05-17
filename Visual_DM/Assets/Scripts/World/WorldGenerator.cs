using UnityEngine;

namespace VisualDM.World
{
    public static class WorldGenerator
    {
        public static GameObject GenerateWorld(float seed)
        {
            int width = 100;
            int height = 100;
            float scale = 0.1f; // Controls Perlin noise granularity

            // Try to load terrain sprites, fallback to generated colored sprites if missing
            Sprite grassSprite = Resources.Load<Sprite>("Sprites/grass");
            Sprite waterSprite = Resources.Load<Sprite>("Sprites/water");
            Sprite mountainSprite = Resources.Load<Sprite>("Sprites/mountain");

            if (grassSprite == null)
                grassSprite = GenerateColoredSprite(Color.green);
            if (waterSprite == null)
                waterSprite = GenerateColoredSprite(Color.blue);
            if (mountainSprite == null)
                mountainSprite = GenerateColoredSprite(Color.gray);

            // Create parent object
            GameObject worldParent = new GameObject("World");

            for (int x = 0; x < width; x++)
            {
                for (int y = 0; y < height; y++)
                {
                    float xCoord = seed + x * scale;
                    float yCoord = seed + y * scale;
                    float noise = Mathf.PerlinNoise(xCoord, yCoord);

                    Sprite tileSprite;
                    // Assign terrain type by noise value
                    if (noise < 0.4f)
                    {
                        tileSprite = waterSprite;
                    }
                    else if (noise < 0.7f)
                    {
                        tileSprite = grassSprite;
                    }
                    else
                    {
                        tileSprite = mountainSprite;
                    }

                    // Create tile GameObject
                    GameObject tile = new GameObject($"Tile_{x}_{y}");
                    tile.transform.position = new Vector3(x, y, 0);
                    tile.transform.parent = worldParent.transform;

                    // Add SpriteRenderer
                    var sr = tile.AddComponent<SpriteRenderer>();
                    sr.sprite = tileSprite;
                    sr.color = Color.white;
                }
            }
            return worldParent;
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
} 