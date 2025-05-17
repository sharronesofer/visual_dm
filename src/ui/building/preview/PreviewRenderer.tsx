// PreviewRenderer.tsx
import React from 'react';
import { ValidationResult } from './validatePlacement';
import { Vector3, Quaternion } from '../../types';

interface PreviewRendererProps {
    model: any; // Replace with actual model type
    position: Vector3;
    rotation: Quaternion;
    validation: ValidationResult;
}

// Utility to get color based on validation status
function getPreviewColor(status: ValidationResult['status']): string {
    switch (status) {
        case 'valid':
            return 'rgba(0,255,0,0.5)'; // Green
        case 'warning':
            return 'rgba(255,255,0,0.5)'; // Yellow
        case 'error':
            return 'rgba(255,0,0,0.5)'; // Red
        default:
            return 'rgba(128,128,128,0.5)';
    }
}

export const PreviewRenderer: React.FC<PreviewRendererProps> = ({ model, position, rotation, validation }) => {
    // In a real engine, this would use a 3D renderer (e.g., Three.js, Babylon.js, Unity, Unreal, etc.)
    // Here, we just show a placeholder and comments for integration points

    // Example: apply ghost material with color overlay
    const previewColor = getPreviewColor(validation.status);

    return (
        <div style={{ position: 'absolute', left: 0, top: 0, pointerEvents: 'none' }}>
            {/* Render 3D model at position/rotation with ghost material and previewColor */}
            {/* Example: <GhostedModel model={model} position={position} rotation={rotation} color={previewColor} /> */}
            <div style={{
                width: 200,
                height: 200,
                background: previewColor,
                borderRadius: 10,
                border: '2px dashed #888',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 18,
                color: '#222',
                opacity: 0.7,
            }}>
                Building Preview
                <div style={{ fontSize: 12, color: '#000', marginTop: 8 }}>
                    Status: {validation.status}
                </div>
            </div>
            {/* Highlight problem areas (stub) */}
            {validation.highlightPoints.map((pt, idx) => (
                <div key={idx} style={{
                    position: 'absolute',
                    left: pt.x, top: pt.y,
                    width: 10, height: 10,
                    background: 'red',
                    borderRadius: '50%',
                    opacity: 0.8,
                }} />
            ))}
        </div>
    );
}; 