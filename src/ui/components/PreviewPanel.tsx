import React from 'react';

/**
 * PreviewPanel displays a real-time preview of the character model.
 * Props will support model data, rotation, zoom, and event handlers for future integration.
 */
export interface PreviewPanelProps {
    // Placeholder for future props
    // model?: CharacterModel;
    // rotation?: number;
    // zoom?: number;
    // onRotate?: (angle: number) => void;
    // onZoom?: (zoom: number) => void;
}

export const PreviewPanel: React.FC<PreviewPanelProps> = (props) => {
    return (
        <div style={{ width: 300, height: 400, background: '#222', borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#888', fontSize: 20 }}>
            Character Preview
        </div>
    );
};

export default PreviewPanel; 