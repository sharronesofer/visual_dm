import { TrajectoryCalculator, ProjectileParams } from './TrajectoryCalculator';

describe('TrajectoryCalculator', () => {
    it('calculates a simple 45-degree launch', () => {
        const speed = 10; // m/s
        const angle = 45; // degrees
        const initialVelocity = TrajectoryCalculator.getVelocityFromAngle(speed, angle);
        const params: ProjectileParams = {
            initialPosition: { x: 0, y: 0 },
            initialVelocity,
            gravity: 9.81,
            timeStep: 0.01,
            maxTime: 2.0,
        };
        const result = TrajectoryCalculator.calculateTrajectory(params);
        // Theoretical max height: (v^2 * sin^2(angle)) / (2g)
        const expectedMaxHeight = (speed * speed * Math.pow(Math.sin(Math.PI / 4), 2)) / (2 * 9.81);
        expect(Math.abs(result.maxHeight - expectedMaxHeight)).toBeLessThan(0.05);
        // Theoretical range: (v^2 * sin(2*angle)) / g
        const expectedRange = (speed * speed * Math.sin(Math.PI / 2)) / 9.81;
        expect(Math.abs(result.totalDistance - expectedRange)).toBeLessThan(0.1);
        expect(result.landingPosition.y).toBe(0);
    });

    it('handles vertical launch', () => {
        const speed = 10;
        const angle = 90;
        const initialVelocity = TrajectoryCalculator.getVelocityFromAngle(speed, angle);
        const params: ProjectileParams = {
            initialPosition: { x: 0, y: 0 },
            initialVelocity,
            gravity: 9.81,
            timeStep: 0.01,
            maxTime: 3.0,
        };
        const result = TrajectoryCalculator.calculateTrajectory(params);
        expect(result.landingPosition.x).toBeCloseTo(0, 2);
        expect(result.maxHeight).toBeGreaterThan(4);
    });

    it('handles zero velocity (no movement)', () => {
        const params: ProjectileParams = {
            initialPosition: { x: 0, y: 0 },
            initialVelocity: { dx: 0, dy: 0 },
            gravity: 9.81,
            timeStep: 0.01,
            maxTime: 1.0,
        };
        const result = TrajectoryCalculator.calculateTrajectory(params);
        expect(result.points.length).toBe(2); // Only initial and one step
        expect(result.landingPosition.x).toBe(0);
        expect(result.landingPosition.y).toBe(0);
    });

    it('getVelocityFromAngle returns correct vector', () => {
        const v = TrajectoryCalculator.getVelocityFromAngle(10, 0);
        expect(v.dx).toBeCloseTo(10);
        expect(v.dy).toBeCloseTo(0);
        const v2 = TrajectoryCalculator.getVelocityFromAngle(10, 90);
        expect(v2.dx).toBeCloseTo(0);
        expect(v2.dy).toBeCloseTo(10);
    });
}); 