import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { Task } from '../../types';

interface AIInsightsProps {
  tasks: Task[];
}

export const AIInsights: React.FC<AIInsightsProps> = ({ tasks }) => {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        AI Indsigt
      </Typography>
      <Paper sx={{ p: 2, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
        <Typography>
          {tasks.length > 0
            ? `Du har ${tasks.length} aktive opgaver. Lad mig hjælpe dig med at prioritere dem.`
            : 'Ingen opgaver at analysere endnu.'}
        </Typography>
      </Paper>
    </Box>
  );
}; 