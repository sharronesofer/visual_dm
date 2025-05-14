from typing import Any, Union



class AutosaveConfig:
    key: str
    debounceMs?: float
    maxAge?: float
    version?: str
interface AutosaveData<T> {
  data: T
  timestamp: float
  version: str
}
class AutosaveStatus:
    lastSaved: Union[Date, None]
    hasUnsavedChanges: bool
    isRestoring: bool
class AutosaveManager<T> {
  private config: Required<AutosaveConfig>
  private lastSavedData: str | null = null
  private status: \'AutosaveStatus\' = {
    lastSaved: null,
    hasUnsavedChanges: false,
    isRestoring: false,
  }
  private statusListeners: ((status: AutosaveStatus) => void)[] = []
  constructor(config: AutosaveConfig) {
    this.config = {
      debounceMs: 2000, 
      maxAge: 24 * 60 * 60 * 1000, 
      version: '1.0',
      ...config,
    }
  }
  private debouncedSave = debounce(async (data: T) => {
    try {
      const serializedData = JSON.stringify(data)
      if (serializedData !== this.lastSavedData) {
        const autosaveData: AutosaveData<T> = {
          data,
          timestamp: Date.now(),
          version: this.config.version,
        }
        localStorage.setItem(this.config.key, JSON.stringify(autosaveData))
        this.lastSavedData = serializedData
        this.updateStatus({
          lastSaved: new Date(),
          hasUnsavedChanges: false,
        })
      }
    } catch (error) {
      console.error('Autosave failed:', error)
    }
  }, this.config.debounceMs)
  public async saveImmediately(data: T): Promise<void> {
    this.debouncedSave.cancel() 
    return new Promise((resolve, reject) => {
      try {
        const serializedData = JSON.stringify(data)
        const autosaveData: AutosaveData<T> = {
          data,
          timestamp: Date.now(),
          version: this.config.version,
        }
        localStorage.setItem(this.config.key, JSON.stringify(autosaveData))
        this.lastSavedData = serializedData
        this.updateStatus({
          lastSaved: new Date(),
          hasUnsavedChanges: false,
        })
        resolve()
      } catch (error) {
        reject(error)
      }
    })
  }
  public queueSave(data: T): void {
    this.updateStatus({ hasUnsavedChanges: true })
    this.debouncedSave(data)
  }
  public load(): T | null {
    try {
      const saved = localStorage.getItem(this.config.key)
      if (!saved) return null
      const autosaveData: AutosaveData<T> = JSON.parse(saved)
      if (autosaveData.version !== this.config.version) {
        console.warn('Autosave data version mismatch, clearing saved data')
        this.clear()
        return null
      }
      const age = Date.now() - autosaveData.timestamp
      if (age > this.config.maxAge) {
        console.warn('Autosave data expired, clearing saved data')
        this.clear()
        return null
      }
      this.lastSavedData = JSON.stringify(autosaveData.data)
      this.updateStatus({
        lastSaved: new Date(autosaveData.timestamp),
        hasUnsavedChanges: false,
      })
      return autosaveData.data
    } catch (error) {
      console.error('Failed to load autosaved data:', error)
      return null
    }
  }
  public clear(): void {
    localStorage.removeItem(this.config.key)
    this.lastSavedData = null
    this.updateStatus({
      lastSaved: null,
      hasUnsavedChanges: false,
    })
  }
  public subscribeToStatus(listener: (status: AutosaveStatus) => void): () => void {
    this.statusListeners.push(listener)
    listener({ ...this.status }) 
    return () => {
      this.statusListeners = this.statusListeners.filter(l => l !== listener)
    }
  }
  private updateStatus(updates: Partial<AutosaveStatus>): void {
    this.status = {
      ...this.status,
      ...updates,
    }
    this.statusListeners.forEach(listener => listener({ ...this.status }))
  }
  public hasUnsavedChanges(): bool {
    return this.status.hasUnsavedChanges
  }
  public getLastSaveTime(): Date | null {
    return this.status.lastSaved
  }
}