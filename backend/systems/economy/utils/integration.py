"""
Economy System Integration - Complete integration layer for economy system.

This module provides integration between the economy system and other game systems
including event system, WebSocket communication, database management, and 
cross-system coordination.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from contextlib import asynccontextmanager

from backend.systems.economy.services.economy_manager import EconomyManager
from backend.systems.economy.events import (
    EconomyEventBus, 
    EconomyEventType, 
    EconomyEvent,
    ResourceEvent,
    MarketEvent,
    PriceEvent,
    TradeEvent,
    TransactionEvent,
    get_event_bus,
    publish_system_event
)
from backend.systems.economy.websocket_events import (
    EconomyWebSocketManager,
    notify_market_updated,
    notify_price_updated,
    notify_transaction_completed,
    notify_trade_route_updated,
    notify_economic_analytics,
    notify_economy_status
)
from backend.systems.economy.database_service import (
    EconomyDatabaseService,
    get_database_service,
    database_session
)
from backend.systems.economy.deployment import (
    EconomyDeploymentManager,
    DeploymentConfig,
    get_deployment_manager
)

logger = logging.getLogger(__name__)

class EconomyIntegrationManager:
    """
    Complete integration manager for the economy system.
    
    This class coordinates all economy subsystems and provides a unified
    interface for economy operations with full event handling, WebSocket
    integration, and database management.
    """
    
    _instance: Optional['EconomyIntegrationManager'] = None
    
    def __init__(self):
        """Initialize the economy integration manager."""
        if EconomyIntegrationManager._instance is not None:
            raise Exception("EconomyIntegrationManager is a singleton, use get_instance()")
        
        # Core components
        self.economy_manager: Optional[EconomyManager] = None
        self.event_bus: EconomyEventBus = get_event_bus()
        self.websocket_manager: EconomyWebSocketManager = EconomyWebSocketManager()
        self.database_service: EconomyDatabaseService = get_database_service()
        self.deployment_manager: Optional[EconomyDeploymentManager] = None
        
        # Integration state
        self.is_initialized = False
        self.is_running = False
        self.event_handlers_registered = False
        
        # Performance metrics
        self.metrics = {
            "events_processed": 0,
            "websocket_messages_sent": 0,
            "database_operations": 0,
            "errors_handled": 0,
            "last_tick_time": None,
            "average_response_time": 0.0
        }
        
        logger.info("Economy Integration Manager created")
    
    @classmethod
    def get_instance(cls) -> 'EconomyIntegrationManager':
        """Get the singleton instance of the integration manager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initialize the complete economy system integration.
        
        Args:
            config: Optional configuration dictionary
            
        Returns:
            Initialization status and details
        """
        try:
            logger.info("Initializing Economy Integration Manager...")
            
            # Initialize deployment manager
            deployment_config = DeploymentConfig.from_environment()
            if config:
                # Override with provided config
                for key, value in config.items():
                    if hasattr(deployment_config, key):
                        setattr(deployment_config, key, value)
            
            self.deployment_manager = get_deployment_manager(deployment_config)
            
            # Initialize database
            await self._initialize_database()
            
            # Initialize economy manager with database session
            async with database_session() as session:
                self.economy_manager = EconomyManager.get_instance(session)
                
                # Initialize economy system
                economy_init_result = self.economy_manager.initialize_economy(config)
                logger.info(f"Economy manager initialized: {economy_init_result}")
            
            # Setup event handlers
            await self._setup_event_handlers()
            
            # Initialize WebSocket manager
            # WebSocket manager initialization is handled in its __init__
            
            # Initialize deployment system
            await self.deployment_manager.initialize_system()
            
            # Mark as initialized
            self.is_initialized = True
            
            # Publish system initialization event
            publish_system_event(EconomyEventType.ECONOMY_INITIALIZED, 
                               details={"timestamp": datetime.utcnow().isoformat()})
            
            result = {
                "status": "initialized",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "economy_manager": True,
                    "event_bus": True,
                    "websocket_manager": True,
                    "database_service": True,
                    "deployment_manager": True
                },
                "economy_details": economy_init_result
            }
            
            logger.info("Economy Integration Manager initialized successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to initialize Economy Integration Manager: {e}")
            self.metrics["errors_handled"] += 1
            
            # Publish system error event
            publish_system_event(EconomyEventType.ECONOMY_ERROR, 
                               error=str(e),
                               component="integration_manager")
            raise
    
    async def start(self) -> Dict[str, Any]:
        """
        Start the economy system integration.
        
        Returns:
            Start status and details
        """
        if not self.is_initialized:
            raise RuntimeError("Economy Integration Manager must be initialized before starting")
        
        try:
            logger.info("Starting Economy Integration Manager...")
            
            # Start background tasks
            # Note: In a real application, these would be actual background tasks
            self.is_running = True
            
            # Start periodic tick processing (example implementation)
            # asyncio.create_task(self._periodic_tick_processor())
            
            result = {
                "status": "started",
                "timestamp": datetime.utcnow().isoformat(),
                "running": self.is_running
            }
            
            # Notify via WebSocket
            await notify_economy_status(result)
            
            logger.info("Economy Integration Manager started successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to start Economy Integration Manager: {e}")
            self.metrics["errors_handled"] += 1
            
            publish_system_event(EconomyEventType.ECONOMY_ERROR,
                               error=str(e),
                               component="integration_manager")
            raise
    
    async def shutdown(self) -> Dict[str, Any]:
        """
        Shutdown the economy system integration.
        
        Returns:
            Shutdown status and details
        """
        try:
            logger.info("Shutting down Economy Integration Manager...")
            
            # Stop running processes
            self.is_running = False
            
            # Shutdown economy manager
            if self.economy_manager:
                shutdown_result = self.economy_manager.shutdown_economy()
                logger.info(f"Economy manager shutdown: {shutdown_result}")
            
            # Shutdown deployment manager
            if self.deployment_manager:
                await self.deployment_manager.shutdown_system()
            
            # Close database connections
            if self.database_service:
                self.database_service.close()
            
            # Clear event handlers
            self.event_bus.clear_history()
            
            # Publish shutdown event
            publish_system_event(EconomyEventType.ECONOMY_SHUTDOWN,
                               details={"timestamp": datetime.utcnow().isoformat()})
            
            result = {
                "status": "shutdown",
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": self.get_metrics()
            }
            
            logger.info("Economy Integration Manager shutdown successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error during Economy Integration Manager shutdown: {e}")
            self.metrics["errors_handled"] += 1
            raise
    
    async def process_economic_tick(self, tick_count: int = 1) -> Dict[str, Any]:
        """
        Process economic simulation tick with full integration.
        
        Args:
            tick_count: Number of ticks to process
            
        Returns:
            Tick processing results
        """
        if not self.is_initialized or not self.economy_manager:
            raise RuntimeError("Economy system not properly initialized")
        
        try:
            start_time = datetime.utcnow()
            
            # Process tick in economy manager
            tick_result = self.economy_manager.process_tick(tick_count)
            
            # Update metrics
            self.metrics["last_tick_time"] = start_time.isoformat()
            
            # Notify via WebSocket
            await notify_economy_status({
                "tick_processed": tick_count,
                "timestamp": start_time.isoformat(),
                "results": tick_result
            })
            
            # Publish tick event
            publish_system_event(EconomyEventType.ECONOMIC_TICK_PROCESSED,
                               tick_count=tick_count,
                               results=tick_result)
            
            logger.info(f"Processed {tick_count} economic tick(s)")
            return tick_result
            
        except Exception as e:
            logger.error(f"Error processing economic tick: {e}")
            self.metrics["errors_handled"] += 1
            
            publish_system_event(EconomyEventType.ECONOMY_ERROR,
                               error=str(e),
                               component="tick_processor")
            raise
    
    async def handle_cross_system_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Handle events from other game systems.
        
        Args:
            event_type: Type of the external event
            event_data: Event data
        """
        try:
            logger.info(f"Handling cross-system event: {event_type}")
            
            # Process based on event type
            if event_type in ["character.action", "quest.completed"]:
                await self._handle_gameplay_event(event_type, event_data)
            elif event_type in ["faction.relationship_changed", "diplomacy.treaty_signed"]:
                await self._handle_political_event(event_type, event_data)
            elif event_type in ["world.time_advance", "world.region_updated"]:
                await self._handle_world_event(event_type, event_data)
            else:
                logger.debug(f"Unhandled cross-system event type: {event_type}")
            
            self.metrics["events_processed"] += 1
            
        except Exception as e:
            logger.error(f"Error handling cross-system event {event_type}: {e}")
            self.metrics["errors_handled"] += 1
    
    def get_status(self) -> Dict[str, Any]:
        """Get current integration manager status."""
        return {
            "initialized": self.is_initialized,
            "running": self.is_running,
            "components": {
                "economy_manager": self.economy_manager is not None,
                "event_bus": True,
                "websocket_manager": True,
                "database_service": self.database_service is not None,
                "deployment_manager": self.deployment_manager is not None
            },
            "metrics": self.get_metrics(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get integration performance metrics."""
        return dict(self.metrics)
    
    async def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check."""
        if not self.deployment_manager:
            return {"status": "error", "message": "Deployment manager not initialized"}
        
        try:
            health_checks = await self.deployment_manager.run_health_checks()
            return {
                "status": "healthy" if all(check.status.value == "healthy" for check in health_checks.values()) else "warning",
                "checks": {name: {
                    "status": check.status.value,
                    "message": check.message,
                    "response_time_ms": check.response_time_ms
                } for name, check in health_checks.items()},
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "message": str(e)}
    
    # Private methods
    
    async def _initialize_database(self) -> None:
        """Initialize database components."""
        try:
            # Test database connection
            if not self.database_service.test_connection():
                raise Exception("Database connection test failed")
            
            # Create tables if needed
            self.database_service.create_tables()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def _setup_event_handlers(self) -> None:
        """Setup event handlers for economy events."""
        try:
            # Resource events
            self.event_bus.subscribe(EconomyEventType.RESOURCE_CREATED, self._handle_resource_event)
            self.event_bus.subscribe(EconomyEventType.RESOURCE_UPDATED, self._handle_resource_event)
            self.event_bus.subscribe(EconomyEventType.RESOURCE_AMOUNT_CHANGED, self._handle_resource_event)
            
            # Market events
            self.event_bus.subscribe(EconomyEventType.MARKET_CREATED, self._handle_market_event)
            self.event_bus.subscribe(EconomyEventType.MARKET_UPDATED, self._handle_market_event)
            self.event_bus.subscribe(EconomyEventType.PRICE_UPDATED, self._handle_price_event)
            
            # Trade events
            self.event_bus.subscribe(EconomyEventType.TRADE_ROUTE_CREATED, self._handle_trade_event)
            self.event_bus.subscribe(EconomyEventType.TRADE_EXECUTED, self._handle_trade_event)
            
            # Transaction events
            self.event_bus.subscribe(EconomyEventType.TRANSACTION_COMPLETED, self._handle_transaction_event)
            
            # System events
            self.event_bus.subscribe(EconomyEventType.ECONOMIC_ANALYTICS_UPDATED, self._handle_analytics_event)
            
            self.event_handlers_registered = True
            logger.info("Event handlers registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup event handlers: {e}")
            raise
    
    def _handle_resource_event(self, event: EconomyEvent) -> None:
        """Handle resource-related events."""
        try:
            # Convert to WebSocket notification
            asyncio.create_task(self.websocket_manager.broadcast_market_update({
                "type": "resource_updated",
                "event_type": event.event_type.value,
                "data": event.data,
                "timestamp": event.timestamp.isoformat()
            }))
            
            self.metrics["events_processed"] += 1
            
        except Exception as e:
            logger.error(f"Error handling resource event: {e}")
            self.metrics["errors_handled"] += 1
    
    def _handle_market_event(self, event: EconomyEvent) -> None:
        """Handle market-related events."""
        try:
            # Convert to WebSocket notification
            asyncio.create_task(notify_market_updated({
                "event_type": event.event_type.value,
                "data": event.data,
                "timestamp": event.timestamp.isoformat()
            }))
            
            self.metrics["events_processed"] += 1
            
        except Exception as e:
            logger.error(f"Error handling market event: {e}")
            self.metrics["errors_handled"] += 1
    
    def _handle_price_event(self, event: EconomyEvent) -> None:
        """Handle price-related events."""
        try:
            if event.event_type == EconomyEventType.PRICE_UPDATED:
                resource_id = event.data.get("resource_id", "")
                market_id = event.data.get("market_id", 0)
                new_price = event.data.get("new_price", 0.0)
                
                asyncio.create_task(notify_price_updated(
                    resource_id, market_id, new_price, event.data
                ))
            
            self.metrics["events_processed"] += 1
            
        except Exception as e:
            logger.error(f"Error handling price event: {e}")
            self.metrics["errors_handled"] += 1
    
    def _handle_trade_event(self, event: EconomyEvent) -> None:
        """Handle trade-related events."""
        try:
            # Convert to WebSocket notification
            asyncio.create_task(notify_trade_route_updated({
                "event_type": event.event_type.value,
                "data": event.data,
                "timestamp": event.timestamp.isoformat()
            }))
            
            self.metrics["events_processed"] += 1
            
        except Exception as e:
            logger.error(f"Error handling trade event: {e}")
            self.metrics["errors_handled"] += 1
    
    def _handle_transaction_event(self, event: EconomyEvent) -> None:
        """Handle transaction-related events."""
        try:
            # Convert to WebSocket notification
            asyncio.create_task(notify_transaction_completed({
                "event_type": event.event_type.value,
                "data": event.data,
                "timestamp": event.timestamp.isoformat()
            }))
            
            self.metrics["events_processed"] += 1
            
        except Exception as e:
            logger.error(f"Error handling transaction event: {e}")
            self.metrics["errors_handled"] += 1
    
    def _handle_analytics_event(self, event: EconomyEvent) -> None:
        """Handle analytics-related events."""
        try:
            region_id = event.data.get("region_id", 0)
            analytics = event.data.get("analytics", {})
            
            asyncio.create_task(notify_economic_analytics(region_id, analytics))
            
            self.metrics["events_processed"] += 1
            
        except Exception as e:
            logger.error(f"Error handling analytics event: {e}")
            self.metrics["errors_handled"] += 1
    
    async def _handle_gameplay_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle gameplay-related events that affect economy."""
        # Implementation for character actions, quest completions, etc.
        pass
    
    async def _handle_political_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle political events that affect economy."""
        # Implementation for faction changes, diplomacy, etc.
        pass
    
    async def _handle_world_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle world events that affect economy."""
        # Implementation for time advancement, region updates, etc.
        pass

# Singleton access
def get_integration_manager() -> EconomyIntegrationManager:
    """Get the economy integration manager singleton."""
    return EconomyIntegrationManager.get_instance()

# Context manager for integration lifecycle
@asynccontextmanager
async def economy_integration_context(config: Optional[Dict[str, Any]] = None):
    """Context manager for economy integration lifecycle."""
    manager = get_integration_manager()
    
    try:
        # Initialize
        init_result = await manager.initialize(config)
        logger.info(f"Economy integration initialized: {init_result}")
        
        # Start
        start_result = await manager.start()
        logger.info(f"Economy integration started: {start_result}")
        
        yield manager
        
    finally:
        # Shutdown
        try:
            shutdown_result = await manager.shutdown()
            logger.info(f"Economy integration shutdown: {shutdown_result}")
        except Exception as e:
            logger.error(f"Error during economy integration shutdown: {e}")

# Convenience functions for external integration
async def initialize_economy_system(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Initialize the complete economy system."""
    manager = get_integration_manager()
    return await manager.initialize(config)

async def start_economy_system() -> Dict[str, Any]:
    """Start the economy system."""
    manager = get_integration_manager()
    return await manager.start()

async def shutdown_economy_system() -> Dict[str, Any]:
    """Shutdown the economy system."""
    manager = get_integration_manager()
    return await manager.shutdown()

async def process_economic_tick(tick_count: int = 1) -> Dict[str, Any]:
    """Process economic tick with full integration."""
    manager = get_integration_manager()
    return await manager.process_economic_tick(tick_count)

def get_economy_status() -> Dict[str, Any]:
    """Get economy system status."""
    manager = get_integration_manager()
    return manager.get_status()

async def run_economy_health_check() -> Dict[str, Any]:
    """Run economy system health check."""
    manager = get_integration_manager()
    return await manager.run_health_check()

# Export main classes and functions
__all__ = [
    'EconomyIntegrationManager',
    'get_integration_manager',
    'economy_integration_context',
    'initialize_economy_system',
    'start_economy_system',
    'shutdown_economy_system',
    'process_economic_tick',
    'get_economy_status',
    'run_economy_health_check'
] 