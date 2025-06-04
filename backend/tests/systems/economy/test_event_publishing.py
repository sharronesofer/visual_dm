"""
Test Economy Event Publishing

This module tests that all economic operations properly publish events
with standard data formats for reliable cross-system integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List

from backend.systems.economy.services.economy_manager import EconomyManager
from backend.systems.economy.events.events import (
    EconomyEventType, EconomyEvent, get_event_bus
)
from backend.systems.economy.services.resource import ResourceData
from backend.systems.economy.models.market import MarketData
from backend.systems.economy.models.trade_route import TradeRouteData


class TestEconomyEventPublishing:
    """Test suite for economy event publishing standardization."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_db_session = Mock()
        self.economy_manager = EconomyManager(self.mock_db_session)
        self.event_bus = get_event_bus()
        self.published_events = []
        
        # Mock event publishing to capture events
        def capture_event(event):
            self.published_events.append(event)
        
        self.event_bus.publish = capture_event
    
    def test_resource_creation_publishes_event(self):
        """Test that resource creation publishes appropriate event."""
        # Mock resource service
        mock_resource = Mock()
        mock_resource.id = "test-resource-123"
        mock_resource.region_id = 1
        mock_resource.resource_type = "iron"
        mock_resource.amount = 100.0
        mock_resource.base_value = 10.0
        mock_resource.rarity = "common"
        mock_resource.is_tradeable = True
        
        self.economy_manager.resource_service.create_resource = Mock(return_value=mock_resource)
        
        # Create resource
        resource_data = ResourceData(
            name="Iron Ore",
            resource_type="iron",
            region_id=1,
            amount=100.0
        )
        
        result = self.economy_manager.create_resource(resource_data)
        
        # Verify event was published
        assert len(self.published_events) == 1
        event = self.published_events[0]
        assert event.event_type == EconomyEventType.RESOURCE_CREATED
        assert event.data["resource_id"] == "test-resource-123"
        assert event.data["region_id"] == 1
        assert event.data["resource_type"] == "iron"
        assert event.data["amount"] == 100.0
    
    def test_resource_transfer_publishes_event(self):
        """Test that resource transfers publish appropriate events."""
        # Mock resource service
        mock_resource = Mock()
        mock_resource.resource_type = "gold"
        
        self.economy_manager.resource_service.transfer_resource = Mock(return_value=(True, "Success"))
        self.economy_manager.resource_service.get_resource = Mock(return_value=mock_resource)
        
        # Transfer resource
        result = self.economy_manager.transfer_resource(
            source_region_id=1,
            dest_region_id=2,
            resource_id=123,
            amount=50.0
        )
        
        # Verify event was published
        assert len(self.published_events) == 1
        event = self.published_events[0]
        assert event.event_type == EconomyEventType.RESOURCE_TRANSFERRED
        assert event.data["resource_id"] == "123"
        assert event.data["from_region_id"] == 1
        assert event.data["to_region_id"] == 2
        assert event.data["amount"] == 50.0
        assert event.data["transfer_successful"] == True
    
    def test_trade_route_creation_publishes_event(self):
        """Test that trade route creation publishes appropriate event."""
        # Mock trade service
        mock_route = Mock()
        mock_route.id = 456
        mock_route.name = "Test Route"
        mock_route.origin_region_id = 1
        mock_route.destination_region_id = 2
        mock_route.is_active = True
        mock_route.frequency_ticks = 10
        mock_route.efficiency = 0.8
        mock_route.danger_level = 2
        
        self.economy_manager.trade_service.create_trade_route = Mock(return_value=mock_route)
        
        # Create trade route
        route_data = TradeRouteData(
            name="Test Route",
            origin_region_id=1,
            destination_region_id=2
        )
        
        result = self.economy_manager.create_trade_route(route_data)
        
        # Verify event was published
        assert len(self.published_events) == 1
        event = self.published_events[0]
        assert event.event_type == EconomyEventType.TRADE_ROUTE_CREATED
        assert event.data["trade_route_id"] == 456
        assert event.data["origin_region_id"] == 1
        assert event.data["destination_region_id"] == 2
        assert event.data["route_name"] == "Test Route"
    
    def test_trade_execution_publishes_events(self):
        """Test that trade route processing publishes execution events."""
        # Mock trade service
        trade_events = [
            {
                "trade_route_id": 456,
                "origin_region_id": 1,
                "destination_region_id": 2,
                "resource_id": "iron",
                "amount": 25.0,
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
        
        self.economy_manager.trade_service.process_trade_routes = Mock(
            return_value=(1, trade_events)
        )
        
        # Process trade routes
        result = self.economy_manager.process_trade_routes(1)
        
        # Verify event was published
        assert len(self.published_events) == 1
        event = self.published_events[0]
        assert event.event_type == EconomyEventType.TRADE_EXECUTED
        assert event.data["trade_route_id"] == 456
        assert event.data["origin_region_id"] == 1
        assert event.data["destination_region_id"] == 2
        assert event.data["resource_id"] == "iron"
        assert event.data["amount"] == 25.0
    
    def test_market_creation_publishes_event(self):
        """Test that market creation publishes appropriate event."""
        # Mock market service
        mock_market = Mock()
        mock_market.id = 789
        mock_market.region_id = 1
        mock_market.market_type = "commodity"
        mock_market.name = "Test Market"
        mock_market.is_active = True
        mock_market.base_demand = 100.0
        mock_market.base_supply = 80.0
        
        self.economy_manager.market_service.create_market = Mock(return_value=mock_market)
        
        # Create market
        market_data = MarketData(
            name="Test Market",
            region_id=1,
            market_type="commodity"
        )
        
        result = self.economy_manager.create_market(market_data)
        
        # Verify event was published
        assert len(self.published_events) == 1
        event = self.published_events[0]
        assert event.event_type == EconomyEventType.MARKET_CREATED
        assert event.data["market_id"] == 789
        assert event.data["region_id"] == 1
        assert event.data["market_type"] == "commodity"
        assert event.data["market_name"] == "Test Market"
    
    def test_shop_transaction_publishes_event(self):
        """Test that shop transactions publish appropriate events."""
        # Mock pricing methods
        self.economy_manager.calculate_shop_buy_price = Mock(
            return_value=(150.0, {"base_price": 100.0, "level_modifier": 1.5})
        )
        
        # Process shop transaction
        item = {"id": "sword_001", "name": "Iron Sword", "level": 5}
        result = self.economy_manager.process_shop_transaction(
            transaction_type="buy",
            character_id="player_123",
            npc_id="merchant_456",
            item=item,
            player_level=5
        )
        
        # Verify event was published
        assert len(self.published_events) == 1
        event = self.published_events[0]
        assert event.event_type == EconomyEventType.TRANSACTION_COMPLETED
        assert event.data["buyer_id"] == "player_123"
        assert event.data["seller_id"] == "merchant_456"
        assert event.data["item_id"] == "sword_001"
        assert event.data["unit_price"] == 150.0
        assert event.data["transaction_type"] == "buy"
    
    def test_tournament_entry_fee_publishes_event(self):
        """Test that tournament entry fee calculation publishes event."""
        # Mock tournament service
        self.economy_manager.tournament_service.calculate_entry_fee = Mock(
            return_value=(500, {"base_fee": 400, "level_modifier": 1.25})
        )
        
        # Calculate tournament entry fee
        result = self.economy_manager.calculate_tournament_entry_fee(
            tournament_type="standard",
            player_level=10,
            region_id="region_1",
            currency="gold"
        )
        
        # Verify event was published
        assert len(self.published_events) == 1
        event = self.published_events[0]
        assert event.event_type == EconomyEventType.TOURNAMENT_ENTRY_FEE_CALCULATED
        assert event.data["tournament_type"] == "standard"
        assert event.data["player_level"] == 10
        assert event.data["entry_fee"] == 500
    
    def test_economic_tick_publishes_event(self):
        """Test that economic tick processing publishes comprehensive event."""
        # Mock all services
        self.economy_manager.trade_service.process_trade_routes = Mock(return_value=(2, []))
        self.economy_manager.process_expiring_futures = Mock(
            return_value={"processed_count": 1, "settled": [], "expired": []}
        )
        self.economy_manager._generate_economy_events = Mock(return_value=[])
        
        # Process economic tick
        result = self.economy_manager.process_tick(1)
        
        # Verify event was published
        assert len(self.published_events) == 1
        event = self.published_events[0]
        assert event.event_type == EconomyEventType.ECONOMIC_TICK_PROCESSED
        assert event.data["tick_count"] == 1
        assert "duration_seconds" in event.data
        assert event.data["trade_routes_processed"] == 2
        assert event.data["success"] == True
    
    def test_event_data_format_standardization(self):
        """Test that all events follow standard data format."""
        # Create a resource to trigger an event
        mock_resource = Mock()
        mock_resource.id = "test-resource"
        mock_resource.region_id = 1
        mock_resource.resource_type = "iron"
        mock_resource.amount = 100.0
        mock_resource.base_value = 10.0
        mock_resource.rarity = "common"
        mock_resource.is_tradeable = True
        
        self.economy_manager.resource_service.create_resource = Mock(return_value=mock_resource)
        
        resource_data = ResourceData(
            name="Iron Ore",
            resource_type="iron",
            region_id=1,
            amount=100.0
        )
        
        self.economy_manager.create_resource(resource_data)
        
        # Verify event follows standard format
        assert len(self.published_events) == 1
        event = self.published_events[0]
        
        # Check required fields
        assert hasattr(event, 'event_type')
        assert hasattr(event, 'timestamp')
        assert hasattr(event, 'source')
        assert hasattr(event, 'data')
        assert hasattr(event, 'metadata')
        
        # Check event type format
        assert event.event_type.value.startswith("economy.")
        
        # Check source
        assert event.source == "economy_system"
        
        # Check data structure
        assert isinstance(event.data, dict)
        assert isinstance(event.metadata, dict)
    
    def test_event_publishing_error_handling(self):
        """Test that event publishing errors don't break operations."""
        # Mock resource service
        mock_resource = Mock()
        mock_resource.id = "test-resource"
        mock_resource.region_id = 1
        mock_resource.resource_type = "iron"
        mock_resource.amount = 100.0
        mock_resource.base_value = 10.0
        mock_resource.rarity = "common"
        mock_resource.is_tradeable = True
        
        self.economy_manager.resource_service.create_resource = Mock(return_value=mock_resource)
        
        # Mock event bus to raise exception
        def failing_publish(event):
            raise Exception("Event publishing failed")
        
        self.event_bus.publish = failing_publish
        
        # Create resource - should not fail even if event publishing fails
        resource_data = ResourceData(
            name="Iron Ore",
            resource_type="iron",
            region_id=1,
            amount=100.0
        )
        
        result = self.economy_manager.create_resource(resource_data)
        
        # Operation should still succeed
        assert result == mock_resource
        assert self.economy_manager.resource_service.create_resource.called
    
    def teardown_method(self):
        """Clean up after tests."""
        self.published_events.clear()
        self.event_bus.clear_history()


if __name__ == "__main__":
    pytest.main([__file__]) 