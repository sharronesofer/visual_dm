import React, { useEffect, useState } from 'react';

export interface ConstructionNotificationProps {
    message: string;
    type?: 'success' | 'error' | 'info';
    duration?: number; // ms
    onClose?: () => void;
}

export const ConstructionNotification: React.FC<ConstructionNotificationProps> = ({
    message,
    type = 'info',
    duration = 3000,
    onClose,
}) => {
    const [visible, setVisible] = useState(true);

    useEffect(() => {
        if (duration > 0) {
            const timer = setTimeout(() => {
                setVisible(false);
                if (onClose) onClose();
            }, duration);
            return () => clearTimeout(timer);
        }
    }, [duration, onClose]);

    if (!visible) return null;

    let bgColor = '#2196f3';
    if (type === 'success') bgColor = '#4caf50';
    else if (type === 'error') bgColor = '#f44336';

    return (
        <div
            className="construction-notification"
            style={{
                background: bgColor,
                color: '#fff',
                padding: '12px 24px',
                borderRadius: 6,
                position: 'fixed',
                top: 24,
                right: 24,
                zIndex: 1000,
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                minWidth: 200,
                display: 'flex',
                alignItems: 'center',
            }}
            role="status"
            aria-live="polite"
        >
            <span style={{ flex: 1 }}>{message}</span>
            <button
                onClick={() => { setVisible(false); if (onClose) onClose(); }}
                aria-label="Close notification"
                style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#fff',
                    fontSize: 18,
                    marginLeft: 12,
                    cursor: 'pointer',
                }}
            >
                ×
            </button>
        </div>
    );
};

export default ConstructionNotification; 