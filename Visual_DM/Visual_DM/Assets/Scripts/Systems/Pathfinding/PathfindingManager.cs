using System.Collections.Generic;
using System.Threading.Tasks;

namespace VisualDM.Systems.Pathfinding
{
    /// <summary>
    /// Central manager for handling pathfinding requests, algorithm selection, and path caching.
    /// </summary>
    public class PathfindingManager
    {
        // Singleton instance
        public static PathfindingManager Instance { get; private set; }

        private Dictionary<string, IPathfindingAlgorithm> algorithms;
        private PathCache pathCache;

        public PathfindingManager()
        {
            Instance = this;
            algorithms = new Dictionary<string, IPathfindingAlgorithm>();
            pathCache = new PathCache();
            RegisterDefaultAlgorithms();
        }

        /// <summary>
        /// Registers the default pathfinding algorithms (A*, JPS, Hierarchical).
        /// </summary>
        private void RegisterDefaultAlgorithms()
        {
            algorithms["AStar"] = new AStarPathfinder();
            algorithms["JPS"] = new JPSPathfinder();
            algorithms["Hierarchical"] = new HierarchicalPathfinder();
        }

        /// <summary>
        /// Requests a path asynchronously using the specified algorithm.
        /// </summary>
        /// <param name="start">Start position.</param>
        /// <param name="end">End position.</param>
        /// <param name="algorithm">Algorithm name (default: AStar).</param>
        /// <returns>List of path nodes or null if no path found.</returns>
        public async Task<List<PathNode>> RequestPathAsync(GridPosition start, GridPosition end, string algorithm = "AStar")
        {
            // Check cache first
            var cached = pathCache.Get(start, end, algorithm);
            if (cached != null)
                return cached;

            if (!algorithms.ContainsKey(algorithm))
                algorithm = "AStar";

            var path = await algorithms[algorithm].FindPathAsync(start, end);
            if (path != null)
                pathCache.Add(start, end, algorithm, path);
            return path;
        }

        /// <summary>
        /// Clears the path cache.
        /// </summary>
        public void ClearCache()
        {
            pathCache.Clear();
        }

        /// <summary>
        /// Selects the best algorithm based on context (terrain, distance, computational budget).
        /// </summary>
        /// <param name="start">Start position.</param>
        /// <param name="end">End position.</param>
        /// <param name="context">Optional context object.</param>
        /// <returns>Algorithm name.</returns>
        public string SelectAlgorithm(GridPosition start, GridPosition end, object context = null)
        {
            // TODO: Implement context-based selection logic
            return "AStar";
        }

        /// <summary>
        /// Checks if the cell at the given grid position is walkable.
        /// </summary>
        /// <param name="pos">The grid position to check.</param>
        /// <returns>True if walkable, false if blocked or out of bounds.</returns>
        public static bool IsWalkable(GridPosition pos)
        {
            // Example integration: assumes a singleton DynamicGrid instance and chunk size
            var grid = Grid.DynamicGridInstance; // You may need to adjust this accessor
            if (grid == null) return false;
            var (x, y) = pos.ToInt();
            var chunkManager = grid.ChunkManager; // You may need to adjust this accessor
            var chunk = chunkManager.GetOrLoadChunk(new UnityEngine.Vector2(x, y));
            int localX = x % chunk.ChunkSize;
            int localY = y % chunk.ChunkSize;
            if (localX < 0 || localY < 0 || localX >= chunk.ChunkSize || localY >= chunk.ChunkSize)
                return false;
            var cell = chunk[localX, localY];
            return cell != null && cell.IsWalkable;
        }

        /// <summary>
        /// Returns a list of walkable neighboring grid positions (4-way movement).
        /// </summary>
        /// <param name="pos">The current grid position.</param>
        /// <returns>List of walkable neighbor positions.</returns>
        public static List<GridPosition> GetWalkableNeighbors(GridPosition pos)
        {
            var neighbors = new List<GridPosition>();
            var (x, y) = pos.ToInt();
            var directions = new (int dx, int dy)[]
            {
                (0, 1),  // Up
                (0, -1), // Down
                (-1, 0), // Left
                (1, 0)   // Right
            };
            foreach (var (dx, dy) in directions)
            {
                var neighbor = GridPosition.FromInt(x + dx, y + dy);
                if (IsWalkable(neighbor))
                    neighbors.Add(neighbor);
            }
            return neighbors;
        }
    }
} 