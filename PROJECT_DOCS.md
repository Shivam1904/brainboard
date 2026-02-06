# 🛠️ Developer Manual: Brainboard

> [!NOTE]
> This manual contains strictly essential information for development: Architecture, API Specifications, Core Logic, and Setup.

## 1. Architecture

### Backend (`/backend/`)
**Modules** are organized by function using a Clean Architecture approach.
- **`routes/`**: Transaction-managed HTTP endpoints.
- **`services/`**: Pure business logic (no DB commits).
- **`models/`**: SQLAlchemy models using JSON columns for schema flexibility.
- **`orchestrators/`**: Coordinators for complex flows (e.g., `chat_orchestrator.py` handles WebSocket + AI).

### Frontend (`/src/`)
**Key Components**:
- **`Dashboard.tsx`**: Main entry; uses `react-grid-layout` to render widgets.
- **`services/socket.ts`**: Manages the single WebSocket connection for AI Chat.
- **`config/widgets.ts`**: Static definitions for widget metadata (size, icon, component map).

### API Pattern
The system uses a **Two-Tier API**:
1.  **Dashboard Level**: `GET /api/dashboard/today` returns the *structure* (which widgets to show, layout).
2.  **Widget Level**: Each widget independently calls its own endpoints (e.g., `/api/v1/weather`, `/api/v1/alarms`) for data.

---

## 2. Core Logic Flows

### Dashboard Widget Loading
1.  **Request**: Frontend calls `GET /api/dashboard/today`.
2.  **Server Logic**:
    -   Fetch `daily_widgets` for the date.
    -   Apply logic (e.g., if "Advanced Task" criteria met -> render `AdvancedSingleTaskWidget`).
    -   Return list of widget configs.
3.  **Frontend**: Iterates config, dynamically imports/renders widget components from `src/components/widgets/`.

### AI Chat & Real-time Steps
1.  **Connection**: Frontend initiates `ws://.../ws/chat`.
2.  **Orchestrator**: `ChatOrchestrator` receives message.
3.  **AI Engine**: Processes intent.
4.  **Feedback**: Sends "Thinking Steps" (`{"type": "thinking", ...}`) in real-time.
5.  **Response**: Sends final response or interactive component JSON.
6.  **Fallback**: If WebSocket fails, frontend falls back to local regex-based `AIResponseGenerator.ts`.

---

## 3. API Cheatsheet

### Endpoints
| Method | Path | Description |
| :--- | :--- | :--- |
| **GET** | `/api/v1/dashboard/today` | Get today's layout & widgets |
| **POST** | `/api/v1/dashboard/widget/add` | Add widget to daily view |
| **GET** | `/api/v1/dashboard-widgets/` | List all available widgets |
| **POST** | `/api/v1/dashboard-widgets/` | Create new widget configuration |
| **GET** | `/api/v1/alarms/` | Get all active alarms |
| **GET** | `/api/v1/weather/` | Get current weather (requires lat/lon) |

### Database Schema
-   **`dashboard_widget_details`**: Stores static configuration (title, type, settings).
-   **`daily_widgets`**: Stores instance data (is_active, priority, activity_logs) linked to a date.
-   **JSON Columns**: Used heavily for `widget_config` and `activity_data` to allow schema-less flexibility.

---

## 4. Setup & Commands

### Prerequisites
- Node.js 18+
- Python 3.10+ (via Conda)

### Environment (`.env` in root & backend/)
```env
# Backend
DATABASE_URL=sqlite:///./brainboard.db
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...
# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

### Backend (`/backend/`)
```bash
conda activate brainboard-ai
./run_with_conda.sh init-db  # Reset/Init DB
./run_with_conda.sh server   # Start FastAPI (port 8000)
```

### Frontend (`/`)
```bash
npm install
npm run dev                  # Start Vite (port 5173)
```

### Useful Commands
-   **Kill Port 8000**: `lsof -ti:8000 | xargs kill -9`
-   **Backend Tests**: `pytest`
-   **Code Format**: `black . && isort .`
