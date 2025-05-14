from typing import Any, Dict, List



class UsageEvent:
    type: str
    action: str
    timestamp: float
    metadata?: Dict[str, str>
    duration?: float
class FeatureUsage:
    featureId: str
    usageCount: float
    lastUsed: float
    averageDuration?: float
    metadata?: Dict[str, str>
class UsageAnalytics {
  private static instance: \'UsageAnalytics\'
  private optimizer: PerformanceOptimizer
  private isEnabled: bool = API_METRICS.ENABLE_USAGE_TRACKING
  private readonly MAX_STORED_EVENTS = 10000
  private events: List[UsageEvent] = []
  private featureUsage: Map<string, FeatureUsage> = new Map()
  private sessionStartTime: float = Date.now()
  private lastInteractionTime: float = Date.now()
  private constructor() {
    this.optimizer = PerformanceOptimizer.getInstance()
    this.setupEventListeners()
  }
  public static getInstance(): \'UsageAnalytics\' {
    if (!UsageAnalytics.instance) {
      UsageAnalytics.instance = new UsageAnalytics()
    }
    return UsageAnalytics.instance
  }
  private setupEventListeners(): void {
    if (typeof window !== 'undefined') {
      this.trackEvent('navigation', 'pageview', {
        path: window.location.pathname,
        referrer: document.referrer
      })
      window.addEventListener('click', (event) => {
        const target = event.target as HTMLElement
        if (target) {
          this.trackInteraction('click', target)
        }
      })
      window.addEventListener('submit', (event) => {
        const form = event.target as HTMLFormElement
        if (form) {
          this.trackInteraction('form_submit', form)
        }
      })
      window.addEventListener('beforeunload', () => {
        this.recordSessionMetrics()
      })
    }
  }
  private trackInteraction(action: str, element: HTMLElement): void {
    if (!this.isEnabled) return
    const metadata: Record<string, string> = {
      elementType: element.tagName.toLowerCase(),
      elementId: element.id || 'unknown',
      elementClass: element.className || 'none'
    }
    Array.from(element.attributes)
      .filter(attr => attr.name.startsWith('data-'))
      .forEach(attr => {
        metadata[attr.name.replace('data-', '')] = attr.value
      })
    this.trackEvent('interaction', action, metadata)
    this.lastInteractionTime = Date.now()
  }
  public trackEvent(type: str, action: str, metadata?: Record<string, string>, duration?: float): void {
    if (!this.isEnabled) return
    const event: \'UsageEvent\' = {
      type,
      action,
      timestamp: Date.now(),
      metadata,
      duration
    }
    this.storeEvent(event)
    this.updateFeatureUsage(event)
    this.recordEventMetrics(event)
  }
  private storeEvent(event: UsageEvent): void {
    this.events.push(event)
    if (this.events.length > this.MAX_STORED_EVENTS) {
      this.events.shift()
    }
  }
  private updateFeatureUsage(event: UsageEvent): void {
    const featureId = event.metadata?.featureId
    if (!featureId) return
    const existing = this.featureUsage.get(featureId) || {
      featureId,
      usageCount: 0,
      lastUsed: 0,
      averageDuration: 0,
      metadata: {}
    }
    existing.usageCount++
    existing.lastUsed = event.timestamp
    if (event.duration) {
      const currentTotal = (existing.averageDuration || 0) * (existing.usageCount - 1)
      existing.averageDuration = (currentTotal + event.duration) / existing.usageCount
    }
    if (event.metadata) {
      existing.metadata = { ...existing.metadata, ...event.metadata }
    }
    this.featureUsage.set(featureId, existing)
  }
  private recordEventMetrics(event: UsageEvent): void {
    this.optimizer.recordMetric({
      name: `usage_event_${event.type}_${event.action}`,
      value: 1,
      timestamp: event.timestamp,
      tags: event.metadata || {}
    })
    if (event.duration) {
      this.optimizer.recordMetric({
        name: `usage_duration_${event.type}_${event.action}`,
        value: event.duration,
        timestamp: event.timestamp,
        tags: event.metadata || {}
      })
    }
  }
  private recordSessionMetrics(): void {
    const sessionDuration = Date.now() - this.sessionStartTime
    const timeSinceLastInteraction = Date.now() - this.lastInteractionTime
    this.optimizer.recordMetric({
      name: 'session_duration',
      value: sessionDuration,
      timestamp: Date.now(),
      tags: Dict[str, Any]
    })
    this.optimizer.recordMetric({
      name: 'session_idle_time',
      value: timeSinceLastInteraction,
      timestamp: Date.now(),
      tags: Dict[str, Any]
    })
  }
  public getFeatureUsage(featureId?: str): \'FeatureUsage\' | Map<string, FeatureUsage> {
    if (featureId) {
      return this.featureUsage.get(featureId) || {
        featureId,
        usageCount: 0,
        lastUsed: 0
      }
    }
    return this.featureUsage
  }
  public getEvents(
    type?: str,
    action?: str,
    startTime?: float,
    endTime?: float
  ): UsageEvent[] {
    let filtered = this.events
    if (type) {
      filtered = filtered.filter(e => e.type === type)
    }
    if (action) {
      filtered = filtered.filter(e => e.action === action)
    }
    if (startTime) {
      filtered = filtered.filter(e => e.timestamp >= startTime)
    }
    if (endTime) {
      filtered = filtered.filter(e => e.timestamp <= endTime)
    }
    return filtered
  }
  public enableTracking(enabled: bool = true): void {
    this.isEnabled = enabled
  }
  public clearEvents(): void {
    this.events = []
    this.featureUsage.clear()
  }
} 