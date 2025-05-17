import React from 'react';

export interface ConstructionProgressBarProps {
    percentComplete: number; // 0 to 1
    status: 'in-progress' | 'complete' | 'cancelled';
    onCancel?: () => void;
}

export const ConstructionProgressBar: React.FC<ConstructionProgressBarProps> = ({
    percentComplete,
    status,
    onCancel,
}) => {
    let barColor = '#4caf50'; // green
    if (status === 'cancelled') barColor = '#f44336'; // red
    else if (status === 'in-progress') barColor = '#2196f3'; // blue

    return (
        <div className="construction-progress-bar" style={{ width: 200, margin: '8px 0' }} aria-label="Construction Progress">
            <div
                style={{
                    width: '100%',
                    height: 20,
                    background: '#eee',
                    borderRadius: 4,
                    overflow: 'hidden',
                    position: 'relative',
                }}
            >
                <div
                    style={{
                        width: `${Math.round(percentComplete * 100)}%`,
                        height: '100%',
                        background: barColor,
                        transition: 'width 0.3s',
                    }}
                    aria-valuenow={Math.round(percentComplete * 100)}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    role="progressbar"
                />
                <span
                    style={{
                        position: 'absolute',
                        left: '50%',
                        top: '50%',
                        transform: 'translate(-50%, -50%)',
                        fontWeight: 'bold',
                        color: status === 'cancelled' ? '#f44336' : '#333',
                        fontSize: 14,
                    }}
                >
                    {status === 'complete' ? 'Complete' : status === 'cancelled' ? 'Cancelled' : `${Math.round(percentComplete * 100)}%`}
                </span>
            </div>
            {status === 'in-progress' && onCancel && (
                <button
                    onClick={onCancel}
                    style={{ marginTop: 4, background: '#f44336', color: '#fff', border: 'none', borderRadius: 4, padding: '4px 8px', cursor: 'pointer' }}
                    aria-label="Cancel Construction"
                >
                    Cancel
                </button>
            )}
        </div>
    );
};

export default ConstructionProgressBar; 