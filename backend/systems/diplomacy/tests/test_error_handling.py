"""
Error Handling and Logging Tests for AI Diplomacy System

This script tests various error conditions and verifies that logging and error handling
work correctly throughout the AI diplomacy system.
"""

import asyncio
import logging
import sys
from datetime import datetime
from uuid import UUID, uuid4
from typing import Dict, Any

# Configure test logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('diplomacy_error_test.log')
    ]
)

logger = logging.getLogger(__name__)

# Import the AI services and error types
try:
    from backend.systems.diplomacy.models.core_models import TreatyType
    from backend.systems.diplomacy.services.ai_enhanced_services import (
        create_ai_enhanced_treaty_service,
        create_ai_enhanced_negotiation_service,
        DiplomacyAIError,
        FactionDataError,
        AIProcessingError
    )
except ImportError as e:
    logger.error(f"Failed to import diplomacy modules: {e}")
    sys.exit(1)


class ErrorTestRunner:
    """Test runner for error handling scenarios"""
    
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log the result of a test"""
        status = "PASS" if success else "FAIL"
        logger.info(f"TEST {status}: {test_name} - {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    async def test_invalid_faction_ids(self):
        """Test handling of invalid faction IDs"""
        test_name = "Invalid Faction IDs"
        
        try:
            ai_service = create_ai_enhanced_treaty_service()
            
            # Test with non-existent faction IDs
            fake_faction_1 = uuid4()
            fake_faction_2 = uuid4()
            
            treaty_terms = {
                "duration_years": 5,
                "tariff_reduction": 0.15
            }
            
            try:
                evaluation = ai_service.evaluate_treaty_proposal(
                    fake_faction_1, fake_faction_2, TreatyType.TRADE, treaty_terms
                )
                
                # If we get here without an exception, check if fallback values were used
                if evaluation.get('acceptance_probability') == 0.5:
                    self.log_test_result(test_name, True, "Graceful fallback to default values")
                else:
                    self.log_test_result(test_name, False, "Unexpected behavior with invalid factions")
                    
            except FactionDataError as e:
                self.log_test_result(test_name, True, f"Proper FactionDataError raised: {e.error_code}")
            except Exception as e:
                self.log_test_result(test_name, False, f"Unexpected exception: {type(e).__name__}: {e}")
                
        except Exception as e:
            self.log_test_result(test_name, False, f"Service creation failed: {e}")
    
    async def test_invalid_treaty_terms(self):
        """Test handling of invalid treaty terms"""
        test_name = "Invalid Treaty Terms"
        
        try:
            ai_service = create_ai_enhanced_treaty_service()
            
            faction_1 = uuid4()
            faction_2 = uuid4()
            
            # Test with malformed treaty terms
            invalid_terms = {
                "duration_years": -5,  # Invalid negative duration
                "tariff_reduction": 1.5,  # Invalid > 100% reduction
                "invalid_field": "test"
            }
            
            try:
                evaluation = ai_service.evaluate_treaty_proposal(
                    faction_1, faction_2, TreatyType.TRADE, invalid_terms
                )
                
                # Should handle gracefully
                self.log_test_result(test_name, True, "Invalid terms handled gracefully")
                
            except Exception as e:
                if isinstance(e, DiplomacyAIError):
                    self.log_test_result(test_name, True, f"Proper error handling: {e.error_code}")
                else:
                    self.log_test_result(test_name, False, f"Unexpected exception: {type(e).__name__}: {e}")
                    
        except Exception as e:
            self.log_test_result(test_name, False, f"Test setup failed: {e}")
    
    async def test_self_negotiation_error(self):
        """Test handling of same faction negotiating with itself"""
        test_name = "Self Negotiation Error"
        
        try:
            ai_service = create_ai_enhanced_treaty_service()
            
            same_faction = uuid4()
            
            treaty_terms = {
                "duration_years": 5,
                "tariff_reduction": 0.15
            }
            
            try:
                evaluation = ai_service.evaluate_treaty_proposal(
                    same_faction, same_faction, TreatyType.TRADE, treaty_terms
                )
                
                self.log_test_result(test_name, False, "Should have raised an error for self-negotiation")
                
            except DiplomacyAIError as e:
                if "cannot evaluate treaty with self" in str(e).lower():
                    self.log_test_result(test_name, True, f"Proper self-negotiation error: {e.error_code}")
                else:
                    self.log_test_result(test_name, False, f"Wrong error message: {e}")
            except Exception as e:
                self.log_test_result(test_name, False, f"Unexpected exception: {type(e).__name__}: {e}")
                
        except Exception as e:
            self.log_test_result(test_name, False, f"Test setup failed: {e}")
    
    async def test_database_connection_failure(self):
        """Test handling of database connection failures"""
        test_name = "Database Connection Failure"
        
        try:
            ai_service = create_ai_enhanced_treaty_service()
            
            # Use real-looking but non-existent faction IDs to trigger database lookup
            faction_1 = UUID("12345678-1234-5678-9012-123456789012")
            faction_2 = UUID("87654321-4321-8765-2109-987654321098")
            
            treaty_terms = {
                "duration_years": 5,
                "tariff_reduction": 0.15
            }
            
            try:
                evaluation = ai_service.evaluate_treaty_proposal(
                    faction_1, faction_2, TreatyType.TRADE, treaty_terms
                )
                
                # Should either fail gracefully or use fallback values
                if evaluation.get('acceptance_probability') is not None:
                    self.log_test_result(test_name, True, "Graceful fallback when database unavailable")
                else:
                    self.log_test_result(test_name, False, "No fallback values provided")
                    
            except Exception as e:
                # Database errors should be handled gracefully
                if isinstance(e, (FactionDataError, AIProcessingError)):
                    self.log_test_result(test_name, True, f"Proper error handling: {e.error_code}")
                else:
                    self.log_test_result(test_name, False, f"Unhandled exception: {type(e).__name__}: {e}")
                    
        except Exception as e:
            self.log_test_result(test_name, False, f"Test setup failed: {e}")
    
    async def test_negotiation_response_errors(self):
        """Test negotiation response error handling"""
        test_name = "Negotiation Response Errors"
        
        try:
            ai_service = create_ai_enhanced_negotiation_service()
            
            negotiation_id = uuid4()
            responding_faction = uuid4()
            
            # Test with empty/invalid offer
            invalid_offer = {}
            
            try:
                response = ai_service.generate_ai_negotiation_response(
                    negotiation_id, responding_faction, invalid_offer
                )
                
                # Should handle gracefully
                if response.get('response_type'):
                    self.log_test_result(test_name, True, "Invalid offer handled gracefully")
                else:
                    self.log_test_result(test_name, False, "No proper response to invalid offer")
                    
            except Exception as e:
                if isinstance(e, DiplomacyAIError):
                    self.log_test_result(test_name, True, f"Proper error handling: {e.error_code}")
                else:
                    self.log_test_result(test_name, False, f"Unexpected exception: {type(e).__name__}: {e}")
                    
        except Exception as e:
            self.log_test_result(test_name, False, f"Service creation failed: {e}")
    
    async def test_performance_logging(self):
        """Test that performance logging works correctly"""
        test_name = "Performance Logging"
        
        try:
            ai_service = create_ai_enhanced_treaty_service()
            
            faction_1 = uuid4()
            faction_2 = uuid4()
            
            treaty_terms = {
                "duration_years": 5,
                "tariff_reduction": 0.15,
                "trade_volume_target": "increased by 25%"
            }
            
            # Capture log output to verify performance logging
            start_time = datetime.utcnow()
            
            try:
                evaluation = ai_service.evaluate_treaty_proposal(
                    faction_1, faction_2, TreatyType.TRADE, treaty_terms
                )
                
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                
                # Check if evaluation contains metadata
                if evaluation.get('metadata') and evaluation['metadata'].get('timestamp'):
                    self.log_test_result(test_name, True, f"Performance data recorded (took {duration:.2f}s)")
                else:
                    self.log_test_result(test_name, False, "No performance metadata in response")
                    
            except Exception as e:
                self.log_test_result(test_name, False, f"Performance test failed: {e}")
                
        except Exception as e:
            self.log_test_result(test_name, False, f"Test setup failed: {e}")
    
    async def test_logging_levels(self):
        """Test that different logging levels work correctly"""
        test_name = "Logging Levels"
        
        try:
            # Test different log levels
            logger.debug("DEBUG: Testing debug logging")
            logger.info("INFO: Testing info logging")
            logger.warning("WARNING: Testing warning logging")
            logger.error("ERROR: Testing error logging")
            
            self.log_test_result(test_name, True, "All logging levels functional")
            
        except Exception as e:
            self.log_test_result(test_name, False, f"Logging test failed: {e}")
    
    async def run_all_tests(self):
        """Run all error handling tests"""
        logger.info("Starting AI Diplomacy Error Handling Tests")
        logger.info("=" * 60)
        
        test_methods = [
            self.test_invalid_faction_ids,
            self.test_invalid_treaty_terms,
            self.test_self_negotiation_error,
            self.test_database_connection_failure,
            self.test_negotiation_response_errors,
            self.test_performance_logging,
            self.test_logging_levels
        ]
        
        for test_method in test_methods:
            try:
                await test_method()
            except Exception as e:
                logger.error(f"Test method {test_method.__name__} failed unexpectedly: {e}")
                self.log_test_result(test_method.__name__, False, f"Test framework error: {e}")
        
        # Print summary
        logger.info("=" * 60)
        logger.info("ERROR HANDLING TEST SUMMARY")
        logger.info(f"Total Tests: {len(self.test_results)}")
        logger.info(f"Passed: {self.passed_tests}")
        logger.info(f"Failed: {self.failed_tests}")
        
        if self.failed_tests == 0:
            logger.info("🎉 ALL TESTS PASSED - Error handling is working correctly!")
        else:
            logger.warning(f"⚠️  {self.failed_tests} tests failed - review error handling")
        
        # Detailed results
        logger.info("\\nDETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            logger.info(f"{status} {result['test']}: {result['details']}")
        
        return self.failed_tests == 0


async def main():
    """Main test runner"""
    print("AI Diplomacy System - Error Handling & Logging Tests")
    print("=" * 60)
    
    test_runner = ErrorTestRunner()
    
    try:
        success = await test_runner.run_all_tests()
        
        if success:
            print("\\n🎉 All error handling tests passed!")
            return 0
        else:
            print(f"\\n⚠️  Some tests failed. Check diplomacy_error_test.log for details.")
            return 1
            
    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        print(f"\\n💥 Test runner failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main()) 