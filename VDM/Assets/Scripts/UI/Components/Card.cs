using UnityEngine;
using VisualDM.UI.DesignTokens;

namespace VisualDM.UI
{
    /// <summary>
    /// Runtime-generated card component for Unity 2D UI.
    /// Supports elevation (shadow), border radius, and content slotting. No scene references.
    /// </summary>
    public class Card : MonoBehaviour
    {
        public int Elevation = 1; // 1-4
        public float Width = 320f;
        public float Height = 180f;
        public float BorderRadius = Borders.Medium;
        public Color Background = Colors.Neutral100;

        private SpriteRenderer _background;
        private SpriteRenderer _shadow;

        void Awake()
        {
            // Shadow
            _shadow = new GameObject("Shadow").AddComponent<SpriteRenderer>();
            _shadow.transform.SetParent(transform, false);
            _shadow.transform.localPosition = new Vector3(0, -4, 1);
            _shadow.drawMode = SpriteDrawMode.Sliced;
            _shadow.size = new Vector2(Width, Height);
            // Background
            _background = gameObject.AddComponent<SpriteRenderer>();
            _background.drawMode = SpriteDrawMode.Sliced;
            _background.size = new Vector2(Width, Height);
            // Initial style
            ApplyStyle();
        }

        public void SetElevation(int level)
        {
            Elevation = Mathf.Clamp(level, 1, 4);
            ApplyStyle();
        }

        public void SetBackground(Color color)
        {
            Background = color;
            ApplyStyle();
        }

        public void SetSize(float width, float height)
        {
            Width = width;
            Height = height;
            _background.size = new Vector2(width, height);
            _shadow.size = new Vector2(width, height);
        }

        private void ApplyStyle()
        {
            // Shadow
            var shadow = Elevation switch
            {
                1 => Shadows.Level1,
                2 => Shadows.Level2,
                3 => Shadows.Level3,
                4 => Shadows.Level4,
                _ => Shadows.Level1
            };
            _shadow.color = shadow.Color;
            _shadow.transform.localPosition = new Vector3(shadow.Offset.x, shadow.Offset.y, 1);
            // Background
            _background.color = Background;
            // TODO: Apply border radius using 9-slice sprite or custom mesh
        }
    }
} 