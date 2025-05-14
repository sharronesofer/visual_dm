from typing import Any, Dict, List


class IRegion:
    id: str
    name: str
    boundaries: List[List[[float, float]]]
    style: Dict[str, Any]
/**
 * Concrete implementation of the IRegion interface.
 */
class Region implements IRegion {
  id: str
  name: str
  boundaries: [number, number][][]
  style: Dict[str, Any]
  highlightState: 'normal' | 'hover' | 'selected' | 'disabled'
  pois: List[IPOI]
  constructor(params: Dict[str, Any]
    highlightState?: 'normal' | 'hover' | 'selected' | 'disabled'
    pois?: IPOI[]
  }) {
    this.id = params.id
    this.name = params.name
    this.boundaries = params.boundaries
    this.style = params.style || {}
    this.highlightState = params.highlightState || 'normal'
    this.pois = params.pois || []
  }
  /**
   * Checks if a point is inside the region using ray-casting algorithm.
   */
  containsPoint(point: [number, number]): bool {
    const [lng, lat] = point
    const polygon = this.boundaries[0]
    let inside = false
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      const xi = polygon[i][0],
        yi = polygon[i][1]
      const xj = polygon[j][0],
        yj = polygon[j][1]
      const intersect =
        yi > lat !== yj > lat && lng < ((xj - xi) * (lat - yi)) / (yj - yi + 1e-12) + xi
      if (intersect) inside = !inside
    }
    return inside
  }
  /**
   * Returns the bounding box of the region as [[minLng, minLat], [maxLng, maxLat]].
   */
  getBoundingBox(): [[number, number], [number, number]] {
    let minLng = Infinity,
      minLat = Infinity,
      maxLng = -Infinity,
      maxLat = -Infinity
    for (const ring of this.boundaries) {
      for (const [lng, lat] of ring) {
        if (lng < minLng) minLng = lng
        if (lat < minLat) minLat = lat
        if (lng > maxLng) maxLng = lng
        if (lat > maxLat) maxLat = lat
      }
    }
    return [
      [minLng, minLat],
      [maxLng, maxLat],
    ]
  }
  /**
   * Adds a POI to the region.
   */
  addPOI(poi: IPOI): void {
    this.pois.push(poi)
  }
  /**
   * Removes a POI from the region by ID.
   */
  removePOI(poiId: str): void {
    this.pois = this.pois.filter(p => p.id !== poiId)
  }
  /**
   * Calculates the centroid of the outer boundary (simple average method).
   */
  getCentroid(): [number, number] {
    const polygon = this.boundaries[0]
    let x = 0,
      y = 0
    for (const [lng, lat] of polygon) {
      x += lng
      y += lat
    }
    return [x / polygon.length, y / polygon.length]
  }
  /**
   * Calculates the area of the outer boundary using the Shoelace formula.
   */
  getArea(): float {
    const polygon = this.boundaries[0]
    let area = 0
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      area += (polygon[j][0] + polygon[i][0]) * (polygon[j][1] - polygon[i][1])
    }
    return Math.abs(area / 2)
  }
  /**
   * Serializes the Region instance to a plain object for JSON.
   */
  toJSON(): object {
    return {
      id: this.id,
      name: this.name,
      boundaries: this.boundaries,
      style: this.style,
      highlightState: this.highlightState,
      pois: this.pois.map(poi =>
        typeof poi === 'object' && 'toJSON' in poi ? (poi as any).toJSON() : poi
      ),
    }
  }
  /**
   * Deserializes a Region from a plain object.
   */
  static fromJSON(obj: Any): \'Region\' {
    if (!obj || typeof obj !== 'object') throw new Error('Invalid Region JSON')
    return new Region({
      id: obj.id,
      name: obj.name,
      boundaries: obj.boundaries,
      style: obj.style,
      highlightState: obj.highlightState,
      pois: Array.isArray(obj.pois) ? obj.pois : [],
    })
  }
}
/**
 * Simple Quadtree-based spatial index for Region bounding boxes.
 */
class RegionSpatialIndex {
  private items: List[Region] = []
  /**
   * Insert a region into the index.
   */
  insert(region: Region) {
    this.items.push(region)
  }
  /**
   * Remove a region from the index by id.
   */
  remove(regionId: str) {
    this.items = this.items.filter(r => r.id !== regionId)
  }
  /**
   * Query regions whose bounding boxes intersect a given bounding box.
   */
  queryBox(bbox: [[number, number], [number, number]]): Region[] {
    const [[minLng, minLat], [maxLng, maxLat]] = bbox
    return this.items.filter(region => {
      const [[rMinLng, rMinLat], [rMaxLng, rMaxLat]] = region.getBoundingBox()
      return rMinLng <= maxLng && rMaxLng >= minLng && rMinLat <= maxLat && rMaxLat >= minLat
    })
  }
  /**
   * Query regions containing a given point.
   */
  queryPoint(point: [number, number]): Region[] {
    return this.items.filter(region => region.containsPoint(point))
  }
  /**
   * Get all regions in the index.
   */
  getAll(): Region[] {
    return this.items.slice()
  }
}