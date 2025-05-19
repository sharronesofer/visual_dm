using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace VisualDM.World
{
    /// <summary>
    /// Implementation of the A* pathfinding algorithm for grid-based navigation.
    /// Supports advanced features such as caching, terrain costs, and group movement.
    /// </summary>
    public class PathfindingSystem : IPathfindingSystem
    {
        private readonly GridManager gridManager;
        private readonly Dictionary<string, PathCache> pathCache = new Dictionary<string, PathCache>();
        private readonly Dictionary<string, CategoryPathRules> categoryRules = new Dictionary<string, CategoryPathRules>();
        private readonly float cacheDuration = 5.0f; // 5 seconds
        private readonly int predictiveLookahead = 3;
        
        // Default POI category for pathfinding
        public const string DefaultCategory = "default";
        
        /// <summary>
        /// Initializes a new instance of the PathfindingSystem
        /// </summary>
        /// <param name="gridManager">Grid manager that provides the navigable grid</param>
        public PathfindingSystem(GridManager gridManager)
        {
            this.gridManager = gridManager;
            InitializeDefaultCategoryRules();
        }

        /// <summary>
        /// Sets up default category rules for different types of entities
        /// </summary>
        private void InitializeDefaultCategoryRules()
        {
            // Default rules for general navigation
            categoryRules[DefaultCategory] = new CategoryPathRules(
                new List<CellType> { CellType.ROAD, CellType.EMPTY },
                new List<CellType> { CellType.WALL, CellType.BLOCKED },
                1.0f
            );
            
            // Rules for social NPCs (prefer roads, avoid rough terrain)
            categoryRules["social"] = new CategoryPathRules(
                new List<CellType> { CellType.ROAD, CellType.EMPTY },
                new List<CellType> { CellType.WALL, CellType.BLOCKED, CellType.ROUGH },
                1.0f
            );
            
            // Rules for dungeon creatures (prefer non-road areas)
            categoryRules["dungeon"] = new CategoryPathRules(
                new List<CellType> { CellType.EMPTY },
                new List<CellType> { CellType.ROAD },
                1.5f
            );
            
            // Rules for explorers
            categoryRules["exploration"] = new CategoryPathRules(
                new List<CellType> { CellType.EMPTY, CellType.ROAD },
                new List<CellType> { CellType.BLOCKED },
                0.8f
            );
        }

        /// <summary>
        /// Finds a path between two points using A* algorithm.
        /// </summary>
        /// <param name="start">Starting position</param>
        /// <param name="end">Target position</param>
        /// <param name="characterId">Optional character ID for collision checks</param>
        /// <param name="predictiveAvoidance">Whether to use predictive avoidance</param>
        /// <returns>List of positions forming the path, or empty list if no path found</returns>
        public List<GridPosition> FindPath(GridPosition start, GridPosition end, string characterId = null, bool predictiveAvoidance = false)
        {
            return FindPathWithCategory(start, end, DefaultCategory, characterId, predictiveAvoidance);
        }

        /// <summary>
        /// Finds a path with specific category rules.
        /// </summary>
        /// <param name="start">Starting position</param>
        /// <param name="end">Target position</param>
        /// <param name="category">Category for pathfinding rules</param>
        /// <param name="characterId">Optional character ID for collision checks</param>
        /// <param name="predictiveAvoidance">Whether to use predictive avoidance</param>
        /// <returns>List of positions forming the path, or empty list if no path found</returns>
        public List<GridPosition> FindPathWithCategory(GridPosition start, GridPosition end, string category, string characterId = null, bool predictiveAvoidance = false)
        {
            // Check if the target is valid
            if (!gridManager.IsValidPosition(start) || !gridManager.IsValidPosition(end))
            {
                return new List<GridPosition>();
            }

            // Try cache first
            string cacheKey = GetCacheKey(start, end, category);
            if (pathCache.TryGetValue(cacheKey, out PathCache cachedPath))
            {
                if (Time.time - cachedPath.timestamp < cacheDuration)
                {
                    return new List<GridPosition>(cachedPath.path);
                }
            }

            // Initialize A* algorithm
            var openSet = new List<PathfindingNode>();
            var closedSet = new HashSet<string>();

            var startNode = new PathfindingNode(start, 0, CalculateHeuristic(start, end, category));
            openSet.Add(startNode);

            while (openSet.Count > 0)
            {
                // Get node with lowest F cost
                var currentNode = GetLowestFCostNode(openSet);
                
                // Check if we've reached the destination
                if (currentNode.position.x == end.x && currentNode.position.y == end.y)
                {
                    var path = ReconstructPath(currentNode);
                    
                    // Cache the result
                    pathCache[cacheKey] = new PathCache(path, Time.time, category);
                    return path;
                }

                // Move to closed set
                openSet.Remove(currentNode);
                closedSet.Add(PositionToString(currentNode.position));

                // Process neighbors
                var neighbors = GetWalkableNeighbors(currentNode.position, characterId, category);
                foreach (var neighbor in neighbors)
                {
                    if (closedSet.Contains(PositionToString(neighbor)))
                    {
                        continue;
                    }

                    // Calculate new cost
                    float newGCost = currentNode.gCost + CalculateMovementCost(currentNode.position, neighbor, category);
                    
                    // Add predictive avoidance cost if enabled
                    if (predictiveAvoidance)
                    {
                        newGCost += CalculatePredictiveCollisionCost(neighbor);
                    }

                    // Find if this neighbor is already in the open set
                    var neighborNode = openSet.FirstOrDefault(n => n.position.x == neighbor.x && n.position.y == neighbor.y);
                    
                    if (neighborNode == null)
                    {
                        // Add new node to open set
                        openSet.Add(new PathfindingNode(
                            neighbor,
                            newGCost,
                            CalculateHeuristic(neighbor, end, category),
                            currentNode
                        ));
                    }
                    else if (newGCost < neighborNode.gCost)
                    {
                        // Update existing node with better path
                        neighborNode.gCost = newGCost;
                        neighborNode.parent = currentNode;
                    }
                }
            }

            // No path found
            return new List<GridPosition>();
        }

        /// <summary>
        /// Finds a path suitable for group movement.
        /// </summary>
        /// <param name="start">Starting position</param>
        /// <param name="end">Target position</param>
        /// <param name="options">Group movement options</param>
        /// <param name="characterId">Optional character ID</param>
        /// <returns>List of positions forming the path, or empty list if no path found</returns>
        public List<GridPosition> FindGroupPath(GridPosition start, GridPosition end, GroupPathfindingOptions options, string characterId = null)
        {
            // Calculate group dimensions
            int groupWidth = options.formationWidth * options.formationSpacing;
            int groupHeight = Mathf.CeilToInt((float)options.groupSize / options.formationWidth) * options.formationSpacing;

            // Try cache first
            string cacheKey = $"group:{start.x},{start.y}:{end.x},{end.y}:{options.groupSize}";
            if (pathCache.TryGetValue(cacheKey, out PathCache cachedPath))
            {
                if (Time.time - cachedPath.timestamp < cacheDuration)
                {
                    return new List<GridPosition>(cachedPath.path);
                }
            }

            // Initialize A* algorithm with special group-specific costs
            var openSet = new List<PathfindingNode>();
            var closedSet = new HashSet<string>();

            var startNode = new PathfindingNode(start, 0, CalculateHeuristic(start, end));
            openSet.Add(startNode);

            while (openSet.Count > 0)
            {
                // Get node with lowest F cost
                var currentNode = GetLowestFCostNode(openSet);
                
                // Check if we've reached the destination
                if (currentNode.position.x == end.x && currentNode.position.y == end.y)
                {
                    var path = ReconstructPath(currentNode);
                    
                    // Cache the result
                    pathCache[cacheKey] = new PathCache(path, Time.time);
                    return path;
                }

                // Move to closed set
                openSet.Remove(currentNode);
                closedSet.Add(PositionToString(currentNode.position));

                // Process neighbors
                var neighbors = GetWalkableNeighbors(currentNode.position, characterId);
                foreach (var neighbor in neighbors)
                {
                    if (closedSet.Contains(PositionToString(neighbor)))
                    {
                        continue;
                    }

                    // Calculate new cost with group-specific factors
                    float newGCost = currentNode.gCost + CalculateGroupMovementCost(
                        currentNode.position, 
                        neighbor, 
                        options.groupSize,
                        groupWidth,
                        groupHeight
                    );
                    
                    // Add predictive avoidance cost if enabled
                    if (options.predictiveAvoidance)
                    {
                        newGCost += CalculatePredictiveCollisionCost(neighbor);
                    }

                    // Find if this neighbor is already in the open set
                    var neighborNode = openSet.FirstOrDefault(n => n.position.x == neighbor.x && n.position.y == neighbor.y);
                    
                    if (neighborNode == null)
                    {
                        // Add new node to open set
                        openSet.Add(new PathfindingNode(
                            neighbor,
                            newGCost,
                            CalculateHeuristic(neighbor, end),
                            currentNode
                        ));
                    }
                    else if (newGCost < neighborNode.gCost)
                    {
                        // Update existing node with better path
                        neighborNode.gCost = newGCost;
                        neighborNode.parent = currentNode;
                    }
                }
            }

            // No path found
            return new List<GridPosition>();
        }

        /// <summary>
        /// Checks if a path is possible between two points.
        /// </summary>
        /// <param name="start">Starting position</param>
        /// <param name="end">Target position</param>
        /// <returns>True if a path exists, false otherwise</returns>
        public bool IsPathPossible(GridPosition start, GridPosition end)
        {
            // A simplified version of A* that just checks if a path exists without constructing it
            if (!gridManager.IsValidPosition(start) || !gridManager.IsValidPosition(end))
            {
                return false;
            }

            var openSet = new List<PathfindingNode>();
            var closedSet = new HashSet<string>();

            var startNode = new PathfindingNode(start, 0, CalculateHeuristic(start, end));
            openSet.Add(startNode);

            while (openSet.Count > 0)
            {
                // Get node with lowest F cost
                var currentNode = GetLowestFCostNode(openSet);
                
                // Check if we've reached the destination
                if (currentNode.position.x == end.x && currentNode.position.y == end.y)
                {
                    return true;
                }

                // Move to closed set
                openSet.Remove(currentNode);
                closedSet.Add(PositionToString(currentNode.position));

                // Process neighbors
                var neighbors = GetWalkableNeighbors(currentNode.position);
                foreach (var neighbor in neighbors)
                {
                    if (closedSet.Contains(PositionToString(neighbor)))
                    {
                        continue;
                    }

                    // Calculate new cost (simplified)
                    float newGCost = currentNode.gCost + 1;

                    // Find if this neighbor is already in the open set
                    var neighborNode = openSet.FirstOrDefault(n => n.position.x == neighbor.x && n.position.y == neighbor.y);
                    
                    if (neighborNode == null)
                    {
                        // Add new node to open set
                        openSet.Add(new PathfindingNode(
                            neighbor,
                            newGCost,
                            CalculateHeuristic(neighbor, end),
                            currentNode
                        ));
                    }
                    else if (newGCost < neighborNode.gCost)
                    {
                        // Update existing node with better path
                        neighborNode.gCost = newGCost;
                        neighborNode.parent = currentNode;
                    }
                }
            }

            // No path found
            return false;
        }

        /// <summary>
        /// Finds all accessible positions within a certain distance.
        /// </summary>
        /// <param name="start">Starting position</param>
        /// <param name="maxDistance">Maximum distance to search</param>
        /// <returns>Set of accessible position strings</returns>
        public HashSet<string> FindAccessibleArea(GridPosition start, int maxDistance)
        {
            if (!gridManager.IsValidPosition(start))
            {
                return new HashSet<string>();
            }

            var result = new HashSet<string>();
            var openSet = new List<PathfindingNode>();
            var closedSet = new HashSet<string>();

            var startNode = new PathfindingNode(start, 0, 0);
            openSet.Add(startNode);
            
            while (openSet.Count > 0)
            {
                var currentNode = openSet[0]; // Distance-based BFS
                openSet.RemoveAt(0);
                
                string posStr = PositionToString(currentNode.position);
                if (closedSet.Contains(posStr))
                {
                    continue;
                }
                
                closedSet.Add(posStr);
                result.Add(posStr);
                
                // Stop if we've reached the maximum distance
                if (currentNode.gCost >= maxDistance)
                {
                    continue;
                }
                
                // Check all neighboring cells
                var neighbors = GetWalkableNeighbors(currentNode.position);
                foreach (var neighbor in neighbors)
                {
                    if (!closedSet.Contains(PositionToString(neighbor)))
                    {
                        openSet.Add(new PathfindingNode(
                            neighbor,
                            currentNode.gCost + 1,
                            0,
                            currentNode
                        ));
                    }
                }
            }
            
            return result;
        }

        /// <summary>
        /// Invalidates cached paths that pass through a certain position.
        /// </summary>
        /// <param name="position">Position that has changed</param>
        /// <param name="radius">Radius around the position to invalidate</param>
        public void InvalidateCache(GridPosition position, int radius = 1)
        {
            var keysToRemove = new List<string>();
            
            foreach (var entry in pathCache)
            {
                bool affected = entry.Value.path.Any(pos => 
                    Math.Abs(pos.x - position.x) <= radius && 
                    Math.Abs(pos.y - position.y) <= radius
                );
                
                if (affected)
                {
                    keysToRemove.Add(entry.Key);
                }
            }
            
            foreach (var key in keysToRemove)
            {
                pathCache.Remove(key);
            }
        }

        /// <summary>
        /// Gets the walkable neighboring positions of a position.
        /// </summary>
        /// <param name="position">Central position</param>
        /// <param name="characterId">Optional character ID for special checks</param>
        /// <param name="category">Optional POI category for special rules</param>
        /// <returns>List of walkable neighboring positions</returns>
        private List<GridPosition> GetWalkableNeighbors(GridPosition position, string characterId = null, string category = null)
        {
            var neighbors = new List<GridPosition>();
            
            // Check all 8 neighboring cells
            for (int xOffset = -1; xOffset <= 1; xOffset++)
            {
                for (int yOffset = -1; yOffset <= 1; yOffset++)
                {
                    // Skip the center cell
                    if (xOffset == 0 && yOffset == 0)
                    {
                        continue;
                    }
                    
                    GridPosition neighborPos = new GridPosition(position.x + xOffset, position.y + yOffset);
                    
                    // Check if position is valid and walkable
                    if (IsWalkable(neighborPos, characterId))
                    {
                        // For diagonal movement, check that the path isn't blocked by obstacles
                        if (xOffset != 0 && yOffset != 0)
                        {
                            // Check that we can move through the corners
                            if (!IsWalkable(new GridPosition(position.x + xOffset, position.y), characterId) &&
                                !IsWalkable(new GridPosition(position.x, position.y + yOffset), characterId))
                            {
                                continue;
                            }
                        }
                        
                        neighbors.Add(neighborPos);
                    }
                }
            }
            
            return neighbors;
        }

        /// <summary>
        /// Checks if a position is walkable (valid and not blocked).
        /// </summary>
        /// <param name="position">Position to check</param>
        /// <param name="characterId">Optional character ID for special checks</param>
        /// <returns>True if the position is walkable</returns>
        private bool IsWalkable(GridPosition position, string characterId = null)
        {
            if (!gridManager.IsValidPosition(position))
            {
                return false;
            }
            
            GridCell cell = gridManager.GetCellAt(position);
            
            // Check basic walkability
            if (cell == null || !cell.walkable)
            {
                return false;
            }
            
            // Skip cells occupied by other entities
            if (cell.isOccupied && cell.occupiedBy != characterId)
            {
                return false;
            }
            
            // Check for building, room, and door access
            // This is a placeholder for more complex logic that could be implemented
            // based on the specific character ID
            if (cell.buildingId != null || cell.roomId != null || cell.doorId != null)
            {
                // For now, assume all buildings/rooms/doors are accessible
                return true;
            }
            
            return true;
        }

        /// <summary>
        /// Calculates the cost to move from one position to another.
        /// </summary>
        /// <param name="from">Starting position</param>
        /// <param name="to">Target position</param>
        /// <param name="category">Optional POI category for special rules</param>
        /// <returns>Cost of movement</returns>
        private float CalculateMovementCost(GridPosition from, GridPosition to, string category = null)
        {
            // Base movement cost (1 for orthogonal, sqrt(2) for diagonal)
            float baseCost = (from.x == to.x || from.y == to.y) ? 1.0f : 1.414f; // sqrt(2)
            
            // Apply terrain cost modifier
            GridCell cell = gridManager.GetCellAt(to);
            if (cell == null)
            {
                return float.MaxValue; // Unwalkable
            }
            
            // Get category rules (use default if not found)
            CategoryPathRules rules = categoryRules.TryGetValue(category ?? DefaultCategory, out var r) 
                ? r 
                : categoryRules[DefaultCategory];
            
            // Apply terrain type modifiers
            if (rules.preferredTypes.Contains(cell.cellType))
            {
                baseCost *= 0.8f; // Preferred terrain is faster
            }
            else if (rules.avoidTypes.Contains(cell.cellType))
            {
                baseCost *= 2.0f; // Avoided terrain is slower
            }
            
            // Additional terrain-specific costs
            switch (cell.cellType)
            {
                case CellType.ROUGH:
                    baseCost += 1.0f;
                    break;
                case CellType.WATER:
                    baseCost += 2.0f;
                    break;
                case CellType.FOREST:
                    baseCost += 0.5f;
                    break;
            }
            
            // Apply category weight multiplier
            baseCost *= rules.weightMultiplier;
            
            return baseCost;
        }

        /// <summary>
        /// Calculates the cost for group movement between positions.
        /// </summary>
        /// <param name="from">Starting position</param>
        /// <param name="to">Target position</param>
        /// <param name="groupSize">Size of the group</param>
        /// <param name="groupWidth">Width of the group formation</param>
        /// <param name="groupHeight">Height of the group formation</param>
        /// <returns>Movement cost for the group</returns>
        private float CalculateGroupMovementCost(GridPosition from, GridPosition to, int groupSize, int groupWidth, int groupHeight)
        {
            // Base cost same as individual movement
            float baseCost = CalculateMovementCost(from, to);
            
            // Additional cost based on group size and formation
            float groupCost = 0;
            
            // Check if the entire group formation can fit at the target position
            int formationBlockages = 0;
            for (int xOffset = 0; xOffset < groupWidth; xOffset++)
            {
                for (int yOffset = 0; yOffset < groupHeight; yOffset++)
                {
                    GridPosition formationPos = new GridPosition(to.x + xOffset, to.y + yOffset);
                    
                    // Count non-walkable positions in the formation
                    if (!IsWalkable(formationPos))
                    {
                        formationBlockages++;
                    }
                }
            }
            
            // Add cost based on how many positions in the formation are blocked
            groupCost += formationBlockages * 2.0f;
            
            // Larger groups are penalized more for restricted spaces
            return baseCost + groupCost * Mathf.Sqrt(groupSize);
        }

        /// <summary>
        /// Calculates a predictive collision cost for a position.
        /// </summary>
        /// <param name="position">Position to evaluate</param>
        /// <returns>Collision cost</returns>
        private float CalculatePredictiveCollisionCost(GridPosition position)
        {
            // This is a placeholder for more complex logic that could be implemented
            // It would analyze the potential for collision with moving entities
            
            // Simple placeholder implementation
            float cost = 0;
            
            // Check if adjacent cells are occupied
            for (int xOffset = -1; xOffset <= 1; xOffset++)
            {
                for (int yOffset = -1; yOffset <= 1; yOffset++)
                {
                    // Skip the center
                    if (xOffset == 0 && yOffset == 0)
                    {
                        continue;
                    }
                    
                    GridPosition neighborPos = new GridPosition(position.x + xOffset, position.y + yOffset);
                    GridCell cell = gridManager.GetCellAt(neighborPos);
                    
                    if (cell != null && cell.isOccupied)
                    {
                        cost += 0.5f; // Small cost for occupied neighbors
                    }
                }
            }
            
            return cost;
        }

        /// <summary>
        /// Calculates the heuristic cost (estimate to goal).
        /// </summary>
        /// <param name="from">Starting position</param>
        /// <param name="to">Target position</param>
        /// <param name="category">Optional POI category</param>
        /// <returns>Heuristic cost</returns>
        private float CalculateHeuristic(GridPosition from, GridPosition to, string category = null)
        {
            // Manhattan distance for 4-way movement
            // float dx = Mathf.Abs(from.x - to.x);
            // float dy = Mathf.Abs(from.y - to.y);
            // return dx + dy;
            
            // Diagonal distance for 8-way movement
            float dx = Mathf.Abs(from.x - to.x);
            float dy = Mathf.Abs(from.y - to.y);
            return Mathf.Max(dx, dy) + 0.414f * Mathf.Min(dx, dy); // D + (D2-D)*0.414
        }

        /// <summary>
        /// Gets the lowest F cost node from a list of nodes.
        /// </summary>
        /// <param name="nodes">List of nodes</param>
        /// <returns>Node with lowest F cost</returns>
        private PathfindingNode GetLowestFCostNode(List<PathfindingNode> nodes)
        {
            var lowestCostNode = nodes[0];
            
            for (int i = 1; i < nodes.Count; i++)
            {
                var node = nodes[i];
                
                // Choose the node with lowest F cost, or if F costs are equal, the one with lowest H cost
                if (node.fCost < lowestCostNode.fCost || 
                    (node.fCost == lowestCostNode.fCost && node.hCost < lowestCostNode.hCost))
                {
                    lowestCostNode = node;
                }
            }
            
            return lowestCostNode;
        }

        /// <summary>
        /// Reconstructs a path from end node to start node.
        /// </summary>
        /// <param name="endNode">End node with parent chain</param>
        /// <returns>List of positions from start to end</returns>
        private List<GridPosition> ReconstructPath(PathfindingNode endNode)
        {
            var path = new List<GridPosition>();
            
            // Follow parent links from end to start
            var currentNode = endNode;
            while (currentNode != null)
            {
                path.Add(currentNode.position);
                currentNode = currentNode.parent;
            }
            
            // Reverse to get path from start to end
            path.Reverse();
            return path;
        }

        /// <summary>
        /// Converts a position to a string for use in sets and dictionaries.
        /// </summary>
        /// <param name="position">Grid position</param>
        /// <returns>String representation</returns>
        private string PositionToString(GridPosition position)
        {
            return $"{position.x},{position.y}";
        }

        /// <summary>
        /// Gets a cache key for a start-end pair and optional category.
        /// </summary>
        /// <param name="start">Start position</param>
        /// <param name="end">End position</param>
        /// <param name="category">Optional category</param>
        /// <returns>Cache key string</returns>
        private string GetCacheKey(GridPosition start, GridPosition end, string category = null)
        {
            return category == null || category == DefaultCategory
                ? $"{start.x},{start.y}:{end.x},{end.y}"
                : $"{start.x},{start.y}:{end.x},{end.y}:{category}";
        }
    }
} 