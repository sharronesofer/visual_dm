import { ConversationContextManager } from '../ConversationContextManager';
import { ConversationTurn } from '../types';
import { InMemoryContextStorage } from '../ConversationContextManager';

describe('ConversationContextManager', () => {
    let manager: ConversationContextManager;

    beforeEach(() => {
        manager = new ConversationContextManager({ maxTokens: 8, maxTurns: 3 });
    });

    it('adds and retrieves turns', () => {
        manager.addTurn('user', 'Hello');
        manager.addTurn('npc', 'Hi!');
        expect(manager.getAllTurns().length).toEqual(2);
        expect(manager.getAllTurns()[0].content).toEqual('Hello');
    });

    it('returns context window by tokens', () => {
        manager.addTurn('user', '1234'); // 1 token
        manager.addTurn('npc', '5678'); // 1 token
        manager.addTurn('user', 'abcdefgh'); // 2 tokens
        manager.addTurn('npc', 'ijklmnop'); // 2 tokens
        // maxTokens = 8, so should fit all
        expect(manager.getContext().length).toEqual(4);
        // If we add a long turn, it should trim
        manager.addTurn('user', 'a'.repeat(32)); // 8 tokens
        expect(manager.getContext().length).toEqual(1);
    });

    it('returns context window by turns', () => {
        manager.addTurn('user', 'A');
        manager.addTurn('npc', 'B');
        manager.addTurn('user', 'C');
        manager.addTurn('npc', 'D');
        expect(manager.getContextByTurns().length).toEqual(3);
        expect(manager.getContextByTurns()).toEqual(['B', 'C', 'D']);
    });

    it('clears context', () => {
        manager.addTurn('user', 'X');
        manager.clearContext();
        expect(manager.getAllTurns().length).toEqual(0);
    });

    it('scores recency', () => {
        const now = Date.now();
        const turn: ConversationTurn = { role: 'user', content: 'recent', timestamp: now };
        // With default weights and placeholder semantic/interaction scores, expect 3
        expect(manager.scoreRelevance(turn, now)).toBeCloseTo(3, 1);
        const oldTurn: ConversationTurn = { role: 'user', content: 'old', timestamp: now - 60000 };
        expect(manager.scoreRelevance(oldTurn, now)).toBeLessThan(3);
    });

    it('extracts key information (user turns)', () => {
        manager.addTurn('user', 'U1');
        manager.addTurn('npc', 'N1');
        manager.addTurn('user', 'U2');
        expect(manager.extractKeyInformation()).toEqual(['U1', 'U2']);
    });

    it('saves and loads context using storage backend', async () => {
        const storage = new InMemoryContextStorage();
        manager = new ConversationContextManager({ storageBackend: storage });
        manager.addTurn('user', 'A');
        manager.addTurn('npc', 'B');
        await manager.saveContext();
        manager.clearContext();
        expect(manager.getAllTurns().length).toEqual(0);
        await manager.loadContext();
        expect(manager.getAllTurns().length).toEqual(2);
        expect(manager.getAllTurns()[0].content).toEqual('A');
        expect(manager.getAllTurns()[1].content).toEqual('B');
    });

    it('emits contextUpdated, contextSaved, and contextLoaded events', async () => {
        const storage = new InMemoryContextStorage();
        manager = new ConversationContextManager({ storageBackend: storage });
        const updatedListener = jest.fn();
        const savedListener = jest.fn();
        const loadedListener = jest.fn();
        manager.on('contextUpdated', updatedListener);
        manager.on('contextSaved', savedListener);
        manager.on('contextLoaded', loadedListener);
        manager.addTurn('user', 'A');
        expect(updatedListener).toHaveBeenCalled();
        await manager.saveContext();
        expect(savedListener).toHaveBeenCalled();
        manager.clearContext();
        await manager.loadContext();
        expect(loadedListener).toHaveBeenCalled();
    });
}); 