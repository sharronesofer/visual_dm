import { InteractionManager } from '../InteractionManager';
import { Interactable } from '../Interactable';

describe('InteractionManager', () => {
    let manager: InteractionManager;
    let actor: { id: string; position: { x: number; y: number; z: number } };

    beforeEach(() => {
        manager = new InteractionManager();
        actor = { id: 'player1', position: { x: 0, y: 0, z: 0 } };
    });

    function createMockInteractable(id: string, canInteract = true, prompt = 'Interact?'): Interactable {
        return {
            getId: () => id,
            canInteract: () => canInteract,
            onInteract: jest.fn(),
            getInteractionPrompt: () => prompt,
        };
    }

    it('registers and retrieves interactables', () => {
        const interactable = createMockInteractable('test1');
        manager.registerInteractable(interactable);
        expect(manager.getInteractablesInRange(actor)).toContain(interactable);
    });

    it('deregisters interactables', () => {
        const interactable = createMockInteractable('test2');
        manager.registerInteractable(interactable);
        manager.deregisterInteractable(interactable);
        expect(manager.getInteractablesInRange(actor)).not.toContain(interactable);
    });

    it('returns only interactables that can be interacted with', () => {
        const interactable1 = createMockInteractable('a', true);
        const interactable2 = createMockInteractable('b', false);
        manager.registerInteractable(interactable1);
        manager.registerInteractable(interactable2);
        const prompts = manager.getAvailableInteractionPrompts(actor);
        expect(prompts).toContain('Interact?');
        expect(prompts).toHaveLength(1);
    });

    it('triggers onInteract for the first available interactable', () => {
        const interactable = createMockInteractable('c', true);
        manager.registerInteractable(interactable);
        manager.handleInteractionInput(actor);
        expect((interactable.onInteract as jest.Mock).mock.calls.length).toBe(1);
    });

    it('does not trigger onInteract if no interactables are available', () => {
        const interactable = createMockInteractable('d', false);
        manager.registerInteractable(interactable);
        manager.handleInteractionInput(actor);
        expect((interactable.onInteract as jest.Mock).mock.calls.length).toBe(0);
    });
}); 