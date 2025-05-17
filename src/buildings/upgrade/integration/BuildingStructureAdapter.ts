export interface IBuildingStructureSystem {
    applyUpgrade(buildingId: string, upgradeType: string): Promise<void>;
    applyDowngrade(buildingId: string, downgradeType: string): Promise<void>;
}

export class MockBuildingStructureSystem implements IBuildingStructureSystem {
    private upgrades: Record<string, string[]> = {};
    private downgrades: Record<string, string[]> = {};

    async applyUpgrade(buildingId: string, upgradeType: string): Promise<void> {
        if (!this.upgrades[buildingId]) this.upgrades[buildingId] = [];
        this.upgrades[buildingId].push(upgradeType);
    }

    async applyDowngrade(buildingId: string, downgradeType: string): Promise<void> {
        if (!this.downgrades[buildingId]) this.downgrades[buildingId] = [];
        this.downgrades[buildingId].push(downgradeType);
    }

    getUpgrades(buildingId: string): string[] {
        return this.upgrades[buildingId] || [];
    }

    getDowngrades(buildingId: string): string[] {
        return this.downgrades[buildingId] || [];
    }
} 