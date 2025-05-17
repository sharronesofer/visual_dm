using System.Collections.Generic;

public class PathfindingNode
{
    public GridPosition position;
    public FixedPoint gCost; // Cost from start
    public FixedPoint hCost; // Heuristic cost to end

    // Reference to parent node for path reconstruction
    public PathfindingNode parent;

    // Total cost (g + h)
    public FixedPoint fCost => gCost + hCost;

    public PathfindingNode(GridPosition position, FixedPoint gCost, FixedPoint hCost, PathfindingNode parent = null)
    {
        this.position = position;
        this.gCost = gCost;
        this.hCost = hCost;
        this.parent = parent;
    }
}

public class CategoryPathRules
{
    public List<CellType> preferredTypes = new List<CellType>();
    public List<CellType> avoidTypes = new List<CellType>();
    public FixedPoint weightMultiplier = FixedPoint.OneFP;

    public CategoryPathRules()
    {
    }

    public CategoryPathRules(List<CellType> preferredTypes, List<CellType> avoidTypes, FixedPoint weightMultiplier)
    {
        this.preferredTypes = preferredTypes;
        this.avoidTypes = avoidTypes;
        this.weightMultiplier = weightMultiplier;
    }
}

public class PathCache
{
    public List<GridPosition> path;
    public FixedPoint timestamp;
    public string category;

    public PathCache(List<GridPosition> path, FixedPoint timestamp, string category = null)
    {
        this.path = path;
        this.timestamp = timestamp;
        this.category = category;
    }
} 