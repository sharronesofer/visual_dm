using System;

namespace VisualDM.Core
{
    /// <summary>
    /// High-precision 2D coordinate using fixed-point arithmetic.
    /// </summary>
    public struct PrecisionCoordinate : IEquatable<PrecisionCoordinate>
    {
        public FixedPoint X { get; }
        public FixedPoint Y { get; }

        public PrecisionCoordinate(FixedPoint x, FixedPoint y)
        {
            X = x;
            Y = y;
        }

        public static PrecisionCoordinate FromFloat(float x, float y) => new PrecisionCoordinate(FixedPoint.FromFloat(x), FixedPoint.FromFloat(y));
        public static PrecisionCoordinate FromInt(int x, int y) => new PrecisionCoordinate(FixedPoint.FromInt(x), FixedPoint.FromInt(y));

        public (float, float) ToFloat() => (X.ToFloat(), Y.ToFloat());
        public (int, int) ToInt() => (X.ToInt(), Y.ToInt());

        // Normalization (example: wrap to map bounds)
        public PrecisionCoordinate Normalize(int mapWidth, int mapHeight)
        {
            int normX = ((X.ToInt() % mapWidth) + mapWidth) % mapWidth;
            int normY = ((Y.ToInt() % mapHeight) + mapHeight) % mapHeight;
            return FromInt(normX, normY);
        }

        // Precision-loss detection (warn if fractional part is nonzero after conversion)
        public bool HasPrecisionLoss(float epsilon = 1e-5f)
        {
            float fx = X.ToFloat();
            float fy = Y.ToFloat();
            return Math.Abs(fx - (float)Math.Round(fx)) > epsilon || Math.Abs(fy - (float)Math.Round(fy)) > epsilon;
        }

        public override bool Equals(object obj) => obj is PrecisionCoordinate pc && Equals(pc);
        public bool Equals(PrecisionCoordinate other) => X == other.X && Y == other.Y;
        public override int GetHashCode() => (X, Y).GetHashCode();
        public override string ToString() => $"({X}, {Y})";
    }
} 