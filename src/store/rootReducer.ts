import { combineReducers } from '@reduxjs/toolkit';
import { mediaReducer } from './mediaSlice';
import { authReducer } from './authSlice';
import { themeReducer } from './themeSlice';

export const rootReducer = combineReducers({
  media: mediaReducer,
  auth: authReducer,
  theme: themeReducer,
});

export type RootState = ReturnType<typeof rootReducer>; 