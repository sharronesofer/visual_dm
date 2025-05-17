using System.Collections.Generic;
using System;
using System.Linq;

namespace VisualDM.Systems.Pathfinding
{
    /// <summary>
    /// Provides static methods for path smoothing (Bezier, string-pulling, angle-based).
    /// </summary>
    public static class PathSmoother
    {
        /// <summary>
        /// Smooths a path using quadratic Bezier curves.
        /// </summary>
        public static List<GridPosition> BezierSmooth(List<GridPosition> path, int segments = 10)
        {
            if (path == null || path.Count < 3) return path;
            var smoothed = new List<GridPosition> { path[0] };
            for (int i = 0; i < path.Count - 2; i += 2)
            {
                var p0 = path[i];
                var p1 = path[i + 1];
                var p2 = path[i + 2];
                for (int t = 1; t <= segments; t++)
                {
                    float u = t / (float)segments;
                    float x = (1 - u) * (1 - u) * p0.X + 2 * (1 - u) * u * p1.X + u * u * p2.X;
                    float y = (1 - u) * (1 - u) * p0.Y + 2 * (1 - u) * u * p1.Y + u * u * p2.Y;
                    smoothed.Add(new GridPosition((int)Math.Round(x), (int)Math.Round(y)));
                }
            }
            if (!smoothed.Contains(path[^1])) smoothed.Add(path[^1]);
            return smoothed;
        }

        /// <summary>
        /// Smooths a path using the string-pulling technique (removes unnecessary waypoints).
        /// </summary>
        public static List<GridPosition> StringPull(List<GridPosition> path)
        {
            if (path == null || path.Count < 3) return path;
            var result = new List<GridPosition> { path[0] };
            int anchor = 0;
            for (int i = 2; i < path.Count; i++)
            {
                if (!IsLineClear(path[anchor], path[i]))
                {
                    result.Add(path[i - 1]);
                    anchor = i - 1;
                }
            }
            result.Add(path[^1]);
            return result;
        }

        /// <summary>
        /// Smooths a path by reducing sharp angles.
        /// </summary>
        public static List<GridPosition> AngleSmooth(List<GridPosition> path, float maxAngle = 45f)
        {
            if (path == null || path.Count < 3) return path;
            var result = new List<GridPosition> { path[0] };
            for (int i = 1; i < path.Count - 1; i++)
            {
                var prev = path[i - 1];
                var curr = path[i];
                var next = path[i + 1];
                float angle = GetAngle(prev, curr, next);
                if (Math.Abs(angle) > maxAngle)
                    continue; // Remove sharp turn
                result.Add(curr);
            }
            result.Add(path[^1]);
            return result;
        }

        // Helper: Checks if a straight line between two points is clear (stub, always true)
        private static bool IsLineClear(GridPosition a, GridPosition b)
        {
            // TODO: Integrate with grid/obstacle system
            return true;
        }

        // Helper: Calculates the angle between three points
        private static float GetAngle(GridPosition a, GridPosition b, GridPosition c)
        {
            float abx = b.X - a.X;
            float aby = b.Y - a.Y;
            float bcx = c.X - b.X;
            float bcy = c.Y - b.Y;
            float dot = abx * bcx + aby * bcy;
            float mag1 = (float)Math.Sqrt(abx * abx + aby * aby);
            float mag2 = (float)Math.Sqrt(bcx * bcx + bcy * bcy);
            if (mag1 == 0 || mag2 == 0) return 0;
            float cos = dot / (mag1 * mag2);
            cos = Math.Clamp(cos, -1f, 1f);
            return (float)(Math.Acos(cos) * (180.0 / Math.PI));
        }
    }
} 