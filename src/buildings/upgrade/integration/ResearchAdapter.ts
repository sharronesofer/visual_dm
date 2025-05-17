export interface IResearchSystem {
    hasTechnology(playerId: string, tech: string): Promise<boolean>;
    unlockTechnology(playerId: string, tech: string): Promise<void>;
}

export class MockResearchSystem implements IResearchSystem {
    private playerTechs: Record<string, Set<string>> = {};

    setPlayerTechs(playerId: string, techs: string[]) {
        this.playerTechs[playerId] = new Set(techs);
    }

    async hasTechnology(playerId: string, tech: string): Promise<boolean> {
        return this.playerTechs[playerId]?.has(tech) ?? false;
    }

    async unlockTechnology(playerId: string, tech: string): Promise<void> {
        if (!this.playerTechs[playerId]) this.playerTechs[playerId] = new Set();
        this.playerTechs[playerId].add(tech);
    }
} 