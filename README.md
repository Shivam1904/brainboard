# 🧠 Brainboard

An AI-powered modular productivity dashboard with smart widgets for managing tasks, summaries, and automation.

> [!TIP]
> For detailed architectural documentation, API specifications, and implementation guides, please see [PROJECT_DOCS.md](PROJECT_DOCS.md).

## 🚀 Features

### ✅ **Implemented Widgets**
- **Web Search Widget** - Individual search widgets with unique queries and results
- **Task List Widget** - Daily task management with progress tracking and mission creation
- **Calendar Widget** - Monthly calendar with events, milestones, and navigation
- **All Schedules Widget** - Comprehensive schedule management for all widgets

### 🏗️ **Architecture**
- **Dual Backend System**:
  - **Django** (port 8220): Main REST API for CRUD operations, database management
  - **FastAPI** (port 8221): AI orchestration, WebSocket streaming, AI tool execution
- **Dashboard API** - Dynamic widget loading from server configuration
- **Two-Tier API System** - Dashboard-level configuration + Widget-level data fetching
- **TypeScript** - Full type safety with comprehensive interfaces
- **Responsive Design** - Grid-based layout with drag-and-drop functionality

### 📱 **Widget Management**
- **Dynamic Loading** - Widgets loaded based on server configuration
- **Individual Data Fetching** - Each widget fetches its own data
- **Schedule Management** - Complete CRUD operations for widget schedules
- **Type-Specific Forms** - Different forms for different widget types

## 🛠️ Tech Stack

- **Django Backend**: Main API server (port 8220)
- **FastAPI AI Service**: AI orchestration and WebSocket streaming (port 8221)
- **Frontend**: React + TypeScript + Vite
- **Styling**: Tailwind CSS
- **Grid System**: React Grid Layout
- **Icons**: Lucide React
- **State Management**: React Hooks
- **Database**: SQLite (via Django ORM)

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd brainboard
```

### Quick Start (Recommended)

Use the Makefile to run everything with one command:

```bash
make dev
```

This starts:
- Django backend on `http://localhost:8220`
- FastAPI AI service on `http://localhost:8221`
- Frontend on `http://localhost:5173`

### Manual Setup

If you prefer to run services individually:

#### Django Backend Setup

```bash
cd backend/django_backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Run the server
python manage.py runserver 0.0.0.0:8220
```
The Django API will be at `http://localhost:8220`.

#### FastAPI AI Service Setup

```bash
cd backend

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8221
```
The FastAPI AI service will be at `http://localhost:8221`.
API Documentation: `http://localhost:8221/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
The frontend will start at `http://localhost:5173`.

## 🏗️ Project Structure

```
brainboard/
├── backend/
│   ├── main.py                    # FastAPI AI service entry point
│   ├── config.py                  # FastAPI configuration
│   ├── requirements.txt           # Python dependencies
│   ├── services/                 # AI & business logic
│   ├── routes/                    # FastAPI endpoints
│   └── django_backend/            # Django main API server
│       ├── manage.py              # Django entry point
│       ├── core/                  # Django project settings
│       └── api/                   # Django REST API
├── frontend/                      # React + Vite frontend
│   ├── src/                       # Frontend source code
│   ├── package.json               # Node dependencies
│   └── vite.config.ts             # Vite configuration
├── Makefile                       # Development commands
└── DEVELOPER_GUIDE.md             # Developer documentation
```

## 🛠️ Development

### Prerequisites
- **Node.js 18+** (recommended: use [nvm](https://github.com/nvm-sh/nvm) for version management)
- **Python 3.10+**
- **Git**
- **DB Browser for SQLite** (optional): `brew install --cask db-browser-for-sqlite` for visual database management

### Using Make Commands

The project uses a Makefile for common development tasks:

| Command | Description |
|---------|-------------|
| `make dev` | Run all services (Django, FastAPI, Frontend) |
| `make django-backend` | Run Django API server on port 8220 |
| `make fastapi-ai` | Run FastAPI AI service on port 8221 |
| `make frontend-dev` | Run Vite dev server |
| `make setup` | Install all dependencies |
| `make test` | Run tests |
| `make lint` | Run linters |
| `make help` | Show all available commands |

### Environment Setup

#### Django Backend (`.env`)
Create a `.env` file in the `backend/django_backend/` directory:
```env
# Django Configuration
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# External APIs
OPENAI_API_KEY=your-key-here
SERPER_API_KEY=your-key-here
```

#### FastAPI AI Service (`.env`)
Create a `.env` file in the `backend/` directory:
```env
# FastAPI Configuration
HOST=0.0.0.0
PORT=8221
RELOAD=True

# External APIs
OPENAI_API_KEY=your-key-here
SERPER_API_KEY=your-key-here

# Django API URL
DJANGO_API_URL=http://localhost:8220
```

#### Frontend (`.env`)
Create a `.env` file in the `frontend/` directory:
```env
VITE_API_BASE_URL=http://localhost:8220
VITE_WS_URL=ws://localhost:8221
```

### Important Notes
- **Django runs on port 8220** - Main API server
- **FastAPI runs on port 8221** - AI/websocket service
- **Frontend runs on port 5173** - Vite dev server
- **Always activate your virtual environment** (`source .venv/bin/activate`) before running FastAPI.
- **Keep environments isolated** to avoid dependency conflicts.

## 📋 Available Scripts

### Frontend (`frontend/`)
- `npm run dev` - Start Vite frontend
- `npm run build` - Build frontend for production
- `npm run test` - Run tests
- `npm run lint` - Lint code

### Django Backend (`backend/django_backend/`)
- `python manage.py runserver 0.0.0.0:8220` - Start Django server
- `python manage.py migrate` - Run database migrations
- `python manage.py createsuperuser` - Create admin user

### FastAPI Backend (`backend/`)
- `uvicorn main:app --reload --host 0.0.0.0 --port 8221` - Start FastAPI server

### Using Makefile (Recommended)
- `make dev` - Run all services
- `make setup` - Install all dependencies
- `make test` - Run tests
- `make lint` - Run linters

## 🔧 Troubleshooting

### Common Issues

**Backend Ports Already in Use**:
```bash
# Kill processes on specific ports
lsof -ti:8220 | xargs kill -9  # Django
lsof -ti:8221 | xargs kill -9  # FastAPI
lsof -ti:5173 | xargs kill -9  # Frontend
```

**PostCSS Error**: If you see "module is not defined in ES module scope"
- The `postcss.config.cjs` file should have `.cjs` extension (not `.js`)

**Database Management**:
1. Install: `brew install --cask db-browser-for-sqlite`
2. Open "DB Browser for SQLite" app
3. Click "Open Database" → Navigate to `backend/django_backend/db.sqlite3`
4. Use "Browse Data" tab to view/edit your widgets and summaries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Brainboard** - Organize your digital life with AI-powered widgets! 🧠✨
