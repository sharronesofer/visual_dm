import { debounce } from 'lodash';

export interface AutosaveConfig {
  key: string;
  debounceMs?: number;
  maxAge?: number; // Maximum age in milliseconds
  version?: string; // For handling data structure changes
}

export interface AutosaveData<T> {
  data: T;
  timestamp: number;
  version: string;
}

export interface AutosaveStatus {
  lastSaved: Date | null;
  hasUnsavedChanges: boolean;
  isRestoring: boolean;
}

export class AutosaveManager<T> {
  private config: Required<AutosaveConfig>;
  private lastSavedData: string | null = null;
  private status: AutosaveStatus = {
    lastSaved: null,
    hasUnsavedChanges: false,
    isRestoring: false,
  };
  private statusListeners: ((status: AutosaveStatus) => void)[] = [];

  constructor(config: AutosaveConfig) {
    this.config = {
      debounceMs: 2000, // Default to 2 seconds
      maxAge: 24 * 60 * 60 * 1000, // Default to 24 hours
      version: '1.0',
      ...config,
    };
  }

  // Save data with debouncing
  private debouncedSave = debounce(async (data: T) => {
    try {
      const serializedData = JSON.stringify(data);

      // Only save if data has changed
      if (serializedData !== this.lastSavedData) {
        const autosaveData: AutosaveData<T> = {
          data,
          timestamp: Date.now(),
          version: this.config.version,
        };

        localStorage.setItem(this.config.key, JSON.stringify(autosaveData));

        this.lastSavedData = serializedData;
        this.updateStatus({
          lastSaved: new Date(),
          hasUnsavedChanges: false,
        });
      }
    } catch (error) {
      console.error('Autosave failed:', error);
    }
  }, this.config.debounceMs);

  // Save data immediately
  public async saveImmediately(data: T): Promise<void> {
    this.debouncedSave.cancel(); // Cancel any pending debounced saves
    return new Promise((resolve, reject) => {
      try {
        const serializedData = JSON.stringify(data);
        const autosaveData: AutosaveData<T> = {
          data,
          timestamp: Date.now(),
          version: this.config.version,
        };

        localStorage.setItem(this.config.key, JSON.stringify(autosaveData));

        this.lastSavedData = serializedData;
        this.updateStatus({
          lastSaved: new Date(),
          hasUnsavedChanges: false,
        });
        resolve();
      } catch (error) {
        reject(error);
      }
    });
  }

  // Queue data for autosave
  public queueSave(data: T): void {
    this.updateStatus({ hasUnsavedChanges: true });
    this.debouncedSave(data);
  }

  // Load saved data
  public load(): T | null {
    try {
      const saved = localStorage.getItem(this.config.key);
      if (!saved) return null;

      const autosaveData: AutosaveData<T> = JSON.parse(saved);

      // Check version compatibility
      if (autosaveData.version !== this.config.version) {
        console.warn('Autosave data version mismatch, clearing saved data');
        this.clear();
        return null;
      }

      // Check if data is too old
      const age = Date.now() - autosaveData.timestamp;
      if (age > this.config.maxAge) {
        console.warn('Autosave data expired, clearing saved data');
        this.clear();
        return null;
      }

      this.lastSavedData = JSON.stringify(autosaveData.data);
      this.updateStatus({
        lastSaved: new Date(autosaveData.timestamp),
        hasUnsavedChanges: false,
      });

      return autosaveData.data;
    } catch (error) {
      console.error('Failed to load autosaved data:', error);
      return null;
    }
  }

  // Clear saved data
  public clear(): void {
    localStorage.removeItem(this.config.key);
    this.lastSavedData = null;
    this.updateStatus({
      lastSaved: null,
      hasUnsavedChanges: false,
    });
  }

  // Subscribe to status updates
  public subscribeToStatus(listener: (status: AutosaveStatus) => void): () => void {
    this.statusListeners.push(listener);
    listener({ ...this.status }); // Initial status
    return () => {
      this.statusListeners = this.statusListeners.filter(l => l !== listener);
    };
  }

  // Update status and notify listeners
  private updateStatus(updates: Partial<AutosaveStatus>): void {
    this.status = {
      ...this.status,
      ...updates,
    };
    this.statusListeners.forEach(listener => listener({ ...this.status }));
  }

  // Check if there are unsaved changes
  public hasUnsavedChanges(): boolean {
    return this.status.hasUnsavedChanges;
  }

  // Get the last save time
  public getLastSaveTime(): Date | null {
    return this.status.lastSaved;
  }
}
