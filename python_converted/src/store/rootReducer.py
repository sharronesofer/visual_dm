from typing import Any


const rootReducer = combineReducers({
  media: mediaReducer,
  auth: authReducer,
  theme: themeReducer,
})
RootState = ReturnType[typeof rootReducer] 