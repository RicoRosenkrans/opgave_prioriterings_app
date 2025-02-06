import React, { useState } from 'react';
import { Box, TextField, Button } from '@mui/material';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../../store';
import { createTask } from '../../store/slices/taskSlice';

export const QuickAdd: React.FC = () => {
  const [title, setTitle] = useState('');
  const dispatch = useDispatch<AppDispatch>();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      await dispatch(createTask({ title }));
      setTitle('');
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      <TextField
        fullWidth
        label="Ny opgave"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        margin="normal"
      />
      <Button type="submit" variant="contained" fullWidth>
        Tilføj Opgave
      </Button>
    </Box>
  );
}; 