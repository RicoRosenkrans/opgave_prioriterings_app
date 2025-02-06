import React from 'react';
import { List, ListItem, ListItemText, Chip, IconButton } from '@mui/material';
import { Edit, Delete } from '@mui/icons-material';
import { Task, TaskPriority } from '../../types';
import { useNavigate } from 'react-router-dom';

interface TaskListProps {
  tasks: Task[];
  onDelete: (id: number) => void;
}

const priorityColors: Record<TaskPriority, "error" | "info" | "success" | "warning" | "default" | "primary" | "secondary"> = {
  [TaskPriority.LOW]: 'info',
  [TaskPriority.MEDIUM]: 'success',
  [TaskPriority.HIGH]: 'warning',
  [TaskPriority.URGENT]: 'error'
};

export const TaskList: React.FC<TaskListProps> = ({ tasks, onDelete }) => {
  const navigate = useNavigate();

  return (
    <List>
      {tasks.map((task) => (
        <ListItem
          key={task.id}
          secondaryAction={
            <>
              <IconButton onClick={() => navigate(`/tasks/${task.id}`)}>
                <Edit />
              </IconButton>
              <IconButton onClick={() => onDelete(task.id)}>
                <Delete />
              </IconButton>
            </>
          }
        >
          <ListItemText
            primary={task.title}
            secondary={task.description}
          />
          <Chip
            label={task.priority}
            color={priorityColors[task.priority]}
            size="small"
            sx={{ ml: 1 }}
          />
          <Chip
            label={task.status}
            variant="outlined"
            size="small"
            sx={{ ml: 1 }}
          />
        </ListItem>
      ))}
    </List>
  );
}; 