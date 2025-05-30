# Core Mechanical Systems Data

This directory contains data files for Visual DM's core mechanical systems as outlined in the Development Bible.

## Directory Structure

- `memory/`: Memory system data and memory type definitions
- `motif/`: Motif definitions and influence rules
- `rumor/`: Rumor generation data and templates
- `faction/`: Faction data, relationships, and reputation systems
- `religion/`: Religion templates and religious mechanics
- `economy/`: Economy rules, trade systems, and resource values
- `time/`: Calendar data, time events, and time-based mechanics
- `weather/`: Weather types, patterns, and environmental effects
- `events/`: Event definitions and triggering conditions

## Usage

These data files are consumed by their respective systems in the backend. Each system should have its own data model and validation schemas.

For details on each system's implementation, see the Development Bible and the corresponding system's documentation in the `backend/systems/` directory. 