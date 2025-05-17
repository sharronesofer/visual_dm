using System.Collections.Generic;

namespace VisualDM.Systems.Pathfinding
{
    /// <summary>
    /// LRU cache for storing and retrieving computed paths.
    /// </summary>
    public class PathCache
    {
        // TODO: Implement LRU logic and path validity checks
        private Dictionary<string, List<PathNode>> cache = new Dictionary<string, List<PathNode>>();

        public List<PathNode> Get(GridPosition start, GridPosition end, string algorithm)
        {
            string key = GetKey(start, end, algorithm);
            if (cache.TryGetValue(key, out var path))
                return path;
            return null;
        }

        public void Add(GridPosition start, GridPosition end, string algorithm, List<PathNode> path)
        {
            string key = GetKey(start, end, algorithm);
            cache[key] = path;
        }

        public void Clear()
        {
            cache.Clear();
        }

        private string GetKey(GridPosition start, GridPosition end, string algorithm)
        {
            return $"{algorithm}:{start.X},{start.Y}->{end.X},{end.Y}";
        }
    }
} 