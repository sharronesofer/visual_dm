using System;
using VisualDM.Core;

namespace VisualDM.Grid
{
    /// <summary>
    /// Grid position using high-precision fixed-point coordinates.
    /// </summary>
    public struct GridPosition : IEquatable<GridPosition>
    {
        public PrecisionCoordinate Coord { get; }

        public GridPosition(PrecisionCoordinate coord)
        {
            Coord = coord;
        }

        public static GridPosition FromInt(int x, int y) => new GridPosition(PrecisionCoordinate.FromInt(x, y));
        public static GridPosition FromFloat(float x, float y) => new GridPosition(PrecisionCoordinate.FromFloat(x, y));

        public (int, int) ToInt() => Coord.ToInt();
        public (float, float) ToFloat() => Coord.ToFloat();

        public override bool Equals(object obj) => obj is GridPosition gp && Equals(gp);
        public bool Equals(GridPosition other) => Coord.Equals(other.Coord);
        public override int GetHashCode() => Coord.GetHashCode();
        public override string ToString() => Coord.ToString();
    }
} 