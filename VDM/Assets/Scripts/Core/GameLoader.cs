using UnityEngine;
using System.Threading.Tasks;

namespace VisualDM.Core
{
    public class GameLoader : MonoBehaviour
    {
        public int seed = 0;
        
        private bool _dataSystemInitialized = false;

        void Start()
        {
            // Initialize the modular data system first
            UnityEngine.Debug.Log("Initializing modular data system...");
            
            // Create status indicator for modular data system
            var dataIndicator = new GameObject("ModularDataStatusIndicator");
            var dataSprite = dataIndicator.AddComponent<SpriteRenderer>();
            dataIndicator.transform.position = new Vector3(0f, 4f, 0f); // Top-center
            dataSprite.sortingOrder = 100;
            dataSprite.drawMode = SpriteDrawMode.Simple;
            dataSprite.sprite = GenerateCircleSprite(_dataSystemInitialized ? Color.green : Color.red);
            DontDestroyOnLoad(dataIndicator);

            Destroy(gameObject);
        }
        
        /// <summary>
        /// Called when the data system is fully initialized.
        /// </summary>
        private void OnDataSystemInitialized()
        {
            _dataSystemInitialized = true;
            UnityEngine.Debug.Log("Modular data system initialization event received.");
        }

        // Utility: Generate a simple circle sprite at runtime
        private Sprite GenerateCircleSprite(Color color)
        {
            int diameter = 32;
            Texture2D tex = new Texture2D(diameter, diameter, TextureFormat.ARGB32, false);
            Color[] pixels = new Color[diameter * diameter];
            float r = diameter / 2f;
            Vector2 center = new Vector2(r, r);
            for (int y = 0; y < diameter; y++)
            {
                for (int x = 0; x < diameter; x++)
                {
                    float dist = Vector2.Distance(new Vector2(x, y), center);
                    if (dist <= r)
                        pixels[y * diameter + x] = color;
                    else
                        pixels[y * diameter + x] = new Color(0, 0, 0, 0);
                }
            }
            tex.SetPixels(pixels);
            tex.Apply();
            return Sprite.Create(tex, new Rect(0, 0, diameter, diameter), new Vector2(0.5f, 0.5f), 32);
        }
    }
} 