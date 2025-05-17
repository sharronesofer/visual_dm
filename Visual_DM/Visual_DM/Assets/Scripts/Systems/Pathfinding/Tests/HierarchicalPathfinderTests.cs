using NUnit.Framework;
using System.Threading.Tasks;

namespace VisualDM.Systems.Pathfinding.Tests
{
    public class HierarchicalPathfinderTests
    {
        [Test]
        public async Task TestFindPathAsync_ReturnsPath()
        {
            var pathfinder = new HierarchicalPathfinder();
            var start = new GridPosition(0, 0);
            var end = new GridPosition(10, 10);
            var path = await pathfinder.FindPathAsync(start, end);
            Assert.IsNotNull(path);
        }
    }
} 