import { IPOI } from './interfaces/IPOI';
import { POIType, POISubtype, Coordinates, POISize } from './types/POITypes';

export class BasePOI implements IPOI {
  public id: string;
  public type: POIType;
  public subtype: POISubtype;
  public position: Coordinates;
  public size: POISize;
  public name: string;
  public description?: string;
  public properties: Record<string, unknown>;

  constructor(
    id: string,
    type: POIType,
    subtype: POISubtype,
    position: Coordinates,
    size: POISize,
    name: string,
    description?: string
  ) {
    this.id = id;
    this.type = type;
    this.subtype = subtype;
    this.position = position;
    this.size = size;
    this.name = name;
    this.description = description;
    this.properties = {};
  }

  public setPosition(position: Coordinates): void {
    this.position = position;
  }

  public getPosition(): Coordinates {
    return this.position;
  }

  public setSize(size: POISize): void {
    this.size = size;
  }

  public getSize(): POISize {
    return this.size;
  }

  public getType(): POIType {
    return this.type;
  }

  public getSubtype(): POISubtype {
    return this.subtype;
  }

  public setProperty(key: string, value: unknown): void {
    this.properties[key] = value;
  }

  public getProperty<T>(key: string): T | undefined {
    return this.properties[key] as T;
  }

  public hasProperty(key: string): boolean {
    return key in this.properties;
  }
} 