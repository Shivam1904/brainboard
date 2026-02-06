# 🛠️ Brainboard Developer Guide

Welcome to the Brainboard codebase! This guide is designed to help you understand the system architecture, core concepts, and how to contribute effectively.

## 1. 🏗️ High-Level Architecture

Brainboard is a **modular productivity dashboard** built with a clear separation of concerns:

-   **Frontend**: React + Vite + TypeScript. Responsible for rendering the grid, widgets, and managing the WebSocket connection.
-   **Backend**: Python + FastAPI. Responsible for API endpoints, business logic, AI orchestration, and database persistence.
-   **Database**: SQLite (via SQLAlchemy + aiosqlite). A lightweight, file-based relational database.

### The "Two-Tier" API Pattern

We use a distinct pattern for loading data:

1.  **Dashboard Tier (`/api/dashboard`)**:
    -   The frontend asks: *"What is my layout for today?"*
    -   The backend returns a **List of Widget Configurations** (IDs, types, titles, positions).
    -   This determines *which* components the frontend renders.

2.  **Widget Tier (`/api/v1/{widget_type}`)**:
    -   Each rendered widget independently calls its own API to fetch its specific data.
    -   Example: The `CalendarWidget` calls `/api/v1/alarms` to get events.
    -   **Benefit**: If one widget fails, the rest of the dashboard still loads.

---

## 2. 🧩 Key Concepts

### A. The Widget System

Widgets are the building blocks. A "Widget" consists of two parts:

1.  **Frontend Component**: Located in `src/components/widgets/`. It handles UI and user interaction.
2.  **Backend Data**:
    -   **`DashboardWidgetDetails`**: The configuration (e.g., Title: "Work Tasks", Type: "todo-task").
    -   **`DailyWidget`**: The instance of that widget for a specific day (e.g., "Active on 2024-02-05").

### B. The AI Engine (`backend/ai_engine/`)

The backend isn't just CRUD; it has an AI layer.

-   **`AIOrchestrator`**: The "brain" that manages the conversation flow.
-   **`SessionMemory`**: Remembers context from previous messages.
-   **`ToolRegistry`**: Allows the AI to "do" things (e.g., "Search the web", "Create a task").
-   **WebSocket (`/ws`)**: Used for real-time streaming of AI "thinking steps" and final responses.

---

## 3. 🗺️ Codebase Map

### Backend (`/backend`)
| Directory | Purpose |
| :--- | :--- |
| `main.py` | **Entry Point**. Sets up the app, routes, and error handlers. |
| `config.py` | **Configuration**. Central place for all settings and environment variables. |
| `routes/` | **API Endpoints**. Handles HTTP requests. Keeping logic minimal here. |
| `services/` | **Business Logic**. The heavy lifting. Database queries, calculations, validation. |
| `models/` | **Database Tables**. SQLAlchemy definitions (`User`, `Widget`, `Task`). |
| `schemas/` | **Data Validation**. Pydantic models for request/response typing. |
| `ai_engine/` | **AI Logic**. LLM integration, prompt templates, tool definitions. |

### Frontend (`/src`)
| Directory | Purpose |
| :--- | :--- |
| `components/` | Reusable UI elements (Buttons, Cards). |
| `features/` | Feature-specific logic (e.g., `autom8` landing page). |
| `sections/` | Larger UI sections (e.g., `Hero`, `Features`). |
| `services/` | API clients and WebSocket managers. |

---

## 4. 🚀 Improvement Roadmap

Since you want to improve the project, here are the recommended next steps, ranked by impact:

### 🥇 Priority 1: Testing & Stability
-   [ ] **Add Unit Tests**: The `tests/` directory is sparse. Add tests for `services/` logic (e.g., `dashboard_widget_service.py`).
-   [ ] **E2E Testing**: Add Cypress or Playwright tests to verify the Dashboard loads correctly.

### 🥈 Priority 2: Security & Auth
-   [ ] **Authentication**: Currently, we use a default user (`user_001`). Implementing real JWT-based auth (Auth0 or custom) is a critical next step.
-   [ ] **Input Validation**: Ensure all Pydantic schemas have strict validation (min_length, regex) to prevent bad data.

### 🥉 Priority 3: Architecture
-   [ ] **Migration to Postgres**: SQLite is great for local, but moving to PostgreSQL would enable advanced features like vector search (pgvector) for better AI memory.
-   [ ] **Frontend Query Management**: Implement `TanStack Query` (React Query) for better caching and loading states on the frontend.

### 🎖️ Priority 4: Features
-   [ ] **New Widgets**: Create a "Weather Widget" or "Stock Ticker" to prove the modularity of the system.
-   [ ] **Voice Mode**: Add voice-to-text for the AI chat.

---

## 5. 🛠️ Development Workflow

1.  **Backend**:
    ```bash
    cd backend
    source .venv/bin/activate
    python main.py
    # Swagger Docs: http://localhost:8989/docs
    ```

2.  **Frontend**:
    ```bash
    npm run dev
    # UI: http://localhost:5173
    ```
