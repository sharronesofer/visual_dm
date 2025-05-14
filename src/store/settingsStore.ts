import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SettingsState {
  darkMode: boolean;
  notifications: boolean;
  mapStyle: 'standard' | 'satellite' | 'terrain';
  autoSave: boolean;
  setDarkMode: (darkMode: boolean) => void;
  setNotifications: (notifications: boolean) => void;
  setMapStyle: (mapStyle: 'standard' | 'satellite' | 'terrain') => void;
  setAutoSave: (autoSave: boolean) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    set => ({
      darkMode: false,
      notifications: true,
      mapStyle: 'standard',
      autoSave: true,
      setDarkMode: darkMode => set({ darkMode }),
      setNotifications: notifications => set({ notifications }),
      setMapStyle: mapStyle => set({ mapStyle }),
      setAutoSave: autoSave => set({ autoSave }),
    }),
    {
      name: 'settings-storage',
    }
  )
);
