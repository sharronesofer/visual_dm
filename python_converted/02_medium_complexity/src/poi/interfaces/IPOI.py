from typing import Any, Dict, List, Union



/**
 * Interface for all Point of Interest (POI) objects
 *
 * - id: Unique identifier for the POI
 * - type: Main POI category (see POIType enum)
 * - subtype: Specific POI subtype (see POISubtype enum)
 * - position: 3D coordinates in the world
 * - size: Physical size of the POI
 * - name: Human-readable name
 * - description: Optional description
 * - properties: Arbitrary key-value pairs for extensibility
 * - thematicElements: Thematic/environmental attributes
 * - stateTracking: Persistence and change history
 * - connections: List of connected POI IDs
 *
 * Methods provide validation, serialization, state, connection, and property management.
 */
class IPOI:
    id: str
    type: POIType
    subtype: POISubtype
    position: Coordinates
    size: POISize
    name: str
    description?: str
    properties: Dict[str, unknown>
    thematicElements: ThematicElements
    stateTracking: StateTracking
    connections: List[str]
    validate(): bool
    serialize(): Dict[str, unknown>
    deserialize(data: Dict[str, unknown>): None
    getStateTracking(): StateTracking
    updateStateTracking(details: Union[str, type: 'modification', 'expansion'): None]
    addConnection(poiId: str): None
    removeConnection(poiId: str): None
    getConnections(): List[str]
    setCoordinates(coordinates: Coordinates): None
    getCoordinates(): Coordinates
    setThematicElements(elements: ThematicElements): None
    getThematicElements(): ThematicElements
    setPosition(position: Coordinates): None
    getPosition(): Coordinates
    setSize(size: POISize): None
    getSize(): POISize
    getType(): POIType
    getSubtype(): POISubtype
    setProperty(key: str, value: unknown): None
    getProperty<T>(key: Union[str): T, None]
    hasProperty(key: str): bool 