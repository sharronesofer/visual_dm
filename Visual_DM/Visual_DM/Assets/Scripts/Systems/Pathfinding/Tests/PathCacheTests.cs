using NUnit.Framework;
using System.Collections.Generic;

namespace VisualDM.Systems.Pathfinding.Tests
{
    public class PathCacheTests
    {
        [Test]
        public void TestAddAndGetPath()
        {
            var cache = new PathCache();
            var start = new GridPosition(0, 0);
            var end = new GridPosition(1, 1);
            var path = new List<PathNode> { new PathNode(start), new PathNode(end) };
            cache.Add(start, end, "AStar", path);
            var cached = cache.Get(start, end, "AStar");
            Assert.IsNotNull(cached);
            Assert.AreEqual(2, cached.Count);
        }

        [Test]
        public void TestClearCache()
        {
            var cache = new PathCache();
            cache.Add(new GridPosition(0,0), new GridPosition(1,1), "AStar", new List<PathNode>());
            cache.Clear();
            Assert.IsNull(cache.Get(new GridPosition(0,0), new GridPosition(1,1), "AStar"));
        }
    }
} 