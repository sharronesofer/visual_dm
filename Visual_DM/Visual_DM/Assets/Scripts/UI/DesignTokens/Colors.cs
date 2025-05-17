using UnityEngine;

namespace VisualDM.UI.DesignTokens
{
    public static class Colors
    {
        // Primary Colors
        public static readonly Color PrimaryDefault = new Color(0.20f, 0.40f, 0.80f, 1.0f); // #3366CC
        public static readonly Color PrimaryHover = new Color(0.25f, 0.45f, 0.85f, 1.0f);   // #3F73D9
        public static readonly Color PrimaryActive = new Color(0.16f, 0.32f, 0.64f, 1.0f);  // #2951A3

        // Secondary Colors
        public static readonly Color SecondaryDefault = new Color(0.95f, 0.65f, 0.21f, 1.0f); // #F5A634
        public static readonly Color SecondaryHover = new Color(0.98f, 0.72f, 0.36f, 1.0f);   // #FBC05C
        public static readonly Color SecondaryActive = new Color(0.80f, 0.52f, 0.13f, 1.0f);  // #CC851F

        // Neutral Colors
        public static readonly Color Neutral100 = new Color(1.0f, 1.0f, 1.0f, 1.0f);   // #FFFFFF
        public static readonly Color Neutral200 = new Color(0.95f, 0.95f, 0.95f, 1.0f); // #F2F2F2
        public static readonly Color Neutral300 = new Color(0.85f, 0.85f, 0.85f, 1.0f); // #D9D9D9
        public static readonly Color Neutral400 = new Color(0.60f, 0.60f, 0.60f, 1.0f); // #999999
        public static readonly Color Neutral500 = new Color(0.30f, 0.30f, 0.30f, 1.0f); // #4D4D4D
        public static readonly Color Neutral900 = new Color(0.07f, 0.07f, 0.07f, 1.0f); // #121212

        // Accessibility: WCAG contrast ratio calculation
        public static float GetLuminance(Color color)
        {
            float Linear(float c) => (c <= 0.03928f) ? c / 12.92f : Mathf.Pow((c + 0.055f) / 1.055f, 2.4f);
            return 0.2126f * Linear(color.r) + 0.7152f * Linear(color.g) + 0.0722f * Linear(color.b);
        }

        public static float ContrastRatio(Color a, Color b)
        {
            float l1 = GetLuminance(a);
            float l2 = GetLuminance(b);
            if (l1 < l2) (l1, l2) = (l2, l1);
            return (l1 + 0.05f) / (l2 + 0.05f);
        }

        public static bool MeetsWcagAA(Color a, Color b, bool largeText = false)
        {
            float ratio = ContrastRatio(a, b);
            return largeText ? ratio >= 3.0f : ratio >= 4.5f;
        }

        public static bool MeetsWcagAAA(Color a, Color b, bool largeText = false)
        {
            float ratio = ContrastRatio(a, b);
            return largeText ? ratio >= 4.5f : ratio >= 7.0f;
        }
    }
} 