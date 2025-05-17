using UnityEngine;

namespace VisualDM.UI.DesignTokens
{
    public struct Shadow
    {
        public Vector2 Offset;
        public float Blur;
        public Color Color;
        public Shadow(Vector2 offset, float blur, Color color)
        {
            Offset = offset;
            Blur = blur;
            Color = color;
        }
    }

    public static class Shadows
    {
        // Shadow levels for elevation states
        public static readonly Shadow Level1 = new Shadow(new Vector2(0, -2), 4f, new Color(0, 0, 0, 0.10f));
        public static readonly Shadow Level2 = new Shadow(new Vector2(0, -4), 8f, new Color(0, 0, 0, 0.15f));
        public static readonly Shadow Level3 = new Shadow(new Vector2(0, -8), 16f, new Color(0, 0, 0, 0.20f));
        public static readonly Shadow Level4 = new Shadow(new Vector2(0, -12), 24f, new Color(0, 0, 0, 0.25f));

        // Usage:
        // - Level1: cards, panels
        // - Level2: modals, popups
        // - Level3: tooltips, overlays
        // - Level4: highest elevation (menus, dialogs)
    }
} 