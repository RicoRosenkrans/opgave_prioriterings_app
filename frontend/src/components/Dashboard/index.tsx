import React from 'react';
import { Container, Grid, Paper, Typography } from '@mui/material';
import { TaskList } from './TaskList';
import { StatusPanel } from './StatusPanel';
import { AIInsights } from './AIInsights';
import { QuickAdd } from './QuickAdd';
import { useTasks } from '../../hooks/useTasks';

export const Dashboard: React.FC = () => {
  const { tasks, loading, error, deleteTask } = useTasks();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Opgaveliste */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Dagens Opgaver
            </Typography>
            <TaskList tasks={tasks} onDelete={deleteTask} />
          </Paper>
        </Grid>

        {/* Status Panel */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <StatusPanel tasks={tasks} />
          </Paper>
          
          {/* AI Insights */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <AIInsights tasks={tasks} />
          </Paper>
          
          {/* Quick Add */}
          <Paper sx={{ p: 2 }}>
            <QuickAdd />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}; 