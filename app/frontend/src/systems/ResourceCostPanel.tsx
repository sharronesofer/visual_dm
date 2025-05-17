import React from 'react';
import { BuildingElementType, MaterialType } from '../core/interfaces/types/building';
import { Position } from '../core/interfaces/types/common';

export interface ResourceRequirement {
    resource: string;
    required: number;
    available: number;
}

export interface ResourceCostPanelProps {
    requirements: ResourceRequirement[];
    playerResources: Record<string, number>;
    buildingType: string;
    elementType: BuildingElementType;
    material: MaterialType;
    position: Position;
    onRequestResourceInfo?: (resource: string) => void;
}

export const ResourceCostPanel: React.FC<ResourceCostPanelProps> = ({
    requirements,
    playerResources,
    buildingType,
    elementType,
    material,
    position,
    onRequestResourceInfo,
}) => {
    return (
        <div className="resource-cost-panel" aria-label="Resource Requirements">
            <h3>Required Resources</h3>
            <ul>
                {requirements.map(({ resource, required, available }) => {
                    const sufficient = available >= required;
                    return (
                        <li key={resource} style={{ color: sufficient ? 'inherit' : 'red' }}>
                            <span aria-label={resource} style={{ fontWeight: 'bold' }}>{resource}:</span>
                            <span> {available} / {required}</span>
                            {!sufficient && (
                                <span aria-label="Insufficient" title="Insufficient resources" style={{ marginLeft: 8, color: 'red' }}>⚠️</span>
                            )}
                            {onRequestResourceInfo && (
                                <button
                                    aria-label={`More info about ${resource}`}
                                    onClick={() => onRequestResourceInfo(resource)}
                                    style={{ marginLeft: 8 }}
                                >
                                    ℹ️
                                </button>
                            )}
                        </li>
                    );
                })}
            </ul>
            <div style={{ marginTop: 8, fontSize: 12 }}>
                <span>Building: <b>{buildingType}</b></span> | <span>Element: <b>{elementType}</b></span> | <span>Material: <b>{material}</b></span>
            </div>
            <div style={{ fontSize: 12 }}>Position: ({position.x}, {position.y})</div>
        </div>
    );
};

export default ResourceCostPanel; 