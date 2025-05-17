import { EmotionSystem } from './EmotionSystem';
import { EmotionMapper, VisualEmotionMapping, BehavioralEmotionMapping, InternalEmotionMapping, MappingContext } from '../../models/EmotionMapper';
import { BasicEmotion, EmotionDefinition } from '../../models/EmotionDefinition';
import { NPCData } from '../../core/interfaces/types/npc/npc';
import { expect } from 'chai';
import sinon from 'sinon';
import { eventBus } from '../../eventBus/EventBus';
import { PartyIntegrationEventType } from '../../interfaces/PartyIntegrationEvents';

describe('EmotionSystem Integration', () => {
    let system: EmotionSystem;
    let mapper: EmotionMapper;
    let npc: NPCData;
    let context: MappingContext;

    beforeEach(() => {
        mapper = new EmotionMapper();
        system = new EmotionSystem(mapper);
        npc = {
            personality: { traits: new Map([['aggressiveness', 0.5], ['friendliness', 0.2], ['cautiousness', 0.1]]) },
            // ...other NPCData fields as needed
        } as any;
        context = { npc };
    });

    it('maps emotion to visual and back (bidirectional)', () => {
        // Mock visual mapping
        const visualMapping: VisualEmotionMapping = {
            mapToRepresentation: (emotion, ctx) => ({ representation: { face: emotion.name }, confidence: 1 }),
            mapToEmotion: (representation, ctx) => new BasicEmotion(representation.face, 0.5, 0, 0.5, {})
        };
        mapper.registerMapping('visual', visualMapping);
        const joy = new BasicEmotion('joy', 0.8, 1, 0.7, {});
        const visual = system.mapEmotionToVisual(joy, context);
        expect(visual).to.deep.equal({ face: 'joy' });
        const inferred = system.mapVisualToEmotion(visual, context);
        expect(inferred?.name).to.equal('joy');
    });

    it('maps emotion to behavioral and back (bidirectional)', () => {
        const behavioralMapping: BehavioralEmotionMapping = {
            mapToRepresentation: (emotion, ctx) => ({ representation: { gesture: emotion.name }, confidence: 1 }),
            mapToEmotion: (representation, ctx) => new BasicEmotion(representation.gesture, 0.5, 0, 0.5, {})
        };
        mapper.registerMapping('behavioral', behavioralMapping);
        const anger = new BasicEmotion('anger', 0.9, -1, 0.8, {});
        const behavioral = system.mapEmotionToBehavioral(anger, context);
        expect(behavioral).to.deep.equal({ gesture: 'anger' });
        const inferred = system.mapBehavioralToEmotion(behavioral, context);
        expect(inferred?.name).to.equal('anger');
    });

    it('notifies subscribers on mapping change', () => {
        const callback = sinon.spy();
        mapper.subscribe('visual', callback);
        const visualMapping: VisualEmotionMapping = {
            mapToRepresentation: (emotion, ctx) => ({ representation: { face: emotion.name }, confidence: 1 }),
            mapToEmotion: (representation, ctx) => new BasicEmotion(representation.face, 0.5, 0, 0.5, {})
        };
        mapper.registerMapping('visual', visualMapping);
        const joy = new BasicEmotion('joy', 0.8, 1, 0.7, {});
        system.mapEmotionToVisual(joy, context);
        expect(callback.called).to.be.true;
    });

    it('loads and applies mapping configuration', () => {
        const config = { visual: { type: 'blendshape', params: { scale: 1.2 } } };
        system.loadMappingConfig(config);
        expect(mapper.getConfig()).to.deep.equal(config);
    });

    it('handles missing mapping gracefully', () => {
        const joy = new BasicEmotion('joy', 0.8, 1, 0.7, {});
        const visual = system.mapEmotionToVisual(joy, context);
        expect(visual).to.be.null;
    });

    it('handles conflicting updates and rapid state changes', () => {
        // Simulate rapid mapping changes
        const visualMappingA: VisualEmotionMapping = {
            mapToRepresentation: (emotion, ctx) => ({ representation: { face: 'A' }, confidence: 1 }),
            mapToEmotion: (representation, ctx) => new BasicEmotion('A', 0.5, 0, 0.5, {})
        };
        const visualMappingB: VisualEmotionMapping = {
            mapToRepresentation: (emotion, ctx) => ({ representation: { face: 'B' }, confidence: 1 }),
            mapToEmotion: (representation, ctx) => new BasicEmotion('B', 0.5, 0, 0.5, {})
        };
        mapper.registerMapping('visual', visualMappingA);
        const joy = new BasicEmotion('joy', 0.8, 1, 0.7, {});
        expect(system.mapEmotionToVisual(joy, context)).to.deep.equal({ face: 'A' });
        mapper.registerMapping('visual', visualMappingB);
        expect(system.mapEmotionToVisual(joy, context)).to.deep.equal({ face: 'B' });
    });
});

describe('EmotionSystem Event-Driven Integration', () => {
    it('should call calculateEmotionalResponse when PARTY_DISBANDED event is emitted', () => {
        const system = new EmotionSystem();
        const spy = sinon.spy(system, 'calculateEmotionalResponse');
        const npc = { id: 'npc1' } as any;
        const result = { outcome: { effects: { reputation: 0 } } } as any;
        eventBus.emit(PartyIntegrationEventType.PARTY_DISBANDED, { npc, member: {}, result });
        // Allow event loop to process
        setTimeout(() => {
            expect(spy.calledOnce).to.be.true;
            expect(spy.firstCall.args[0]).to.deep.include({ npc, interactionResult: result });
        }, 10);
    });
}); 