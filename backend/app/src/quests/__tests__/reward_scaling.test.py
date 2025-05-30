from typing import Any


  calculateXP,
  calculateGold,
  applyDiminishingReturns,
  getSpecialRewards,
  scaleRewards,
  RewardParams
} from '../reward_scaling'
describe('Reward Scaling', () => {
  const baseParams: RewardParams = {
    baseXP: 100,
    baseGold: 50,
    difficulty: 2,
    playerLevel: 5,
    questSignificance: 'main',
    repetitionCount: 0
  }
  it('calculates XP scaling', () => {
    const xp = calculateXP(baseParams)
    expect(typeof xp).toBe('number')
    expect(xp).toBeGreaterThan(0)
  })
  it('calculates gold scaling', () => {
    const gold = calculateGold(baseParams)
    expect(typeof gold).toBe('number')
    expect(gold).toBeGreaterThan(0)
  })
  it('applies diminishing returns', () => {
    const value = 100
    const diminished = applyDiminishingReturns(value, 3)
    expect(diminished).toBeLessThan(value)
  })
  it('returns special rewards for milestone quests', () => {
    const specials = getSpecialRewards('milestone')
    expect(Array.isArray(specials)).toBe(true)
    expect(specials.length).toBeGreaterThan(0)
  })
  it('scales rewards for repeated quests', () => {
    const params = { ...baseParams, repetitionCount: 5 }
    const rewards = scaleRewards(params)
    expect(rewards.xp).toBeLessThan(calculateXP(baseParams))
    expect(rewards.gold).toBeLessThan(calculateGold(baseParams))
  })
  it('handles edge cases: max level, high difficulty', () => {
    const params = { ...baseParams, playerLevel: 99, difficulty: 10 }
    const rewards = scaleRewards(params)
    expect(rewards.xp).toBeGreaterThan(0)
    expect(rewards.gold).toBeGreaterThan(0)
  })
}) 