using System;
using UnityEngine;

namespace VisualDM.DTOs.World.Region
{
    /// <summary>
    /// Tile data transfer object
    /// </summary>
    [Serializable]
    public class TileDTO
    {
        public int X { get; set; } = 0;
        public int Y { get; set; } = 0;
        public CoordinateSchemaDTO Coordinates { get; set; } = new CoordinateSchemaDTO();
        public RegionTypeDTO Biome { get; set; } = RegionTypeDTO.Plains;
        public TerrainTypeDTO TerrainType { get; set; } = TerrainTypeDTO.Grassland;
        public float Elevation { get; set; } = 0.0f;
        public float Temperature { get; set; } = 0.0f;
        public float Moisture { get; set; } = 0.0f;
        public bool IsBlocked { get; set; } = false;
        public bool HasResource { get; set; } = false;
        public string ResourceType { get; set; } = string.Empty;
    }
} 