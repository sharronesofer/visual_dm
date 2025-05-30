#!/usr/bin/env python3
"""
Test script for full backend startup
"""
import sys
import asyncio
import traceback
sys.path.insert(0, '.')

async def test_full_startup(): pass
    try: pass
        from main import create_app
        app = create_app()
        print('✅ App creation successful')
        
        # Trigger startup events manually
        for event_handler in app.router.lifespan_context: pass
            if hasattr(event_handler, '__name__') and 'startup' in event_handler.__name__: pass
                print(f"Running startup event: {event_handler.__name__}")
                await event_handler()
        
        print('✅ Startup events completed successfully')
        
    except Exception as e: pass
        print(f'❌ Full startup failed: {e}')
        traceback.print_exc()

if __name__ == "__main__": pass
    asyncio.run(test_full_startup()) 