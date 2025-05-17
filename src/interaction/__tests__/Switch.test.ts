import { Switch } from '../Switch';

describe('Switch', () => {
    it('should return correct id and prompt when off', () => {
        const onToggle = jest.fn();
        const sw = new Switch('switch1', 'Main Power', onToggle);
        expect(sw.getId()).toEqual('switch1');
        expect(sw.getInteractionPrompt()).toEqual('Turn on Main Power');
        expect(sw.canInteract('player1')).toEqual(true);
    });

    it('should toggle on and off, calling onToggle with correct state', async () => {
        const onToggle = jest.fn();
        const sw = new Switch('switch2', 'Lights', onToggle);
        await sw.onInteract('player1');
        expect(onToggle).toHaveBeenCalledWith('player1', true);
        expect(sw.getInteractionPrompt()).toEqual('Turn off Lights');
        await sw.onInteract('player1');
        expect(onToggle).toHaveBeenCalledWith('player1', false);
        expect(sw.getInteractionPrompt()).toEqual('Turn on Lights');
        expect(onToggle).toHaveBeenCalledTimes(2);
    });
}); 