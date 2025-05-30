#!/usr/bin/env python3
"""
Get final collection statistics with timeout
"""

import subprocess
import sys
import signal
import time

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError('Collection timeout')

def get_collection_stats():
    print("🔍 Getting final collection statistics...")
    
    # Set up timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)  # 60 second timeout
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', '--collect-only', '-q'
        ], capture_output=True, text=True)
        
        output = result.stdout + result.stderr
        print(f"Exit code: {result.returncode}")
        
        # Extract collection summary
        lines = output.strip().split('\n')
        for line in lines[-15:]:
            if any(keyword in line.lower() for keyword in ['collected', 'errors', 'items', 'skipped', 'warnings']):
                print(f"📊 {line}")
        
        # Count test functions directly from output
        test_lines = [line for line in lines if '::test_' in line or '::Test' in line]
        print(f"📈 Raw test discovery count: {len(test_lines)}")
        
        return len(test_lines)
        
    except TimeoutError:
        print("⏱️  Collection timed out after 60 seconds")
        return -1
    except Exception as e:
        print(f"❌ Error during collection: {e}")
        return -1
    finally:
        signal.alarm(0)

def main():
    print("🎯 FINAL BACKEND TEST COLLECTION ANALYSIS")
    print("=" * 50)
    
    discovered_count = get_collection_stats()
    
    print("\n" + "=" * 50)
    print("📊 COLLECTION PROGRESS SUMMARY:")
    print(f"   Expected total test functions: 15,275")
    
    if discovered_count > 0:
        percentage = (discovered_count / 15275) * 100
        print(f"   Tests currently discovered: {discovered_count:,}")
        print(f"   Discovery percentage: {percentage:.1f}%")
        
        if percentage > 90:
            print("🎉 EXCELLENT! Nearly full test discovery achieved!")
        elif percentage > 70:
            print("🎯 GREAT PROGRESS! Most tests are being discovered.")
        elif percentage > 50:
            print("📈 GOOD PROGRESS! Majority of tests discovered.")
        elif percentage > 30:
            print("📊 SOME PROGRESS! Significant improvement made.")
        else:
            print("🔧 MORE WORK NEEDED! Still many collection issues.")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 