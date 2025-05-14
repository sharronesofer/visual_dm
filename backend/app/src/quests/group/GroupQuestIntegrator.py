from typing import Any, Dict, List


/**
 * Handles integration between the quest system and group resources/territories
 */
class GroupQuestIntegrator {
  constructor(
    private groupManager: GroupManager,
    private groupResourceSystem: GroupResourceSystem
  ) {}
  /**
   * Create resource-based quest conditions
   */
  createResourceCondition(
    resourceType: str,
    quantity: float,
    groupId?: str
  ): QuestCondition {
    return {
      type: 'group_resource',
      parameters: Dict[str, Any],
      description: `Acquire ${quantity} ${resourceType}${groupId ? ' for group ' + groupId : ''}`,
      evaluate: (questState: QuestState) => {
        if (!groupId) {
          return Array.from(this.groupManager.getAllGroups()).some(group => {
            const resources = this.groupResourceSystem.getGroupResources(group.id)
            return this.hasRequiredResources(resources, resourceType, quantity)
          })
        }
        const resources = this.groupResourceSystem.getGroupResources(groupId)
        return this.hasRequiredResources(resources, resourceType, quantity)
      }
    }
  }
  /**
   * Create territory-based quest conditions
   */
  createTerritoryCondition(
    territoryId: str,
    controlType: 'control' | 'contest',
    groupId?: str
  ): QuestCondition {
    return {
      type: 'group_territory',
      parameters: Dict[str, Any],
      description: `${controlType === 'control' ? 'Control' : 'Contest'} territory ${territoryId}${groupId ? ' with group ' + groupId : ''}`,
      evaluate: (questState: QuestState) => {
        if (!groupId) {
          const territories = Array.from(this.groupResourceSystem.getTerritories().values())
          const territory = territories.find(t => t.id === territoryId) as Territory | undefined
          return territory ? (
            controlType === 'control' 
              ? !!territory.controllingGroupId
              : territory.contestedBy.length > 0
          ) : false
        }
        return controlType === 'control'
          ? this.groupResourceSystem.getGroupTerritories(groupId).some(t => t.id === territoryId)
          : this.groupResourceSystem.getContestedTerritories(groupId).some(t => t.id === territoryId)
      }
    }
  }
  /**
   * Create a resource gathering quest template
   */
  createResourceGatheringQuest(
    resourceType: str,
    quantity: float,
    targetGroupId: str,
    difficulty: float = 1
  ): QuestTemplate {
    const group = this.groupManager.getGroup(targetGroupId)
    if (!group) {
      throw new Error(`Group ${targetGroupId} not found`)
    }
    return {
      id: `resource_gather_${resourceType}_${Date.now()}`,
      title: `Gather ${quantity} ${resourceType} for ${group.name}`,
      description: `Help ${group.name} gather resources to strengthen their position`,
      type: 'RESOURCE_GATHERING',
      questType: 'RESOURCE_GATHERING',
      status: 'PENDING',
      difficulty,
      requirements: Dict[str, Any],
      objectives: [
        {
          id: 'gather_resources',
          description: `Gather ${quantity} ${resourceType}`,
          type: 'COLLECT',
          completed: false,
          conditions: [
            {
              type: 'group_resource',
              parameters: Dict[str, Any],
              description: `Collect ${quantity} ${resourceType} for ${group.name}`,
              evaluate: (questState: QuestState) => {
                const resources = Array.from(this.groupResourceSystem.getResources().values())
                  .filter(r => r.type === resourceType && group.resources.sharedInventory.has(r.id))
                const total = resources.reduce((sum, r) => sum + r.quantity, 0)
                return total >= quantity
              }
            }
          ]
        }
      ],
      dialogue: [],
      rewards: Dict[str, Any]
    }
  }
  /**
   * Create a territory control quest template
   */
  createTerritoryControlQuest(
    territoryId: str,
    targetGroupId: str,
    controlType: 'control' | 'contest',
    difficulty: float = 1
  ): QuestTemplate {
    const group = this.groupManager.getGroup(targetGroupId)
    const territory = this.groupResourceSystem.getTerritories().get(territoryId)
    if (!group || !territory) {
      throw new Error(`Group ${targetGroupId} or territory ${territoryId} not found`)
    }
    const action = controlType === 'control' ? 'Control' : 'Contest'
    return {
      id: `territory_${controlType}_${territoryId}_${Date.now()}`,
      title: `${action} ${territory.name}`,
      description: `Help ${group.name} ${controlType} the territory of ${territory.name}`,
      type: 'TERRITORY_CONTROL',
      questType: 'TERRITORY_CONTROL',
      status: 'PENDING',
      difficulty,
      requirements: Dict[str, Any],
      objectives: [
        {
          id: `${controlType}_territory`,
          description: `${action} the territory of ${territory.name}`,
          type: controlType === 'control' ? 'CONTROL' : 'CONTEST',
          completed: false,
          conditions: [
            {
              type: 'territory_control',
              parameters: Dict[str, Any],
              description: `${action} the territory of ${territory.name}`,
              evaluate: (questState: QuestState) => {
                const currentTerritory = this.groupResourceSystem.getTerritories().get(territoryId)
                if (!currentTerritory) return false
                return controlType === 'control'
                  ? currentTerritory.controllingGroupId === targetGroupId
                  : currentTerritory.contestedBy.includes(targetGroupId)
              }
            }
          ]
        }
      ],
      dialogue: [],
      rewards: Dict[str, Any]
    }
  }
  /**
   * Check if resources meet requirements
   */
  private hasRequiredResources(
    resources: List[Resource],
    resourceType: str,
    quantity: float
  ): bool {
    return resources
      .filter(r => r.type === resourceType)
      .reduce((total, r) => total + r.quantity, 0) >= quantity
  }
} 