#!/usr/bin/env python3
import os
import subprocess
import sys
import time

# Order of operations
# 1. utils (least critical)
# 2. services
# 3. api
# 4. core (most critical)

SCRIPTS = [
    "consolidate_utils.py",
    "consolidate_services.py",
    "consolidate_api.py",
    "consolidate_core.py"
]

def main():
    """Run all consolidation scripts in order."""
    # Make sure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("Starting consolidation process...")
    
    for script in SCRIPTS:
        if not os.path.exists(script):
            print(f"Error: {script} not found.")
            continue
        
        print(f"\n{'=' * 50}")
        print(f"Running {script}...")
        print(f"{'=' * 50}\n")
        
        # Run the script
        try:
            subprocess.run([sys.executable, script], check=True)
            print(f"\n{script} completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"\nError running {script}: {e}")
            response = input("Continue with next script? (y/n): ")
            if response.lower() != 'y':
                print("Aborting consolidation process.")
                return
        
        # Pause between scripts to allow reviewing output
        print("\nWaiting 5 seconds before moving to the next script...")
        time.sleep(5)
    
    print("\nAll consolidation scripts have been executed.")
    print("Please test the application to ensure everything is working correctly.")

if __name__ == "__main__":
    main() 