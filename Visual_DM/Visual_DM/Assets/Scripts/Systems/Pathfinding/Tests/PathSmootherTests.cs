using NUnit.Framework;
using System.Collections.Generic;

namespace VisualDM.Systems.Pathfinding.Tests
{
    public class PathSmootherTests
    {
        [Test]
        public void TestBezierSmooth_ReturnsPath()
        {
            var path = new List<GridPosition> { new GridPosition(0,0), new GridPosition(1,1), new GridPosition(2,2) };
            var smoothed = PathSmoother.BezierSmooth(path);
            Assert.IsNotNull(smoothed);
        }

        [Test]
        public void TestStringPull_ReturnsPath()
        {
            var path = new List<GridPosition> { new GridPosition(0,0), new GridPosition(1,1), new GridPosition(2,2) };
            var smoothed = PathSmoother.StringPull(path);
            Assert.IsNotNull(smoothed);
        }

        [Test]
        public void TestAngleSmooth_ReturnsPath()
        {
            var path = new List<GridPosition> { new GridPosition(0,0), new GridPosition(1,1), new GridPosition(2,2) };
            var smoothed = PathSmoother.AngleSmooth(path);
            Assert.IsNotNull(smoothed);
        }
    }
} 