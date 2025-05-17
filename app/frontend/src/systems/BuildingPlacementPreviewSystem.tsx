import { Position } from '../core/interfaces/types/common';
import { BuildingElementType, MaterialType, BuildingStructure } from '../core/interfaces/types/building';
import { ConstructionValidator, ConstructionRequest } from './ConstructionRequestSystem';
import { EventBus } from '../core/interfaces/types/events';
import ResourceCostPanel, { ResourceRequirement } from './ResourceCostPanel';
import React, { useMemo } from 'react';

export type PlacementMode = 'grid' | 'free-form';

export interface PlacementState {
    mode: PlacementMode;
    elementType: BuildingElementType;
    material: MaterialType;
    position: Position;
    isLoadBearing?: boolean;
    buildingType: string;
    playerId: string;
    resources: Record<string, number>;
    structure: BuildingStructure;
}

export class BuildingPlacementController {
    private state: PlacementState;
    private validator: ConstructionValidator;
    private eventBus = EventBus.getInstance();
    private onUpdate: (state: PlacementState, valid: boolean, errors: string[]) => void;

    constructor(
        initialState: PlacementState,
        validator: ConstructionValidator,
        onUpdate: (state: PlacementState, valid: boolean, errors: string[]) => void
    ) {
        this.state = initialState;
        this.validator = validator;
        this.onUpdate = onUpdate;
    }

    setPosition(position: Position) {
        this.state.position = position;
        this.validateAndUpdate();
    }

    setMode(mode: PlacementMode) {
        this.state.mode = mode;
        this.validateAndUpdate();
    }

    setElementType(type: BuildingElementType) {
        this.state.elementType = type;
        this.validateAndUpdate();
    }

    setMaterial(material: MaterialType) {
        this.state.material = material;
        this.validateAndUpdate();
    }

    setIsLoadBearing(isLoadBearing: boolean) {
        this.state.isLoadBearing = isLoadBearing;
        this.validateAndUpdate();
    }

    setBuildingType(buildingType: string) {
        this.state.buildingType = buildingType;
        this.validateAndUpdate();
    }

    setResources(resources: Record<string, number>) {
        this.state.resources = resources;
        this.validateAndUpdate();
    }

    setStructure(structure: BuildingStructure) {
        this.state.structure = structure;
        this.validateAndUpdate();
    }

    private validateAndUpdate() {
        const request: ConstructionRequest = {
            id: 'preview',
            playerId: this.state.playerId,
            buildingType: this.state.buildingType,
            elementType: this.state.elementType,
            position: this.state.position,
            material: this.state.material,
            isLoadBearing: this.state.isLoadBearing,
            resources: this.state.resources,
            timestamp: Date.now()
        };
        // Dummy player and resource/permission checks for preview
        const player: any = { id: this.state.playerId };
        const resourceCheck = () => true;
        const permissionCheck = () => true;
        const result = this.validator.validate(
            request,
            this.state.structure,
            player,
            resourceCheck,
            permissionCheck
        );
        this.onUpdate(this.state, result.valid, result.errors);
    }
}

export class BuildingPreviewRenderer {
    /**
     * Render a building preview with color overlay and error visualization.
     * @param state PlacementState for the preview
     * @param valid Whether the placement is valid
     * @param errors Array of error messages
     * @param containerId Optional DOM container for rendering (for canvas/3D integration)
     */
    static renderPreview(state: PlacementState, valid: boolean, errors: string[], containerId?: string): void {
        // This is a stub for actual 3D/canvas rendering. In a real implementation, this would:
        // - Render a semi-transparent building model at state.position
        // - Apply color overlay: green (valid), yellow (warning), red (invalid)
        // - Overlay error messages near the model or in a UI panel
        // - Highlight problematic areas (e.g., collision points)
        // For now, log to console for demonstration.
        let color = 'green';
        if (!valid && errors.length > 0) color = 'red';
        else if (!valid) color = 'yellow';
        console.log('[Preview] Render at', state.position, `Color: ${color}`, 'Errors:', errors);
        // Optionally, trigger a UI update or canvas redraw here.
    }
}

export class PlacementValidator {
    private validator: ConstructionValidator;
    constructor(validator: ConstructionValidator) {
        this.validator = validator;
    }
    validate(request: ConstructionRequest, structure: BuildingStructure, player: any) {
        // Use dummy resource/permission checks for preview
        return this.validator.validate(request, structure, player, () => true, () => true);
    }
}

// --- Enhanced React UI for Building Placement Preview ---

interface ErrorOverlayProps {
    errors: string[];
}

const ErrorOverlay: React.FC<ErrorOverlayProps> = ({ errors }) => (
    <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        color: 'red',
        background: 'rgba(255,0,0,0.1)',
        zIndex: 1000,
        pointerEvents: 'none',
        fontWeight: 'bold',
        padding: '4px',
    }}>
        {errors.map((err, i) => <div key={i}>{err}</div>)}
    </div>
);

export interface BuildingPlacementPreviewUIProps {
    placementState: PlacementState;
    playerResources: Record<string, number>;
    getRequiredResources: (state: PlacementState) => ResourceRequirement[];
    valid: boolean;
    errors: string[];
}

export const BuildingPlacementPreviewUI: React.FC<BuildingPlacementPreviewUIProps> = ({
    placementState,
    playerResources,
    getRequiredResources,
    valid,
    errors,
}) => {
    const requirements = useMemo(() => getRequiredResources(placementState), [placementState, getRequiredResources]);
    // Determine preview color
    let color = 'rgba(0,255,0,0.4)'; // green
    if (!valid && errors.length > 0) color = 'rgba(255,0,0,0.4)'; // red
    else if (!valid) color = 'rgba(255,255,0,0.4)'; // yellow

    // Render a simple box as a placeholder for the building preview
    // In a real app, this would be a 3D/canvas model
    return (
        <div style={{ position: 'relative', width: 400, height: 400, border: '1px solid #ccc' }}>
            <div
                style={{
                    position: 'absolute',
                    left: placementState.position.x,
                    top: placementState.position.y,
                    width: 80,
                    height: 80,
                    background: color,
                    opacity: 0.7,
                    border: '2px dashed #333',
                    borderRadius: 8,
                    pointerEvents: 'none',
                    transition: 'background 0.2s',
                }}
                aria-label="Building Preview"
            />
            {!valid && errors.length > 0 && <ErrorOverlay errors={errors} />}
            <ResourceCostPanel
                requirements={requirements}
                playerResources={playerResources}
                buildingType={placementState.buildingType}
                elementType={placementState.elementType}
                material={placementState.material}
                position={placementState.position}
            />
        </div>
    );
};

// --- Controller/Integration Example ---
// Usage: Instantiate BuildingPlacementController, pass onUpdate to update UI state
// Example (in a parent React component):
// const [valid, setValid] = useState(true);
// const [errors, setErrors] = useState<string[]>([]);
// const controller = useMemo(() => new BuildingPlacementController(initialState, validator, (state, valid, errors) => {
//   setValid(valid); setErrors(errors);
// }), [initialState, validator]);
//
// <BuildingPlacementPreviewUI
//   placementState={controller.state}
//   playerResources={playerResources}
//   getRequiredResources={getRequiredResources}
//   valid={valid}
//   errors={errors}
// />
// ... existing code ...

// --- Placement Validation Utility ---

/**
 * Validates a building placement using ConstructionValidator and optional collision checks.
 * Returns { valid: boolean, errors: string[] }
 */
export function validatePlacement(
    request: ConstructionRequest,
    structure: BuildingStructure,
    player: any,
    validator: ConstructionValidator,
    collisionSystem?: any // Optionally pass a CollisionSystem instance
): { valid: boolean; errors: string[] } {
    // Run construction validation
    const result = validator.validate(request, structure, player, () => true, () => true);
    let errors = result.errors ? [...result.errors] : [];
    let valid = result.valid;
    // Optionally, run collision checks
    if (collisionSystem && request.position) {
        // Assume request has dimensions or can infer from elementType
        const dimensions = { width: 80, height: 80 }; // Placeholder, replace with real logic
        const collisions = collisionSystem.findCollisions(request.position, dimensions);
        if (collisions.length > 0) {
            valid = false;
            errors.push('Collision detected with existing structure.');
        }
    }
    return { valid, errors };
}

// --- Unit Test Stub (to be placed in __tests__ or test file) ---
// describe('validatePlacement', () => {
//   it('should return valid=true for valid placement', () => {
//     // Setup mock ConstructionValidator, BuildingStructure, etc.
//     // Call validatePlacement and assert result.valid === true
//   });
//   it('should return valid=false and errors for invalid placement', () => {
//     // Setup mock with failing validation or collision
//     // Call validatePlacement and assert result.valid === false and errors.length > 0
//   });
// }); 