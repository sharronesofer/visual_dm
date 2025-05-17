import { EventBus, EventPriority } from '../events/EventBus';
import { SceneEventType, ISceneEvent } from '../events/SceneEventTypes';
import { InventorySystem } from './InventorySystem';
import { UnifiedApiGateway, InventoryApi } from '../services/UnifiedApiGateway';
import { ItemEvent } from '../events/SceneEventTypes';
import { ValidationService, ValidationContext } from '../services/ValidationService';

export class InventorySystemAdapter implements InventoryApi {
    private inventorySystem: InventorySystem;
    private eventBus: EventBus;
    private apiGateway: UnifiedApiGateway;
    private static instance: InventorySystemAdapter;

    private constructor(inventorySystem: InventorySystem) {
        this.inventorySystem = inventorySystem;
        this.eventBus = EventBus.getInstance();
        this.apiGateway = UnifiedApiGateway.getInstance();
        this.registerEventHandlers();
    }

    public static getInstance(inventorySystem: InventorySystem): InventorySystemAdapter {
        if (!InventorySystemAdapter.instance) {
            InventorySystemAdapter.instance = new InventorySystemAdapter(inventorySystem);
        }
        return InventorySystemAdapter.instance;
    }

    private registerEventHandlers() {
        this.eventBus.on(
            SceneEventType.ITEM_ACQUIRED,
            this.handleItemAcquired.bind(this),
            { priority: EventPriority.NORMAL }
        );
        this.eventBus.on(
            SceneEventType.ITEM_REMOVED,
            this.handleItemRemoved.bind(this),
            { priority: EventPriority.NORMAL }
        );
        this.eventBus.on(
            SceneEventType.ITEM_MODIFIED,
            this.handleItemModified.bind(this),
            { priority: EventPriority.NORMAL }
        );
    }

    private async handleItemAcquired(event: ISceneEvent) {
        // Implement logic to update system state based on item acquired event
    }

    private async handleItemRemoved(event: ISceneEvent) {
        // Implement logic to update system state based on item removed event
    }

    private async handleItemModified(event: ISceneEvent) {
        // Implement logic to update system state based on item modified event
    }

    public async getInventory(agentId: string): Promise<any> {
        if (typeof this.inventorySystem.getInventoryItems === 'function') {
            return await this.inventorySystem.getInventoryItems(agentId);
        }
        throw new Error('getInventoryItems not implemented');
    }

    public async addItem(agentId: string, item: any, quantity: number = 1): Promise<boolean> {
        if (typeof this.inventorySystem.addItemToInventory === 'function') {
            const result = await this.inventorySystem.addItemToInventory(agentId, item.id, quantity);
            if (result.success) {
                const event: ItemEvent = {
                    type: SceneEventType.ITEM_ACQUIRED,
                    itemId: item.id,
                    action: 'acquired',
                    ownerId: agentId,
                    timestamp: Date.now(),
                    details: item,
                    source: 'InventorySystemAdapter',
                };
                await this.eventBus.emit(event);
                return true;
            }
        }
        throw new Error('addItemToInventory not implemented or failed');
    }

    public async removeItem(agentId: string, itemId: string, quantity: number = 1): Promise<boolean> {
        if (typeof this.inventorySystem.removeItemFromInventory === 'function') {
            const result = await this.inventorySystem.removeItemFromInventory(agentId, itemId, quantity);
            if (result.success) {
                const event: ItemEvent = {
                    type: SceneEventType.ITEM_REMOVED,
                    itemId,
                    action: 'removed',
                    ownerId: agentId,
                    timestamp: Date.now(),
                    details: result.removedItem || {},
                    source: 'InventorySystemAdapter',
                };
                await this.eventBus.emit(event);
                return true;
            }
        }
        throw new Error('removeItemFromInventory not implemented or failed');
    }

    public async updateItem(agentId: string, item: any): Promise<boolean> {
        const validationService = ValidationService.getInstance();
        // Pre-operation validation
        const preContext = await validationService.validateAsync('inventory', { agentId, item });
        if (preContext.errors.length > 0) {
            throw new Error('Validation failed before item update: ' + preContext.errors.join('; '));
        }
        // No direct updateItem method; throw error or implement as needed
        throw new Error('updateItem not implemented in InventorySystem');
    }

    // Add more hooks as needed for validation, cross-system updates, etc.
} 