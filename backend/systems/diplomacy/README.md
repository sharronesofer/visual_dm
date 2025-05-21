# Diplomacy System

## Overview

The diplomacy system manages diplomatic relations between factions, including:

- Treaty management (creation, negotiation, signing, expiration)
- Negotiation processes (offers, counter-offers, acceptance, rejection)
- Diplomatic events tracking
- Faction relationships and tension management
- War status determination and resolution
- Treaty violations and enforcement
- Diplomatic incidents and resolutions
- Ultimatums with escalation paths
- Sanctions and enforcement mechanisms

> **IMPORTANT: The tension_war module functionality has been consolidated into this module.**
> The TensionService class now handles all faction relationship management, tension tracking, and war state determination.
> Legacy tension_war endpoints are still available in the router for backward compatibility.

## Architecture

The system follows a standard layered architecture:

1. **Models** - Data structures for all diplomatic entities
2. **Repository** - Data access and persistence
3. **Services** - Business logic split into:
   - `DiplomacyService` - For treaty and negotiation management
   - `TensionService` - For faction relationship, tension, and war management
4. **Router** - REST API endpoints

## Key Components

### Treaties

Treaties formalize agreements between factions with specific terms. 
Types include: `PEACE`, `ALLIANCE`, `TRADE`, `NON_AGGRESSION`, `MUTUAL_DEFENSE`.

### Negotiations

Multi-step process where factions propose, counter, accept or reject offers.
Successful negotiations result in treaties.

### Treaty Violations

Tracks instances where a faction violates the terms of a treaty, allowing for:
- Recording evidence of violations
- Acknowledgment by the violating party
- Resolution processes with diplomatic consequences
- Automatic treaty enforcement

### Diplomatic Incidents

Tracks significant events that impact diplomatic relations between factions:
- Different severity levels (MINOR, MODERATE, MAJOR, CRITICAL)
- Resolution mechanisms
- Tension impact calculation
- Public/private incident tracking
- Witness tracking for third-party factions

### Ultimatums

Formal demands issued by one faction to another with clear consequences:
- Deadline-based expiration
- Accept/reject decision paths
- Automatic consequences if rejected or expired
- Integration with tension system
- Formal justification tracking

### Sanctions

Economic and diplomatic pressure mechanisms:
- Multiple sanction types (TRADE_EMBARGO, ASSET_FREEZE, etc.)
- Supporting and opposing faction tracking
- Violation recording
- Conditions for lifting
- Economic and diplomatic impact tracking

### Diplomatic Events

Significant occurrences that affect diplomatic relations, such as treaty signings,
violations, declarations of war, etc.

### Faction Relationships

Tracks the state of relations between pairs of factions, including:
- Tension level (0-100)
- Diplomatic status (NEUTRAL, FRIENDLY, ALLIED, HOSTILE, WAR)
- Historical interactions and treaties

## Usage Examples

See the router for endpoint definitions and usage patterns. Key endpoints include:

- Treaty management: `/diplomacy/treaties/*`
- Negotiation process: `/diplomacy/negotiations/*`
- Diplomatic events: `/diplomacy/events/*`
- Faction relationships: `/diplomacy/relations/*`
- Treaty violations: `/diplomacy/violations/*`
- Diplomatic incidents: `/diplomacy/incidents/*`
- Ultimatums: `/diplomacy/ultimatums/*`
- Sanctions: `/diplomacy/sanctions/*`
- Legacy tension endpoints: `/diplomacy/tension/*` and `/diplomacy/war/*`

## Integration

The diplomacy system integrates with:

- Faction system (for faction metadata)
- Event dispatcher (for broadcasting diplomatic events)
- World state (for accessing faction states)

## Migration from tension_war Module

The functionality from the `tension_war` module has been consolidated into the diplomacy system 
for better cohesion and reduced duplication. The new architecture:

1. Moves tension and war-related functionality into the `TensionService` class
2. Preserves backward compatibility through legacy endpoints
3. Enhances the relationship model to track more diplomatic metrics
4. Improves tension adjustment with reasons and history

Use the migration script (`backend/migrate_tension_diplomacy.py`) to update any existing code 
that imports from the legacy `tension_war` module.

## Structure

The diplomacy system is implemented with these core files:

- **__init__.py** - Main module exports
- **models.py** - Data models and domain objects (Treaty, Negotiation, DiplomaticEvent, etc.)
- **schemas.py** - API schemas for request/response validation
- **repository.py** - Data persistence layer for diplomatic entities
- **services.py** - Business logic and operations
- **router.py** - REST API endpoints

## Features

- Treaty management (creation, signing, expiration)
- Negotiation process with offers and counter-offers
- Diplomatic events and event tracking
- Faction relationship management
- Tension tracking between factions (-100 to +100 scale)
- Treaty violation tracking and enforcement
- Diplomatic incident management and resolution
- Ultimatum issuance and response handling
- Sanction imposition and violation tracking

## API Endpoints

### Treaties

- `POST /diplomacy/treaties` - Create a new treaty
- `GET /diplomacy/treaties/{treaty_id}` - Get a treaty by ID
- `GET /diplomacy/treaties` - List treaties (with filtering options)
- `PATCH /diplomacy/treaties/{treaty_id}` - Update a treaty
- `POST /diplomacy/treaties/{treaty_id}/expire` - Mark a treaty as expired

### Negotiations

- `POST /diplomacy/negotiations` - Start a new negotiation
- `GET /diplomacy/negotiations/{negotiation_id}` - Get a negotiation by ID
- `POST /diplomacy/negotiations/{negotiation_id}/offers` - Make an offer
- `POST /diplomacy/negotiations/{negotiation_id}/accept` - Accept the current offer
- `POST /diplomacy/negotiations/{negotiation_id}/reject` - Reject the current offer

### Diplomatic Events

- `POST /diplomacy/events` - Create a new diplomatic event
- `GET /diplomacy/events` - List diplomatic events (with filtering options)

### Faction Relationships

- `GET /diplomacy/relations/{faction_id}` - Get all relationships for a faction
- `GET /diplomacy/relations/{faction_a_id}/{faction_b_id}` - Get relationship between two factions
- `POST /diplomacy/relations/{faction_a_id}/{faction_b_id}/tension` - Update tension
- `POST /diplomacy/relations/{faction_a_id}/{faction_b_id}/status` - Set diplomatic status

### Treaty Violations

- `POST /diplomacy/violations` - Report a treaty violation
- `GET /diplomacy/violations` - List treaty violations (with filtering options)
- `POST /diplomacy/violations/{violation_id}/acknowledge` - Acknowledge a violation
- `POST /diplomacy/violations/{violation_id}/resolve` - Resolve a treaty violation
- `GET /diplomacy/compliance/{faction_id}` - Check treaty compliance of a faction
- `POST /diplomacy/enforce-treaties` - Enforce treaties automatically

### Diplomatic Incidents

- `POST /diplomacy/incidents` - Create a diplomatic incident
- `GET /diplomacy/incidents/{incident_id}` - Get an incident by ID
- `GET /diplomacy/incidents` - List diplomatic incidents (with filtering options)
- `PATCH /diplomacy/incidents/{incident_id}` - Update a diplomatic incident
- `POST /diplomacy/incidents/{incident_id}/resolve` - Resolve a diplomatic incident

### Ultimatums

- `POST /diplomacy/ultimatums` - Issue an ultimatum
- `GET /diplomacy/ultimatums/{ultimatum_id}` - Get an ultimatum by ID
- `GET /diplomacy/ultimatums` - List ultimatums (with filtering options)
- `PATCH /diplomacy/ultimatums/{ultimatum_id}` - Update an ultimatum
- `POST /diplomacy/ultimatums/{ultimatum_id}/respond` - Respond to an ultimatum
- `POST /diplomacy/ultimatums/check-expired` - Check for expired ultimatums

### Sanctions

- `POST /diplomacy/sanctions` - Create a new sanction
- `GET /diplomacy/sanctions/{sanction_id}` - Get a sanction by ID
- `GET /diplomacy/sanctions` - List sanctions (with filtering options)
- `PATCH /diplomacy/sanctions/{sanction_id}` - Update a sanction
- `POST /diplomacy/sanctions/{sanction_id}/lift` - Lift a sanction
- `POST /diplomacy/sanctions/{sanction_id}/violations` - Record a sanction violation
- `POST /diplomacy/sanctions/check-expired` - Check for expired sanctions
