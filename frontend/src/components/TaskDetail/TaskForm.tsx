import React from 'react';
import { Box, TextField, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { Task, TaskStatus, TaskPriority } from '../../types';

interface TaskFormProps {
  task: Task;
  onSubmit: (task: Task) => void;
}

export const TaskForm: React.FC<TaskFormProps> = ({ task, onSubmit }) => {
  return (
    <Box component="form" sx={{ mt: 2 }}>
      <TextField
        fullWidth
        label="Titel"
        value={task.title}
        margin="normal"
      />
      <TextField
        fullWidth
        label="Beskrivelse"
        value={task.description}
        multiline
        rows={4}
        margin="normal"
      />
      <FormControl fullWidth margin="normal">
        <InputLabel>Status</InputLabel>
        <Select value={task.status}>
          {Object.values(TaskStatus).map(status => (
            <MenuItem key={status} value={status}>{status}</MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
}; 