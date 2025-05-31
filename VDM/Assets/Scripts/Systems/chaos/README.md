# Chaos System

This directory contains the Unity frontend implementation for the Chaos system, mirroring the backend/systems/chaos structure.

## Directory Structure

- **Models/** - DTOs and data models for API communication
- **Services/** - HTTP/WebSocket communication services
- **UI/** - User interface components
- **Integration/** - Unity-specific integration logic

## Architecture

This system follows the standard frontend-backend alignment pattern:
1. Models mirror backend DTOs exactly
2. Services handle API communication
3. UI components provide user interaction
4. Integration layer bridges Unity-specific requirements

## Dependencies

This system depends on:
- Backend: backend/systems/chaos
- Frontend: Core, Services, UI frameworks

## Features

- Real-time chaos event monitoring
- Pressure source visualization
- Environmental effects integration
- Admin configuration panels 