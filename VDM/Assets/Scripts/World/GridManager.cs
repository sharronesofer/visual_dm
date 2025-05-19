using UnityEngine;
using System;
using System.Linq;
using System.Collections.Generic;

namespace VisualDM.World
{
    /// <summary>
    /// Manages a 2D grid with cells that have various properties.
    /// Provides methods for accessing and modifying the grid cells.
    /// </summary>
    public class GridManager
    {
        [Serializable]
        public class SerializedGridData
        {
            public GridDimensions dimensions;
            public List<List<SerializedGridCell>> cells;
        }

        [Serializable]
        public class SerializedGridCell
        {
            public CellType cellType;
            public bool isOccupied;
            public string occupiedBy;
            public string buildingId;
            public string roomId;
            public string doorId;
        }

        private GridDimensions dimensions;
        private GridCell[,] cells;

        /// <summary>
        /// Creates a new grid with specified dimensions.
        /// </summary>
        /// <param name="dimensions">Width and height of the grid</param>
        public GridManager(GridDimensions dimensions)
        {
            this.dimensions = dimensions;
            this.cells = new GridCell[dimensions.height, dimensions.width];

            // Initialize cells
            for (int y = 0; y < dimensions.height; y++)
            {
                for (int x = 0; x < dimensions.width; x++)
                {
                    cells[y, x] = new GridCell
                    {
                        cellType = CellType.EMPTY,
                        walkable = true,
                        isOccupied = false,
                        occupiedBy = null
                    };
                }
            }
        }

        /// <summary>
        /// Gets the cell at the specified position.
        /// </summary>
        /// <param name="position">Position in the grid</param>
        /// <returns>The cell at the position, or null if the position is invalid</returns>
        public GridCell GetCellAt(GridPosition position)
        {
            if (!IsValidPosition(position))
            {
                return null;
            }
            return cells[position.y, position.x];
        }

        /// <summary>
        /// Sets the type of a cell at the specified position.
        /// </summary>
        /// <param name="position">Position in the grid</param>
        /// <param name="cellType">New cell type</param>
        public void SetCellType(GridPosition position, CellType cellType)
        {
            if (!IsValidPosition(position))
            {
                return;
            }

            GridCell cell = cells[position.y, position.x];
            cell.cellType = cellType;

            // Update walkability based on cell type
            cell.walkable = cellType != CellType.WALL && cellType != CellType.BLOCKED;
        }

        /// <summary>
        /// Sets the occupied status of a cell.
        /// </summary>
        /// <param name="position">Position in the grid</param>
        /// <param name="occupied">Whether the cell is occupied</param>
        public void SetOccupied(GridPosition position, bool occupied)
        {
            if (!IsValidPosition(position))
            {
                return;
            }
            cells[position.y, position.x].isOccupied = occupied;
        }

        /// <summary>
        /// Sets the entity occupying a cell.
        /// </summary>
        /// <param name="position">Position in the grid</param>
        /// <param name="entityId">ID of the occupying entity</param>
        public void SetOccupiedBy(GridPosition position, string entityId)
        {
            if (!IsValidPosition(position))
            {
                return;
            }
            cells[position.y, position.x].occupiedBy = entityId;
            cells[position.y, position.x].isOccupied = entityId != null;
        }

        /// <summary>
        /// Checks if a position is within the grid boundaries.
        /// </summary>
        /// <param name="position">Position to check</param>
        /// <returns>True if the position is valid</returns>
        public bool IsValidPosition(GridPosition position)
        {
            return position.x >= 0 && position.x < dimensions.width &&
                   position.y >= 0 && position.y < dimensions.height;
        }

        /// <summary>
        /// Gets the width of the grid.
        /// </summary>
        public int GetWidth()
        {
            return dimensions.width;
        }

        /// <summary>
        /// Gets the height of the grid.
        /// </summary>
        public int GetHeight()
        {
            return dimensions.height;
        }

        /// <summary>
        /// Gets the dimensions of the grid.
        /// </summary>
        public GridDimensions GetDimensions()
        {
            return dimensions;
        }

        /// <summary>
        /// Clears the grid, resetting all cells to default values.
        /// </summary>
        public void Clear()
        {
            for (int y = 0; y < dimensions.height; y++)
            {
                for (int x = 0; x < dimensions.width; x++)
                {
                    cells[y, x] = new GridCell
                    {
                        cellType = CellType.EMPTY,
                        walkable = true,
                        isOccupied = false,
                        occupiedBy = null
                    };
                }
            }
        }

        /// <summary>
        /// Converts the grid to a serializable format.
        /// </summary>
        /// <returns>Serialized grid data</returns>
        public SerializedGridData ToSerializedData()
        {
            var serializedData = new SerializedGridData
            {
                dimensions = this.dimensions,
                cells = new List<List<SerializedGridCell>>()
            };

            for (int y = 0; y < dimensions.height; y++)
            {
                List<SerializedGridCell> row = new List<SerializedGridCell>();
                for (int x = 0; x < dimensions.width; x++)
                {
                    GridCell cell = cells[y, x];
                    row.Add(new SerializedGridCell
                    {
                        cellType = cell.cellType,
                        isOccupied = cell.isOccupied,
                        occupiedBy = cell.occupiedBy,
                        buildingId = cell.buildingId,
                        roomId = cell.roomId,
                        doorId = cell.doorId
                    });
                }
                serializedData.cells.Add(row);
            }

            return serializedData;
        }

        /// <summary>
        /// Creates a GridManager from serialized data.
        /// </summary>
        /// <param name="data">Serialized grid data</param>
        /// <returns>A new GridManager instance</returns>
        public static GridManager FromSerializedData(SerializedGridData data)
        {
            GridManager manager = new GridManager(data.dimensions);

            for (int y = 0; y < data.dimensions.height; y++)
            {
                for (int x = 0; x < data.dimensions.width; x++)
                {
                    SerializedGridCell cellData = data.cells[y][x];
                    GridCell cell = manager.cells[y, x];
                    cell.cellType = cellData.cellType;
                    cell.isOccupied = cellData.isOccupied;
                    cell.occupiedBy = cellData.occupiedBy;
                    cell.walkable = cellData.cellType != CellType.WALL && cellData.cellType != CellType.BLOCKED;
                    cell.buildingId = cellData.buildingId;
                    cell.roomId = cellData.roomId;
                    cell.doorId = cellData.doorId;
                }
            }

            return manager;
        }

        /// <summary>
        /// Gets a building by its ID (placeholder - to be implemented).
        /// </summary>
        public object GetBuildingById(string buildingId)
        {
            // TODO: Implement actual building lookup
            return null;
        }

        /// <summary>
        /// Gets a room by its ID (placeholder - to be implemented).
        /// </summary>
        public object GetRoomById(string roomId)
        {
            // TODO: Implement actual room lookup
            return null;
        }

        /// <summary>
        /// Gets a door by its ID (placeholder - to be implemented).
        /// </summary>
        public object GetDoorById(string doorId)
        {
            // TODO: Implement actual door lookup
            return null;
        }
    }
} 