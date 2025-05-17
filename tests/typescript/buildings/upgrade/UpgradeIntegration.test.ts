import { expect } from 'chai';
import { BuildingUpgradeTransaction as BaseBuildingUpgradeTransaction, UpgradeCommand, ResourceDeductionCommand, BuildingStateChangeCommand, TransactionFailedException } from '../../../../src/buildings/upgrade/BuildingUpgradeTransaction';
import { ResourceManager } from '../../../../src/buildings/upgrade/ResourceManager';
import { TechnologyRequirementChecker } from '../../../../src/buildings/upgrade/TechnologyRequirementChecker';
import { MockInventorySystem as BaseMockInventorySystem } from '../../../../src/buildings/upgrade/integration/InventoryAdapter';
import { MockResearchSystem } from '../../../../src/buildings/upgrade/integration/ResearchAdapter';
import { MockBuildingStructureSystem } from '../../../../src/buildings/upgrade/integration/BuildingStructureAdapter';

// Extend mock classes for test access
class MockInventorySystem extends BaseMockInventorySystem {
    public getPlayerResources(playerId: string) {
        // @ts-ignore
        return { ...(this.playerResources[playerId] || {}) };
    }
}

class BuildingUpgradeTransaction extends BaseBuildingUpgradeTransaction {
    public getState() {
        // @ts-ignore
        return this.state;
    }
    public getLog() {
        // @ts-ignore
        return this.log || [];
    }
    public async run() {
        // @ts-ignore
        return await this.execute();
    }
}

// Helper to delay for stress tests
const delay = (ms: number) => new Promise(res => setTimeout(res, ms));

describe('Upgrade System Integration & Stress Tests', () => {
    let inventory: MockInventorySystem;
    let research: MockResearchSystem;
    let structure: MockBuildingStructureSystem;
    let resourceManager: ResourceManager;
    let techChecker: TechnologyRequirementChecker;
    const playerId = 'player1';
    const buildingId = 'b1';

    beforeEach(() => {
        inventory = new MockInventorySystem();
        research = new MockResearchSystem();
        structure = new MockBuildingStructureSystem();
        resourceManager = new ResourceManager(inventory);
        techChecker = new TechnologyRequirementChecker(research);
        inventory.setPlayerResources(playerId, { wood: 100, stone: 50 });
        research.setPlayerTechs(playerId, ['TechA']);
    });

    it('should complete a full upgrade flow', async () => {
        // Simulate resource deduction, tech check, and building state change
        const cost = { resources: { wood: 50, stone: 20 } };
        const commands: UpgradeCommand[] = [
            new ResourceDeductionCommand(inventory.getPlayerResources(playerId), cost),
            new BuildingStateChangeCommand({ level: 1 }, { level: 2 })
        ];
        const tx = new BuildingUpgradeTransaction(commands);
        await tx.run();
        expect(tx.getState()).to.equal('completed');
        const resources = inventory.getPlayerResources(playerId);
        expect(resources.wood).to.equal(50);
        expect(resources.stone).to.equal(30);
    });

    it('should rollback on resource failure', async () => {
        const cost = { resources: { wood: 200 } };
        const commands: UpgradeCommand[] = [
            new ResourceDeductionCommand(inventory.getPlayerResources(playerId), cost),
            new BuildingStateChangeCommand({ level: 1 }, { level: 2 })
        ];
        const tx = new BuildingUpgradeTransaction(commands);
        try {
            await tx.run();
            throw new Error('Should have failed');
        } catch (err) {
            expect(tx.getState()).to.equal('failed');
            expect(err).to.be.instanceOf(TransactionFailedException);
            // Resources should be unchanged
            const resources = inventory.getPlayerResources(playerId);
            expect(resources.wood).to.equal(100);
        }
    });

    it('should handle concurrent upgrades (stress test)', async function () {
        this.timeout(10000);
        const numConcurrent = 10;
        inventory.setPlayerResources(playerId, { wood: 1000, stone: 1000 });
        const tasks = Array.from({ length: numConcurrent }, (_, i) => {
            const cost = { resources: { wood: 10, stone: 10 } };
            const commands: UpgradeCommand[] = [
                new ResourceDeductionCommand(inventory.getPlayerResources(playerId), cost),
                new BuildingStateChangeCommand({ level: i }, { level: i + 1 })
            ];
            const tx = new BuildingUpgradeTransaction(commands);
            return tx.run();
        });
        await Promise.all(tasks);
        const resources = inventory.getPlayerResources(playerId);
        expect(resources.wood).to.equal(1000 - 10 * numConcurrent);
        expect(resources.stone).to.equal(1000 - 10 * numConcurrent);
    });

    it('should log all transaction steps for audit', async () => {
        const cost = { resources: { wood: 10 } };
        const commands: UpgradeCommand[] = [
            new ResourceDeductionCommand(inventory.getPlayerResources(playerId), cost),
            new BuildingStateChangeCommand({ level: 1 }, { level: 2 })
        ];
        const tx = new BuildingUpgradeTransaction(commands);
        await tx.run();
        expect(tx.getLog()).to.be.an('array').that.is.not.empty;
        expect(tx.getLog().some((l: string) => l.includes('executed'))).to.be.true;
    });

    it('should support plugin extensibility (mock)', async () => {
        // Simulate a plugin upgrade command
        class CustomUpgradeCommand extends UpgradeCommand {
            executed = false;
            async execute() { this.executed = true; }
            async rollback() { this.executed = false; }
        }
        const custom = new CustomUpgradeCommand();
        const tx = new BuildingUpgradeTransaction([custom]);
        await tx.run();
        expect(custom.executed).to.be.true;
        expect(tx.getState()).to.equal('completed');
    });

    it('should measure performance under load', async function () {
        this.timeout(20000);
        inventory.setPlayerResources(playerId, { wood: 10000, stone: 10000 });
        const numOps = 100;
        const start = Date.now();
        const tasks = Array.from({ length: numOps }, (_, i) => {
            const cost = { resources: { wood: 1, stone: 1 } };
            const commands: UpgradeCommand[] = [
                new ResourceDeductionCommand(inventory.getPlayerResources(playerId), cost),
                new BuildingStateChangeCommand({ level: i }, { level: i + 1 })
            ];
            const tx = new BuildingUpgradeTransaction(commands);
            return tx.run();
        });
        await Promise.all(tasks);
        const duration = Date.now() - start;
        expect(duration).to.be.lessThan(5000); // Should complete quickly
    });
}); 