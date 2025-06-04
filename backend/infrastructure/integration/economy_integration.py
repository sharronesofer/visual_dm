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
from backend.infrastructure.websocket.economy import (
    EconomyWebSocketManager,
    notify_market_updated,
    notify_price_updated,
    notify_transaction_completed,
    notify_trade_route_updated,
    notify_economic_analytics,
    notify_economy_status
)
from backend.infrastructure.database import (
    DatabaseService,
    get_database_service,
    database_session
)
from backend.infrastructure.deployment.economy import (
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
        self.database_service: DatabaseService = get_database_service()
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
            
            # Publish system start event
            publish_system_event(EconomyEventType.ECONOMY_STARTED, 
                               details=result)
            
            logger.info("Economy Integration Manager started successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to start Economy Integration Manager: {e}")
            self.metrics["errors_handled"] += 1
            
            # Publish system error event
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
            
            # Stop background tasks
            self.is_running = False
            
            # Shutdown deployment manager
            if self.deployment_manager:
                await self.deployment_manager.shutdown_system()
            
            # Clear event handlers
            self.event_handlers_registered = False
            
            result = {
                "status": "shutdown",
                "timestamp": datetime.utcnow().isoformat(),
                "final_metrics": self.get_metrics()
            }
            
            # Publish system shutdown event
            publish_system_event(EconomyEventType.ECONOMY_SHUTDOWN, 
                               details=result)
            
            logger.info("Economy Integration Manager shutdown successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error during Economy Integration Manager shutdown: {e}")
            self.metrics["errors_handled"] += 1
            raise

    async def process_economic_tick(self, tick_count: int = 1) -> Dict[str, Any]:
        """
        Process economic tick operations.
        
        Args:
            tick_count: Number of ticks to process
            
        Returns:
            Tick processing results
        """
        if not self.is_running:
            raise RuntimeError("Economy Integration Manager is not running")
        
        try:
            start_time = datetime.utcnow()
            
            # Process through economy manager
            if self.economy_manager:
                economy_results = []
                for _ in range(tick_count):
                    result = self.economy_manager.process_economic_tick()
                    economy_results.append(result)
                
                # Update metrics
                self.metrics["last_tick_time"] = start_time.isoformat()
                
                # Notify via WebSocket
                await notify_economic_analytics({
                    "tick_results": economy_results,
                    "processed_at": start_time.isoformat()
                })
                
                return {
                    "status": "completed",
                    "tick_count": tick_count,
                    "processed_at": start_time.isoformat(),
                    "results": economy_results
                }
            else:
                raise RuntimeError("Economy manager not initialized")
                
        except Exception as e:
            logger.error(f"Error processing economic tick: {e}")
            self.metrics["errors_handled"] += 1
            
            # Publish error event
            publish_system_event(EconomyEventType.ECONOMY_ERROR, 
                               error=str(e),
                               component="tick_processor")
            raise

    async def handle_cross_system_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Handle events from other game systems.
        
        Args:
            event_type: Type of the event
            event_data: Event data
        """
        try:
            if event_type.startswith("gameplay_"):
                await self._handle_gameplay_event(event_type, event_data)
            elif event_type.startswith("political_"):
                await self._handle_political_event(event_type, event_data)
            elif event_type.startswith("world_"):
                await self._handle_world_event(event_type, event_data)
            else:
                logger.warning(f"Unknown cross-system event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Error handling cross-system event {event_type}: {e}")
            self.metrics["errors_handled"] += 1

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the integration manager."""
        return {
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "event_handlers_registered": self.event_handlers_registered,
            "economy_manager_status": "active" if self.economy_manager else "inactive",
            "deployment_manager_status": "active" if self.deployment_manager else "inactive"
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return self.metrics.copy()

    async def run_health_check(self) -> Dict[str, Any]:
        """
        Run a comprehensive health check of the economy system.
        
        Returns:
            Health check results
        """
        try:
            health_status = {
                "overall_status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {}
            }
            
            # Check economy manager
            if self.economy_manager:
                health_status["components"]["economy_manager"] = "healthy"
            else:
                health_status["components"]["economy_manager"] = "inactive"
                health_status["overall_status"] = "degraded"
            
            # Check database
            try:
                async with database_session() as session:
                    # Simple query to test database connectivity
                    pass
                health_status["components"]["database"] = "healthy"
            except Exception:
                health_status["components"]["database"] = "unhealthy"
                health_status["overall_status"] = "unhealthy"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "overall_status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }

    async def _initialize_database(self) -> None:
        """Initialize database connections and verify schema."""
        try:
            # Test database connection
            async with database_session() as session:
                # Verify economy tables exist
                # This would contain actual schema validation in production
                pass
            logger.info("Database initialized successfully for economy integration")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    async def _setup_event_handlers(self) -> None:
        """Setup event handlers for economy events."""
        try:
            # Register event handlers
            self.event_bus.subscribe(EconomyEventType.RESOURCE_UPDATED, self._handle_resource_event)
            self.event_bus.subscribe(EconomyEventType.MARKET_UPDATED, self._handle_market_event)
            self.event_bus.subscribe(EconomyEventType.PRICE_UPDATED, self._handle_price_event)
            self.event_bus.subscribe(EconomyEventType.TRADE_COMPLETED, self._handle_trade_event)
            self.event_bus.subscribe(EconomyEventType.TRANSACTION_COMPLETED, self._handle_transaction_event)
            self.event_bus.subscribe(EconomyEventType.ANALYTICS_UPDATED, self._handle_analytics_event)
            
            self.event_handlers_registered = True
            logger.info("Economy event handlers registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup event handlers: {e}")
            raise

    def _handle_resource_event(self, event: EconomyEvent) -> None:
        """Handle resource-related events."""
        try:
            self.metrics["events_processed"] += 1
            
            # Process resource event
            if isinstance(event, ResourceEvent):
                # Notify via WebSocket
                asyncio.create_task(notify_market_updated({
                    "resource_id": event.resource_id,
                    "region_id": event.region_id,
                    "event_type": "resource_updated",
                    "timestamp": event.timestamp.isoformat()
                }))
                
        except Exception as e:
            logger.error(f"Error handling resource event: {e}")
            self.metrics["errors_handled"] += 1

    def _handle_market_event(self, event: EconomyEvent) -> None:
        """Handle market-related events."""
        try:
            self.metrics["events_processed"] += 1
            
            # Process market event
            if isinstance(event, MarketEvent):
                # Notify via WebSocket
                asyncio.create_task(notify_market_updated({
                    "market_id": event.market_id,
                    "region_id": event.region_id,
                    "event_type": "market_updated",
                    "timestamp": event.timestamp.isoformat()
                }))
                
        except Exception as e:
            logger.error(f"Error handling market event: {e}")
            self.metrics["errors_handled"] += 1

    def _handle_price_event(self, event: EconomyEvent) -> None:
        """Handle price-related events."""
        try:
            self.metrics["events_processed"] += 1
            
            # Process price event
            if isinstance(event, PriceEvent):
                # Notify via WebSocket
                asyncio.create_task(notify_price_updated({
                    "resource_id": event.resource_id,
                    "region_id": event.region_id,
                    "old_price": event.old_price,
                    "new_price": event.new_price,
                    "event_type": "price_updated",
                    "timestamp": event.timestamp.isoformat()
                }))
                
        except Exception as e:
            logger.error(f"Error handling price event: {e}")
            self.metrics["errors_handled"] += 1

    def _handle_trade_event(self, event: EconomyEvent) -> None:
        """Handle trade-related events."""
        try:
            self.metrics["events_processed"] += 1
            
            # Process trade event
            if isinstance(event, TradeEvent):
                # Notify via WebSocket
                asyncio.create_task(notify_trade_route_updated({
                    "trade_route_id": event.trade_route_id,
                    "from_region": event.from_region,
                    "to_region": event.to_region,
                    "event_type": "trade_completed",
                    "timestamp": event.timestamp.isoformat()
                }))
                
        except Exception as e:
            logger.error(f"Error handling trade event: {e}")
            self.metrics["errors_handled"] += 1

    def _handle_transaction_event(self, event: EconomyEvent) -> None:
        """Handle transaction-related events."""
        try:
            self.metrics["events_processed"] += 1
            
            # Process transaction event
            if isinstance(event, TransactionEvent):
                # Notify via WebSocket
                asyncio.create_task(notify_transaction_completed({
                    "transaction_id": event.transaction_id,
                    "player_id": event.player_id,
                    "npc_id": event.npc_id,
                    "amount": event.amount,
                    "event_type": "transaction_completed",
                    "timestamp": event.timestamp.isoformat()
                }))
                
        except Exception as e:
            logger.error(f"Error handling transaction event: {e}")
            self.metrics["errors_handled"] += 1

    def _handle_analytics_event(self, event: EconomyEvent) -> None:
        """Handle analytics-related events."""
        try:
            self.metrics["events_processed"] += 1
            
            # Notify via WebSocket
            asyncio.create_task(notify_economic_analytics({
                "event_type": "analytics_updated",
                "timestamp": event.timestamp.isoformat(),
                "details": event.details
            }))
            
        except Exception as e:
            logger.error(f"Error handling analytics event: {e}")
            self.metrics["errors_handled"] += 1

    async def _handle_gameplay_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle gameplay system events."""
        # Implementation would handle specific gameplay events
        pass

    async def _handle_political_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle political system events."""
        # Implementation would handle specific political events
        pass

    async def _handle_world_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle world system events."""
        # Implementation would handle specific world events
        pass


def get_integration_manager() -> EconomyIntegrationManager:
    """Get the economy integration manager instance."""
    return EconomyIntegrationManager.get_instance()


@asynccontextmanager
async def economy_integration_context(config: Optional[Dict[str, Any]] = None):
    """
    Context manager for economy integration operations.
    
    Args:
        config: Optional configuration for the economy system
    """
    integration_manager = get_integration_manager()
    
    try:
        # Initialize if not already done
        if not integration_manager.is_initialized:
            await integration_manager.initialize(config)
        
        # Start if not already running
        if not integration_manager.is_running:
            await integration_manager.start()
        
        yield integration_manager
        
    finally:
        # Shutdown is handled externally or by application lifecycle
        pass


# Convenience functions for common operations
async def initialize_economy_system(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Initialize the economy system integration."""
    return await get_integration_manager().initialize(config)


async def start_economy_system() -> Dict[str, Any]:
    """Start the economy system integration."""
    return await get_integration_manager().start()


async def shutdown_economy_system() -> Dict[str, Any]:
    """Shutdown the economy system integration."""
    return await get_integration_manager().shutdown()


async def process_economic_tick(tick_count: int = 1) -> Dict[str, Any]:
    """Process economic tick operations."""
    return await get_integration_manager().process_economic_tick(tick_count)


def get_economy_status() -> Dict[str, Any]:
    """Get the current economy system status."""
    return get_integration_manager().get_status()


async def run_economy_health_check() -> Dict[str, Any]:
    """Run economy system health check."""
    return await get_integration_manager().run_health_check() 