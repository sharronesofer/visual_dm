using UnityEngine;

namespace VDM.NPC
{
    /// <summary>
    /// Displays a visual indicator above an NPC when they have a new rumor.
    /// </summary>
    public class RumorIndicator : MonoBehaviour
    {
        public Sprite IconSprite;
        private GameObject iconObject;
        private float yOffset = 1.5f;

        void Start()
        {
            if (IconSprite == null)
            {
                // Create a simple default icon (red circle)
                Texture2D tex = new Texture2D(16, 16);
                Color[] pixels = new Color[16 * 16];
                for (int i = 0; i < pixels.Length; i++) pixels[i] = Color.clear;
                for (int y = 4; y < 12; y++)
                    for (int x = 4; x < 12; x++)
                        if ((x - 8) * (x - 8) + (y - 8) * (y - 8) < 16)
                            tex.SetPixel(x, y, Color.red);
                tex.Apply();
                IconSprite = Sprite.Create(tex, new Rect(0, 0, 16, 16), new Vector2(0.5f, 0.5f));
            }
            iconObject = new GameObject("RumorIcon");
            iconObject.transform.SetParent(transform);
            iconObject.transform.localPosition = new Vector3(0, yOffset, 0);
            var sr = iconObject.AddComponent<SpriteRenderer>();
            sr.sprite = IconSprite;
            sr.sortingOrder = 100;
        }

        /// <summary>
        /// Remove the indicator (e.g., when rumor is acknowledged or expires).
        /// </summary>
        public void RemoveIndicator()
        {
            if (iconObject != null)
                Destroy(iconObject);
        }
    }
} 