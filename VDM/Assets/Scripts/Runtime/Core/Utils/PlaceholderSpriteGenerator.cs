using System;
using System.IO;
using UnityEngine;

namespace VDM.Core
{
    /// <summary>
    /// Generates and loads placeholder sprites for testing and development
    /// Supports headless CLI test runs
    /// </summary>
    public class PlaceholderSpriteGenerator : MonoBehaviour
    {
        [Header("Sprite Specifications")]
        [SerializeField] private PlaceholderSpriteSpec[] spriteSpecs = new PlaceholderSpriteSpec[]
        {
            new PlaceholderSpriteSpec("grassland_hex", 64, 64, Color.green),
            new PlaceholderSpriteSpec("character_sprite", 128, 128, Color.blue),
            new PlaceholderSpriteSpec("small_building_icon", 256, 256, Color.gray),
            new PlaceholderSpriteSpec("ui_panel_background", 512, 256, Color.white),
            new PlaceholderSpriteSpec("dialogue_frame", 800, 200, Color.yellow)
        };

        [Header("Configuration")]
        [SerializeField] private string placeholderPath = "Assets/Placeholders/";
        [SerializeField] private bool generateOnStart = false;
        [SerializeField] private bool enableHeadlessMode = false;

        private Sprite[] loadedSprites;

        [System.Serializable]
        public class PlaceholderSpriteSpec
        {
            public string filename;
            public int width;
            public int height;
            public Color color;

            public PlaceholderSpriteSpec(string filename, int width, int height, Color color)
            {
                this.filename = filename;
                this.width = width;
                this.height = height;
                this.color = color;
            }
        }

        private void Start()
        {
            if (generateOnStart || enableHeadlessMode)
            {
                GenerateAndLoadSprites();
            }
        }

        /// <summary>
        /// Generate placeholder sprites and save them as PNG files
        /// </summary>
        public void GenerateAndLoadSprites()
        {
            try
            {
                Debug.Log("PlaceholderSpriteGenerator: Starting sprite generation...");
                
                // Ensure directory exists
                string fullPath = Path.Combine(Application.dataPath, "../", placeholderPath);
                if (!Directory.Exists(fullPath))
                {
                    Directory.CreateDirectory(fullPath);
                    Debug.Log($"Created directory: {fullPath}");
                }

                loadedSprites = new Sprite[spriteSpecs.Length];

                for (int i = 0; i < spriteSpecs.Length; i++)
                {
                    var spec = spriteSpecs[i];
                    string filename = $"{spec.filename}.png";
                    string filePath = Path.Combine(fullPath, filename);

                    // Generate sprite texture
                    Texture2D texture = GeneratePlaceholderTexture(spec);
                    
                    // Save as PNG
                    byte[] pngData = texture.EncodeToPNG();
                    File.WriteAllBytes(filePath, pngData);
                    
                    // Create sprite from texture
                    Sprite sprite = Sprite.Create(
                        texture,
                        new Rect(0, 0, texture.width, texture.height),
                        new Vector2(0.5f, 0.5f),
                        100.0f
                    );
                    sprite.name = spec.filename;
                    loadedSprites[i] = sprite;

                    Debug.Log($"Generated and saved: {filename} ({spec.width}x{spec.height})");
                }

                Debug.Log($"PlaceholderSpriteGenerator: Successfully generated {spriteSpecs.Length} sprites");
                
                // Display sprites if not in headless mode
                if (!enableHeadlessMode && Application.isPlaying)
                {
                    DisplaySprites();
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"PlaceholderSpriteGenerator: Error generating sprites: {ex.Message}");
            }
        }

        /// <summary>
        /// Generate a placeholder texture with the specified dimensions and color
        /// </summary>
        private Texture2D GeneratePlaceholderTexture(PlaceholderSpriteSpec spec)
        {
            Texture2D texture = new Texture2D(spec.width, spec.height, TextureFormat.RGBA32, false);
            
            // Fill with base color
            Color[] pixels = new Color[spec.width * spec.height];
            for (int i = 0; i < pixels.Length; i++)
            {
                pixels[i] = spec.color;
            }

            // Add border and pattern for visual distinction
            AddBorderAndPattern(pixels, spec);
            
            texture.SetPixels(pixels);
            texture.Apply();
            
            return texture;
        }

        /// <summary>
        /// Add border and simple pattern to make sprites visually distinct
        /// </summary>
        private void AddBorderAndPattern(Color[] pixels, PlaceholderSpriteSpec spec)
        {
            int width = spec.width;
            int height = spec.height;
            Color borderColor = Color.black;
            Color patternColor = new Color(spec.color.r * 0.8f, spec.color.g * 0.8f, spec.color.b * 0.8f, spec.color.a);

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    int index = y * width + x;
                    
                    // Border
                    if (x == 0 || x == width - 1 || y == 0 || y == height - 1)
                    {
                        pixels[index] = borderColor;
                    }
                    // Simple pattern based on sprite type
                    else if (ShouldApplyPattern(x, y, spec))
                    {
                        pixels[index] = patternColor;
                    }
                }
            }
        }

        /// <summary>
        /// Determine if pattern should be applied at given coordinates
        /// </summary>
        private bool ShouldApplyPattern(int x, int y, PlaceholderSpriteSpec spec)
        {
            switch (spec.filename)
            {
                case "grassland_hex":
                    // Hexagonal pattern
                    return (x + y) % 8 == 0;
                
                case "character_sprite":
                    // Cross pattern
                    return (x == spec.width / 2) || (y == spec.height / 2);
                
                case "small_building_icon":
                    // Grid pattern
                    return (x % 16 == 0) || (y % 16 == 0);
                
                case "ui_panel_background":
                    // Subtle dots
                    return (x % 32 == 0) && (y % 32 == 0);
                
                case "dialogue_frame":
                    // Corner decorations
                    return (x < 20 && y < 20) || (x > spec.width - 20 && y < 20) ||
                           (x < 20 && y > spec.height - 20) || (x > spec.width - 20 && y > spec.height - 20);
                
                default:
                    return false;
            }
        }

        /// <summary>
        /// Display sprites in the scene for visual verification
        /// </summary>
        private void DisplaySprites()
        {
            if (loadedSprites == null) return;

            float spacing = 2.0f;
            float startX = -(loadedSprites.Length - 1) * spacing * 0.5f;

            for (int i = 0; i < loadedSprites.Length; i++)
            {
                GameObject spriteObj = new GameObject($"PlaceholderSprite_{spriteSpecs[i].filename}");
                spriteObj.transform.parent = transform;
                spriteObj.transform.position = new Vector3(startX + i * spacing, 0, 0);

                SpriteRenderer renderer = spriteObj.AddComponent<SpriteRenderer>();
                renderer.sprite = loadedSprites[i];
                
                // Scale to reasonable size for display
                float scale = Mathf.Min(1.0f, 100.0f / Mathf.Max(spriteSpecs[i].width, spriteSpecs[i].height));
                spriteObj.transform.localScale = Vector3.one * scale;
            }
        }

        /// <summary>
        /// Get loaded sprites for external use
        /// </summary>
        public Sprite[] GetLoadedSprites()
        {
            return loadedSprites;
        }

        /// <summary>
        /// Get sprite by filename
        /// </summary>
        public Sprite GetSpriteByName(string filename)
        {
            if (loadedSprites == null) return null;

            for (int i = 0; i < spriteSpecs.Length; i++)
            {
                if (spriteSpecs[i].filename == filename)
                {
                    return loadedSprites[i];
                }
            }

            return null;
        }

        /// <summary>
        /// Static method for headless CLI testing
        /// </summary>
        public static void RunHeadlessTest()
        {
            Debug.Log("PlaceholderSpriteGenerator: Running headless test...");
            
            GameObject testObj = new GameObject("PlaceholderSpriteGenerator_Test");
            PlaceholderSpriteGenerator generator = testObj.AddComponent<PlaceholderSpriteGenerator>();
            generator.enableHeadlessMode = true;
            generator.GenerateAndLoadSprites();
            
            // Verify sprites were generated
            Sprite[] sprites = generator.GetLoadedSprites();
            if (sprites != null && sprites.Length > 0)
            {
                Debug.Log($"Headless test successful: Generated {sprites.Length} sprites");
                foreach (var sprite in sprites)
                {
                    if (sprite != null)
                    {
                        Debug.Log($"  - {sprite.name}: {sprite.texture.width}x{sprite.texture.height}");
                    }
                }
            }
            else
            {
                Debug.LogError("Headless test failed: No sprites generated");
            }
            
            DestroyImmediate(testObj);
        }

        #if UNITY_EDITOR
        [UnityEditor.MenuItem("VDM/Generate Placeholder Sprites")]
        public static void GenerateSpritesMenuItem()
        {
            GameObject generatorObj = FindObjectOfType<PlaceholderSpriteGenerator>()?.gameObject;
            if (generatorObj == null)
            {
                generatorObj = new GameObject("PlaceholderSpriteGenerator");
                generatorObj.AddComponent<PlaceholderSpriteGenerator>();
            }

            PlaceholderSpriteGenerator generator = generatorObj.GetComponent<PlaceholderSpriteGenerator>();
            generator.GenerateAndLoadSprites();
        }
        #endif
    }
} 