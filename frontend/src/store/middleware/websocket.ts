import { Middleware } from 'redux';
import { addNotification } from '../slices/uiSlice';

export const websocketMiddleware: Middleware = store => next => action => {
  if (action.type === 'websocket/message') {
    const { type, payload } = action.payload;
    
    switch (type) {
      case 'task_update':
        store.dispatch(addNotification(`Opgave ${payload.id} blev opdateret`));
        break;
    }
  }
  
  return next(action);
}; 