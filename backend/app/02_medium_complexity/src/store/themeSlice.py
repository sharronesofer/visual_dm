from typing import Any, Dict



class ThemeState:
    theme: Theme
const initialState: \'ThemeState\' = {
  theme: 'light',
}
const themeSlice = createSlice({
  name: 'theme',
  initialState,
  reducers: Dict[str, Any],
    toggleTheme: (state: ThemeState) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light'
    },
  },
})
const { setTheme, toggleTheme } = themeSlice.actions
const themeReducer = themeSlice.reducer 