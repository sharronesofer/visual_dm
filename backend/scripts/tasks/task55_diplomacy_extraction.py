#!/usr/bin/env python3
"""
Task 55: Diplomacy System Modular Extraction

This script extracts the monolithic diplomacy/services.py (2,225 lines) into 
focused, single-responsibility domain modules following the Development Bible.

Phase 2: Diplomacy System Refactoring
"""

import os
import ast
import shutil
from pathlib import Path
from typing import Dict, List, Any, Set

class DiplomacyExtractor:
    """Extract diplomacy system into domain-specific modules."""
    
    def __init__(self, backend_path: str = None):
        if backend_path:
            self.backend_path = Path(backend_path)
        else:
            self.backend_path = Path.cwd()
        self.diplomacy_path = self.backend_path / "systems" / "diplomacy"
        
        print(f"Backend path: {self.backend_path}")
        print(f"Diplomacy path: {self.diplomacy_path}")
        
    def extract_diplomacy_system(self):
        """Extract diplomacy/services.py into modular structure."""
        print("🔨 Phase 2: Extracting Diplomacy System")
        
        if not self.diplomacy_path.exists():
            print(f"❌ Diplomacy directory not found: {self.diplomacy_path}")
            return
            
        # Read the monolithic services.py file
        services_file = self.diplomacy_path / "services.py"
        if not services_file.exists():
            print(f"❌ Services file not found: {services_file}")
            return
            
        with open(services_file, 'r') as f:
            content = f.read()
            
        # Create backup
        backup_file = services_file.with_suffix('.py.backup')
        if not backup_file.exists():
            backup_file.write_text(content)
            print(f"📁 Created backup: {backup_file}")
        
        # Extract different service classes
        self._extract_tension_service(content)
        self._extract_treaty_service(content)
        self._extract_negotiation_service(content)
        self._extract_incident_service(content)
        self._extract_ultimatum_service(content)
        self._extract_sanction_service(content)
        
        print("✅ Diplomacy system extraction complete")
        
    def _extract_tension_service(self, content: str):
        """Extract TensionService class to services/tension_service.py."""
        print("  📊 Extracting TensionService...")
        
        # Find the TensionService class
        lines = content.split('\n')
        tension_class_start = None
        tension_class_end = None
        
        for i, line in enumerate(lines):
            if 'class TensionService:' in line:
                tension_class_start = i
            elif tension_class_start and line.startswith('class ') and 'TensionService' not in line:
                tension_class_end = i
                break
                
        if tension_class_start is None:
            print("    ❌ TensionService class not found")
            return
            
        if tension_class_end is None:
            tension_class_end = len(lines)
            
        # Extract the class
        class_lines = lines[tension_class_start:tension_class_end]
        
        # Create the new tension service file
        tension_service_content = f'''"""
Tension Service - Diplomacy System Module

Part of the refactored diplomacy system architecture following Development Bible standards.
Extracted from monolithic services.py for improved maintainability.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, UUID
import logging

from backend.systems.diplomacy.models import DiplomaticStatus
from backend.systems.diplomacy.repository import DiplomacyRepository
from backend.infrastructure.events.event_dispatcher import EventDispatcher

logger = logging.getLogger(__name__)

{chr(10).join(class_lines)}
'''
        
        # Write to the modular file
        tension_file = self.diplomacy_path / "services" / "tension_service.py"
        tension_file.write_text(tension_service_content)
        print(f"    ✅ Extracted TensionService to {tension_file.relative_to(self.backend_path)}")
        
    def _extract_treaty_service(self, content: str):
        """Extract treaty-related methods to services/treaty_service.py."""
        print("  📜 Extracting TreatyService...")
        
        # Extract treaty-related methods from DiplomacyService
        treaty_methods = [
            'create_treaty',
            '_update_faction_relationships_for_treaty',
            '_create_treaty_event',
            'get_treaty',
            'expire_treaty',
            '_update_relationships_for_expired_treaty',
            'list_treaties',
            'has_treaty_of_type',
            'report_treaty_violation',
            'acknowledge_violation',
            'resolve_violation',
            'get_treaty_violations',
            'check_treaty_compliance',
            'enforce_treaties_automatically',
            'notify_treaty_breach'
        ]
        
        extracted_methods = self._extract_methods_from_diplomacy_service(content, treaty_methods)
        
        treaty_service_content = f'''"""
Treaty Service - Diplomacy System Module

Part of the refactored diplomacy system architecture following Development Bible standards.
Extracted from monolithic services.py for improved maintainability.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4
import logging

from backend.systems.diplomacy.models import (
    DiplomaticEvent, 
    DiplomaticEventType, 
    Treaty, 
    TreatyType,
    TreatyViolation,
    TreatyViolationType
)
from backend.systems.diplomacy.repository import DiplomacyRepository
from backend.infrastructure.events.event_dispatcher import EventDispatcher

logger = logging.getLogger(__name__)

class TreatyService:
    """Service for managing treaties and treaty violations."""
    
    def __init__(self, repository: Optional[DiplomacyRepository] = None):
        """Initialize the treaty service."""
        self.repository = repository or DiplomacyRepository()
        self._event_dispatcher = EventDispatcher.get_instance()

{extracted_methods}
'''
        
        # Write to the modular file
        treaty_file = self.diplomacy_path / "services" / "treaty_service.py"
        treaty_file.write_text(treaty_service_content)
        print(f"    ✅ Extracted TreatyService to {treaty_file.relative_to(self.backend_path)}")
        
    def _extract_negotiation_service(self, content: str):
        """Extract negotiation-related methods to services/negotiation_service.py."""
        print("  🤝 Extracting NegotiationService...")
        
        negotiation_methods = [
            'start_negotiation',
            '_create_negotiation_event',
            '_update_relationships_for_negotiation',
            'get_negotiation',
            'make_offer',
            'accept_offer',
            'reject_offer',
            '_update_relationships_for_completed_negotiation',
            'add_negotiation_offer'
        ]
        
        extracted_methods = self._extract_methods_from_diplomacy_service(content, negotiation_methods)
        
        negotiation_service_content = f'''"""
Negotiation Service - Diplomacy System Module

Part of the refactored diplomacy system architecture following Development Bible standards.
Extracted from monolithic services.py for improved maintainability.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4
import logging

from backend.systems.diplomacy.models import (
    DiplomaticEvent, 
    DiplomaticEventType, 
    DiplomaticStatus,
    Negotiation, 
    NegotiationOffer,
    NegotiationStatus, 
    Treaty, 
    TreatyType
)
from backend.systems.diplomacy.repository import DiplomacyRepository
from backend.infrastructure.events.event_dispatcher import EventDispatcher

logger = logging.getLogger(__name__)

class NegotiationService:
    """Service for managing diplomatic negotiations."""
    
    def __init__(self, repository: Optional[DiplomacyRepository] = None):
        """Initialize the negotiation service."""
        self.repository = repository or DiplomacyRepository()
        self._event_dispatcher = EventDispatcher.get_instance()

{extracted_methods}
'''
        
        # Write to the modular file
        negotiation_file = self.diplomacy_path / "services" / "negotiation_service.py"
        negotiation_file.write_text(negotiation_service_content)
        print(f"    ✅ Extracted NegotiationService to {negotiation_file.relative_to(self.backend_path)}")
        
    def _extract_incident_service(self, content: str):
        """Extract incident-related methods to services/incident_service.py."""
        print("  ⚠️ Extracting IncidentService...")
        
        incident_methods = [
            'create_diplomatic_incident',
            'get_diplomatic_incident',
            'update_diplomatic_incident',
            'list_diplomatic_incidents',
            'resolve_diplomatic_incident'
        ]
        
        extracted_methods = self._extract_methods_from_diplomacy_service(content, incident_methods)
        
        incident_service_content = f'''"""
Incident Service - Diplomacy System Module

Part of the refactored diplomacy system architecture following Development Bible standards.
Extracted from monolithic services.py for improved maintainability.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4
import logging

from backend.systems.diplomacy.models import (
    DiplomaticEvent, 
    DiplomaticEventType,
    DiplomaticIncident,
    DiplomaticIncidentType,
    DiplomaticIncidentSeverity
)
from backend.systems.diplomacy.repository import DiplomacyRepository
from backend.infrastructure.events.event_dispatcher import EventDispatcher

logger = logging.getLogger(__name__)

class IncidentService:
    """Service for managing diplomatic incidents."""
    
    def __init__(self, repository: Optional[DiplomacyRepository] = None):
        """Initialize the incident service."""
        self.repository = repository or DiplomacyRepository()
        self._event_dispatcher = EventDispatcher.get_instance()

{extracted_methods}
'''
        
        # Write to the modular file
        incident_file = self.diplomacy_path / "services" / "incident_service.py"
        incident_file.write_text(incident_service_content)
        print(f"    ✅ Extracted IncidentService to {incident_file.relative_to(self.backend_path)}")
        
    def _extract_ultimatum_service(self, content: str):
        """Extract ultimatum-related methods to services/ultimatum_service.py."""
        print("  ⏰ Extracting UltimatumService...")
        
        ultimatum_methods = [
            'create_ultimatum',
            'get_ultimatum',
            'update_ultimatum',
            'list_ultimatums',
            'respond_to_ultimatum',
            'check_expired_ultimatums',
            '_handle_accepted_ultimatum',
            '_handle_rejected_ultimatum'
        ]
        
        extracted_methods = self._extract_methods_from_diplomacy_service(content, ultimatum_methods)
        
        ultimatum_service_content = f'''"""
Ultimatum Service - Diplomacy System Module

Part of the refactored diplomacy system architecture following Development Bible standards.
Extracted from monolithic services.py for improved maintainability.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4
import logging

from backend.systems.diplomacy.models import (
    DiplomaticEvent, 
    DiplomaticEventType,
    Ultimatum,
    UltimatumStatus
)
from backend.systems.diplomacy.repository import DiplomacyRepository
from backend.infrastructure.events.event_dispatcher import EventDispatcher

logger = logging.getLogger(__name__)

class UltimatumService:
    """Service for managing diplomatic ultimatums."""
    
    def __init__(self, repository: Optional[DiplomacyRepository] = None):
        """Initialize the ultimatum service."""
        self.repository = repository or DiplomacyRepository()
        self._event_dispatcher = EventDispatcher.get_instance()

{extracted_methods}
'''
        
        # Write to the modular file
        ultimatum_file = self.diplomacy_path / "services" / "ultimatum_service.py"
        ultimatum_file.write_text(ultimatum_service_content)
        print(f"    ✅ Extracted UltimatumService to {ultimatum_file.relative_to(self.backend_path)}")
        
    def _extract_sanction_service(self, content: str):
        """Extract sanction-related methods to services/sanction_service.py."""
        print("  🚫 Extracting SanctionService...")
        
        sanction_methods = [
            'create_sanction',
            'get_sanction',
            'update_sanction',
            'lift_sanction',
            'list_sanctions',
            'record_sanction_violation',
            'check_expired_sanctions'
        ]
        
        extracted_methods = self._extract_methods_from_diplomacy_service(content, sanction_methods)
        
        sanction_service_content = f'''"""
Sanction Service - Diplomacy System Module

Part of the refactored diplomacy system architecture following Development Bible standards.
Extracted from monolithic services.py for improved maintainability.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4
import logging

from backend.systems.diplomacy.models import (
    DiplomaticEvent, 
    DiplomaticEventType,
    Sanction,
    SanctionType,
    SanctionStatus
)
from backend.systems.diplomacy.repository import DiplomacyRepository
from backend.infrastructure.events.event_dispatcher import EventDispatcher

logger = logging.getLogger(__name__)

class SanctionService:
    """Service for managing diplomatic sanctions."""
    
    def __init__(self, repository: Optional[DiplomacyRepository] = None):
        """Initialize the sanction service."""
        self.repository = repository or DiplomacyRepository()
        self._event_dispatcher = EventDispatcher.get_instance()

{extracted_methods}
'''
        
        # Write to the modular file
        sanction_file = self.diplomacy_path / "services" / "sanction_service.py"
        sanction_file.write_text(sanction_service_content)
        print(f"    ✅ Extracted SanctionService to {sanction_file.relative_to(self.backend_path)}")
        
    def _extract_methods_from_diplomacy_service(self, content: str, method_names: List[str]) -> str:
        """Extract specific methods from the DiplomacyService class."""
        lines = content.split('\n')
        extracted_lines = []
        
        for method_name in method_names:
            method_start = None
            method_end = None
            indentation_level = None
            
            # Find method start
            for i, line in enumerate(lines):
                if f'def {method_name}(' in line and ('self,' in line or 'self)' in line):
                    method_start = i
                    indentation_level = len(line) - len(line.lstrip())
                    break
                    
            if method_start is None:
                print(f"    ⚠️  Method {method_name} not found")
                continue
                
            # Find method end
            for i in range(method_start + 1, len(lines)):
                line = lines[i]
                if line.strip() == '':
                    continue
                current_indentation = len(line) - len(line.lstrip())
                if current_indentation <= indentation_level and (line.strip().startswith('def ') or line.strip().startswith('class ')):
                    method_end = i
                    break
                    
            if method_end is None:
                method_end = len(lines)
                
            # Extract method lines
            method_lines = lines[method_start:method_end]
            extracted_lines.extend(method_lines)
            extracted_lines.append('')  # Add blank line between methods
            
        return '\n'.join(extracted_lines)
        
    def run_phase_2(self):
        """Execute Phase 2 of the modular extraction."""
        print("🚀 Starting Task 55: Modular Extraction - Phase 2")
        print("=" * 60)
        
        self.extract_diplomacy_system()
        
        print("✅ Phase 2 extraction successful")
        return True

def main():
    """Main execution function."""
    extractor = DiplomacyExtractor()
    
    if extractor.run_phase_2():
        print("\n🎉 Task 55 Phase 2 Complete!")
        print("Next steps:")
        print("1. Update diplomacy imports")
        print("2. Create integration layer") 
        print("3. Run comprehensive testing")
        print("4. Proceed to Phase 3 (motif system)")
    else:
        print("\n❌ Task 55 Phase 2 Failed")

if __name__ == "__main__":
    main() 