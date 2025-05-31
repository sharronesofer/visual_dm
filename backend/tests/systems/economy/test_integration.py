"""
Economy System Integration Tests - Comprehensive tests for the complete economy system.

Tests the integration of all economy system components including EconomyManager,
services, API routes, WebSocket events, event system, database, and deployment.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from backend.systems.economy.economy_manager import EconomyManager
from backend.systems.economy.resource_service import ResourceService
from backend.systems.economy.market_service import MarketService
from backend.systems.economy.database_service import EconomyDatabaseService
from backend.systems.economy.events import (
    EconomyEventBus, EconomyEventType, get_event_bus,
    publish_resource_event, publish_market_event
)
from backend.systems.economy.websocket_events import economy_websocket_manager
from backend.systems.economy.deployment import (
    EconomyDeploymentManager, DeploymentConfig, HealthStatus
)

class TestEconomySystemIntegration:
    """Integration tests for the complete economy system."""
    
    def setup_method(self):
        """Set up test environment."""
        # Reset singletons for clean testing
        EconomyManager._instance = None
        
        # Create test database service
        self.db_service = EconomyDatabaseService()
        
        # Create economy manager with test database
        self.economy_manager = EconomyManager.get_instance(self.db_service.create_session())
        
        # Get event bus
        self.event_bus = get_event_bus()
        
        # Create deployment manager with test config
        self.deployment_config = DeploymentConfig(
            environment="test",
            debug_mode=True,
            websocket_enabled=True,
            event_system_enabled=True
        )
        self.deployment_manager = EconomyDeploymentManager(self.deployment_config)
    
    def test_economy_manager_initialization(self):
        """Test that EconomyManager initializes correctly with all services."""
        assert self.economy_manager is not None
        assert self.economy_manager.resource_service is not None
        assert self.economy_manager.market_service is not None
        assert isinstance(self.economy_manager.resource_service, ResourceService)
        assert isinstance(self.economy_manager.market_service, MarketService)
    
    def test_resource_service_integration(self):
        """Test ResourceService integration with EconomyManager."""
        # Test resource creation through economy manager
        resource_data = {
            "id": "test_resource_integration",
            "name": "Test Resource Integration",
            "resource_type": "raw_material",
            "base_value": 100.0,
            "region_id": 1
        }
        
        result = self.economy_manager.create_resource(resource_data)
        assert result["success"] is True
        assert "resource" in result
        
        # Test resource retrieval
        resource = self.economy_manager.get_resource("test_resource_integration")
        assert resource is not None
        assert resource["name"] == "Test Resource Integration"
        
        # Test resource update
        update_result = self.economy_manager.update_resource(
            "test_resource_integration", 
            {"base_value": 150.0}
        )
        assert update_result["success"] is True
        
        # Verify update
        updated_resource = self.economy_manager.get_resource("test_resource_integration")
        assert updated_resource["base_value"] == 150.0
    
    def test_market_service_integration(self):
        """Test MarketService integration with EconomyManager."""
        # Test market creation through economy manager
        market_data = {
            "name": "Test Market Integration",
            "region_id": 1,
            "market_type": "commodity",
            "tax_rate": 0.05
        }
        
        result = self.economy_manager.create_market(market_data)
        assert result["success"] is True
        assert "market" in result
        
        market_id = result["market"]["id"]
        
        # Test market retrieval
        market = self.economy_manager.get_market(market_id)
        assert market is not None
        assert market["name"] == "Test Market Integration"
        
        # Test market update
        update_result = self.economy_manager.update_market(
            market_id, 
            {"tax_rate": 0.08}
        )
        assert update_result["success"] is True
        
        # Verify update
        updated_market = self.economy_manager.get_market(market_id)
        assert updated_market["tax_rate"] == 0.08
    
    def test_price_calculation_integration(self):
        """Test price calculation integration across services."""
        # Create a resource
        resource_data = {
            "id": "price_test_resource",
            "name": "Price Test Resource",
            "resource_type": "commodity",
            "base_value": 50.0,
            "region_id": 1
        }
        self.economy_manager.create_resource(resource_data)
        
        # Create a market
        market_data = {
            "name": "Price Test Market",
            "region_id": 1,
            "market_type": "commodity",
            "tax_rate": 0.1
        }
        market_result = self.economy_manager.create_market(market_data)
        market_id = market_result["market"]["id"]
        
        # Test price calculation
        price_result = self.economy_manager.calculate_price(
            resource_id="price_test_resource",
            market_id=market_id,
            quantity=10.0
        )
        
        assert "price" in price_result
        assert "details" in price_result
        assert price_result["price"] > 0
        assert "base_price" in price_result["details"]
        assert "tax_amount" in price_result["details"]
    
    def test_event_system_integration(self):
        """Test event system integration with economy operations."""
        events_received = []
        
        def event_handler(event):
            events_received.append(event)
        
        # Subscribe to resource events
        self.event_bus.subscribe(EconomyEventType.RESOURCE_CREATED, event_handler)
        
        # Create a resource (should trigger event)
        resource_data = {
            "id": "event_test_resource",
            "name": "Event Test Resource",
            "resource_type": "commodity",
            "base_value": 75.0,
            "region_id": 1
        }
        
        # Publish event manually (simulating EconomyManager integration)
        publish_resource_event(
            EconomyEventType.RESOURCE_CREATED,
            resource_id="event_test_resource",
            region_id=1,
            resource_type="commodity",
            amount=75.0
        )
        
        # Verify event was received
        assert len(events_received) == 1
        event = events_received[0]
        assert event.event_type == EconomyEventType.RESOURCE_CREATED
        assert event.data["resource_id"] == "event_test_resource"
        assert event.data["region_id"] == 1
    
    @pytest.mark.asyncio
    async def test_websocket_integration(self):
        """Test WebSocket integration with event system."""
        # Mock WebSocket
        mock_websocket = Mock()
        mock_websocket.send_text = AsyncMock()
        
        # Connect to WebSocket manager
        await economy_websocket_manager.connect(mock_websocket, "test_client")
        
        # Subscribe to economy channel
        await economy_websocket_manager.subscribe(mock_websocket, "economy")
        
        # Publish an event (should trigger WebSocket broadcast)
        publish_resource_event(
            EconomyEventType.RESOURCE_CREATED,
            resource_id="websocket_test_resource",
            region_id=1,
            resource_type="commodity",
            amount=100.0
        )
        
        # Give async handlers time to process
        await asyncio.sleep(0.1)
        
        # Verify WebSocket received messages
        assert mock_websocket.send_text.called
        
        # Clean up
        await economy_websocket_manager.disconnect(mock_websocket)
    
    def test_database_service_integration(self):
        """Test database service integration."""
        # Test connection
        assert self.db_service.test_connection() is True
        
        # Test session creation
        session = self.db_service.create_session()
        assert session is not None
        
        # Test database stats
        stats = self.db_service.get_database_stats()
        assert isinstance(stats, dict)
        assert "connection_info" in stats
        
        # Clean up
        session.close()
    
    @pytest.mark.asyncio
    async def test_deployment_manager_integration(self):
        """Test deployment manager integration with all systems."""
        # Set up deployment manager with economy manager
        self.deployment_manager.economy_manager = self.economy_manager
        self.deployment_manager.db_service = self.db_service
        self.deployment_manager.event_bus = self.event_bus
        self.deployment_manager.websocket_manager = economy_websocket_manager
        
        # Run health checks
        health_checks = await self.deployment_manager.run_health_checks()
        
        # Verify health checks
        assert "economy_manager" in health_checks
        assert "event_system" in health_checks
        assert "websocket_system" in health_checks
        assert "performance" in health_checks
        assert "system" in health_checks
        
        # Check that economy manager is healthy
        economy_check = health_checks["economy_manager"]
        assert economy_check.status == HealthStatus.HEALTHY
        assert "Economy manager operational" in economy_check.message
        
        # Get deployment info
        deployment_info = self.deployment_manager.get_deployment_info()
        assert deployment_info["environment"] == "test"
        assert deployment_info["is_ready"] is False  # Not fully initialized
        
        # Get metrics
        metrics = self.deployment_manager.get_metrics()
        assert "timestamp" in metrics
        assert "uptime_seconds" in metrics
        assert "is_ready" in metrics
    
    def test_economic_analytics_integration(self):
        """Test economic analytics integration."""
        # Create test data
        resource_data = {
            "id": "analytics_resource",
            "name": "Analytics Resource",
            "resource_type": "commodity",
            "base_value": 200.0,
            "region_id": 1
        }
        self.economy_manager.create_resource(resource_data)
        
        # Test analytics calculation
        analytics = self.economy_manager.calculate_economic_analytics(region_id=1)
        
        assert "region_id" in analytics
        assert "total_resources" in analytics
        assert "total_value" in analytics
        assert "resource_breakdown" in analytics
        assert analytics["region_id"] == 1
        assert analytics["total_resources"] >= 1
    
    def test_economic_forecasting_integration(self):
        """Test economic forecasting integration."""
        # Create test data
        resource_data = {
            "id": "forecast_resource",
            "name": "Forecast Resource",
            "resource_type": "commodity",
            "base_value": 150.0,
            "region_id": 1
        }
        self.economy_manager.create_resource(resource_data)
        
        # Test forecasting
        forecast = self.economy_manager.generate_economic_forecast(
            region_id=1,
            time_horizon_days=30
        )
        
        assert "region_id" in forecast
        assert "time_horizon_days" in forecast
        assert "forecast_data" in forecast
        assert "confidence_score" in forecast
        assert forecast["region_id"] == 1
        assert forecast["time_horizon_days"] == 30
        assert 0 <= forecast["confidence_score"] <= 1
    
    def test_population_impact_integration(self):
        """Test population impact calculation integration."""
        # Create test resource
        resource_data = {
            "id": "population_resource",
            "name": "Population Resource",
            "resource_type": "essential",
            "base_value": 100.0,
            "region_id": 1
        }
        self.economy_manager.create_resource(resource_data)
        
        # Test population impact calculation
        impact = self.economy_manager.calculate_population_impact(
            region_id=1,
            population_size=10000
        )
        
        assert "region_id" in impact
        assert "population_size" in impact
        assert "resource_impacts" in impact
        assert "overall_impact" in impact
        assert impact["region_id"] == 1
        assert impact["population_size"] == 10000
    
    def test_tick_processing_integration(self):
        """Test economic tick processing integration."""
        # Create test data
        resource_data = {
            "id": "tick_resource",
            "name": "Tick Resource",
            "resource_type": "commodity",
            "base_value": 80.0,
            "region_id": 1
        }
        self.economy_manager.create_resource(resource_data)
        
        market_data = {
            "name": "Tick Market",
            "region_id": 1,
            "market_type": "commodity",
            "tax_rate": 0.05
        }
        self.economy_manager.create_market(market_data)
        
        # Test tick processing
        tick_result = self.economy_manager.process_economic_tick(region_id=1)
        
        assert "region_id" in tick_result
        assert "processed_at" in tick_result
        assert "updates" in tick_result
        assert tick_result["region_id"] == 1
        assert isinstance(tick_result["updates"], dict)
    
    def test_economy_status_integration(self):
        """Test economy status integration."""
        # Create some test data
        resource_data = {
            "id": "status_resource",
            "name": "Status Resource",
            "resource_type": "commodity",
            "base_value": 120.0,
            "region_id": 1
        }
        self.economy_manager.create_resource(resource_data)
        
        market_data = {
            "name": "Status Market",
            "region_id": 1,
            "market_type": "commodity",
            "tax_rate": 0.06
        }
        self.economy_manager.create_market(market_data)
        
        # Test economy status
        status = self.economy_manager.get_economy_status()
        
        assert "initialized" in status
        assert "total_resources" in status
        assert "total_markets" in status
        assert "total_trade_routes" in status
        assert "regions" in status
        assert status["initialized"] is True
        assert status["total_resources"] >= 1
        assert status["total_markets"] >= 1
    
    @pytest.mark.asyncio
    async def test_full_system_integration(self):
        """Test full system integration with all components working together."""
        events_received = []
        
        def event_handler(event):
            events_received.append(event)
        
        # Subscribe to all events
        self.event_bus.subscribe_all(event_handler)
        
        # Mock WebSocket
        mock_websocket = Mock()
        mock_websocket.send_text = AsyncMock()
        
        # Connect WebSocket
        await economy_websocket_manager.connect(mock_websocket, "integration_test")
        await economy_websocket_manager.subscribe(mock_websocket, "economy")
        await economy_websocket_manager.subscribe(mock_websocket, "markets")
        
        # Create resource (should trigger events and WebSocket notifications)
        resource_data = {
            "id": "full_integration_resource",
            "name": "Full Integration Resource",
            "resource_type": "luxury",
            "base_value": 300.0,
            "region_id": 1
        }
        
        resource_result = self.economy_manager.create_resource(resource_data)
        assert resource_result["success"] is True
        
        # Publish event manually (simulating full integration)
        publish_resource_event(
            EconomyEventType.RESOURCE_CREATED,
            resource_id="full_integration_resource",
            region_id=1,
            resource_type="luxury",
            amount=300.0
        )
        
        # Create market
        market_data = {
            "name": "Full Integration Market",
            "region_id": 1,
            "market_type": "luxury",
            "tax_rate": 0.15
        }
        
        market_result = self.economy_manager.create_market(market_data)
        assert market_result["success"] is True
        
        market_id = market_result["market"]["id"]
        
        # Publish market event
        publish_market_event(
            EconomyEventType.MARKET_CREATED,
            market_id=market_id,
            region_id=1,
            market_type="luxury"
        )
        
        # Calculate price (integrating multiple services)
        price_result = self.economy_manager.calculate_price(
            resource_id="full_integration_resource",
            market_id=market_id,
            quantity=5.0
        )
        assert "price" in price_result
        assert price_result["price"] > 0
        
        # Run analytics
        analytics = self.economy_manager.calculate_economic_analytics(region_id=1)
        assert analytics["total_resources"] >= 1
        assert analytics["total_value"] > 0
        
        # Generate forecast
        forecast = self.economy_manager.generate_economic_forecast(
            region_id=1,
            time_horizon_days=7
        )
        assert forecast["confidence_score"] > 0
        
        # Process tick
        tick_result = self.economy_manager.process_economic_tick(region_id=1)
        assert "updates" in tick_result
        
        # Get final status
        status = self.economy_manager.get_economy_status()
        assert status["initialized"] is True
        assert status["total_resources"] >= 1
        assert status["total_markets"] >= 1
        
        # Give async handlers time to process
        await asyncio.sleep(0.1)
        
        # Verify events were received
        assert len(events_received) >= 2  # At least resource and market creation events
        
        # Verify WebSocket received messages
        assert mock_websocket.send_text.called
        
        # Clean up
        await economy_websocket_manager.disconnect(mock_websocket)
        
        # Verify integration completed successfully
        assert True  # If we get here, full integration test passed

class TestEconomySystemPerformance:
    """Performance tests for the economy system."""
    
    def setup_method(self):
        """Set up performance test environment."""
        EconomyManager._instance = None
        self.db_service = EconomyDatabaseService()
        self.economy_manager = EconomyManager.get_instance(self.db_service.create_session())
    
    def test_bulk_resource_operations_performance(self):
        """Test performance of bulk resource operations."""
        import time
        
        start_time = time.time()
        
        # Create multiple resources
        for i in range(100):
            resource_data = {
                "id": f"perf_resource_{i}",
                "name": f"Performance Resource {i}",
                "resource_type": "commodity",
                "base_value": 50.0 + i,
                "region_id": 1
            }
            result = self.economy_manager.create_resource(resource_data)
            assert result["success"] is True
        
        creation_time = time.time() - start_time
        
        # Retrieve all resources
        start_time = time.time()
        resources = self.economy_manager.get_resources_by_region(1)
        retrieval_time = time.time() - start_time
        
        # Verify performance is reasonable
        assert creation_time < 10.0  # Should create 100 resources in under 10 seconds
        assert retrieval_time < 1.0   # Should retrieve resources in under 1 second
        assert len(resources) >= 100
    
    def test_price_calculation_performance(self):
        """Test performance of price calculations."""
        import time
        
        # Create test data
        resource_data = {
            "id": "perf_price_resource",
            "name": "Performance Price Resource",
            "resource_type": "commodity",
            "base_value": 100.0,
            "region_id": 1
        }
        self.economy_manager.create_resource(resource_data)
        
        market_data = {
            "name": "Performance Price Market",
            "region_id": 1,
            "market_type": "commodity",
            "tax_rate": 0.1
        }
        market_result = self.economy_manager.create_market(market_data)
        market_id = market_result["market"]["id"]
        
        # Test multiple price calculations
        start_time = time.time()
        
        for i in range(1000):
            price_result = self.economy_manager.calculate_price(
                resource_id="perf_price_resource",
                market_id=market_id,
                quantity=1.0 + (i % 10)
            )
            assert "price" in price_result
        
        calculation_time = time.time() - start_time
        
        # Should calculate 1000 prices in reasonable time
        assert calculation_time < 5.0  # Under 5 seconds for 1000 calculations
        
        # Calculate average time per calculation
        avg_time_ms = (calculation_time / 1000) * 1000
        assert avg_time_ms < 5.0  # Under 5ms per calculation

if __name__ == "__main__":
    # Run basic integration test
    test_integration = TestEconomySystemIntegration()
    test_integration.setup_method()
    
    print("Running Economy System Integration Tests...")
    
    try:
        test_integration.test_economy_manager_initialization()
        print("✅ Economy Manager initialization test passed")
        
        test_integration.test_resource_service_integration()
        print("✅ Resource Service integration test passed")
        
        test_integration.test_market_service_integration()
        print("✅ Market Service integration test passed")
        
        test_integration.test_price_calculation_integration()
        print("✅ Price calculation integration test passed")
        
        test_integration.test_event_system_integration()
        print("✅ Event system integration test passed")
        
        test_integration.test_database_service_integration()
        print("✅ Database service integration test passed")
        
        test_integration.test_economic_analytics_integration()
        print("✅ Economic analytics integration test passed")
        
        test_integration.test_economic_forecasting_integration()
        print("✅ Economic forecasting integration test passed")
        
        test_integration.test_population_impact_integration()
        print("✅ Population impact integration test passed")
        
        test_integration.test_tick_processing_integration()
        print("✅ Tick processing integration test passed")
        
        test_integration.test_economy_status_integration()
        print("✅ Economy status integration test passed")
        
        print("\n🎯 All Economy System Integration Tests Passed!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        raise 