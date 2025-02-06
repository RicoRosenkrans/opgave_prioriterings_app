import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { Task } from '../../types';
import axios from 'axios';

interface TaskState {
  items: Task[];
  loading: boolean;
  error: string | null;
}

const initialState: TaskState = {
  items: [],
  loading: false,
  error: null
};

export const fetchTasks = createAsyncThunk(
  'tasks/fetchTasks',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/tasks`);
      return response.data;
    } catch (error) {
      return rejectWithValue('Kunne ikke hente opgaver. Er serveren startet?');
    }
  }
);

export const createTask = createAsyncThunk(
  'tasks/createTask',
  async (taskData: { title: string, description?: string }) => {
    const response = await axios.post(
      `${process.env.REACT_APP_API_URL}/tasks`,
      taskData
    );
    return response.data;
  }
);

const taskSlice = createSlice({
  name: 'tasks',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchTasks.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTasks.fulfilled, (state, action) => {
        state.items = action.payload;
        state.loading = false;
      })
      .addCase(fetchTasks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(createTask.fulfilled, (state, action) => {
        state.items.push(action.payload);
      });
  },
});

export default taskSlice.reducer; 