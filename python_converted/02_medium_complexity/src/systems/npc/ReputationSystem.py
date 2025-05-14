from typing import Any



class ReputationChange:
    value: float
    reason: str
    timestamp: float
class ReputationSystem {
  private reputationHistory: Map<string, ReputationChange[]>
  constructor() {
    this.reputationHistory = new Map()
  }
  public async processInteractionReputation(
    npcId: str,
    targetId: str,
    result: InteractionResult
  ): Promise<number> {
    try {
      let reputationChange = this.calculateBaseReputation(result)
      reputationChange = this.applyInteractionModifiers(reputationChange, result)
      this.recordReputationChange(npcId, targetId, reputationChange, result)
      return reputationChange
    } catch (error) {
      console.error('Error processing reputation change:', error)
      return 0
    }
  }
  private calculateBaseReputation(result: InteractionResult): float {
    let change = 0
    change += result.success ? 0.05 : -0.05
    if (result.reputationChange) {
      change += result.reputationChange
    }
    return change
  }
  private applyInteractionModifiers(baseChange: float, result: InteractionResult): float {
    let finalChange = baseChange
    if (result.economicImpact) {
      const economicValue = result.economicImpact.value || 0
      if (economicValue > 0) {
        finalChange *= 1.2 
      } else if (economicValue < 0) {
        finalChange *= 0.8 
      }
    }
    if (result.emotionalResponse) {
      if (result.emotionalResponse.includes('happy') || 
          result.emotionalResponse.includes('pleased')) {
        finalChange *= 1.1
      } else if (result.emotionalResponse.includes('angry') || 
                 result.emotionalResponse.includes('upset')) {
        finalChange *= 0.9
      }
    }
    return Math.max(-0.5, Math.min(0.5, finalChange))
  }
  private recordReputationChange(
    npcId: str,
    targetId: str,
    value: float,
    result: InteractionResult
  ): void {
    const key = `${npcId}:${targetId}`
    if (!this.reputationHistory.has(key)) {
      this.reputationHistory.set(key, [])
    }
    const change: \'ReputationChange\' = {
      value,
      reason: this.generateChangeReason(result),
      timestamp: Date.now()
    }
    this.reputationHistory.get(key)?.push(change)
  }
  private generateChangeReason(result: InteractionResult): str {
    if (result.success) {
      return 'Successful interaction'
    } else {
      return 'Failed interaction'
    }
  }
  public getReputationHistory(npcId: str, targetId: str): ReputationChange[] {
    const key = `${npcId}:${targetId}`
    return this.reputationHistory.get(key) || []
  }
  public getAggregateReputation(npcId: str, targetId: str): float {
    const history = this.getReputationHistory(npcId, targetId)
    if (history.length === 0) return 0
    let totalWeight = 0
    let weightedSum = 0
    const now = Date.now()
    const dayInMs = 24 * 60 * 60 * 1000
    history.forEach(change => {
      const daysAgo = (now - change.timestamp) / dayInMs
      const weight = Math.max(0, 1 - (daysAgo / 30)) 
      weightedSum += change.value * weight
      totalWeight += weight
    })
    return totalWeight > 0 ? weightedSum / totalWeight : 0
  }
} 