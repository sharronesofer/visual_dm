using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Grid
{
    /// <summary>
    /// Represents a chunk of the grid, containing a fixed-size array of hex cells.
    /// </summary>
    public class GridChunk
    {
        public readonly int ChunkSize;
        public readonly Vector2Int ChunkPosition;
        private HexCell[,] cells;

        /// <summary>
        /// Initializes a new GridChunk at the given chunk position.
        /// </summary>
        public GridChunk(Vector2Int chunkPosition, int chunkSize)
        {
            ChunkPosition = chunkPosition;
            ChunkSize = chunkSize;
            cells = new HexCell[chunkSize, chunkSize];
        }

        /// <summary>
        /// Gets or sets the cell at the given local chunk coordinates.
        /// </summary>
        public HexCell this[int x, int y]
        {
            get => cells[x, y];
            set => cells[x, y] = value;
        }

        /// <summary>
        /// Serializes the chunk data for storage or transfer.
        /// </summary>
        public byte[] Serialize()
        {
            // TODO: Implement efficient serialization (e.g., binary, compression)
            return new byte[0];
        }

        /// <summary>
        /// Deserializes chunk data from a byte array.
        /// </summary>
        public static GridChunk Deserialize(byte[] data)
        {
            // TODO: Implement deserialization logic
            return null;
        }
    }

    public enum CellType { Floor, Wall, Water, Grass, Custom }

    /// <summary>
    /// Represents a single hex cell in the grid.
    /// </summary>
    public class HexCell
    {
        /// <summary>
        /// The type of this cell (e.g., Floor, Wall, Water).
        /// </summary>
        public CellType Type { get; set; }
        /// <summary>
        /// Whether this cell is walkable.
        /// </summary>
        public bool IsWalkable { get; set; }

        public HexCell(CellType type = CellType.Floor, bool isWalkable = true)
        {
            Type = type;
            IsWalkable = isWalkable;
        }
    }
} 