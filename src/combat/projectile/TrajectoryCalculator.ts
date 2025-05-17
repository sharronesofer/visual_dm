import { Position, Vector2D } from '../../core/interfaces/types/types/common/geometry';
import { normalizeVector } from '../../core/utils/utils/geometry/index';

export interface ProjectileParams {
    initialPosition: Position;
    initialVelocity: Vector2D; // dx, dy in world units/sec
    gravity?: number; // m/s^2, default 9.81
    timeStep?: number; // seconds per sample, default 0.05
    maxTime?: number; // max simulation time, default 5s
}

export interface TrajectoryPoint extends Position {
    time: number;
}

export interface TrajectoryResult {
    points: TrajectoryPoint[];
    maxHeight: number;
    totalDistance: number;
    landingPosition: Position;
}

export class TrajectoryCalculator {
    static calculateTrajectory(params: ProjectileParams): TrajectoryResult {
        const gravity = params.gravity ?? 9.81;
        const timeStep = params.timeStep ?? 0.05;
        const maxTime = params.maxTime ?? 5.0;
        const { initialPosition, initialVelocity } = params;

        let t = 0;
        let x = initialPosition.x;
        let y = initialPosition.y;
        let vx = initialVelocity.dx;
        let vy = initialVelocity.dy;
        let maxHeight = y;
        const points: TrajectoryPoint[] = [{ x, y, time: t }];

        while (t < maxTime) {
            t += timeStep;
            x += vx * timeStep;
            vy -= gravity * timeStep;
            y += vy * timeStep;
            if (y > maxHeight) maxHeight = y;
            points.push({ x, y, time: t });
            if (y <= 0) break; // Landed (ground at y=0)
        }

        const landing = points[points.length - 1];
        const totalDistance = landing.x - initialPosition.x;
        return {
            points,
            maxHeight,
            totalDistance: Math.abs(totalDistance),
            landingPosition: { x: landing.x, y: 0 },
        };
    }

    // Utility: get launch velocity vector from speed and angle (degrees)
    static getVelocityFromAngle(speed: number, angleDeg: number): Vector2D {
        const angleRad = (angleDeg * Math.PI) / 180;
        return {
            dx: speed * Math.cos(angleRad),
            dy: speed * Math.sin(angleRad),
        };
    }

    // Debug: simple text visualization (for test harness)
    static debugPrintTrajectory(result: TrajectoryResult): void {
        for (const pt of result.points) {
            console.log(`t=${pt.time.toFixed(2)}s: x=${pt.x.toFixed(2)}, y=${pt.y.toFixed(2)}`);
        }
        console.log(`Max height: ${result.maxHeight.toFixed(2)}, Total distance: ${result.totalDistance.toFixed(2)}`);
    }
} 