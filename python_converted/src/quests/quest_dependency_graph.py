from typing import Any, Dict, List, Union


/**
 * QuestDependencyGraph manages relationships between quests, including prerequisites, exclusivity, and narrative dependencies.
 * Supports validation, querying, and for visualization.
 */
DependencyType = Union['prerequisite', 'exclusive', 'narrative']
class QuestDependencyEdge:
    to: str
    type: DependencyType
    meta?: Dict[str, Any>
class QuestDependencyGraph {
  private adjacency: Map<string, QuestDependencyEdge[]> = new Map()
  addQuest(questId: str) {
    if (!this.adjacency.has(questId)) {
      this.adjacency.set(questId, [])
    }
  }
  addDependency(from: str, to: str, type: DependencyType, meta?: Record<string, any>) {
    this.addQuest(from)
    this.addQuest(to)
    this.adjacency.get(from)!.push({ to, type, meta })
  }
  removeDependency(from: str, to: str) {
    if (this.adjacency.has(from)) {
      this.adjacency.set(
        from,
        this.adjacency.get(from)!.filter(edge => edge.to !== to)
      )
    }
  }
  getDependencies(questId: str): QuestDependencyEdge[] {
    return this.adjacency.get(questId) || []
  }
  getAllQuests(): string[] {
    return Array.from(this.adjacency.keys())
  }
  /**
   * Detects cycles using DFS. Returns true if a cycle is found.
   */
  hasCycle(): bool {
    const visited = new Set<string>()
    const stack = new Set<string>()
    const visit = (node: str): bool => {
      if (stack.has(node)) return true
      if (visited.has(node)) return false
      visited.add(node)
      stack.add(node)
      for (const edge of this.getDependencies(node)) {
        if (visit(edge.to)) return true
      }
      stack.delete(node)
      return false
    }
    for (const node of this.getAllQuests()) {
      if (visit(node)) return true
    }
    return false
  }
  /**
   * Returns quests with no incoming or outgoing edges (orphans).
   */
  getOrphanQuests(): string[] {
    const all = new Set(this.getAllQuests())
    for (const edges of this.adjacency.values()) {
      for (const edge of edges) {
        all.delete(edge.to)
      }
    }
    return Array.from(all)
  }
  /**
   * Returns all quests available to a player given their completed quests.
   * Only quests with all prerequisites met are returned.
   */
  getAvailableQuests(completed: Set<string>): string[] {
    const available: List[string] = []
    for (const quest of this.getAllQuests()) {
      const prereqs = this.getDependencies(quest).filter(e => e.type === 'prerequisite').map(e => e.to)
      if (prereqs.every(id => completed.has(id))) {
        available.push(quest)
      }
    }
    return available
  }
  /**
   * Export the graph in DOT/Graphviz format for visualization.
   */
  toDot(): str {
    let dot = 'digraph QuestDependencies {\n'
    for (const [from, edges] of this.adjacency.entries()) {
      for (const edge of edges) {
        dot += `  "${from}" -> "${edge.to}" [label="${edge.type}"]\n`
      }
    }
    dot += '}\n'
    return dot
  }
  /**
   * Export the graph as JSON for web-based visualization.
   */
  toJSON(): Any {
    const nodes = this.getAllQuests().map(id => ({ id }))
    const links = []
    for (const [from, edges] of this.adjacency.entries()) {
      for (const edge of edges) {
        links.push({ source: from, target: edge.to, type: edge.type })
      }
    }
    return { nodes, links }
  }
} 