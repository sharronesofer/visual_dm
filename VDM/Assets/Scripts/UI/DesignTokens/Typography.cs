using UnityEngine;
using TMPro;

namespace VisualDM.UI
{
    public static class Typography
    {
        // Font Sizes (in Unity units)
        public const float HeadingLarge = 32f;
        public const float HeadingMedium = 24f;
        public const float HeadingSmall = 18f;
        public const float Body = 14f;
        public const float Caption = 12f;
        public const float Code = 13f;

        // Line Heights (multipliers)
        public const float HeadingLineHeight = 1.2f;
        public const float BodyLineHeight = 1.4f;
        public const float CodeLineHeight = 1.3f;

        // Font Weights (TMP uses font asset weights, but we can document intended usage)
        public const FontWeight HeadingWeight = FontWeight.Bold;
        public const FontWeight BodyWeight = FontWeight.Regular;
        public const FontWeight CodeWeight = FontWeight.Regular;

        // Font Asset References (assign at runtime via GameLoader or ThemeManager)
        public static TMP_FontAsset SansFont;
        public static TMP_FontAsset MonoFont;

        // Usage documentation
        // - Use HeadingLarge/Medium/Small for h1/h2/h3
        // - Use Body for standard text
        // - Use Code for code blocks/monospace
        // - Assign SansFont and MonoFont at runtime (e.g., in GameLoader)
    }
} 