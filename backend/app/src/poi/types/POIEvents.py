from typing import Any, List


/**
 * Interface defining all POI-related events and their payload types
 */
class POIEvents:
    'poi: created': { poi: IPOI
  'poi:registered': { poi: IPOI }
  'poi:deregistered': { poiId: str }
  'poi:modified': { poiId: str; poi: IPOI }
  'poi:deleted': { poiId: str }
  'poi:activated': { poiId: str; poi: IPOI }
  'poi:deactivated': { poiId: str; poi: IPOI }
  'poi:discovered': { poiId: str; poi: IPOI }
  'poi:explored': { poiId: str; poi: IPOI }
  'poi:stateSaved': { poiId: str; state: Record<string, unknown> }
  'poi:parentSet': { childId: str; parentId: str }
  'poi:parentRemoved': { childId: str; previousParentId: str }
  'poi:dependencyAdded': { poiId: str; dependencyId: str }
  'poi:dependencyRemoved': { poiId: str; dependencyId: str }
  'poi:moved': { poiId: str; oldPosition: Coordinates; newPosition: Coordinates }
  'poi:entered': { poiId: str; actorId: str }
  'poi:exited': { poiId: str; actorId: str }
  'poi:searched': { 
    center: Coordinates
    radius: float
    type?: POIType
    subType?: POISubtype
    results: List[IPOI]
  }
  'poi:error': { 
    type: 'validation' | 'registration' | 'deregistration' | 'modification' | 'query'
    poiId?: str
    error: Error
  }
} 