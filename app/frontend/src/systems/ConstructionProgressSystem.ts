import { EventBus } from '../core/interfaces/types/events';
import { ConstructionStartEvent, ConstructionCancelEvent, ConstructionProgressEvent, TickEvent } from '../core/interfaces/types/events';
import ConstructionProgressBar from './ConstructionProgressBar';
import React, { useEffect, useState } from 'react';

export interface ConstructionProgress {
    buildingId: string;
    startTime: number;
    duration: number;
    percentComplete: number;
    status: 'in-progress' | 'complete' | 'cancelled';
}

export type ConstructionProgressMap = Record<string, ConstructionProgress>;

export class ConstructionProgressSystem {
    private progressMap: ConstructionProgressMap = {};
    private eventBus = EventBus.getInstance();

    constructor() {
        this.eventBus.on('construction:start', this.handleStart as (event: ConstructionStartEvent) => void);
        this.eventBus.on('construction:cancel', this.handleCancel as (event: ConstructionCancelEvent) => void);
        this.eventBus.on('tick', this.handleTick as (event: TickEvent) => void);
    }

    handleStart = (event: ConstructionStartEvent) => {
        const { buildingId, duration } = event;
        this.progressMap[buildingId] = {
            buildingId,
            startTime: Date.now(),
            duration,
            percentComplete: 0,
            status: 'in-progress',
        };
        this.emitUpdate(buildingId);
    };

    handleCancel = (event: ConstructionCancelEvent) => {
        const { buildingId } = event;
        if (this.progressMap[buildingId]) {
            this.progressMap[buildingId].status = 'cancelled';
            this.progressMap[buildingId].percentComplete = 0;
            this.emitUpdate(buildingId);
            // TODO: Resource refund logic here
        }
    };

    handleTick = (_event: TickEvent) => {
        const now = Date.now();
        Object.values(this.progressMap).forEach(progress => {
            if (progress.status === 'in-progress') {
                const elapsed = now - progress.startTime;
                progress.percentComplete = Math.min(1, elapsed / progress.duration);
                if (progress.percentComplete >= 1) {
                    progress.status = 'complete';
                }
                this.emitUpdate(progress.buildingId);
            }
        });
    };

    emitUpdate(buildingId: string) {
        const progress = this.progressMap[buildingId];
        const event: ConstructionProgressEvent = {
            type: 'construction:progress',
            buildingId,
            progress,
            timestamp: Date.now(),
            source: 'ConstructionProgressSystem',
        };
        this.eventBus.emit('construction:progress', event);
    }

    getProgress(buildingId: string): ConstructionProgress | undefined {
        return this.progressMap[buildingId];
    }

    // For multiplayer: sync state from server
    syncProgress(progressList: ConstructionProgress[]) {
        progressList.forEach(progress => {
            this.progressMap[progress.buildingId] = progress;
            this.emitUpdate(progress.buildingId);
        });
    }
}

export default ConstructionProgressSystem; 