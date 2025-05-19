using UnityEngine;
using System.Collections;

namespace VisualDM.Systems
{
    /// <summary>
    /// Entry point for the Visual DM application.
    /// This script is attached to the only GameObject in the Bootstrap scene.
    /// </summary>
    public class GameLoader : MonoBehaviour
    {
        // Configuration options
        [SerializeField] private int seed = 0;
        [SerializeField] private bool useFixedSeed = false;
        [SerializeField] private float initializationTimeout = 30f;
        
        // Initialization tracking
        private bool _initializationComplete = false;
        private GameObject _statusIndicator;
        
        private void Start()
        {
            Debug.Log("Visual DM GameLoader initializing...");
            
            // Create a status indicator to show initialization progress
            CreateStatusIndicator();
            
            // Initialize the GameManager with optional fixed seed
            if (useFixedSeed && seed != 0)
            {
                // Use reflection to set the seed directly on the GameManager
                var gameManagerObj = GameManager.Instance.gameObject;
                var gameManagerComponent = gameManagerObj.GetComponent<GameManager>();
                var seedField = gameManagerComponent.GetType().GetField("Seed", 
                    System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                
                if (seedField != null)
                {
                    seedField.SetValue(gameManagerComponent, seed);
                    Debug.Log($"Using fixed seed: {seed}");
                }
            }
            
            // Subscribe to initialization complete event
            GameManager.Instance.OnInitializationComplete += OnInitializationComplete;
            
            // Start the initialization timeout coroutine
            StartCoroutine(InitializationTimeoutCoroutine());
        }
        
        /// <summary>
        /// Update the status indicator based on initialization state
        /// </summary>
        private void Update()
        {
            if (_statusIndicator != null)
            {
                // Update indicator color based on initialization status
                var renderer = _statusIndicator.GetComponent<SpriteRenderer>();
                if (renderer != null)
                {
                    renderer.color = _initializationComplete ? Color.green : Color.yellow;
                }
            }
        }
        
        /// <summary>
        /// Handle the completion of GameManager initialization
        /// </summary>
        private void OnInitializationComplete()
        {
            _initializationComplete = true;
            Debug.Log("GameManager initialization complete.");
            
            // Update the status indicator
            if (_statusIndicator != null)
            {
                var renderer = _statusIndicator.GetComponent<SpriteRenderer>();
                if (renderer != null)
                {
                    renderer.color = Color.green;
                }
            }
            
            // Destroy this GameObject when initialization is complete
            // This will leave only the GameManager and its children active
            Destroy(gameObject, 1f); // Wait a moment before destroying for visual feedback
        }
        
        /// <summary>
        /// Create a visual indicator for initialization status
        /// </summary>
        private void CreateStatusIndicator()
        {
            _statusIndicator = new GameObject("InitializationStatusIndicator");
            var renderer = _statusIndicator.AddComponent<SpriteRenderer>();
            renderer.sortingOrder = 100;
            renderer.sprite = GenerateCircleSprite(Color.yellow);
            _statusIndicator.transform.position = new Vector3(0, 0, -1);
            
            // Don't destroy the indicator when this object is destroyed
            DontDestroyOnLoad(_statusIndicator);
        }
        
        /// <summary>
        /// Watch for initialization timeout
        /// </summary>
        private IEnumerator InitializationTimeoutCoroutine()
        {
            float timer = 0f;
            
            while (!_initializationComplete && timer < initializationTimeout)
            {
                timer += Time.deltaTime;
                yield return null;
            }
            
            if (!_initializationComplete)
            {
                Debug.LogError($"GameManager initialization timed out after {initializationTimeout} seconds!");
                
                // Update status indicator to show error
                if (_statusIndicator != null)
                {
                    var renderer = _statusIndicator.GetComponent<SpriteRenderer>();
                    if (renderer != null)
                    {
                        renderer.color = Color.red;
                    }
                }
            }
        }
        
        /// <summary>
        /// Generate a simple circle sprite for the status indicator
        /// </summary>
        private Sprite GenerateCircleSprite(Color color)
        {
            int size = 32;
            Texture2D texture = new Texture2D(size, size, TextureFormat.RGBA32, false);
            Color[] pixels = new Color[size * size];
            
            // Create a circle
            Vector2 center = new Vector2(size / 2f, size / 2f);
            float radius = size / 2f - 2f; // Slightly smaller than half size
            
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    float distance = Vector2.Distance(new Vector2(x, y), center);
                    int index = y * size + x;
                    
                    if (distance <= radius)
                    {
                        pixels[index] = color;
                    }
                    else
                    {
                        pixels[index] = new Color(0, 0, 0, 0); // Transparent
                    }
                }
            }
            
            texture.SetPixels(pixels);
            texture.Apply();
            
            return Sprite.Create(texture, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), 100f);
        }
    }
} 