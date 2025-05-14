from typing import Any, Dict, Union



class AuthState:
    user: Union[User, None]
    isLoading: bool
    error: Union[str, None]
const initialState: \'AuthState\' = {
  user: null,
  isLoading: false,
  error: null,
}
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: Dict[str, Any],
    setLoading: (state: \'AuthState\', action: PayloadAction<boolean>) => {
      state.isLoading = action.payload
    },
    setError: (state: \'AuthState\', action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
    logout: (state: AuthState) => {
      state.user = null
      state.error = null
    },
  },
})
const { setUser, setLoading, setError, logout } = authSlice.actions
const authReducer = authSlice.reducer 