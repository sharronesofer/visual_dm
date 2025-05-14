from typing import Any, Dict


const dummyReducer = (state = {}, action: Dict[str, Any]) => {
  switch (action.type) {
    default:
      return state
  }
}
const rootReducer = combineReducers({
  dummy: dummyReducer,
})
RootState = ReturnType[typeof rootReducer]
default rootReducer 