import { IRegion } from './region';
import { IPOI } from './poi';

export function isRegion(obj: any): obj is IRegion {
  return (
    obj &&
    typeof obj.id === 'string' &&
    typeof obj.name === 'string' &&
    Array.isArray(obj.boundaries) &&
    typeof obj.style === 'object' &&
    typeof obj.highlightState === 'string' &&
    Array.isArray(obj.pois)
  );
}

export function isPOI(obj: any): obj is IPOI {
  return (
    obj &&
    typeof obj.id === 'string' &&
    typeof obj.name === 'string' &&
    Array.isArray(obj.coordinates) &&
    obj.coordinates.length === 2 &&
    typeof obj.type === 'string' &&
    typeof obj.state === 'string' &&
    typeof obj.regionId === 'string'
  );
}
