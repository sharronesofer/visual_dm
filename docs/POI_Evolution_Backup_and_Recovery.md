# POI Evolution Backup, Restore, and Integrity Procedures

## Overview
This document describes how to back up, restore, and verify the integrity of the POI evolution history tables (`poi_states`, `poi_transitions`, `poi_histories`) in the Visual DM database.

---

## Backup Procedure

Use the provided shell script to create a timestamped backup of the POI evolution tables.

### Usage
```sh
bash scripts/backup_poi_evolution.sh [backup_directory]
```
- Default backup directory: `./backups`
- Output: `poi_evolution_backup_<timestamp>.sql`

---

## Restore Procedure

Use the restore script to load a backup into the database. **Warning:** This will overwrite the current POI evolution tables.

### Usage
```sh
bash scripts/restore_poi_evolution.sh <backup_file.sql>
```
- Prompts for confirmation before proceeding.

---

## Data Integrity Check

Run the Python script to check for referential integrity issues in the POI evolution tables.

### Usage
```sh
python3 scripts/check_poi_evolution_integrity.py
```
- Reports orphaned states, transitions with missing states, and histories with missing references.

---

## Best Practices
- Schedule regular backups (e.g., via cron or CI/CD pipeline).
- Store backups securely and offsite if possible.
- Periodically test restores in a staging environment.
- Run integrity checks after restores and before major upgrades.
- Retain backups according to your data retention policy.

---

## Requirements
- PostgreSQL client tools (`pg_dump`, `psql`)
- Python 3 with `psycopg2` installed (`pip install psycopg2`)

---

## Performance Optimization & Integration

### Indexes
- The POI evolution tables are indexed on all major foreign keys and query columns (see migration).
- For large-scale deployments, monitor query plans and add indexes as needed.

### Recommended Repository Interface
Implement or extend your repository/service layer with methods like:
- `get_current_state(poi_id)`
- `get_state_history(poi_id)`
- `get_transitions(poi_id, event_type=None)`
- `add_state(poi_id, state_data, created_by)`
- `add_transition(poi_id, from_state_id, to_state_id, event_type, event_data, triggered_by)`

### Example SQLAlchemy Queries
```python
# Get current state for a POI
session.query(POIState).filter_by(poi_id=poi_id, valid_to=None).one()

# Get full state history for a POI
session.query(POIState).filter_by(poi_id=poi_id).order_by(POIState.valid_from.desc()).all()

# Get transitions for a POI
session.query(POITransition).filter_by(poi_id=poi_id).order_by(POITransition.triggered_at.desc()).all()

# Get transitions by event type
session.query(POITransition).filter_by(poi_id=poi_id, event_type='upgrade').all()
```

### Monitoring & Scaling
- Enable PostgreSQL slow query logging in production.
- Use `EXPLAIN ANALYZE` to profile slow queries.
- Consider table partitioning for `poi_histories` if it grows very large.
- Regularly run the integrity check script after bulk operations or restores.

---

For questions or issues, contact the project maintainer. 