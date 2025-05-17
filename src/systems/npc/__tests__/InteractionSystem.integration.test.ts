import { InteractionSystem, InteractionType, InteractionContext } from '../InteractionSystem';
import { DialogueManager } from '../DialogueManager';
import { DialogueGenerationService } from '../../../dialogue/DialogueGenerationService';
import { ConversationContextManager } from '../../../dialogue/ConversationContextManager';
import { ResponseCacheManager } from '../../../dialogue/ResponseCacheManager';
import { GPTClient, GPTConfig } from '../../../dialogue/GPTClient';
import assert from 'assert';
import { vi, describe, it, beforeEach } from 'vitest';
import { DialogueConfigurationManager } from '../../../dialogue/config/DialogueConfigurationManager';

// Mocks for dependencies
const mockEmotionSystem = { calculateEmotionalResponse: vi.fn().mockResolvedValue({ primary: 'happy', secondary: 'calm' }) };
const mockReputationSystem = {};
const mockMemoryManager = { queryMemories: vi.fn().mockResolvedValue([]), addMemory: vi.fn() };
const mockGroupSystem = {};
const mockEconomicSystem = {};

vi.mock('../../../core/services/NPCEventLoggingService', () => {
    const mockLoggingService = { logInteraction: vi.fn(), getInstance: () => mockLoggingService };
    return { NPCEventLoggingService: mockLoggingService };
});

// Mock GPTClient to return a fixed response
class MockGPTClient {
    async generateCompletion() {
        return { text: 'Mentoring advice: Always be curious.' };
    }
}

describe('InteractionSystem Integration', () => {
    let interactionSystem: InteractionSystem;
    let dialogueManager: DialogueManager;
    let contextManager: ConversationContextManager;
    let cacheManager: ResponseCacheManager;

    beforeEach(() => {
        contextManager = new ConversationContextManager({ maxTokens: 100, maxTurns: 10 });
        cacheManager = new ResponseCacheManager({ maxSize: 10, expiryMs: 10000 });
        const gptClient = new MockGPTClient() as any as GPTClient;
        const dialogueService = new DialogueGenerationService(gptClient, { model: 'gpt-test' });
        const configManager = new DialogueConfigurationManager({ model: 'gpt-test' });
        dialogueManager = new DialogueManager(
            mockEmotionSystem as any,
            mockMemoryManager as any,
            dialogueService,
            contextManager,
            cacheManager,
            configManager
        );
        const groupSystem = {} as any;
        const economicSystem = {} as any;
        interactionSystem = new InteractionSystem(
            dialogueManager,
            mockEmotionSystem as any,
            mockReputationSystem as any,
            mockMemoryManager as any,
            groupSystem,
            economicSystem,
            configManager,
            contextManager,
            vi.fn()
        );
        // Patch dispatch with a mock for test environment
        (interactionSystem as any).dispatch = vi.fn();
    });

    it('generates GPT-driven dialogue and updates context/cache', async () => {
        const mentor = {
            id: 'npc1',
            name: 'MentorNPC',
            stats: { intelligence: 1, wisdom: 1, charisma: 1 },
            personality: { traits: new Map([['empathy', 1]]) }
        };
        const student = {
            id: 'npc2',
            name: 'StudentNPC',
            stats: { intelligence: 1, wisdom: 1, charisma: 1 },
            personality: { traits: new Map() }
        };
        const context: InteractionContext = {
            npcId: mentor.id,
            targetId: student.id,
            type: InteractionType.MENTORING
        };

        // First call: should generate via GPT
        const result1 = await interactionSystem.processInteraction(mentor as any, student as any, context);
        assert.ok(result1.outcome.description.includes('Mentoring advice:'));
        // Context should be updated
        assert.ok(contextManager.getAllTurns().length > 0);
        // Cache should have the entry (analytics: hits + misses > 0)
        if (typeof (cacheManager as any).getAnalytics === 'function') {
            const analytics = (cacheManager as any).getAnalytics();
            assert.ok((analytics.hits + analytics.misses) > 0);
        }
        // Check lastDialogue payload for GPT/caching metadata
        const lastDialogue1 = (interactionSystem as any).dispatch.mock.calls[0][0].payload.lastDialogue;
        assert.strictEqual(lastDialogue1.cacheStatus, 'miss');
        assert.ok(lastDialogue1.gptMetadata);
        assert.strictEqual(typeof lastDialogue1.gptMetadata.tokensUsed, 'number');
        assert.strictEqual(typeof lastDialogue1.gptMetadata.model, 'string');
        assert.ok(Array.isArray(lastDialogue1.contextSnapshot));
        assert.ok(lastDialogue1.cacheAnalytics);
        assert.strictEqual(typeof lastDialogue1.cacheAnalytics.hits, 'number');
        assert.strictEqual(typeof lastDialogue1.cacheAnalytics.misses, 'number');
        // Second call: should hit cache (simulate same prompt/context)
        contextManager.clearContext();
        const result2 = await interactionSystem.processInteraction(mentor as any, student as any, context);
        assert.ok(result2.outcome.description.includes('Mentoring advice:'));
        if (typeof (cacheManager as any).getAnalytics === 'function') {
            const analytics = (cacheManager as any).getAnalytics();
            assert.ok(analytics.hits > 0);
        }
        // Check lastDialogue payload for cache hit
        const lastDialogue2 = (interactionSystem as any).dispatch.mock.calls[1][0].payload.lastDialogue;
        assert.strictEqual(lastDialogue2.cacheStatus, 'hit');
        assert.ok(Array.isArray(lastDialogue2.contextSnapshot));
        assert.ok(lastDialogue2.cacheAnalytics);
        assert.strictEqual(typeof lastDialogue2.cacheAnalytics.hits, 'number');
        assert.strictEqual(typeof lastDialogue2.cacheAnalytics.misses, 'number');
    });
}); 