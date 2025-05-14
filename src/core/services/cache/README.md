# Cache Invalidation System

This module provides a comprehensive cache invalidation system with multiple strategies:

1. **Time-Based Invalidation**: Automatically expires cache entries after a specified TTL
2. **Tag-Based Invalidation**: Allows invalidating related cache entries using tags
3. **Event-Driven Invalidation**: Provides a pub/sub system for invalidating cache on data changes

## Basic Usage

```typescript
import { 
  defaultTagBasedCache, 
  invalidateByTags,
  invalidateOnUpdate,
  invalidateOnCreate,
  invalidateOnDelete
} from 'core/services/cache';

// Store data in cache with tags
defaultTagBasedCache.set(
  'users:list', 
  usersList, 
  ['users', 'collection'],
  60 * 1000 // 1 minute TTL
);

defaultTagBasedCache.set(
  `users:${userId}`, 
  userData, 
  ['users', `users:${userId}`],
  5 * 60 * 1000 // 5 minutes TTL
);

// Retrieve cached data
const cachedUserList = defaultTagBasedCache.get('users:list');
const cachedUser = defaultTagBasedCache.get(`users:${userId}`);

// Invalidate by tags
invalidateByTags(['users:1234']); // Invalidate specific user
invalidateByTags(['users']);      // Invalidate all user-related caches

// Event-based invalidation
invalidateOnCreate('users', newUserId);
invalidateOnUpdate('users', updatedUserId);
invalidateOnDelete('users', deletedUserId);
```

## Advanced Usage

### Custom Tag-Based Cache

```typescript
import { TagBasedCache } from 'core/services/cache';

// Create a custom cache instance
const myCache = new TagBasedCache<UserData>({
  maxItems: 1000,           // Max number of items
  maxSize: 10 * 1024 * 1024, // 10MB max size
  defaultTTL: 30 * 60 * 1000, // 30 minutes default
  debug: true               // Enable debug logging
});

// Use the cache
myCache.set('key', userData, ['user', 'profile']);
myCache.invalidateByTag('user'); // Invalidate by single tag
myCache.invalidateByTags(['user', 'profile']); // Invalidate by multiple tags
myCache.invalidateByPattern(/^user:/); // Invalidate by pattern
```

### Custom Invalidation Strategies

```typescript
import { 
  TagBasedCache, 
  CacheInvalidationStrategies,
  EventDrivenInvalidation 
} from 'core/services/cache';

// Create cache and invalidation instances
const myCache = new TagBasedCache();

const invalidation = new CacheInvalidationStrategies({
  enableTimeBasedInvalidation: true,
  enableTagBasedInvalidation: true,
  enableEventDrivenInvalidation: true,
  defaultTTL: 3600 // 1 hour in seconds
});

// Start monitoring
invalidation.startInvalidationMonitoring(myCache);

// Publish custom invalidation events
invalidation.publishInvalidationEvent(
  'updated',
  'products',
  productId,
  { changedFields: ['price', 'inventory'] }
);

// Clean up when done
invalidation.stopInvalidationMonitoring();
```

### Direct Event System Usage

```typescript
import { EventDrivenInvalidation } from 'core/services/cache';

const events = EventDrivenInvalidation.getInstance();

// Subscribe to specific events
const unsubscribe = events.subscribe('products:updated', (data) => {
  console.log(`Product ${data.entityId} was updated`);
  // Custom invalidation logic here
});

// Custom event publishing
events.publishUpdate('products', productId, { changedFields: ['price'] });
events.publishCreate('orders', orderId);
events.publishDelete('cart-items', itemId);
events.publishBulkOperation('products', 'import', { count: 250 });

// Unsubscribe when done
unsubscribe();
```

## Practical Integration Examples

### With API Service

```typescript
class UserService {
  async getUser(id: string) {
    const cacheKey = `users:${id}`;
    
    // Try to get from cache first
    const cached = defaultTagBasedCache.get(cacheKey);
    if (cached) return cached;
    
    // Fetch from API if not cached
    const userData = await api.get(`/users/${id}`);
    
    // Cache with appropriate tags
    defaultTagBasedCache.set(
      cacheKey,
      userData,
      ['users', `users:${id}`]
    );
    
    return userData;
  }
  
  async updateUser(id: string, data: Partial<User>) {
    // Update in the API
    const updatedUser = await api.put(`/users/${id}`, data);
    
    // Trigger invalidation
    invalidateOnUpdate('users', id, { 
      changedFields: Object.keys(data) 
    });
    
    return updatedUser;
  }
}
```

### With Redux/State Management

```typescript
// In a redux slice or store middleware
const invalidateMiddleware = store => next => action => {
  // Run the action first
  const result = next(action);
  
  // Then handle cache invalidation based on action type
  switch (action.type) {
    case 'users/created':
      invalidateOnCreate('users', action.payload.id);
      break;
    case 'users/updated':
      invalidateOnUpdate('users', action.payload.id, {
        changedFields: action.payload.changedFields
      });
      break;
    case 'users/deleted':
      invalidateOnDelete('users', action.payload.id);
      break;
    case 'users/bulkImport':
      defaultInvalidationSystem.publishInvalidationEvent(
        'bulk',
        'users',
        undefined,
        { count: action.payload.count }
      );
      break;
  }
  
  return result;
};
```

## Best Practices

1. **Use Consistent Tags**: Create a tagging convention and apply it consistently
   - Entity type as base tag: `'users'`
   - Entity instance: `'users:1234'`
   - Collections/queries: `'users:list'`, `'users:active'`

2. **Set Appropriate TTLs**: Different data should have different expiration times
   - Frequently changing data: shorter TTL (seconds to minutes)
   - Relatively stable data: longer TTL (hours)
   - Configuration data: very long TTL (days)

3. **Monitor Cache Performance**: Watch for cache hit rates and memory usage
   - The `stats()` method provides useful metrics

4. **Clean Up Event Listeners**: Always unsubscribe event handlers when components unmount

5. **Handle Race Conditions**: For frequently updated data, use debouncing (already built-in) 