namespace VisualDM.UI.DesignTokens
{
    public static class Spacing
    {
        // Base unit (4px grid, mapped to Unity units as needed)
        public const float Unit = 4f;
        public const float XSmall = Unit;         // 4
        public const float Small = Unit * 2;      // 8
        public const float Medium = Unit * 4;     // 16
        public const float Large = Unit * 6;      // 24
        public const float XLarge = Unit * 8;     // 32

        // Compound spacing (for layouts)
        public const float Section = Unit * 12;   // 48
        public const float Page = Unit * 20;      // 80

        // Usage:
        // - Use XSmall/Small for tight padding
        // - Medium/Large for standard margins
        // - Section/Page for major layout spacing
    }
} 