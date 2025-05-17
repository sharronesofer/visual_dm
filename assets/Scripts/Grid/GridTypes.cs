using System;
using UnityEngine;

namespace VisualDM.Grid
{
    /// <summary>
    /// Represents a position in a 2D grid
    /// </summary>
    [Serializable]
    public struct GridPosition
    {
        public int x;
        public int y;

        public GridPosition(int x, int y)
        {
            this.x = x;
            this.y = y;
        }

        public override bool Equals(object obj)
        {
            if (!(obj is GridPosition))
                return false;

            var other = (GridPosition)obj;
            return x == other.x && y == other.y;
        }

        public override int GetHashCode()
        {
            return HashCode.Combine(x, y);
        }

        public static bool operator ==(GridPosition a, GridPosition b)
        {
            return a.x == b.x && a.y == b.y;
        }

        public static bool operator !=(GridPosition a, GridPosition b)
        {
            return a.x != b.x || a.y != b.y;
        }

        public override string ToString()
        {
            return $"({x}, {y})";
        }

        // Conversion from/to Vector2Int for Unity integration
        public static implicit operator Vector2Int(GridPosition position)
        {
            return new Vector2Int(position.x, position.y);
        }

        public static implicit operator GridPosition(Vector2Int vector)
        {
            return new GridPosition(vector.x, vector.y);
        }
    }

    /// <summary>
    /// Represents the dimensions of a grid
    /// </summary>
    [Serializable]
    public struct GridDimensions
    {
        public int width;
        public int height;

        public GridDimensions(int width, int height)
        {
            this.width = width;
            this.height = height;
        }
    }

    /// <summary>
    /// Defines the possible types of cells in a grid
    /// </summary>
    public enum CellType
    {
        EMPTY,
        OCCUPIED,
        BLOCKED,
        PATH,
        WATER,
        MOUNTAIN,
        FOREST,
        WALL,
        ROAD,
        ROUGH
    }

    /// <summary>
    /// Represents a cell in a grid with its properties
    /// </summary>
    [Serializable]
    public class GridCell
    {
        public CellType cellType;
        public bool walkable;
        public bool isOccupied;
        public string occupiedBy;
        public string buildingId;
        public string roomId;
        public string doorId;

        public GridCell()
        {
            cellType = CellType.EMPTY;
            walkable = true;
            isOccupied = false;
            occupiedBy = null;
            buildingId = null;
            roomId = null;
            doorId = null;
        }

        public GridCell(CellType cellType, bool walkable = true, bool isOccupied = false, string occupiedBy = null)
        {
            this.cellType = cellType;
            this.walkable = walkable;
            this.isOccupied = isOccupied;
            this.occupiedBy = occupiedBy;
            this.buildingId = null;
            this.roomId = null;
            this.doorId = null;
        }
    }
} 