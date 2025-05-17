export interface ResourceTransactionLogEntry {
    buildingId: string;
    playerId: string;
    originalMaterials: Record<string, number>;
    refundedMaterials: Record<string, number>;
    timestamp: number;
    reason: string;
    destructionType: string;
}

export class ResourceTransactionLogger {
    private logs: ResourceTransactionLogEntry[] = [];

    logRefund(entry: ResourceTransactionLogEntry): void {
        this.logs.push(entry);
        // In a real system, persist to DB or external log
        // For now, just log to console
        console.log('[ResourceTransactionLogger] Refund:', entry);
    }

    getLogs(): ResourceTransactionLogEntry[] {
        return this.logs;
    }
} 