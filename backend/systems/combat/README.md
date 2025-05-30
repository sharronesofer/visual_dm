# Combat System

This directory contains the combat system implementation for Visual DM.

The combat system provides turn-based combat capabilities with effects, combatants, and state management.

## Structure

- **models/** - Data models for combat statistics
- **schemas/** - Pydantic schemas for API interfaces 
- **services/** - Business logic for combat operations
- **repositories/** - Data storage and retrieval for combat state
- **routers/** - FastAPI routes for combat endpoints

## API Endpoints

- **POST /combat/state** - Create a new combat instance
- **GET /combat/state/{combat_id}** - Get a specific combat state
- **PUT /combat/state/{combat_id}** - Update an existing combat state
- **DELETE /combat/state/{combat_id}** - End a combat instance
- **GET /combat/states** - List all active combat instances
