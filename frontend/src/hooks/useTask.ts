import { useEffect, useState } from 'react';
import { Task } from '../types';
import axios from 'axios';

export const useTask = (id: number) => {
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTask = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/tasks/${id}`);
      setTask(response.data);
      setError(null);
    } catch (err) {
      setError('Kunne ikke hente opgaven');
      setTask(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTask();
  }, [id]);

  const updateTask = async (updatedTask: Partial<Task>) => {
    try {
      const response = await axios.patch(
        `${process.env.REACT_APP_API_URL}/tasks/${id}`,
        updatedTask
      );
      setTask(response.data);
      return response.data;
    } catch (err) {
      setError('Kunne ikke opdatere opgaven');
      throw err;
    }
  };

  return { task, loading, error, updateTask };
}; 