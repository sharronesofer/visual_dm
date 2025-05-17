import { describe, it, expect } from 'vitest';
import { validatePlacement } from '../validatePlacement';
import { Vector3, Quaternion } from '../../types';

describe('validatePlacement', () => {
    const defaultRotation: Quaternion = { x: 0, y: 0, z: 0, w: 1 };

    it('returns valid for normal placement', () => {
        const pos: Vector3 = { x: 10, y: 10, z: 2 };
        const result = validatePlacement('house', pos, defaultRotation);
        expect(result.status).toBe('valid');
        expect(result.messages.length).toBe(0);
    });

    it('returns error for out-of-bounds placement', () => {
        const pos: Vector3 = { x: -1, y: 5, z: 2 };
        const result = validatePlacement('house', pos, defaultRotation);
        expect(result.status).toBe('error');
        expect(result.messages[0]).toMatch(/outside allowed area/i);
    });

    it('returns error for tower without foundation', () => {
        const pos: Vector3 = { x: 5, y: 5, z: 0 };
        const result = validatePlacement('tower', pos, defaultRotation);
        expect(result.status).toBe('error');
        expect(result.messages[0]).toMatch(/foundation/i);
    });
}); 