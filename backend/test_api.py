#!/usr/bin/env python3
"""
Test script to start backend and test API endpoints
"""
import subprocess
import time
import sys
import signal
import os
import requests
import json

def test_backend_endpoints(): pass
    """Test backend startup and endpoints."""
    print("🚀 Starting backend for API testing...")
    
    # Start the backend process
    proc = subprocess.Popen([sys.executable, 'simple_start.py'], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           preexec_fn=os.setsid)
    
    # Wait for startup
    print("⏳ Waiting for backend to start...")
    time.sleep(8)
    
    success = True
    
    try: pass
        # Test root endpoint
        print("🔍 Testing root endpoint...")
        response = requests.get('http://localhost:8000', timeout=10)
        if response.status_code == 200: pass
            print(f"✅ Root endpoint: {response.json()}")
        else: pass
            print(f"❌ Root endpoint failed with status {response.status_code}")
            success = False
        
        # Test docs endpoint
        print("🔍 Testing docs endpoint...")
        response = requests.get('http://localhost:8000/docs', timeout=10)
        if response.status_code == 200: pass
            print("✅ Docs endpoint accessible")
        else: pass
            print(f"❌ Docs endpoint failed with status {response.status_code}")
            success = False
            
        # Test openapi.json
        print("🔍 Testing OpenAPI spec...")
        response = requests.get('http://localhost:8000/openapi.json', timeout=10)
        if response.status_code == 200: pass
            spec = response.json()
            print(f"✅ OpenAPI spec available, title: {spec.get('info', {}).get('title', 'Unknown')}")
            
            # List available endpoints
            paths = spec.get('paths', {})
            print(f"📝 Available endpoints ({len(paths)} total):")
            for path in sorted(paths.keys()): pass
                methods = list(paths[path].keys())
                print(f"   {path}: {', '.join(methods).upper()}")
        else: pass
            print(f"❌ OpenAPI spec failed with status {response.status_code}")
            success = False
            
    except requests.exceptions.ConnectionError: pass
        print("❌ Could not connect to backend")
        success = False
    except requests.exceptions.Timeout: pass
        print("❌ Request timed out")
        success = False
    except Exception as e: pass
        print(f"❌ Test failed with error: {e}")
        success = False
    
    # Clean up
    try: pass
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except: pass
        proc.terminate()
    
    proc.wait()
    
    if success: pass
        print("\n🎉 All backend tests passed!")
    else: pass
        print("\n❌ Some backend tests failed")
    
    return success

if __name__ == "__main__": pass
    success = test_backend_endpoints()
    sys.exit(0 if success else 1) 