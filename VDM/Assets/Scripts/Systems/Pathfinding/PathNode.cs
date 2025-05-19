namespace VisualDM.Systems.Pathfinding
{
    /// <summary>
    /// Represents a node in a path, including grid position and optional metadata.
    /// </summary>
    public struct PathNode
    {
        public GridPosition Position;
        public float Cost;
        public float Heuristic;
        public PathNode? Parent;

        public PathNode(GridPosition position, float cost = 0, float heuristic = 0, PathNode? parent = null)
        {
            Position = position;
            Cost = cost;
            Heuristic = heuristic;
            Parent = parent;
        }
    }
} 