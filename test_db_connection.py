#!/usr/bin/env python3
import sys
sys.path.append('/Users/Sharrone/Dreamforge')

from backend.infrastructure.persistence.equipment.equipment_dependencies import (
    get_equipment_database, 
    get_equipment_business_logic_service
)

print('Testing equipment database connection...')
try:
    # Test database connection
    session_gen = get_equipment_database()
    session = next(session_gen)
    print('✅ Database connection successful!')
    
    # Test business logic service
    service = get_equipment_business_logic_service()
    print('✅ Business logic service created successfully!')
    
    print('🎉 Equipment database layer is working!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc() 