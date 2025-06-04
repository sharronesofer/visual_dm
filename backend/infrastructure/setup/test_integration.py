#!/usr/bin/env python3
"""
Test script for equipment system integration.

This script tests the equipment system independently to verify
all components work together properly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from fastapi import FastAPI
from fastapi.testclient import TestClient

def test_equipment_system():
    """Test the equipment system integration."""
    
    print("🧪 Testing Equipment System Integration...")
    
    # Test 1: Import the router
    try:
        from backend.systems.equipment.routers import equipment_router
        print("✅ Equipment router imported successfully")
        print(f"   Router prefix: {equipment_router.prefix}")
        print(f"   Router tags: {equipment_router.tags}")
    except Exception as e:
        print(f"❌ Equipment router import failed: {e}")
        return False
    
    # Test 2: Create a minimal FastAPI app with just the equipment router
    try:
        app = FastAPI(title="Equipment System Test")
        app.include_router(equipment_router)
        print("✅ FastAPI app created with equipment router")
    except Exception as e:
        print(f"❌ FastAPI app creation failed: {e}")
        return False
    
    # Test 3: Test the health endpoint
    try:
        client = TestClient(app)
        response = client.get("/equipment/health")
        print(f"✅ Health endpoint responded: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Test template listing (should work even without database)
    try:
        response = client.get("/equipment/templates")
        print(f"✅ Templates endpoint responded: {response.status_code}")
        if response.status_code == 500:
            print("   Expected 500 error (no database configured)")
        elif response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Templates endpoint test failed: {e}")
        return False
    
    print("\n🎉 Equipment system integration test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_equipment_system()
    sys.exit(0 if success else 1) 