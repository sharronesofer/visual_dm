import { FactionReputation, FactionReputationData } from '../models/FactionReputation';
import { Logger } from '../utils/logger';

export class ReputationManager {
    private static instance: ReputationManager;
    private reputations: Map<string, FactionReputation>;
    private logger: Logger;

    private constructor() {
        this.reputations = new Map();
        this.logger = Logger.getInstance().child('ReputationManager');
    }

    public static getInstance(): ReputationManager {
        if (!ReputationManager.instance) {
            ReputationManager.instance = new ReputationManager();
        }
        return ReputationManager.instance;
    }

    public getReputation(factionId: string): FactionReputation | undefined {
        return this.reputations.get(factionId);
    }

    public setReputation(factionId: string, data: FactionReputationData): void {
        this.reputations.set(factionId, new FactionReputation(data));
        this.logger.info(`Set reputation for faction ${factionId}`, data);
    }

    public modifyMoral(factionId: string, delta: number): void {
        const rep = this.reputations.get(factionId);
        if (rep) {
            rep.moral += delta;
            this.logger.info(`Modified moral for faction ${factionId} by ${delta}`);
        }
    }

    public modifyFame(factionId: string, delta: number): void {
        const rep = this.reputations.get(factionId);
        if (rep) {
            rep.fame += delta;
            this.logger.info(`Modified fame for faction ${factionId} by ${delta}`);
        }
    }

    public getAllReputations(): FactionReputation[] {
        return Array.from(this.reputations.values());
    }

    public loadReputations(data: FactionReputationData[]): void {
        this.reputations.clear();
        for (const repData of data) {
            this.reputations.set(repData.factionId, new FactionReputation(repData));
        }
        this.logger.info('Loaded reputations from data', { count: data.length });
    }

    public saveReputations(): FactionReputationData[] {
        return Array.from(this.reputations.values()).map(rep => rep.toJSON());
    }

    public reset(): void {
        this.reputations.clear();
        this.logger.info('Reset all reputations');
    }
} 