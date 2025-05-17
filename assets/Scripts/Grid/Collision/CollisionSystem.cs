using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Grid.Collision
{
    /// <summary>
    /// Represents the bounds of an object in a QuadTree
    /// </summary>
    public class QuadTreeBounds
    {
        public int x;
        public int y;
        public int width;
        public int height;

        public QuadTreeBounds(int x, int y, int width, int height)
        {
            this.x = x;
            this.y = y;
            this.width = width;
            this.height = height;
        }
    }

    /// <summary>
    /// Represents a node in a QuadTree spatial partitioning structure
    /// </summary>
    public class QuadTreeNode
    {
        public QuadTreeBounds bounds;
        public List<string> objects;
        public List<QuadTreeNode> nodes;
        public int level;

        public QuadTreeNode(QuadTreeBounds bounds, int level)
        {
            this.bounds = bounds;
            this.objects = new List<string>();
            this.nodes = new List<QuadTreeNode>();
            this.level = level;
        }
    }

    /// <summary>
    /// Provides spatial partitioning and collision detection using a QuadTree data structure.
    /// Optimized for grid-based object placement and collision queries.
    /// </summary>
    public class CollisionSystem
    {
        private GridManager gridManager;
        private QuadTreeNode quadTree;
        private readonly int MAX_OBJECTS = 10;
        private readonly int MAX_LEVELS = 5;

        /// <summary>
        /// Storage dictionary for object bounds to avoid recreating them
        /// </summary>
        private Dictionary<string, QuadTreeBounds> objectBounds = new Dictionary<string, QuadTreeBounds>();

        /// <summary>
        /// Initializes a new instance of the collision system
        /// </summary>
        /// <param name="gridManager">Grid manager for additional collision checks</param>
        public CollisionSystem(GridManager gridManager = null)
        {
            this.gridManager = gridManager;

            // Initialize quadtree with grid dimensions or default values
            int width = gridManager != null ? gridManager.GetWidth() : 100;
            int height = gridManager != null ? gridManager.GetHeight() : 100;

            this.quadTree = new QuadTreeNode(
                new QuadTreeBounds(0, 0, width, height),
                0
            );
        }

        /// <summary>
        /// Clears all objects from the collision system
        /// </summary>
        public void Clear()
        {
            this.quadTree.objects.Clear();
            this.quadTree.nodes.Clear();
            this.objectBounds.Clear();
        }

        /// <summary>
        /// Inserts an object into the collision system
        /// </summary>
        /// <param name="objectId">Unique identifier for the object</param>
        /// <param name="position">Position of the object on the grid</param>
        /// <param name="dimensions">Dimensions of the object</param>
        public void Insert(string objectId, GridPosition position, GridDimensions dimensions)
        {
            QuadTreeBounds bounds = new QuadTreeBounds(
                position.x,
                position.y,
                dimensions.width,
                dimensions.height
            );

            // Store bounds for later reference
            objectBounds[objectId] = bounds;

            InsertIntoNode(this.quadTree, objectId, bounds);
        }

        /// <summary>
        /// Removes an object from the collision system
        /// </summary>
        /// <param name="objectId">Unique identifier for the object</param>
        /// <param name="position">Position of the object on the grid</param>
        /// <param name="dimensions">Dimensions of the object</param>
        public void Remove(string objectId, GridPosition position, GridDimensions dimensions)
        {
            QuadTreeBounds bounds = new QuadTreeBounds(
                position.x,
                position.y,
                dimensions.width,
                dimensions.height
            );

            RemoveFromNode(this.quadTree, objectId, bounds);
            objectBounds.Remove(objectId);
        }

        /// <summary>
        /// Updates an object's position in the collision system
        /// </summary>
        /// <param name="objectId">Unique identifier for the object</param>
        /// <param name="oldPos">Previous position of the object</param>
        /// <param name="newPos">New position of the object</param>
        /// <param name="dimensions">Dimensions of the object</param>
        public void Update(string objectId, GridPosition oldPos, GridPosition newPos, GridDimensions dimensions)
        {
            Remove(objectId, oldPos, dimensions);
            Insert(objectId, newPos, dimensions);
        }

        /// <summary>
        /// Finds all objects that collide with the specified bounds
        /// </summary>
        /// <param name="position">Position to check for collisions</param>
        /// <param name="dimensions">Dimensions of the area to check</param>
        /// <returns>List of object IDs that collide with the specified bounds</returns>
        public List<string> FindCollisions(GridPosition position, GridDimensions dimensions)
        {
            QuadTreeBounds bounds = new QuadTreeBounds(
                position.x,
                position.y,
                dimensions.width,
                dimensions.height
            );

            List<string> potentialCollisions = QueryNode(this.quadTree, bounds);
            List<string> result = new List<string>();

            foreach (string objId in potentialCollisions)
            {
                if (CheckDetailedCollision(objId, bounds))
                {
                    result.Add(objId);
                }
            }

            return result;
        }

        /// <summary>
        /// Finds a valid position for an object near the specified position
        /// </summary>
        /// <param name="objectId">Unique identifier for the object</param>
        /// <param name="position">Desired position of the object</param>
        /// <param name="dimensions">Dimensions of the object</param>
        /// <param name="maxAttempts">Maximum number of positions to try</param>
        /// <returns>A valid position, or null if no valid position was found</returns>
        public GridPosition? FindValidPosition(
            string objectId,
            GridPosition position,
            GridDimensions dimensions,
            int maxAttempts = 10)
        {
            // Try original position first
            if (IsPositionValid(position, dimensions, objectId))
            {
                return position;
            }

            // Try positions in expanding spiral pattern
            List<GridPosition> spiralOffsets = GenerateSpiralOffsets(maxAttempts);
            foreach (GridPosition offset in spiralOffsets)
            {
                GridPosition newPos = new GridPosition(
                    position.x + offset.x,
                    position.y + offset.y
                );

                if (IsPositionValid(newPos, dimensions, objectId))
                {
                    return newPos;
                }
            }

            return null;
        }

        /// <summary>
        /// Inserts an object into a quadtree node
        /// </summary>
        private void InsertIntoNode(QuadTreeNode node, string objectId, QuadTreeBounds bounds)
        {
            // If node has subnodes, insert into appropriate subnode
            if (node.nodes.Count > 0)
            {
                int index = GetNodeIndex(node, bounds);
                if (index != -1)
                {
                    InsertIntoNode(node.nodes[index], objectId, bounds);
                    return;
                }
            }

            // Add object to this node
            node.objects.Add(objectId);

            // Split if needed
            if (node.objects.Count > MAX_OBJECTS && node.level < MAX_LEVELS)
            {
                if (node.nodes.Count == 0)
                {
                    Split(node);
                }

                // Redistribute existing objects
                int i = 0;
                while (i < node.objects.Count)
                {
                    string currentId = node.objects[i];
                    if (!objectBounds.TryGetValue(currentId, out QuadTreeBounds currentBounds))
                    {
                        i++;
                        continue;
                    }

                    int index = GetNodeIndex(node, currentBounds);
                    if (index != -1)
                    {
                        // Remove from current node and add to subnode
                        string movedId = node.objects[i];
                        node.objects.RemoveAt(i);
                        InsertIntoNode(node.nodes[index], movedId, currentBounds);
                    }
                    else
                    {
                        i++;
                    }
                }
            }
        }

        /// <summary>
        /// Removes an object from a quadtree node
        /// </summary>
        private void RemoveFromNode(QuadTreeNode node, string objectId, QuadTreeBounds bounds)
        {
            // If node has subnodes, try to remove from appropriate subnode
            if (node.nodes.Count > 0)
            {
                int index = GetNodeIndex(node, bounds);
                if (index != -1)
                {
                    RemoveFromNode(node.nodes[index], objectId, bounds);
                    return;
                }
            }

            // Remove object from this node
            node.objects.Remove(objectId);
        }

        /// <summary>
        /// Queries a quadtree node for objects that may intersect the given bounds
        /// </summary>
        private List<string> QueryNode(QuadTreeNode node, QuadTreeBounds bounds)
        {
            List<string> result = new List<string>();

            // Get index for bounds
            int index = GetNodeIndex(node, bounds);

            // Add objects from this node
            result.AddRange(node.objects);

            // If node has subnodes and bounds fits in a subnode, add from that subnode
            if (node.nodes.Count > 0)
            {
                if (index != -1)
                {
                    result.AddRange(QueryNode(node.nodes[index], bounds));
                }
                else
                {
                    // Bounds overlaps multiple nodes, check all
                    foreach (QuadTreeNode subnode in node.nodes)
                    {
                        if (BoundsOverlap(bounds, subnode.bounds))
                        {
                            result.AddRange(QueryNode(subnode, bounds));
                        }
                    }
                }
            }

            return result;
        }

        /// <summary>
        /// Splits a quadtree node into four child nodes
        /// </summary>
        private void Split(QuadTreeNode node)
        {
            int subWidth = node.bounds.width / 2;
            int subHeight = node.bounds.height / 2;
            int x = node.bounds.x;
            int y = node.bounds.y;
            int level = node.level + 1;

            // Create the four child nodes (clockwise from top right)
            node.nodes.Add(new QuadTreeNode(
                new QuadTreeBounds(x + subWidth, y, subWidth, subHeight),
                level
            ));

            node.nodes.Add(new QuadTreeNode(
                new QuadTreeBounds(x, y, subWidth, subHeight),
                level
            ));

            node.nodes.Add(new QuadTreeNode(
                new QuadTreeBounds(x, y + subHeight, subWidth, subHeight),
                level
            ));

            node.nodes.Add(new QuadTreeNode(
                new QuadTreeBounds(x + subWidth, y + subHeight, subWidth, subHeight),
                level
            ));
        }

        /// <summary>
        /// Gets the index of the quadtree node where the bounds fits
        /// </summary>
        private int GetNodeIndex(QuadTreeNode node, QuadTreeBounds bounds)
        {
            int verticalMidpoint = node.bounds.x + (node.bounds.width / 2);
            int horizontalMidpoint = node.bounds.y + (node.bounds.height / 2);

            bool fitsTop = bounds.y < horizontalMidpoint && bounds.y + bounds.height < horizontalMidpoint;
            bool fitsBottom = bounds.y > horizontalMidpoint;
            bool fitsLeft = bounds.x < verticalMidpoint && bounds.x + bounds.width < verticalMidpoint;
            bool fitsRight = bounds.x > verticalMidpoint;

            if (fitsTop && fitsRight) return 0;
            if (fitsTop && fitsLeft) return 1;
            if (fitsBottom && fitsLeft) return 2;
            if (fitsBottom && fitsRight) return 3;

            return -1;
        }

        /// <summary>
        /// Checks if two bounds overlap
        /// </summary>
        private bool BoundsOverlap(QuadTreeBounds a, QuadTreeBounds b)
        {
            return a.x < b.x + b.width && a.x + a.width > b.x &&
                   a.y < b.y + b.height && a.y + a.height > b.y;
        }

        /// <summary>
        /// Checks if an object collides with the specified bounds
        /// </summary>
        private bool CheckDetailedCollision(string objectId, QuadTreeBounds bounds)
        {
            return objectBounds.TryGetValue(objectId, out QuadTreeBounds objBounds) && 
                   BoundsOverlap(bounds, objBounds);
        }

        /// <summary>
        /// Checks if a position is valid for an object
        /// </summary>
        private bool IsPositionValid(
            GridPosition position,
            GridDimensions dimensions,
            string excludeId = null)
        {
            // Check if position is within grid bounds
            if (gridManager != null)
            {
                for (int y = 0; y < dimensions.height; y++)
                {
                    for (int x = 0; x < dimensions.width; x++)
                    {
                        GridPosition checkPos = new GridPosition(position.x + x, position.y + y);
                        if (!gridManager.IsValidPosition(checkPos))
                        {
                            return false;
                        }

                        GridCell cell = gridManager.GetCellAt(checkPos);
                        if (cell == null || !cell.walkable || (cell.isOccupied && cell.occupiedBy != excludeId))
                        {
                            return false;
                        }
                    }
                }
            }

            // Check for collisions with other objects
            QuadTreeBounds bounds = new QuadTreeBounds(
                position.x,
                position.y,
                dimensions.width,
                dimensions.height
            );

            List<string> collisions = QueryNode(this.quadTree, bounds);
            foreach (string objId in collisions)
            {
                if (objId != excludeId && CheckDetailedCollision(objId, bounds))
                {
                    return false;
                }
            }

            return true;
        }

        /// <summary>
        /// Generates positions in a spiral pattern around the center
        /// </summary>
        private List<GridPosition> GenerateSpiralOffsets(int maxAttempts)
        {
            List<GridPosition> result = new List<GridPosition>();
            
            // Generate spiral pattern (layer by layer)
            int layer = 1;
            int count = 0;
            
            while (count < maxAttempts)
            {
                // Add positions in the current layer (going around clockwise)
                
                // Top edge (left to right)
                for (int x = -layer + 1; x <= layer && count < maxAttempts; x++)
                {
                    result.Add(new GridPosition(x, -layer));
                    count++;
                }
                
                // Right edge (top to bottom)
                for (int y = -layer + 1; y <= layer && count < maxAttempts; y++)
                {
                    result.Add(new GridPosition(layer, y));
                    count++;
                }
                
                // Bottom edge (right to left)
                for (int x = layer - 1; x >= -layer && count < maxAttempts; x--)
                {
                    result.Add(new GridPosition(x, layer));
                    count++;
                }
                
                // Left edge (bottom to top)
                for (int y = layer - 1; y >= -layer + 1 && count < maxAttempts; y--)
                {
                    result.Add(new GridPosition(-layer, y));
                    count++;
                }
                
                layer++;
            }
            
            return result;
        }
    }
} 