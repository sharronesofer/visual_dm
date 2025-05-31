"""
Unity Frontend Integration Service

Handles comprehensive Unity frontend integration, model synchronization,
and real-time updates for the POI system.
"""

from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass, field, asdict
import logging
from datetime import datetime
import json
import asyncio

from backend.systems.poi.models import PoiEntity, POIType, POIState
from backend.infrastructure.database import get_db
from backend.infrastructure.events import EventDispatcher
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class UnityMessageType(str, Enum):
    """Types of messages sent to Unity frontend"""
    POI_UPDATE = "poi_update"
    POI_CREATE = "poi_create"
    POI_DELETE = "poi_delete"
    BULK_UPDATE = "bulk_update"
    EVENT_NOTIFICATION = "event_notification"
    SYSTEM_STATUS = "system_status"
    REALTIME_DATA = "realtime_data"
    UI_UPDATE = "ui_update"


class UnityUpdateFrequency(str, Enum):
    """Update frequency for different data types"""
    REALTIME = "realtime"       # Immediate updates
    HIGH = "high"               # Every 1-5 seconds
    MEDIUM = "medium"           # Every 10-30 seconds
    LOW = "low"                 # Every 1-5 minutes
    BATCH = "batch"             # Batched periodic updates


@dataclass
class UnityPOIModel:
    """Unity-compatible POI model with enhanced data"""
    id: str
    name: str
    poi_type: str
    state: str
    location: Tuple[float, float]  # x, y coordinates
    
    # Basic properties
    population: int = 0
    max_population: int = 0
    prosperity_level: float = 0.0
    happiness: float = 0.5
    
    # Visual properties
    size_scale: float = 1.0
    color_tint: str = "#FFFFFF"
    icon_type: str = "default"
    animation_state: str = "idle"
    effect_particles: List[str] = field(default_factory=list)
    
    # Economic data
    resources: Dict[str, int] = field(default_factory=dict)
    trade_routes: List[str] = field(default_factory=list)
    economic_status: str = "stable"
    
    # Political/Faction data
    controlling_faction: Optional[str] = None
    faction_influences: Dict[str, float] = field(default_factory=dict)
    political_stability: float = 0.5
    
    # Environmental data
    biome: str = "grassland"
    elevation: float = 0.5
    climate_effects: List[str] = field(default_factory=list)
    
    # Metropolitan data
    metropolitan_area_id: Optional[str] = None
    urban_density: float = 0.0
    infrastructure_level: float = 0.0
    
    # Event data
    active_events: List[Dict[str, Any]] = field(default_factory=list)
    recent_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # UI/UX data
    tooltip_data: Dict[str, Any] = field(default_factory=dict)
    interaction_options: List[str] = field(default_factory=list)
    notification_badges: List[str] = field(default_factory=list)
    
    # Timestamps
    last_updated: str = ""
    created_at: str = ""
    
    def to_unity_json(self) -> str:
        """Convert to Unity-compatible JSON"""
        data = asdict(self)
        data['location'] = {'x': self.location[0], 'y': self.location[1]}
        return json.dumps(data, default=str)


@dataclass
class UnitySystemStatus:
    """System status information for Unity"""
    poi_count: int = 0
    active_events: int = 0
    total_population: int = 0
    economic_health: float = 0.5
    political_stability: float = 0.5
    simulation_speed: float = 1.0
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    last_update: str = ""


@dataclass
class UnityEventNotification:
    """Event notification for Unity UI"""
    event_id: str
    event_type: str
    priority: str
    title: str
    message: str
    poi_id: Optional[str] = None
    icon: str = "info"
    duration: float = 5.0  # seconds to display
    timestamp: str = ""
    action_buttons: List[Dict[str, str]] = field(default_factory=list)


class UnityFrontendIntegration:
    """Service for Unity frontend integration and real-time updates"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or get_db()
        self.event_dispatcher = EventDispatcher()
        
        # Unity connection management
        self.connected_clients: Dict[str, Dict[str, Any]] = {}
        self.update_queues: Dict[str, asyncio.Queue] = {}
        
        # Data synchronization
        self.poi_models_cache: Dict[UUID, UnityPOIModel] = {}
        self.pending_updates: Dict[UUID, Dict[str, Any]] = {}
        self.last_sync_time: datetime = datetime.utcnow()
        
        # Update frequency management
        self.update_frequencies: Dict[str, UnityUpdateFrequency] = {
            'poi_population': UnityUpdateFrequency.MEDIUM,
            'poi_resources': UnityUpdateFrequency.LOW,
            'poi_events': UnityUpdateFrequency.REALTIME,
            'faction_influence': UnityUpdateFrequency.MEDIUM,
            'system_status': UnityUpdateFrequency.HIGH,
            'ui_notifications': UnityUpdateFrequency.REALTIME
        }
        
        # Performance tracking
        self.messages_sent = 0
        self.update_performance: Dict[str, float] = {}
        
        # Initialize event subscriptions
        self._initialize_event_subscriptions()
    
    def _initialize_event_subscriptions(self):
        """Subscribe to POI system events for Unity updates"""
        # Subscribe to POI events via event dispatcher
        self.event_dispatcher.subscribe('poi_created', self._handle_poi_created)
        self.event_dispatcher.subscribe('poi_updated', self._handle_poi_updated)
        self.event_dispatcher.subscribe('poi_deleted', self._handle_poi_deleted)
        self.event_dispatcher.subscribe('population_changed', self._handle_population_changed)
        self.event_dispatcher.subscribe('resource_production', self._handle_resource_event)
        self.event_dispatcher.subscribe('influence_changed', self._handle_influence_changed)
        self.event_dispatcher.subscribe('disaster_event', self._handle_disaster_event)
    
    def register_unity_client(self, client_id: str, client_info: Dict[str, Any]) -> bool:
        """Register a Unity client for updates"""
        try:
            self.connected_clients[client_id] = {
                'info': client_info,
                'connected_at': datetime.utcnow(),
                'last_ping': datetime.utcnow(),
                'subscriptions': set(),
                'update_preferences': {}
            }
            
            # Create update queue for this client
            self.update_queues[client_id] = asyncio.Queue()
            
            logger.info(f"Unity client {client_id} registered")
            
            # Send initial data sync
            self._send_initial_sync(client_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error registering Unity client: {e}")
            return False
    
    def unregister_unity_client(self, client_id: str) -> bool:
        """Unregister a Unity client"""
        try:
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
            
            if client_id in self.update_queues:
                del self.update_queues[client_id]
            
            logger.info(f"Unity client {client_id} unregistered")
            return True
            
        except Exception as e:
            logger.error(f"Error unregistering Unity client: {e}")
            return False
    
    def convert_poi_to_unity_model(self, poi: PoiEntity) -> UnityPOIModel:
        """Convert POI entity to Unity-compatible model"""
        try:
            # Calculate visual properties
            size_scale = self._calculate_poi_size_scale(poi)
            color_tint = self._determine_poi_color(poi)
            icon_type = self._get_poi_icon_type(poi)
            animation_state = self._determine_animation_state(poi)
            
            # Calculate derived metrics
            prosperity_level = self._calculate_prosperity(poi)
            happiness = self._calculate_happiness(poi)
            
            # Get tooltip data
            tooltip_data = self._generate_tooltip_data(poi)
            
            # Get interaction options
            interaction_options = self._get_interaction_options(poi)
            
            unity_model = UnityPOIModel(
                id=str(poi.id),
                name=poi.name,
                poi_type=poi.poi_type,
                state=poi.state,
                location=(poi.location_x or 0, poi.location_y or 0),
                population=poi.population or 0,
                max_population=poi.max_population or 0,
                prosperity_level=prosperity_level,
                happiness=happiness,
                size_scale=size_scale,
                color_tint=color_tint,
                icon_type=icon_type,
                animation_state=animation_state,
                resources=poi.resources or {},
                tooltip_data=tooltip_data,
                interaction_options=interaction_options,
                last_updated=datetime.utcnow().isoformat(),
                created_at=poi.created_at.isoformat() if poi.created_at else ""
            )
            
            # Add to cache
            self.poi_models_cache[poi.id] = unity_model
            
            return unity_model
            
        except Exception as e:
            logger.error(f"Error converting POI to Unity model: {e}")
            return None
    
    def sync_all_pois(self) -> List[UnityPOIModel]:
        """Sync all POIs to Unity format"""
        try:
            pois = self.db_session.query(PoiEntity).all()
            unity_models = []
            
            for poi in pois:
                unity_model = self.convert_poi_to_unity_model(poi)
                if unity_model:
                    unity_models.append(unity_model)
            
            # Send bulk update to all clients
            self._send_bulk_update_to_all_clients(unity_models)
            
            self.last_sync_time = datetime.utcnow()
            logger.info(f"Synced {len(unity_models)} POIs to Unity")
            
            return unity_models
            
        except Exception as e:
            logger.error(f"Error syncing POIs: {e}")
            return []
    
    def send_realtime_update(self, poi_id: UUID, update_data: Dict[str, Any]) -> bool:
        """Send real-time update for a specific POI"""
        try:
            if poi_id in self.poi_models_cache:
                unity_model = self.poi_models_cache[poi_id]
                
                # Update model with new data
                for key, value in update_data.items():
                    if hasattr(unity_model, key):
                        setattr(unity_model, key, value)
                
                unity_model.last_updated = datetime.utcnow().isoformat()
                
                # Send to all connected clients
                message = {
                    'type': UnityMessageType.POI_UPDATE.value,
                    'poi_id': str(poi_id),
                    'data': asdict(unity_model),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                self._broadcast_message(message)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending realtime update: {e}")
            return False
    
    def send_event_notification(self, event_data: Dict[str, Any]) -> bool:
        """Send event notification to Unity UI"""
        try:
            notification = UnityEventNotification(
                event_id=event_data.get('event_id', str(uuid4())),
                event_type=event_data.get('event_type', 'info'),
                priority=event_data.get('priority', 'medium'),
                title=event_data.get('title', 'POI Event'),
                message=event_data.get('message', ''),
                poi_id=event_data.get('poi_id'),
                icon=self._get_event_icon(event_data.get('event_type', 'info')),
                duration=event_data.get('duration', 5.0),
                timestamp=datetime.utcnow().isoformat()
            )
            
            message = {
                'type': UnityMessageType.EVENT_NOTIFICATION.value,
                'notification': asdict(notification),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self._broadcast_message(message)
            return True
            
        except Exception as e:
            logger.error(f"Error sending event notification: {e}")
            return False
    
    def update_system_status(self) -> bool:
        """Update and send system status to Unity"""
        try:
            # Calculate system metrics
            total_pois = self.db_session.query(PoiEntity).count()
            total_population = self.db_session.query(PoiEntity).with_entities(
                PoiEntity.population
            ).scalar() or 0
            
            # Calculate health metrics
            economic_health = self._calculate_global_economic_health()
            political_stability = self._calculate_global_political_stability()
            
            status = UnitySystemStatus(
                poi_count=total_pois,
                total_population=total_population,
                economic_health=economic_health,
                political_stability=political_stability,
                last_update=datetime.utcnow().isoformat()
            )
            
            message = {
                'type': UnityMessageType.SYSTEM_STATUS.value,
                'status': asdict(status),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self._broadcast_message(message)
            return True
            
        except Exception as e:
            logger.error(f"Error updating system status: {e}")
            return False
    
    def get_unity_client_status(self) -> Dict[str, Any]:
        """Get status of Unity client connections"""
        return {
            'connected_clients': len(self.connected_clients),
            'client_details': {
                client_id: {
                    'connected_at': info['connected_at'].isoformat(),
                    'last_ping': info['last_ping'].isoformat(),
                    'subscriptions': list(info['subscriptions'])
                }
                for client_id, info in self.connected_clients.items()
            },
            'messages_sent': self.messages_sent,
            'cached_models': len(self.poi_models_cache),
            'last_sync': self.last_sync_time.isoformat()
        }
    
    def _send_initial_sync(self, client_id: str):
        """Send initial data sync to a new client"""
        try:
            # Send all POI models
            unity_models = [model for model in self.poi_models_cache.values()]
            
            message = {
                'type': UnityMessageType.BULK_UPDATE.value,
                'pois': [asdict(model) for model in unity_models],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self._send_message_to_client(client_id, message)
            
            # Send system status
            self.update_system_status()
            
        except Exception as e:
            logger.error(f"Error sending initial sync: {e}")
    
    def _broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected Unity clients"""
        for client_id in self.connected_clients.keys():
            self._send_message_to_client(client_id, message)
        
        self.messages_sent += 1
    
    def _send_message_to_client(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific Unity client"""
        try:
            if client_id in self.update_queues:
                # In a real implementation, this would send via WebSocket, TCP, or Unity-specific protocol
                logger.debug(f"Sending message to Unity client {client_id}: {message['type']}")
                
                # For now, we'll simulate by putting in queue
                # self.update_queues[client_id].put_nowait(message)
                
        except Exception as e:
            logger.error(f"Error sending message to client {client_id}: {e}")
    
    def _send_bulk_update_to_all_clients(self, unity_models: List[UnityPOIModel]):
        """Send bulk update to all clients"""
        message = {
            'type': UnityMessageType.BULK_UPDATE.value,
            'pois': [asdict(model) for model in unity_models],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self._broadcast_message(message)
    
    def _calculate_poi_size_scale(self, poi: PoiEntity) -> float:
        """Calculate visual size scale for POI based on population and type"""
        base_scales = {
            'city': 2.0,
            'town': 1.5,
            'village': 1.0,
            'fortress': 1.8,
            'market': 1.2,
            'temple': 1.3,
            'mine': 1.1
        }
        
        base_scale = base_scales.get(poi.poi_type, 1.0)
        
        # Scale by population
        if poi.population and poi.population > 0:
            population_factor = min(2.0, 1.0 + (poi.population / 10000))
            return base_scale * population_factor
        
        return base_scale
    
    def _determine_poi_color(self, poi: PoiEntity) -> str:
        """Determine color tint for POI based on state and properties"""
        state_colors = {
            'growing': '#00FF00',      # Green
            'stable': '#FFFFFF',       # White
            'declining': '#FF8800',    # Orange
            'abandoned': '#666666',    # Gray
            'ruined': '#330000'        # Dark red
        }
        
        return state_colors.get(poi.state, '#FFFFFF')
    
    def _get_poi_icon_type(self, poi: PoiEntity) -> str:
        """Get icon type for POI"""
        icon_mapping = {
            'city': 'city_icon',
            'town': 'town_icon',
            'village': 'village_icon',
            'fortress': 'fortress_icon',
            'market': 'market_icon',
            'temple': 'temple_icon',
            'mine': 'mine_icon'
        }
        
        return icon_mapping.get(poi.poi_type, 'default_icon')
    
    def _determine_animation_state(self, poi: PoiEntity) -> str:
        """Determine animation state for POI"""
        if poi.state == 'growing':
            return 'growing'
        elif poi.state == 'declining':
            return 'declining'
        elif poi.state == 'abandoned':
            return 'abandoned'
        else:
            return 'idle'
    
    def _calculate_prosperity(self, poi: PoiEntity) -> float:
        """Calculate prosperity level (0.0 to 1.0)"""
        # Simplified calculation based on population and resources
        population_factor = min(1.0, (poi.population or 0) / 1000)
        resource_factor = len(poi.resources or {}) / 10.0
        
        return min(1.0, (population_factor + resource_factor) / 2.0)
    
    def _calculate_happiness(self, poi: PoiEntity) -> float:
        """Calculate happiness level (0.0 to 1.0)"""
        # Simplified calculation - in real implementation would consider many factors
        state_happiness = {
            'growing': 0.8,
            'stable': 0.6,
            'declining': 0.3,
            'abandoned': 0.1,
            'ruined': 0.0
        }
        
        return state_happiness.get(poi.state, 0.5)
    
    def _generate_tooltip_data(self, poi: PoiEntity) -> Dict[str, Any]:
        """Generate tooltip data for Unity UI"""
        return {
            'name': poi.name,
            'type': poi.poi_type,
            'population': poi.population or 0,
            'state': poi.state,
            'description': poi.description or '',
            'resources': list((poi.resources or {}).keys()),
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def _get_interaction_options(self, poi: PoiEntity) -> List[str]:
        """Get available interaction options for POI"""
        options = ['view_details', 'view_history']
        
        if poi.poi_type in ['city', 'town', 'village']:
            options.extend(['trade', 'diplomacy'])
        
        if poi.poi_type == 'fortress':
            options.append('military_orders')
        
        if poi.poi_type == 'temple':
            options.append('religious_services')
        
        return options
    
    def _get_event_icon(self, event_type: str) -> str:
        """Get icon for event notification"""
        icon_mapping = {
            'disaster': 'warning',
            'trade': 'commerce',
            'diplomacy': 'handshake',
            'military': 'sword',
            'economic': 'coin',
            'population': 'people',
            'construction': 'hammer'
        }
        
        return icon_mapping.get(event_type, 'info')
    
    def _calculate_global_economic_health(self) -> float:
        """Calculate global economic health metric"""
        # Simplified calculation - would be more complex in real implementation
        return 0.7  # Placeholder
    
    def _calculate_global_political_stability(self) -> float:
        """Calculate global political stability metric"""
        # Simplified calculation - would be more complex in real implementation
        return 0.6  # Placeholder
    
    # Event handlers
    def _handle_poi_created(self, event_data: Dict[str, Any]):
        """Handle POI creation event"""
        poi_id = event_data.get('poi_id')
        if poi_id:
            # Fetch POI and convert to Unity model
            poi = self.db_session.query(PoiEntity).filter_by(id=poi_id).first()
            if poi:
                unity_model = self.convert_poi_to_unity_model(poi)
                if unity_model:
                    message = {
                        'type': UnityMessageType.POI_CREATE.value,
                        'poi': asdict(unity_model),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    self._broadcast_message(message)
    
    def _handle_poi_updated(self, event_data: Dict[str, Any]):
        """Handle POI update event"""
        poi_id = event_data.get('poi_id')
        changed_fields = event_data.get('changed_fields', [])
        
        if poi_id:
            self.send_realtime_update(UUID(poi_id), {'changed_fields': changed_fields})
    
    def _handle_poi_deleted(self, event_data: Dict[str, Any]):
        """Handle POI deletion event"""
        poi_id = event_data.get('poi_id')
        if poi_id:
            # Remove from cache
            if UUID(poi_id) in self.poi_models_cache:
                del self.poi_models_cache[UUID(poi_id)]
            
            message = {
                'type': UnityMessageType.POI_DELETE.value,
                'poi_id': poi_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            self._broadcast_message(message)
    
    def _handle_population_changed(self, event_data: Dict[str, Any]):
        """Handle population change event"""
        poi_id = event_data.get('poi_id')
        new_population = event_data.get('new_population')
        
        if poi_id and new_population is not None:
            self.send_realtime_update(UUID(poi_id), {'population': new_population})
            
            # Send notification for significant changes
            change_percentage = event_data.get('change_percentage', 0)
            if abs(change_percentage) > 20:
                self.send_event_notification({
                    'event_type': 'population',
                    'title': 'Population Change',
                    'message': f"Population changed by {change_percentage:.1f}%",
                    'poi_id': poi_id,
                    'priority': 'medium'
                })
    
    def _handle_resource_event(self, event_data: Dict[str, Any]):
        """Handle resource event"""
        poi_id = event_data.get('poi_id')
        resource_type = event_data.get('resource_type')
        amount = event_data.get('amount')
        
        if poi_id:
            # Update resource display
            self.send_realtime_update(UUID(poi_id), {
                'resource_update': {
                    'type': resource_type,
                    'amount': amount
                }
            })
    
    def _handle_influence_changed(self, event_data: Dict[str, Any]):
        """Handle faction influence change event"""
        poi_id = event_data.get('poi_id')
        faction_id = event_data.get('faction_id')
        new_value = event_data.get('new_value')
        
        if poi_id and faction_id:
            self.send_realtime_update(UUID(poi_id), {
                'faction_influences': {faction_id: new_value}
            })
    
    def _handle_disaster_event(self, event_data: Dict[str, Any]):
        """Handle disaster event"""
        poi_id = event_data.get('poi_id')
        disaster_type = event_data.get('disaster_type')
        severity = event_data.get('severity', 0.0)
        
        if poi_id:
            # Send critical notification
            self.send_event_notification({
                'event_type': 'disaster',
                'title': f'{disaster_type.title()} Disaster',
                'message': f'Severity: {severity:.1f}',
                'poi_id': poi_id,
                'priority': 'critical',
                'duration': 10.0
            })
            
            # Update POI with disaster effects
            self.send_realtime_update(UUID(poi_id), {
                'active_events': [{'type': disaster_type, 'severity': severity}],
                'effect_particles': ['disaster_smoke', 'debris']
            })


# Factory function for dependency injection
def get_unity_frontend_integration(db_session: Optional[Session] = None) -> UnityFrontendIntegration:
    """Factory function to create UnityFrontendIntegration instance"""
    return UnityFrontendIntegration(db_session) 