import { expect } from 'chai';
import { ResourceManager } from '../../../../../src/buildings/upgrade/ResourceManager';
import { MockInventorySystem } from '../../../../../src/buildings/upgrade/integration/InventoryAdapter';

describe('ResourceManager Integration', () => {
    let inventory: MockInventorySystem;
    let manager: ResourceManager;
    const playerId = 'player1';

    beforeEach(() => {
        inventory = new MockInventorySystem();
        manager = new ResourceManager(inventory);
        inventory.setPlayerResources(playerId, { wood: 100, stone: 50 });
    });

    it('should check if player can afford resources', async () => {
        expect(await manager.canAfford(playerId, { wood: 50 })).to.be.true;
        expect(await manager.canAfford(playerId, { wood: 200 })).to.be.false;
    });

    it('should deduct resources from player', async () => {
        await manager.deduct(playerId, { wood: 30, stone: 10 });
        expect(await manager.canAfford(playerId, { wood: 70, stone: 40 })).to.be.true;
        expect(await manager.canAfford(playerId, { wood: 71 })).to.be.false;
    });

    it('should refund resources to player', async () => {
        await manager.deduct(playerId, { wood: 20 });
        await manager.refund(playerId, { wood: 10 });
        expect(await manager.canAfford(playerId, { wood: 91 })).to.be.true;
    });

    it('should throw on insufficient resources', async () => {
        try {
            await manager.deduct(playerId, { wood: 200 });
            expect.fail('Should have thrown');
        } catch (err) {
            expect(err.message).to.include('Insufficient resources');
        }
    });
}); 