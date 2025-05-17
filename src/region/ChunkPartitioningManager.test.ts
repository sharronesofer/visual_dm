import { ChunkPartitioningManager, ChunkState } from './ChunkPartitioningManager';
import { EventBus } from '../core/events/EventBus';
import { SceneEventType } from '../core/events/SceneEventTypes';

describe('ChunkPartitioningManager', () => {
    let manager: ChunkPartitioningManager;
    let events: any[];

    beforeEach(() => {
        manager = new ChunkPartitioningManager();
        events = [];
        jest.spyOn(EventBus, 'getInstance').mockReturnValue({
            emit: (event: any) => events.push(event),
        } as any);
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    it('sets and gets chunk state', () => {
        manager.setChunkState('1,1', 'loading');
        expect(manager.getChunkState('1,1')).toBe('loading');
        manager.setChunkState('1,1', 'loaded');
        expect(manager.getChunkState('1,1')).toBe('loaded');
    });

    it('emits event on state change', () => {
        manager.setChunkState('2,2', 'loading');
        manager.setChunkState('2,2', 'loaded');
        expect(events.some(e => e.data.chunkId === '2,2' && e.data.state === 'loaded')).toBe(true);
    });

    it('sets and gets chunk priority', () => {
        manager.setChunkPriority('3,3', 5);
        expect(manager.getChunkPriority('3,3')).toBe(5);
        manager.setChunkPriority('3,3', 10);
        expect(manager.getChunkPriority('3,3')).toBe(10);
    });

    it('emits event on priority change', () => {
        manager.setChunkPriority('4,4', 1);
        manager.setChunkPriority('4,4', 2);
        expect(events.some(e => e.data.chunkId === '4,4' && e.data.priority === 2)).toBe(true);
    });

    it('handles dependencies and canUnload logic', () => {
        manager.addDependency('5,5', '6,6');
        expect(manager.canUnload('5,5')).toBe(false);
        manager.removeDependency('5,5', '6,6');
        expect(manager.canUnload('5,5')).toBe(true);
    });

    it('returns all chunk info', () => {
        manager.setChunkState('7,7', 'loaded');
        manager.setChunkPriority('7,7', 3);
        const all = manager.getAllChunks();
        expect(all.length).toBeGreaterThan(0);
        expect(all[0].id).toBe('7,7');
    });
}); 