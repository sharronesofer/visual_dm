from typing import Any


class AutoSaveConfig:
    interval: float
    storageKey: str
    maxSaves: float
class SavedCharacter:
    data: CharacterData
    timestamp: float
    isValid: bool
    isAutosave: bool
class AutoSaveService {
  private static instance: \'AutoSaveService\'
  private intervalId: float | null = null
  private validationService: ValidationService
  private config: \'AutoSaveConfig\' = {
    interval: 30000, 
    storageKey: 'dnd_character_autosaves',
    maxSaves: 5,
  }
  private setIntervalFn: typeof window.setInterval = window.setInterval
  private clearIntervalFn: typeof window.clearInterval = window.clearInterval
  private constructor() {
    this.validationService = ValidationService.getInstance()
  }
  public static getInstance(): \'AutoSaveService\' {
    if (!AutoSaveService.instance) {
      AutoSaveService.instance = new AutoSaveService()
    }
    return AutoSaveService.instance
  }
  public setTimerFunctions(
    setIntervalFn: typeof window.setInterval,
    clearIntervalFn: typeof window.clearInterval
  ): void {
    this.setIntervalFn = setIntervalFn
    this.clearIntervalFn = clearIntervalFn
  }
  public configure(config: Partial<AutoSaveConfig>): void {
    this.config = { ...this.config, ...config }
  }
  public startAutoSave(
    characterData: CharacterData,
    onChange: (data: CharacterData) => void
  ): void {
    this.stopAutoSave()
    this.intervalId = this.setIntervalFn(() => {
      this.saveCharacter(characterData, true)
      onChange(characterData)
    }, this.config.interval)
    this.saveCharacter(characterData, true)
  }
  public stopAutoSave(): void {
    if (this.intervalId !== null) {
      this.clearIntervalFn(this.intervalId)
      this.intervalId = null
    }
  }
  public saveCharacter(characterData: CharacterData, isAutosave: bool = false): void {
    try {
      const validation = this.validationService.validateCharacter(characterData)
      const savedCharacter: \'SavedCharacter\' = {
        data: characterData,
        timestamp: Date.now(),
        isValid: validation.isValid,
        isAutosave,
      }
      const saves = this.getSavedCharacters()
      saves.unshift(savedCharacter)
      const trimmedSaves = saves.slice(0, this.config.maxSaves)
      localStorage.setItem(this.config.storageKey, JSON.stringify(trimmedSaves))
    } catch (error) {
      console.error('Failed to save character:', error)
    }
  }
  public getSavedCharacters(): SavedCharacter[] {
    try {
      const saves = localStorage.getItem(this.config.storageKey)
      return saves ? JSON.parse(saves) : []
    } catch (error) {
      console.error('Failed to retrieve saved characters:', error)
      return []
    }
  }
  public getLatestSave(): \'SavedCharacter\' | null {
    const saves = this.getSavedCharacters()
    return saves.length > 0 ? saves[0] : null
  }
  public getLatestValidSave(): \'SavedCharacter\' | null {
    const saves = this.getSavedCharacters()
    return saves.find(save => save.isValid) || null
  }
  public clearSaves(): void {
    try {
      localStorage.removeItem(this.config.storageKey)
    } catch (error) {
      console.error('Failed to clear saved characters:', error)
    }
  }
  public hasPendingChanges(): bool {
    const latestSave = this.getLatestSave()
    if (!latestSave) return false
    const latestValidSave = this.getLatestValidSave()
    if (!latestValidSave) return true
    return latestSave.timestamp > latestValidSave.timestamp
  }
  public restoreLatestValidSave(): CharacterData | null {
    const save = this.getLatestValidSave()
    return save ? save.data : null
  }
  public isAutoSaveEnabled(): bool {
    return this.intervalId !== null
  }
}