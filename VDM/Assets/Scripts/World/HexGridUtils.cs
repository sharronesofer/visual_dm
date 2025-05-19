using System;
using System.Collections.Generic;

namespace VisualDM.World
{
    /// <summary>
    /// Static utility functions for multi-scale hex grid operations (region/POI conversion, containment, etc).
    /// </summary>
    public static class HexGridUtils
    {
        public const int RegionToPOIRadius = 11; // 121 POI hexes per region (radius 11)

        public static HexCoordinate POIToRegion(HexCoordinate poi)
        {
            // Integer division by region radius
            int q = (int)Math.Floor((double)poi.X / RegionToPOIRadius);
            int r = (int)Math.Floor((double)poi.Z / RegionToPOIRadius);
            return HexCoordinate.FromAxial(q, r);
        }

        public static HexCoordinate RegionToPOIOrigin(HexCoordinate region)
        {
            // Returns the POI hex at the center of the region
            var (q, r) = region.ToAxial();
            return HexCoordinate.FromAxial(q * RegionToPOIRadius, r * RegionToPOIRadius);
        }

        public static IEnumerable<HexCoordinate> POIsInRegion(HexCoordinate region)
        {
            // Enumerate all POI hexes contained in a region hex
            var origin = RegionToPOIOrigin(region);
            int radius = RegionToPOIRadius;
            for (int dx = -radius + 1; dx < radius; dx++)
            {
                for (int dz = Math.Max(-radius + 1, -dx - radius + 1); dz < Math.Min(radius, -dx + radius); dz++)
                {
                    int dy = -dx - dz;
                    yield return new HexCoordinate(origin.X + dx, origin.Y + dy, origin.Z + dz);
                }
            }
        }

        /// <summary>
        /// Returns the parent region hex for a given POI hex.
        /// </summary>
        public static HexCoordinate GetParentRegion(HexCoordinate poi)
        {
            return POIToRegion(poi);
        }

        /// <summary>
        /// Enumerates all POI hex coordinates for a given region hex.
        /// </summary>
        public static IEnumerable<HexCoordinate> EnumeratePOIsForRegion(HexCoordinate region)
        {
            return POIsInRegion(region);
        }
    }
}