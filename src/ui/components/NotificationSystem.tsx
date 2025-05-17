import React, { useState, useEffect } from 'react';

export const NotificationSystem: React.FC = () => {
    const [notifications, setNotifications] = useState<string[]>([]);

    useEffect(() => {
        // TODO: Subscribe to reputation change events and update notifications
        // For now, placeholder
    }, []);

    return (
        <div className="notification-system">
            {notifications.map((msg, idx) => (
                <div key={idx} className="notification">
                    {msg}
                </div>
            ))}
        </div>
    );
}; 