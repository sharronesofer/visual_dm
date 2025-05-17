import { BuildingImpactDetector, BuildingCollider } from './BuildingImpactDetector';
import { TrajectoryPoint } from './TrajectoryCalculator';

describe('BuildingImpactDetector', () => {
    const building: BuildingCollider = {
        id: 'b1',
        bounds: { x: 5, y: 0, width: 2, height: 4 },
    };
    const building2: BuildingCollider = {
        id: 'b2',
        bounds: { x: 10, y: 0, width: 2, height: 4 },
    };

    it('detects a direct hit', () => {
        const trajectory: TrajectoryPoint[] = [
            { x: 0, y: 2, time: 0 },
            { x: 6, y: 2, time: 1 },
        ];
        const impacts = BuildingImpactDetector.detectImpacts(trajectory, [building], 'arrow');
        expect(impacts.length).toBe(1);
        expect(impacts[0].buildingId).toBe('b1');
    });

    it('detects a grazing hit (edge)', () => {
        const trajectory: TrajectoryPoint[] = [
            { x: 0, y: 0, time: 0 },
            { x: 5, y: 0, time: 1 }, // exactly on left edge
        ];
        const impacts = BuildingImpactDetector.detectImpacts(trajectory, [building], 'arrow');
        expect(impacts.length).toBe(1);
    });

    it('detects no collision for near miss', () => {
        const trajectory: TrajectoryPoint[] = [
            { x: 0, y: 5, time: 0 },
            { x: 7, y: 5, time: 1 },
        ];
        const impacts = BuildingImpactDetector.detectImpacts(trajectory, [building], 'arrow');
        expect(impacts.length).toBe(0);
    });

    it('detects multiple buildings', () => {
        const trajectory: TrajectoryPoint[] = [
            { x: 0, y: 2, time: 0 },
            { x: 12, y: 2, time: 1 },
        ];
        const impacts = BuildingImpactDetector.detectImpacts(trajectory, [building, building2], 'fireball');
        expect(impacts.length).toBe(2);
        expect(impacts.map(i => i.buildingId)).toContain('b1');
        expect(impacts.map(i => i.buildingId)).toContain('b2');
    });

    it('returns correct impact angle', () => {
        const trajectory: TrajectoryPoint[] = [
            { x: 0, y: 0, time: 0 },
            { x: 6, y: 0, time: 1 },
        ];
        const impacts = BuildingImpactDetector.detectImpacts(trajectory, [building], 'arrow');
        expect(Math.abs(impacts[0].angle)).toBeLessThan(1); // horizontal
    });
}); 