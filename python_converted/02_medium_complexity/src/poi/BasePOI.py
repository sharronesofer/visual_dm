from typing import Any



class BasePOI implements IPOI {
  public id: str
  public type: POIType
  public subtype: POISubtype
  public position: Coordinates
  public size: POISize
  public name: str
  public description?: str
  public properties: Record<string, unknown>
  constructor(
    id: str,
    type: POIType,
    subtype: POISubtype,
    position: Coordinates,
    size: POISize,
    name: str,
    description?: str
  ) {
    this.id = id
    this.type = type
    this.subtype = subtype
    this.position = position
    this.size = size
    this.name = name
    this.description = description
    this.properties = {}
  }
  public setPosition(position: Coordinates): void {
    this.position = position
  }
  public getPosition(): Coordinates {
    return this.position
  }
  public setSize(size: POISize): void {
    this.size = size
  }
  public getSize(): POISize {
    return this.size
  }
  public getType(): POIType {
    return this.type
  }
  public getSubtype(): POISubtype {
    return this.subtype
  }
  public setProperty(key: str, value: unknown): void {
    this.properties[key] = value
  }
  public getProperty<T>(key: str): T | undefined {
    return this.properties[key] as T
  }
  public hasProperty(key: str): bool {
    return key in this.properties
  }
} 