from typing import Any



class POI implements IPOI {
  private _id: str
  private _name: str
  private _coordinates: [number, number]
  private _type: str
  private _state: 'active' | 'inactive'
  private _regionId: str
  private _metadata?: Record<string, any>
  constructor(
    id: str,
    name: str,
    coordinates: [number, number],
    type: str,
    regionId: str,
    state: 'active' | 'inactive' = 'inactive',
    metadata?: Record<string, any>
  ) {
    this.validateCoordinates(coordinates)
    this._id = id
    this._name = name
    this._coordinates = coordinates
    this._type = type
    this._state = state
    this._regionId = regionId
    this._metadata = metadata
  }
  get id(): str {
    return this._id
  }
  get name(): str {
    return this._name
  }
  get coordinates(): [number, number] {
    return [...this._coordinates]
  }
  get type(): str {
    return this._type
  }
  get state(): 'active' | 'inactive' {
    return this._state
  }
  get regionId(): str {
    return this._regionId
  }
  get metadata(): Record<string, any> | undefined {
    return this._metadata ? { ...this._metadata } : undefined
  }
  setState(newState: 'active' | 'inactive'): void {
    this._state = newState
  }
  setType(newType: str): void {
    this._type = newType
  }
  setMetadata(newMetadata: Record<string, any>): void {
    this._metadata = newMetadata
  }
  distanceTo(point: [number, number] | IPOI): float {
    const targetCoords = Array.isArray(point) ? point : point.coordinates
    return this.calculateHaversineDistance(this._coordinates, targetCoords)
  }
  getDisplayInfo(): { title: str; description?: str; iconUrl?: str } {
    return {
      title: this._name,
      description: this._metadata?.description,
      iconUrl: this._metadata?.iconUrl,
    }
  }
  private validateCoordinates(coords: [number, number]): void {
    const [longitude, latitude] = coords
    if (longitude < -180 || longitude > 180) {
      throw new Error(`Invalid longitude value: ${longitude}. Must be between -180 and 180.`)
    }
    if (latitude < -90 || latitude > 90) {
      throw new Error(`Invalid latitude value: ${latitude}. Must be between -90 and 90.`)
    }
  }
  private calculateHaversineDistance(coords1: [number, number], coords2: [number, number]): float {
    const [lon1, lat1] = coords1
    const [lon2, lat2] = coords2
    const R = 6371000 
    const φ1 = (lat1 * Math.PI) / 180
    const φ2 = (lat2 * Math.PI) / 180
    const Δφ = ((lat2 - lat1) * Math.PI) / 180
    const Δλ = ((lon2 - lon1) * Math.PI) / 180
    const a =
      Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
      Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    return R * c
  }
  toJSON(): Record<string, any> {
    return {
      id: this._id,
      name: this._name,
      coordinates: this._coordinates,
      type: this._type,
      state: this._state,
      regionId: this._regionId,
      metadata: this._metadata,
    }
  }
  static fromJSON(data: Record<string, any>): \'POI\' {
    return new POI(
      data.id,
      data.name,
      data.coordinates,
      data.type,
      data.regionId,
      data.state || 'inactive',
      data.metadata
    )
  }
}