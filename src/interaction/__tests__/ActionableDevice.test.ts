import { ActionableDevice } from '../ActionableDevice';

describe('ActionableDevice', () => {
    it('should return correct id and prompt before activation', () => {
        const device = new ActionableDevice('dev1', 'Control Panel', jest.fn());
        expect(device.getId()).toBe('dev1');
        expect(device.getInteractionPrompt()).toBe('Activate Control Panel');
        expect(device.canInteract('player1')).toBe(true);
    });

    it('should trigger action and mark as activated after interaction', async () => {
        const action = jest.fn();
        const device = new ActionableDevice('dev2', 'Door Switch', action);
        await device.onInteract('player1');
        expect(action).toHaveBeenCalled();
        expect(device.canInteract('player1')).toBe(false);
        expect(device.getInteractionPrompt()).toBe('');
    });

    it('should not trigger action again after activation', async () => {
        const action = jest.fn();
        const device = new ActionableDevice('dev3', 'Alarm', action);
        await device.onInteract('player1');
        await device.onInteract('player1');
        expect(action).toHaveBeenCalledTimes(1);
        expect(device.canInteract('player1')).toBe(false);
    });
}); 