import React from 'react';
import { useParams } from 'react-router-dom';
import { Container, Paper, Typography } from '@mui/material';
import { TaskForm } from './TaskDetail/TaskForm';
import { AIAssistancePanel } from './TaskDetail/AIAssistancePanel';
import { useTask } from '../hooks/useTask';
import { useWebSocket } from '../hooks/useWebSocket';


export const TaskDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { task, loading, error, updateTask } = useTask(Number(id));
  const { connected } = useWebSocket();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!task) return <div>Task not found</div>;

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          {task.title}
        </Typography>
        
        <TaskForm task={task} onSubmit={updateTask} />
        
        <AIAssistancePanel
          taskId={task.id}
          connected={connected}
        />
      </Paper>
    </Container>
  );
}; 