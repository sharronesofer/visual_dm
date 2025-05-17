import { InteractionManager, Actor } from '../InteractionManager';
import { InteractionUI } from '../InteractionUI';
import { Interactable } from '../Interactable';

describe('InteractionUI', () => {
    let manager: InteractionManager;
    let actor: Actor;

    beforeEach(() => {
        manager = new InteractionManager();
        actor = { id: 'player1', position: { x: 0, y: 0, z: 0 } };
    });

    function createMockInteractable(id: string, prompt: string, canInteract = true): Interactable {
        return {
            getId: () => id,
            canInteract: () => canInteract,
            onInteract: jest.fn(),
            getInteractionPrompt: () => prompt,
        };
    }

    it('should return prompts for interactables in range', () => {
        const i1 = createMockInteractable('a', 'Open Door');
        const i2 = createMockInteractable('b', 'Pick up Key', false);
        manager.registerInteractable(i1);
        manager.registerInteractable(i2);
        const ui = new InteractionUI(manager);
        const prompts = ui.getPrompts(actor);
        expect(prompts).toEqual([{ prompt: 'Open Door', interactableId: 'a' }]);
    });

    it('should return highlight data for interactables in range', () => {
        const i1 = createMockInteractable('a', 'Open Door');
        manager.registerInteractable(i1);
        const ui = new InteractionUI(manager, { highlightColor: '#00FF00', icon: 'star' });
        const highlights = ui.getHighlightData(actor);
        expect(highlights).toEqual([{ interactableId: 'a', color: '#00FF00', icon: 'star' }]);
    });

    it('should call feedback callbacks', () => {
        const onSuccess = jest.fn();
        const onFail = jest.fn();
        const onUnavailable = jest.fn();
        const ui = new InteractionUI(manager, { onSuccess, onFail, onUnavailable });
        ui.handleSuccess('Success!');
        ui.handleFail('Fail!');
        ui.handleUnavailable('Unavailable!');
        expect(onSuccess).toHaveBeenCalledWith('Success!');
        expect(onFail).toHaveBeenCalledWith('Fail!');
        expect(onUnavailable).toHaveBeenCalledWith('Unavailable!');
    });
}); 