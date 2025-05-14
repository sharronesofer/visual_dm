import {
    defaultTagBasedCache,
    invalidateByTags,
    invalidateOnUpdate,
    invalidateOnCreate,
    invalidateOnDelete,
    eventDrivenInvalidation,
    TagBasedCache,
    CacheInvalidationStrategies
} from '../';

/**
 * Example showing basic tag-based caching
 */
function basicTagBasedCacheExample() {
    // Store a user in cache with tags
    const user = { id: '1234', name: 'John Doe', email: 'john@example.com' };
    defaultTagBasedCache.set(
        `user:${user.id}`,
        user,
        ['users', `user:${user.id}`]
    );

    // Store a list of users with different tags
    const userList = [user, { id: '5678', name: 'Jane Doe', email: 'jane@example.com' }];
    defaultTagBasedCache.set(
        'users:list',
        userList,
        ['users', 'collection']
    );

    // Retrieve from cache
    const cachedUser = defaultTagBasedCache.get(`user:${user.id}`);
    console.log('Cached user:', cachedUser);

    const cachedList = defaultTagBasedCache.get('users:list');
    console.log('Cached list:', cachedList);

    // Invalidate a specific user
    console.log('Invalidating user:1234 tag...');
    const invalidatedCount = invalidateByTags([`user:${user.id}`]);
    console.log(`Invalidated ${invalidatedCount} cache entries`);

    // User should be gone, but list remains
    console.log('User after invalidation:', defaultTagBasedCache.get(`user:${user.id}`));
    console.log('List after user invalidation:', defaultTagBasedCache.get('users:list'));

    // Invalidate all user data
    console.log('Invalidating all user data...');
    const allInvalidated = invalidateByTags(['users']);
    console.log(`Invalidated ${allInvalidated} cache entries`);

    // Both should be gone now
    console.log('User after full invalidation:', defaultTagBasedCache.get(`user:${user.id}`));
    console.log('List after full invalidation:', defaultTagBasedCache.get('users:list'));
}

/**
 * Example showing event-driven invalidation
 */
function eventDrivenInvalidationExample() {
    // Create a custom cache with its own invalidation system
    const productCache = new TagBasedCache<any>({
        maxItems: 100,
        debug: true
    });

    const invalidationSystem = new CacheInvalidationStrategies({
        enableTimeBasedInvalidation: true,
        enableTagBasedInvalidation: true,
        enableEventDrivenInvalidation: true,
        debug: true
    });

    // Start monitoring
    invalidationSystem.startInvalidationMonitoring(productCache);

    // Add some products to cache
    productCache.set(
        'product:123',
        { id: '123', name: 'Laptop', price: 999 },
        ['products', 'product:123']
    );

    productCache.set(
        'product:456',
        { id: '456', name: 'Phone', price: 699 },
        ['products', 'product:456']
    );

    productCache.set(
        'products:list',
        [{ id: '123', name: 'Laptop' }, { id: '456', name: 'Phone' }],
        ['products', 'collection']
    );

    // Set up a subscriber to listen for product updates
    const unsubscribe = eventDrivenInvalidation.subscribe('products:updated', (data) => {
        console.log('Product update event received:', data);
        console.log(`Invalidating cache for product ${data.entityId}`);

        // Could do custom invalidation logic here
        productCache.invalidateByTags([`product:${data.entityId}`]);
    });

    // Simulate updating a product 
    console.log('Simulating product update...');
    invalidateOnUpdate('products', '123', { changedFields: ['price'] });

    // The subscription should have triggered and invalidated the cache
    console.log('Product after event:', productCache.get('product:123'));
    console.log('List after event:', productCache.get('products:list'));

    // Clean up
    unsubscribe();
    invalidationSystem.stopInvalidationMonitoring();
}

/**
 * Run the examples
 */
function runExamples() {
    console.log('=== Basic Tag-Based Cache Example ===');
    basicTagBasedCacheExample();

    console.log('\n=== Event-Driven Invalidation Example ===');
    eventDrivenInvalidationExample();
}

// Only run if this file is executed directly
if (require.main === module) {
    runExamples();
}

export { basicTagBasedCacheExample, eventDrivenInvalidationExample, runExamples }; 