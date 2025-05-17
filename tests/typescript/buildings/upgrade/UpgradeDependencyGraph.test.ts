import { UpgradeDependencyGraph } from '../../../../src/buildings/upgrade/UpgradeDependencyGraph';
import { expect } from 'chai';

describe('UpgradeDependencyGraph', () => {
    it('should add and retrieve upgrade paths', () => {
        const graph = new UpgradeDependencyGraph();
        graph.addUpgradePath('Hut', 'House');
        graph.addUpgradePath('House', 'Villa');
        expect(graph.getUpgradePaths('Hut')).to.deep.equal(['House']);
        expect(graph.getUpgradePaths('House')).to.deep.equal(['Villa']);
        expect(graph.getUpgradePaths('Villa')).to.deep.equal([]);
    });

    it('should check for the existence of an upgrade path', () => {
        const graph = new UpgradeDependencyGraph();
        graph.addUpgradePath('Hut', 'House');
        expect(graph.hasUpgradePath('Hut', 'House')).to.be.true;
        expect(graph.hasUpgradePath('House', 'Hut')).to.be.false;
    });

    it('should detect cycles in the upgrade graph', () => {
        const graph = new UpgradeDependencyGraph();
        graph.addUpgradePath('A', 'B');
        graph.addUpgradePath('B', 'C');
        expect(graph.hasCycle()).to.be.false;
        graph.addUpgradePath('C', 'A');
        expect(graph.hasCycle()).to.be.true;
    });
}); 