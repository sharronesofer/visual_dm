import { expect } from 'chai';
import sinon from 'sinon';
import { eventBus } from '../../eventBus/EventBus';
import { PartyIntegrationEventType } from '../../interfaces/PartyIntegrationEvents';
import { InteractionSystem } from './InteractionSystem';

describe('InteractionSystem Morale/Loyalty Event-Driven Integration', () => {
    let system: InteractionSystem;
    beforeEach(() => {
        // Provide stubs for required dependencies
        system = new InteractionSystem({} as any, {} as any, {} as any, {} as any, {} as any, {} as any, {} as any, {} as any);
        // @ts-ignore: access private fields for test
        system.npcMorale.clear();
        // @ts-ignore
        system.npcLoyalty.clear();
    });

    it('should update morale for all members on PARTY_DISBANDED', () => {
        // @ts-ignore: stub getPartyMemberIds
        sinon.stub(system, 'getPartyMemberIds').returns(['npc1', 'npc2']);
        // @ts-ignore
        system.npcMorale.set('npc1', 60);
        // @ts-ignore
        system.npcMorale.set('npc2', 40);
        eventBus.emit(PartyIntegrationEventType.PARTY_DISBANDED, { partyId: 'party1' });
        // @ts-ignore
        expect(system.npcMorale.get('npc1')).to.equal(40);
        // @ts-ignore
        expect(system.npcMorale.get('npc2')).to.equal(20);
    });

    it('should update morale and loyalty for member on MEMBER_JOINED', () => {
        // @ts-ignore
        system.npcMorale.set('npc3', 80);
        // @ts-ignore
        system.npcLoyalty.set('npc3', 70);
        eventBus.emit(PartyIntegrationEventType.MEMBER_JOINED, { partyId: 'party2', memberId: 'npc3' });
        // @ts-ignore
        expect(system.npcMorale.get('npc3')).to.equal(90);
        // @ts-ignore
        expect(system.npcLoyalty.get('npc3')).to.equal(75);
    });

    it('should update morale and loyalty for member on MEMBER_KICKED', () => {
        // @ts-ignore
        system.npcMorale.set('npc4', 30);
        // @ts-ignore
        system.npcLoyalty.set('npc4', 20);
        eventBus.emit(PartyIntegrationEventType.MEMBER_KICKED, { partyId: 'party3', memberId: 'npc4' });
        // @ts-ignore
        expect(system.npcMorale.get('npc4')).to.equal(0);
        // @ts-ignore
        expect(system.npcLoyalty.get('npc4')).to.equal(5);
    });
}); 