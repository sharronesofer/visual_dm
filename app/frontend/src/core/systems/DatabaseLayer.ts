/**
 * DatabaseLayer.ts
 * 
 * Provides a unified interface for data persistence across all backend systems.
 * Implements CRUD operations with caching, indexing, and query capabilities.
 */

import { BaseEntity, updateEntityTimestamp } from './DataModels';

// Type for record collections
export type Collection<T> = Map<string, T>;

/**
 * In-memory database implementation for development and testing
 * This can be replaced with a real database adapter in production
 */
export class DatabaseAdapter {
    private collections: Map<string, Collection<any>>;
    private indexedFields: Map<string, Set<string>>;
    private indices: Map<string, Map<string, Set<string>>>;
    private cacheEnabled: boolean;
    private cacheSize: number;
    private cacheHits: number;
    private cacheMisses: number;

    constructor(options: { cacheEnabled?: boolean, cacheSize?: number } = {}) {
        this.collections = new Map();
        this.indexedFields = new Map();
        this.indices = new Map();
        this.cacheEnabled = options.cacheEnabled ?? true;
        this.cacheSize = options.cacheSize ?? 10000;
        this.cacheHits = 0;
        this.cacheMisses = 0;
    }

    /**
     * Initialize a collection
     */
    public initCollection<T extends BaseEntity>(collectionName: string, indexedFields: string[] = []): Collection<T> {
        if (!this.collections.has(collectionName)) {
            this.collections.set(collectionName, new Map<string, T>());
            this.indexedFields.set(collectionName, new Set(indexedFields));
            this.indices.set(collectionName, new Map());

            // Initialize indices for each indexed field
            indexedFields.forEach(field => {
                if (!this.indices.get(collectionName)?.has(field)) {
                    this.indices.get(collectionName)?.set(field, new Map());
                }
            });
        }

        return this.collections.get(collectionName) as Collection<T>;
    }

    /**
     * Create a new record in a collection
     */
    public async create<T extends BaseEntity>(collectionName: string, data: T): Promise<T> {
        const collection = this.getOrCreateCollection<T>(collectionName);
        collection.set(data.id, data);

        // Update indices
        this.updateIndices(collectionName, data);

        return data;
    }

    /**
     * Create multiple records in a collection
     */
    public async createMany<T extends BaseEntity>(collectionName: string, dataArray: T[]): Promise<T[]> {
        const collection = this.getOrCreateCollection<T>(collectionName);

        for (const data of dataArray) {
            collection.set(data.id, data);
            this.updateIndices(collectionName, data);
        }

        return dataArray;
    }

    /**
     * Read a record by ID
     */
    public async read<T extends BaseEntity>(collectionName: string, id: string): Promise<T | null> {
        const collection = this.getCollection<T>(collectionName);
        if (!collection) return null;

        if (this.cacheEnabled) {
            this.cacheHits++; // Simplified cache hit counting
        } else {
            this.cacheMisses++;
        }

        return collection.get(id) || null;
    }

    /**
     * Read multiple records by IDs
     */
    public async readMany<T extends BaseEntity>(collectionName: string, ids: string[]): Promise<T[]> {
        const collection = this.getCollection<T>(collectionName);
        if (!collection) return [];

        return ids
            .map(id => collection.get(id))
            .filter((item): item is T => item !== undefined);
    }

    /**
     * Update a record
     */
    public async update<T extends BaseEntity>(collectionName: string, id: string, data: Partial<T>): Promise<T | null> {
        const collection = this.getCollection<T>(collectionName);
        if (!collection) return null;

        const existingData = collection.get(id);
        if (!existingData) return null;

        // Remove existing indices
        this.removeIndices(collectionName, existingData);

        // Update the data
        const updatedData = {
            ...existingData,
            ...data,
            id, // Ensure ID is not changed
            updatedAt: Date.now() // Update timestamp
        } as T;

        collection.set(id, updatedData);

        // Update indices with new data
        this.updateIndices(collectionName, updatedData);

        return updatedData;
    }

    /**
     * Delete a record by ID
     */
    public async delete<T extends BaseEntity>(collectionName: string, id: string): Promise<boolean> {
        const collection = this.getCollection<T>(collectionName);
        if (!collection) return false;

        const existingData = collection.get(id);
        if (!existingData) return false;

        // Remove indices
        this.removeIndices(collectionName, existingData);

        // Remove the record
        return collection.delete(id);
    }

    /**
     * Find records by a field value
     */
    public async findByField<T extends BaseEntity>(
        collectionName: string,
        field: string,
        value: any
    ): Promise<T[]> {
        const collection = this.getCollection<T>(collectionName);
        if (!collection) return [];

        // Check if field is indexed
        if (this.isFieldIndexed(collectionName, field)) {
            // Use index for lookup
            const fieldIndex = this.indices.get(collectionName)?.get(field);
            const recordIds = fieldIndex?.get(this.getIndexKey(value));

            if (recordIds && recordIds.size > 0) {
                return Array.from(recordIds)
                    .map(id => collection.get(id))
                    .filter((item): item is T => item !== undefined);
            }

            return [];
        }

        // Fallback to full scan
        return Array.from(collection.values()).filter(item => {
            const itemField = this.getNestedProperty(item, field);
            return this.compareValues(itemField, value);
        });
    }

    /**
     * Find records by query
     */
    public async query<T extends BaseEntity>(
        collectionName: string,
        queryFn: (item: T) => boolean,
        limit?: number
    ): Promise<T[]> {
        const collection = this.getCollection<T>(collectionName);
        if (!collection) return [];

        let results = Array.from(collection.values()).filter(queryFn);

        if (limit !== undefined) {
            results = results.slice(0, limit);
        }

        return results;
    }

    /**
     * Get all records in a collection
     */
    public async getAll<T extends BaseEntity>(collectionName: string): Promise<T[]> {
        const collection = this.getCollection<T>(collectionName);
        if (!collection) return [];

        return Array.from(collection.values());
    }

    /**
     * Count records in a collection
     */
    public async count(collectionName: string): Promise<number> {
        const collection = this.getCollection(collectionName);
        if (!collection) return 0;

        return collection.size;
    }

    /**
     * Clear a collection
     */
    public async clearCollection(collectionName: string): Promise<void> {
        const collection = this.getCollection(collectionName);
        if (!collection) return;

        collection.clear();

        // Clear indices
        const collectionIndices = this.indices.get(collectionName);
        if (collectionIndices) {
            collectionIndices.forEach(index => {
                index.clear();
            });
        }
    }

    /**
     * Drop a collection (remove it entirely)
     */
    public async dropCollection(collectionName: string): Promise<void> {
        this.collections.delete(collectionName);
        this.indexedFields.delete(collectionName);
        this.indices.delete(collectionName);
    }

    /**
     * Get cache statistics
     */
    public getCacheStats(): { hits: number, misses: number, ratio: number } {
        const total = this.cacheHits + this.cacheMisses;
        const ratio = total > 0 ? this.cacheHits / total : 0;
        return {
            hits: this.cacheHits,
            misses: this.cacheMisses,
            ratio
        };
    }

    /**
     * Reset cache statistics
     */
    public resetCacheStats(): void {
        this.cacheHits = 0;
        this.cacheMisses = 0;
    }

    // Helper methods

    private getOrCreateCollection<T extends BaseEntity>(collectionName: string): Collection<T> {
        if (!this.collections.has(collectionName)) {
            return this.initCollection<T>(collectionName);
        }
        return this.collections.get(collectionName) as Collection<T>;
    }

    private getCollection<T extends BaseEntity>(collectionName: string): Collection<T> | undefined {
        return this.collections.get(collectionName) as Collection<T> | undefined;
    }

    private isFieldIndexed(collectionName: string, field: string): boolean {
        return this.indexedFields.get(collectionName)?.has(field) || false;
    }

    private updateIndices<T extends BaseEntity>(collectionName: string, data: T): void {
        const indexedFields = this.indexedFields.get(collectionName);
        if (!indexedFields) return;

        indexedFields.forEach(field => {
            const fieldValue = this.getNestedProperty(data, field);
            if (fieldValue !== undefined) {
                const indexKey = this.getIndexKey(fieldValue);
                const fieldIndex = this.indices.get(collectionName)?.get(field);

                if (fieldIndex) {
                    if (!fieldIndex.has(indexKey)) {
                        fieldIndex.set(indexKey, new Set());
                    }
                    fieldIndex.get(indexKey)?.add(data.id);
                }
            }
        });
    }

    private removeIndices<T extends BaseEntity>(collectionName: string, data: T): void {
        const indexedFields = this.indexedFields.get(collectionName);
        if (!indexedFields) return;

        indexedFields.forEach(field => {
            const fieldValue = this.getNestedProperty(data, field);
            if (fieldValue !== undefined) {
                const indexKey = this.getIndexKey(fieldValue);
                const fieldIndex = this.indices.get(collectionName)?.get(field);

                if (fieldIndex && fieldIndex.has(indexKey)) {
                    fieldIndex.get(indexKey)?.delete(data.id);
                }
            }
        });
    }

    private getIndexKey(value: any): string {
        if (value === null) return 'null';
        if (value === undefined) return 'undefined';

        switch (typeof value) {
            case 'string':
                return value;
            case 'number':
            case 'boolean':
                return value.toString();
            case 'object':
                if (Array.isArray(value)) {
                    return `arr:${value.map(v => this.getIndexKey(v)).join(',')}`;
                }
                return `obj:${JSON.stringify(value)}`;
            default:
                return `${typeof value}:${String(value)}`;
        }
    }

    private getNestedProperty(obj: any, path: string): any {
        const parts = path.split('.');
        let current = obj;

        for (const part of parts) {
            if (current === null || current === undefined) {
                return undefined;
            }
            current = current[part];
        }

        return current;
    }

    private compareValues(a: any, b: any): boolean {
        if (a === b) return true;

        if (a === null || a === undefined || b === null || b === undefined) {
            return false;
        }

        if (typeof a === 'object' && typeof b === 'object') {
            return JSON.stringify(a) === JSON.stringify(b);
        }

        return false;
    }
}

/**
 * Repository base class for entity operations
 * Provides a higher-level API for system components
 */
export class Repository<T extends BaseEntity> {
    protected db: DatabaseAdapter;
    protected collectionName: string;
    protected indexedFields: string[];

    constructor(
        db: DatabaseAdapter,
        collectionName: string,
        indexedFields: string[] = []
    ) {
        this.db = db;
        this.collectionName = collectionName;
        this.indexedFields = indexedFields;

        // Initialize collection
        this.db.initCollection<T>(collectionName, indexedFields);
    }

    public async create(data: Omit<T, 'id' | 'createdAt' | 'updatedAt'>): Promise<T> {
        const now = Date.now();
        const entity = {
            ...data,
            id: this.generateId(),
            createdAt: now,
            updatedAt: now
        } as T;

        return this.db.create(this.collectionName, entity);
    }

    public async findById(id: string): Promise<T | null> {
        return this.db.read<T>(this.collectionName, id);
    }

    public async findByIds(ids: string[]): Promise<T[]> {
        return this.db.readMany<T>(this.collectionName, ids);
    }

    public async findAll(): Promise<T[]> {
        return this.db.getAll<T>(this.collectionName);
    }

    public async findBy(field: string, value: any): Promise<T[]> {
        return this.db.findByField<T>(this.collectionName, field, value);
    }

    public async update(id: string, data: Partial<T>): Promise<T | null> {
        return this.db.update<T>(this.collectionName, id, data);
    }

    public async delete(id: string): Promise<boolean> {
        return this.db.delete<T>(this.collectionName, id);
    }

    public async query(queryFn: (item: T) => boolean, limit?: number): Promise<T[]> {
        return this.db.query<T>(this.collectionName, queryFn, limit);
    }

    public async count(): Promise<number> {
        return this.db.count(this.collectionName);
    }

    protected generateId(): string {
        return `${this.collectionName}_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    }
}

/**
 * Factory function to create a Repository for a specific entity type
 */
export function createRepository<T extends BaseEntity>(
    db: DatabaseAdapter,
    collectionName: string,
    indexedFields: string[] = []
): Repository<T> {
    return new Repository<T>(db, collectionName, indexedFields);
}

/**
 * Global database instance for systems to use
 */
export const globalDatabase = new DatabaseAdapter(); 