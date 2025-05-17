import { Vector3, Quaternion } from '../../types';

export interface ConstraintViolation {
    type: 'collision' | 'structural' | 'resource' | 'connection';
    message: string;
    location?: Vector3;
}

export interface ValidationResult {
    status: 'valid' | 'warning' | 'error';
    messages: string[];
    highlightPoints: Vector3[];
    constraintViolations: ConstraintViolation[];
}

export function validatePlacement(
    buildingType: string,
    position: Vector3,
    rotation: Quaternion
): ValidationResult {
    // Stubbed logic for demonstration
    // In production, replace with real collision/structural/resource checks
    const violations: ConstraintViolation[] = [];
    const highlightPoints: Vector3[] = [];
    const messages: string[] = [];

    // Example: fake collision check
    if (position.x < 0 || position.y < 0) {
        violations.push({
            type: 'collision',
            message: 'Cannot place building outside map bounds.',
            location: position,
        });
        highlightPoints.push(position);
        messages.push('Placement is outside allowed area.');
    }

    // Example: fake structural check
    if (buildingType === 'tower' && position.z < 1) {
        violations.push({
            type: 'structural',
            message: 'Tower must be placed on a foundation.',
            location: position,
        });
        highlightPoints.push(position);
        messages.push('Tower requires a foundation.');
    }

    let status: 'valid' | 'warning' | 'error' = 'valid';
    if (violations.length > 0) {
        status = violations.some(v => v.type === 'collision' || v.type === 'structural') ? 'error' : 'warning';
    }

    return {
        status,
        messages,
        highlightPoints,
        constraintViolations: violations,
    };
} 