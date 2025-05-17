using NUnit.Framework;
using System.Threading.Tasks;

namespace VisualDM.Systems.Pathfinding.Tests
{
    public class JPSPathfinderTests
    {
        [Test]
        public async Task TestFindPathAsync_ReturnsPath()
        {
            var pathfinder = new JPSPathfinder();
            var start = new GridPosition(0, 0);
            var end = new GridPosition(3, 3);
            var path = await pathfinder.FindPathAsync(start, end);
            Assert.IsNotNull(path);
        }
    }
} 