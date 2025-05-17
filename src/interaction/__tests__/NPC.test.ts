import { NPC } from '../NPC';

describe('NPC', () => {
    it('should return correct id and prompt before interaction', () => {
        const npc = new NPC('npc1', 'Bob', 'Hello there!', jest.fn());
        expect(npc.getId()).toEqual('npc1');
        expect(npc.getInteractionPrompt()).toEqual('Talk to Bob');
        expect(npc.canInteract('player1')).toEqual(true);
    });

    it('should trigger dialogue and mark as interacted after interaction', async () => {
        const onDialogue = jest.fn();
        const npc = new NPC('npc2', 'Alice', 'Welcome!', onDialogue);
        await npc.onInteract('player1');
        expect(onDialogue).toHaveBeenCalledWith('player1');
        expect(npc.canInteract('player1')).toEqual(false);
        expect(npc.getInteractionPrompt()).toEqual('');
    });

    it('should not trigger dialogue again after interaction', async () => {
        const onDialogue = jest.fn();
        const npc = new NPC('npc3', 'Eve', 'Goodbye!', onDialogue);
        await npc.onInteract('player1');
        await npc.onInteract('player1');
        expect(onDialogue).toHaveBeenCalledTimes(1);
        expect(npc.canInteract('player1')).toEqual(false);
    });
}); 