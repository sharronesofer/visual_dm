namespace AI
{
    public static class TemplateVersion
    {
        public static int CompareVersions(string v1, string v2)
        {
            // Simple dot-separated version comparison (e.g., "1.0" vs "1.1")
            var parts1 = v1.Split('.');
            var parts2 = v2.Split('.');
            int len = System.Math.Max(parts1.Length, parts2.Length);
            for (int i = 0; i < len; i++)
            {
                int p1 = i < parts1.Length ? int.Parse(parts1[i]) : 0;
                int p2 = i < parts2.Length ? int.Parse(parts2[i]) : 0;
                if (p1 != p2) return p1.CompareTo(p2);
            }
            return 0;
        }

        public static bool IsValidVersion(string version)
        {
            // Accepts "major.minor" format
            return System.Text.RegularExpressions.Regex.IsMatch(version, "^\\d+\\.\\d+$");
        }

        // Stub for migration path logic
        public static bool HasMigrationPath(string fromVersion, string toVersion)
        {
            // In a real system, check for migration scripts or logic
            return false;
        }
    }
} 