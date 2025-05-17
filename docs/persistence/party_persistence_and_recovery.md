# Party Data Persistence, Versioning, Migration, and Recovery

## Overview
This document describes the architecture, components, and operational procedures for the party data persistence layer, including versioning, migration, and recovery mechanisms. It is intended for developers, maintainers, and integrators working with party data in Visual DM.

---

## Architecture & Components

- **PartyRepository**: Handles all CRUD operations for party data, enforces transaction-based persistence, atomicity, and data integrity via SHA-256 checksums.
- **Schema Versioning**: Each party record stores a `schema_version`. The repository uses a strategy pattern to handle upgrades and backward compatibility.
- **Migration Framework**: The `PartyMigrationManager` manages migration paths, batch migration, validation, and rollback. Migration functions are registered for each version pair.
- **Recovery Manager**: The `PartyRecoveryManager` provides point-in-time recovery (via WAL), automated backups, restore, and integrity validation.

### Diagram: High-Level Architecture
```
[Client/API] -> [PartyRepository] -> [DB]
                        |-> [Versioning]
                        |-> [MigrationManager]
                        |-> [RecoveryManager]
```

---

## Recovery Procedures

### 1. Restore from Backup
1. Stop all writes to the party table.
2. Use `PartyRecoveryManager.restore_from_backup('party_backup_<timestamp>.json')`.
3. Validate with `PartyRecoveryManager.validate_recovery()`.
4. Resume normal operations.

### 2. Point-in-Time Recovery
1. Stop all writes to the party table.
2. Use `PartyRecoveryManager.point_in_time_recovery('party_wal.log', '<target_timestamp>')`.
3. Validate with `PartyRecoveryManager.validate_recovery()`.
4. Resume normal operations.

### 3. Automated Backup
- Backups are created automatically every N seconds (configurable).
- Use `PartyRecoveryManager.list_backups()` to view available backups.

---

## Troubleshooting Guide
- **Checksum mismatch**: Indicates possible data corruption. Restore from backup or WAL.
- **Migration failure**: Use rollback support in `PartyMigrationManager`. Check migration function logic.
- **Backup validation fails**: Do not restore from this backup. Use an earlier backup.
- **Automated backup not running**: Ensure the recovery manager thread is started and not stopped.

---

## Integration Points
- **Reputation System**: PartyRepository is the single source of truth for party membership, which is referenced by reputation calculations.
- **Emotion System**: Party membership changes trigger emotion events; subscribe to repository events or use hooks.
- **Interaction System**: Party state is used for interaction eligibility and outcomes; always query via the repository for up-to-date data.

---

## Code Examples

### Creating a Party
```python
from app.core.repositories.party_repository import PartyRepository
repo = PartyRepository(session)
party = repo.create_party({
    'name': 'Adventurers',
    'leader_id': 1,
    # ... other fields ...
})
```

### Migrating a Party to a New Schema Version
```python
from app.core.repositories.party_repository import PartyMigrationManager
migration_manager = PartyMigrationManager(session)
def migration_fn(party):
    # ... migration logic ...
    return party
migration_manager.register_migration('1.0.0', '1.1.0', migration_fn)
migration_manager.migrate_party(party, '1.1.0')
```

### Restoring from Backup
```python
from app.core.repositories.party_repository import PartyRecoveryManager
recovery_manager = PartyRecoveryManager(session)
recovery_manager.restore_from_backup('party_backup_20240516T120000.json')
recovery_manager.validate_recovery()
```

---

## Developer Guide: Extending the Persistence Layer
- **Add a new schema version**: Subclass `PartyVersionStrategy`, implement upgrade/downgrade, and register in `PartyVersionRegistry`.
- **Add a migration**: Register a migration function in `PartyMigrationManager` for the version pair.
- **Add a new recovery workflow**: Extend `PartyRecoveryManager` with new methods as needed.
- **Integrate with new systems**: Use repository hooks/events for consistency.

---

## Diagrams
- [ ] Add sequence diagram: Party creation, migration, and recovery
- [ ] Add data flow diagram: Backup and restore

---

## References
- See also: [backup-recovery.md](./backup-recovery.md), [disaster-recovery.md](../disaster-recovery.md), [integration_points.md](./integration_points.md)
- For onboarding: [developer_onboarding.md](./developer_onboarding.md)
- For migration details: [migration_procedures.md](./migration_procedures.md) 