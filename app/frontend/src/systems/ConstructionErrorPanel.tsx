import React from 'react';

export interface ConstructionErrorPanelProps {
    errors: string[];
    onClose?: () => void;
}

export const ConstructionErrorPanel: React.FC<ConstructionErrorPanelProps> = ({ errors, onClose }) => {
    if (!errors || errors.length === 0) return null;
    return (
        <div
            className="construction-error-panel"
            style={{
                background: '#f44336',
                color: '#fff',
                padding: '16px 24px',
                borderRadius: 6,
                position: 'fixed',
                bottom: 24,
                right: 24,
                zIndex: 1000,
                minWidth: 240,
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
            }}
            role="alert"
            aria-live="assertive"
        >
            <div style={{ fontWeight: 'bold', marginBottom: 8 }}>Construction Error</div>
            <ul style={{ margin: 0, padding: 0, listStyle: 'disc inside' }}>
                {errors.map((err, i) => (
                    <li key={i} style={{ marginBottom: 4 }}>{err}</li>
                ))}
            </ul>
            {onClose && (
                <button
                    onClick={onClose}
                    aria-label="Close error panel"
                    style={{
                        background: 'transparent',
                        border: 'none',
                        color: '#fff',
                        fontSize: 18,
                        marginTop: 12,
                        cursor: 'pointer',
                        float: 'right',
                    }}
                >
                    ×
                </button>
            )}
        </div>
    );
};

export default ConstructionErrorPanel; 