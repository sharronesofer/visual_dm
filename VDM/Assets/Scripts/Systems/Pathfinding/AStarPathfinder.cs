using System.Collections.Generic;
using System.Threading.Tasks;
using System.Linq;

namespace VisualDM.Systems.Pathfinding
{
    /// <summary>
    /// A* pathfinding algorithm implementation with configurable heuristics.
    /// </summary>
    public class AStarPathfinder : IPathfindingAlgorithm
    {
        public enum HeuristicType { Manhattan, Euclidean, Chebyshev }
        private HeuristicType heuristic;

        public AStarPathfinder(HeuristicType heuristicType = HeuristicType.Manhattan)
        {
            heuristic = heuristicType;
        }

        /// <summary>
        /// Asynchronously finds a path using the A* algorithm.
        /// </summary>
        public async Task<List<PathNode>> FindPathAsync(GridPosition start, GridPosition end)
        {
            return await Task.Run(() => FindPath(start, end));
        }

        private List<PathNode> FindPath(GridPosition start, GridPosition end)
        {
            var openSet = new SortedSet<(float fScore, int tieBreaker, PathNode node)>(Comparer<(float, int, PathNode)>.Create((a, b) =>
            {
                int cmp = a.fScore.CompareTo(b.fScore);
                if (cmp == 0) cmp = a.tieBreaker.CompareTo(b.tieBreaker);
                return cmp;
            }));
            var closedSet = new HashSet<GridPosition>();
            var gScore = new Dictionary<GridPosition, float>();
            var cameFrom = new Dictionary<GridPosition, PathNode?>();
            int tieBreaker = 0;

            gScore[start] = 0;
            float h = Heuristic(start, end);
            openSet.Add((h, tieBreaker++, new PathNode(start, 0, h, null)));

            while (openSet.Count > 0)
            {
                var currentTuple = openSet.Min;
                openSet.Remove(currentTuple);
                var current = currentTuple.node;

                if (current.Position.X == end.X && current.Position.Y == end.Y)
                {
                    return ReconstructPath(current);
                }

                closedSet.Add(current.Position);

                foreach (var neighbor in GetNeighbors(current.Position))
                {
                    if (closedSet.Contains(neighbor)) continue;
                    if (!IsWalkable(neighbor)) continue;

                    float tentativeG = gScore[current.Position] + 1; // Assume cost=1 for all moves
                    if (!gScore.ContainsKey(neighbor) || tentativeG < gScore[neighbor])
                    {
                        gScore[neighbor] = tentativeG;
                        float f = tentativeG + Heuristic(neighbor, end);
                        var neighborNode = new PathNode(neighbor, tentativeG, Heuristic(neighbor, end), current);
                        openSet.Add((f, tieBreaker++, neighborNode));
                        cameFrom[neighbor] = current;
                    }
                }
            }
            return new List<PathNode>(); // No path found
        }

        private List<PathNode> ReconstructPath(PathNode node)
        {
            var path = new List<PathNode>();
            PathNode? current = node;
            while (current != null)
            {
                path.Add(current.Value);
                current = current.Value.Parent;
            }
            path.Reverse();
            return path;
        }

        private float Heuristic(GridPosition a, GridPosition b)
        {
            int dx = System.Math.Abs(a.X - b.X);
            int dy = System.Math.Abs(a.Y - b.Y);
            switch (heuristic)
            {
                case HeuristicType.Manhattan:
                    return dx + dy;
                case HeuristicType.Euclidean:
                    return (float)System.Math.Sqrt(dx * dx + dy * dy);
                case HeuristicType.Chebyshev:
                    return System.Math.Max(dx, dy);
                default:
                    return dx + dy;
            }
        }

        private IEnumerable<GridPosition> GetNeighbors(GridPosition pos)
        {
            // 4-way movement (up, down, left, right)
            yield return new GridPosition(pos.X + 1, pos.Y);
            yield return new GridPosition(pos.X - 1, pos.Y);
            yield return new GridPosition(pos.X, pos.Y + 1);
            yield return new GridPosition(pos.X, pos.Y - 1);
            // Optionally add diagonals for 8-way movement
        }

        private bool IsWalkable(GridPosition pos)
        {
            // TODO: Integrate with grid and dynamic obstacle system
            return true;
        }
    }
} 