// Modifier interfaces and base classes
export interface Modifier {
    id: string;
    type: string;
    target: string; // e.g., 'deteriorationRate', 'repairRate'
    magnitude: number;
    duration?: number; // in ticks or ms, undefined = permanent
    priority?: number;
    apply(base: number): number;
}

export class AdditiveModifier implements Modifier {
    id: string;
    type: string;
    target: string;
    magnitude: number;
    duration?: number;
    priority?: number;
    constructor(id: string, target: string, magnitude: number, duration?: number, priority: number = 0) {
        this.id = id;
        this.type = 'additive';
        this.target = target;
        this.magnitude = magnitude;
        this.duration = duration;
        this.priority = priority;
    }
    apply(base: number): number {
        return base + this.magnitude;
    }
}

export class MultiplicativeModifier implements Modifier {
    id: string;
    type: string;
    target: string;
    magnitude: number;
    duration?: number;
    priority?: number;
    constructor(id: string, target: string, magnitude: number, duration?: number, priority: number = 0) {
        this.id = id;
        this.type = 'multiplicative';
        this.target = target;
        this.magnitude = magnitude;
        this.duration = duration;
        this.priority = priority;
    }
    apply(base: number): number {
        return base * this.magnitude;
    }
}

// Example: Material, Environmental, Technology Modifiers
export class MaterialModifier extends MultiplicativeModifier {
    constructor(id: string, target: string, magnitude: number, duration?: number) {
        super(id, target, magnitude, duration, 10); // High priority for material
        this.type = 'material';
    }
}

export class EnvironmentalModifier extends AdditiveModifier {
    constructor(id: string, target: string, magnitude: number, duration?: number) {
        super(id, target, magnitude, duration, 5); // Medium priority for environment
        this.type = 'environmental';
    }
}

export class TechnologyModifier extends MultiplicativeModifier {
    constructor(id: string, target: string, magnitude: number, duration?: number) {
        super(id, target, magnitude, duration, 1); // Low priority for tech
        this.type = 'technology';
    }
}

// ModifierStack for stacking and ordering
export class ModifierStack {
    private modifiers: Modifier[] = [];

    add(modifier: Modifier) {
        // Prevent duplicate IDs
        if (!this.modifiers.find(m => m.id === modifier.id)) {
            this.modifiers.push(modifier);
            this.modifiers.sort((a, b) => (b.priority || 0) - (a.priority || 0));
        }
    }

    remove(modifierId: string) {
        this.modifiers = this.modifiers.filter(m => m.id !== modifierId);
    }

    get(target: string): Modifier[] {
        return this.modifiers.filter(m => m.target === target);
    }

    applyAll(base: number, target: string): number {
        let value = base;
        // Apply additive first, then multiplicative
        for (const m of this.get(target).filter(m => m.type === 'additive' || m.type === 'environmental')) {
            value = m.apply(value);
        }
        for (const m of this.get(target).filter(m => m.type === 'multiplicative' || m.type === 'material' || m.type === 'technology')) {
            value = m.apply(value);
        }
        return value;
    }
}

// ModifierRegistry for global management
export class ModifierRegistry {
    private static instance: ModifierRegistry;
    private stacks: Map<string, ModifierStack> = new Map(); // key: moduleId

    private constructor() { }

    static getInstance(): ModifierRegistry {
        if (!ModifierRegistry.instance) {
            ModifierRegistry.instance = new ModifierRegistry();
        }
        return ModifierRegistry.instance;
    }

    getStack(moduleId: string): ModifierStack {
        if (!this.stacks.has(moduleId)) {
            this.stacks.set(moduleId, new ModifierStack());
        }
        return this.stacks.get(moduleId)!;
    }

    addModifier(moduleId: string, modifier: Modifier) {
        this.getStack(moduleId).add(modifier);
    }

    removeModifier(moduleId: string, modifierId: string) {
        this.getStack(moduleId).remove(modifierId);
    }

    getEffectiveRate(moduleId: string, base: number, target: string): number {
        return this.getStack(moduleId).applyAll(base, target);
    }
} 