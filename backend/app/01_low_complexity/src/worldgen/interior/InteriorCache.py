from typing import Any



class InteriorCache {
  private cache: Map<string, InteriorLayout> = new Map()
  private maxSize: float
  constructor(maxSize = 50) {
    this.maxSize = maxSize
  }
  private key(params: InteriorParams): str {
    return JSON.stringify(params)
  }
  get(params: InteriorParams): InteriorLayout | undefined {
    return this.cache.get(this.key(params))
  }
  set(params: InteriorParams, layout: InteriorLayout): void {
    const k = this.key(params)
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value
      if (typeof firstKey === 'string') {
        this.cache.delete(firstKey)
      }
    }
    this.cache.set(k, layout)
  }
  clear(): void {
    this.cache.clear()
  }
} 