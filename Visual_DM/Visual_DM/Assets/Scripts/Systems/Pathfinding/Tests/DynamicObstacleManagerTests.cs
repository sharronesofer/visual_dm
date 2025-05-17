using NUnit.Framework;

namespace VisualDM.Systems.Pathfinding.Tests
{
    public class DynamicObstacleManagerTests
    {
        [Test]
        public void TestAddAndRemoveObstacle()
        {
            var manager = new DynamicObstacleManager();
            var pos = new GridPosition(2, 2);
            manager.AddObstacle(pos);
            Assert.IsTrue(manager.IsBlocked(pos));
            manager.RemoveObstacle(pos);
            Assert.IsFalse(manager.IsBlocked(pos));
        }

        [Test]
        public void TestClearObstacles()
        {
            var manager = new DynamicObstacleManager();
            manager.AddObstacle(new GridPosition(1, 1));
            manager.Clear();
            Assert.IsFalse(manager.IsBlocked(new GridPosition(1, 1)));
        }
    }
} 