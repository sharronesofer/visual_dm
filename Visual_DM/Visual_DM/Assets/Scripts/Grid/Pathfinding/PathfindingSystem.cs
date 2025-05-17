using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Systems.Pathfinding;

public class PathfindingSystem : MonoBehaviour
{
    private readonly FixedPoint cacheDuration = FixedPoint.FromFloat(5.0f); // 5 seconds

    public List<GridPosition> FindPath(GridPosition start, GridPosition end, string characterId = null, bool predictiveAvoidance = false)
    {
        return FindPathWithCategory(start, end, DefaultCategory, characterId, predictiveAvoidance);
    }

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
            if (FixedPoint.FromFloat(Time.time) - cachedPath.timestamp < cacheDuration)
            {
                return new List<GridPosition>(cachedPath.path);
            }
        }

        // Initialize A* algorithm
        var openSet = new List<PathfindingNode>();
        var closedSet = new HashSet<string>();

        var startNode = new PathfindingNode(start, FixedPoint.Zero, CalculateHeuristic(start, end, category));
        openSet.Add(startNode);

        while (openSet.Count > 0)
        {
            // Get node with lowest F cost
            var currentNode = GetLowestFCostNode(openSet);
            
            // Check if we've reached the destination
            if (currentNode.position.Equals(end))
            {
                var path = ReconstructPath(currentNode);
                
                // Cache the result
                pathCache[cacheKey] = new PathCache(path, FixedPoint.FromFloat(Time.time), category);
                return path;
            }

            // Move to closed set
            openSet.Remove(currentNode);
            closedSet.Add(PositionToString(currentNode.position));

            // Process neighbors
            var neighbors = PathfindingManager.GetWalkableNeighbors(currentNode.position);
            foreach (var neighbor in neighbors)
            {
                if (closedSet.Contains(PositionToString(neighbor)))
                {
                    continue;
                }

                // Calculate new cost
                FixedPoint newGCost = currentNode.gCost + CalculateMovementCost(currentNode.position, neighbor, category);
                
                // Add predictive avoidance cost if enabled
                if (predictiveAvoidance)
                {
                    newGCost += CalculatePredictiveCollisionCost(neighbor);
                }

                // Find if this neighbor is already in the open set
                var neighborNode = openSet.FirstOrDefault(n => n.position.Equals(neighbor));
                
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

    private FixedPoint CalculateMovementCost(GridPosition from, GridPosition to, string category = null)
    {
        // Example: Manhattan distance as cost
        var (fx, fy) = from.ToInt();
        var (tx, ty) = to.ToInt();
        int dx = Math.Abs(fx - tx);
        int dy = Math.Abs(fy - ty);
        return FixedPoint.FromInt(dx + dy);
    }

    private FixedPoint CalculateHeuristic(GridPosition from, GridPosition to, string category = null)
    {
        // Example: Manhattan distance as heuristic
        var (fx, fy) = from.ToInt();
        var (tx, ty) = to.ToInt();
        int dx = Math.Abs(fx - tx);
        int dy = Math.Abs(fy - ty);
        return FixedPoint.FromInt(dx + dy);
    }
} 