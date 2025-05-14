import { GroupResourceSystem, Resource, Territory } from '../../systems/npc/GroupResourceSystem';
import { QuestState, QuestTemplate, QuestCondition, QuestObjective, QuestType } from '../types';
import { GroupManager } from '../../systems/npc/GroupManager';
import { Group } from '../../types/npc/group';

/**
 * Handles integration between the quest system and group resources/territories
 */
export class GroupQuestIntegrator {
  constructor(
    private groupManager: GroupManager,
    private groupResourceSystem: GroupResourceSystem
  ) {}

  /**
   * Create resource-based quest conditions
   */
  createResourceCondition(
    resourceType: string,
    quantity: number,
    groupId?: string
  ): QuestCondition {
    return {
      type: 'group_resource',
      parameters: {
        resourceType,
        quantity,
        groupId
      },
      description: `Acquire ${quantity} ${resourceType}${groupId ? ' for group ' + groupId : ''}`,
      evaluate: (questState: QuestState) => {
        if (!groupId) {
          // Check if any group has the required resources
          return Array.from(this.groupManager.getAllGroups()).some(group => {
            const resources = this.groupResourceSystem.getGroupResources(group.id);
            return this.hasRequiredResources(resources, resourceType, quantity);
          });
        }

        // Check specific group's resources
        const resources = this.groupResourceSystem.getGroupResources(groupId);
        return this.hasRequiredResources(resources, resourceType, quantity);
      }
    };
  }

  /**
   * Create territory-based quest conditions
   */
  createTerritoryCondition(
    territoryId: string,
    controlType: 'control' | 'contest',
    groupId?: string
  ): QuestCondition {
    return {
      type: 'group_territory',
      parameters: {
        territoryId,
        controlType,
        groupId
      },
      description: `${controlType === 'control' ? 'Control' : 'Contest'} territory ${territoryId}${groupId ? ' with group ' + groupId : ''}`,
      evaluate: (questState: QuestState) => {
        if (!groupId) {
          // Check if any group controls/contests the territory
          const territories = Array.from(this.groupResourceSystem.getTerritories().values());
          const territory = territories.find(t => t.id === territoryId) as Territory | undefined;
          return territory ? (
            controlType === 'control' 
              ? !!territory.controllingGroupId
              : territory.contestedBy.length > 0
          ) : false;
        }

        // Check specific group's territory control/contest
        return controlType === 'control'
          ? this.groupResourceSystem.getGroupTerritories(groupId).some(t => t.id === territoryId)
          : this.groupResourceSystem.getContestedTerritories(groupId).some(t => t.id === territoryId);
      }
    };
  }

  /**
   * Create a resource gathering quest template
   */
  createResourceGatheringQuest(
    resourceType: string,
    quantity: number,
    targetGroupId: string,
    difficulty: number = 1
  ): QuestTemplate {
    const group = this.groupManager.getGroup(targetGroupId);
    if (!group) {
      throw new Error(`Group ${targetGroupId} not found`);
    }

    return {
      id: `resource_gather_${resourceType}_${Date.now()}`,
      title: `Gather ${quantity} ${resourceType} for ${group.name}`,
      description: `Help ${group.name} gather resources to strengthen their position`,
      type: 'RESOURCE_GATHERING',
      questType: 'RESOURCE_GATHERING',
      status: 'PENDING',
      difficulty,
      requirements: {
        minimumLevel: Math.max(1, Math.floor(difficulty * 0.5)),
        minimumReputation: 0,
        items: [],
        abilities: []
      },
      objectives: [
        {
          id: 'gather_resources',
          description: `Gather ${quantity} ${resourceType}`,
          type: 'COLLECT',
          completed: false,
          conditions: [
            {
              type: 'group_resource',
              parameters: {
                resourceType,
                quantity,
                groupId: targetGroupId
              },
              description: `Collect ${quantity} ${resourceType} for ${group.name}`,
              evaluate: (questState: QuestState) => {
                const resources = Array.from(this.groupResourceSystem.getResources().values())
                  .filter(r => r.type === resourceType && group.resources.sharedInventory.has(r.id));
                const total = resources.reduce((sum, r) => sum + r.quantity, 0);
                return total >= quantity;
              }
            }
          ]
        }
      ],
      dialogue: [],
      rewards: {
        gold: 100 * difficulty,
        experience: 50 * difficulty,
        items: []
      }
    };
  }

  /**
   * Create a territory control quest template
   */
  createTerritoryControlQuest(
    territoryId: string,
    targetGroupId: string,
    controlType: 'control' | 'contest',
    difficulty: number = 1
  ): QuestTemplate {
    const group = this.groupManager.getGroup(targetGroupId);
    const territory = this.groupResourceSystem.getTerritories().get(territoryId);
    
    if (!group || !territory) {
      throw new Error(`Group ${targetGroupId} or territory ${territoryId} not found`);
    }

    const action = controlType === 'control' ? 'Control' : 'Contest';
    return {
      id: `territory_${controlType}_${territoryId}_${Date.now()}`,
      title: `${action} ${territory.name}`,
      description: `Help ${group.name} ${controlType} the territory of ${territory.name}`,
      type: 'TERRITORY_CONTROL',
      questType: 'TERRITORY_CONTROL',
      status: 'PENDING',
      difficulty,
      requirements: {
        minimumLevel: Math.max(1, Math.floor(difficulty * 0.75)),
        minimumReputation: controlType === 'control' ? 10 : 0,
        items: [],
        abilities: []
      },
      objectives: [
        {
          id: `${controlType}_territory`,
          description: `${action} the territory of ${territory.name}`,
          type: controlType === 'control' ? 'CONTROL' : 'CONTEST',
          completed: false,
          conditions: [
            {
              type: 'territory_control',
              parameters: {
                territoryId,
                controlType,
                groupId: targetGroupId
              },
              description: `${action} the territory of ${territory.name}`,
              evaluate: (questState: QuestState) => {
                const currentTerritory = this.groupResourceSystem.getTerritories().get(territoryId);
                if (!currentTerritory) return false;

                return controlType === 'control'
                  ? currentTerritory.controllingGroupId === targetGroupId
                  : currentTerritory.contestedBy.includes(targetGroupId);
              }
            }
          ]
        }
      ],
      dialogue: [],
      rewards: {
        gold: 200 * difficulty,
        experience: 100 * difficulty,
        items: []
      }
    };
  }

  /**
   * Check if resources meet requirements
   */
  private hasRequiredResources(
    resources: Resource[],
    resourceType: string,
    quantity: number
  ): boolean {
    return resources
      .filter(r => r.type === resourceType)
      .reduce((total, r) => total + r.quantity, 0) >= quantity;
  }
} 