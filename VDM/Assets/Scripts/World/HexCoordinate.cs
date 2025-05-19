using System;
using UnityEngine;

namespace VisualDM.World
{
    /// <summary>
    /// Represents a hexagonal coordinate in cubic (x, y, z) form for both region and POI scales.
    /// </summary>
    public struct HexCoordinate : IEquatable<HexCoordinate>
    {
        public readonly int X;
        public readonly int Y;
        public readonly int Z;

        public HexCoordinate(int x, int y, int z)
        {
            if (x + y + z != 0)
                throw new ArgumentException("Hex coordinates must sum to zero (x + y + z = 0)");
            X = x;
            Y = y;
            Z = z;
        }

        public static HexCoordinate FromAxial(int q, int r) => new HexCoordinate(q, -q - r, r);
        public (int q, int r) ToAxial() => (X, Z);

        public int Distance(HexCoordinate other)
            => (Math.Abs(X - other.X) + Math.Abs(Y - other.Y) + Math.Abs(Z - other.Z)) / 2;

        public HexCoordinate Neighbor(int direction)
        {
            // Directions: 0=E, 1=NE, 2=NW, 3=W, 4=SW, 5=SE
            var directions = new[] {
                new HexCoordinate(1, -1, 0), new HexCoordinate(1, 0, -1), new HexCoordinate(0, 1, -1),
                new HexCoordinate(-1, 1, 0), new HexCoordinate(-1, 0, 1), new HexCoordinate(0, -1, 1)
            };
            return new HexCoordinate(X + directions[direction].X, Y + directions[direction].Y, Z + directions[direction].Z);
        }

        public override bool Equals(object obj) => obj is HexCoordinate hc && Equals(hc);
        public bool Equals(HexCoordinate other) => X == other.X && Y == other.Y && Z == other.Z;
        public override int GetHashCode() => (X, Y, Z).GetHashCode();
        public override string ToString() => $"({X}, {Y}, {Z})";
    }
}