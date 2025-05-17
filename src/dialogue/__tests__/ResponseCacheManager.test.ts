import { ResponseCacheManager, ResponseCacheConfig } from '../ResponseCacheManager';
import { DialogueMetadata } from '../types';

describe('ResponseCacheManager', () => {
    const meta: DialogueMetadata = { tokensUsed: 10, responseTimeMs: 100, model: 'gpt-test' };
    let cache: ResponseCacheManager;

    beforeEach(() => {
        cache = new ResponseCacheManager({ maxSize: 2, expiryMs: 50 });
    });

    it('stores and retrieves responses', () => {
        cache.set('hello', ['world'], 'hi!', meta);
        expect(cache.get('hello', ['world'])).toEqual('hi!');
    });

    it('returns undefined for expired entries', async () => {
        cache.set('foo', [], 'bar', meta);
        await new Promise((r) => setTimeout(r, 60));
        expect(cache.get('foo', [])).toBeUndefined();
    });

    it('evicts oldest entry when maxSize is reached', () => {
        cache.set('a', [], '1', meta);
        cache.set('b', [], '2', meta);
        cache.set('c', [], '3', meta); // Should evict 'a'
        expect(cache.get('a', [])).toBeUndefined();
        expect(cache.get('b', [])).toEqual('2');
        expect(cache.get('c', [])).toEqual('3');
    });

    it('tracks analytics for hits and misses', () => {
        cache.set('x', [], 'y', meta);
        cache.get('x', []);
        cache.get('z', []);
        const analytics = cache.getAnalytics();
        expect(analytics.hits).toEqual(1);
        expect(analytics.misses).toEqual(1);
        expect(analytics.mostFrequent[ResponseCacheManager.makeKey('x', [])]).toEqual(1);
    });

    it('clears cache and analytics', () => {
        cache.set('a', [], '1', meta);
        cache.clear();
        expect(cache.get('a', [])).toBeUndefined();
        expect(cache.getAnalytics().hits).toEqual(0);
    });

    it('invalidates entries by predicate', () => {
        cache.set('a', [], '1', meta);
        cache.set('b', [], '2', meta);
        cache.invalidate((entry) => entry.response === '1');
        expect(cache.get('a', [])).toBeUndefined();
        expect(cache.get('b', [])).toEqual('2');
    });

    it('prewarms the cache', () => {
        cache.prewarm([
            { prompt: 'p1', context: ['c1'], response: 'r1', metadata: meta },
            { prompt: 'p2', context: ['c2'], response: 'r2', metadata: meta },
        ]);
        expect(cache.get('p1', ['c1'])).toEqual('r1');
        expect(cache.get('p2', ['c2'])).toEqual('r2');
    });
}); 