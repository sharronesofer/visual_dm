using System;
using System.Collections.Generic;

namespace VisualDM.Grid.Pathfinding
{
    /// <summary>
    /// Represents a node in the pathfinding algorithm with position and cost information
    /// </summary>
    public class PathfindingNode
    {
        public GridPosition position;
        public float gCost; // Cost from start
        public float hCost; // Heuristic cost to end

        // Reference to parent node for path reconstruction
        public PathfindingNode parent;

        // Total cost (g + h)
        public float fCost => gCost + hCost;

        public PathfindingNode(GridPosition position, float gCost, float hCost, PathfindingNode parent = null)
        {
            this.position = position;
            this.gCost = gCost;
            this.hCost = hCost;
            this.parent = parent;
        }
    }

    /// <summary>
    /// Options for group pathfinding
    /// </summary>
    public class GroupPathfindingOptions
    {
        public int groupSize = 1;
        public int formationWidth = 1;
        public int formationSpacing = 2;
        public bool predictiveAvoidance = true;

        public GroupPathfindingOptions()
        {
        }

        public GroupPathfindingOptions(int groupSize, int formationWidth, int formationSpacing, bool predictiveAvoidance)
        {
            this.groupSize = groupSize;
            this.formationWidth = formationWidth;
            this.formationSpacing = formationSpacing;
            this.predictiveAvoidance = predictiveAvoidance;
        }
    }

    /// <summary>
    /// Defines rules for pathfinding based on POI category
    /// </summary>
    public class CategoryPathRules
    {
        public List<CellType> preferredTypes = new List<CellType>();
        public List<CellType> avoidTypes = new List<CellType>();
        public float weightMultiplier = 1.0f;

        public CategoryPathRules()
        {
        }

        public CategoryPathRules(List<CellType> preferredTypes, List<CellType> avoidTypes, float weightMultiplier)
        {
            this.preferredTypes = preferredTypes;
            this.avoidTypes = avoidTypes;
            this.weightMultiplier = weightMultiplier;
        }
    }

    /// <summary>
    /// Interface for a pathfinding system
    /// </summary>
    public interface IPathfindingSystem
    {
        List<GridPosition> FindPath(GridPosition start, GridPosition end, string characterId = null, bool predictiveAvoidance = false);
        List<GridPosition> FindGroupPath(GridPosition start, GridPosition end, GroupPathfindingOptions options, string characterId = null);
        bool IsPathPossible(GridPosition start, GridPosition end);
        HashSet<string> FindAccessibleArea(GridPosition start, int maxDistance);
        void InvalidateCache(GridPosition position, int radius = 1);
    }

    /// <summary>
    /// Entry in the path cache
    /// </summary>
    public class PathCache
    {
        public List<GridPosition> path;
        public float timestamp;
        public string category;

        public PathCache(List<GridPosition> path, float timestamp, string category = null)
        {
            this.path = path;
            this.timestamp = timestamp;
            this.category = category;
        }
    }
} 