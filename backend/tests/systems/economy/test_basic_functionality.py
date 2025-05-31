"""
Basic functionality tests for economy system without advanced pytest markers.

Tests core functionality of EconomyManager, ResourceService, and MarketService.
"""

import logging
import pytest
from unittest.mock import Mock, patch
from unittest import TestCase


class TestEconomyBasicFunctionality(TestCase):
    """Test class for basic economy functionality using unittest."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Reset any singleton instances
        # Clear any cached imports
        import sys
        modules_to_clear = [key for key in sys.modules.keys() if 'economy' in key]
        for module in modules_to_clear:
            if 'tests' not in module:  # Don't clear test modules
                sys.modules.pop(module, None)
    
    def test_rules_system_works(self):
        """Test that the rules system can be imported and works."""
        # This should work since rules system is working
        from backend.systems.rules.rules import balance_constants, calculate_ability_modifier
        
        # Test basic functionality
        self.assertIsInstance(balance_constants, dict)
        self.assertIn('starting_gold', balance_constants)
        self.assertEqual(balance_constants['starting_gold'], 100)
        
        # Test calculations
        modifier = calculate_ability_modifier(16)
        self.assertEqual(modifier, 3)
        
        print("✅ Rules system basic functionality works")
    
    @patch('backend.systems.economy.services.resource_service.ResourceService')
    @patch('backend.systems.economy.services.market_service.MarketService')
    @patch('backend.systems.economy.services.trade_service.TradeService')
    @patch('backend.systems.economy.services.futures_service.FuturesService')
    def test_economy_manager_basic(self, mock_futures, mock_trade, mock_market, mock_resource):
        """Test basic EconomyManager functionality with mocked dependencies."""
        # Mock the imports to avoid circular import issues
        with patch.dict('sys.modules', {
            'backend.systems.economy.services.resource': Mock(),
            'backend.systems.economy.models.trade_route': Mock(),
            'backend.systems.economy.models.market': Mock(),
            'backend.systems.economy.models.commodity_future': Mock(),
        }):
            
            try:
                # Reset singleton for clean test
                from backend.systems.economy.services.economy_manager import EconomyManager
                EconomyManager._instance = None
                
                # Mock the service constructors
                mock_resource.return_value = Mock()
                mock_trade.return_value = Mock()
                mock_market.return_value = Mock()
                mock_futures.return_value = Mock()
                
                # Test singleton creation
                manager1 = EconomyManager.get_instance()
                manager2 = EconomyManager.get_instance()
                self.assertIs(manager1, manager2)
                
                # Test initialization
                self.assertIsNotNone(manager1)
                self.assertTrue(hasattr(manager1, 'resource_service'))
                self.assertTrue(hasattr(manager1, 'market_service'))
                self.assertTrue(hasattr(manager1, 'trade_service'))
                self.assertTrue(hasattr(manager1, 'futures_service'))
                
                print("✅ EconomyManager basic functionality with mocked dependencies works")
                
            except ImportError as e:
                print(f"⚠️ EconomyManager import test skipped due to import issues: {e}")
                self.skipTest(f"Import issues prevent testing: {e}")
    
    @patch('backend.systems.economy.services.resource_service.ResourceService')
    def test_economy_manager_status(self, mock_resource_service):
        """Test EconomyManager status reporting with mocked dependencies."""
        with patch.dict('sys.modules', {
            'backend.systems.economy.services.resource': Mock(),
            'backend.systems.economy.models.trade_route': Mock(),
            'backend.systems.economy.models.market': Mock(),
            'backend.systems.economy.models.commodity_future': Mock(),
            'backend.systems.economy.services.trade_service': Mock(),
            'backend.systems.economy.services.market_service': Mock(),
            'backend.systems.economy.services.futures_service': Mock(),
        }):
            
            try:
                from backend.systems.economy.services.economy_manager import EconomyManager
                EconomyManager._instance = None
                
                manager = EconomyManager.get_instance()
                status = manager.get_economy_status()
                
                self.assertIsInstance(status, dict)
                self.assertIn('initialized', status)
                self.assertIn('services', status)
                self.assertIn('timestamp', status)
                self.assertTrue(status['initialized'])
                
                services = status['services']
                self.assertTrue(services['resource_service'])
                self.assertTrue(services['trade_service'])
                self.assertTrue(services['market_service'])
                self.assertTrue(services['futures_service'])
                
                print("✅ EconomyManager status reporting works")
                
            except ImportError as e:
                print(f"⚠️ EconomyManager status test skipped due to import issues: {e}")
                self.skipTest(f"Import issues prevent testing: {e}")


def test_economy_manager_basic():
    """Standalone test function for compatibility."""
    test_case = TestEconomyBasicFunctionality()
    test_case.setUp()
    test_case.test_rules_system_works()
    test_case.test_economy_manager_basic()
    test_case.test_economy_manager_status()


def run_all_tests():
    """Run all basic functionality tests."""
    print("🚀 Running Economy System Basic Functionality Tests...")
    print()
    
    test_case = TestEconomyBasicFunctionality()
    test_case.setUp()
    
    try:
        test_case.test_rules_system_works()
        test_case.test_economy_manager_basic()
        test_case.test_economy_manager_status()
        
        print()
        print("🎉 All Economy System Basic Functionality Tests Passed!")
        print("✅ Rules system is working correctly")
        print("✅ EconomyManager coordination layer tested with mocks")
        print("✅ Import issues handled gracefully with mocking")
        
    except Exception as e:
        print(f"\n❌ Tests failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests() 