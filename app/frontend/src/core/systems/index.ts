/**
 * Core Backend Systems Index
 * 
 * This file exports all the backend system components for easier imports.
 */

// Core Data Models & Types
export * from './DataModels';

// Base System Functionality
export * from './BaseSystemManager';
export * from './DatabaseLayer';

// Individual Systems
export * from './MemorySystem';
export * from './RelationshipSystem';
export * from './InventorySystem';
export * from './EconomySystem';
export * from './WorldSystem';
export * from './NavigationSystem';
export * from './MotifSystem';
export * from './NarrativeSystem';
export * from './QuestSystem';

// Initialize the system registry
import { systemRegistry } from './BaseSystemManager';
export { systemRegistry };

/**
 * Initialize all backend systems
 * This function should be called at application startup
 */
export async function initializeBackendSystems(debug: boolean = false): Promise<void> {
    try {
        // Initialize the memory system
        import('./MemorySystem').then(({ MemorySystem }) => {
            const memorySystem = new MemorySystem({
                name: 'MemorySystem',
                debug,
                autoInitialize: true
            });
            systemRegistry.registerSystem(memorySystem);
        });

        // Initialize the relationship system
        import('./RelationshipSystem').then(({ RelationshipSystem }) => {
            const relationshipSystem = new RelationshipSystem({
                name: 'RelationshipSystem',
                debug,
                autoInitialize: true
            });
            systemRegistry.registerSystem(relationshipSystem);
        });

        // Initialize the inventory system
        import('./InventorySystem').then(({ InventorySystem }) => {
            const inventorySystem = new InventorySystem({
                name: 'InventorySystem',
                debug,
                autoInitialize: true
            });
            systemRegistry.registerSystem(inventorySystem);
        });

        // Initialize the economy system
        import('./EconomySystem').then(({ EconomySystem }) => {
            const economySystem = new EconomySystem({
                name: 'EconomySystem',
                debug,
                autoInitialize: true
            });
            systemRegistry.registerSystem(economySystem);
        });

        // Initialize the world system
        import('./WorldSystem').then(({ WorldSystem }) => {
            const worldSystem = new WorldSystem({
                name: 'WorldSystem',
                debug,
                autoInitialize: true
            });
            systemRegistry.registerSystem(worldSystem);
        });

        // Initialize the navigation system (depends on WorldSystem)
        import('./NavigationSystem').then(({ NavigationSystem }) => {
            const navigationSystem = new NavigationSystem({
                name: 'NavigationSystem',
                debug,
                autoInitialize: true
            });
            systemRegistry.registerSystem(navigationSystem);
        });

        // Initialize the motif system
        import('./MotifSystem').then(({ MotifSystem }) => {
            const motifSystem = new MotifSystem({
                name: 'MotifSystem',
                debug,
                autoInitialize: true
            });
            systemRegistry.registerSystem(motifSystem);
        });

        // Initialize the narrative system (depends on MotifSystem)
        import('./NarrativeSystem').then(({ NarrativeSystem }) => {
            const narrativeSystem = new NarrativeSystem({
                name: 'NarrativeSystem',
                debug,
                autoInitialize: true
            });
            systemRegistry.registerSystem(narrativeSystem);
        });

        // Initialize the quest system (depends on MotifSystem and NarrativeSystem)
        import('./QuestSystem').then(({ QuestSystem }) => {
            const questSystem = new QuestSystem({
                name: 'QuestSystem',
                debug,
                autoInitialize: true
            });
            systemRegistry.registerSystem(questSystem);
        });

        console.log('All backend systems initialized successfully');
    } catch (error) {
        console.error('Failed to initialize backend systems:', error);
        throw error;
    }
} 