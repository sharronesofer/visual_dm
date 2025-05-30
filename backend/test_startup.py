#!/usr/bin/env python3
"""
Simple script to test backend startup
"""
import subprocess
import time
import sys
import signal
import os

def test_backend():
    """Test if backend starts and responds correctly."""
    print("🚀 Starting backend for testing...")
    
    # Start the backend process
    proc = subprocess.Popen([sys.executable, 'main.py'], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           preexec_fn=os.setsid)
    
    # Wait for startup
    time.sleep(8)
    
    try:
        # Test with curl
        result = subprocess.run(['curl', '-s', 'http://localhost:8000'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout:
            print("✅ Backend is responding!")
            print(f"Response: {result.stdout}")
            success = True
        else:
            print("❌ Backend not responding")
            success = False
            
    except subprocess.TimeoutExpired:
        print("❌ Backend test timed out")
        success = False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        success = False
    
    # Clean up
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except: pass
        proc.terminate()
    
    proc.wait()
    return success

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1) 