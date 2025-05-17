import { IResearchSystem } from './integration/ResearchAdapter';

export class TechnologyRequirementChecker {
    constructor(private research: IResearchSystem) { }

    async hasTech(playerId: string, tech: string): Promise<boolean> {
        return this.research.hasTechnology(playerId, tech);
    }

    async unlockTech(playerId: string, tech: string): Promise<void> {
        await this.research.unlockTechnology(playerId, tech);
    }
} 