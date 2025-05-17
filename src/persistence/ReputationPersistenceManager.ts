// import { Database } from '../types/database';
import { FactionReputationData } from '../models/FactionReputation';
import { Logger } from '../utils/logger';

// Minimal Database interface for local use
interface Database {
    execute(sql: string, params?: any[]): Promise<void>;
    query(sql: string, params?: any[]): Promise<any[]>;
}

export class ReputationPersistenceManager {
    private database: Database;
    private logger: Logger;

    constructor(database: Database) {
        this.database = database;
        this.logger = Logger.getInstance().child('ReputationPersistenceManager');
        this.initializeTables().catch(error => {
            this.logger.error('Failed to initialize reputation tables', { error });
            throw error;
        });
    }

    private async initializeTables(): Promise<void> {
        await this.database.execute(`
            CREATE TABLE IF NOT EXISTS reputations (
                playerId TEXT NOT NULL,
                factionId TEXT NOT NULL,
                moral INTEGER NOT NULL,
                fame INTEGER NOT NULL,
                lastUpdated TIMESTAMP NOT NULL,
                legendaryAchievements JSON,
                PRIMARY KEY (playerId, factionId)
            )
        `);
        this.logger.info('Reputation table initialized');
    }

    public async saveReputation(playerId: string, data: FactionReputationData): Promise<void> {
        await this.database.execute(`
            INSERT OR REPLACE INTO reputations (playerId, factionId, moral, fame, lastUpdated, legendaryAchievements)
            VALUES (?, ?, ?, ?, ?, ?)
        `, [
            playerId,
            data.factionId,
            data.moral,
            data.fame,
            data.lastUpdated.toISOString(),
            JSON.stringify(data.legendaryAchievements || [])
        ]);
        this.logger.info('Saved reputation', { playerId, factionId: data.factionId });
    }

    public async loadReputations(playerId: string): Promise<FactionReputationData[]> {
        const rows = await this.database.query(`
            SELECT * FROM reputations WHERE playerId = ?
        `, [playerId]);
        return rows.map((row: any) => ({
            factionId: row.factionId,
            moral: row.moral,
            fame: row.fame,
            lastUpdated: new Date(row.lastUpdated),
            legendaryAchievements: JSON.parse(row.legendaryAchievements || '[]')
        }));
    }
} 