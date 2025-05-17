import React, { useEffect, useState } from 'react';
import ConstructionProgressBar from './ConstructionProgressBar';
import { EventBus } from '../core/interfaces/types/events';
import { ConstructionProgress } from './ConstructionProgressSystem';

export const ConstructionProgressUI: React.FC<{ buildingId: string }> = ({ buildingId }) => {
    const [progress, setProgress] = useState<ConstructionProgress | null>(null);

    useEffect(() => {
        const bus = EventBus.getInstance();
        const handler = (event: any) => {
            if (event.buildingId === buildingId) setProgress(event.progress);
        };
        bus.on('construction:progress', handler);
        return () => { bus.off('construction:progress', handler); };
    }, [buildingId]);

    if (!progress) return null;
    return (
        <ConstructionProgressBar
            percentComplete={progress.percentComplete}
            status={progress.status}
            onCancel={progress.status === 'in-progress' ? () => {
                const bus = EventBus.getInstance();
                bus.emit('construction:cancel', {
                    type: 'construction:cancel',
                    buildingId,
                    timestamp: Date.now(),
                    source: 'ConstructionProgressUI',
                });
            } : undefined}
        />
    );
};

export default ConstructionProgressUI; 