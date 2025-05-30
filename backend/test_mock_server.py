#!/usr/bin/env python3
"""
Mock Server Test Suite
---------------------
Comprehensive test script to validate the Visual DM Mock Server functionality.
Tests all API endpoints and WebSocket communication.
"""

import asyncio
import json
import websockets
import requests
import sys
from datetime import datetime
from typing import Dict, Any

class MockServerTester: pass
    def __init__(self, base_url: str = "http://localhost:8001", ws_url: str = "ws://localhost:8001/ws"): pass
        self.base_url = base_url
        self.ws_url = ws_url
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""): pass
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status} - {test_name}: {details}")
    
    def test_health_check(self): pass
        """Test basic health check endpoint"""
        try: pass
            response = requests.get(f"{self.base_url}/health", timeout=5)
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_test("Health Check", success, f"Status: {response.status_code}, Data: {data}")
            return success
        except Exception as e: pass
            self.log_test("Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_authentication(self): pass
        """Test authentication endpoint"""
        try: pass
            credentials = {"username": "testuser", "password": "testpass"}
            response = requests.post(f"{self.base_url}/auth/login", json=credentials, timeout=5)
            success = response.status_code == 200
            
            if success: pass
                data = response.json()
                self.auth_token = data.get("access_token")
                self.log_test("Authentication", True, f"Token received: {self.auth_token[:20]}...")
            else: pass
                self.log_test("Authentication", False, f"Status: {response.status_code}")
            
            return success
        except Exception as e: pass
            self.log_test("Authentication", False, f"Error: {str(e)}")
            return False
    
    def test_character_crud(self): pass
        """Test character CRUD operations"""
        try: pass
            # Create character
            character_data = {
                "character_id": "test_char_001",
                "character_name": "Test Hero",
                "race": "human",
                "attributes": {
                    "strength": 2,
                    "dexterity": 1,
                    "constitution": 2,
                    "intelligence": 0,
                    "wisdom": 1,
                    "charisma": 1
                },
                "background": "Adventurer",
                "alignment": "chaotic_good"
            }
            
            # POST - Create character
            response = requests.post(f"{self.base_url}/characters", json=character_data, timeout=5)
            if response.status_code == 201: pass
                created_char = response.json()
                char_id = created_char["id"]
                self.log_test("Character Create", True, f"Created character with ID: {char_id}")
                
                # GET - Retrieve character
                response = requests.get(f"{self.base_url}/characters/{char_id}", timeout=5)
                if response.status_code == 200: pass
                    retrieved_char = response.json()
                    self.log_test("Character Retrieve", True, f"Retrieved: {retrieved_char['character_name']}")
                    
                    # PUT - Update character
                    update_data = {"character_name": "Updated Test Hero", "level": 5}
                    response = requests.put(f"{self.base_url}/characters/{char_id}", json=update_data, timeout=5)
                    if response.status_code == 200: pass
                        updated_char = response.json()
                        self.log_test("Character Update", True, f"Updated to: {updated_char['character_name']}")
                        
                        # GET - List characters with filters
                        response = requests.get(f"{self.base_url}/characters?race=human&page=1&per_page=10", timeout=5)
                        if response.status_code == 200: pass
                            char_list = response.json()
                            self.log_test("Character List", True, f"Found {len(char_list['items'])} characters")
                        else: pass
                            self.log_test("Character List", False, f"Status: {response.status_code}")
                    else: pass
                        self.log_test("Character Update", False, f"Status: {response.status_code}")
                else: pass
                    self.log_test("Character Retrieve", False, f"Status: {response.status_code}")
            else: pass
                self.log_test("Character Create", False, f"Status: {response.status_code}")
                
        except Exception as e: pass
            self.log_test("Character CRUD", False, f"Error: {str(e)}")
    
    def test_quest_operations(self): pass
        """Test quest-related operations"""
        try: pass
            # GET - List quests
            response = requests.get(f"{self.base_url}/quests?page=1&per_page=10", timeout=5)
            if response.status_code == 200: pass
                quests = response.json()
                self.log_test("Quest List", True, f"Found {len(quests['items'])} quests")
                
                if quests['items']: pass
                    quest_id = quests['items'][0]['id']
                    
                    # GET - Retrieve specific quest
                    response = requests.get(f"{self.base_url}/quests/{quest_id}", timeout=5)
                    if response.status_code == 200: pass
                        quest = response.json()
                        self.log_test("Quest Retrieve", True, f"Retrieved: {quest['title']}")
                        
                        # POST - Update quest progress
                        progress_data = {
                            "objective_id": quest['objectives'][0]['id'] if quest['objectives'] else "obj_001",
                            "completed": True
                        }
                        response = requests.post(f"{self.base_url}/quests/{quest_id}/progress", json=progress_data, timeout=5)
                        if response.status_code == 200: pass
                            updated_quest = response.json()
                            self.log_test("Quest Progress", True, f"Updated quest status: {updated_quest['status']}")
                        else: pass
                            self.log_test("Quest Progress", False, f"Status: {response.status_code}")
                    else: pass
                        self.log_test("Quest Retrieve", False, f"Status: {response.status_code}")
            else: pass
                self.log_test("Quest List", False, f"Status: {response.status_code}")
                
        except Exception as e: pass
            self.log_test("Quest Operations", False, f"Error: {str(e)}")
    
    def test_time_system(self): pass
        """Test time system operations"""
        try: pass
            # GET - Current time
            response = requests.get(f"{self.base_url}/time/current", timeout=5)
            if response.status_code == 200: pass
                time_data = response.json()
                self.log_test("Time Get", True, f"Current time: {time_data['year']}-{time_data['month']}-{time_data['day']} {time_data['hour']}:{time_data['minute']}")
                
                # POST - Advance time
                advance_data = {"amount": 30, "unit": "minute"}
                response = requests.post(f"{self.base_url}/time/advance", json=advance_data, timeout=5)
                if response.status_code == 200: pass
                    result = response.json()
                    new_time = result['new_time']
                    self.log_test("Time Advance", True, f"Advanced to: {new_time['hour']}:{new_time['minute']}")
                else: pass
                    self.log_test("Time Advance", False, f"Status: {response.status_code}")
            else: pass
                self.log_test("Time Get", False, f"Status: {response.status_code}")
                
        except Exception as e: pass
            self.log_test("Time System", False, f"Error: {str(e)}")
    
    def test_combat_system(self): pass
        """Test combat system operations"""
        try: pass
            # POST - Create combat state
            combat_data = {
                "participants": [
                    {
                        "character_id": "char_001",
                        "initiative": 15,
                        "hit_points": 45,
                        "max_hit_points": 45,
                        "position": {"x": 0.0, "y": 0.0},
                        "status_effects": []
                    }
                ]
            }
            response = requests.post(f"{self.base_url}/combat/state", json=combat_data, timeout=5)
            if response.status_code == 201: pass
                combat_state = response.json()
                combat_id = combat_state["combat_id"]
                self.log_test("Combat Create", True, f"Created combat: {combat_id}")
                
                # GET - Retrieve combat state
                response = requests.get(f"{self.base_url}/combat/state/{combat_id}", timeout=5)
                if response.status_code == 200: pass
                    retrieved_state = response.json()
                    self.log_test("Combat Retrieve", True, f"Combat status: {retrieved_state['status']}")
                else: pass
                    self.log_test("Combat Retrieve", False, f"Status: {response.status_code}")
            else: pass
                self.log_test("Combat Create", False, f"Status: {response.status_code}")
                
        except Exception as e: pass
            self.log_test("Combat System", False, f"Error: {str(e)}")
    
    def test_region_system(self): pass
        """Test region system operations"""
        try: pass
            # GET - List regions
            response = requests.get(f"{self.base_url}/regions", timeout=5)
            if response.status_code == 200: pass
                regions = response.json()
                self.log_test("Region List", True, f"Found {len(regions['items'])} regions")
                
                if regions['items']: pass
                    region_id = regions['items'][0]['id']
                    
                    # GET - Retrieve specific region
                    response = requests.get(f"{self.base_url}/regions/{region_id}", timeout=5)
                    if response.status_code == 200: pass
                        region = response.json()
                        self.log_test("Region Retrieve", True, f"Retrieved region: {region['name']}")
                    else: pass
                        self.log_test("Region Retrieve", False, f"Status: {response.status_code}")
            else: pass
                self.log_test("Region List", False, f"Status: {response.status_code}")
                
        except Exception as e: pass
            self.log_test("Region System", False, f"Error: {str(e)}")
    
    async def test_websocket(self): pass
        """Test WebSocket communication"""
        try: pass
            uri = self.ws_url
            async with websockets.connect(uri) as websocket: pass
                # Wait for welcome message
                welcome_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                welcome_data = json.loads(welcome_msg)
                self.log_test("WebSocket Connect", True, f"Received: {welcome_data['type']}")
                
                # Send test message
                test_message = {
                    "type": "ping",
                    "data": {"message": "Hello from test client"},
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(test_message))
                
                # Wait for echo response
                response_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                response_data = json.loads(response_msg)
                self.log_test("WebSocket Echo", True, f"Echo type: {response_data['type']}")
                
        except Exception as e: pass
            self.log_test("WebSocket Communication", False, f"Error: {str(e)}")
    
    def test_error_handling(self): pass
        """Test error handling for invalid requests"""
        try: pass
            # Test 404 for non-existent character
            response = requests.get(f"{self.base_url}/characters/nonexistent", timeout=5)
            if response.status_code == 404: pass
                self.log_test("404 Error Handling", True, "Correctly returned 404 for missing character")
            else: pass
                self.log_test("404 Error Handling", False, f"Expected 404, got {response.status_code}")
            
            # Test 401 for invalid credentials
            bad_credentials = {"username": "invalid", "password": "wrong"}
            response = requests.post(f"{self.base_url}/auth/login", json=bad_credentials, timeout=5)
            if response.status_code == 401: pass
                self.log_test("401 Error Handling", True, "Correctly returned 401 for invalid credentials")
            else: pass
                self.log_test("401 Error Handling", False, f"Expected 401, got {response.status_code}")
                
        except Exception as e: pass
            self.log_test("Error Handling", False, f"Error: {str(e)}")
    
    def run_all_tests(self): pass
        """Run all test suites"""
        print("🧪 Starting Visual DM Mock Server Test Suite")
        print("=" * 60)
        
        # Test if server is running
        if not self.test_health_check(): pass
            print("❌ Mock server is not running. Please start the server first:")
            print("   python backend/mock_server.py")
            return False
        
        # Run all tests
        self.test_authentication()
        self.test_character_crud()
        self.test_quest_operations()
        self.test_time_system()
        self.test_combat_system()
        self.test_region_system()
        self.test_error_handling()
        
        # Run WebSocket test
        print("\n🔌 Testing WebSocket Communication...")
        try: pass
            asyncio.run(self.test_websocket())
        except Exception as e: pass
            self.log_test("WebSocket Test", False, f"Error: {str(e)}")
        
        # Print summary
        self.print_summary()
        
        return all(result["success"] for result in self.test_results)
    
    def print_summary(self): pass
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100: pass
            print("\n🎉 ALL TESTS PASSED! Mock server is working correctly.")
        elif success_rate >= 80: pass
            print("\n⚠️  Most tests passed, but some issues found.")
        else: pass
            print("\n❌ Multiple test failures. Please check mock server implementation.")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests: pass
            print("\n❌ FAILED TESTS:")
            for test in failed_tests: pass
                print(f"   - {test['test']}: {test['details']}")

def main(): pass
    """Main test runner"""
    tester = MockServerTester()
    
    print("🎮 Visual DM Mock Server Test Suite")
    print("📍 Testing server at: http://localhost:8001")
    print("🔌 Testing WebSocket at: ws://localhost:8001/ws")
    print()
    
    success = tester.run_all_tests()
    
    if success: pass
        print("\n✅ Mock server validation complete - ready for Unity integration!")
        return 0
    else: pass
        print("\n❌ Mock server validation failed - please fix issues before proceeding.")
        return 1

if __name__ == "__main__": pass
    sys.exit(main()) 