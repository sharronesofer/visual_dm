from typing import Any, Dict, List, Union


class MediaState:
    items: List[MediaAsset]
    isLoading: bool
    error: Union[str, None]
    selectedItem: Union[MediaAsset, None]
const initialState: \'MediaState\' = {
  items: [],
  isLoading: false,
  error: null,
  selectedItem: null,
}
const mediaSlice = createSlice({
  name: 'media',
  initialState,
  reducers: Dict[str, Any],
    setLoading: (state: \'MediaState\', action: PayloadAction<boolean>) => {
      state.isLoading = action.payload
    },
    setError: (state: \'MediaState\', action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
    setSelectedItem: (state: \'MediaState\', action: PayloadAction<MediaAsset | null>) => {
      state.selectedItem = action.payload
    },
  },
})
const { setItems, setLoading, setError, setSelectedItem } = mediaSlice.actions
const mediaReducer = mediaSlice.reducer 