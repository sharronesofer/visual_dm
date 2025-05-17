import { CombatAction } from './CombatAction';

export class ActionDependency {
    /**
     * Topological sort for dependency-aware execution order.
     * Throws if a cycle is detected.
     */
    static topologicalSort(actions: CombatAction[]): CombatAction[] {
        const sorted: CombatAction[] = [];
        const visited = new Set<string>();
        const temp = new Set<string>();

        function visit(action: CombatAction) {
            if (temp.has(action.id)) throw new Error('Cycle detected in action dependencies');
            if (!visited.has(action.id)) {
                temp.add(action.id);
                for (const prereq of action.getPrerequisites()) {
                    visit(prereq);
                }
                temp.delete(action.id);
                visited.add(action.id);
                sorted.push(action);
            }
        }

        for (const action of actions) {
            visit(action);
        }
        return sorted;
    }

    /**
     * Validate that all dependencies are present in the action list.
     */
    static validateDependencies(actions: CombatAction[]): boolean {
        const ids = new Set(actions.map(a => a.id));
        for (const action of actions) {
            for (const prereq of action.getPrerequisites()) {
                if (!ids.has(prereq.id)) return false;
            }
        }
        return true;
    }
} 