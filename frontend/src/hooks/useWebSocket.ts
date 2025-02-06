import { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import { addNotification } from '../store/slices/uiSlice';

export const useWebSocket = () => {
  const [connected, setConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const dispatch = useDispatch();

  useEffect(() => {
    const socket = new WebSocket(process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws');

    socket.onopen = () => {
      setConnected(true);
      dispatch(addNotification('Forbundet til server'));
    };

    socket.onclose = () => {
      setConnected(false);
      dispatch(addNotification('Mistede forbindelse til server'));
    };

    socket.onerror = (error) => {
      console.error('WebSocket fejl:', error);
      dispatch(addNotification('Der opstod en fejl i forbindelsen'));
    };

    setWs(socket);
    return () => socket.close();
  }, [dispatch]);

  return { connected, ws };
}; 