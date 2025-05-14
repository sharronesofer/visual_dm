# Persistence Layer Integration Points

**Version:** 1.0.0
**Last Updated:** 2023-11-15
**Status:** Active

## Overview

This document outlines all integration points between the persistence layer and other system components, including APIs, service interfaces, and external system connections. It serves as a comprehensive reference for developers working on features that interact with the persistence layer.

## Data Access Layer Architecture

The persistence layer follows a repository pattern to abstract database operations from business logic. The following diagram illustrates the high-level architecture:

![Data Access Layer Architecture](./diagrams/data_access_layer.png)

## Core Integration Interfaces

### Item Repository

**Interface:** `ItemRepository`
**File Location:** `src/repositories/ItemRepository.ts`

This interface provides methods for CRUD operations on game items.

#### Methods

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `findById` | `id: string` | `Promise<Item>` | Retrieves an item by its UUID |
| `findAll` | `filter?: ItemFilter` | `Promise<Item[]>` | Retrieves items matching filter criteria |
| `findByType` | `type: ItemType` | `Promise<Item[]>` | Retrieves items of a specific type |
| `findByRarity` | `rarityId: number` | `Promise<Item[]>` | Retrieves items of a specific rarity |
| `create` | `item: ItemInput` | `Promise<Item>` | Creates a new item |
| `update` | `id: string, item: Partial<ItemInput>` | `Promise<Item>` | Updates an existing item |
| `delete` | `id: string` | `Promise<boolean>` | Deletes an item |

#### Example Usage

```typescript
// Get all weapons
const weapons = await itemRepository.findByType('WEAPON');

// Create a new item
const newItem = await itemRepository.create({
  name: 'Excalibur',
  description: 'A legendary sword',
  type: 'WEAPON',
  weight: 5.5,
  value: 1000,
  rarityId: 5, // Legendary
  baseStats: { damage: 50, speed: 1.2 }
});
```

### Rarity Repository

**Interface:** `RarityRepository`
**File Location:** `src/repositories/RarityRepository.ts`

This interface provides methods for accessing rarity tier data.

#### Methods

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `findById` | `id: number` | `Promise<RarityTier>` | Retrieves a rarity tier by ID |
| `findByName` | `name: RarityName` | `Promise<RarityTier>` | Retrieves a rarity tier by name |
| `findAll` | - | `Promise<RarityTier[]>` | Retrieves all rarity tiers |

#### Example Usage

```typescript
// Get legendary rarity tier
const legendaryTier = await rarityRepository.findByName('LEGENDARY');

// Get all rarity tiers
const allTiers = await rarityRepository.findAll();
```

## API Integration

### REST API Endpoints

#### Items API

**Base URL:** `/api/v1/items`

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|-------------|----------|
| `/api/v1/items` | GET | List all items | N/A | Array of Item objects |
| `/api/v1/items?type={type}` | GET | Filter items by type | N/A | Array of Item objects |
| `/api/v1/items/{id}` | GET | Get item by ID | N/A | Item object |
| `/api/v1/items` | POST | Create a new item | ItemInput object | Created Item object |
| `/api/v1/items/{id}` | PUT | Update an item | Partial ItemInput | Updated Item object |
| `/api/v1/items/{id}` | DELETE | Delete an item | N/A | Success message |

#### Rarity API

**Base URL:** `/api/v1/rarities`

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|-------------|----------|
| `/api/v1/rarities` | GET | List all rarity tiers | N/A | Array of RarityTier objects |
| `/api/v1/rarities/{id}` | GET | Get rarity tier by ID | N/A | RarityTier object |

### GraphQL API

**Endpoint:** `/api/graphql`

#### Queries

```graphql
type Query {
  item(id: ID!): Item
  items(type: ItemType, rarityId: Int): [Item!]!
  rarities: [RarityTier!]!
  rarity(id: Int!): RarityTier
}
```

#### Mutations

```graphql
type Mutation {
  createItem(input: ItemInput!): Item!
  updateItem(id: ID!, input: ItemUpdateInput!): Item!
  deleteItem(id: ID!): Boolean!
}
```

#### Types

```graphql
type Item {
  id: ID!
  name: String!
  description: String!
  type: ItemType!
  weight: Float!
  value: Int!
  baseStats: JSON!
  rarity: RarityTier
  createdAt: DateTime!
  updatedAt: DateTime!
}

type RarityTier {
  id: Int!
  name: RarityName!
  probability: Float!
  valueMultiplier: Float!
  colorHex: String!
  createdAt: DateTime!
}

enum ItemType {
  WEAPON
  ARMOR
  POTION
  SCROLL
  MATERIAL
  TREASURE
  KEY
  QUEST
  MISC
}

enum RarityName {
  COMMON
  UNCOMMON
  RARE
  EPIC
  LEGENDARY
}

input ItemInput {
  name: String!
  description: String!
  type: ItemType!
  weight: Float!
  value: Int!
  rarityId: Int
  baseStats: JSON!
}

input ItemUpdateInput {
  name: String
  description: String
  type: ItemType
  weight: Float
  value: Int
  rarityId: Int
  baseStats: JSON
}
```

## Service-to-Service Integration

### ItemService

**Interface:** `ItemService`
**File Location:** `src/services/ItemService.ts`

This service encapsulates business logic for item management and integrates with the persistence layer.

#### Methods

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `getItemById` | `id: string` | `Promise<Item>` | Retrieves an item with additional business logic |
| `getAllItems` | `filter?: ItemFilter` | `Promise<Item[]>` | Retrieves items with filtering and sorting |
| `calculateItemValue` | `item: Item` | `Promise<number>` | Calculates the actual value based on rarity |
| `createItem` | `input: ItemInput` | `Promise<Item>` | Creates an item with validation |
| `modifyItem` | `id: string, changes: Partial<ItemInput>` | `Promise<Item>` | Updates an item with validation |
| `removeItem` | `id: string` | `Promise<boolean>` | Removes an item with cascading logic |

#### Dependencies

- `ItemRepository`
- `RarityRepository`
- `ValidationService`

### InventoryManager

**Interface:** `InventoryManager`
**File Location:** `src/services/InventoryManager.ts`

This service manages player inventories and integrates with the persistence layer for item retrieval.

#### Methods

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `addItemToInventory` | `playerId: string, itemId: string, quantity?: number` | `Promise<boolean>` | Adds an item to player inventory |
| `removeItemFromInventory` | `playerId: string, itemId: string, quantity?: number` | `Promise<boolean>` | Removes an item from inventory |
| `getPlayerInventory` | `playerId: string` | `Promise<InventoryItem[]>` | Gets all items in a player's inventory |

#### Dependencies

- `ItemRepository`
- `PlayerRepository`
- `InventoryRepository`

## External System Integration

### Game Client Integration

The game client interacts with the persistence layer through REST API and WebSocket connections.

#### REST API Interactions

- GET `/api/v1/items` - Retrieve item data for client display
- GET `/api/v1/items/{id}` - Fetch detailed item information

#### WebSocket Events

**Channel:** `item-updates`

| Event | Data | Description |
|-------|------|-------------|
| `item-acquired` | `{ playerId, itemId, timestamp }` | Player acquired an item |
| `item-used` | `{ playerId, itemId, timestamp }` | Player used an item |
| `item-modified` | `{ itemId, changes, timestamp }` | Item properties were modified |

### Analytics System Integration

The persistence layer sends event data to the analytics system through a message queue.

#### Message Queue Configuration

- **Queue Name:** `game-events`
- **Message Format:** JSON
- **Delivery:** At-least-once delivery

#### Event Types

| Event Type | Payload | Description |
|------------|---------|-------------|
| `ITEM_CREATED` | `{ itemId, name, type, rarity, timestamp }` | New item created |
| `ITEM_DELETED` | `{ itemId, timestamp }` | Item deleted |
| `ITEM_TRANSACTION` | `{ itemId, fromId, toId, quantity, value, timestamp }` | Item changed ownership |

## Authentication and Authorization

### Authentication Methods

- **JWT Tokens:** Used for all API requests
- **API Keys:** Used for service-to-service communication

### Authorization Levels

| Role | Description | Permissions |
|------|-------------|------------|
| `READ_ONLY` | Can only read data | GET operations on all endpoints |
| `GAME_CLIENT` | Normal game client access | GET operations + limited inventory POST/PUT |
| `ADMIN` | Administrative access | All operations on all endpoints |
| `SERVICE` | Internal service access | Specific endpoints based on service requirements |

### Implementation

Authorization is implemented using middleware that validates the JWT token or API key and checks permissions before allowing access to the requested resource.

```typescript
// Example middleware usage
app.use('/api/v1/items', authorize(['ADMIN', 'SERVICE']), itemsRouter);
```

## Error Handling

### Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `DB_CONNECTION_ERROR` | 503 | Database connection failure |
| `ITEM_NOT_FOUND` | 404 | Requested item doesn't exist |
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `AUTHENTICATION_ERROR` | 401 | Invalid credentials |

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Item weight must be positive",
    "details": {
      "field": "weight",
      "constraint": "min",
      "value": -5
    }
  }
}
```

## Monitoring and Logging

### Database Query Logging

All database queries are logged with the following information:

- Query text (with sensitive data redacted)
- Execution time
- Number of rows affected/returned
- Timestamp
- Correlation ID for request tracing

### Performance Metrics

The following metrics are collected for monitoring:

- Query execution time
- Connection pool utilization
- Cache hit/miss rate
- Transaction rate
- Error rate

### Integration with Monitoring Tools

Database metrics are integrated with the following monitoring systems:

- **Prometheus:** For metrics collection
- **Grafana:** For visualization
- **ELK Stack:** For log analysis
- **Pagerduty:** For alerts

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2023-11-15 | Integration Team | Initial documentation | 