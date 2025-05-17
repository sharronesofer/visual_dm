import { StateStorage, StorageValue } from 'zustand/middleware';

/**
 * Configuration for store persistence
 */
export interface PersistenceConfig {
  /** Storage key prefix */
  prefix: string;
  /** Storage implementation (defaults to localStorage) */
  storage?: StateStorage;
  /** Debounce time in ms for auto-save (0 for immediate) */
  debounceTime?: number;
  /** Version for migration handling */
  version?: number;
}

/**
 * Extended storage interface with getAllKeys method
 */
interface ExtendedStorage extends StateStorage {
  getAllKeys?(): Promise<string[]>;
}

/**
 * Persistence handler interface
 */
export interface PersistenceHandler {
  /** Get stored state */
  getStoredState: <T>(key: string) => Promise<T | null>;
  /** Save state with optional debounce */
  saveState: <T>(key: string, state: T, immediate?: boolean) => Promise<void>;
  /** Remove stored state */
  removeState: (key: string) => Promise<void>;
  /** Clear all stored states */
  clearAllStates: () => Promise<void>;
}

/**
 * Minimal in-memory storage fallback for Node/test environments
 */
const createMemoryStorage = (): StateStorage => {
  const data: Record<string, string> = {};
  return {
    getItem(key: string) {
      return Promise.resolve(data[key] ?? null);
    },
    setItem(key: string, value: string) {
      data[key] = value;
      return Promise.resolve();
    },
    removeItem(key: string) {
      delete data[key];
      return Promise.resolve();
    },
  };
};

/**
 * Creates a persistence handler for state management
 */
export const createPersistence = (config: PersistenceConfig): PersistenceHandler => {
  const {
    prefix,
    storage = (typeof localStorage !== 'undefined' ? localStorage : createMemoryStorage()) as ExtendedStorage,
    debounceTime = 1000,
    version = 1,
  } = config;

  let saveTimeout: NodeJS.Timeout | null = null;

  return {
    /**
     * Get stored state
     */
    getStoredState: async <T>(key: string): Promise<T | null> => {
      try {
        const fullKey = `${prefix}${key}_v${version}`;
        const stored = await storage.getItem(fullKey);
        if (!stored) return null;

        const { state, version: storedVersion } = JSON.parse(
          stored
        ) as StorageValue<T>;
        if (storedVersion !== version) return null;

        return state;
      } catch (error) {
        console.error('Error loading stored state:', error);
        return null;
      }
    },

    /**
     * Save state with optional debounce
     */
    saveState: async <T>(
      key: string,
      state: T,
      immediate = false
    ): Promise<void> => {
      const save = async () => {
        try {
          const fullKey = `${prefix}${key}_v${version}`;
          const value: StorageValue<T> = {
            state,
            version,
          };
          await storage.setItem(fullKey, JSON.stringify(value));
        } catch (error) {
          console.error('Error saving state:', error);
          throw error; // Re-throw to allow error handling by caller
        }
      };

      if (saveTimeout) {
        clearTimeout(saveTimeout);
      }

      if (immediate) {
        await save();
      } else {
        return new Promise((resolve, reject) => {
          saveTimeout = setTimeout(async () => {
            try {
              await save();
              resolve();
            } catch (error) {
              reject(error);
            }
          }, debounceTime);
        });
      }
    },

    /**
     * Remove stored state
     */
    removeState: async (key: string): Promise<void> => {
      try {
        const fullKey = `${prefix}${key}_v${version}`;
        await storage.removeItem(fullKey);

        // Clear any pending saves
        if (saveTimeout) {
          clearTimeout(saveTimeout);
          saveTimeout = null;
        }
      } catch (error) {
        console.error('Error removing state:', error);
        throw error;
      }
    },

    /**
     * Clear all stored states
     */
    clearAllStates: async (): Promise<void> => {
      try {
        const keys = await (storage as ExtendedStorage).getAllKeys?.();
        if (!keys) {
          // Fallback for storages without getAllKeys
          for (let i = 0; i < (storage as Storage).length; i++) {
            const key = (storage as Storage).key(i);
            if (key?.startsWith(prefix)) {
              await storage.removeItem(key);
            }
          }
          return;
        }

        const storeKeys = keys.filter((key: string) => key.startsWith(prefix));
        await Promise.all(
          storeKeys.map((key: string) => storage.removeItem(key))
        );

        // Clear any pending saves
        if (saveTimeout) {
          clearTimeout(saveTimeout);
          saveTimeout = null;
        }
      } catch (error) {
        console.error('Error clearing states:', error);
        throw error;
      }
    },
  };
};
