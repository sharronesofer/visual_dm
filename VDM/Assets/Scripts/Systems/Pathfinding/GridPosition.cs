namespace VisualDM.Systems.Pathfinding
{
    /// <summary>
    /// Represents a position on the grid for pathfinding.
    /// </summary>
    public struct GridPosition
    {
        public int X;
        public int Y;

        public GridPosition(int x, int y)
        {
            X = x;
            Y = y;
        }
    }
} 