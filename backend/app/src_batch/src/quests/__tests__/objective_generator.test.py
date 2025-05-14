from typing import Any



  generateKillObjectives,
  generateCollectObjectives,
  generateExploreObjectives,
  generateDiplomaticObjectives,
  generateObjectiveForType,
  validateObjective,
  ObjectiveGenerationContext
} from '../objective_generator'
const baseContext: ObjectiveGenerationContext = {
  playerLevel: 3,
  location: 'forest',
  availableTargets: ['goblin', 'wolf', 'herb'],
  questHistory: [],
  difficulty: 2
}
describe('Objective Generator', () => {
  it('generates valid kill objectives', () => {
    const objs = generateKillObjectives(baseContext)
    expect(Array.isArray(objs)).toBe(true)
    for (const obj of objs) {
      expect(obj.type).toBe('KILL')
      expect(validateObjective(obj)).toBe(true)
    }
  })
  it('generates valid collect objectives', () => {
    const objs = generateCollectObjectives(baseContext)
    expect(Array.isArray(objs)).toBe(true)
    for (const obj of objs) {
      expect(obj.type).toBe('COLLECT')
      expect(validateObjective(obj)).toBe(true)
    }
  })
  it('generates valid explore objectives', () => {
    const objs = generateExploreObjectives(baseContext)
    expect(Array.isArray(objs)).toBe(true)
    for (const obj of objs) {
      expect(obj.type).toBe('EXPLORE')
      expect(validateObjective(obj)).toBe(true)
    }
  })
  it('generates valid diplomatic objectives', () => {
    const objs = generateDiplomaticObjectives(baseContext)
    expect(Array.isArray(objs)).toBe(true)
    for (const obj of objs) {
      expect(obj.type).toBe('DIPLOMATIC_MEETING')
      expect(validateObjective(obj)).toBe(true)
    }
  })
  it('factory generates correct type', () => {
    const types = ['KILL', 'COLLECT', 'EXPLORE', 'DIPLOMATIC']
    for (const type of types) {
      const objs = generateObjectiveForType(type as any, baseContext)
      expect(Array.isArray(objs)).toBe(true)
      for (const obj of objs) {
        expect(validateObjective(obj)).toBe(true)
      }
    }
  })
  it('prevents repetition of objectives', () => {
    const context = { ...baseContext, availableTargets: ['goblin'] }
    const first = generateKillObjectives(context)
    const second = generateKillObjectives(context)
    if (first.length && second.length) {
      expect(first[0].id).not.toBe(second[0].id)
    }
  })
}) 