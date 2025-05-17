// BuildingPreviewSystem.ts
// Core controller for managing building preview state and integration

import { Vector3, Quaternion } from '../../types';
import { validatePlacement, ValidationResult } from './validatePlacement';

export type PreviewState = {
    buildingType: string;
    position: Vector3;
    rotation: Quaternion;
    validation: ValidationResult;
};

export class BuildingPreviewSystem {
    private state: PreviewState | null = null;
    private onUpdate: (() => void) | null = null;

    constructor() { }

    setPreview(buildingType: string, position: Vector3, rotation: Quaternion) {
        const validation = validatePlacement(buildingType, position, rotation);
        this.state = { buildingType, position, rotation, validation };
        this.triggerUpdate();
    }

    clearPreview() {
        this.state = null;
        this.triggerUpdate();
    }

    getPreviewState(): PreviewState | null {
        return this.state;
    }

    onStateUpdate(cb: () => void) {
        this.onUpdate = cb;
    }

    private triggerUpdate() {
        if (this.onUpdate) this.onUpdate();
    }
} 