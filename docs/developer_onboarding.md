# Persistence Layer Developer Onboarding Guide

**Version:** 1.0.0
**Last Updated:** 2023-11-15
**Status:** Active

## Introduction

Welcome to the Visual DM persistence layer! This guide will help you set up your development environment, understand our data architecture, and follow best practices when working with the database components of our system.

## Getting Started

### Prerequisites

Before you begin, please ensure you have the following installed:

- Node.js (v16+)
- PostgreSQL (v13+)
- Docker (for containerized development environment)
- Git

### Local Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-organization/visual-dm.git
   cd visual-dm
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Set up local database**

   Using Docker (recommended):

   ```bash
   # Start PostgreSQL and initialize with proper configuration
   docker-compose up -d db
   ```

   Or manually:

   ```bash
   # Create a new database
   createdb visual_dm_dev
   
   # Apply migrations
   npm run migrate up
   ```

4. **Configure environment variables**

   Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

   Update the database connection details in `.env`:

   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=visual_dm_dev
   DB_USER=postgres
   DB_PASSWORD=your_password
   ```

5. **Seed the database with sample data**

   ```bash
   npm run seed
   ```

6. **Verify your setup**

   ```bash
   npm run test:db
   ```

## Data Architecture Overview

Our persistence layer follows a clean, layered architecture:

1. **Repository Layer** - Abstracts database operations and provides domain-specific methods
2. **Entity Mappers** - Converts between database rows and domain objects
3. **Query Builders** - Constructs SQL queries in a type-safe way
4. **Connection Manager** - Handles database connections and transactions

![Data Access Layer Architecture](./diagrams/data_access_layer.png)

Review the [Entity Relationship Diagram](./diagrams/entity_relationship_diagram.png) to understand our data model structure.

## Core Concepts

### Repository Pattern

We use the repository pattern to abstract database access. Each entity type has a corresponding repository that provides CRUD operations and domain-specific queries.

Example repository usage:

```typescript
// Get an item by ID
const item = await itemRepository.findById('some-uuid');

// Create a new item
const newItem = await itemRepository.create({
  name: 'Magic Sword',
  description: 'A powerful magical sword',
  type: 'WEAPON',
  weight: 3.5,
  value: 500,
  rarityId: 3, // RARE
  baseStats: { damage: 25, critChance: 0.1 }
});
```

### Transactions

For operations that require atomicity across multiple changes, use transaction support:

```typescript
await transactionManager.runInTransaction(async (txClient) => {
  // All operations in this callback run in a single transaction
  await itemRepository.create(newItem, txClient);
  await inventoryRepository.addItem(playerId, newItem.id, txClient);
});
```

### Environment Separation

We maintain separate database instances for each environment:

- `development` - For local development
- `test` - For automated testing
- `staging` - For pre-production testing
- `production` - For live system

Always ensure your code works correctly across all environments. 

## Common Tasks

### Creating a New Entity

1. **Define your entity and repository interface**

   Create a new file in `src/entities`:

   ```typescript
   // src/entities/Character.ts
   export interface Character {
     id: string;
     name: string;
     level: number;
     playerId: string;
     attributes: Record<string, number>;
     createdAt: Date;
     updatedAt: Date;
   }
   
   export interface CharacterRepository {
     findById(id: string): Promise<Character | null>;
     findByPlayerId(playerId: string): Promise<Character[]>;
     create(character: Omit<Character, 'id' | 'createdAt' | 'updatedAt'>): Promise<Character>;
     update(id: string, character: Partial<Character>): Promise<Character>;
     delete(id: string): Promise<boolean>;
   }
   ```

2. **Create migration file**

   Add a new migration in `src/db/migrations` following the naming convention:

   ```sql
   -- 003_create_characters.sql
   CREATE TABLE characters (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     name VARCHAR(100) NOT NULL,
     level INTEGER NOT NULL DEFAULT 1,
     player_id UUID NOT NULL REFERENCES players(id),
     attributes JSONB NOT NULL DEFAULT '{}',
     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );
   
   CREATE INDEX idx_characters_player_id ON characters(player_id);
   
   CREATE TRIGGER update_characters_updated_at
       BEFORE UPDATE ON characters
       FOR EACH ROW
       EXECUTE FUNCTION update_updated_at_column();
   ```

3. **Implement the repository**

   Create a file in `src/repositories`:

   ```typescript
   // src/repositories/PgCharacterRepository.ts
   import { Pool, PoolClient } from 'pg';
   import { Character, CharacterRepository } from '../entities/Character';
   
   export class PgCharacterRepository implements CharacterRepository {
     constructor(private pool: Pool) {}
     
     async findById(id: string): Promise<Character | null> {
       const result = await this.pool.query(
         'SELECT * FROM characters WHERE id = $1',
         [id]
       );
       
       if (result.rows.length === 0) {
         return null;
       }
       
       return this.mapRowToCharacter(result.rows[0]);
     }
     
     // ... implement other methods
     
     private mapRowToCharacter(row: any): Character {
       return {
         id: row.id,
         name: row.name,
         level: row.level,
         playerId: row.player_id,
         attributes: row.attributes,
         createdAt: row.created_at,
         updatedAt: row.updated_at
       };
     }
   }
   ```

4. **Register the repository**

   Update the dependency injection container in `src/di.ts`:

   ```typescript
   container.register('CharacterRepository', {
     useClass: PgCharacterRepository
   });
   ```

5. **Add documentation**

   Update the [data models documentation](./data_models.md) with your new entity.

### Adding a Migration

To add a new migration:

1. Determine the next sequence number
2. Create a file in `src/db/migrations` with the naming pattern `[seq]_[action]_[entity].sql`
3. Include forward migration and commented rollback statements
4. Update documentation as needed

Example:

```sql
-- 004_add_experience_to_characters.sql
-- Description: Add experience points tracking to characters
-- Date: 2023-11-15

-- Forward migration
ALTER TABLE characters ADD COLUMN experience INTEGER NOT NULL DEFAULT 0;
CREATE INDEX idx_characters_experience ON characters(experience);

-- Rollback statements
-- DROP INDEX idx_characters_experience;
-- ALTER TABLE characters DROP COLUMN experience;
```

Apply your migration:

```bash
npm run migrate up
```

### Working with JSON/JSONB Fields

PostgreSQL's JSONB type is used for flexible data structures. Here's how to work with it:

```typescript
// Querying specific JSON properties
const powerfulItems = await this.pool.query(
  'SELECT * FROM items WHERE base_stats->\'damage\' > $1',
  [30]
);

// Updating JSON properties
await this.pool.query(
  'UPDATE items SET base_stats = jsonb_set(base_stats, \'{damage}\', $1) WHERE id = $2',
  ['40', itemId]
);

// Adding to JSON array
await this.pool.query(
  'UPDATE characters SET attributes = jsonb_insert(attributes, \'{abilities}\', $1) WHERE id = $2',
  ['["fireball"]', characterId]
);
```

## Common Pitfalls and Gotchas

### N+1 Query Problem

Avoid loading related entities in a loop, which can lead to performance issues:

```typescript
// BAD: N+1 query pattern
const players = await playerRepository.findAll();
for (const player of players) {
  // This results in a separate query for EACH player
  player.inventory = await inventoryRepository.findByPlayerId(player.id);
}

// GOOD: Use JOIN queries or batch loading
const players = await playerRepository.findAllWithInventory();
```

### Connection Management

Never create database connections outside the connection pool:

```typescript
// BAD: Creating a direct connection
const client = new Client({ ...config });
await client.connect();

// GOOD: Using the connection pool
const client = await pool.connect();
try {
  // use client
} finally {
  client.release(); // ALWAYS release connections back to the pool
}

// BETTER: Use the repository pattern which handles this automatically
const items = await itemRepository.findAll();
```

### SQL Injection

Always use parameterized queries, never string concatenation:

```typescript
// BAD: SQL injection vulnerability
await pool.query(`SELECT * FROM items WHERE name = '${name}'`);

// GOOD: Using parameterized query
await pool.query('SELECT * FROM items WHERE name = $1', [name]);
```

## Troubleshooting

### Common Errors

**`ER_NO_SUCH_TABLE`**
- **Cause**: The required database table doesn't exist
- **Solution**: Run migrations to create the table

**`Connection refused`**
- **Cause**: Database server is not running or connection details are incorrect
- **Solution**: Check your database connection settings and ensure the server is running

**`Invalid input syntax for type uuid`**
- **Cause**: Trying to use an invalid UUID format
- **Solution**: Ensure UUIDs are in the correct format (e.g., 123e4567-e89b-12d3-a456-426614174000)

### Debugging Database Issues

1. **Check the database logs**

   ```bash
   docker-compose logs db
   ```

2. **Connect directly to the database**

   ```bash
   psql -h localhost -U postgres -d visual_dm_dev
   ```

3. **View current migrations**

   ```sql
   SELECT * FROM schema_migrations ORDER BY applied_at;
   ```

4. **View table structure**

   ```sql
   \d items
   ```

## Resources and Further Reading

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [node-postgres Documentation](https://node-postgres.com/)
- [SQL Tutorial](https://www.w3schools.com/sql/)
- [Entity-Relationship Modeling](https://www.visual-paradigm.com/guide/data-modeling/what-is-entity-relationship-diagram/)

## Contributing to the Persistence Layer

Please follow these guidelines when contributing to the persistence layer:

1. Always write migrations for schema changes
2. Include both forward and rollback statements
3. Write tests for your repositories
4. Update documentation to reflect your changes
5. Follow the existing naming conventions
6. Use parameterized queries to prevent SQL injection
7. Release connections back to the pool

## Getting Help

If you have questions or need assistance:

- **Slack Channel**: #db-persistence-team
- **Maintainers**: @dbteam, @leaddev
- **Documentation**: See [data_models.md](./data_models.md) and [migration_procedures.md](./migration_procedures.md) 