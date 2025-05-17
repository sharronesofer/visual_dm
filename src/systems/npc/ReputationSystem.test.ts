import { expect } from 'chai';
import sinon from 'sinon';
import { eventBus } from '../../eventBus/EventBus';
import { PartyIntegrationEventType } from '../../interfaces/PartyIntegrationEvents';
import { reputationSystem, __clearReputationHistoryForTest } from './ReputationSystem';

describe('ReputationSystem Event-Driven Integration', () => {
    beforeEach(() => {
        __clearReputationHistoryForTest();
    });

    it('should call processInteractionReputation and update history on MEMBER_KICKED event', async () => {
        const spy = sinon.spy(reputationSystem, 'processInteractionReputation');
        const npc = { id: 'npc1' } as any;
        const party = { id: 'party1' } as any;
        const result = { success: false, outcome: { effects: { reputation: -0.2 } } } as any;
        eventBus.emit(PartyIntegrationEventType.MEMBER_KICKED, { npc, party, result });
        // Allow event loop to process
        await new Promise(res => setTimeout(res, 10));
        expect(spy.calledOnce).to.be.true;
        expect(spy.firstCall.args[0]).to.equal(npc);
        expect(spy.firstCall.args[1]).to.equal(party.id);
        expect(spy.firstCall.args[2]).to.equal(result);
        // Check reputation history updated
        const history = reputationSystem.getReputationHistory('npc1', 'party1');
        expect(history.length).to.be.greaterThan(0);
        spy.restore();
    });

    it('should call processInteractionReputation and update history on MEMBER_JOINED event', async () => {
        const spy = sinon.spy(reputationSystem, 'processInteractionReputation');
        const npc = { id: 'npc2' } as any;
        const party = { id: 'party2' } as any;
        const result = { success: true, outcome: { effects: { reputation: 0.05 } } } as any;
        eventBus.emit(PartyIntegrationEventType.MEMBER_JOINED, { npc, party, result });
        // Allow event loop to process
        await new Promise(res => setTimeout(res, 10));
        expect(spy.calledOnce).to.be.true;
        expect(spy.firstCall.args[0]).to.equal(npc);
        expect(spy.firstCall.args[1]).to.equal(party.id);
        expect(spy.firstCall.args[2]).to.equal(result);
        // Check reputation history updated
        const history = reputationSystem.getReputationHistory('npc2', 'party2');
        expect(history.length).to.be.greaterThan(0);
        spy.restore();
    });
}); 