from typing import Any


describe('QuestDependencyGraph', () => {
  let graph: QuestDependencyGraph
  beforeEach(() => {
    graph = new QuestDependencyGraph()
  })
  it('adds and removes dependencies', () => {
    graph.addQuest('A')
    graph.addQuest('B')
    graph.addDependency('A', 'B', 'prerequisite')
    expect(graph.getDependencies('A').length).toBe(1)
    graph.removeDependency('A', 'B')
    expect(graph.getDependencies('A').length).toBe(0)
  })
  it('detects cycles', () => {
    graph.addDependency('A', 'B', 'prerequisite')
    graph.addDependency('B', 'C', 'prerequisite')
    graph.addDependency('C', 'A', 'prerequisite')
    expect(graph.hasCycle()).toBe(true)
  })
  it('detects no cycles in acyclic graph', () => {
    graph.addDependency('A', 'B', 'prerequisite')
    graph.addDependency('B', 'C', 'prerequisite')
    expect(graph.hasCycle()).toBe(false)
  })
  it('finds orphan quests', () => {
    graph.addQuest('A')
    graph.addQuest('B')
    graph.addDependency('A', 'B', 'prerequisite')
    graph.addQuest('C')
    expect(graph.getOrphanQuests()).toContain('C')
  })
  it('returns available quests based on completed set', () => {
    graph.addDependency('A', 'B', 'prerequisite')
    graph.addDependency('B', 'C', 'prerequisite')
    const completed = new Set(['A', 'B'])
    expect(graph.getAvailableQuests(completed)).toContain('C')
    expect(graph.getAvailableQuests(completed)).not.toContain('A')
  })
  it('exports DOT format', () => {
    graph.addDependency('A', 'B', 'prerequisite')
    const dot = graph.toDot()
    expect(dot).toContain('digraph QuestDependencies')
    expect(dot).toContain('"A" -> "B" [label="prerequisite"]')
  })
  it('exports JSON format', () => {
    graph.addDependency('A', 'B', 'prerequisite')
    const json = graph.toJSON()
    expect(Array.isArray(json.nodes)).toBe(true)
    expect(Array.isArray(json.links)).toBe(true)
    expect(json.links[0]).toMatchObject({ source: 'A', target: 'B', type: 'prerequisite' })
  })
}) 