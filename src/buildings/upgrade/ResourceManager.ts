import { IInventorySystem } from './integration/InventoryAdapter';

export class ResourceManager {
    constructor(private inventory: IInventorySystem) { }

    async canAfford(playerId: string, resources: Record<string, number>): Promise<boolean> {
        return this.inventory.hasResources(playerId, resources);
    }

    async deduct(playerId: string, resources: Record<string, number>): Promise<void> {
        await this.inventory.deductResources(playerId, resources);
    }

    async refund(playerId: string, resources: Record<string, number>): Promise<void> {
        await this.inventory.refundResources(playerId, resources);
    }
} 