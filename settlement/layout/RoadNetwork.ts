import { LayoutPatternResult } from './GridLayoutGenerator';
import { Settlement, SettlementType } from '../Settlement';

export type RoadType = 'main' | 'side' | 'alley';

export interface RoadNode {
    x: number;
    y: number;
    id: string;
}

export interface RoadEdge {
    from: string;
    to: string;
    type: RoadType;
    width: number;
}

export class RoadNetwork {
    nodes: Map<string, RoadNode> = new Map();
    edges: RoadEdge[] = [];
    settlement: Settlement;
    pattern: LayoutPatternResult;

    constructor(pattern: LayoutPatternResult, settlement: Settlement) {
        this.pattern = pattern;
        this.settlement = settlement;
        this.buildNetwork();
    }

    private buildNetwork() {
        // Add main roads from pattern pathways
        for (const p of this.pattern.pathways) {
            const id = `${p.x},${p.y}`;
            if (!this.nodes.has(id)) {
                this.nodes.set(id, { x: p.x, y: p.y, id });
            }
        }
        // Connect adjacent main road nodes
        for (const node of this.nodes.values()) {
            for (const dx of [-1, 0, 1]) {
                for (const dy of [-1, 0, 1]) {
                    if (Math.abs(dx) + Math.abs(dy) !== 1) continue; // Only cardinal directions
                    const nx = node.x + dx;
                    const ny = node.y + dy;
                    const nid = `${nx},${ny}`;
                    if (this.nodes.has(nid)) {
                        this.edges.push({ from: node.id, to: nid, type: 'main', width: this.roadWidth('main') });
                    }
                }
            }
        }
        // Add side streets and alleys based on density and settlement type
        this.addSideStreetsAndAlleys();
    }

    private addSideStreetsAndAlleys() {
        // For simplicity, add side streets between every other main road node
        if (this.settlement.type === SettlementType.CITY) {
            for (const node of this.nodes.values()) {
                for (const dx of [-2, 2]) {
                    const nx = node.x + dx;
                    const ny = node.y;
                    const nid = `${nx},${ny}`;
                    if (!this.nodes.has(nid)) {
                        this.nodes.set(nid, { x: nx, y: ny, id: nid });
                        this.edges.push({ from: node.id, to: nid, type: 'side', width: this.roadWidth('side') });
                    }
                }
                for (const dy of [-2, 2]) {
                    const nx = node.x;
                    const ny = node.y + dy;
                    const nid = `${nx},${ny}`;
                    if (!this.nodes.has(nid)) {
                        this.nodes.set(nid, { x: nx, y: ny, id: nid });
                        this.edges.push({ from: node.id, to: nid, type: 'side', width: this.roadWidth('side') });
                    }
                }
            }
        }
        // Add alleys for towns and cities
        if (this.settlement.type !== SettlementType.VILLAGE) {
            for (const node of this.nodes.values()) {
                for (const dx of [-1, 1]) {
                    for (const dy of [-1, 1]) {
                        const nx = node.x + dx;
                        const ny = node.y + dy;
                        const nid = `${nx},${ny}`;
                        if (!this.nodes.has(nid)) {
                            this.nodes.set(nid, { x: nx, y: ny, id: nid });
                            this.edges.push({ from: node.id, to: nid, type: 'alley', width: this.roadWidth('alley') });
                        }
                    }
                }
            }
        }
    }

    private roadWidth(type: RoadType): number {
        switch (type) {
            case 'main': return 4;
            case 'side': return 2;
            case 'alley': return 1;
            default: return 1;
        }
    }

    // Validate that all nodes are connected (BFS)
    isFullyConnected(): boolean {
        if (this.nodes.size === 0) return true;
        const visited = new Set<string>();
        const nodeIds = Array.from(this.nodes.keys());
        const queue: string[] = [nodeIds[0]];
        while (queue.length > 0) {
            const current = queue.shift()!;
            if (visited.has(current)) continue;
            visited.add(current);
            for (const edge of this.edges) {
                if (edge.from === current && !visited.has(edge.to)) {
                    queue.push(edge.to);
                }
                if (edge.to === current && !visited.has(edge.from)) {
                    queue.push(edge.from);
                }
            }
        }
        return visited.size === this.nodes.size;
    }
} 