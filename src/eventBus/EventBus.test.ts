import { describe, it, expect, vi, beforeEach } from 'vitest';
import { InMemoryEventBus } from './EventBus.ts';

describe('InMemoryEventBus', () => {
    let eventBus: InMemoryEventBus;
    beforeEach(() => {
        eventBus = new InMemoryEventBus();
    });

    it('should register and emit events to handlers', async () => {
        const payload = { foo: 'bar' };
        const handler = vi.fn();
        eventBus.on('test:event', handler);
        eventBus.emit('test:event', payload);
        await new Promise(r => setTimeout(r, 10));
        expect(handler).toHaveBeenCalledWith(payload);
    });

    it('should allow handler removal', async () => {
        const handler = vi.fn();
        eventBus.on('test:remove', handler);
        eventBus.off('test:remove', handler);
        eventBus.emit('test:remove', { removed: true });
        await new Promise(r => setTimeout(r, 10));
        expect(handler).not.toHaveBeenCalled();
    });

    it('should handle errors in handlers gracefully', async () => {
        const handler = vi.fn(() => { throw new Error('Handler error'); });
        eventBus.on('test:error', handler);
        eventBus.emit('test:error', {});
        await new Promise(r => setTimeout(r, 10));
        expect(handler).toHaveBeenCalled();
    });

    it('should support multiple handlers for the same event', async () => {
        const results: string[] = [];
        eventBus.on('multi', () => results.push('a'));
        eventBus.on('multi', () => results.push('b'));
        eventBus.emit('multi', {});
        await new Promise(r => setTimeout(r, 10));
        expect(results).toContain('a');
        expect(results).toContain('b');
    });
}); 