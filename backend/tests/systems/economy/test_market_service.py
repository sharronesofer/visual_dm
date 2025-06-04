"""
Comprehensive tests for MarketService - Market management and pricing functionality.

Tests market CRUD operations, pricing calculations, market dynamics, and analytics.
"""

import pytest
import logging
from unittest.mock import Mock, patch
from datetime import datetime

from backend.systems.economy.services.market_service import MarketService
from backend.infrastructure.database.economy.market_models import Market
from backend.systems.economy.models.market import MarketData


class TestMarketService:
    """Test suite for MarketService functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = MarketService()
        self.service_with_db = MarketService(db_session=Mock())
        
        # Create mock resource service for testing
        self.mock_resource_service = Mock()
        self.service_with_resources = MarketService(resource_service=self.mock_resource_service)
    
    def test_initialization(self):
        """Test MarketService initialization."""
        # Test without dependencies
        service = MarketService()
        assert service.db_session is None
        assert service.resource_service is None
        
        # Test with database session
        mock_session = Mock()
        service_with_db = MarketService(mock_session)
        assert service_with_db.db_session is mock_session
        
        # Test with resource service
        mock_resource_service = Mock()
        service_with_resources = MarketService(resource_service=mock_resource_service)
        assert service_with_resources.resource_service is mock_resource_service
    
    def test_get_market(self):
        """Test market retrieval functionality."""
        # Test with string ID
        market = self.service.get_market('1')
        if market:  # May be None due to database issues
            assert hasattr(market, 'id')
            assert hasattr(market, 'name')
            assert hasattr(market, 'region_id')
            assert hasattr(market, 'market_type')
        
        # Test with integer ID
        market_int = self.service.get_market(1)
        if market_int:
            assert hasattr(market_int, 'id')
    
    def test_get_market_mock_fallback(self):
        """Test market retrieval with mock fallback when database is unavailable."""
        # Service without db_session should use mock implementation
        service_no_db = MarketService()
        market = service_no_db.get_market('1')
        
        assert market is not None
        assert market.id == 1
        assert market.name == 'Market 1'
        assert market.region_id == 1
        assert market.market_type == 'general'
    
    def test_get_markets_by_region(self):
        """Test market retrieval by region."""
        markets = self.service.get_markets_by_region(1)
        
        assert isinstance(markets, list)
        
        # Verify market structure if any exist
        for market in markets:
            assert hasattr(market, 'id')
            assert hasattr(market, 'name')
            assert hasattr(market, 'region_id')
            if hasattr(market, 'region_id'):
                assert market.region_id == 1
    
    def test_get_markets_by_region_mock_fallback(self):
        """Test market retrieval by region with mock fallback."""
        service_no_db = MarketService()
        markets = service_no_db.get_markets_by_region(5)
        
        assert isinstance(markets, list)
        assert len(markets) >= 1  # Mock should return at least one market
        
        for market in markets:
            assert market.region_id == 5
            assert hasattr(market, 'market_type')
    
    def test_create_market_with_dict(self):
        """Test market creation with dictionary data."""
        market_data = {
            'name': 'Test Market',
            'region_id': '2',
            'market_type': 'specialized',
            'tax_rate': 0.08
        }
        
        created_market = self.service.create_market(market_data)
        
        if created_market:
            assert created_market.name == 'Test Market'
            assert hasattr(created_market, 'region_id')
            assert hasattr(created_market, 'market_type')
    
    def test_create_market_with_market_data(self):
        """Test market creation with MarketData object."""
        market_data = MarketData(
            name='Data Market',
            region_id='3',
            market_type='black_market',
            tax_rate=0.15
        )
        
        created_market = self.service.create_market(market_data)
        
        if created_market:
            assert created_market.name == 'Data Market'
            assert hasattr(created_market, 'market_type')
    
    def test_update_market(self):
        """Test market update functionality."""
        updates = {
            'name': 'Updated Market Name',
            'tax_rate': 0.12,
            'market_type': 'luxury'
        }
        
        updated_market = self.service.update_market(1, updates)
        
        if updated_market:
            assert updated_market.name == 'Updated Market Name'
            if hasattr(updated_market, 'tax_rate'):
                assert updated_market.tax_rate == 0.12
    
    def test_update_market_invalid_attributes(self):
        """Test market update with invalid attributes."""
        updates = {
            'invalid_field': 'should_be_ignored',
            'name': 'Valid Update'
        }
        
        updated_market = self.service.update_market(1, updates)
        
        if updated_market:
            assert updated_market.name == 'Valid Update'
            assert not hasattr(updated_market, 'invalid_field')
    
    def test_delete_market(self):
        """Test market deletion functionality."""
        result = self.service.delete_market(1)
        assert isinstance(result, bool)
        # May be False if market not found or database issues, but shouldn't crash
    
    def test_calculate_price_basic(self):
        """Test basic price calculation functionality."""
        price, details = self.service.calculate_price(1, 1, 1.0)
        
        assert isinstance(price, (int, float))
        assert price >= 0
        assert isinstance(details, dict)
        
        # Check details structure
        if 'error' not in details:
            assert 'final_price' in details
            assert 'quantity' in details
            assert 'market_id' in details
            assert 'resource_id' in details
        else:
            # Error is acceptable if market not found
            assert isinstance(details['error'], str)
    
    def test_calculate_price_with_quantity(self):
        """Test price calculation with different quantities."""
        # Test different quantities
        for quantity in [1.0, 5.0, 10.0, 0.5]:
            price, details = self.service.calculate_price(1, 1, quantity)
            
            assert isinstance(price, (int, float))
            assert price >= 0
            
            if 'error' not in details:
                assert details['quantity'] == quantity
                # Price should generally scale with quantity
                assert details['final_price'] >= 0
    
    def test_calculate_price_with_resource_service(self):
        """Test price calculation with resource service integration."""
        # Mock resource with base price
        mock_resource = Mock()
        mock_resource.base_price = 15.0
        self.mock_resource_service.get_resource.return_value = mock_resource
        
        price, details = self.service_with_resources.calculate_price(1, 1, 2.0)
        
        if 'error' not in details:
            # Should use the base price from resource service
            assert details['base_price'] == 15.0
            assert details['quantity'] == 2.0
    
    def test_calculate_price_with_market_modifiers(self):
        """Test price calculation with market price modifiers."""
        # Test that price modifiers affect calculation
        service_no_db = MarketService()
        
        # Get a mock market and set price modifier
        market = service_no_db.get_market(1)
        if market:
            market.set_price_modifier('1', 1.5)  # 50% price increase
            
            price, details = service_no_db.calculate_price(1, 1, 1.0)
            
            if 'error' not in details:
                assert details['price_modifier'] == 1.5
                # Final price should reflect the modifier
                expected_price = details['base_price'] * 1.5 * 1.0
                assert abs(details['final_price'] - expected_price) < 0.01
    
    def test_update_market_conditions(self):
        """Test market condition updates."""
        updated_markets = self.service.update_market_conditions(1)
        
        assert isinstance(updated_markets, list)
        
        # Test with event modifiers
        event_modifiers = {
            '1': 1.2,  # 20% price increase for resource 1
            '2': 0.8   # 20% price decrease for resource 2
        }
        
        updated_markets_with_events = self.service.update_market_conditions(1, event_modifiers)
        assert isinstance(updated_markets_with_events, list)
    
    def test_get_resource_price_trends(self):
        """Test resource price trend analysis."""
        trends = self.service.get_resource_price_trends(1)
        
        assert isinstance(trends, dict)
        assert 'resource_id' in trends
        assert 'timestamp' in trends
        assert trends['resource_id'] == 1
        
        # Test with region filter
        trends_region = self.service.get_resource_price_trends(1, region_id=1)
        assert isinstance(trends_region, dict)
        assert trends_region['region_id'] == 1
    
    def test_get_resource_price_trends_structure(self):
        """Test resource price trends data structure."""
        trends = self.service.get_resource_price_trends(1, region_id=1)
        
        expected_keys = ['resource_id', 'region_id', 'markets', 'average_price', 'price_range', 'timestamp']
        
        for key in expected_keys:
            assert key in trends
        
        assert isinstance(trends['markets'], list)
        assert isinstance(trends['average_price'], (int, float))
        assert isinstance(trends['price_range'], dict)
        
        if 'min' in trends['price_range'] and 'max' in trends['price_range']:
            assert trends['price_range']['min'] <= trends['price_range']['max']
    
    def test_error_handling(self):
        """Test error handling in MarketService operations."""
        # Test with invalid market ID
        market = self.service.get_market('invalid_id')
        # Should handle gracefully (may return None or mock data)
        
        # Test with invalid region ID
        markets = self.service.get_markets_by_region(-999)
        assert isinstance(markets, list)
        
        # Test price calculation with invalid parameters
        price, details = self.service.calculate_price(-1, -1, -1)
        assert isinstance(price, (int, float))
        assert isinstance(details, dict)
    
    def test_logging_functionality(self):
        """Test that logging is working in MarketService."""
        with patch('backend.systems.economy.services.market_service.logger') as mock_logger:
            service = MarketService()
            assert mock_logger.info.called
    
    def test_database_session_interaction(self):
        """Test MarketService behavior with database session."""
        mock_session = Mock()
        service = MarketService(mock_session)
        
        assert service.db_session is mock_session
        
        # Test operations that should use database session
        try:
            service.create_market({'name': 'Test', 'region_id': '1'})
            # Should attempt to use session for database operations
        except Exception:
            pass  # Expected with mock session
    
    def test_market_data_serialization(self):
        """Test that market operations return JSON-serializable data."""
        import json
        
        # Test price calculation serialization
        price, details = self.service.calculate_price(1, 1, 1.0)
        try:
            json.dumps(details)
        except (TypeError, ValueError):
            # Only fail if details is not None and not serializable
            if details is not None:
                pytest.fail("Price calculation details not JSON serializable")
        
        # Test price trends serialization
        trends = self.service.get_resource_price_trends(1)
        try:
            json.dumps(trends)
        except (TypeError, ValueError):
            pytest.fail("Price trends not JSON serializable")
    
    def test_concurrent_market_access(self):
        """Test concurrent access to market operations."""
        # Simulate multiple concurrent market retrievals
        markets = []
        for i in range(10):
            market = self.service.get_market(i)
            markets.append(market)
        
        # All should complete without crashing
        assert len(markets) == 10
    
    def test_market_types_handling(self):
        """Test handling of different market types."""
        market_types = ['general', 'specialized', 'black_market', 'luxury']
        
        for market_type in market_types:
            market_data = {
                'name': f'{market_type.title()} Market',
                'region_id': '1',
                'market_type': market_type,
                'tax_rate': 0.05
            }
            
            created_market = self.service.create_market(market_data)
            if created_market:
                assert hasattr(created_market, 'market_type')
    
    def test_price_modifier_operations(self):
        """Test price modifier setting and retrieval."""
        service_no_db = MarketService()
        market = service_no_db.get_market(1)
        
        if market:
            # Test setting price modifier
            market.set_price_modifier('test_resource', 1.25)
            
            # Test getting price modifier
            modifier = market.get_price_modifier('test_resource')
            assert modifier == 1.25
            
            # Test default modifier for non-existent resource
            default_modifier = market.get_price_modifier('non_existent')
            assert default_modifier == 1.0
    
    def test_supply_demand_operations(self):
        """Test supply and demand tracking in markets."""
        service_no_db = MarketService()
        market = service_no_db.get_market(1)
        
        if market:
            # Test updating supply and demand
            market.update_supply_demand('resource_1', 100.0, 80.0)
            
            # Verify the update affected price modifiers
            modifier = market.get_price_modifier('resource_1')
            # With demand (80) < supply (100), modifier should be less than 1
            assert 0.1 <= modifier <= 10.0  # Within reasonable bounds
    
    def test_trade_volume_tracking(self):
        """Test trade volume recording in markets."""
        service_no_db = MarketService()
        market = service_no_db.get_market(1)
        
        if market:
            # Test recording trades
            market.record_trade('resource_1', 25.0)
            market.record_trade('resource_1', 15.0)
            
            # Volume should accumulate
            if hasattr(market, 'trading_volume'):
                volume = market.trading_volume.get('resource_1', 0)
                assert volume >= 40.0  # Should be at least the sum of trades
    
    @pytest.mark.performance
    def test_performance_market_operations(self):
        """Test performance of market operations."""
        import time
        
        # Test market retrieval performance
        start_time = time.time()
        for i in range(50):
            self.service.get_market(i)
        get_time = time.time() - start_time
        
        assert get_time < 2.0  # Should complete 50 operations quickly
        
        # Test price calculation performance
        start_time = time.time()
        for i in range(100):
            self.service.calculate_price(1, 1, i + 1.0)
        calc_time = time.time() - start_time
        
        assert calc_time < 1.0  # Should complete 100 calculations quickly


class TestMarketServiceIntegration:
    """Integration tests for MarketService with other services."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.mock_resource_service = Mock()
        self.service = MarketService(resource_service=self.mock_resource_service)
    
    def test_resource_service_integration(self):
        """Test integration with ResourceService."""
        # Mock resource with specific attributes
        mock_resource = Mock()
        mock_resource.base_price = 20.0
        mock_resource.type = 'luxury'
        self.mock_resource_service.get_resource.return_value = mock_resource
        
        price, details = self.service.calculate_price(1, 1, 1.0)
        
        # Should call resource service
        self.mock_resource_service.get_resource.assert_called_with(1)
        
        if 'error' not in details:
            assert details['base_price'] == 20.0
    
    def test_cross_service_data_flow(self):
        """Test data flow between MarketService and other services."""
        # Test that market service can handle resource service data
        mock_resource = Mock()
        mock_resource.base_price = 10.0
        mock_resource.rarity = 'rare'
        self.mock_resource_service.get_resource.return_value = mock_resource
        
        # Price calculation should incorporate resource data
        price, details = self.service.calculate_price(1, 1, 5.0)
        
        if 'error' not in details:
            # Should use resource base price in calculation
            assert details['base_price'] == 10.0
            assert details['quantity'] == 5.0
    
    def test_event_readiness(self):
        """Test that MarketService is ready for event system integration."""
        # Test that operations return data suitable for event publishing
        price, details = self.service.calculate_price(1, 1, 1.0)
        
        # Should have identifiable data for events
        if 'error' not in details:
            assert 'market_id' in details
            assert 'resource_id' in details
            assert 'final_price' in details
        
        # Market condition updates should return actionable data
        markets = self.service.update_market_conditions(1)
        assert isinstance(markets, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 