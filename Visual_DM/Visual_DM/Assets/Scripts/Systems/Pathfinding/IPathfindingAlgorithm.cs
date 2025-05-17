using System.Collections.Generic;
using System.Threading.Tasks;

namespace VisualDM.Systems.Pathfinding
{
    /// <summary>
    /// Interface for pathfinding algorithms.
    /// </summary>
    public interface IPathfindingAlgorithm
    {
        /// <summary>
        /// Asynchronously finds a path between two grid positions.
        /// </summary>
        /// <param name="start">Start position.</param>
        /// <param name="end">End position.</param>
        /// <returns>List of path nodes or null if no path found.</returns>
        Task<List<PathNode>> FindPathAsync(GridPosition start, GridPosition end);
    }
} 