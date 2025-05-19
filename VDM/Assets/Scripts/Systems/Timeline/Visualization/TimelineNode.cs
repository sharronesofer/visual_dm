using UnityEngine;
using VisualDM.Timeline.Models;
using System;

namespace VisualDM.Timeline.Visualization
{
    public class TimelineNode : MonoBehaviour
    {
        public Feat FeatData { get; private set; }
        public SpriteRenderer Renderer { get; private set; }
        public bool IsSelected { get; private set; }
        public bool IsHighlighted { get; private set; }

        public event Action<TimelineNode> OnPointerEnter;
        public event Action<TimelineNode> OnPointerExit;
        public event Action<TimelineNode> OnPointerClick;

        public void Initialize(Feat feat, Color color)
        {
            FeatData = feat;
            Renderer = gameObject.AddComponent<SpriteRenderer>();
            Renderer.sprite = CreateCircleSprite();
            Renderer.color = color;
            transform.localScale = Vector3.one * 0.5f;
        }

        private Sprite CreateCircleSprite()
        {
            // Placeholder: Use a built-in or generated circle sprite
            // In production, replace with a proper asset or procedural circle
            Texture2D tex = new Texture2D(32, 32);
            Color[] pixels = new Color[32 * 32];
            Vector2 center = new Vector2(15.5f, 15.5f);
            for (int y = 0; y < 32; y++)
            for (int x = 0; x < 32; x++)
            {
                float dist = Vector2.Distance(new Vector2(x, y), center);
                pixels[y * 32 + x] = dist < 15.5f ? Color.white : Color.clear;
            }
            tex.SetPixels(pixels);
            tex.Apply();
            return Sprite.Create(tex, new Rect(0, 0, 32, 32), new Vector2(0.5f, 0.5f));
        }

        private void OnMouseEnter()
        {
            OnPointerEnter?.Invoke(this);
            if (!IsHighlighted)
                Renderer.color *= 1.2f;
        }

        private void OnMouseExit()
        {
            OnPointerExit?.Invoke(this);
            if (!IsHighlighted)
                Renderer.color = GetColorByCategory(FeatData.Category);
        }

        private void OnMouseDown()
        {
            OnPointerClick?.Invoke(this);
        }

        public void SetHighlight(bool highlight, Color? highlightColor = null)
        {
            IsHighlighted = highlight;
            if (highlight)
                Renderer.color = highlightColor ?? Color.yellow;
            else
                Renderer.color = GetColorByCategory(FeatData.Category);
        }

        private Color GetColorByCategory(FeatCategory category)
        {
            switch (category)
            {
                case FeatCategory.Combat: return new Color(0.8f, 0.2f, 0.2f);
                case FeatCategory.Magic: return new Color(0.2f, 0.4f, 0.8f);
                case FeatCategory.Utility: return new Color(0.2f, 0.8f, 0.4f);
                case FeatCategory.Social: return new Color(0.8f, 0.6f, 0.2f);
                case FeatCategory.Exploration: return new Color(0.5f, 0.3f, 0.8f);
                default: return Color.gray;
            }
        }
    }
} 