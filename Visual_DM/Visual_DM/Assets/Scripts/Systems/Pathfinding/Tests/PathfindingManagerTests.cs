using NUnit.Framework;
using System.Threading.Tasks;
using System.Collections.Generic;
using VisualDM.Grid;

namespace VisualDM.Systems.Pathfinding.Tests
{
    public class PathfindingManagerTests
    {
        [SetUp]
        public void Setup()
        {
            // Setup a minimal grid for testing
            var grid = new DynamicGrid(4);
            // Assume singleton assignment for test
            Grid.DynamicGridInstance = grid;
            var chunkManager = new ChunkManager(4);
            grid.ChunkManager = chunkManager;
            var chunk = new GridChunk(new UnityEngine.Vector2Int(0, 0), 4);
            for (int x = 0; x < 4; x++)
                for (int y = 0; y < 4; y++)
                    chunk[x, y] = new HexCell(CellType.Floor, true);
            // Make (1,1) not walkable
            chunk[1, 1] = new HexCell(CellType.Wall, false);
            chunkManager.GetOrLoadChunk(new UnityEngine.Vector2(0, 0)); // Ensure chunk is loaded
            chunkManager.loadedChunks[new UnityEngine.Vector2Int(0, 0)] = chunk;
        }

        [Test]
        public async Task TestRequestPathAsync_ReturnsPath()
        {
            var manager = new PathfindingManager();
            var start = new GridPosition(0, 0);
            var end = new GridPosition(5, 5);
            var path = await manager.RequestPathAsync(start, end);
            Assert.IsNotNull(path);
        }

        [Test]
        public void TestClearCache()
        {
            var manager = new PathfindingManager();
            manager.ClearCache();
            Assert.Pass();
        }

        [Test]
        public void TestIsWalkable_WalkableAndBlocked()
        {
            var walkable = PathfindingManager.IsWalkable(GridPosition.FromInt(0, 0));
            var blocked = PathfindingManager.IsWalkable(GridPosition.FromInt(1, 1));
            Assert.IsTrue(walkable);
            Assert.IsFalse(blocked);
        }

        [Test]
        public void TestGetWalkableNeighbors_OnlyReturnsWalkable()
        {
            var pos = GridPosition.FromInt(1, 0);
            var neighbors = PathfindingManager.GetWalkableNeighbors(pos);
            // (1,1) is blocked, so should not be in neighbors
            foreach (var n in neighbors)
                Assert.AreNotEqual(GridPosition.FromInt(1, 1), n);
        }
    }
} 