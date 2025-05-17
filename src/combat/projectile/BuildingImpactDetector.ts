import { Position, Rectangle } from '../../core/interfaces/types/types/common/geometry';
import { TrajectoryPoint } from './TrajectoryCalculator';

export interface BuildingCollider {
    id: string;
    bounds: Rectangle;
}

export interface ImpactLog {
    buildingId: string;
    point: Position;
    angle: number; // in degrees
    projectileType: string;
}

export class BuildingImpactDetector {
    /**
     * Checks for collisions between a projectile trajectory and a set of building colliders.
     * Returns an array of impact logs for all detected impacts (first impact per building).
     */
    static detectImpacts(
        trajectory: TrajectoryPoint[],
        buildings: BuildingCollider[],
        projectileType: string
    ): ImpactLog[] {
        const impacts: ImpactLog[] = [];
        const impactedBuildings = new Set<string>();
        for (let i = 1; i < trajectory.length; i++) {
            const prev = trajectory[i - 1];
            const curr = trajectory[i];
            for (const building of buildings) {
                if (impactedBuildings.has(building.id)) continue;
                if (this.segmentIntersectsRect(prev, curr, building.bounds)) {
                    // Calculate impact angle (in degrees)
                    const dx = curr.x - prev.x;
                    const dy = curr.y - prev.y;
                    const angle = (Math.atan2(dy, dx) * 180) / Math.PI;
                    impacts.push({
                        buildingId: building.id,
                        point: { x: curr.x, y: curr.y },
                        angle,
                        projectileType,
                    });
                    impactedBuildings.add(building.id);
                }
            }
        }
        return impacts;
    }

    /**
     * Checks if a line segment (p1-p2) intersects a rectangle (AABB)
     */
    static segmentIntersectsRect(p1: Position, p2: Position, rect: Rectangle): boolean {
        // Liang-Barsky or Cohen-Sutherland could be used, but for simplicity, check segment against all 4 edges
        const edges = [
            // Top
            [{ x: rect.x, y: rect.y }, { x: rect.x + rect.width, y: rect.y }],
            // Bottom
            [{ x: rect.x, y: rect.y + rect.height }, { x: rect.x + rect.width, y: rect.y + rect.height }],
            // Left
            [{ x: rect.x, y: rect.y }, { x: rect.x, y: rect.y + rect.height }],
            // Right
            [{ x: rect.x + rect.width, y: rect.y }, { x: rect.x + rect.width, y: rect.y + rect.height }],
        ];
        for (const [a, b] of edges) {
            if (this.segmentsIntersect(p1, p2, a, b)) return true;
        }
        // Also check if segment is fully inside the rectangle
        if (
            p1.x >= rect.x && p1.x <= rect.x + rect.width &&
            p1.y >= rect.y && p1.y <= rect.y + rect.height
        ) return true;
        return false;
    }

    /**
     * Checks if two line segments (p1-p2 and q1-q2) intersect
     */
    static segmentsIntersect(p1: Position, p2: Position, q1: Position, q2: Position): boolean {
        function ccw(a: Position, b: Position, c: Position) {
            return (c.y - a.y) * (b.x - a.x) > (b.y - a.y) * (c.x - a.x);
        }
        return (
            ccw(p1, q1, q2) !== ccw(p2, q1, q2) &&
            ccw(p1, p2, q1) !== ccw(p1, p2, q2)
        );
    }
} 