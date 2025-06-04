# Motif System Cleanup Plan

## Executive Summary

This plan addresses the identified maintenance concerns and implements the recommended modular cleanup opportunities for the Motif System. The cleanup will eliminate duplicate code, complete the ongoing refactoring, extract hardcoded configuration to JSON, and establish clear architectural boundaries.

---

## 1. Immediate Maintenance Actions

### 1.1 Remove Duplicate Functions

**Problem:** Multiple implementations of the same functions across different files.

**Actions:**

1. **Consolidate `roll_chaos_event()`**:
   - ✅ **Keep**: `business_utils.py:39` (current implementation)
   - ❌ **Remove**: `chaos_utils.py:33` (legacy)
   - ❌ **Remove**: `manager_core.py:119` (mock fallback)

2. **Consolidate `NARRATIVE_CHAOS_TABLE`**:
   - ✅ **Keep**: `business_utils.py:16` (current implementation)
   - ❌ **Remove**: `chaos_utils.py:10` (legacy duplicate)
   - ❌ **Remove**: `manager_core.py:122` (mock fallback)

3. **Consolidate Motif CRUD Operations**:
   - ✅ **Keep**: `service.py` (main business logic)
   - ✅ **Keep**: `manager_core.py` (high-level interface)
   - ❌ **Remove**: `services.py` (legacy/mock implementations)

### 1.2 Complete Legacy File Deprecation

**Problem:** MIGRATION_PLAN.md indicates files marked for removal but still containing functionality.

**Actions:**

1. **Remove Legacy Files** (per migration plan):
   ```
   ❌ backend/systems/motif/utils/chaos_utils.py
   ❌ backend/systems/motif/services/motif_engine_class.py
   ❌ backend/systems/motif/services/services.py
   ```

2. **Update Import References**:
   - Search codebase for imports from removed files
   - Redirect to new implementations
   - Update `__init__.py` files to remove deprecated exports

### 1.3 Address TODO Comments

**Problem:** Database integration issues blocking system functionality.

**Actions:**

1. **Fix Database Integration** (`motif_engine_class.py:4`, `chaos_utils.py:4`):
   - Since these files are being removed, this resolves automatically
   - Ensure `manager_core.py` repository pattern handles persistence correctly

2. **Verify Repository Pattern**:
   - Confirm `MotifRepository` handles all persistence needs
   - Test motif creation, retrieval, and chaos event logging

---

## 2. Chaos System Integration Resolution

### 2.1 Current Chaos Architecture Analysis

**Three-Layer Chaos System** (Post-cleanup):

1. **Data Layer** (`business_utils.py`):
   - `NARRATIVE_CHAOS_TABLE`: Event definitions
   - `roll_chaos_event()`: Random selection logic

2. **Service Layer** (`manager_core.py`):
   - `inject_chaos_event()`: Event creation and persistence
   - Integration with repository and event system

3. **Domain Layer** (Motif categories):
   - `MotifCategory.CHAOS`: Thematic chaos motifs
   - Chaos-influenced motif generation

### 2.2 Recommended Integration Pattern

**Clear Separation of Concerns:**

```python
# business_utils.py - Pure utility functions
def roll_chaos_event() -> str
NARRATIVE_CHAOS_TABLE: List[str]

# manager_core.py - Business logic integration  
async def inject_chaos_event(event_type, region=None, context=None)
async def trigger_chaos_motif(intensity: float, scope: MotifScope)

# Motif effects system - Domain impact
async def apply_chaos_motif_effects(motif: Motif, target_systems: List[str])
```

**Integration Points:**
- **NPC System**: NPCs query chaos events from world log for reaction logic
- **Event System**: Uses chaos table for random narrative disruptions
- **Motif System**: Chaos events can create/strengthen chaos-category motifs

---

## 3. JSON Configuration Extraction

### 3.1 Create Configuration Structure

**New File**: `backend/systems/motif/config/motif_config.json`

```json
{
  "chaos_events": {
    "political": [
      "NPC betrays a faction or personal goal",
      "Town leader is assassinated",
      "Enemy faction completes objective offscreen",
      "False flag sent from another region"
    ],
    "supernatural": [
      "Player receives a divine omen", 
      "Corrupted prophecy appears in a temple or vision",
      "Magical item begins to misbehave",
      "PC has a surreal dream altering perception"
    ],
    "social": [
      "NPC vanishes mysteriously",
      "NPC's child arrives with a claim",
      "NPC becomes hostile based on misinformation",
      "Rumor spreads about a player betrayal",
      "Secret faction is revealed through slip-up",
      "NPC becomes obsessed with the PC"
    ],
    "criminal": [
      "PC is blamed for a crime in a new city",
      "Artifact or item changes hands unexpectedly"
    ],
    "temporal": [
      "Villain resurfaces (real or false)",
      "Time skip or memory blackout (~5 minutes)",
      "Prophecy misidentifies the chosen one"
    ],
    "relational": [
      "Ally requests an impossible favor"
    ]
  },
  "action_to_motif_mapping": {
    "heroic_deed": "HOPE",
    "betrayal": "BETRAYAL",
    "sacrifice": "SACRIFICE", 
    "revenge": "VENGEANCE",
    "discovery": "REVELATION",
    "destruction": "RUIN",
    "protection": "PROTECTION",
    "leadership": "ASCENSION",
    "deception": "DECEPTION",
    "redemption": "REDEMPTION"
  },
  "theme_relationships": {
    "opposing_pairs": [
      ["hope", "despair"],
      ["order", "chaos"],
      ["peace", "conflict"],
      ["unity", "division"],
      ["creation", "destruction"],
      ["ascension", "collapse"],
      ["loyalty", "betrayal"],
      ["truth", "deception"],
      ["justice", "corruption"],
      ["courage", "fear"],
      ["wisdom", "ignorance"],
      ["humility", "pride"],
      ["redemption", "vengeance"],
      ["innocence", "guilt"],
      ["freedom", "control"],
      ["faith", "doubt"],
      ["light", "shadow"],
      ["growth", "stagnation"],
      ["healing", "harm"]
    ],
    "complementary_pairs": [
      ["power", "responsibility"],
      ["sacrifice", "redemption"],
      ["struggle", "growth"],
      ["loss", "wisdom"],
      ["challenge", "strength"],
      ["mystery", "discovery"],
      ["conflict", "resolution"],
      ["darkness", "hope"],
      ["tradition", "innovation"],
      ["solitude", "reflection"]
    ]
  },
  "name_generation": {
    "ASCENSION": {
      "base_names": ["Rising", "Elevation", "Ascent", "Climb", "Uplift"],
      "modifiers": ["of the World", "Universal", "Cosmic", "Eternal", "Infinite"]
    },
    "BETRAYAL": {
      "base_names": ["Broken Trust", "Treachery", "Deception", "False Promise", "Backstab"],
      "modifiers": ["of the Land", "Regional", "Territorial", "Local", "Provincial"]
    },
    "CHAOS": {
      "base_names": ["Disorder", "Turmoil", "Mayhem", "Upheaval", "Anarchy"],
      "modifiers": ["of the Place", "Intimate", "Personal", "Immediate", "Close"]
    },
    "COLLAPSE": {
      "base_names": ["Downfall", "Ruin", "Decay", "Crumble", "Fall"],
      "modifiers": ["of the Hero", "Personal", "Individual", "Chosen", "Destined"]
    },
    "DEATH": {
      "base_names": ["Mortality", "End", "Passing", "Finality", "Demise"],
      "modifiers": ["of the World", "Universal", "Cosmic", "Eternal", "Infinite"]
    },
    "HOPE": {
      "base_names": ["Light", "Promise", "Dawn", "Renewal", "Faith"],
      "modifiers": ["of the Land", "Regional", "Territorial", "Local", "Provincial"]
    },
    "POWER": {
      "base_names": ["Dominion", "Authority", "Control", "Might", "Supremacy"],
      "modifiers": ["of the Place", "Intimate", "Personal", "Immediate", "Close"]
    },
    "REDEMPTION": {
      "base_names": ["Salvation", "Atonement", "Renewal", "Forgiveness", "Recovery"],
      "modifiers": ["of the Hero", "Personal", "Individual", "Chosen", "Destined"]
    },
    "VENGEANCE": {
      "base_names": ["Retribution", "Justice", "Payback", "Reckoning", "Revenge"],
      "modifiers": ["of the World", "Universal", "Cosmic", "Eternal", "Infinite"]
    }
  },
  "settings": {
    "default_chaos_weight": 0.1,
    "max_concurrent_motifs_per_region": 5,
    "motif_decay_rate_days": 0.1,
    "chaos_trigger_threshold": 7.5,
    "motif_interaction_radius": 50.0
  }
}
```

### 3.2 Create Configuration Loader

**New File**: `backend/systems/motif/config/config_loader.py`

```python
"""
Configuration loader for Motif System
Handles loading and caching of JSON configuration data
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class MotifConfig:
    """Singleton configuration loader for Motif System."""
    
    _instance = None
    _config_data = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config_data is None:
            self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file."""
        config_path = Path(__file__).parent / "motif_config.json"
        
        try:
            with open(config_path, 'r') as f:
                self._config_data = json.load(f)
        except FileNotFoundError:
            # Fallback to embedded defaults if file missing
            self._config_data = self._get_default_config()
    
    def get_chaos_events(self, category: Optional[str] = None) -> List[str]:
        """Get chaos events, optionally filtered by category."""
        chaos_events = self._config_data.get("chaos_events", {})
        
        if category:
            return chaos_events.get(category, [])
        
        # Return all events if no category specified
        all_events = []
        for events in chaos_events.values():
            all_events.extend(events)
        return all_events
    
    def get_action_motif_mapping(self) -> Dict[str, str]:
        """Get mapping from player actions to motif categories."""
        return self._config_data.get("action_to_motif_mapping", {})
    
    def get_opposing_themes(self) -> List[List[str]]:
        """Get list of opposing theme pairs."""
        return self._config_data.get("theme_relationships", {}).get("opposing_pairs", [])
    
    def get_complementary_themes(self) -> List[List[str]]:
        """Get list of complementary theme pairs."""
        return self._config_data.get("theme_relationships", {}).get("complementary_pairs", [])
    
    def get_name_components(self, category: str) -> Dict[str, List[str]]:
        """Get name generation components for a motif category."""
        return self._config_data.get("name_generation", {}).get(category, {
            "base_names": ["Unknown"],
            "modifiers": [""]
        })
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting value."""
        return self._config_data.get("settings", {}).get(key, default)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Embedded fallback configuration."""
        return {
            "chaos_events": {
                "general": [
                    "NPC betrays a faction or personal goal",
                    "Player receives a divine omen",
                    "NPC vanishes mysteriously"
                ]
            },
            "action_to_motif_mapping": {
                "heroic_deed": "HOPE",
                "betrayal": "BETRAYAL"
            },
            "theme_relationships": {
                "opposing_pairs": [["hope", "despair"], ["order", "chaos"]],
                "complementary_pairs": [["power", "responsibility"]]
            },
            "name_generation": {
                "DEFAULT": {
                    "base_names": ["Unknown"],
                    "modifiers": [""]
                }
            },
            "settings": {
                "default_chaos_weight": 0.1,
                "max_concurrent_motifs_per_region": 5
            }
        }

# Global instance
config = MotifConfig()
```

### 3.3 Update Code to Use Configuration

**Modify `business_utils.py`**:

```python
# Replace hardcoded table with config loader
from backend.systems.motif.config.config_loader import config

def roll_chaos_event(category: Optional[str] = None):
    """Roll a random chaos event from the narrative chaos table."""
    return random.choice(config.get_chaos_events(category))

def generate_motif_name(category: MotifCategory, scope: MotifScope) -> str:
    """Generate a thematic name for a motif based on its category and scope."""
    name_data = config.get_name_components(category.value)
    base = random.choice(name_data["base_names"])
    modifier = random.choice(name_data["modifiers"])
    # ... rest of logic
```

**Modify `pc_motif_service.py`**:

```python
# Replace hardcoded mapping with config
from backend.systems.motif.config.config_loader import config

async def trigger_pc_motif_from_action(self, player_id: str, action_type: str, ...):
    """Create or modify PC motifs based on player actions."""
    category_mapping = config.get_action_motif_mapping()
    category = category_mapping.get(action_type, MotifCategory.ECHO)
    # ... rest of logic
```

---

## 4. Implementation Timeline

### Phase 1: Cleanup (Week 1)
- [ ] Remove duplicate functions
- [ ] Delete deprecated legacy files
- [ ] Update import references
- [ ] Fix remaining mock implementations

### Phase 2: Configuration Extraction (Week 2)  
- [ ] Create JSON configuration file
- [ ] Implement configuration loader
- [ ] Update business logic to use config
- [ ] Add configuration validation

### Phase 3: Testing & Documentation (Week 3)
- [ ] Unit tests for config loader
- [ ] Integration tests for chaos system
- [ ] Update README with configuration docs
- [ ] Performance testing

### Phase 4: Deployment & Monitoring (Week 4)
- [ ] Deploy configuration system
- [ ] Monitor for integration issues
- [ ] Gather feedback from narrative designers
- [ ] Iterate on configuration structure

---

## 5. Benefits Post-Cleanup

### For Developers:
- **Reduced Complexity**: Single source of truth for each function
- **Clearer Architecture**: Well-defined layer boundaries
- **Easier Testing**: Isolated, configurable components
- **Better Maintainability**: Less duplicate code to update

### For Designers:
- **Content Control**: Direct editing of narrative elements via JSON
- **Rapid Iteration**: No code deployment needed for content changes
- **Easy Expansion**: Add new chaos events, motif relationships, naming components
- **Localization Ready**: JSON structure supports multiple languages

### For Players:
- **Richer Narratives**: More diverse, well-integrated thematic experiences
- **Consistent World**: Better narrative continuity across systems
- **Dynamic Stories**: Configurable chaos and motif systems create emergent narratives

---

## 6. Risk Mitigation

### Configuration Corruption:
- **Validation Schema**: JSON schema validation on load
- **Fallback System**: Embedded defaults if file missing/corrupt
- **Version Control**: Track configuration changes in git

### Performance Impact:
- **Caching**: Configuration loaded once and cached
- **Lazy Loading**: Only load needed configuration sections
- **Monitoring**: Track configuration load times

### Integration Breakage:
- **Gradual Migration**: Phase rollout with feature flags  
- **Comprehensive Testing**: Unit and integration test coverage
- **Rollback Plan**: Ability to revert to hardcoded values if needed

This cleanup plan transforms the Motif System from a development bottleneck into a designer-friendly, maintainable narrative toolkit while eliminating the identified technical debt. 