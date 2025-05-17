using System.Collections.Generic;
using System.Threading.Tasks;
using System.Linq;

namespace VisualDM.Systems.Pathfinding
{
    /// <summary>
    /// Jump Point Search (JPS) pathfinding algorithm implementation for grid-based optimization.
    /// </summary>
    public class JPSPathfinder : IPathfindingAlgorithm
    {
        public JPSPathfinder() { }

        /// <summary>
        /// Asynchronously finds a path using the JPS algorithm.
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

                foreach (var dir in Directions)
                {
                    var jumpPoint = Jump(current.Position, dir, end);
                    if (jumpPoint == null) continue;
                    if (closedSet.Contains(jumpPoint.Value)) continue;
                    if (!IsWalkable(jumpPoint.Value)) continue;

                    float tentativeG = gScore[current.Position] + Distance(current.Position, jumpPoint.Value);
                    if (!gScore.ContainsKey(jumpPoint.Value) || tentativeG < gScore[jumpPoint.Value])
                    {
                        gScore[jumpPoint.Value] = tentativeG;
                        float f = tentativeG + Heuristic(jumpPoint.Value, end);
                        var neighborNode = new PathNode(jumpPoint.Value, tentativeG, Heuristic(jumpPoint.Value, end), current);
                        openSet.Add((f, tieBreaker++, neighborNode));
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
            return dx + dy; // Manhattan for 4-way
        }

        private float Distance(GridPosition a, GridPosition b)
        {
            int dx = System.Math.Abs(a.X - b.X);
            int dy = System.Math.Abs(a.Y - b.Y);
            return dx + dy;
        }

        private static readonly List<GridPosition> Directions = new List<GridPosition>
        {
            new GridPosition(1, 0),  // Right
            new GridPosition(-1, 0), // Left
            new GridPosition(0, 1),  // Up
            new GridPosition(0, -1)  // Down
        };

        private GridPosition? Jump(GridPosition pos, GridPosition dir, GridPosition end)
        {
            var next = new GridPosition(pos.X + dir.X, pos.Y + dir.Y);
            if (!IsWalkable(next)) return null;
            if (next.X == end.X && next.Y == end.Y) return next;

            // Forced neighbor check for 4-way
            if (dir.X != 0)
            {
                if ((!IsWalkable(new GridPosition(next.X, next.Y + 1)) && IsWalkable(new GridPosition(pos.X, pos.Y + 1))) ||
                    (!IsWalkable(new GridPosition(next.X, next.Y - 1)) && IsWalkable(new GridPosition(pos.X, pos.Y - 1))))
                    return next;
            }
            else if (dir.Y != 0)
            {
                if ((!IsWalkable(new GridPosition(next.X + 1, next.Y)) && IsWalkable(new GridPosition(pos.X + 1, pos.Y))) ||
                    (!IsWalkable(new GridPosition(next.X - 1, next.Y)) && IsWalkable(new GridPosition(pos.X - 1, pos.Y))))
                    return next;
            }

            return Jump(next, dir, end);
        }

        private bool IsWalkable(GridPosition pos)
        {
            // TODO: Integrate with grid and dynamic obstacle system
            return true;
        }
    }
} 