using UnityEngine;

namespace VisualDM.UI
{
    public static class Borders
    {
        // Border widths (in Unity units)
        public const float Thin = 1f;
        public const float Regular = 2f;
        public const float Thick = 4f;

        // Border radii (for rounded corners)
        public const float None = 0f;
        public const float Small = 4f;
        public const float Medium = 8f;
        public const float Large = 16f;

        // Border colors
        public static readonly Color Default = Colors.Neutral300;
        public static readonly Color Focus = Colors.PrimaryDefault;
        public static readonly Color Error = new Color(0.85f, 0.20f, 0.20f, 1.0f); // #D93333

        // Usage:
        // - Use Thin/Regular/Thick for border width
        // - Use Small/Medium/Large for corner radius
        // - Use Default/Focus/Error for border color states
    }
} 