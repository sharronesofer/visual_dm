using System;
using System.Collections.Generic;

namespace VisualDM.Systems.Pathfinding
{
    /// <summary>
    /// Manages dynamic obstacles and triggers path recalculation when obstacles change.
    /// </summary>
    public class DynamicObstacleManager
    {
        public event Action OnObstaclesChanged;
        private HashSet<GridPosition> dynamicObstacles = new HashSet<GridPosition>();

        /// <summary>
        /// Adds a dynamic obstacle and triggers recalculation.
        /// </summary>
        public void AddObstacle(GridPosition pos)
        {
            if (dynamicObstacles.Add(pos))
                OnObstaclesChanged?.Invoke();
        }

        /// <summary>
        /// Removes a dynamic obstacle and triggers recalculation.
        /// </summary>
        public void RemoveObstacle(GridPosition pos)
        {
            if (dynamicObstacles.Remove(pos))
                OnObstaclesChanged?.Invoke();
        }

        /// <summary>
        /// Checks if a position is currently blocked by a dynamic obstacle.
        /// </summary>
        public bool IsBlocked(GridPosition pos)
        {
            return dynamicObstacles.Contains(pos);
        }

        /// <summary>
        /// Clears all dynamic obstacles.
        /// </summary>
        public void Clear()
        {
            dynamicObstacles.Clear();
            OnObstaclesChanged?.Invoke();
        }
    }
} 