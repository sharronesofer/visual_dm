#!/usr/bin/env python3
"""
Debug script to test app creation
"""
import sys
import traceback
sys.path.insert(0, '.')

try:
    from main import create_app
    app = create_app()
    print('✅ App creation successful')
except Exception as e:
    print(f'❌ App creation failed: {e}')
    traceback.print_exc() 