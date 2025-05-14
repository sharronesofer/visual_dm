import { POI } from '../types/poi';
import { Region } from '../types/map';

// Simple point-in-polygon algorithm (ray-casting)
function isPointInPolygon(point: [number, number], polygon: [number, number][]): boolean {
  const [x, y] = point;
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [xi, yi] = polygon[i];
    const [xj, yj] = polygon[j];
    const intersect = yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi + 0.0000001) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

// Determine which region contains a POI (returns the first match or null)
export function determineContainingRegion(poi: POI, regions: Region[]): Region | null {
  // Assume each region has a 'boundaries' property: Array<[lng, lat]>
  for (const region of regions) {
    if (region.boundaries && isPointInPolygon(poi.coordinates, region.boundaries)) {
      return region;
    }
  }
  return null;
}

/**
 * Hit test POIs given a mouse position in screen/pixel coordinates.
 * @param pois Array of POIs, each with coordinates in map/world space and a pixel position property (or provide a transform function)
 * @param mousePos [x, y] in screen/pixel coordinates
 * @param options.threshold Hit radius in pixels (default: 12)
 * @param options.zoom Optional zoom factor to adjust hit radius
 * @param options.poiToScreen Optional function to convert POI coordinates to screen position
 * @returns The first POI hit (closest if multiple overlap), or null if none
 */
export function hitTestPOI(
  pois: {
    id: string;
    coordinates: [number, number];
    position?: [number, number];
    size?: number;
  }[],
  mousePos: [number, number],
  options: {
    threshold?: number;
    zoom?: number;
    poiToScreen?: (poi: { coordinates: [number, number] }) => [number, number];
  } = {}
): { poi: any; distance: number } | null {
  const { threshold = 12, zoom = 1, poiToScreen } = options;
  let closest: { poi: any; distance: number } | null = null;
  for (const poi of pois) {
    // Determine screen position of POI
    let screenPos: [number, number];
    if (poi.position) {
      screenPos = poi.position;
    } else if (poiToScreen) {
      screenPos = poiToScreen(poi);
    } else {
      continue; // Cannot test without screen position
    }
    const dx = mousePos[0] - screenPos[0];
    const dy = mousePos[1] - screenPos[1];
    const dist = Math.sqrt(dx * dx + dy * dy);
    // Adjust threshold for zoom and POI size
    const effectiveThreshold = (poi.size || threshold) * (1 / zoom);
    if (dist <= effectiveThreshold) {
      if (!closest || dist < closest.distance) {
        closest = { poi, distance: dist };
      }
    }
  }
  return closest;
}
