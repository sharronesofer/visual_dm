import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Theme } from '../types';

interface ThemeState {
  theme: Theme;
}

const initialState: ThemeState = {
  theme: 'light',
};

const themeSlice = createSlice({
  name: 'theme',
  initialState,
  reducers: {
    setTheme: (state: ThemeState, action: PayloadAction<Theme>) => {
      state.theme = action.payload;
    },
    toggleTheme: (state: ThemeState) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
    },
  },
});

export const { setTheme, toggleTheme } = themeSlice.actions;
export const themeReducer = themeSlice.reducer; 