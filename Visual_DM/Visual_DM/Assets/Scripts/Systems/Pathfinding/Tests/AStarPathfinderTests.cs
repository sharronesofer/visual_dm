using NUnit.Framework;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace VisualDM.Systems.Pathfinding.Tests
{
    public class AStarPathfinderTests
    {
        [Test]
        public async Task TestFindPathAsync_ReturnsPath()
        {
            var pathfinder = new AStarPathfinder();
            var start = new GridPosition(0, 0);
            var end = new GridPosition(3, 3);
            var path = await pathfinder.FindPathAsync(start, end);
            Assert.IsNotNull(path);
        }
    }
} 