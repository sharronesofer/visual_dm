import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { MediaAsset } from '../types';

interface MediaState {
  items: MediaAsset[];
  isLoading: boolean;
  error: string | null;
  selectedItem: MediaAsset | null;
}

const initialState: MediaState = {
  items: [],
  isLoading: false,
  error: null,
  selectedItem: null,
};

const mediaSlice = createSlice({
  name: 'media',
  initialState,
  reducers: {
    setItems: (state: MediaState, action: PayloadAction<MediaAsset[]>) => {
      state.items = action.payload;
    },
    setLoading: (state: MediaState, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state: MediaState, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    setSelectedItem: (state: MediaState, action: PayloadAction<MediaAsset | null>) => {
      state.selectedItem = action.payload;
    },
  },
});

export const { setItems, setLoading, setError, setSelectedItem } = mediaSlice.actions;
export const mediaReducer = mediaSlice.reducer; 