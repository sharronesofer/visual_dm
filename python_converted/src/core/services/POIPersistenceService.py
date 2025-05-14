from typing import Any


class POIPersistenceService {
  private static instance: \'POIPersistenceService\'
  private autosaveManager: AutosaveManager<POIPersistentState>
  private autoSaveInterval: float = 30000 
  private maxRetries: float = 3
  private retryDelay: float = 1000 
  private constructor() {
    this.autosaveManager = new AutosaveManager<POIPersistentState>({
      key: 'visual-dm-poi-state',
      version: '1.0.0',
      debounceMs: 1000,
      maxAge: 7 * 24 * 60 * 60 * 1000, 
    })
    this.startAutoSave()
  }
  public static getInstance(): \'POIPersistenceService\' {
    if (!POIPersistenceService.instance) {
      POIPersistenceService.instance = new POIPersistenceService()
    }
    return POIPersistenceService.instance
  }
  private async retryOperation<T>(operation: () => Promise<T>): Promise<T> {
    let lastError: Error | null = null
    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      try {
        return await operation()
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error))
        if (attempt < this.maxRetries) {
          await new Promise(resolve => setTimeout(resolve, this.retryDelay * attempt))
        }
      }
    }
    throw lastError
  }
  private startAutoSave(): void {
    setInterval(async () => {
      try {
        const state = usePoiStore.getState()
        await this.retryOperation(async () => {
          await this.autosaveManager.queueSave({
            pois: state.pois,
            activePOIs: state.activePOIs,
            currentPOI: state.currentPOI,
          })
          return Promise.resolve()
        })
      } catch (error) {
        console.error('Failed to auto-save POI state:', error)
        const store = usePoiStore.getState()
        store.setError('Failed to auto-save game state. Your progress may not be saved.')
      }
    }, this.autoSaveInterval)
  }
  public async saveImmediately(): Promise<POIServiceResponse> {
    try {
      const state = usePoiStore.getState()
      await this.retryOperation(() =>
        this.autosaveManager.saveImmediately({
          pois: state.pois,
          activePOIs: state.activePOIs,
          currentPOI: state.currentPOI,
        })
      )
      return { success: true }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save POI state'
      return { success: false, error: errorMessage }
    }
  }
  public loadState(): POIServiceResponse {
    try {
      const savedState = this.autosaveManager.load()
      if (savedState) {
        const store = usePoiStore.getState()
        store.setLoading(true)
        try {
          Object.entries(savedState.pois).forEach(([, poi]) => {
            const { chunks, activeChunks, isActive, ...poiData } = poi
            store.createPOI(poiData)
          })
          savedState.activePOIs.forEach(id => {
            store.activatePOI(id)
          })
          if (savedState.currentPOI) {
            store.setCurrentPOI(savedState.currentPOI)
          }
          store.setLoading(false)
          return { success: true, data: savedState }
        } catch (error) {
          store.setLoading(false)
          const errorMessage =
            error instanceof Error ? error.message : 'Failed to restore POI state'
          store.setError(errorMessage)
          return { success: false, error: errorMessage }
        }
      }
      return { success: true, data: null }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load POI state'
      const store = usePoiStore.getState()
      store.setError(errorMessage)
      return { success: false, error: errorMessage }
    }
  }
  public clearState(): void {
    try {
      this.autosaveManager.clear()
    } catch (error) {
      console.error('Failed to clear POI state:', error)
      const store = usePoiStore.getState()
      store.setError('Failed to clear saved game state.')
    }
  }
}
default POIPersistenceService