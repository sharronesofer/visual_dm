using System;

namespace VisualDM.Core
{
    /// <summary>
    /// Fixed-point number struct (16.16 format) for high-precision coordinate calculations.
    /// </summary>
    public struct FixedPoint : IComparable<FixedPoint>, IEquatable<FixedPoint>
    {
        private const int FRACTIONAL_BITS = 16;
        private const int FRACTIONAL_MASK = (1 << FRACTIONAL_BITS) - 1;
        private const int INTEGER_MASK = ~FRACTIONAL_MASK;
        private const int ONE = 1 << FRACTIONAL_BITS;
        private readonly int rawValue;

        public static readonly FixedPoint Zero = new FixedPoint(0);
        public static readonly FixedPoint OneFP = new FixedPoint(ONE);

        public FixedPoint(int rawValue)
        {
            this.rawValue = rawValue;
        }

        public static FixedPoint FromInt(int value) => new FixedPoint(value << FRACTIONAL_BITS);
        public static FixedPoint FromFloat(float value) => new FixedPoint((int)(value * ONE));
        public static FixedPoint FromDouble(double value) => new FixedPoint((int)(value * ONE));
        public int ToInt() => rawValue >> FRACTIONAL_BITS;
        public float ToFloat() => rawValue / (float)ONE;
        public double ToDouble() => rawValue / (double)ONE;

        // Arithmetic operators
        public static FixedPoint operator +(FixedPoint a, FixedPoint b) => new FixedPoint(a.rawValue + b.rawValue);
        public static FixedPoint operator -(FixedPoint a, FixedPoint b) => new FixedPoint(a.rawValue - b.rawValue);
        public static FixedPoint operator *(FixedPoint a, FixedPoint b) => new FixedPoint((int)(((long)a.rawValue * b.rawValue) >> FRACTIONAL_BITS));
        public static FixedPoint operator /(FixedPoint a, FixedPoint b)
        {
            if (b.rawValue == 0) throw new DivideByZeroException();
            return new FixedPoint((int)(((long)a.rawValue << FRACTIONAL_BITS) / b.rawValue));
        }
        public static bool operator ==(FixedPoint a, FixedPoint b) => a.rawValue == b.rawValue;
        public static bool operator !=(FixedPoint a, FixedPoint b) => a.rawValue != b.rawValue;
        public static bool operator <(FixedPoint a, FixedPoint b) => a.rawValue < b.rawValue;
        public static bool operator >(FixedPoint a, FixedPoint b) => a.rawValue > b.rawValue;
        public static bool operator <=(FixedPoint a, FixedPoint b) => a.rawValue <= b.rawValue;
        public static bool operator >=(FixedPoint a, FixedPoint b) => a.rawValue >= b.rawValue;

        public override bool Equals(object obj) => obj is FixedPoint fp && this == fp;
        public bool Equals(FixedPoint other) => this == other;
        public override int GetHashCode() => rawValue.GetHashCode();
        public int CompareTo(FixedPoint other) => rawValue.CompareTo(other.rawValue);
        public override string ToString() => ToFloat().ToString("F5");
    }
} 