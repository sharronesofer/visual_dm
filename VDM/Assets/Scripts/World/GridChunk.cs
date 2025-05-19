using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.World
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

        /// <summary>
        /// Generates a region-level grid chunk (region hexes only).
        /// </summary>
        public static GridChunk GenerateRegionChunk(Vector2Int chunkPosition, int chunkSize)
        {
            var chunk = new GridChunk(chunkPosition, chunkSize);
            for (int x = 0; x < chunkSize; x++)
            {
                for (int y = 0; y < chunkSize; y++)
                {
                    // Map chunk-local (x, y) to region hex coordinates (axial)
                    int q = chunkPosition.x * chunkSize + x;
                    int r = chunkPosition.y * chunkSize + y;
                    var coord = HexCoordinate.FromAxial(q, r);
                    chunk[x, y] = new HexCell(CellType.Floor, true, coord);
                }
            }
            return chunk;
        }

        /// <summary>
        /// Generates a POI-level grid chunk for a given region hex.
        /// </summary>
        public static List<HexCell> GeneratePOIHexesForRegion(HexCoordinate regionHex)
        {
            var poiHexes = new List<HexCell>();
            foreach (var poiCoord in HexGridUtils.POIsInRegion(regionHex))
            {
                poiHexes.Add(new HexCell(CellType.Floor, true, poiCoord));
            }
            return poiHexes;
        }

        /// <summary>
        /// Place an object at the given hex coordinate (if cell exists and is empty).
        /// </summary>
        public bool PlaceObjectAt(HexCoordinate coord, object obj)
        {
            foreach (var cell in cells)
            {
                if (cell != null && cell.Coordinate.HasValue && cell.Coordinate.Value.Equals(coord))
                {
                    return cell.PlaceObject(obj);
                }
            }
            return false;
        }

        /// <summary>
        /// Remove the placed object at the given hex coordinate (if any).
        /// </summary>
        public void RemoveObjectAt(HexCoordinate coord)
        {
            foreach (var cell in cells)
            {
                if (cell != null && cell.Coordinate.HasValue && cell.Coordinate.Value.Equals(coord))
                {
                    cell.ClearObject();
                    return;
                }
            }
        }

        /// <summary>
        /// Get the placed object at the given hex coordinate (null if none).
        /// </summary>
        public object GetObjectAt(HexCoordinate coord)
        {
            foreach (var cell in cells)
            {
                if (cell != null && cell.Coordinate.HasValue && cell.Coordinate.Value.Equals(coord))
                {
                    return cell.GetPlacedObject();
                }
            }
            return null;
        }

        /// <summary>
        /// Enumerate all placed objects in this chunk (optionally filter by scale).
        /// </summary>
        public IEnumerable<(HexCoordinate coord, object obj)> EnumeratePlacedObjects()
        {
            foreach (var cell in cells)
            {
                if (cell != null && cell.Coordinate.HasValue && cell.PlacedObject != null)
                {
                    yield return (cell.Coordinate.Value, cell.PlacedObject);
                }
            }
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
        /// <summary>
        /// The hex coordinate of this cell (region or POI scale).
        /// </summary>
        public HexCoordinate? Coordinate { get; set; }
        /// <summary>
        /// The object placed on this cell (building, feature, etc). Null if empty.
        /// </summary>
        public object PlacedObject { get; private set; }

        public HexCell(CellType type = CellType.Floor, bool isWalkable = true, HexCoordinate? coordinate = null)
        {
            Type = type;
            IsWalkable = isWalkable;
            Coordinate = coordinate;
        }

        /// <summary>
        /// Place an object on this cell. Returns true if successful, false if already occupied.
        /// </summary>
        public bool PlaceObject(object obj)
        {
            if (PlacedObject != null) return false;
            PlacedObject = obj;
            return true;
        }

        /// <summary>
        /// Remove the placed object from this cell.
        /// </summary>
        public void ClearObject()
        {
            PlacedObject = null;
        }

        /// <summary>
        /// Get the placed object (null if none).
        /// </summary>
        public object GetPlacedObject() => PlacedObject;
    }
}