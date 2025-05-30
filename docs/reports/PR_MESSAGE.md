# Implement Canonical Relationship System

## What does this PR do?
This PR implements the canonical relationship system as specified in the Visual DM Development Bible. It creates a unified system for managing all entity relationships (character-faction, character-quest, spatial, authentication) with a standardized data structure and API endpoints.

## Type of change
- [x] New feature (non-breaking change which adds functionality)
- [x] Refactoring (code improvement without functional changes)
- [x] This change requires a documentation update

## Motivation and Context
The Development Bible specifies a unified relationship system with a standard structure, but the current implementation was inconsistent with these specifications. This PR brings the codebase into alignment with the canonical requirements while maintaining backward compatibility.

Key issues addressed:
1. Inconsistent file organization - relationship code was spread across multiple locations
2. Non-standard API endpoints - using `/relationships/{character_id}` instead of `/characters/{character_id}/relationships/`
3. Inconsistent model attributes - using UUIDs vs. string IDs
4. Missing specialized endpoints for specific relationship operations
5. Additional non-canonical relationship types
6. Redundant specialized service methods

## How Has This Been Tested?
- [x] Unit tests for the Relationship model
- [x] Unit tests for the RelationshipService
- [x] Integration tests for the API endpoints
- [x] Manual testing of key endpoints

## Breaking Changes
While this change introduces a new, canonical API, it maintains backward compatibility with the existing implementation by:
1. Marking the existing implementation as deprecated with warnings
2. Updating documentation to direct users to the canonical implementation
3. Keeping the old endpoints functional but displaying deprecation notices

Migration path is documented in `backend/app/characters/MIGRATION.md`.

## Checklist:
- [x] My code follows the style guidelines of this project
- [x] I have performed a self-review of my own code
- [x] I have commented my code, particularly in hard-to-understand areas
- [x] I have made corresponding changes to the documentation
- [x] My changes generate no new warnings
- [x] I have added tests that prove my fix is effective or that my feature works
- [x] New and existing unit tests pass locally with my changes
- [x] I have created a changeset for this user-facing change

## Additional context
This implementation is part of the larger Memory System Refactoring initiative. The relationship system serves as a foundational component for character memories, faction interactions, quest tracking, and spatial relationships. 