import { BuildingType } from './BuildingUpgradeDefinition';

export class UpgradeDependencyGraph {
    private adjacency: Map<BuildingType, Set<BuildingType>> = new Map();

    addUpgradePath(from: BuildingType, to: BuildingType): void {
        if (!this.adjacency.has(from)) {
            this.adjacency.set(from, new Set());
        }
        this.adjacency.get(from)!.add(to);
    }

    getUpgradePaths(from: BuildingType): BuildingType[] {
        return Array.from(this.adjacency.get(from) || []);
    }

    hasUpgradePath(from: BuildingType, to: BuildingType): boolean {
        return this.adjacency.get(from)?.has(to) || false;
    }

    // Detects cycles in the upgrade graph
    hasCycle(): boolean {
        const visited = new Set<BuildingType>();
        const recStack = new Set<BuildingType>();

        const visit = (node: BuildingType): boolean => {
            if (!visited.has(node)) {
                visited.add(node);
                recStack.add(node);
                for (const neighbor of this.adjacency.get(node) || []) {
                    if (!visited.has(neighbor) && visit(neighbor)) {
                        return true;
                    } else if (recStack.has(neighbor)) {
                        return true;
                    }
                }
            }
            recStack.delete(node);
            return false;
        };

        for (const node of this.adjacency.keys()) {
            if (visit(node)) {
                return true;
            }
        }
        return false;
    }
} 