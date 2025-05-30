from typing import Any, Dict, List


jest.mock('../../../systems/npc/MemoryManager')
jest.mock('../../consequences/ConsequenceSystem')
jest.mock('../../factions/FactionQuestSystem')
describe('QuestMemoryIntegrator', () => {
  let memoryManager: jest.Mocked<MemoryManager>
  let consequenceSystem: jest.Mocked<ConsequenceSystem>
  let factionQuestSystem: jest.Mocked<FactionQuestSystem>
  let integrator: QuestMemoryIntegrator
  const mockNpcId = 'npc-1'
  const mockPlayerId = 'player-1'
  beforeEach(() => {
    const mockWorldState: WorldState = {
      factionStandings: {},
      npcRelationships: {},
      environmentalConditions: {},
      availableQuests: new Set<string>(),
      economyFactors: Dict[str, Any] },
      activeEffects: [],
      customState: {}
    }
    const mockFactionConfig: FactionQuestConfig = {
      reputationGainRate: 10,
      reputationLossRate: 5,
      tierThresholds: [0, 25, 50, 75, 100],
      competingQuestProbability: 0.3,
      mutuallyExclusiveThreshold: 0.7,
      minimumStandingForSpecialQuests: 50
    }
    memoryManager = new MemoryManager() as jest.Mocked<MemoryManager>
    consequenceSystem = new ConsequenceSystem(mockWorldState) as jest.Mocked<ConsequenceSystem>
    factionQuestSystem = new FactionQuestSystem(
      mockFactionConfig,
      consequenceSystem
    ) as jest.Mocked<FactionQuestSystem>
    integrator = new QuestMemoryIntegrator(
      memoryManager,
      consequenceSystem,
      factionQuestSystem
    )
  })
  describe('recordQuestMemory', () => {
    it('should create memory events for NPCs involved in the quest', async () => {
      const questEvent: QuestEvent = {
        questId: 'quest-1',
        type: QuestType.FACTION,
        status: QuestStatus.COMPLETED,
        playerId: mockPlayerId,
        involvedNpcIds: [mockNpcId],
        outcome: QuestStatus.COMPLETED,
        description: 'Test quest completion'
      }
      const context = {
        playerChoices: ['diplomatic_solution'],
        factionImpact: new Map([[FactionType.MERCHANTS, 10]])
      }
      await integrator.recordQuestMemory(mockNpcId, questEvent, context)
      expect(memoryManager.addMemory).toHaveBeenCalledWith(
        mockNpcId,
        expect.objectContaining({
          type: MemoryEventType.QUEST,
          importance: expect.any(Number),
          details: expect.objectContaining({
            questId: questEvent.questId,
            questType: questEvent.type,
            outcome: questEvent.outcome,
            description: questEvent.description,
            emotionalImpact: expect.any(Number),
            playerActions: ['diplomatic_solution']
          })
        })
      )
    })
    it('should handle faction-specific quest events', async () => {
      const questEvent: QuestEvent = {
        questId: 'quest-2',
        type: QuestType.FACTION,
        status: QuestStatus.COMPLETED,
        playerId: mockPlayerId,
        involvedNpcIds: [mockNpcId],
        outcome: QuestStatus.COMPLETED,
        factionId: FactionType.MERCHANTS,
        description: 'Test faction quest completion'
      }
      const context = {
        playerChoices: ['honorable_choice'],
        factionImpact: new Map([
          [FactionType.MERCHANTS, 15],
          [FactionType.WARRIORS, -5]
        ])
      }
      await integrator.recordQuestMemory(mockNpcId, questEvent, context)
      expect(memoryManager.addMemory).toHaveBeenCalledWith(
        mockNpcId,
        expect.objectContaining({
          type: MemoryEventType.QUEST,
          details: expect.objectContaining({
            factionImpact: Dict[str, Any],
            description: questEvent.description,
            emotionalImpact: expect.any(Number),
            playerActions: ['honorable_choice']
          })
        })
      )
    })
    it('should calculate memory importance based on quest outcome and context', async () => {
      const questEvent: QuestEvent = {
        questId: 'quest-3',
        type: QuestType.MAJOR,
        status: QuestStatus.FAILED,
        playerId: mockPlayerId,
        involvedNpcIds: [mockNpcId],
        outcome: QuestStatus.FAILED,
        description: 'Test quest failure'
      }
      const context = {
        playerChoices: ['risky_attempt', 'noble_sacrifice'],
        emotionalSignificance: 0.8
      }
      await integrator.recordQuestMemory(mockNpcId, questEvent, context)
      expect(memoryManager.addMemory).toHaveBeenCalledWith(
        mockNpcId,
        expect.objectContaining({
          importance: expect.any(Number),
          details: expect.objectContaining({
            emotionalImpact: 0.8,
            description: questEvent.description,
            playerActions: ['risky_attempt', 'noble_sacrifice']
          })
        })
      )
    })
  })
  describe('getRelevantQuestMemories', () => {
    it('should retrieve quest-related memories for an NPC', async () => {
      const mockMemories: List[MemoryEvent] = [{
        id: 'memory-1',
        type: MemoryEventType.QUEST,
        timestamp: Date.now(),
        importance: 0.7,
        details: Dict[str, Any],
        participants: [mockPlayerId, mockNpcId],
        tags: ['quest_faction', 'outcome_completed']
      }]
      memoryManager.queryMemories.mockResolvedValue(mockMemories)
      const memories = await integrator.getRelevantQuestMemories(mockNpcId, {
        questType: QuestType.FACTION,
        playerId: mockPlayerId
      })
      expect(memoryManager.queryMemories).toHaveBeenCalledWith(
        mockNpcId,
        expect.objectContaining({
          type: MemoryEventType.QUEST,
          participants: [mockPlayerId]
        })
      )
      expect(memories).toHaveLength(1)
      expect(memories[0].details.questId).toBe('quest-1')
    })
    it('should filter memories by importance threshold', async () => {
      const mockMemories: List[MemoryEvent] = [
        {
          id: 'memory-1',
          type: MemoryEventType.QUEST,
          timestamp: Date.now() - 1000000,
          importance: 0.3,
          details: Dict[str, Any],
          participants: [mockPlayerId, mockNpcId],
          tags: ['quest_minor', 'outcome_completed']
        },
        {
          id: 'memory-2',
          type: MemoryEventType.QUEST,
          timestamp: Date.now(),
          importance: 0.8,
          details: Dict[str, Any],
          participants: [mockPlayerId, mockNpcId],
          tags: ['quest_major', 'outcome_completed']
        }
      ]
      memoryManager.queryMemories.mockResolvedValue(mockMemories)
      const memories = await integrator.getRelevantQuestMemories(mockNpcId, {
        minImportance: 0.5
      })
      expect(memories).toHaveLength(1)
      expect(memories[0].details.questId).toBe('quest-recent')
    })
  })
  describe('modifyDialogueBasedOnMemories', () => {
    it('should modify dialogue based on relevant quest memories', async () => {
      const mockMemories: List[MemoryEvent] = [{
        id: 'memory-1',
        type: MemoryEventType.QUEST,
        timestamp: Date.now(),
        importance: 0.8,
        details: Dict[str, Any],
        participants: [mockPlayerId, mockNpcId],
        tags: ['quest_major', 'outcome_completed', 'heroic']
      }]
      memoryManager.queryMemories.mockResolvedValue(mockMemories)
      const baseDialogue = "Welcome, traveler."
      const modifiedDialogue = await integrator.modifyDialogueBasedOnMemories(
        mockNpcId,
        mockPlayerId,
        baseDialogue
      )
      expect(memoryManager.queryMemories).toHaveBeenCalledWith(
        mockNpcId,
        expect.objectContaining({
          type: MemoryEventType.QUEST,
          participants: [mockPlayerId]
        })
      )
      expect(modifiedDialogue).not.toBe(baseDialogue)
      expect(modifiedDialogue).toContain('heroic')
    })
    it('should return original dialogue when no relevant memories exist', async () => {
      memoryManager.queryMemories.mockResolvedValue([])
      const baseDialogue = "Welcome, stranger."
      const modifiedDialogue = await integrator.modifyDialogueBasedOnMemories(
        mockNpcId,
        mockPlayerId,
        baseDialogue
      )
      expect(modifiedDialogue).toBe(baseDialogue)
    })
  })
  describe('adjustNPCBehavior', () => {
    it('should calculate behavior adjustments based on quest memories', async () => {
      const mockMemories: List[MemoryEvent] = [
        {
          id: 'memory-1',
          type: MemoryEventType.QUEST,
          timestamp: Date.now(),
          importance: 0.9,
          details: Dict[str, Any],
          participants: [mockPlayerId, mockNpcId],
          tags: ['quest_major', 'outcome_completed', 'heroic']
        }
      ]
      memoryManager.queryMemories.mockResolvedValue(mockMemories)
      const adjustments = await integrator.adjustNPCBehavior(mockNpcId, mockPlayerId)
      expect(adjustments).toEqual(expect.objectContaining({
        trustModifier: expect.any(Number),
        dispositionChange: expect.any(Number),
        questAvailabilityAdjustment: expect.any(Number)
      }))
      expect(adjustments.trustModifier).toBeGreaterThan(0)
      expect(adjustments.dispositionChange).toBeGreaterThan(0)
      expect(adjustments.questAvailabilityAdjustment).toBeGreaterThan(0)
    })
    it('should handle negative quest outcomes appropriately', async () => {
      const mockMemories: List[MemoryEvent] = [
        {
          id: 'memory-2',
          type: MemoryEventType.QUEST,
          timestamp: Date.now(),
          importance: 0.7,
          details: Dict[str, Any],
          participants: [mockPlayerId, mockNpcId],
          tags: ['quest_faction', 'outcome_failed', 'negative']
        }
      ]
      memoryManager.queryMemories.mockResolvedValue(mockMemories)
      const adjustments = await integrator.adjustNPCBehavior(mockNpcId, mockPlayerId)
      expect(adjustments.trustModifier).toBeLessThan(0)
      expect(adjustments.dispositionChange).toBeLessThan(0)
      expect(adjustments.questAvailabilityAdjustment).toBeLessThan(0)
    })
  })
  describe('processQuestMemory', () => {
    it('should create memory events for NPCs involved in the quest', () => {
      const questEvent: QuestEvent = {
        questId: 'quest-1',
        type: QuestType.FACTION,
        status: QuestStatus.COMPLETED,
        playerId: mockPlayerId,
        involvedNpcIds: [mockNpcId],
        outcome: QuestStatus.COMPLETED,
        description: 'Test quest completion'
      }
      const context = {
        playerChoices: ['diplomatic_solution'],
        factionImpact: new Map([[FactionType.MERCHANTS, 10]])
      }
      integrator.recordQuestMemory(mockNpcId, questEvent, context)
      expect(memoryManager.addMemory).toHaveBeenCalledWith(
        mockNpcId,
        expect.objectContaining({
          type: MemoryEventType.QUEST,
          importance: expect.any(Number),
          details: expect.objectContaining({
            questId: questEvent.questId,
            questType: questEvent.type,
            outcome: questEvent.outcome,
            description: questEvent.description,
            emotionalImpact: expect.any(Number),
            playerActions: expect.any(Array)
          })
        })
      )
    })
    it('should handle faction-specific quest events', () => {
      const questEvent: QuestEvent = {
        questId: 'quest-2',
        type: QuestType.FACTION,
        status: QuestStatus.COMPLETED,
        playerId: mockPlayerId,
        involvedNpcIds: [mockNpcId],
        outcome: QuestStatus.COMPLETED,
        factionId: FactionType.MERCHANTS,
        description: 'Test faction quest completion'
      }
      const context = {
        playerChoices: ['honorable_choice'],
        factionImpact: new Map([
          [FactionType.MERCHANTS, 15],
          [FactionType.WARRIORS, -5]
        ])
      }
      integrator.recordQuestMemory(mockNpcId, questEvent, context)
      expect(memoryManager.addMemory).toHaveBeenCalledWith(
        mockNpcId,
        expect.objectContaining({
          type: MemoryEventType.QUEST,
          details: expect.objectContaining({
            factionImpact: Dict[str, Any],
            description: questEvent.description,
            emotionalImpact: expect.any(Number),
            playerActions: expect.any(Array)
          })
        })
      )
    })
    it('should calculate memory importance based on quest outcome and context', () => {
      const questEvent: QuestEvent = {
        questId: 'quest-3',
        type: QuestType.MAJOR,
        status: QuestStatus.FAILED,
        playerId: mockPlayerId,
        involvedNpcIds: [mockNpcId],
        outcome: QuestStatus.FAILED,
        description: 'Test quest failure'
      }
      const context = {
        playerChoices: ['risky_attempt', 'noble_sacrifice'],
        emotionalImpact: 0.8
      }
      integrator.recordQuestMemory(mockNpcId, questEvent, context)
      expect(memoryManager.addMemory).toHaveBeenCalledWith(
        mockNpcId,
        expect.objectContaining({
          type: MemoryEventType.QUEST,
          importance: expect.any(Number),
          details: expect.objectContaining({
            questId: questEvent.questId,
            questType: questEvent.type,
            outcome: questEvent.outcome,
            description: questEvent.description,
            emotionalImpact: expect.any(Number),
            playerActions: expect.any(Array)
          })
        })
      )
    })
  })
}) 