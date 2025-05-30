# Feats Data

This directory contains the master data file for Visual DM's feat system, which defines character abilities, combat techniques, and special powers.

## Files

- `feats_master.json`: The canonical, finalized schema for all feats in the game

## Legacy Files

The original feats files are preserved in `/backend/data/feats/` for historical and development reference:

- `feats.json`: Basic feat definitions
- `feats_fully_finalized_schema.json`: Complete schema with all feat details
- `feats_index_full_prereqs.json`: Index with prerequisite information
- `feats_index_updated.json`: Updated index with revisions
- `feats_structured_for_logic.json`: Structured format for game logic
- `feats_updated_with_casting_ability.json`: Version with casting ability information
- `feats_with_prerequisites.json`: Version focusing on prerequisites
- `Active_Combat_Feats.json`: Combat-specific feats

## Usage

The master feat file is consumed by the character, NPC, and monster generation systems. It defines the abilities and special powers available to all entities in the game.

For implementation details, see the Development Bible section on the Feat System. 