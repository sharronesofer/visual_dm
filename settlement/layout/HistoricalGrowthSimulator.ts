import { Settlement } from '../Settlement';
import { LayoutPatternResult, ILayoutPatternGenerator } from './GridLayoutGenerator';
import { PatternBlender } from './PatternBlender';

export interface GrowthPhase {
    generator: ILayoutPatternGenerator;
    weight: number;
}

export class HistoricalGrowthSimulator {
    static simulateGrowth(
        settlement: Settlement,
        phases: GrowthPhase[]
    ): LayoutPatternResult {
        if (phases.length === 0) {
            throw new Error('No growth phases provided');
        }
        const patterns: LayoutPatternResult[] = [];
        const weights: number[] = [];
        for (const phase of phases) {
            patterns.push(phase.generator.generate(settlement));
            weights.push(phase.weight);
        }
        return PatternBlender.blend(patterns, weights);
    }
} 