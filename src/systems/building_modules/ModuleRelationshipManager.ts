import { BuildingModule } from './BuildingModule';

export type RelationshipType = 'supports' | 'contains' | 'protects' | 'requires';

export interface IModuleRelationship {
    type: RelationshipType;
    from: string; // moduleId
    to: string;   // moduleId
    strength?: number; // For supports/protects
    metadata?: Record<string, any>;
}

export class ModuleGroup {
    id: string;
    moduleIds: Set<string> = new Set();
    constructor(id: string, moduleIds: string[] = []) {
        this.id = id;
        for (const m of moduleIds) this.moduleIds.add(m);
    }
    add(moduleId: string) { this.moduleIds.add(moduleId); }
    remove(moduleId: string) { this.moduleIds.delete(moduleId); }
    has(moduleId: string) { return this.moduleIds.has(moduleId); }
    getAll(): string[] { return Array.from(this.moduleIds); }
}

export class ModuleRelationshipManager {
    private relationships: IModuleRelationship[] = [];
    private groups: Map<string, ModuleGroup> = new Map();
    private moduleMap: Map<string, BuildingModule> = new Map();

    registerModule(module: BuildingModule) {
        this.moduleMap.set(module.moduleId, module);
    }

    unregisterModule(moduleId: string) {
        this.moduleMap.delete(moduleId);
        this.relationships = this.relationships.filter(r => r.from !== moduleId && r.to !== moduleId);
        for (const group of this.groups.values()) {
            group.remove(moduleId);
        }
    }

    addRelationship(rel: IModuleRelationship) {
        this.relationships.push(rel);
    }

    removeRelationship(from: string, to: string, type?: RelationshipType) {
        this.relationships = this.relationships.filter(r =>
            !(r.from === from && r.to === to && (!type || r.type === type))
        );
    }

    getRelationships(moduleId: string, type?: RelationshipType): IModuleRelationship[] {
        return this.relationships.filter(r =>
            (r.from === moduleId || r.to === moduleId) && (!type || r.type === type)
        );
    }

    addGroup(group: ModuleGroup) {
        this.groups.set(group.id, group);
    }

    getGroup(groupId: string): ModuleGroup | undefined {
        return this.groups.get(groupId);
    }

    // Cascading damage: propagate damage from one module to related modules
    propagateDamage(moduleId: string, amount: number, cause: string = 'cascade') {
        // Example: if a wall supports a roof, and wall is destroyed, roof takes damage
        const outgoing = this.relationships.filter(r => r.from === moduleId && r.type === 'supports');
        for (const rel of outgoing) {
            const target = this.moduleMap.get(rel.to);
            if (target) {
                // Damage is scaled by relationship strength (default 1)
                const scaled = amount * (rel.strength ?? 1);
                target.applyDamage(scaled);
                // Recursively propagate if needed
                if (target.health <= 0) {
                    this.propagateDamage(target.moduleId, scaled, 'cascade');
                }
            }
        }
    }

    // Validation: ensure all required relationships are satisfied
    validateIntegrity(): { valid: boolean; errors: string[] } {
        const errors: string[] = [];
        // Example: every roof must be supported by at least one wall
        for (const rel of this.relationships) {
            if (rel.type === 'supports') {
                const from = this.moduleMap.get(rel.from);
                const to = this.moduleMap.get(rel.to);
                if (!from || !to) {
                    errors.push(`Invalid relationship: ${rel.from} or ${rel.to} not found`);
                } else if (from.health <= 0 && to.health > 0) {
                    errors.push(`Module ${rel.to} is unsupported due to ${rel.from} being destroyed`);
                }
            }
        }
        return { valid: errors.length === 0, errors };
    }

    // Hierarchy traversal
    getChildren(parentId: string): string[] {
        return this.relationships.filter(r => r.type === 'contains' && r.from === parentId).map(r => r.to);
    }

    getParent(childId: string): string | undefined {
        const rel = this.relationships.find(r => r.type === 'contains' && r.to === childId);
        return rel?.from;
    }

    // Group operations
    damageGroup(groupId: string, amount: number) {
        const group = this.groups.get(groupId);
        if (group) {
            for (const moduleId of group.getAll()) {
                const mod = this.moduleMap.get(moduleId);
                if (mod) mod.applyDamage(amount);
            }
        }
    }

    repairGroup(groupId: string, amount: number) {
        const group = this.groups.get(groupId);
        if (group) {
            for (const moduleId of group.getAll()) {
                const mod = this.moduleMap.get(moduleId);
                if (mod) mod.repair(amount);
            }
        }
    }
} 