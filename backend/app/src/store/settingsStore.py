from typing import Any, Union


class SettingsState:
    darkMode: bool
    notifications: bool
    mapStyle: Union['standard', 'satellite', 'terrain']
    autoSave: bool
    setDarkMode: (darkMode: bool) => None
    setNotifications: (notifications: bool) => None
    setMapStyle: Union[(mapStyle: 'standard', 'satellite', 'terrain') => None]
    setAutoSave: (autoSave: bool) => None
const useSettingsStore = create<SettingsState>()(
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
)