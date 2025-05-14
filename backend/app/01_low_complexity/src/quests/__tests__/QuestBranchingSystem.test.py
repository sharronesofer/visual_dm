from typing import Any, Dict



const { QuestBranchingSystem } = require('../QuestBranchingSystem')
const { MemoryManager } = require('../../systems/npc/MemoryManager')
const { FactionQuestSystem } = require('../factions/FactionQuestSystem')
const { QuestMemoryIntegrator } = require('../memory/QuestMemoryIntegrator')
const { FactionType } = require('../../types/factions/faction')
describe('QuestBranchingSystem', () => {
  let memoryManager
  let factionQuestSystem
  let questMemoryIntegrator
  let system
  beforeEach(() => {
    memoryManager = {
      queryMemories: jest.fn().mockResolvedValue([])
    }
    factionQuestSystem = {
      getFactionStanding: jest.fn().mockResolvedValue(50),
      modifyFactionStanding: jest.fn()
    }
    questMemoryIntegrator = {
      recordQuestMemory: jest.fn().mockResolvedValue(undefined),
      getRelevantQuestMemories: jest.fn().mockResolvedValue([])
    }
    system = new QuestBranchingSystem(memoryManager, factionQuestSystem, questMemoryIntegrator)
  })
  it('evaluates branches and returns those with positive weight and met requirements', async () => {
    const stage = {
      id: 'stage1',
      title: 'Test Stage',
      description: '',
      branches: [
        {
          id: 'b1',
          condition: Dict[str, Any],
          nextStageId: 'stage2',
          description: 'Branch 1',
          factionRequirements: Dict[str, Any]
        },
        {
          id: 'b2',
          condition: Dict[str, Any],
          nextStageId: 'stage3',
          description: 'Branch 2',
          factionRequirements: Dict[str, Any]
        }
      ],
      objectives: []
    }
    factionQuestSystem.getFactionStanding.mockImplementation((playerId, faction) => {
      if (faction === FactionType.MERCHANTS) return Promise.resolve(50)
      return Promise.resolve(0)
    })
    const branches = await system.evaluateBranches('q1', stage, 'player1', system.defaultOptions)
    expect(branches.map(b => b.id)).toContain('b1')
    expect(branches.map(b => b.id)).not.toContain('b2')
  })
  it('transitions to the correct next stage id and records memory', async () => {
    const stage = {
      id: 'stage1',
      title: 'Test Stage',
      description: '',
      branches: [
        {
          id: 'b1',
          condition: Dict[str, Any],
          nextStageId: 'stage2',
          description: 'Branch 1'
        }
      ],
      objectives: []
    }
    const branch = stage.branches[0]
    const nextStageId = await system.transitionQuestStage('q1', stage, branch, 'player1')
    expect(nextStageId).toBe('stage2')
    expect(questMemoryIntegrator.recordQuestMemory).toHaveBeenCalled()
  })
  it('applies consequences when transitioning', async () => {
    const stage = {
      id: 'stage1',
      title: 'Test Stage',
      description: '',
      branches: [
        {
          id: 'b1',
          condition: Dict[str, Any],
          nextStageId: 'stage2',
          description: 'Branch 1',
          consequences: [
            { type: 'FACTION_STANDING', target: FactionType.MERCHANTS, value: 10, description: 'Gain standing' }
          ]
        }
      ],
      objectives: []
    }
    const branch = stage.branches[0]
    await system.transitionQuestStage('q1', stage, branch, 'player1')
    expect(factionQuestSystem.modifyFactionStanding).toHaveBeenCalledWith('player1', FactionType.MERCHANTS, 10)
  })
}) 