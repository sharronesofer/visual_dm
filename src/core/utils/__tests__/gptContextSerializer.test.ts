import { describe, it, expect } from 'vitest';
import { ContextSerializer, CONTEXT_VERSION, GPTContext, ContextPriority } from '../gptContextSerializer';

function makeContext(size = 3, essential = 1): GPTContext {
    const ctx: GPTContext = {};
    for (let i = 0; i < size; i++) {
        ctx[`k${i}`] = {
            key: `k${i}`,
            value: 'x'.repeat(essential && i < essential ? 100 : 10),
            priority: i < essential ? 'essential' : 'optional',
        };
    }
    return ctx;
}

describe('ContextSerializer', () => {
    it('serializes and deserializes context', () => {
        const ctx = makeContext(2, 1);
        const str = ContextSerializer.serialize(ctx);
        const restored = ContextSerializer.deserialize(str);
        expect(Object.keys(restored)).toEqual(Object.keys(ctx));
        expect(restored.k0.value).toBe(ctx.k0.value);
        expect(restored.k1.value).toBe(ctx.k1.value);
        expect(restored.k0.priority).toBe('essential');
        expect(restored.k1.priority).toBe('optional');
    });

    it('includes version field', () => {
        const ctx = makeContext(1, 1);
        const str = ContextSerializer.serialize(ctx);
        const wrapper = JSON.parse(str);
        let json = wrapper.data;
        if (wrapper.compressed) {
            // decompress
            json = require('lz-string').decompressFromUTF16(json);
        }
        const payload = JSON.parse(json);
        expect(payload.version).toBe(CONTEXT_VERSION);
    });

    it('compresses large context', () => {
        const ctx = makeContext(50, 25);
        const str = ContextSerializer.serialize(ctx);
        const wrapper = JSON.parse(str);
        expect(typeof wrapper.compressed).toBe('boolean');
        if (wrapper.compressed) {
            expect(typeof wrapper.data).toBe('string');
            // decompress should succeed
            expect(() => {
                try {
                    require('lz-string').decompressFromUTF16(wrapper.data);
                } catch (e) {
                    if (e instanceof Error) throw e;
                    throw new Error('Unknown error during decompression');
                }
            }).not.toThrow();
        }
    });

    it('prunes optional elements to fit max size', () => {
        const ctx = makeContext(20, 2); // 2 essential, 18 optional
        const pruned = ContextSerializer.pruneToFit(ctx, 500); // very small size
        // Only essentials should remain
        expect(Object.values(pruned).every(e => e.priority === 'essential')).toBe(true);
    });

    it('throws on invalid input', () => {
        expect(() => ContextSerializer.deserialize('not-json')).toThrow();
        expect(() => ContextSerializer.deserialize(JSON.stringify({ data: 'not-json', compressed: false }))).toThrow();
    });

    it('tags elements by priority', () => {
        const el = ContextSerializer.tagElement('foo', 123, 'essential');
        expect(el.key).toBe('foo');
        expect(el.value).toBe(123);
        expect(el.priority).toBe('essential');
    });

    it('calculates serialized size', () => {
        const ctx = makeContext(3, 2);
        const size = ContextSerializer.getSerializedSize(ctx);
        expect(typeof size).toBe('number');
        expect(size).toBeGreaterThan(0);
    });
}); 