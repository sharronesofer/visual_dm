from typing import Any, Union


class AuthState:
    token: Union[str, None]
    setToken: (token: str) => None
    clearToken: () => None
const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      setToken: (token) => set({ token }),
      clearToken: () => set({ token: null }),
    }),
    {
      name: 'auth-storage',
    }
  )
) 