import React from 'react';
import { Box, Button, Typography } from '@mui/material';
import { Psychology } from '@mui/icons-material';

interface AIAssistancePanelProps {
  taskId: number;
  connected: boolean;
}

export const AIAssistancePanel: React.FC<AIAssistancePanelProps> = ({ taskId, connected }) => {
  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6" gutterBottom>
        AI Assistance
      </Typography>
      <Button
        variant="contained"
        startIcon={<Psychology />}
        disabled={!connected}
        onClick={() => console.log('Anmoder om prioritetsforslag')}
      >
        Få Prioritetsforslag
      </Button>
    </Box>
  );
}; 