import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UIState {
  darkMode: boolean;
  notifications: string[];
}

const initialState: UIState = {
  darkMode: false,
  notifications: []
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleDarkMode(state) {
      state.darkMode = !state.darkMode;
    },
    addNotification(state, action: PayloadAction<string>) {
      state.notifications.push(action.payload);
    },
    clearNotification(state, action: PayloadAction<number>) {
      state.notifications.splice(action.payload, 1);
    }
  }
});

export const { toggleDarkMode, addNotification, clearNotification } = uiSlice.actions;
export default uiSlice.reducer; 