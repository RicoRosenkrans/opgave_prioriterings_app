import { configureStore } from '@reduxjs/toolkit';
import tasksReducer from './slices/taskSlice';
import uiReducer from './slices/uiSlice';
import { websocketMiddleware } from './middleware/websocket';

export const store = configureStore({
  reducer: {
    tasks: tasksReducer,
    ui: uiReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(websocketMiddleware)
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 