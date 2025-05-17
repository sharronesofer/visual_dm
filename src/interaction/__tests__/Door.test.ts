import { Door } from '../Door';

describe('Door', () => {
    it('should return correct id and prompt before opening (no key required)', () => {
        const door = new Door('door1');
        expect(door.getId()).toEqual('door1');
        expect(door.getInteractionPrompt()).toEqual('Open Door');
        expect(door.canInteract('player1')).toEqual(true);
    });

    it('should open when interacted with (no key required)', async () => {
        const door = new Door('door2');
        await door.onInteract('player1');
        expect(door.canInteract('player1')).toEqual(false);
        expect(door.getInteractionPrompt()).toEqual('');
    });

    it('should require key and not open if key is missing', async () => {
        const hasKey = jest.fn(() => false);
        const door = new Door('door3', 'RedKey', hasKey);
        expect(door.getInteractionPrompt()).toEqual('Open Door (requires RedKey)');
        expect(door.canInteract('player1')).toEqual(false);
        await door.onInteract('player1');
        expect(door.canInteract('player1')).toEqual(false);
        expect(hasKey).toHaveBeenCalledWith('player1', 'RedKey');
    });

    it('should open if key is present', async () => {
        const hasKey = jest.fn(() => true);
        const door = new Door('door4', 'BlueKey', hasKey);
        expect(door.canInteract('player1')).toEqual(true);
        await door.onInteract('player1');
        expect(door.canInteract('player1')).toEqual(false);
        expect(door.getInteractionPrompt()).toEqual('');
    });
}); 