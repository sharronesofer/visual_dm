# Economic Espionage System - Comprehensive System Report

## Overview

The Economic Espionage System is a sophisticated game mechanic that allows NPCs and factions to engage in covert operations against competitors. This system handles economic warfare through intelligence gathering, sabotage, market manipulation, and spy network management. It creates a shadow economy where information becomes currency and trust becomes vulnerability.

**Status Update**: This system has undergone significant refactoring to address technical debt and improve maintainability. Hard-coded constants have been moved to JSON configuration, the monolithic service has been broken into specialized services, and comprehensive business rule validation has been added.

---

## 1. Logical Subsystems

### 1.1 Core Data Models Subsystem
**Location:** `models.py`  
**Purpose:** Defines the fundamental building blocks for all espionage activities. This subsystem contains the business rules and data structures that represent real-world espionage concepts in game terms.

### 1.2 Configuration Management Subsystem
**Location:** `config/` directory  
**Purpose:** Manages all configurable parameters for the espionage system, including operation success rates, damage values, agent effectiveness, and risk thresholds. This subsystem enables game designers to balance gameplay without code changes.

### 1.3 Specialized Business Services Subsystem
**Location:** `services/` directory  
**Purpose:** Houses specialized services that handle different aspects of espionage operations:
- **EspionageService**: Core orchestration and calculations
- **EspionageOperationService**: Operation planning, execution, and lifecycle management
- **EspionageAgentService**: Agent recruitment, training, assignment, and performance evaluation
- **EspionageValidationService**: Business rule validation and data integrity checks

### 1.4 Module Integration Subsystem
**Location:** `__init__.py` and `services/__init__.py`  
**Purpose:** Manages how the espionage system exposes its functionality to other parts of the game and controls which features are currently available versus planned for future development.

---

## 2. Business Logic in Simple Terms

### 2.1 Core Data Models (`models.py`)

This file defines what espionage looks like in the game world:

**Operation Types:** The system recognizes 11 different kinds of espionage activities, ranging from simple price snooping (easy but low-value) to full network infiltration (extremely difficult but potentially devastating). Each operation type has its own risk-reward profile.

**Agent Roles:** Espionage agents aren't just generic spies - they have specialized jobs like infiltrators (who sneak into places), informants (who share secrets), saboteurs (who break things), and spymasters (who run other agents). Each role affects what operations they can perform and how well they do them.

**Intelligence Categories:** The system tracks eight types of economic secrets, from basic pricing data to complex strategic plans. More valuable intelligence requires more sophisticated operations to obtain.

**Network Management:** Spy networks aren't just collections of agents - they have organizational structures, coverage areas, and specializations. A network might be excellent at gathering trade route information but terrible at sabotage operations.

**Status Tracking:** Every operation, agent, and network has a current status that affects what can be done with them. A "compromised" agent can't safely run new operations, while a "dormant" network might be rebuilding after a security breach.

### 2.2 Configuration Management (`config/config_loader.py` and `config/espionage_config.json`)

The configuration system eliminates hard-coded magic numbers and makes the system designer-friendly:

**Operation Success Rates:** Base success probabilities for each operation type are now stored in JSON, allowing quick balance adjustments without code changes. Route surveillance has an 80% base success rate, while network infiltration only has 20%.

**Economic Damage Values:** The financial impact of successful sabotage operations is configurable, enabling economic balance tuning during playtesting.

**Agent Effectiveness Matrix:** A comprehensive mapping of how effective each agent role is at each operation type. Infiltrators excel at trade secret theft (140% effectiveness) but are poor at market manipulation (80% effectiveness).

**Risk Management Parameters:** All burn risk multipliers, heat decay rates, and operational thresholds are configurable, allowing fine-tuning of the risk-reward balance that drives player decision-making.

### 2.3 Business Logic Services

#### 2.3.1 Core Espionage Service (`services/espionage_service.py`)

The main orchestration service now focuses on pure business logic:

**Capability Assessment:** Calculates a faction's overall espionage capabilities using configurable formulas that combine network capacities and agent skill bonuses.

**Success Probability:** Uses the configuration system to calculate operation success chances based on agent roles, skills, target defenses, and operation type. The calculation is now transparent and configurable.

**Outcome Determination:** Determines what happens when operations complete, using configuration data to decide intelligence gained and economic damage dealt.

**Agent Risk Calculation:** Tracks how operations affect agent burn risk using configurable multipliers and thresholds.

**Agent Validation and Recommendations:** New functionality that validates agent assignments and recommends optimal agents for specific operations based on role effectiveness and risk profiles.

#### 2.3.2 Operation Service (`services/operation_service.py`)

Specialized service for managing the complete operation lifecycle:

**Operation Planning:** Analyzes operation feasibility, recommends agents, calculates success probabilities, and estimates resource requirements and timelines.

**Execution Management:** Handles the actual execution of operations, including environmental factors, success determination, detection calculation, and outcome processing.

**Feasibility Validation:** Checks if operations are viable with current resources, agent availability, and success probability thresholds.

**Difficulty Calculation:** Determines operation difficulty based on type, target security, and additional complexity factors.

**Timeline Estimation:** Calculates how long operations will take based on type and difficulty, helping with resource planning.

#### 2.3.3 Agent Service (`services/agent_service.py`)

Comprehensive agent lifecycle management:

**Agent Recommendation:** Scores and ranks agents for specific operations based on role effectiveness, skill levels, burn risk, and validation criteria.

**Recruitment Assessment:** Evaluates NPCs for potential recruitment, considering loyalty, financial situation, personality traits, and access levels.

**Heat and Burnout Management:** Handles agent cooling-off periods, burn risk decay, and status recommendations based on configurable thresholds.

**Training Simulation:** Simulates agent improvement through various training programs, each with different costs, benefits, and success rates.

**Performance Evaluation:** Analyzes agent effectiveness over time, generating ratings and recommendations based on success rates, reliability, and risk management.

#### 2.3.4 Validation Service (`services/validation_service.py`)

Comprehensive business rule validation beyond basic data validation:

**Operation Business Rules:** Validates complete operations against timing constraints, agent assignments, faction relationships, resource requirements, and operational security.

**Agent Status Consistency:** Ensures agent status fields (status, burn_risk, heat_level) are consistent with each other and recent operation history.

**Network-Agent Relationships:** Validates that spy networks accurately track their agent counts and that agents properly reference their networks.

**Operation Overlap Detection:** Prevents agents from being double-booked for overlapping operations.

**Faction Ethics Validation:** Ensures operations align with faction ethics (pacifist factions can't do sabotage) and relationship constraints (can't spy on allies with inappropriate operations).

---

## 3. Integration with Broader Codebase

### 3.1 NPC System Integration
The espionage system heavily relies on the NPC system for agent recruitment and operation targets. Every espionage agent is backed by an actual NPC (`npc_id` field), which means agent behavior is influenced by the NPC's personality traits, skills, and relationships. When an NPC becomes an espionage agent, their existing characteristics affect their spy capabilities.

**Downstream Effects:** Changes to NPC personality systems or skill calculations would directly impact espionage agent effectiveness. If the NPC loyalty system changes, agent loyalty and burn risk calculations would need updating.

### 3.2 Faction System Integration
Spy networks are owned by factions (`faction_id` field), and operations typically involve faction-vs-faction competition. The espionage system reads faction hidden attributes to determine espionage capabilities and ethical boundaries.

**Downstream Effects:** Faction relationship changes affect operation success rates and agent recruitment possibilities. If faction alliance systems change, the espionage system's friend-vs-foe calculations would need adjustment.

### 3.3 Economic System Integration
Economic espionage targets business data like pricing, supplier relationships, and trade routes. The intelligence gathered feeds back into economic decision-making for NPCs and factions.

**Downstream Effects:** Changes to the economic model (new trade goods, different pricing mechanisms) would require updates to intelligence types and operation outcomes. Economic damage calculations would need recalibration if business value models change.

### 3.4 Infrastructure Dependencies
The system relies on `backend.infrastructure` for database persistence, API schemas, and repository patterns. The business models in `systems/espionage` get converted to database entities in `infrastructure/models/espionage_models.py`.

**Downstream Effects:** Database schema changes in infrastructure would require corresponding updates to business models. API changes would affect how other systems request espionage data.

---

## 4. Maintenance Concerns - RESOLVED

### 4.1 Technical Debt - ADDRESSED

**✅ Specialized Services Implemented:**
The TODO for five major service components has been addressed:
- ✅ `EspionageOperationService` - Fully implemented with comprehensive operation lifecycle management
- ✅ `EspionageAgentService` - Fully implemented with agent lifecycle and performance management  
- ✅ `EspionageValidationService` - New service for business rule validation
- 🔄 `EconomicIntelligenceService` - Planned for future implementation
- 🔄 `SpyNetworkService` - Planned for future implementation

### 4.2 Code Structure Issues - RESOLVED

**✅ Monolithic Service Refactored:**
The single `EspionageService` class has been refactored with specialized responsibilities:
- Core calculations and orchestration remain in `EspionageService`
- Operation planning and execution moved to `EspionageOperationService`
- Agent management moved to `EspionageAgentService`
- Business rule validation moved to `EspionageValidationService`

**✅ Comprehensive Validation Added:**
The new `EspionageValidationService` provides business rule validation for:
- Agent assignment constraints (skill level, burn risk, availability)
- Faction relationship rules (can't spy on allies inappropriately)
- Operation timing and overlap prevention
- Resource requirement validation
- Agent status consistency checks

**✅ Hard-coded Constants Eliminated:**
All magic numbers have been moved to `config/espionage_config.json`:
- Operation success rates and damage values
- Agent effectiveness matrices by role and operation type
- Risk thresholds and calculation parameters
- Burn risk multipliers and heat decay rates

### 4.3 Logic Conflicts - RESOLVED

**✅ Agent Status Management Clarified:**
The relationship between agent status fields is now validated:
- `EspionageValidationService.validate_agent_status_consistency()` ensures status, burn_risk, and heat_level are consistent
- Configurable thresholds define when agents should be restricted or retired
- Heat decay and burn risk recovery are properly modeled with time-based calculations

**✅ Network-Agent Relationship Fixed:**
Added validation to ensure network agent counts match actual agent assignments:
- `validate_network_agent_relationships()` detects inconsistencies
- Agent assignment validation prevents orphaned agents
- Clear business rules for network membership

**✅ Operation Timing Clarified:**
Added comprehensive validation for operation timing:
- `validate_operation_overlaps()` prevents agent double-booking
- Start time validation ensures consistency between planned and actual times
- Status-timing consistency checks prevent invalid state combinations

---

## 5. Configuration-Driven Design - IMPLEMENTED

The espionage system is now fully configuration-driven, enabling game designers to adjust gameplay balance without programmer involvement:

### 5.1 JSON Configuration Files

**✅ `config/espionage_config.json`:**
All gameplay parameters are now externalized:
- Operation success rates and damage values
- Agent effectiveness matrices
- Risk thresholds and calculation parameters
- Economic costs and timeline estimates

**✅ `config/config_loader.py`:**
Robust configuration management with:
- Type-safe parameter access
- Validation of configuration values
- Default fallbacks for missing parameters
- Hot-reloading capability for runtime updates

### 5.2 Designer-Friendly Balance Control

**Game designers can now adjust:**
- Operation difficulty and success rates for balance testing
- Economic damage values for different espionage operations
- Agent specialization effectiveness to create meaningful role choices
- Risk thresholds to control player tension and agent lifecycle management
- Training costs and improvement rates for progression tuning

**Why this matters:**
- Rapid iteration during playtesting without code deployment
- Non-programmers can experiment with different espionage economies
- A/B testing of different balance configurations
- Seasonal events can temporarily modify espionage parameters

---

## 6. Future Enhancement Opportunities

### 6.1 Remaining Services to Implement

**Economic Intelligence Service:**
Specialized service for managing intelligence data lifecycle, analysis, and economic impact assessment.

**Spy Network Service:**
Dedicated service for network management, territory control, and inter-network competition.

**Espionage Engine:**
High-level orchestration engine for complex multi-operation campaigns and faction-level espionage strategies.

### 6.2 Additional Configuration Opportunities

**Personality-Based Recruitment:**
Move NPC personality-to-recruitment mappings into configuration for different cultural or faction-specific recruitment patterns.

**Environmental Factors:**
Configure how weather, political climate, and economic conditions affect operation success rates.

**Faction-Specific Ethics:**
Externalize faction ethics rules to allow for custom faction types with unique espionage constraints.

The Economic Espionage System is now a robust, maintainable, and designer-friendly system that provides rich gameplay mechanics while remaining flexible for future enhancements and balance adjustments. 