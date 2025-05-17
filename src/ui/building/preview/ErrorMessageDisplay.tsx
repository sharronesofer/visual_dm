// ErrorMessageDisplay.tsx
import React from 'react';
import { Vector3 } from '../../types';

interface ErrorMessageDisplayProps {
    messages: string[];
    status: 'warning' | 'error';
    anchor?: Vector3; // Optional position for 3D/2D overlay
}

export const ErrorMessageDisplay: React.FC<ErrorMessageDisplayProps> = ({ messages, status, anchor }) => {
    // Color coding
    const color = status === 'error' ? '#ff3333' : '#ffcc00';
    // Positioning: if anchor provided, use absolute positioning (stub for 3D overlay)
    const style: React.CSSProperties = anchor
        ? {
            position: 'absolute',
            left: anchor.x,
            top: anchor.y,
            background: color,
            color: '#fff',
            padding: '8px 14px',
            borderRadius: 6,
            fontSize: 14,
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
            zIndex: 1000,
            pointerEvents: 'none',
            maxWidth: 260,
        }
        : {
            background: color,
            color: '#fff',
            padding: '8px 14px',
            borderRadius: 6,
            fontSize: 14,
            margin: '8px 0',
            maxWidth: 260,
        };

    return (
        <div style={style}>
            {messages.map((msg, idx) => (
                <div key={idx} style={{ marginBottom: 4 }}>{msg}</div>
            ))}
        </div>
    );
}; 