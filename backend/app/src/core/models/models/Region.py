from typing import Any, Dict, List


class Region implements IRegion {
  private _id: str
  private _name: str
  private _boundaries: [number, number][][]
  private _style: Dict[str, Any]
  private _highlightState: 'normal' | 'hover' | 'selected' | 'disabled'
  private _pois: List[IPOI]
  constructor(
    id: str,
    name: str,
    boundaries: [number, number][][],
    style?: {
      fillColor?: str
      strokeColor?: str
      strokeWidth?: float
      opacity?: float
    }
  ) {
    this._id = id
    this._name = name
    this._boundaries = boundaries
    this._style = style || {
      fillColor: '#3388ff',
      strokeColor: '#3388ff',
      strokeWidth: 2,
      opacity: 0.5,
    }
    this._highlightState = 'normal'
    this._pois = []
  }
  get id() {
    return this._id
  }
  get name() {
    return this._name
  }
  get boundaries() {
    return this._boundaries
  }
  get style() {
    return this._style
  }
  get highlightState() {
    return this._highlightState
  }
  get pois() {
    return this._pois
  }
  set highlightState(state: 'normal' | 'hover' | 'selected' | 'disabled') {
    this._highlightState = state
  }
  addPOI(poi: IPOI): void {
    if (!this._pois.find(p => p.id === poi.id)) {
      this._pois.push(poi)
    }
  }
  removePOI(poiId: str): void {
    this._pois = this._pois.filter(p => p.id !== poiId)
  }
  containsPoint(point: [number, number]): bool {
    let inside = false
    const x = point[0]
    const y = point[1]
    for (const polygon of this._boundaries) {
      for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
        const xi = polygon[i][0],
          yi = polygon[i][1]
        const xj = polygon[j][0],
          yj = polygon[j][1]
        const intersect = yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi
        if (intersect) inside = !inside
      }
    }
    return inside
  }
  getBoundingBox(): [[number, number], [number, number]] {
    let minLng = Infinity,
      minLat = Infinity,
      maxLng = -Infinity,
      maxLat = -Infinity
    for (const polygon of this._boundaries) {
      for (const point of polygon) {
        minLng = Math.min(minLng, point[0])
        minLat = Math.min(minLat, point[1])
        maxLng = Math.max(maxLng, point[0])
        maxLat = Math.max(maxLat, point[1])
      }
    }
    return [
      [minLng, minLat],
      [maxLng, maxLat],
    ]
  }
  getArea(): float {
    let totalArea = 0
    for (const polygon of this._boundaries) {
      let area = 0
      for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
        area += (polygon[j][0] + polygon[i][0]) * (polygon[j][1] - polygon[i][1])
      }
      totalArea += Math.abs(area / 2)
    }
    return totalArea * 111319.9 * 111319.9
  }
  getCentroid(): [number, number] {
    let sumLng = 0,
      sumLat = 0,
      pointCount = 0
    for (const polygon of this._boundaries) {
      for (const point of polygon) {
        sumLng += point[0]
        sumLat += point[1]
        pointCount++
      }
    }
    return [sumLng / pointCount, sumLat / pointCount]
  }
  toJSON(): Record<string, any> {
    return {
      id: this._id,
      name: this._name,
      boundaries: this._boundaries,
      style: this._style,
      highlightState: this._highlightState,
      pois: this._pois.map(poi =>
        typeof (poi as any).toJSON === 'function' ? (poi as any).toJSON() : poi
      ),
    }
  }
  static fromJSON(data: Any): \'Region\' {
    if (!data || typeof data !== 'object')
      throw new Error('Invalid data for Region deserialization')
    if (typeof data.id !== 'string') throw new Error('Region id must be a string')
    if (typeof data.name !== 'string') throw new Error('Region name must be a string')
    if (!Array.isArray(data.boundaries)) throw new Error('Region boundaries must be an array')
    if (typeof data.style !== 'object') throw new Error('Region style must be an object')
    if (typeof data.highlightState !== 'string')
      throw new Error('Region highlightState must be a string')
    const region = new Region(data.id, data.name, data.boundaries, data.style)
    region.highlightState = data.highlightState
    if (Array.isArray(data.pois)) {
      data.pois.forEach((poiData: Any) => {
        if (
          typeof poiData === 'object' &&
          typeof poiData.id === 'string' &&
          typeof poiData.coordinates === 'object'
        ) {
          const POI = require('./POI').POI
          region.addPOI(POI.fromJSON(poiData))
        }
      })
    }
    return region
  }
}