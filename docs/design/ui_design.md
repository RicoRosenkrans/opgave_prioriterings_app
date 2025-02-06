# UI Design Dokumentation

## 1. Dashboard
![Dashboard Wireframe](wireframes/dashboard.png)

```ascii
+------------------+------------------+
|     Header       |  Notifikationer |
+------------------+------------------+
| Dagens Opgaver   |   Status Panel  |
|  - Task 1 [H]    |   ⚪ TODO: 5    |
|  - Task 2 [M]    |   🔵 AKTIV: 3   |
|  - Task 3 [L]    |   ✅ DONE: 8    |
+------------------+------------------+
|    AI Indsigt    |   Hurtig-Add   |
| "Du har 2 høj-   |  [+ Ny Opgave] |
|  prioritets..."  |                 |
+------------------+------------------+
```

### Komponenter:
- **Header**: Navigation og brugerinfo
- **Notifikationspanel**: Realtidsopdateringer
- **Opgaveliste**: Prioriteret visning med farvekodet status
- **Status Panel**: Numerisk overblik
- **AI Indsigt**: Dynamiske anbefalinger
- **Hurtig-Add**: Opgaveoprettelse med ét klik

## 2. Opgavevisning
![Task View Wireframe](wireframes/task_view.png)

```ascii
+----------------------------------+
| Opgave: [Titel]          [Status]|
+----------------------------------+
| Beskrivelse:                     |
| [Markdown Editor]                |
|                                  |
+----------------------------------+
| Prioritet:  [H] [M] [L]         |
| Deadline:   [Datovælger]        |
| Status:     [Dropdown]           |
+----------------------------------+
| AI Assistance:                   |
| [💡 Foreslå Prioritet]           |
| [📊 Generer Status]              |
+----------------------------------+
```

### Funktioner:
- Markdown editor til beskrivelser
- Drag-n-drop fil upload
- Realtids AI-forslag
- Automatisk gem

## 3. Dialog Interface
![Dialog Interface Wireframe](wireframes/dialog.png)

```ascii
+----------------------------------+
|           Chat Historie          |
| Du: Status på projekt A?         |
| 🤖: Her er en oversigt...        |
|     - 3 opgaver i gang          |
|     - Deadline om 2 dage        |
|                                 |
+----------------------------------+
| [🎤] [Skriv besked...]  [Send]  |
+----------------------------------+
```

### Funktioner:
- Voice-to-text input
- Kontekstbevidst AI-assistent
- Markdown formatering
- Eksport af samtaler

## 4. Stemmekontrol & TTS
![Voice Control Wireframe](wireframes/voice.png)

```ascii
+----------------------------------+
|        Stemmekommandoer         |
| [🎤] "Læs dagens opgaver"       |
|     "Opret ny opgave"           |
|     "Status update"             |
+----------------------------------+
| TTS Indstillinger:              |
| Hastighed: [■■■□□]              |
| Stemme:    [Dansk ▼]            |
+----------------------------------+
```

### Nøglefunktioner:
- Naturlig stemmekommando genkendelse
- Konfigurerbar TTS-output
- Baggrundsoplæsning af opdateringer
- Stemmepåmindelser for deadlines

## 5. Responsivt Design
Alle komponenter er designet til at fungere på:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobil (< 768px)

## 6. Tilgængelighed
- WCAG 2.1 AA compliant
- Høj kontrast tema
- Skærmlæservenlig
- Tastaturgenveje

## 7. Tema & Styling
```css
:root {
  /* Farver */
  --primary: #2563eb;
  --secondary: #64748b;
  --success: #22c55e;
  --warning: #f59e0b;
  --error: #ef4444;
  
  /* Typografi */
  --font-primary: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  
  /* Spacing */
  --spacing-base: 1rem;
  --radius-sm: 0.375rem;
}
```

## 8. Implementeringsdetaljer

### React Komponenter:
```typescript
// TaskList.tsx
interface TaskListProps {
  tasks: Task[];
  onTaskUpdate: (task: Task) => void;
  onVoiceCommand?: (command: string) => void;
}

// DialogPanel.tsx
interface DialogPanelProps {
  clientId: number;
  onMessage: (msg: WebSocketMessage) => void;
  enableVoice?: boolean;
}
```

### WebSocket Integration:
```typescript
// useWebSocket.ts
const useWebSocket = (clientId: number) => {
  // WebSocket logik her...
};
```

## 9. State Management

### Redux Store Structure
```typescript
// store/types.ts
interface RootState {
  tasks: TaskState;
  ui: UIState;
  websocket: WebSocketState;
  auth: AuthState;
}

interface TaskState {
  items: Task[];
  loading: boolean;
  error: string | null;
  filters: {
    status?: TaskStatus;
    priority?: TaskPriority;
    search?: string;
  };
  selectedTask: Task | null;
}

interface UIState {
  darkMode: boolean;
  sidebarOpen: boolean;
  notifications: Notification[];
  voiceEnabled: boolean;
  ttsSettings: {
    speed: number;
    voice: string;
  };
}

interface WebSocketState {
  connected: boolean;
  pendingMessages: WebSocketMessage[];
  subscriptions: number[]; // task IDs
}
```

### Redux Slices
```typescript
// store/slices/taskSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const fetchTasks = createAsyncThunk(
  'tasks/fetchTasks',
  async () => {
    const response = await fetch('/api/v1/tasks');
    return response.json();
  }
);

const taskSlice = createSlice({
  name: 'tasks',
  initialState,
  reducers: {
    updateTask(state, action) {
      const index = state.items.findIndex(t => t.id === action.payload.id);
      if (index !== -1) {
        state.items[index] = action.payload;
      }
    },
    setFilter(state, action) {
      state.filters = { ...state.filters, ...action.payload };
    },
    // ... andre reducers
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTasks.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchTasks.fulfilled, (state, action) => {
        state.items = action.payload;
        state.loading = false;
      });
  },
});
```

### WebSocket Integration med Redux
```typescript
// store/middleware/websocket.ts
import { Middleware } from 'redux';

export const websocketMiddleware: Middleware = store => next => action => {
  // Handle WebSocket relaterede actions
  if (action.type === 'websocket/message') {
    const { type, payload } = action.payload;
    
    switch (type) {
      case 'task_update':
        store.dispatch(updateTask(payload));
        break;
      case 'priority_suggestion':
        store.dispatch(showNotification({
          type: 'info',
          message: `Ny prioritetsforslag for opgave ${payload.taskId}`
        }));
        break;
    }
  }
  
  return next(action);
};
```

### Hooks og Selectors
```typescript
// hooks/useTasks.ts
export const useTasks = () => {
  const dispatch = useAppDispatch();
  const tasks = useSelector(selectTasks);
  const filters = useSelector(selectTaskFilters);

  const filteredTasks = useMemo(() => {
    return tasks.filter(task => {
      if (filters.status && task.status !== filters.status) return false;
      if (filters.priority && task.priority !== filters.priority) return false;
      if (filters.search && !task.title.toLowerCase().includes(filters.search.toLowerCase())) return false;
      return true;
    });
  }, [tasks, filters]);

  return {
    tasks: filteredTasks,
    loading: useSelector(selectTasksLoading),
    error: useSelector(selectTasksError),
    updateTask: (task: Task) => dispatch(updateTask(task)),
    setFilter: (filter: Partial<TaskFilters>) => dispatch(setFilter(filter)),
  };
};
```

### Komponent Integration
```typescript
// components/TaskList.tsx
export const TaskList: React.FC = () => {
  const { tasks, loading, updateTask, setFilter } = useTasks();
  const { connected } = useWebSocket();

  if (loading) return <LoadingSpinner />;

  return (
    <div className="task-list">
      <TaskFilters onFilterChange={setFilter} />
      {tasks.map(task => (
        <TaskItem
          key={task.id}
          task={task}
          onUpdate={updateTask}
          realtime={connected}
        />
      ))}
    </div>
  );
};
```

## 10. API Integration

### API Service Layer
```typescript
// services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor for auth tokens
api.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Håndter token udløb
      store.dispatch(logout());
    }
    return Promise.reject(error);
  }
);
```

### Task Service
```typescript
// services/taskService.ts
import { api } from './api';
import type { Task, CreateTaskDTO, UpdateTaskDTO } from '../types';

export const taskService = {
  async getAll(): Promise<Task[]> {
    const { data } = await api.get('/tasks');
    return data;
  },

  async getById(id: number): Promise<Task> {
    const { data } = await api.get(`/tasks/${id}`);
    return data;
  },

  async create(task: CreateTaskDTO): Promise<Task> {
    const { data } = await api.post('/tasks', task);
    return data;
  },

  async update(id: number, task: UpdateTaskDTO): Promise<Task> {
    const { data } = await api.patch(`/tasks/${id}`, task);
    return data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/tasks/${id}`);
  }
};
```

### AI Assistance Service
```typescript
// services/aiService.ts
import { api } from './api';

export const aiService = {
  async getPrioritySuggestion(taskId: number): Promise<PrioritySuggestion> {
    const { data } = await api.post(`/ai/priority/${taskId}`);
    return data;
  },

  async getStatusReport(taskIds: number[]): Promise<StatusReport> {
    const { data } = await api.post('/ai/status-report', { taskIds });
    return data;
  }
};
```

### WebSocket Service
```typescript
// services/websocketService.ts
export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private messageQueue: WebSocketMessage[] = [];

  constructor(private clientId: number) {}

  connect() {
    this.ws = new WebSocket(`ws://localhost:8000/ws/dialog/${this.clientId}`);
    
    this.ws.onopen = () => {
      this.flushMessageQueue();
      store.dispatch(setWebSocketConnected(true));
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      store.dispatch(handleWebSocketMessage(message));
    };

    this.ws.onclose = () => {
      store.dispatch(setWebSocketConnected(false));
      this.scheduleReconnect();
    };
  }

  send(message: WebSocketMessage) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      this.messageQueue.push(message);
    }
  }

  subscribeToTask(taskId: number) {
    this.send({
      type: 'subscribe',
      task_id: taskId
    });
  }

  requestPriority(task: Task) {
    this.send({
      type: 'priority_request',
      task: task
    });
  }

  private flushMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) this.send(message);
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => this.connect(), 5000);
  }
}
```

### Integration med Components
```typescript
// components/TaskDetail.tsx
export const TaskDetail: React.FC<{ taskId: number }> = ({ taskId }) => {
  const { task, loading, error } = useTask(taskId);
  const { connected } = useWebSocket();
  const dispatch = useAppDispatch();

  useEffect(() => {
    if (connected) {
      websocketService.subscribeToTask(taskId);
    }
  }, [taskId, connected]);

  const handlePriorityRequest = async () => {
    try {
      const suggestion = await aiService.getPrioritySuggestion(taskId);
      dispatch(showNotification({
        type: 'success',
        message: 'Prioritetsforslag modtaget'
      }));
    } catch (error) {
      dispatch(showNotification({
        type: 'error',
        message: 'Kunne ikke hente prioritetsforslag'
      }));
    }
  };

  return (
    <div className="task-detail">
      {loading ? (
        <LoadingSpinner />
      ) : error ? (
        <ErrorMessage message={error} />
      ) : task ? (
        <>
          <TaskHeader task={task} />
          <TaskForm task={task} onSubmit={handleUpdate} />
          <AIAssistancePanel
            onPriorityRequest={handlePriorityRequest}
            connected={connected}
          />
        </>
      ) : null}
    </div>
  );
};
``` 