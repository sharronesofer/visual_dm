export interface IInventorySystem {
    hasResources(playerId: string, resources: Record<string, number>): Promise<boolean>;
    deductResources(playerId: string, resources: Record<string, number>): Promise<void>;
    refundResources(playerId: string, resources: Record<string, number>): Promise<void>;
}

export class MockInventorySystem implements IInventorySystem {
    private playerResources: Record<string, Record<string, number>> = {};

    setPlayerResources(playerId: string, resources: Record<string, number>) {
        this.playerResources[playerId] = { ...resources };
    }

    async hasResources(playerId: string, resources: Record<string, number>): Promise<boolean> {
        const player = this.playerResources[playerId] || {};
        return Object.entries(resources).every(([res, amt]) => (player[res] || 0) >= amt);
    }

    async deductResources(playerId: string, resources: Record<string, number>): Promise<void> {
        if (!(await this.hasResources(playerId, resources))) throw new Error('Insufficient resources');
        for (const [res, amt] of Object.entries(resources)) {
            this.playerResources[playerId][res] -= amt;
        }
    }

    async refundResources(playerId: string, resources: Record<string, number>): Promise<void> {
        for (const [res, amt] of Object.entries(resources)) {
            this.playerResources[playerId][res] = (this.playerResources[playerId][res] || 0) + amt;
        }
    }
} 