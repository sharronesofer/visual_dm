"""Services for poi system - Pure Business Logic"""

# Import business logic services
from .services import (
    PoiData,
    CreatePoiData,
    UpdatePoiData,
    PoiRepository,
    PoiValidationService,
    PoiBusinessService,
    create_poi_business_service
)
from .poi_state_service import (
    POIStateBusinessService,
    StateTransitionValidator,
    StateTransitionRule,
    StateTransitionEvent,
    POIState,
    POIType,
    POIStateData,
    POIRepository as StateRepository,
    StateTransitionConfigService,
    EventDispatcher,
    create_poi_state_business_service
)
from .metropolitan_spread_service import (
    MetropolitanSpreadService,
    MetropolitanArea,
    UrbanSize,
    HexCoordinate,
    get_metropolitan_spread_service
)
from .resource_management_service import (
    ResourceManagementService,
    ResourceType,
    ResourceCategory,
    ResourceStock,
    ProductionCapability,
    TradeOffer,
    get_resource_management_service
)
from .migration_service import (
    MigrationService,
    MigrationGroup,
    MigrationType,
    MigrationTrigger,
    MigrationStatus,
    PopulationDemographics,
    get_migration_service
)
from .lifecycle_events_service import (
    LifecycleEventsService,
    LifecycleEventType,
    LifecycleEvent,
    EventTemplate,
    EventSeverity,
    EventFrequency,
    POILifecycleData,
    get_lifecycle_events_service
)
from .faction_influence_service import (
    FactionInfluenceService,
    InfluenceType,
    InfluenceAction,
    FactionInfluence,
    ControlLevel,
    Faction,
    FactionRelation,
    FactionRelationship,
    InfluenceEvent,
    get_faction_influence_service
)
from .landmark_service import (
    LandmarkService,
    LandmarkType,
    LandmarkRarity,
    LandmarkFeature,
    Landmark,
    LandmarkStatus,
    LandmarkEffect,
    LandmarkQuest,
    get_landmark_service
)
from .event_integration_service import (
    EventIntegrationService,
    POIEventType,
    EventPriority,
    POIEvent,
    EventSubscription,
    publish_event_on_method,
    get_event_integration_service
)

# Import technical services from infrastructure
from backend.infrastructure.poi_generators import (
    POIGenerator,
    GenerationType,
    BiomeType,
    GenerationRule,
    WorldCell,
    GenerationParameters,
    get_poi_generator
)
from backend.infrastructure.poi_integrations import (
    UnityFrontendIntegration,
    UnityMessageType,
    UnityUpdateFrequency,
    UnityPOIModel,
    UnitySystemStatus,
    UnityEventNotification,
    get_unity_frontend_integration
)
from backend.infrastructure.tilemap_generators import (
    TilemapService,
    TileType,
    RoomType,
    Tile,
    Room,
    Tilemap,
    get_tilemap_service
)

__all__ = [
    # Core business services
    "PoiData",
    "CreatePoiData", 
    "UpdatePoiData",
    "PoiRepository",
    "PoiValidationService",
    "PoiBusinessService",
    "create_poi_business_service",
    
    # State management business services
    "POIStateBusinessService",
    "StateTransitionValidator", 
    "StateTransitionRule",
    "StateTransitionEvent",
    "POIState",
    "POIType",
    "POIStateData",
    "StateRepository",
    "StateTransitionConfigService",
    "EventDispatcher",
    "create_poi_state_business_service",
    
    # Other business services
    "MetropolitanSpreadService",
    "MetropolitanArea",
    "UrbanSize",
    "HexCoordinate",
    "get_metropolitan_spread_service",
    "ResourceManagementService",
    "ResourceType",
    "ResourceCategory",
    "ResourceStock",
    "ProductionCapability",
    "TradeOffer",
    "get_resource_management_service",
    "MigrationService",
    "MigrationGroup",
    "MigrationType",
    "MigrationTrigger",
    "MigrationStatus",
    "PopulationDemographics",
    "get_migration_service",
    "LifecycleEventsService",
    "LifecycleEventType",
    "LifecycleEvent",
    "EventTemplate",
    "EventSeverity",
    "EventFrequency",
    "POILifecycleData",
    "get_lifecycle_events_service",
    "FactionInfluenceService",
    "InfluenceType",
    "InfluenceAction",
    "FactionInfluence",
    "ControlLevel",
    "Faction",
    "FactionRelation",
    "FactionRelationship",
    "InfluenceEvent",
    "get_faction_influence_service",
    "LandmarkService",
    "LandmarkType",
    "LandmarkRarity",
    "LandmarkFeature",
    "Landmark",
    "LandmarkStatus",
    "LandmarkEffect",
    "LandmarkQuest",
    "get_landmark_service",
    "EventIntegrationService",
    "POIEventType",
    "EventPriority",
    "POIEvent",
    "EventSubscription",
    "publish_event_on_method",
    "get_event_integration_service",
    
    # Technical services (from infrastructure)
    "POIGenerator",
    "GenerationType",
    "BiomeType",
    "GenerationRule",
    "WorldCell",
    "GenerationParameters",
    "get_poi_generator",
    "UnityFrontendIntegration",
    "UnityMessageType",
    "UnityUpdateFrequency",
    "UnityPOIModel",
    "UnitySystemStatus",
    "UnityEventNotification",
    "get_unity_frontend_integration",
    "TilemapService",
    "TileType",
    "RoomType",
    "Tile",
    "Room",
    "Tilemap",
    "get_tilemap_service"
]
