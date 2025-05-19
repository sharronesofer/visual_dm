using UnityEngine;
using VisualDM.UI.DesignTokens;

namespace VisualDM.UI
{
    /// <summary>
    /// Runtime-generated icon component for Unity 2D UI.
    /// Supports sprite loading by name, color tinting, and sizing. No scene references.
    /// </summary>
    public class Icon : MonoBehaviour
    {
        public string IconName;
        public Color Tint = Colors.Neutral900;
        public float Size = 24f;
        private SpriteRenderer _renderer;

        void Awake()
        {
            _renderer = gameObject.AddComponent<SpriteRenderer>();
            ApplyStyle();
        }

        public void SetIcon(string iconName, Sprite sprite = null)
        {
            IconName = iconName;
            if (sprite != null)
                _renderer.sprite = sprite;
            else
                _renderer.sprite = Resources.Load<Sprite>(iconName); // Assumes icon is in Resources
            ApplyStyle();
        }

        public void SetTint(Color color)
        {
            Tint = color;
            ApplyStyle();
        }

        public void SetSize(float size)
        {
            Size = size;
            transform.localScale = Vector3.one * (Size / 100f); // Normalize to 100px base
        }

        private void ApplyStyle()
        {
            _renderer.color = Tint;
            SetSize(Size);
        }
    }
} 