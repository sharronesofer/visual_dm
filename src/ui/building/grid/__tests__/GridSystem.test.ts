import { describe, it, expect } from 'vitest';
import { GridSystem } from '../GridSystem';
import { Vector3 } from '../../types';

describe('GridSystem', () => {
    it('snaps position to grid', () => {
        const grid = new GridSystem(2);
        const pos: Vector3 = { x: 2.7, y: 3.1, z: 0.9 };
        const snapped = grid.snapPosition(pos);
        expect(snapped).toEqual({ x: 2, y: 4, z: 0 });
    });

    it('returns original position if snapping disabled', () => {
        const grid = new GridSystem(1, false);
        const pos: Vector3 = { x: 1.2, y: 2.8, z: 0.5 };
        expect(grid.snapPosition(pos)).toEqual(pos);
    });

    it('checks alignment within threshold', () => {
        const grid = new GridSystem(1);
        const a: Vector3 = { x: 1, y: 2, z: 3 };
        const b: Vector3 = { x: 1.005, y: 2, z: 3 };
        expect(grid.isAligned(a, b, 0.01)).toBe(true);
        const c: Vector3 = { x: 1.1, y: 2, z: 3 };
        expect(grid.isAligned(a, c, 0.01)).toBe(false);
    });
}); 