import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import { Task, TaskStatus } from '../../types';

interface StatusPanelProps {
  tasks: Task[];
}

export const StatusPanel: React.FC<StatusPanelProps> = ({ tasks }) => {
  const todoCount = tasks.filter(t => t.status === TaskStatus.TODO).length;
  const inProgressCount = tasks.filter(t => t.status === TaskStatus.IN_PROGRESS).length;
  const doneCount = tasks.filter(t => t.status === TaskStatus.DONE).length;

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Status Overblik
      </Typography>
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Chip label={`TODO: ${todoCount}`} color="default" />
        <Chip label={`I GANG: ${inProgressCount}`} color="primary" />
        <Chip label={`FÆRDIG: ${doneCount}`} color="success" />
      </Box>
    </Box>
  );
}; 