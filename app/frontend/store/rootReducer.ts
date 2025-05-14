import { combineReducers } from '@reduxjs/toolkit';

// Example slice for testing
const dummyReducer = (state = {}, action: { type: string }) => {
  switch (action.type) {
    default:
      return state;
  }
};

const rootReducer = combineReducers({
  dummy: dummyReducer,
});

export type RootState = ReturnType<typeof rootReducer>;
export default rootReducer; 