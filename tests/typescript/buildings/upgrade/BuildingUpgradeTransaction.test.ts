import { expect } from 'chai';
import {
    BuildingUpgradeTransaction,
    UpgradeCommand,
    ResourceDeductionCommand,
    BuildingStateChangeCommand,
    TransactionFailedException
} from '../../../../src/buildings/upgrade/BuildingUpgradeTransaction';

describe('BuildingUpgradeTransaction', () => {
    it('should complete a successful transaction', async () => {
        const playerResources = { wood: 100 };
        const cost = { resources: { wood: 50 } };
        const building = { level: 1 };
        const newState = { level: 2 };
        const commands: UpgradeCommand[] = [
            new ResourceDeductionCommand(playerResources, cost),
            new BuildingStateChangeCommand(building, newState)
        ];
        const tx = new BuildingUpgradeTransaction(commands);
        await tx.start();
        expect(tx.getState()).to.equal('completed');
        expect(playerResources.wood).to.equal(50);
        expect(building.level).to.equal(2);
        const logs = tx.getLogs();
        expect(logs.some(l => l.event === 'transaction_completed')).to.be.true;
    });

    it('should rollback if a command fails', async () => {
        const playerResources = { wood: 10 };
        const cost = { resources: { wood: 50 } };
        const building = { level: 1 };
        const newState = { level: 2 };
        const commands: UpgradeCommand[] = [
            new ResourceDeductionCommand(playerResources, cost),
            new BuildingStateChangeCommand(building, newState)
        ];
        const tx = new BuildingUpgradeTransaction(commands);
        try {
            await tx.start();
            expect.fail('Transaction should have failed');
        } catch (err) {
            expect(err).to.be.instanceOf(TransactionFailedException);
            expect(tx.getState()).to.equal('failed');
            expect(playerResources.wood).to.equal(10); // rolled back
            expect(building.level).to.equal(1); // not changed
            const logs = tx.getLogs();
            expect(logs.some(l => l.event === 'transaction_failed')).to.be.true;
            expect(logs.some(l => l.event === 'command_rolled_back')).to.be.true;
        }
    });

    it('should save checkpoints after each command', async () => {
        const playerResources = { wood: 100 };
        const cost = { resources: { wood: 10 } };
        const building = { level: 1 };
        const newState = { level: 2 };
        const commands: UpgradeCommand[] = [
            new ResourceDeductionCommand(playerResources, cost),
            new BuildingStateChangeCommand(building, newState)
        ];
        const tx = new BuildingUpgradeTransaction(commands);
        await tx.start();
        const checkpoint = tx.getCheckpoint();
        expect(checkpoint).to.have.property('executed', 2);
    });

    it('should log all transaction steps', async () => {
        const playerResources = { wood: 100 };
        const cost = { resources: { wood: 10 } };
        const building = { level: 1 };
        const newState = { level: 2 };
        const commands: UpgradeCommand[] = [
            new ResourceDeductionCommand(playerResources, cost),
            new BuildingStateChangeCommand(building, newState)
        ];
        const tx = new BuildingUpgradeTransaction(commands);
        await tx.start();
        const logs = tx.getLogs();
        expect(logs.find(l => l.event === 'transaction_start')).to.exist;
        expect(logs.find(l => l.event === 'command_executed')).to.exist;
        expect(logs.find(l => l.event === 'checkpoint_saved')).to.exist;
        expect(logs.find(l => l.event === 'transaction_completed')).to.exist;
    });
}); 