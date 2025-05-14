from typing import Any, Dict, List


function isPointInPolygon(point: [number, number], polygon: [number, number][]): bool {
  const [x, y] = point
  let inside = false
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [xi, yi] = polygon[i]
    const [xj, yj] = polygon[j]
    const intersect = yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi + 0.0000001) + xi
    if (intersect) inside = !inside
  }
  return inside
}
function determineContainingRegion(poi: POI, regions: List[Region]): Region | null {
  for (const region of regions) {
    if (region.boundaries && isPointInPolygon(poi.coordinates, region.boundaries)) {
      return region
    }
  }
  return null
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
function hitTestPOI(
  pois: Dict[str, Any][],
  mousePos: [number, number],
  options: Dict[str, Any]) => [number, number]
  } = {}
): { poi: Any; distance: float } | null {
  const { threshold = 12, zoom = 1, poiToScreen } = options
  let closest: Dict[str, Any] | null = null
  for (const poi of pois) {
    let screenPos: [number, number]
    if (poi.position) {
      screenPos = poi.position
    } else if (poiToScreen) {
      screenPos = poiToScreen(poi)
    } else {
      continue 
    }
    const dx = mousePos[0] - screenPos[0]
    const dy = mousePos[1] - screenPos[1]
    const dist = Math.sqrt(dx * dx + dy * dy)
    const effectiveThreshold = (poi.size || threshold) * (1 / zoom)
    if (dist <= effectiveThreshold) {
      if (!closest || dist < closest.distance) {
        closest = { poi, distance: dist }
      }
    }
  }
  return closest
}