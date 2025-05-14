# Database Migration Procedures

**Version:** 1.0.0
**Last Updated:** 2023-11-15
**Status:** Active

## Overview

This document outlines the standardized procedures for performing database schema changes, data migrations, and version management. Following these procedures ensures that database changes are applied consistently and safely across all environments.

## Migration File Structure

### Location

All migration files are stored in the `src/db/migrations/` directory. Files are prefixed with a sequential number to indicate the order in which they should be applied (e.g., `001_create_base_items.sql`).

### Naming Convention

Migration files should follow this naming pattern:

```
[3-digit-sequence]_[action]_[table_name].sql
```

Examples:
- `001_create_base_items.sql`
- `002_create_rarity_tiers.sql`
- `003_add_timestamp_to_inventory.sql`
- `004_rename_user_column.sql`

### File Content Structure

Each migration file should contain:

1. A clear comment header explaining the purpose of the migration
2. Forward migration SQL statements
3. Rollback statements (commented out or in a separate down file)
4. Any necessary data transformation logic

Example:

```sql
-- Migration: Add last_login column to users table
-- Description: Tracks the last time a user logged in
-- Date: 2023-11-15

-- Forward migration
ALTER TABLE users ADD COLUMN last_login TIMESTAMP WITH TIME ZONE;
CREATE INDEX idx_users_last_login ON users(last_login);

-- Rollback statements
-- ALTER TABLE users DROP COLUMN last_login;
-- DROP INDEX idx_users_last_login;
```

## Migration Process

### Adding New Migrations

1. Determine the next sequence number by finding the highest existing number and incrementing by 1
2. Create a new SQL file with the correct naming convention
3. Add SQL statements for the schema changes and any necessary data transformations
4. Include commented rollback statements
5. Add the file to version control
6. Document the change in the migration history log

### Applying Migrations

Migrations should be applied in the following order:

1. Development environment
2. Testing/QA environment
3. Staging environment
4. Production environment

Use the following command to apply migrations:

```bash
# Using the migration tool
npm run migrate up

# Directly using psql (if necessary)
psql -h <host> -U <user> -d <database> -f src/db/migrations/[migration_file].sql
```

Always verify that each migration completes successfully before proceeding to the next environment.

### Rollback Procedure

If a migration fails or causes issues, use the rollback procedure:

1. Identify the problematic migration
2. Execute the rollback statements from that migration
3. Verify the rollback was successful
4. Fix the migration file
5. Re-apply the corrected migration

```bash
# Using the migration tool
npm run migrate down

# Directly using psql (if necessary)
psql -h <host> -U <user> -d <database> -f src/db/migrations/rollbacks/[migration_file].sql
```

## Data Validation

### Pre-Migration Validation

Before applying migrations to production, perform the following checks:

1. Verify the migration works in development and testing environments
2. Run a dry-run to estimate execution time
3. Check for potential lock issues or performance impacts
4. Ensure backup procedures are in place
5. Schedule the migration during low-usage periods if it may cause downtime

### Post-Migration Validation

After applying a migration, verify:

1. The schema changes were applied correctly
2. Data integrity is maintained
3. Application functionality is not adversely affected
4. Indexes are working as expected
5. Query performance meets requirements

## Version Management

### Migration Versioning

The database version is tracked in a special table called `schema_migrations`:

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
  version VARCHAR(255) PRIMARY KEY,
  applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

Each migration automatically updates this table when applied.

### Database Version History

| Version | Date | Description | Applied By |
|---------|------|-------------|------------|
| 001 | 2023-10-01 | Initial schema with items table | John Doe |
| 002 | 2023-10-15 | Added rarity tiers | Jane Smith |

## Testing Migrations

### Test Requirements

All migrations must be tested for:

1. **Correctness**: Schema changes are applied as expected
2. **Performance**: Migration completes within an acceptable timeframe
3. **Rollback**: Rollback procedure works correctly
4. **Application Compatibility**: Application continues to function with the new schema

### Test Procedures

1. Apply the migration to a test database
2. Run automated tests against the new schema
3. Test rollback and reapplication
4. Benchmark performance with realistic data volumes
5. Verify all application features that interact with the changed schema

## Best Practices

### DO:

- Create small, focused migrations that do one thing
- Include a description and purpose in each migration file
- Test migrations thoroughly before applying to production
- Schedule complex migrations during maintenance windows
- Always have a rollback plan
- Document all migrations in the version history

### DON'T:

- Modify existing migration files once they've been applied to any environment
- Combine multiple unrelated schema changes in a single migration
- Apply migrations directly to production without testing
- Forget to update application code to work with the new schema
- Skip the validation steps

## Migration Templates

### Basic Table Creation

```sql
-- Migration: Create [table_name]
-- Description: [description]
-- Date: [YYYY-MM-DD]

-- Forward migration
CREATE TABLE [table_name] (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  [column_name] [data_type] [constraints],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_[table_name]_[column_name] ON [table_name]([column_name]);

-- Create updated_at trigger
CREATE TRIGGER update_[table_name]_updated_at
    BEFORE UPDATE ON [table_name]
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Rollback
-- DROP TRIGGER update_[table_name]_updated_at ON [table_name];
-- DROP INDEX idx_[table_name]_[column_name];
-- DROP TABLE [table_name];
```

### Adding a Column

```sql
-- Migration: Add [column_name] to [table_name]
-- Description: [description]
-- Date: [YYYY-MM-DD]

-- Forward migration
ALTER TABLE [table_name] ADD COLUMN [column_name] [data_type] [constraints];
CREATE INDEX idx_[table_name]_[column_name] ON [table_name]([column_name]);

-- Rollback
-- DROP INDEX idx_[table_name]_[column_name];
-- ALTER TABLE [table_name] DROP COLUMN [column_name];
```

### Creating an Enum Type

```sql
-- Migration: Create [enum_name] enum type
-- Description: [description]
-- Date: [YYYY-MM-DD]

-- Forward migration
CREATE TYPE [enum_name] AS ENUM (
  'VALUE1',
  'VALUE2',
  'VALUE3'
);

-- Rollback
-- DROP TYPE [enum_name];
```

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2023-11-15 | DB Architecture Team | Initial documentation | 