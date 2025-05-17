import { IPOI } from '../interfaces/IPOI';
import { POIType, POISubtype, Coordinates } from './POITypes';

/**
 * Interface defining all POI-related events and their payload types
 */
export interface POIEvents {
  // Lifecycle events
  'poi:created': { poi: IPOI };
  'poi:registered': { poi: IPOI };
  'poi:deregistered': { poiId: string };
  'poi:modified': { poiId: string; poi: IPOI };
  'poi:deleted': { poiId: string };

  // State events
  'poi:activated': { poiId: string; poi: IPOI };
  'poi:deactivated': { poiId: string; poi: IPOI };
  'poi:discovered': { poiId: string; poi: IPOI };
  'poi:explored': { poiId: string; poi: IPOI };
  'poi:stateSaved': { poiId: string; state: Record<string, unknown> };

  // Relationship events
  'poi:parentSet': { childId: string; parentId: string };
  'poi:parentRemoved': { childId: string; previousParentId: string };
  'poi:dependencyAdded': { poiId: string; dependencyId: string };
  'poi:dependencyRemoved': { poiId: string; dependencyId: string };

  // Spatial events
  'poi:moved': { poiId: string; oldPosition: Coordinates; newPosition: Coordinates };
  'poi:entered': { poiId: string; actorId: string };
  'poi:exited': { poiId: string; actorId: string };

  // Query events
  'poi:searched': {
    center: Coordinates;
    radius: number;
    type?: POIType;
    subType?: POISubtype;
    results: IPOI[];
  };

  // Error events
  'poi:error': {
    type: 'validation' | 'registration' | 'deregistration' | 'modification' | 'query' | 'capture';
    poiId?: string;
    error: Error;
  };

  // Evolution events
  /**
   * Emitted when a POI evolves (e.g., state, thematic, or property change due to evolution rules)
   * @version 1
   */
  'poi:evolved': { poiId: string; poi: IPOI; trigger: string; changes: Partial<IPOI>; version: number };

  /**
   * Emitted when a POI is captured (ownership or control changes)
   * @version 1
   */
  'poi:captured': { poiId: string; poi: IPOI; captorId: string; previousOwnerId?: string; timestamp: number; version: number };

  /**
   * Emitted when a POI is destroyed (removed from the world, not just deactivated)
   * @version 1
   */
  'poi:destroyed': { poiId: string; poi: IPOI; reason: string; timestamp: number; version: number };
} 