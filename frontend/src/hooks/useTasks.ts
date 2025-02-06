import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { fetchTasks } from '../store/slices/taskSlice';

export const useTasks = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { items: tasks, loading, error } = useSelector((state: RootState) => state.tasks);

  useEffect(() => {
    dispatch(fetchTasks());
  }, [dispatch]);

  return {
    tasks,
    loading,
    error,
    deleteTask: (id: number) => {
      // Implementer sletning her
      console.log('Sletter opgave:', id);
    }
  };
}; 